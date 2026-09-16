from llvmlite import ir
from ...ast import (
    NumberExpr, BoolExpr, StringExpr, InterpolatedStringExpr, ComptimeExpr,
    NoneExpr,
)


class LiteralsMixin:

    def visit_NumberExpr(self, node):
        if node.value.startswith('0x') or node.value.startswith('0X'):
            return ir.Constant(self.f64_ty, float(int(node.value, 16))) if node.is_float else ir.Constant(self.i64_ty, int(node.value, 16))
        return ir.Constant(self.f64_ty, float(node.value)) if node.is_float else ir.Constant(self.i64_ty, int(node.value))

    def visit_BoolExpr(self, node):
        return ir.Constant(ir.IntType(1), 1 if node.value else 0)

    def visit_StringExpr(self, node):
        return self.create_global_string(node.value)

    def visit_NoneExpr(self, node):
        """NOVO (A): Constrói Option::None (tag=1, sem payload).

        O prelude declara `enum Option: Some(int); None`, então Option
        está em struct_types. Se não estiver, retorna 0.
        """
        if "Option" in self.struct_types:
            return self._construct_enum("Option", 1, [])
        return ir.Constant(self.i64_ty, 0)

    def visit_InterpolatedStringExpr(self, node):
        return self.codegen_fstring(node.parts)

    def codegen_fstring(self, elements):
        """Cria um buffer no stack e concatena todas as partes de uma F-string."""
        buf_size = 1024
        buf_ty = ir.ArrayType(self.i8_ty, buf_size)
        buf_ptr = self.builder.alloca(buf_ty, name="fstr_buf")

        i8_ptr = self.i8_ty.as_pointer()
        buf_i8_ptr = self.builder.bitcast(buf_ptr, i8_ptr, name="fstr_buf_i8")

        self.builder.store(ir.Constant(self.i8_ty, 0), buf_i8_ptr)

        for i, el in enumerate(elements):
            if isinstance(el, StringExpr):
                str_val = self.visit(el)
                self.builder.call(self.strcat, [buf_i8_ptr, str_val], name=f"fstr_cat_{i}")
            else:
                val = self.visit(el)
                if val.type == self.i64_ty:
                    int_buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 32), name=f"fstr_int_buf_{i}")
                    int_buf_ptr = self.builder.bitcast(int_buf, i8_ptr, name=f"fstr_int_ptr_{i}")
                    fmt_str = self.create_global_string("%ld")
                    self.builder.call(self.snprintf, [int_buf_ptr, ir.Constant(self.i64_ty, 32), fmt_str, val], name=f"fstr_snprintf_{i}")
                    self.builder.call(self.strcat, [buf_i8_ptr, int_buf_ptr], name=f"fstr_int_cat_{i}")
                elif val.type == self.voidptr_ty:
                    self.builder.call(self.strcat, [buf_i8_ptr, val], name=f"fstr_str_cat_{i}")

        return buf_i8_ptr

    def visit_ComptimeExpr(self, node):
        # NOVO (B): se o semantic fez constant folding, usa o valor dobrado
        if getattr(node, 'folded', None) is not None:
            return self.visit(node.folded)
        return self.visit(node.expr)