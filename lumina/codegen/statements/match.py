from llvmlite import ir


class MatchStmtMixin:

    def visit_MatchStmt(self, node):
        # MatchStmt.cases é 4-tuple: (variant, bindings, guard, body).
        # bindings pode ser None, [name] ou [name1, name2].
        has_guard = any(len(c) >= 4 and c[2] is not None for c in node.cases)

        cond_val = self.visit(node.condition)
        end_bb = self.builder.append_basic_block(name="match.end")

        if has_guard:
            self._codegen_match_with_guard(node, cond_val, end_bb)
            return

        # Caso 1: match sobre i64
        if cond_val.type == self.i64_ty:
            default_bb = self.builder.append_basic_block(name="match.default")
            sw = self.builder.switch(cond_val, default_bb)

            for case in node.cases:
                if len(case) == 4:
                    val_node, var_name, _guard, body = case
                else:
                    val_node, var_name, body = case
                case_bb = self.builder.append_basic_block(name="match.case")
                if isinstance(val_node, str):
                    try:
                        val = ir.Constant(self.i64_ty, int(val_node))
                    except ValueError:
                        continue
                else:
                    val = self.visit(val_node)
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
            return

        # Caso 2: match sobre enum {i32 tag, i64 payload_0, ...}
        if isinstance(cond_val.type, ir.PointerType) and isinstance(cond_val.type.pointee, ir.IdentifiedStructType):
            struct_name = cond_val.type.pointee.name
            if struct_name not in self.struct_defs:
                return
            struct_def = self.struct_defs[struct_name]
            if not hasattr(struct_def, 'variants'):
                return

            variant_map = {v[0]: i for i, v in enumerate(struct_def.variants)}

            tag_ptr = self.builder.gep(cond_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)], name="match_tag_ptr")
            tag_val = self.builder.load(tag_ptr, name="match_tag")

            default_bb = self.builder.append_basic_block(name="match.default")
            sw = self.builder.switch(tag_val, default_bb)

            for case in node.cases:
                if len(case) == 4:
                    variant_name, var_name, _guard, body = case
                else:
                    variant_name, var_name, body = case
                if variant_name not in variant_map:
                    continue
                case_idx = variant_map[variant_name]
                case_bb = self.builder.append_basic_block(name=f"match.{variant_name.lower()}")
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
            return

    def _codegen_match_with_guard(self, node, cond_val, end_bb):
        """Match com guards: if/else encadeado.

        Case self-binding (`case n if n > 10:`): o binding precisa estar
        disponível DENTRO do guard, então declaramos antes.
        """
        for i, case in enumerate(node.cases):
            if len(case) == 4:
                variant, binding, guard, body = case
            else:
                variant, binding, body = case
                guard = None

            test_bb = self.builder.append_basic_block(name=f"match.guard_test.{i}")
            body_bb = self.builder.append_basic_block(name=f"match.guard_body.{i}")
            next_bb = self.builder.append_basic_block(name=f"match.guard_next.{i}")

            self.builder.branch(test_bb)
            self.builder.position_at_end(test_bb)

            # Self-binding: `n` recebe cond_val aqui, antes do guard
            if variant is None and binding:
                binding_name = binding[0] if isinstance(binding, list) else binding
                var_ptr = self.builder.alloca(cond_val.type, name=binding_name)
                self.builder.store(cond_val, var_ptr)
                self.symbol_table[binding_name] = var_ptr

            if variant is None:
                pattern_match = ir.Constant(ir.IntType(1), 1)
            elif cond_val.type == self.i64_ty:
                if isinstance(variant, str):
                    try:
                        case_val = ir.Constant(self.i64_ty, int(variant))
                        pattern_match = self.builder.icmp_signed("==", cond_val, case_val, name=f"match_eq_{i}")
                    except ValueError:
                        self.builder.branch(next_bb)
                        self.builder.position_at_end(next_bb)
                        continue
                else:
                    case_val = self.visit(variant)
                    pattern_match = self.builder.icmp_signed("==", cond_val, case_val, name=f"match_eq_{i}")
            else:
                pattern_match = ir.Constant(ir.IntType(1), 1)

            if guard:
                self.builder.position_at_end(test_bb)
                guard_val = self.visit(guard)
                if guard_val.type != ir.IntType(1):
                    guard_val = self.builder.icmp_signed("!=", guard_val, ir.Constant(guard_val.type, 0), name=f"guard_cond_{i}")
                final_cond = self.builder.and_(pattern_match, guard_val, name=f"match_and_{i}")
            else:
                final_cond = pattern_match

            self.builder.cbranch(final_cond, body_bb, next_bb)

            self.builder.position_at_end(body_bb)

            if binding and variant is not None:
                names = binding if isinstance(binding, list) else [binding]
                if isinstance(cond_val.type, ir.PointerType) and isinstance(cond_val.type.pointee, ir.IdentifiedStructType):
                    for i2, name in enumerate(names):
                        pp = self.builder.gep(
                            cond_val,
                            [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i2 + 1)],
                            name=f"payload_ptr_{i2}",
                        )
                        payload_val = self.builder.load(pp, name=f"payload_{i2}")
                        var_ptr = self.builder.alloca(self.i64_ty, name=name)
                        self.builder.store(payload_val, var_ptr)
                        self.symbol_table[name] = var_ptr
                else:
                    for name in names:
                        var_ptr = self.builder.alloca(self.i64_ty, name=name)
                        self.builder.store(cond_val, var_ptr)
                        self.symbol_table[name] = var_ptr

            for stmt in body:
                self.visit(stmt)
            if not self.builder.block.is_terminated:
                self.builder.branch(end_bb)

            self.builder.position_at_end(next_bb)

        if node.default:
            for stmt in node.default:
                self.visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)

        self.builder.position_at_end(end_bb)
