from llvmlite import ir
from ...ast import StructLiteralExpr, VariableExpr, NumberExpr


class MatchStmtMixin:

    def visit_MatchStmt(self, node):
        cond_val = self.visit(node.condition)
        end_bb = self.builder.append_basic_block(name="match_end")
        self._match_chain(node, cond_val, end_bb)

    def _match_chain(self, node, cond_val, end_bb):
        kind = self._classify_match_kind(cond_val)

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

        self.builder.position_at_end(next_bb)
        if node.default:
            for stmt in node.default:
                if self.builder.block.is_terminated:
                    break
                self.visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)

        self.builder.position_at_end(end_bb)

    def _emit_case(self, i, case, kind, cond_val, variant_map, prev_next_bb, end_bb):
        if len(case) == 4:
            variant, binding, guard, body = case
        else:
            variant, binding, body = case
            guard = None

        is_struct_match = isinstance(variant, StructLiteralExpr)
        if not is_struct_match:
            variant, binding = self._coerce_self_binding(variant, binding, cond_val)

        test_bb  = self.builder.append_basic_block(name=f"match_test_{i}")
        bind_bb  = self.builder.append_basic_block(name=f"match_bind_{i}")
        body_bb  = self.builder.append_basic_block(name=f"match_body_{i}")
        next_bb  = self.builder.append_basic_block(name=f"match_next_{i + 1}")

        self.builder.position_at_end(prev_next_bb)
        self.builder.branch(test_bb)

        self.builder.position_at_end(test_bb)
        
        if is_struct_match:
            pattern_match = self._compute_struct_pattern_match(cond_val, variant)
        else:
            pattern_match = self._compute_pattern_match(kind, cond_val, variant, variant_map, i)
            
        self.builder.cbranch(pattern_match, bind_bb, next_bb)

        self.builder.position_at_end(bind_bb)
        
        if is_struct_match:
            self._emit_struct_bindings(cond_val, variant, binding)
        else:
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

        self.builder.position_at_end(body_bb)
        start = self._begin_scope()
        for stmt in body:
            if self.builder.block.is_terminated:
                break
            self.visit(stmt)
        self._end_scope(start)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)

        return next_bb

    def _classify_match_kind(self, cond_val):
        if cond_val.type == self.i64_ty:
            return "int"
        if (isinstance(cond_val.type, ir.PointerType)
                and isinstance(cond_val.type.pointee, ir.IdentifiedStructType)):
            name = cond_val.type.pointee.name
            if name in self.struct_defs and hasattr(self.struct_defs[name], 'variants'):
                return "enum"
            if name in self.struct_defs:
                return "struct"
        if cond_val.type == self.voidptr_ty:
            return "str"
        return "unknown"

    def _build_variant_map(self, kind, cond_val):
        if kind != "enum":
            return {}
        struct_name = cond_val.type.pointee.name
        struct_def = self.struct_defs[struct_name]
        return {v[0]: i for i, v in enumerate(struct_def.variants)}

    def _compute_struct_pattern_match(self, cond_val, variant_node):
        struct_name = cond_val.type.pointee.name
        fields_map = self.struct_fields.get(struct_name, {})
        
        result = ir.Constant(ir.IntType(1), 1)
        
        for field in variant_node.fields:
            fname = field.name
            fexpr = field.value
            
            # Se for apenas variável (binding), não testa valor
            if isinstance(fexpr, VariableExpr) and fexpr.name not in self.functions_table:
                continue
            # Se for número ou string, testa o valor
            if isinstance(fexpr, (NumberExpr, VariableExpr)):
                elem_index = fields_map.get(fname)
                if elem_index is None:
                    return ir.Constant(ir.IntType(1), 0)
                
                elem_ptr = self.builder.gep(
                    cond_val,
                    [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, elem_index)],
                    name=f"struct_match_ptr_{fname}"
                )
                field_val = self.builder.load(elem_ptr, name=f"struct_match_val_{fname}")
                
                if isinstance(fexpr, NumberExpr):
                    expected_val = ir.Constant(self.i64_ty, int(fexpr.value, 0))
                    cmp_val = self.builder.icmp_signed("==", field_val, expected_val, name=f"struct_match_eq_{fname}")
                else:
                    expected_str = self.visit(fexpr)
                    cmp_res = self.builder.call(self.strcmp, [field_val, expected_str], name=f"struct_match_strcmp_{fname}")
                    cmp_val = self.builder.icmp_signed("==", cmp_res, ir.Constant(ir.IntType(32), 0), name=f"struct_match_streq_{fname}")
                
                result = self.builder.and_(result, cmp_val, name=f"struct_match_and_{fname}")
                
        return result

    def _emit_struct_bindings(self, cond_val, variant_node, binding):
        struct_name = cond_val.type.pointee.name
        fields_map = self.struct_fields.get(struct_name, {})
            
        for field in variant_node.fields:
            fname = field.name
            fexpr = field.value
            if isinstance(fexpr, VariableExpr) and fexpr.name not in self.functions_table:
                elem_index = fields_map.get(fname)
                if elem_index is not None:
                    elem_ptr = self.builder.gep(
                        cond_val,
                        [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, elem_index)],
                        name=f"struct_bind_ptr_{fexpr.name}"
                    )
                    field_val = self.builder.load(elem_ptr, name=f"struct_bind_val_{fexpr.name}")
                    var_ptr = self.builder.alloca(field_val.type, name=fexpr.name)
                    self.builder.store(field_val, var_ptr)
                    self.symbol_table[fexpr.name] = var_ptr

    def _compute_pattern_match(self, kind, cond_val, variant, variant_map, i):
        if isinstance(variant, list):
            if len(variant) == 0:
                return ir.Constant(ir.IntType(1), 0)
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

    def _compute_pattern_match_single(self, kind, cond_val, variant, variant_map, suffix):
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

    def _emit_bindings(self, kind, cond_val, variant, binding):
        if not binding:
            return
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
                field_ty = pp.type.pointee
                payload_val = self.builder.load(pp, name=f"payload_{name}")
                var_ptr = self.builder.alloca(field_ty, name=name)
                self.builder.store(payload_val, var_ptr)
                self.symbol_table[name] = var_ptr
        else:
            for name in names:
                var_ptr = self.builder.alloca(cond_val.type, name=name)
                self.builder.store(cond_val, var_ptr)
                self.symbol_table[name] = var_ptr

    def _is_enum_condition(self, cond_val):
        return self._classify_match_kind(cond_val) == "enum"

    def _coerce_self_binding(self, variant, binding, cond_val):
        if isinstance(variant, list):
            return variant, binding
        if not isinstance(variant, str) or not variant:
            return variant, binding
        if self._is_enum_condition(cond_val):
            return variant, binding
        try:
            int(variant)
            return variant, binding
        except (ValueError, TypeError):
            pass
        if binding is None:
            return None, [variant]
        return variant, binding
