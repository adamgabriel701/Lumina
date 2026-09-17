from llvmlite import ir


class MatchStmtMixin:

    def visit_MatchStmt(self, node):
        # MatchStmt.cases é 4-tuple: (variant, bindings, guard, body).
        # bindings pode ser None, [name] ou [name1, name2].
        has_guard = any(len(c) >= 4 and c[2] is not None for c in node.cases)

        cond_val = self.visit(node.condition)
        end_bb = self.builder.append_basic_block(name="match_end")

        if has_guard:
            self._codegen_match_with_guard(node, cond_val, end_bb)
            return

        # Caso 1: match sobre i64
        if cond_val.type == self.i64_ty:
            self._codegen_match_int(node, cond_val, end_bb)
            return

        # Caso 2: match sobre enum {i32 tag, i64 payload_0, ...}
        if isinstance(cond_val.type, ir.PointerType) and isinstance(cond_val.type.pointee, ir.IdentifiedStructType):
            struct_name = cond_val.type.pointee.name
            if struct_name in self.struct_defs and hasattr(self.struct_defs[struct_name], 'variants'):
                self._codegen_match_enum(node, cond_val, end_bb)
                return

        # Caso 3: match sobre str (i8*)  ← NOVO
        if cond_val.type == self.voidptr_ty:
            self._codegen_match_str(node, cond_val, end_bb)
            return

        # Fallback: tipo desconhecido. Ainda assim, garante terminador
        # e posiciona no end_bb para não deixar IR inválido.
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)
        self.builder.position_at_end(end_bb)

    # ------------------------------------------------------------------
    # Match em i64
    # ------------------------------------------------------------------
    def _codegen_match_int(self, node, cond_val, end_bb):
        default_bb = self.builder.append_basic_block(name="match_default")
        sw = self.builder.switch(cond_val, default_bb)

        for case in node.cases:
            if len(case) == 4:
                val_node, var_name, _guard, body = case
            else:
                val_node, var_name, body = case

            if isinstance(val_node, str):
                try:
                    val = ir.Constant(self.i64_ty, int(val_node))
                except (ValueError, TypeError):
                    continue
            else:
                val = self.visit(val_node)

            case_bb = self.builder.append_basic_block(name="match_case")
            sw.add_case(val, case_bb)
            self.builder.position_at_end(case_bb)

            if var_name:
                if isinstance(var_name, list):
                    for name in var_name:
                        var_ptr = self.builder.alloca(self.i64_ty, name=name)
                        self.symbol_table[name] = var_ptr
                else:
                    var_ptr = self.builder.alloca(self.i64_ty, name=var_name)
                    self.symbol_table[var_name] = var_ptr

            for stmt in body:
                self.visit(stmt)
            if not self.builder.block.is_terminated:
                self.builder.branch(end_bb)

        self.builder.position_at_end(default_bb)
        if node.default:
            for stmt in node.default:
                self.visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)
        self.builder.position_at_end(end_bb)

    # ------------------------------------------------------------------
    # Match em enum
    # ------------------------------------------------------------------
    def _codegen_match_enum(self, node, cond_val, end_bb):
        struct_name = cond_val.type.pointee.name
        struct_def = self.struct_defs[struct_name]
        variant_map = {v[0]: i for i, v in enumerate(struct_def.variants)}

        tag_ptr = self.builder.gep(
            cond_val,
            [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)],
            name="match_tag_ptr",
        )
        tag_val = self.builder.load(tag_ptr, name="match_tag")

        default_bb = self.builder.append_basic_block(name="match_default")
        sw = self.builder.switch(tag_val, default_bb)

        for case in node.cases:
            if len(case) == 4:
                variant_name, var_name, _guard, body = case
            else:
                variant_name, var_name, body = case
            if variant_name not in variant_map:
                continue
            case_idx = variant_map[variant_name]
            case_bb = self.builder.append_basic_block(name=f"match_{variant_name.lower()}")
            sw.add_case(ir.Constant(self.i32_ty, case_idx), case_bb)
            self.builder.position_at_end(case_bb)

            if var_name:
                if isinstance(var_name, list):
                    for i, name in enumerate(var_name):
                        pp = self.builder.gep(
                            cond_val,
                            [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i + 1)],
                            name=f"payload_ptr_{name}",
                        )
                        payload_val = self.builder.load(pp, name=f"payload_{name}")
                        var_ptr = self.builder.alloca(self.i64_ty, name=name)
                        self.builder.store(payload_val, var_ptr)
                        self.symbol_table[name] = var_ptr
                else:
                    payload_ptr = self.builder.gep(
                        cond_val,
                        [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)],
                        name="payload_ptr",
                    )
                    payload_val = self.builder.load(payload_ptr, name="payload_load")
                    var_ptr = self.builder.alloca(self.i64_ty, name=var_name)
                    self.builder.store(payload_val, var_ptr)
                    self.symbol_table[var_name] = var_ptr

            for stmt in body:
                self.visit(stmt)
            if not self.builder.block.is_terminated:
                self.builder.branch(end_bb)

        self.builder.position_at_end(default_bb)
        if node.default:
            for stmt in node.default:
                self.visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)
        self.builder.position_at_end(end_bb)

    # ------------------------------------------------------------------
    # Match em str (i8*)  ← NOVO
    # ------------------------------------------------------------------
    def _codegen_match_str(self, node, cond_val, end_bb):
        """Compara strings com strcmp e ramifica.

        Cada case é testado em sequência; se nenhum casar, cai no default.
        """
        # Usa o strcmp já declarado em setup_libc_functions.
        # (Ver `LLVMCodegen.setup_libc_functions`.)
        strcmp_fn = self.strcmp

        next_bb = self.builder.append_basic_block(name="match_str_next_0")
        self.builder.branch(next_bb)

        for i, case in enumerate(node.cases):
            if len(case) == 4:
                variant, binding, guard, body = case
            else:
                variant, binding, body = case
                guard = None

            test_bb = self.builder.append_basic_block(name=f"match_str_test_{i}")
            body_bb = self.builder.append_basic_block(name=f"match_str_body_{i}")
            next_next_bb = self.builder.append_basic_block(name=f"match_str_next_{i + 1}")

            self.builder.position_at_end(next_bb)
            self.builder.branch(test_bb)

            self.builder.position_at_end(test_bb)

            # `variant` veio do parser como string literal Python
            # (ex: 'run') ou como expressão (VariableExpr).
            if isinstance(variant, str):
                case_str = self.create_global_string(variant)
            else:
                case_str = self.visit(variant)

            cmp_result = self.builder.call(
                strcmp_fn, [cond_val, case_str], name=f"strcmp_{i}"
            )
            is_eq = self.builder.icmp_signed(
                "==", cmp_result, ir.Constant(ir.IntType(32), 0), name=f"str_eq_{i}"
            )

            if guard:
                guard_val = self.visit(guard)
                if guard_val.type != ir.IntType(1):
                    guard_val = self.builder.icmp_signed(
                        "!=", guard_val, ir.Constant(guard_val.type, 0),
                        name=f"guard_cond_{i}",
                    )
                final_cond = self.builder.and_(is_eq, guard_val, name=f"match_and_{i}")
            else:
                final_cond = is_eq

            self.builder.cbranch(final_cond, body_bb, next_next_bb)

            self.builder.position_at_end(body_bb)

            # Binding: em match sobre str, `case x` sem guard vira self-binding
            if binding:
                names = binding if isinstance(binding, list) else [binding]
                for name in names:
                    var_ptr = self.builder.alloca(self.voidptr_ty, name=name)
                    self.builder.store(cond_val, var_ptr)
                    self.symbol_table[name] = var_ptr

            for stmt in body:
                self.visit(stmt)
            if not self.builder.block.is_terminated:
                self.builder.branch(end_bb)

            next_bb = next_next_bb

        # Default / fallthrough
        self.builder.position_at_end(next_bb)
        if node.default:
            for stmt in node.default:
                self.visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)

        self.builder.position_at_end(end_bb)

    # ------------------------------------------------------------------
    # Helper: match com guards
    # ------------------------------------------------------------------
    def _is_enum_condition(self, cond_val):
        return (
            isinstance(cond_val.type, ir.PointerType)
            and isinstance(cond_val.type.pointee, ir.IdentifiedStructType)
            and cond_val.type.pointee.name in self.struct_defs
            and hasattr(self.struct_defs[cond_val.type.pointee.name], 'variants')
        )

    def _coerce_self_binding(self, variant, binding, cond_val):
        """Se `variant` é string que não é número E não estamos
        num match de enum, converte em self-binding.
        """
        if not isinstance(variant, str) or not variant:
            return variant, binding
        if self._is_enum_condition(cond_val):
            return variant, binding
        try:
            int(variant)
            return variant, binding
        except (ValueError, TypeError):
            if binding is None:
                return None, [variant]
            return variant, binding

    def _codegen_match_with_guard(self, node, cond_val, end_bb):
        """Match com guards.

        Para enum, usa 4 blocos por case:
            test_bb: testa tag
            bind_bb: extrai payload nos bindings
            body_bb: executa corpo
            next_bb: próximo case

        Para int/str, mantém 3 blocos (testa + guard combinados).

        O ponto crítico é que os bindings do enum precisam existir ANTES
        da avaliação do guard — senão `case Circle(r) if r > 10` avalia
        `r` como 0 (não declarado) e o guard sempre falha.
        """
        is_enum = self._is_enum_condition(cond_val)

        variant_map = {}
        if is_enum:
            struct_name = cond_val.type.pointee.name
            struct_def = self.struct_defs[struct_name]
            variant_map = {v[0]: i for i, v in enumerate(struct_def.variants)}

        for i, case in enumerate(node.cases):
            if len(case) == 4:
                variant, binding, guard, body = case
            else:
                variant, binding, body = case
                guard = None

            variant, binding = self._coerce_self_binding(variant, binding, cond_val)

            test_bb = self.builder.append_basic_block(name=f"match_guard_test_{i}")
            body_bb = self.builder.append_basic_block(name=f"match_guard_body_{i}")
            next_bb = self.builder.append_basic_block(name=f"match_guard_next_{i}")

            self.builder.branch(test_bb)
            self.builder.position_at_end(test_bb)

            # Self-binding: variant is None + binding existente
            # (ex: `case n if n > 10`). Vincula antes do guard.
            if variant is None and binding:
                binding_name = binding[0] if isinstance(binding, list) else binding
                var_ptr = self.builder.alloca(cond_val.type, name=binding_name)
                self.builder.store(cond_val, var_ptr)
                self.symbol_table[binding_name] = var_ptr

            # ============================================================
            # ENUM: 4 blocos, bindings antes do guard
            # ============================================================
            if is_enum:
                # 1. Testa tag
                if variant is None:
                    pattern_match = ir.Constant(ir.IntType(1), 1)
                elif variant in variant_map:
                    tag_ptr = self.builder.gep(
                        cond_val,
                        [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)],
                        name=f"tag_ptr_{i}",
                    )
                    tag_val = self.builder.load(tag_ptr, name=f"tag_{i}")
                    pattern_match = self.builder.icmp_signed(
                        "==", tag_val,
                        ir.Constant(self.i32_ty, variant_map[variant]),
                        name=f"tag_eq_{i}",
                    )
                else:
                    pattern_match = ir.Constant(ir.IntType(1), 0)

                bind_bb = self.builder.append_basic_block(name=f"match_guard_bind_{i}")
                self.builder.cbranch(pattern_match, bind_bb, next_bb)

                # 2. Extrai payload para os bindings
                self.builder.position_at_end(bind_bb)
                if binding and variant is not None:
                    names = binding if isinstance(binding, list) else [binding]
                    for idx, name in enumerate(names):
                        pp = self.builder.gep(
                            cond_val,
                            [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, idx + 1)],
                            name=f"payload_ptr_{idx}",
                        )
                        payload_val = self.builder.load(pp, name=f"payload_{idx}")
                        var_ptr = self.builder.alloca(self.i64_ty, name=name)
                        self.builder.store(payload_val, var_ptr)
                        self.symbol_table[name] = var_ptr

                # 3. Guard (bindings agora em escopo)
                if guard:
                    guard_val = self.visit(guard)
                    if guard_val.type != ir.IntType(1):
                        guard_val = self.builder.icmp_signed(
                            "!=", guard_val, ir.Constant(guard_val.type, 0),
                            name=f"guard_cond_{i}",
                        )
                    self.builder.cbranch(guard_val, body_bb, next_bb)
                else:
                    self.builder.branch(body_bb)

            # ============================================================
            # INT/STR: 3 blocos (comportamento anterior)
            # ============================================================
            else:
                if variant is None:
                    pattern_match = ir.Constant(ir.IntType(1), 1)
                elif cond_val.type == self.i64_ty:
                    if isinstance(variant, str):
                        try:
                            case_val = ir.Constant(self.i64_ty, int(variant))
                            pattern_match = self.builder.icmp_signed(
                                "==", cond_val, case_val, name=f"match_eq_{i}",
                            )
                        except ValueError:
                            pattern_match = ir.Constant(ir.IntType(1), 1)
                    else:
                        case_val = self.visit(variant)
                        pattern_match = self.builder.icmp_signed(
                            "==", cond_val, case_val, name=f"match_eq_{i}",
                        )
                else:
                    pattern_match = ir.Constant(ir.IntType(1), 1)

                if guard:
                    self.builder.position_at_end(test_bb)
                    guard_val = self.visit(guard)
                    if guard_val.type != ir.IntType(1):
                        guard_val = self.builder.icmp_signed(
                            "!=", guard_val, ir.Constant(guard_val.type, 0),
                            name=f"guard_cond_{i}",
                        )
                    final_cond = self.builder.and_(
                        pattern_match, guard_val, name=f"match_and_{i}",
                    )
                else:
                    final_cond = pattern_match

                self.builder.cbranch(final_cond, body_bb, next_bb)

            # ============================================================
            # Corpo (comum aos dois caminhos)
            # ============================================================
            self.builder.position_at_end(body_bb)
            for stmt in body:
                if self.builder.block.is_terminated:
                    break
                self.visit(stmt)
            if not self.builder.block.is_terminated:
                self.builder.branch(end_bb)

            self.builder.position_at_end(next_bb)

        # Default / fallthrough
        if node.default:
            for stmt in node.default:
                if self.builder.block.is_terminated:
                    break
                self.visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)

        self.builder.position_at_end(end_bb)