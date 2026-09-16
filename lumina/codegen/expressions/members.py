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

        # NOVO: top-level `let X = <literal>` vira constante inline.
        # Sem isso, `MAP_INITIAL_CAP` usado dentro de funções retorna 0.
        global_node = getattr(self, 'global_var_decls', {}).get(node.name)
        if global_node is not None:
            return self.visit(global_node.value)

        return ir.Constant(self.i64_ty, 0)

    def visit_MemberExpr(self, node):
        """Acesso a campo, com suporte a safe navigation (`?.`)."""
        obj_val = self.visit(node.obj)

        if not (isinstance(obj_val.type, ir.PointerType)
                and isinstance(obj_val.type.pointee, ir.IdentifiedStructType)):
            return ir.Constant(self.i64_ty, 0)

        struct_name = obj_val.type.pointee.name
        field_idx = self.struct_fields.get(struct_name, {}).get(node.member)
        if field_idx is None:
            return ir.Constant(self.i64_ty, 0)

        if not node.is_safe:
            elem_ptr = self.builder.gep(
                obj_val,
                [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, field_idx)],
            )
            return self.builder.load(elem_ptr, name=node.member + "_load")

        # Safe nav: se obj_val for null, retorna 0; senão, faz o load
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

    # ------------------------------------------------------------------
    # Index normal: arr[i]
    # ------------------------------------------------------------------
    def visit_IndexExpr(self, node):
        """Index simples: `arr[i]`.

        Slicing (`arr[a..b]`) é tratado em `visit_SliceExpr` — nó dedicado.
        """
        arr_val = self.visit(node.array)
        idx_val = self.visit(node.index)

        if isinstance(arr_val.type, ir.PointerType):
            if isinstance(arr_val.type.pointee, ir.ArrayType):
                elem_ptr = self.builder.gep(arr_val, [ir.Constant(self.i32_ty, 0), idx_val])
                raw = self.builder.load(elem_ptr, name="arr_idx_load")
            else:
                elem_ptr = self.builder.gep(arr_val, [idx_val])
                raw = self.builder.load(elem_ptr, name="ptr_idx_load")

            # Normaliza para i64 — cobre alloc_bytes (i8*), str (i8*),
            # arrays de bool (i1*) e de ponteiros.
            return self._normalize_loaded(raw, name_hint="idx")

        return ir.Constant(self.i64_ty, 0)

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