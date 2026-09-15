from llvmlite import ir
from ...ast import (
    StringExpr, VariableExpr, StructLiteralExpr,
    StructLiteralField, LambdaExpr,
)


class AggregatesMixin:

    def visit_ArrayExpr(self, node):
        elem_ty = self.i64_ty
        if len(node.elements) > 0:
            first_val = self.visit(node.elements[0])
            elem_ty = first_val.type
            if not isinstance(elem_ty, ir.IntType):
                elem_ty = self.i64_ty

        array_ty = ir.ArrayType(elem_ty, len(node.elements))
        ptr = self.builder.alloca(array_ty, name="array_lit")

        for i, el in enumerate(node.elements):
            el_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)], name=f"arr_el_{i}")
            val = self.visit(el)
            if val.type != elem_ty:
                if isinstance(val.type, ir.PointerType) and isinstance(elem_ty, ir.PointerType):
                    val = self.builder.bitcast(val, elem_ty, name=f"arr_cast_{i}")
                elif isinstance(val.type, ir.IntType) and isinstance(elem_ty, ir.IntType):
                    if val.type.width < elem_ty.width:
                        val = self.builder.sext(val, elem_ty, name=f"arr_sext_{i}")
            self.builder.store(val, el_ptr)
        return ptr

    def visit_StructLiteralExpr(self, node):
        struct_ty = self.get_llvm_type(node.struct_name)
        ptr = self.builder.alloca(struct_ty, name=node.struct_name.lower() + "_lit")

        for field in node.fields:
            if isinstance(field, tuple):
                fname, fexpr = field
            else:
                fname = field.name
                fexpr = field.value

            elem_index = self.struct_fields[node.struct_name].get(fname, 0)
            elem_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, elem_index)], name=fname + "_ptr")
            val = self.visit(fexpr)
            self.builder.store(val, elem_ptr)
        return ptr

    def visit_LambdaExpr(self, node):
        if not hasattr(self, 'lambda_counter'):
            self.lambda_counter = 0
        func_name = f"__lambda_{self.lambda_counter}"
        self.lambda_counter += 1

        ret_ty = self.get_llvm_param_type(node.return_type)

        param_types = []
        for p in node.params:
            if isinstance(p, tuple):
                p_type = p[1]
            else:
                p_type = p.type_ann
            param_types.append(self.get_llvm_param_type(p_type))

        func_type = ir.FunctionType(ret_ty, param_types)
        func = ir.Function(self.module, func_type, name=func_name)

        old_builder = self.builder
        old_symtab = self.symbol_table
        block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        self.symbol_table = {}

        for i, p in enumerate(node.params):
            if isinstance(p, tuple):
                p_name, p_type = p[0], p[1]
            else:
                p_name, p_type = p.name, p.type_ann

            p_ty = self.get_llvm_param_type(p_type)
            ptr = self.builder.alloca(p_ty, name=p_name)
            self.builder.store(func.args[i], ptr)
            self.symbol_table[p_name] = ptr

        # Body: Expr inline vira `ret expr`
        from ...ast.expressions import Expr as ExprBase
        for stmt in node.body:
            if isinstance(stmt, ExprBase):
                val = self.visit(stmt)
                if ret_ty != ir.VoidType() and val.type != ret_ty:
                    if ret_ty == self.i64_ty and val.type == self.f64_ty:
                        val = self.builder.fptosi(val, self.i64_ty, name="lambda_ret_cast")
                    elif ret_ty == self.f64_ty and val.type == self.i64_ty:
                        val = self.builder.sitofp(val, self.f64_ty, name="lambda_ret_cast")
                    elif isinstance(ret_ty, ir.PointerType) and val.type == self.i64_ty:
                        val = self.builder.inttoptr(val, ret_ty, name="lambda_ret_cast")
                    elif ret_ty == self.i64_ty and isinstance(val.type, ir.PointerType):
                        val = self.builder.ptrtoint(val, self.i64_ty, name="lambda_ret_cast")
                self.builder.ret(val)
                break
            else:
                self.visit(stmt)

        if not self.builder.block.is_terminated:
            if ret_ty == ir.VoidType():
                self.builder.ret_void()
            else:
                self.builder.ret(ir.Constant(ret_ty, 0))

        self.builder = old_builder
        self.symbol_table = old_symtab
        return self.builder.bitcast(func, self.voidptr_ty, name="lambda_ptr")
