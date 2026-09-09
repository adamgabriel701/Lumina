from llvmlite import ir
from ..ast import NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, TupleExpr, UnaryExpr, PropagateExpr, ComptimeExpr, StructLiteralExpr, MatchExpr, CastExpr

class ExpressionCodegen:
    def codegen_expr(self, node):
        if isinstance(node, NumberExpr): return ir.Constant(self.f64_ty, float(node.value)) if node.is_float else ir.Constant(self.i64_ty, int(node.value))
        elif isinstance(node, BoolExpr): return ir.Constant(ir.IntType(1), 1 if node.value else 0)
        elif isinstance(node, StringExpr): return self.create_global_string(node.value)
        elif isinstance(node, UnaryExpr): return self.codegen_unary(node)
        elif isinstance(node, DerefExpr): return self.codegen_deref(node)
        elif isinstance(node, AddressOfExpr): return self.codegen_address_of(node)
        elif isinstance(node, VariableExpr): return self.codegen_variable(node)
        elif isinstance(node, BinaryExpr): return self.codegen_binary(node)
        elif isinstance(node, IndexExpr): return self.codegen_index(node)
        elif isinstance(node, MemberExpr): return self.codegen_member(node)
        elif isinstance(node, CallExpr): return self.codegen_native_call(node) or self.codegen_user_call(node)
        elif isinstance(node, PropagateExpr): return self.codegen_propagate(node)
        elif isinstance(node, ComptimeExpr): return self.codegen_comptime(node)
        elif isinstance(node, StructLiteralExpr):
            # Aloca a Struct na memória
            struct_ty = self.get_llvm_type(node.struct_name)
            ptr = self.builder.alloca(struct_ty, name=node.struct_name.lower() + "_lit")
            
            # Preenche os campos
            for field_name, field_expr in node.fields:
                # Descobre o índice do campo
                elem_index = self.struct_fields[node.struct_name].get(field_name, 0)
                elem_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, elem_index)], name=field_name + "_ptr")
                
                # Avalia a expressão e salva no campo
                val = self.codegen_expr(field_expr)
                self.builder.store(val, elem_ptr)
                
            return ptr
        # NOVO: Geração de código para Match Expression
        elif isinstance(node, MatchExpr):
            cond_val = self.codegen_expr(node.condition)
            default_bb = self.builder.append_basic_block(name="match_expr.default")
            end_bb = self.builder.append_basic_block(name="match_expr.end")
            sw = self.builder.switch(cond_val, default_bb)
            
            incoming = [] # Lista de (valor, bloco) para o phi node
            
            for val_node, res_node in node.cases:
                case_bb = self.builder.append_basic_block(name="match_expr.case")
                val = self.codegen_expr(val_node)
                sw.add_case(val, case_bb)
                
                self.builder.position_at_end(case_bb)
                res_val = self.codegen_expr(res_node)
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((res_val, self.builder.block))
                
            self.builder.position_at_end(default_bb)
            if node.default:
                default_val = self.codegen_expr(node.default)
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((default_val, self.builder.block))
            else:
                # Se não houver default, retorna 0
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((ir.Constant(self.i64_ty, 0), self.builder.block))
                
            self.builder.position_at_end(end_bb)
            phi = self.builder.phi(self.i64_ty, name="match_expr_res")
            for val, blk in incoming:
                phi.add_incoming(val, blk)
            return phi

        # NOVO: Geração de código para CastExpr
        elif isinstance(node, CastExpr):
            val = self.codegen_expr(node.expr)
            target_ty = self.get_llvm_type(node.target_type)
            
            # Se os tipos já forem iguais, não faz nada
            if val.type == target_ty:
                return val
                
            # Int -> Float
            if val.type == self.i64_ty and target_ty == self.f64_ty:
                return self.builder.sitofp(val, self.f64_ty, name="int_to_float")
                
            # Float -> Int (Trunca a parte decimal)
            elif val.type == self.f64_ty and target_ty == self.i64_ty:
                return self.builder.fptosi(val, self.i64_ty, name="float_to_int")
                
            # Ptr -> Int
            elif isinstance(val.type, ir.PointerType) and target_ty == self.i64_ty:
                return self.builder.ptrtoint(val, self.i64_ty, name="ptr_to_int")
                
            # Int -> Ptr
            elif val.type == self.i64_ty and isinstance(target_ty, ir.PointerType):
                return self.builder.inttoptr(val, target_ty, name="int_to_ptr")
                
            # Bitcast para ponteiros genéricos (void*)
            elif isinstance(val.type, ir.PointerType) and isinstance(target_ty, ir.PointerType):
                return self.builder.bitcast(val, target_ty, name="ptr_bitcast")
                
            raise Exception(f"Cast de {val.type} para {target_ty} não suportado.")
        raise Exception(f"Nó não suportado no Codegen: {type(node)}")

    def codegen_unary(self, node):
        if node.op == 'not':
            val = self.codegen_expr(node.val)
            if val.type != ir.IntType(1): val = self.builder.icmp_signed("!=", val, ir.Constant(val.type, 0), name="not_cond")
            return self.builder.xor(val, ir.Constant(ir.IntType(1), 1), name="not_tmp")
        elif node.op == '-':
            val = self.codegen_expr(node.val)
            return self.builder.fneg(val, name="fneg_tmp") if val.type == self.f64_ty else self.builder.neg(val, name="neg_tmp")
        elif node.op == '+': return self.codegen_expr(node.val)

    def codegen_binary(self, node):
        if node.op == 'in':
            val = self.codegen_expr(node.left); start = self.codegen_expr(node.right.left); end = self.codegen_expr(node.right.right)
            ge = self.builder.icmp_signed(">=", val, start, name="in_ge"); lt = self.builder.icmp_signed("<", val, end, name="in_lt")
            return self.builder.zext(self.builder.and_(ge, lt, name="in_res"), self.i64_ty, name="in_int")
            
        left = self.codegen_expr(node.left); right = self.codegen_expr(node.right)
        
        # Operadores Sobrecarregados
        if isinstance(left.type, ir.PointerType) and isinstance(left.type.pointee, ir.IdentifiedStructType) and left.type == right.type:
            struct_name = left.type.pointee.name
            op_map = {'+': '__add__', '-': '__sub__', '*': '__mul__', '/': '__div__', '==': '__eq__'}
            method_name = op_map.get(node.op)
            if method_name:
                func_name = f"{struct_name}_{method_name}"
                if func_name in self.functions_table:
                    func, func_type = self.functions_table[func_name]
                    return self.builder.call(func, [left, right], name=func_name + "_call")

        if node.op in ('and', 'or'):
            if left.type != ir.IntType(1): left = self.builder.icmp_signed("!=", left, ir.Constant(left.type, 0), name="and_left_cond")
            if right.type != ir.IntType(1): right = self.builder.icmp_signed("!=", right, ir.Constant(right.type, 0), name="and_right_cond")
            return self.builder.and_(left, right, name="and_tmp") if node.op == 'and' else self.builder.or_(left, right, name="or_tmp")
            
        if node.op in ('&', '|', '^', '<<', '>>'):
            if node.op == '&': return self.builder.and_(left, right, name="bw_and_tmp")
            elif node.op == '|': return self.builder.or_(left, right, name="bw_or_tmp")
            elif node.op == '^': return self.builder.xor(left, right, name="bw_xor_tmp")
            elif node.op == '<<': return self.builder.shl(left, right, name="bw_shl_tmp")
            elif node.op == '>>': return self.builder.ashr(left, right, name="bw_shr_tmp")
            
        if node.op in ('==', '!=') and isinstance(left.type, ir.PointerType):
            if right.type == self.i64_ty: right = self.builder.inttoptr(right, left.type, name="int_to_ptr_cmp")
            return self.builder.icmp_signed("==", left, right, name="ptr_eq_tmp") if node.op == '==' else self.builder.icmp_signed("!=", left, right, name="ptr_neq_tmp")
            
        if isinstance(left.type, ir.PointerType) and right.type == self.i64_ty:
            if node.op == '+': return self.builder.gep(left, [right], name="ptr_add_tmp")
            elif node.op == '-': return self.builder.gep(left, [self.builder.neg(right, name="neg_idx")], name="ptr_sub_tmp")
            
        if node.op == '+' and (left.type == self.voidptr_ty or right.type == self.voidptr_ty): return self.codegen_str_concat(left, right)
        if node.op in ('+=', '-=', '*=', '/='): return self.codegen_compound_assign(node.op, left, right)
        
        if left.type == self.f64_ty or right.type == self.f64_ty:
            left = self.to_float_if_needed(left); right = self.to_float_if_needed(right)
            if node.op == '+': return self.builder.fadd(left, right, name="fadd_tmp")
            elif node.op == '-': return self.builder.fsub(left, right, name="fsub_tmp")
            elif node.op == '*': return self.builder.fmul(left, right, name="fmul_tmp")
            elif node.op == '/': return self.builder.fdiv(left, right, name="fdiv_tmp")
            elif node.op in ('==', '!=', '<', '>', '<=', '>='): return self.builder.fcmp_ordered(node.op, left, right, name="fcmp_tmp")
        else:
            if node.op == '+': return self.builder.add(left, right, name="add_tmp")
            elif node.op == '-': return self.builder.sub(left, right, name="sub_tmp")
            elif node.op == '*': return self.builder.mul(left, right, name="mul_tmp")
            elif node.op == '/': return self.builder.sdiv(left, right, name="div_tmp")
            elif node.op == '%': return self.builder.srem(left, right, name="mod_tmp")
            elif node.op in ('==', '!=', '<', '>', '<=', '>='): return self.builder.icmp_signed(node.op, left, right, name="cmp_tmp")

    def codegen_str_concat(self, left, right):
        if right.type == self.i64_ty:
            int_buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 32), name="int_buf")
            int_buf_ptr = self.builder.bitcast(int_buf, self.voidptr_ty, name="int_ptr")
            self.builder.call(self.snprintf, [int_buf_ptr, ir.Constant(self.i64_ty, 32), self.create_global_string("%ld"), right], name="int_to_str")
            right = int_buf_ptr
        if left.type == self.i64_ty and right.type == self.voidptr_ty: left, right = right, left
        if left.type == self.voidptr_ty and right.type == self.voidptr_ty:
            buf = self.builder.call(self.malloc, [ir.Constant(self.i64_ty, 256)], name="concat_buf")
            self.builder.call(self.strcpy, [buf, left], name="copy_left"); self.builder.call(self.strcat, [buf, right], name="cat_right")
            return buf

    def codegen_compound_assign(self, op, left, right):
        base_op = op[0]
        if left.type == self.f64_ty or right.type == self.f64_ty:
            left = self.to_float_if_needed(left); right = self.to_float_if_needed(right)
            if base_op == '+': return self.builder.fadd(left, right, name="fadd_assign")
            elif base_op == '-': return self.builder.fsub(left, right, name="fsub_assign")
            elif base_op == '*': return self.builder.fmul(left, right, name="fmul_assign")
            elif base_op == '/': return self.builder.fdiv(left, right, name="fdiv_assign")
        else:
            if base_op == '+': return self.builder.add(left, right, name="add_assign")
            elif base_op == '-': return self.builder.sub(left, right, name="sub_assign")
            elif base_op == '*': return self.builder.mul(left, right, name="mul_assign")
            elif base_op == '/': return self.builder.sdiv(left, right, name="div_assign")

    def codegen_user_call(self, node):
        if node.name in self.functions_table:
            func, func_type = self.functions_table[node.name]
            args = []
            for i, arg_node in enumerate(node.args):
                arg_val = self.codegen_expr(arg_node)
                if isinstance(arg_val.type, ir.ArrayType):
                    ptr_ty = arg_val.type.element.as_pointer(); arg_val = self.builder.bitcast(arg_val, ptr_ty, name="array_decay")
                if func_type.args[i] == self.f64_ty and arg_val.type == self.i64_ty: arg_val = self.to_float_if_needed(arg_val)
                elif func_type.args[i] == self.i64_ty.as_pointer() and arg_val.type == self.voidptr_ty: arg_val = self.builder.bitcast(arg_val, self.i64_ty.as_pointer(), name="arg_ptr_cast")
                elif func_type.args[i] == self.voidptr_ty and isinstance(arg_val.type, ir.PointerType) and arg_val.type != self.voidptr_ty: arg_val = self.builder.bitcast(arg_val, self.voidptr_ty, name="arg_void_cast")
                args.append(arg_val)
            if hasattr(self, 'function_defs') and node.name in self.function_defs:
                func_ast = self.function_defs[node.name]
                for i in range(len(node.args), len(func_ast.params)):
                    if func_ast.params[i][2] is not None: args.append(self.codegen_expr(func_ast.params[i][2]))
            tail_flag = getattr(self, 'is_tail_return', False)
            return self.builder.call(func, args, name=node.name + "_call", tail=tail_flag)
        raise Exception(f"Função '{node.name}' não encontrada.")

    def codegen_propagate(self, node):
        enum_val = self.codegen_expr(node.val)
        if isinstance(enum_val.type, ir.IdentifiedStructType):
            enum_ptr = self.builder.alloca(enum_val.type, name="prop_tmp"); self.builder.store(enum_val, enum_ptr)
        else: enum_ptr = enum_val
        tag_ptr = self.builder.gep(enum_ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)]); tag_val = self.builder.load(tag_ptr, name="prop_tag")
        is_err = self.builder.icmp_signed("!=", tag_val, ir.Constant(self.i32_ty, 0), name="is_err")
        then_bb = self.builder.append_basic_block(name="prop.ok"); else_bb = self.builder.append_basic_block(name="prop.err")
        self.builder.cbranch(is_err, else_bb, then_bb)
        self.builder.position_at_end(else_bb); self.builder.ret(enum_val)
        self.builder.position_at_end(then_bb)
        payload_ptr = self.builder.gep(enum_ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)])
        return self.builder.load(payload_ptr, name="prop_val")

    def codegen_comptime(self, node):
        def eval_comptime(n):
            if isinstance(n, NumberExpr): return int(n.value)
            elif isinstance(n, BinaryExpr):
                l, r = eval_comptime(n.left), eval_comptime(n.right)
                if n.op == '+': return l + r
                elif n.op == '-': return l - r
                elif n.op == '*': return l * r
                elif n.op == '/': return l // r
            raise Exception("comptime não suporta essa expressão.")
        result = eval_comptime(node.expr)
        print(f"⚙️  Comptime avaliado: {result}")
        return ir.Constant(self.i64_ty, result)