from llvmlite import ir
from ..ast import (
    NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, 
    ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, TupleExpr, 
    UnaryExpr, PropagateExpr, ComptimeExpr, StructLiteralExpr, MatchExpr, 
    CastExpr, LambdaExpr, ErrorNode
)

class ExpressionCodegen:
    
    def codegen_expr(self, node):
        if isinstance(node, ErrorNode): return ir.Constant(self.i64_ty, 0)
        elif isinstance(node, NumberExpr):
            if node.value.startswith('0x') or node.value.startswith('0X'):
                return ir.Constant(self.f64_ty, float(int(node.value, 16))) if node.is_float else ir.Constant(self.i64_ty, int(node.value, 16))
            return ir.Constant(self.f64_ty, float(node.value)) if node.is_float else ir.Constant(self.i64_ty, int(node.value))
        elif isinstance(node, BoolExpr): return ir.Constant(ir.IntType(1), 1 if node.value else 0)
        elif isinstance(node, StringExpr): return self.create_global_string(node.value)
        elif isinstance(node, UnaryExpr): return self.codegen_unary(node)
        elif isinstance(node, DerefExpr): return self.codegen_deref(node)
        elif isinstance(node, AddressOfExpr): return self.codegen_address_of(node)
        elif isinstance(node, VariableExpr): return self.codegen_variable(node)
        elif isinstance(node, BinaryExpr): return self.codegen_binary(node)
        elif isinstance(node, IndexExpr): return self.codegen_index(node)
        elif isinstance(node, MemberExpr): return self.codegen_member(node)
        elif isinstance(node, CallExpr):
            # CORREÇÃO: Extrai o nome da função com segurança
            func_name = getattr(node.callee, 'name', None)
            
            if node.is_method and func_name in self.functions_table:
                node.is_method = False
                
            if node.is_method:
                return self.codegen_method_call(node, func_name)
            else:
                return self.codegen_user_call(node, func_name)
        elif isinstance(node, PropagateExpr): return self.codegen_propagate(node)
        elif isinstance(node, ComptimeExpr): return self.codegen_comptime(node)
        elif isinstance(node, StructLiteralExpr): return self.codegen_struct_literal(node)
        elif isinstance(node, MatchExpr): return self.codegen_match_expr(node)
        elif isinstance(node, LambdaExpr): return self.codegen_lambda_expr(node)
        elif isinstance(node, CastExpr): return self.codegen_cast_expr(node)
        elif isinstance(node, ArrayExpr): return self.codegen_array_expr(node)
        raise Exception(f"Nó não suportado no Codegen: {type(node).__name__}")

    def codegen_user_call(self, node, func_name):
        # CORREÇÃO: Intercepta o print e outras funções embutidas
        if func_name == "print":
            if len(node.args) >= 1:
                val = self.codegen_expr(node.args[0])
                if isinstance(val.type, ir.PointerType) and val.type != self.voidptr_ty:
                    val = self.builder.bitcast(val, self.voidptr_ty, name="print_cast")
                self.builder.call(self.printf, [self.create_global_string("%s\n"), val], name="print_call")
            return ir.Constant(self.i64_ty, 0)
            
        if func_name in self.functions_table:
            func, func_type = self.functions_table[func_name]
            args = []
            for i, arg_node in enumerate(node.args):
                arg_val = self.codegen_expr(arg_node)
                if isinstance(arg_val.type, ir.ArrayType):
                    ptr_ty = arg_val.type.element.as_pointer()
                    arg_val = self.builder.bitcast(arg_val, ptr_ty, name="array_decay")
                if func_type.args[i] == self.f64_ty and arg_val.type == self.i64_ty:
                    arg_val = self.to_float_if_needed(arg_val)
                args.append(arg_val)
            return self.builder.call(func, args, name=func_name + "_call")
            
        raise Exception(f"Função '{func_name}' não encontrada na tabela do Codegen.")

    def codegen_method_call(self, node, method_name):
        obj_node = node.args[0]
        obj_val = self.codegen_expr(obj_node)
        if isinstance(obj_val.type, ir.PointerType) and isinstance(obj_val.type.pointee, ir.IdentifiedStructType):
            struct_name = obj_val.type.pointee.name
            real_method_name = f"{struct_name}_{method_name}"
            if real_method_name in self.functions_table:
                func, func_type = self.functions_table[real_method_name]
                args = [obj_val]
                for arg_node in node.args[1:]:
                    args.append(self.codegen_expr(arg_node))
                return self.builder.call(func, args, name=real_method_name + "_call")
        if obj_val.type == self.voidptr_ty:
            if method_name == "contains": return ir.Constant(ir.IntType(1), 1)
        raise Exception(f"Método '{method_name}' não encontrado no Codegen.")
        
    def codegen_struct_literal(self, node):
        struct_ty = self.get_llvm_type(node.struct_name)
        ptr = self.builder.alloca(struct_ty, name=node.struct_name.lower() + "_lit")
        for field_name, field_expr in node.fields:
            elem_index = self.struct_fields[node.struct_name].get(field_name, 0)
            elem_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, elem_index)], name=field_name + "_ptr")
            val = self.codegen_expr(field_expr)
            self.builder.store(val, elem_ptr)
        return ptr

    def codegen_array_expr(self, node):
        elem_ty = self.i64_ty
        array_ty = ir.ArrayType(elem_ty, len(node.elements))
        ptr = self.builder.alloca(array_ty, name="array_lit")
        for i, el in enumerate(node.elements):
            el_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)], name=f"arr_el_{i}")
            val = self.codegen_expr(el)
            self.builder.store(val, el_ptr)
        return ptr

    def codegen_cast_expr(self, node):
        val = self.codegen_expr(node.expr)
        target_ty = self.get_llvm_type(node.target_type)
        if val.type == target_ty: return val
        if val.type == self.i64_ty and target_ty == self.f64_ty: return self.builder.sitofp(val, self.f64_ty, name="int_to_float")
        elif val.type == self.f64_ty and target_ty == self.i64_ty: return self.builder.fptosi(val, self.i64_ty, name="float_to_int")
        elif isinstance(val.type, ir.PointerType) and target_ty == self.i64_ty: return self.builder.ptrtoint(val, self.i64_ty, name="ptr_to_int")
        elif val.type == self.i64_ty and isinstance(target_ty, ir.PointerType): return self.builder.inttoptr(val, target_ty, name="int_to_ptr")
        elif isinstance(val.type, ir.PointerType) and isinstance(target_ty, ir.PointerType): return self.builder.bitcast(val, target_ty, name="ptr_bitcast")
        raise Exception(f"Cast de {val.type} para {target_ty} não suportado.")

    def codegen_lambda_expr(self, node):
        func_name = f"__lambda_{id(node)}"
        ret_ty = self.get_llvm_type(node.return_type)
        param_types = [self.get_llvm_param_type(p[1]) for p in node.params]
        func_type = ir.FunctionType(ret_ty, param_types)
        func = ir.Function(self.module, func_type, name=func_name)
        old_builder = self.builder
        old_symtab = self.symbol_table if hasattr(self, 'symbol_table') else {}
        block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        self.symbol_table = {}
        for i, param in enumerate(node.params):
            p_name, p_type = param[0], param[1]
            p_ty = self.get_llvm_param_type(p_type)
            ptr = self.builder.alloca(p_ty, name=p_name)
            self.builder.store(func.args[i], ptr)
            self.symbol_table[p_name] = ptr
        for stmt in node.body:
            self.codegen_stmt(stmt)
        if not self.builder.block.is_terminated:
            if ret_ty == ir.VoidType(): self.builder.ret_void()
            else: self.builder.ret(ir.Constant(ret_ty, 0))
        self.builder = old_builder
        self.symbol_table = old_symtab
        func_ptr = self.builder.bitcast(func, self.voidptr_ty, name="lambda_ptr")
        return func_ptr

    def codegen_match_expr(self, node):
        cond_val = self.codegen_expr(node.condition)
        if cond_val.type == self.i64_ty:
            end_bb = self.builder.append_basic_block(name="match.end")
            default_bb = self.builder.append_basic_block(name="match.default")
            sw = self.builder.switch(cond_val, default_bb)
            incoming = []
            phi_ty = None
            for val_node, res_node in node.cases:
                case_bb = self.builder.append_basic_block(name="match.case")
                val = self.codegen_expr(val_node)
                sw.add_case(val, case_bb)
                self.builder.position_at_end(case_bb)
                res_val = self.codegen_expr(res_node)
                if phi_ty is None: phi_ty = res_val.type
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((res_val, self.builder.block))
            self.builder.position_at_end(default_bb)
            if node.default:
                default_val = self.codegen_expr(node.default)
                if phi_ty is None: phi_ty = default_val.type
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((default_val, self.builder.block))
            else:
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    if phi_ty and isinstance(phi_ty, ir.PointerType):
                        incoming.append((ir.Constant(phi_ty, None), self.builder.block))
                    else:
                        incoming.append((ir.Constant(self.i64_ty, 0), self.builder.block))
            self.builder.position_at_end(end_bb)
            if phi_ty is None: phi_ty = self.i64_ty
            phi = self.builder.phi(phi_ty, name="match_res")
            for val, blk in incoming: phi.add_incoming(val, blk)
            return phi
        raise Exception("Match não suportado para este tipo no Codegen.")