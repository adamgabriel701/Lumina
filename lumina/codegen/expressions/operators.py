from llvmlite import ir
from ...ast import (
    VariableExpr, BinaryExpr, UnaryExpr, CastExpr,
    AddressOfExpr, DerefExpr, PropagateExpr,
)


class OperatorsMixin:

    # ------------------------------------------------------------------
    # Helpers de normalização
    # ------------------------------------------------------------------
    def _normalize_ints(self, left, right):
        """Se um lado é i64 e o outro é iN (N<64), estende o menor.

        Cobre i1 (bool), i8 (char), i32, etc. Também converte ponteiros
        em i64 quando o outro lado é int (permitido por design).
        """
        # ptr ↔ int
        if isinstance(left.type, ir.PointerType) and right.type == self.i64_ty:
            left = self.builder.ptrtoint(left, self.i64_ty, name="bin_ptrtoint_l")
        elif left.type == self.i64_ty and isinstance(right.type, ir.PointerType):
            right = self.builder.ptrtoint(right, self.i64_ty, name="bin_ptrtoint_r")

        # int de larguras diferentes
        if (isinstance(left.type, ir.IntType) and isinstance(right.type, ir.IntType)
                and left.type != right.type):
            target = self.i64_ty
            if left.type.width < 64:
                if left.type.width == 1:
                    left = self.builder.zext(left, target, name="bin_zext_l")
                else:
                    left = self.builder.sext(left, target, name="bin_sext_l")
            if right.type.width < 64:
                if right.type.width == 1:
                    right = self.builder.zext(right, target, name="bin_zext_r")
                else:
                    right = self.builder.sext(right, target, name="bin_sext_r")

        return left, right

    def _try_struct_operator(self, node, left, right):
        """Se ambos são ponteiros para o mesmo struct, procura
        Struct___op__ e chama. Retorna o valor ou None.
        """
        if not (isinstance(left.type, ir.PointerType)
                and isinstance(left.type.pointee, ir.IdentifiedStructType)):
            return None
        if left.type != right.type:
            return None

        struct_name = left.type.pointee.name
        op_map = {
            '+': '__add__', '-': '__sub__', '*': '__mul__', '/': '__div__',
            '==': '__eq__', '!=': '__ne__', '<': '__lt__', '>': '__gt__',
            '<=': '__le__', '>=': '__ge__',
        }
        method_name = op_map.get(node.op)
        if not method_name:
            return None

        real_name = f"{struct_name}_{method_name}"
        if real_name not in self.functions_table:
            return None

        func = self.functions_table[real_name][0]
        return self.builder.call(func, [left, right], name=f"op_{real_name}")

    # ------------------------------------------------------------------
    # Binários
    # ------------------------------------------------------------------
    def visit_BinaryExpr(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if left is None or right is None:
            return ir.Constant(self.i64_ty, 0)

        # Concatenação de strings com '+'
        if node.op == '+' and left.type == self.voidptr_ty and right.type == self.voidptr_ty:
            len1 = self.builder.call(self.strlen, [left], name="sconcat_len1")
            len2 = self.builder.call(self.strlen, [right], name="sconcat_len2")
            sum_len = self.builder.add(len1, len2, name="sconcat_sum")
            total_len = self.builder.add(sum_len, ir.Constant(self.i64_ty, 1), name="sconcat_total")
            buf = self.builder.call(self.malloc, [total_len], name="sconcat_buf")
            self.builder.call(self.strcpy, [buf, left], name="sconcat_cpy")
            self.builder.call(self.strcat, [buf, right], name="sconcat_cat")
            return buf

        # Overload de operador em struct (NOVO)
        struct_result = self._try_struct_operator(node, left, right)
        if struct_result is not None:
            return struct_result

        # Coerção: se um lado é string, converte o número
        if left.type == self.voidptr_ty and right.type in (self.i64_ty, self.f64_ty):
            if right.type == self.f64_ty:
                fmt = self.create_global_string("%f")
            else:
                fmt = self.create_global_string("%ld")
            buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 64), name="num_to_str")
            buf_ptr = self.builder.bitcast(buf, self.voidptr_ty, name="num_to_str_ptr")
            self.builder.call(self.snprintf, [buf_ptr, ir.Constant(self.i64_ty, 64), fmt, right], name="num_to_str_call")
            right = buf_ptr
        elif right.type == self.voidptr_ty and left.type in (self.i64_ty, self.f64_ty):
            if left.type == self.f64_ty:
                fmt = self.create_global_string("%f")
            else:
                fmt = self.create_global_string("%ld")
            buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 64), name="num_to_str")
            buf_ptr = self.builder.bitcast(buf, self.voidptr_ty, name="num_to_str_ptr")
            self.builder.call(self.snprintf, [buf_ptr, ir.Constant(self.i64_ty, 64), fmt, left], name="num_to_str_call")
            left = buf_ptr

        # Matemática
        if node.op in ('+', '-', '*', '/', '%'):
            if left.type == self.voidptr_ty or right.type == self.voidptr_ty:
                return ir.Constant(self.i64_ty, 0)

            # NOVO: normaliza ints e ponteiros antes de operar
            left, right = self._normalize_ints(left, right)

            if left.type == self.f64_ty or right.type == self.f64_ty:
                left = self.to_float_if_needed(left)
                right = self.to_float_if_needed(right)
                if node.op == '+':
                    return self.builder.fadd(left, right, name="fadd")
                elif node.op == '-':
                    return self.builder.fsub(left, right, name="fsub")
                elif node.op == '*':
                    return self.builder.fmul(left, right, name="fmul")
                elif node.op == '/':
                    return self.builder.fdiv(left, right, name="fdiv")
            else:
                if node.op == '+':
                    return self.builder.add(left, right, name="add")
                elif node.op == '-':
                    return self.builder.sub(left, right, name="sub")
                elif node.op == '*':
                    return self.builder.mul(left, right, name="mul")
                elif node.op == '/':
                    return self.builder.sdiv(left, right, name="div")
                elif node.op == '%':
                    return self.builder.srem(left, right, name="mod")

        # Comparações
        if node.op in ('==', '!=', '<', '>', '<=', '>='):
            # NOVO: normaliza antes de comparar
            if left.type != right.type:
                left, right = self._normalize_ints(left, right)
            if left.type != right.type:
                # Última tentativa: ptrtoint se um é ponteiro e o outro é int
                if isinstance(left.type, ir.PointerType) and right.type == self.i64_ty:
                    left = self.builder.ptrtoint(left, self.i64_ty, name="cmp_ptrtoint_l")
                elif left.type == self.i64_ty and isinstance(right.type, ir.PointerType):
                    right = self.builder.ptrtoint(right, self.i64_ty, name="cmp_ptrtoint_r")

            if left.type == self.f64_ty or right.type == self.f64_ty:
                left = self.to_float_if_needed(left)
                right = self.to_float_if_needed(right)
                return self.builder.fcmp_ordered(node.op, left, right, name="fcmp")
            else:
                return self.builder.icmp_signed(node.op, left, right, name="icmp")

        return ir.Constant(self.i64_ty, 0)

    def visit_UnaryExpr(self, node):
        val = self.visit(node.val)
        if node.op == '-':
            return self.builder.neg(val, name="neg") if val.type == self.i64_ty else self.builder.fneg(val, name="fneg")
        elif node.op == 'not':
            zero = ir.Constant(val.type, 0)
            return self.builder.icmp_signed("!=", val, zero, name="not_cond")
        return val

    def visit_CastExpr(self, node):
        val = self.visit(node.expr)
        target_ty = self.get_llvm_type(node.target_type)
        if val.type == target_ty:
            return val
        if val.type == self.i64_ty and target_ty == self.f64_ty:
            return self.builder.sitofp(val, self.f64_ty, name="int_to_float")
        elif val.type == self.f64_ty and target_ty == self.i64_ty:
            return self.builder.fptosi(val, self.i64_ty, name="float_to_int")
        elif isinstance(val.type, ir.PointerType) and target_ty == self.i64_ty:
            return self.builder.ptrtoint(val, self.i64_ty, name="ptr_to_int")
        elif val.type == self.i64_ty and isinstance(target_ty, ir.PointerType):
            return self.builder.inttoptr(val, target_ty, name="int_to_ptr")
        # NOVO: casts entre ints de larguras diferentes
        elif isinstance(val.type, ir.IntType) and isinstance(target_ty, ir.IntType):
            if val.type.width < target_ty.width:
                if val.type.width == 1:
                    return self.builder.zext(val, target_ty, name="cast_zext")
                return self.builder.sext(val, target_ty, name="cast_sext")
            return self.builder.trunc(val, target_ty, name="cast_trunc")
        return val

    def visit_AddressOfExpr(self, node):
        if isinstance(node.val, VariableExpr):
            ptr = self.symbol_table.get(node.val.name)
            if ptr:
                return ptr
        return self.visit(node.val)

    def visit_DerefExpr(self, node):
        ptr = self.visit(node.val)
        if not isinstance(ptr.type, ir.PointerType):
            return ir.Constant(self.i64_ty, 0)
        return self.builder.load(ptr, name="deref_load")

    def visit_PropagateExpr(self, node):
        result_ptr = self.visit(node.val)

        if not (isinstance(result_ptr.type, ir.PointerType)
                and isinstance(result_ptr.type.pointee, ir.IdentifiedStructType)):
            return result_ptr

        struct_name = result_ptr.type.pointee.name
        if struct_name != "Result":
            return result_ptr

        tag_ptr = self.builder.gep(
            result_ptr,
            [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)],
            name="prop_tag_ptr",
        )
        tag_val = self.builder.load(tag_ptr, name="prop_tag")

        is_err = self.builder.icmp_signed(
            "!=", tag_val, ir.Constant(self.i32_ty, 0), name="prop_iserr",
        )

        err_bb = self.builder.append_basic_block(name="prop_err")
        ok_bb = self.builder.append_basic_block(name="prop_ok")

        self.builder.cbranch(is_err, err_bb, ok_bb)

        self.builder.position_at_end(err_bb)
        func_ret_ty = self.functions_table[self.current_func_name][1].return_type
        if result_ptr.type != func_ret_ty:
            if isinstance(func_ret_ty, ir.PointerType):
                ret_val = self.builder.bitcast(result_ptr, func_ret_ty, name="prop_ret_cast")
            else:
                ret_val = self.builder.ptrtoint(result_ptr, func_ret_ty, name="prop_ret_int")
        else:
            ret_val = result_ptr
        self.builder.ret(ret_val)

        self.builder.position_at_end(ok_bb)
        payload_ptr = self.builder.gep(
            result_ptr,
            [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)],
            name="prop_payload_ptr",
        )
        payload_val = self.builder.load(payload_ptr, name="prop_payload")

        return payload_val