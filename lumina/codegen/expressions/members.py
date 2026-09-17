from llvmlite import ir
from ...ast import BinaryExpr, SliceExpr


class MembersMixin:

    # ------------------------------------------------------------------
    # Helper: normaliza um valor lido de memória para i64.
    # O resto do codegen assume que todo valor "escalar" é i64.
    # - i1  → zext (bool)
    # - iN  → sext (N < 64, ex: i8 de alloc_bytes)
    # - ptr → ptrtoint
    # - f64 → mantém (é float, não é escalar inteiro)
    # - i64 → mantém
    # ------------------------------------------------------------------
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

        # Globais mutáveis → carrega da GlobalVariable LLVM.
        gv = getattr(self, 'global_mut_vars', {}).get(node.name)
        if gv is not None:
            return self.builder.load(gv, name=f"g_{node.name}_load")

        # Top-level `let X = <literal>` vira constante inline.
        global_node = getattr(self, 'global_var_decls', {}).get(node.name)
        if global_node is not None:
            return self.visit(global_node.value)

        # NOVO: variante de enum sem payload usada bare (ex: `Stop`).
        # Constrói o enum com tag correta e zero payloads.
        lookup = self._find_enum_variant(node.name)
        if lookup is not None:
            enum_name, variant_idx = lookup
            enum_def = self.struct_defs[enum_name]
            for v in enum_def.variants:
                if v[0] != node.name:
                    continue
                payloads = v[1] if len(v) > 1 else []
                if not payloads:
                    return self._construct_enum(enum_name, variant_idx, [])
                break  # tem payload — só via `Name(args)`

        return ir.Constant(self.i64_ty, 0)

    def visit_MemberExpr(self, node):
        """Acesso a campo. Com `?.` (is_safe) OU `@safe` na função,
        faz null check e retorna 0 se o ponteiro for nil."""
        obj_val = self.visit(node.obj)

        if not (isinstance(obj_val.type, ir.PointerType)
                and isinstance(obj_val.type.pointee, ir.IdentifiedStructType)):
            return ir.Constant(self.i64_ty, 0)

        struct_name = obj_val.type.pointee.name
        field_idx = self.struct_fields.get(struct_name, {}).get(node.member)
        if field_idx is None:
            return ir.Constant(self.i64_ty, 0)

        # Safe se `?.` explícito OU modo @safe ativo
        safe = node.is_safe or getattr(self, '_safe_mode', False)

        if not safe:
            elem_ptr = self.builder.gep(
                obj_val,
                [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, field_idx)],
            )
            return self.builder.load(elem_ptr, name=node.member + "_load")

        # Null check
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
        """Index `arr[i]`. Com `@safe`, checa nil do array."""
        arr_val = self.visit(node.array)
        idx_val = self.visit(node.index)

        if not isinstance(arr_val.type, ir.PointerType):
            return ir.Constant(self.i64_ty, 0)

        # Em modo @safe, checa nil
        if getattr(self, '_safe_mode', False):
            null_ptr = ir.Constant(arr_val.type, None)
            is_null = self.builder.icmp_signed("==", arr_val, null_ptr, name="safe_idx_isnull")

            null_bb = self.builder.append_basic_block(name="safe_idx_null")
            ok_bb = self.builder.append_basic_block(name="safe_idx_ok")
            end_bb = self.builder.append_basic_block(name="safe_idx_end")

            self.builder.cbranch(is_null, null_bb, ok_bb)

            self.builder.position_at_end(null_bb)
            self.builder.branch(end_bb)

            self.builder.position_at_end(ok_bb)
            raw = self._load_index(arr_val, idx_val)
            self.builder.branch(end_bb)

            self.builder.position_at_end(end_bb)
            default_val = ir.Constant(self.i64_ty, 0)
            phi = self.builder.phi(self.i64_ty, name="safe_idx_result")
            phi.add_incoming(default_val, null_bb)
            phi.add_incoming(raw, ok_bb)
            return phi

        return self._load_index(arr_val, idx_val)

    def _load_index(self, arr_val, idx_val):
        """Helper: load real do index (sem null check)."""
        if isinstance(arr_val.type.pointee, ir.ArrayType):
            elem_ptr = self.builder.gep(arr_val, [ir.Constant(self.i32_ty, 0), idx_val])
            raw = self.builder.load(elem_ptr, name="arr_idx_load")
        else:
            elem_ptr = self.builder.gep(arr_val, [idx_val])
            raw = self.builder.load(elem_ptr, name="ptr_idx_load")
        return self._normalize_loaded(raw, name_hint="idx")

    # ------------------------------------------------------------------
    # Slicing: arr[a..b], arr[..b], arr[a..], arr[..]
    # ------------------------------------------------------------------
    def visit_SliceExpr(self, node):
        """`arr[start..end]` com bounds opcionais.

        - Strings: copia bytes e retorna nova string (malloc + strncpy).
        - Arrays: copia elementos i64 para novo buffer.
        - `start` ausente → 0.
        - `end` ausente em string → strlen(arr).
        - `end` ausente em array → limitação conhecida: usa `start` (length=0).
          Fica o TODO de adicionar `len()` para arrays no futuro.
        """
        arr_val = self.visit(node.array)

        # --- Bound inferior ---
        if node.start is not None:
            start_val = self.visit(node.start)
            if start_val.type != self.i64_ty:
                start_val = self.builder.sext(start_val, self.i64_ty, name="slice_start_sext")
        else:
            start_val = ir.Constant(self.i64_ty, 0)

        is_string = (
            arr_val.type == self.voidptr_ty
            or (isinstance(arr_val.type, ir.PointerType) and arr_val.type.pointee == self.i8_ty)
        )

        # --- Bound superior ---
        if node.end is not None:
            end_val = self.visit(node.end)
            if end_val.type != self.i64_ty:
                end_val = self.builder.sext(end_val, self.i64_ty, name="slice_end_sext")
        else:
            if is_string:
                # String sem `end`: usa strlen
                end_val = self.builder.call(self.strlen, [arr_val], name="slice_strlen")
            else:
                # Array sem `end`: limitação — assume length = start (buffer vazio)
                end_val = start_val

        length = self.builder.sub(end_val, start_val, name="slice_len")

        # ------------------------------------------------------------------
        # Caso 1: String → aloca nova string + strncpy
        # ------------------------------------------------------------------
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

        # ------------------------------------------------------------------
        # Caso 2: Array (ponteiro) → copia elemento por elemento
        # ------------------------------------------------------------------
        if isinstance(arr_val.type, ir.PointerType):
            buf_size = self.builder.mul(
                length, ir.Constant(self.i64_ty, 8), name="slice_arr_size"
            )
            buf = self.builder.call(self.malloc, [buf_size], name="slice_arr_buf")
            buf_ty = self.i64_ty.as_pointer()
            buf = self.builder.bitcast(buf, buf_ty, name="slice_arr_cast")

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
            val_loaded = self._normalize_loaded(val_loaded, name_hint="slice_val")

            dst_ptr = self.builder.gep(buf, [i], name="slice_dst_ptr")
            self.builder.store(val_loaded, dst_ptr)

            next_i = self.builder.add(i, ir.Constant(self.i64_ty, 1), name="slice_i_next")
            i.add_incoming(next_i, self.builder.block)

            cond = self.builder.icmp_signed("<", next_i, length, name="slice_cond")
            self.builder.cbranch(cond, loop_bb, end_bb)

            self.builder.position_at_end(end_bb)
            return buf

        # Fallback: tipo desconhecido
        return ir.Constant(self.i64_ty, 0)