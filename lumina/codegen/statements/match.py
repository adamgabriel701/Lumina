from llvmlite import ir


class MatchStmtMixin:

    # ==================================================================
    # Dispatcher
    # ==================================================================
    def visit_MatchStmt(self, node):
        cond_val = self.visit(node.condition)
        end_bb = self.builder.append_basic_block(name="match_end")
        self._match_chain(node, cond_val, end_bb)

    # ==================================================================
    # Cadeia de branches por case (common a int/enum/str)
    #
    # Estrutura por case:
    #   test_bb: avalia pattern_match
    #   bind_bb: extrai bindings (só quando casou o pattern)
    #   body_bb: executa corpo (só quando guard passou, se houver)
    #   next_bb: próximo case
    #
    # IMPORTANTE: bindings são extraídos ANTES do guard ser avaliado.
    # Isso permite `case Circle(r) if r > 10` e `case s if s.contains(...)`.
    #
    # NOTA: optamos por chain sequencial em vez de `switch` (jump table).
    # Para um compilador em desenvolvimento, simplicidade > micro-otimização.
    # Quando performance importar, adicionar fast-path: se todos os cases
    # são int literals sem guard/binding, emitir `switch`.
    # ==================================================================
    def _match_chain(self, node, cond_val, end_bb):
        kind = self._classify_match_kind(cond_val)

        # Tipos não suportados em MatchStmt (ex: struct não-enum).
        # Comportamento atual: no-op, vai direto para end_bb.
        if kind == "unknown":
            if not self.builder.block.is_terminated:
                self.builder.branch(end_bb)
            self.builder.position_at_end(end_bb)
            return

        variant_map = self._build_variant_map(kind, cond_val)

        next_bb = self.builder.append_basic_block(name="match_next_0")
        self.builder.branch(next_bb)

        for i, case in enumerate(node.cases):
            next_bb = self._emit_case(
                i, case, kind, cond_val, variant_map, next_bb, end_bb
            )

        # Default / fallthrough
        self.builder.position_at_end(next_bb)
        if node.default:
            for stmt in node.default:
                if self.builder.block.is_terminated:
                    break
                self.visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)

        self.builder.position_at_end(end_bb)

    # ==================================================================
    # Emissão de um case
    # ==================================================================
    def _emit_case(self, i, case, kind, cond_val, variant_map, prev_next_bb, end_bb):
        # Normaliza o tuple
        if len(case) == 4:
            variant, binding, guard, body = case
        else:
            variant, binding, body = case
            guard = None

        variant, binding = self._coerce_self_binding(variant, binding, cond_val)

        test_bb  = self.builder.append_basic_block(name=f"match_test_{i}")
        bind_bb  = self.builder.append_basic_block(name=f"match_bind_{i}")
        body_bb  = self.builder.append_basic_block(name=f"match_body_{i}")
        next_bb  = self.builder.append_basic_block(name=f"match_next_{i + 1}")

        # --- test_bb: pattern_match ---
        self.builder.position_at_end(prev_next_bb)
        self.builder.branch(test_bb)

        self.builder.position_at_end(test_bb)
        pattern_match = self._compute_pattern_match(
            kind, cond_val, variant, variant_map, i
        )
        self.builder.cbranch(pattern_match, bind_bb, next_bb)

        # --- bind_bb: extrai bindings (antes do guard) ---
        self.builder.position_at_end(bind_bb)
        self._emit_bindings(kind, cond_val, variant, binding)

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

        # --- body_bb: corpo ---
        self.builder.position_at_end(body_bb)
        for stmt in body:
            if self.builder.block.is_terminated:
                break
            self.visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)

        return next_bb

    # ==================================================================
    # Classificação e maps
    # ==================================================================
    def _classify_match_kind(self, cond_val):
        """Retorna 'int', 'enum', 'str' ou 'unknown'."""
        if cond_val.type == self.i64_ty:
            return "int"
        if (isinstance(cond_val.type, ir.PointerType)
                and isinstance(cond_val.type.pointee, ir.IdentifiedStructType)):
            name = cond_val.type.pointee.name
            if name in self.struct_defs and hasattr(self.struct_defs[name], 'variants'):
                return "enum"
        if cond_val.type == self.voidptr_ty:
            return "str"
        return "unknown"

    def _build_variant_map(self, kind, cond_val):
        if kind != "enum":
            return {}
        struct_name = cond_val.type.pointee.name
        struct_def = self.struct_defs[struct_name]
        return {v[0]: i for i, v in enumerate(struct_def.variants)}

    # ==================================================================
    # Teste do pattern (kind-specific)
    # ==================================================================
    def _compute_pattern_match(self, kind, cond_val, variant, variant_map, i):
        """Retorna um valor i1: True se o pattern do case casa.

        `variant` pode ser:
          - `None`             → wildcard ou self-binding (sempre casa)
          - `str` / `StringExpr` → single pattern
          - `list`             → multi-pattern (`case 1 | 2:`), OR dos testes

        Para list, avalia cada alternativa e combina com `or`.
        """
        if isinstance(variant, list):
            if len(variant) == 0:
                return ir.Constant(ir.IntType(1), 0)
            # Avalia cada alternativa; OR incremental
            result = self._compute_pattern_match_single(
                kind, cond_val, variant[0], variant_map, f"{i}_0"
            )
            for j, v in enumerate(variant[1:], start=1):
                r = self._compute_pattern_match_single(
                    kind, cond_val, v, variant_map, f"{i}_{j}"
                )
                result = self.builder.or_(
                    result, r, name=f"match_or_{i}_{j}"
                )
            return result

        return self._compute_pattern_match_single(
            kind, cond_val, variant, variant_map, str(i)
        )

    def _compute_pattern_match_single(self, kind, cond_val, variant,
                                       variant_map, suffix):
        """Um único pattern (não-lista)."""
        if variant is None:
            return ir.Constant(ir.IntType(1), 1)

        if kind == "int":
            if isinstance(variant, str):
                try:
                    case_val = ir.Constant(self.i64_ty, int(variant))
                except (ValueError, TypeError):
                    return ir.Constant(ir.IntType(1), 0)
            else:
                case_val = self.visit(variant)
                if case_val.type != self.i64_ty:
                    case_val = self._coerce_arg(
                        case_val, self.i64_ty, suffix=f"_match{suffix}"
                    )
            return self.builder.icmp_signed(
                "==", cond_val, case_val, name=f"match_eq_{suffix}"
            )

        if kind == "enum":
            if not isinstance(variant, str) or variant not in variant_map:
                return ir.Constant(ir.IntType(1), 0)
            tag_ptr = self.builder.gep(
                cond_val,
                [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)],
                name=f"match_tag_ptr_{suffix}",
            )
            tag_val = self.builder.load(tag_ptr, name=f"match_tag_{suffix}")
            return self.builder.icmp_signed(
                "==", tag_val,
                ir.Constant(self.i32_ty, variant_map[variant]),
                name=f"match_tag_eq_{suffix}",
            )

        if kind == "str":
            if isinstance(variant, str):
                case_str = self.create_global_string(variant)
            else:
                case_str = self.visit(variant)
            cmp_result = self.builder.call(
                self.strcmp, [cond_val, case_str],
                name=f"match_strcmp_{suffix}",
            )
            return self.builder.icmp_signed(
                "==", cmp_result, ir.Constant(ir.IntType(32), 0),
                name=f"match_str_eq_{suffix}",
            )

        return ir.Constant(ir.IntType(1), 0)

    # ==================================================================
    # Bindings (kind-specific)
    # ==================================================================
    def _emit_bindings(self, kind, cond_val, variant, binding):
        if not binding:
            return

        # Multi-pattern com binding é rejeitado no parser; salvaguarda
        if isinstance(variant, list):
            return

        names = binding if isinstance(binding, list) else [binding]

        if kind == "enum" and variant is not None:
            for idx, name in enumerate(names):
                pp = self.builder.gep(
                    cond_val,
                    [ir.Constant(self.i32_ty, 0),
                     ir.Constant(self.i32_ty, idx + 1)],
                    name=f"payload_ptr_{name}",
                )
                payload_val = self.builder.load(pp, name=f"payload_{name}")
                var_ptr = self.builder.alloca(self.i64_ty, name=name)
                self.builder.store(payload_val, var_ptr)
                self.symbol_table[name] = var_ptr
        else:
            # Self-binding
            for name in names:
                var_ptr = self.builder.alloca(cond_val.type, name=name)
                self.builder.store(cond_val, var_ptr)
                self.symbol_table[name] = var_ptr

    # ==================================================================
    # Helpers de coerção
    # ==================================================================
    def _is_enum_condition(self, cond_val):
        """Mantido por compatibilidade (usado em testes)."""
        return self._classify_match_kind(cond_val) == "enum"

    def _coerce_self_binding(self, variant, binding, cond_val):
        # Multi-pattern: não tenta converter (variantes são literais)
        if isinstance(variant, list):
            return variant, binding
        
        if not isinstance(variant, str) or not variant:
            return variant, binding

        if self._is_enum_condition(cond_val):
            return variant, binding

        # Tenta int; se for número, não é self-binding
        try:
            int(variant)
            return variant, binding
        except (ValueError, TypeError):
            pass

        # String não-numérica: provavelmente é self-binding
        if binding is None:
            return None, [variant]
        return variant, binding