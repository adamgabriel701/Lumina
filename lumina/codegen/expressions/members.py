from llvmlite import ir
from ...ast import BinaryExpr


class MembersMixin:

    def visit_VariableExpr(self, node):
        ptr = self.symbol_table.get(node.name)
        if not ptr:
            return ir.Constant(self.i64_ty, 0)
        return self.builder.load(ptr, name=node.name + "_load")

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
            elem_ptr = self.builder.gep(obj_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, field_idx)])
            return self.builder.load(elem_ptr, name=node.member + "_load")

        # Safe nav: se obj_val for null, retorna 0; senão, faz o load
        null_ptr = ir.Constant(obj_val.type, None)
        is_null = self.builder.icmp_signed("==", obj_val, null_ptr, name="safe_nav_isnull")

        null_bb = self.builder.append_basic_block(name="safe_nav.null")
        ok_bb = self.builder.append_basic_block(name="safe_nav.ok")
        end_bb = self.builder.append_basic_block(name="safe_nav.end")

        self.builder.cbranch(is_null, null_bb, ok_bb)

        self.builder.position_at_end(null_bb)
        self.builder.branch(end_bb)

        self.builder.position_at_end(ok_bb)
        elem_ptr = self.builder.gep(obj_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, field_idx)])
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
        """Index (`arr[i]`) ou slicing (`arr[a..b]`)."""
        arr_val = self.visit(node.array)

        # --- Slicing: arr[start..end] ---
        if isinstance(node.index, BinaryExpr) and node.index.op == '..':
            start_val = self.visit(node.index.left)
            end_val = self.visit(node.index.right)

            if start_val.type != self.i64_ty:
                start_val = self.builder.sext(start_val, self.i64_ty, name="slice_start_sext")
            if end_val.type != self.i64_ty:
                end_val = self.builder.sext(end_val, self.i64_ty, name="slice_end_sext")

            length = self.builder.sub(end_val, start_val, name="slice_len")

            # String slicing: retorna substring
            if arr_val.type == self.voidptr_ty or (isinstance(arr_val.type, ir.PointerType) and arr_val.type.pointee == self.i8_ty):
                length_plus = self.builder.add(length, ir.Constant(self.i64_ty, 1), name="slice_len_plus")
                buf = self.builder.call(self.malloc, [length_plus], name="slice_buf")
                start_ptr = self.builder.gep(arr_val, [start_val], name="slice_start_ptr")
                self.builder.call(self.strncpy, [buf, start_ptr, length], name="slice_cpy")
                end_ptr = self.builder.gep(buf, [length], name="slice_end_ptr")
                self.builder.store(ir.Constant(self.i8_ty, 0), end_ptr)
                return buf

            # Array slicing (ponteiro): copia elemento por elemento
            elif isinstance(arr_val.type, ir.PointerType):
                buf_size = self.builder.mul(length, ir.Constant(self.i64_ty, 8), name="slice_arr_size")
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
                if val_loaded.type != self.i64_ty:
                    if isinstance(val_loaded.type, ir.PointerType):
                        val_loaded = self.builder.ptrtoint(val_loaded, self.i64_ty, name="slice_val_cast")
                    elif val_loaded.type.width < 64:
                        val_loaded = self.builder.sext(val_loaded, self.i64_ty, name="slice_val_sext")

                dst_ptr = self.builder.gep(buf, [i], name="slice_dst_ptr")
                self.builder.store(val_loaded, dst_ptr)

                next_i = self.builder.add(i, ir.Constant(self.i64_ty, 1), name="slice_i_next")
                i.add_incoming(next_i, self.builder.block)

                cond = self.builder.icmp_signed("<", next_i, length, name="slice_cond")
                self.builder.cbranch(cond, loop_bb, end_bb)

                self.builder.position_at_end(end_bb)
                return buf

        # --- Index normal ---
        idx_val = self.visit(node.index)
        if isinstance(arr_val.type, ir.PointerType):
            if isinstance(arr_val.type.pointee, ir.ArrayType):
                elem_ptr = self.builder.gep(arr_val, [ir.Constant(self.i32_ty, 0), idx_val])
                return self.builder.load(elem_ptr, name="arr_idx_load")
            else:
                elem_ptr = self.builder.gep(arr_val, [idx_val])
                return self.builder.load(elem_ptr, name="ptr_idx_load")
        return ir.Constant(self.i64_ty, 0)
