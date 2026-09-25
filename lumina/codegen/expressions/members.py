from llvmlite import ir
from ...ast import BinaryExpr, SliceExpr, VariableExpr


class MembersMixin:

    def _normalize_loaded(self, val, name_hint="load"):
        if isinstance(val.type, ir.IntType) and val.type.width < 64:
            if val.type.width == 1:
                return self.builder.zext(val, self.i64_ty, name=f"{name_hint}_zext")
            return self.builder.sext(val, self.i64_ty, name=f"{name_hint}_sext")
        if isinstance(val.type, ir.PointerType):
            return self.builder.ptrtoint(val, self.i64_ty, name=f"{name_hint}_ptrtoint")
        return val

    def visit_VariableExpr(self, node):
        ptr = self.symbol_table.get(node.name)
        if ptr:
            return self.builder.load(ptr, name=node.name + "_load")

        lookup = self._find_enum_variant(node.name)
        if lookup is not None:
            enum_name, variant_idx = lookup
            enum_def = self.struct_defs[enum_name]
            for v in enum_def.variants:
                if v[0] != node.name:
                    continue
                payloads = v[1] if len(v) > 1 else []
                if not payloads:
                    type_params = getattr(enum_def, 'type_params', None) or []
                    if type_params:
                        default_args = ["int"] * len(type_params)
                        concrete = f"{enum_name}<{','.join(default_args)}>"
                        return self._construct_enum(concrete, variant_idx, [])
                    return self._construct_enum(enum_name, variant_idx, [])
                break

        if node.name in self.functions_table:
            func, _ = self.functions_table[node.name]
            return self._wrap_fn_as_closure(func, name_hint=node.name)

        gv = getattr(self, 'global_mut_vars', {}).get(node.name)
        if gv is not None:
            return self.builder.load(gv, name=f"g_{node.name}_load")

        global_node = getattr(self, 'global_var_decls', {}).get(node.name)
        if global_node is not None:
            return self.visit(global_node.value)

        return ir.Constant(self.i64_ty, 0)

    def visit_MemberExpr(self, node):
        obj_val = self.visit(node.obj)

        if not (isinstance(obj_val.type, ir.PointerType)
                and isinstance(obj_val.type.pointee, ir.IdentifiedStructType)):
            return ir.Constant(self.i64_ty, 0)

        struct_name = obj_val.type.pointee.name
        field_idx = self.struct_fields.get(struct_name, {}).get(node.member)
        if field_idx is None:
            return ir.Constant(self.i64_ty, 0)

        safe = node.is_safe or getattr(self, '_safe_mode', False)

        if not safe:
            elem_ptr = self.builder.gep(
                obj_val,
                [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, field_idx)],
            )
            return self.builder.load(elem_ptr, name=node.member + "_load")

        null_ptr = ir.Constant(obj_val.type, None)
        is_null = self.builder.icmp_signed("==", obj_val, null_ptr, name="safe_nav_isnull")

        null_bb = self.builder.append_basic_block(name="safe_nav_null")
        ok_bb = self.builder.append_basic_block(name="safe_nav_ok")
        end_bb = self.builder.append_basic_block(name="safe_nav_end")

        self.builder.cbranch(is_null, null_bb, ok_bb)

        self.builder.position_at_end(null_bb)
        self.builder.branch(end_bb)

        self.builder.position_at_end(ok_bb)
        elem_ptr = self.builder.gep(
            obj_val,
            [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, field_idx)],
        )
        field_val = self.builder.load(elem_ptr, name=node.member + "_load")
        self.builder.branch(end_bb)

        self.builder.position_at_end(end_bb)
        if isinstance(field_val.type, ir.PointerType):
            default_val = ir.Constant(field_val.type, None)
        else:
            default_val = ir.Constant(field_val.type, 0)
        phi = self.builder.phi(field_val.type, name="safe_nav_result")
        phi.add_incoming(default_val, null_bb)
        phi.add_incoming(field_val, ok_bb)
        return phi

    def visit_IndexExpr(self, node):
        arr_val = self.visit(node.array)
        idx_val = self.visit(node.index)

        if not isinstance(arr_val.type, ir.PointerType):
            return ir.Constant(self.i64_ty, 0)

        if getattr(self, '_safe_mode', False):
            null_ptr = ir.Constant(arr_val.type, None)
            is_null = self.builder.icmp_signed("==", arr_val, null_ptr, name="safe_idx_isnull")

            null_bb = self.builder.append_basic_block(name="safe_idx_null")
            ok_bb = self.builder.append_basic_block(name="safe_idx_ok")
            end_bb = self.builder.append_basic_block(name="safe_idx_end")

            self.builder.cbranch(is_null, null_bb, ok_bb)

            self.builder.position_at_end(ok_bb)
            raw = self._load_index(arr_val, idx_val)
            self.builder.branch(end_bb)

            self.builder.position_at_end(null_bb)
            if isinstance(raw.type, ir.PointerType):
                default_val = ir.Constant(raw.type, None)
            elif raw.type == self.f64_ty:
                default_val = ir.Constant(raw.type, 0.0)
            else:
                default_val = ir.Constant(raw.type, 0)
            self.builder.branch(end_bb)

            self.builder.position_at_end(end_bb)
            phi = self.builder.phi(raw.type, name="safe_idx_result")
            phi.add_incoming(default_val, null_bb)
            phi.add_incoming(raw, ok_bb)
            return phi

        return self._load_index(arr_val, idx_val)

    def _load_index(self, arr_val, idx_val):
        if isinstance(arr_val.type.pointee, ir.ArrayType):
            elem_ptr = self.builder.gep(arr_val, [ir.Constant(self.i32_ty, 0), idx_val])
            elem_ty = elem_ptr.type.pointee
            raw = self.builder.load(elem_ptr, name="arr_idx_load")
        else:
            elem_ty = arr_val.type.pointee
            elem_ptr = self.builder.gep(arr_val, [idx_val])
            raw = self.builder.load(elem_ptr, name="ptr_idx_load")

        if elem_ty == self.i64_ty:
            return raw
        if elem_ty == self.f64_ty:
            return raw
        if isinstance(elem_ty, ir.PointerType):
            return raw
        if isinstance(elem_ty, ir.IntType) and elem_ty.width < 64:
            if elem_ty.width == 1:
                return self.builder.zext(raw, self.i64_ty, name="idx_zext")
            return self.builder.sext(raw, self.i64_ty, name="idx_sext")
        return raw

    # ==================================================================
    # Helper: coerce um valor inteiro para i64.
    #
    # `i1` (bool) → `zext` (1 → 1, 0 → 0).
    # `iN` (N<64, N≠1) → `sext` (preserva sinal).
    # `i64` → no-op.
    #
    # **Crítico:** usar `sext` em `i1` produz `-1` (todos os bits 1),
    # não `1`. Isso quebra slices cujo bound é uma comparação
    # (`v[0..n == 4]`), transformando `length = 1` em `length = -1` e
    # levando a `malloc(-8)` → NULL → SIGSEGV em `s[0]`.
    # ==================================================================
    def _to_i64_int(self, val, name_hint):
        """Converte `val` para i64 com semântica correta para i1."""
        if val.type == self.i64_ty:
            return val
        if isinstance(val.type, ir.IntType):
            if val.type.width == 1:
                return self.builder.zext(val, self.i64_ty, name=f"{name_hint}_zext")
            return self.builder.sext(val, self.i64_ty, name=f"{name_hint}_sext")
        # Fallback: não é int — provavelmente erro já detectado em semantic.
        return val

    def visit_SliceExpr(self, node):
        """`arr[start..end]` com bounds opcionais.

        FIX (Fase 10c): bounds convertidos para i64 via `_to_i64_int`,
        que usa `zext` para `i1` (comportamento correto para `bool`).
        Antes, `sext` transformava `n == 4` (i1 = 1) em `i64 -1`.
        """
        arr_val = self.visit(node.array)

        if node.start is not None:
            start_val = self.visit(node.start)
            start_val = self._to_i64_int(start_val, "slice_start")
        else:
            start_val = ir.Constant(self.i64_ty, 0)

        is_string = (
            arr_val.type == self.voidptr_ty
            or (isinstance(arr_val.type, ir.PointerType) and arr_val.type.pointee == self.i8_ty)
        )

        if node.end is not None:
            end_val = self.visit(node.end)
            end_val = self._to_i64_int(end_val, "slice_end")
        else:
            if is_string:
                end_val = self.builder.call(self.strlen, [arr_val], name="slice_strlen")
            else:
                arr_len = None
                if isinstance(node.array, VariableExpr):
                    arr_len = getattr(self, 'array_lengths', {}).get(node.array.name)
                if arr_len is not None:
                    end_val = ir.Constant(self.i64_ty, arr_len)
                else:
                    end_val = start_val

        length = self.builder.sub(end_val, start_val, name="slice_len")

        if is_string:
            length_plus = self.builder.add(
                length, ir.Constant(self.i64_ty, 1), name="slice_len_plus"
            )
            buf = self.builder.call(self.malloc, [length_plus], name="slice_buf")
            start_ptr = self.builder.gep(arr_val, [start_val], name="slice_start_ptr")
            self.builder.call(self.strncpy, [buf, start_ptr, length], name="slice_cpy")
            end_ptr = self.builder.gep(buf, [length], name="slice_end_ptr")
            self.builder.store(ir.Constant(self.i8_ty, 0), end_ptr)
            return buf

        if isinstance(arr_val.type, ir.PointerType):
            elem_ty = arr_val.type.pointee

            if isinstance(elem_ty, ir.IntType):
                elem_bytes = max(1, elem_ty.width // 8)
            else:
                elem_bytes = 8

            byte_count = self.builder.mul(
                length, ir.Constant(self.i64_ty, elem_bytes), name="slice_arr_size"
            )
            raw_buf = self.builder.call(self.malloc, [byte_count], name="slice_arr_buf")
            buf = self.builder.bitcast(raw_buf, elem_ty.as_pointer(), name="slice_arr_cast")

            loop_bb = self.builder.append_basic_block(name="slice_loop")
            end_bb = self.builder.append_basic_block(name="slice_end")
            pred_bb = self.builder.block

            self.builder.branch(loop_bb)
            self.builder.position_at_end(loop_bb)

            i = self.builder.phi(self.i64_ty, name="slice_i")
            i.add_incoming(ir.Constant(self.i64_ty, 0), pred_bb)

            src_idx = self.builder.add(start_val, i, name="slice_src_idx")
            src_ptr = self.builder.gep(arr_val, [src_idx], name="slice_src_ptr")
            val_loaded = self.builder.load(src_ptr, name="slice_val")

            dst_ptr = self.builder.gep(buf, [i], name="slice_dst_ptr")
            self.builder.store(val_loaded, dst_ptr)

            next_i = self.builder.add(i, ir.Constant(self.i64_ty, 1), name="slice_i_next")
            i.add_incoming(next_i, self.builder.block)

            cond = self.builder.icmp_signed("<", next_i, length, name="slice_cond")
            self.builder.cbranch(cond, loop_bb, end_bb)

            self.builder.position_at_end(end_bb)
            return buf

        return ir.Constant(self.i64_ty, 0)