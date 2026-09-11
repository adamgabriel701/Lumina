from llvmlite import ir
from functools import singledispatch
from lumina.errors import LuminaError
from lumina.semantic.expressions import get_suggestion
from ..ast import (
    NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, 
    ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, TupleExpr, 
    UnaryExpr, PropagateExpr, ComptimeExpr, StructLiteralExpr, MatchExpr, 
    CastExpr, LambdaExpr, ErrorNode
)

class ExpressionCodegen:
    
    def setup_codegen_state(self):
        """Inicializa contadores e tabelas se não existirem"""
        if not hasattr(self, 'string_counter'): self.string_counter = 0
        if not hasattr(self, 'lambda_counter'): self.lambda_counter = 0

    @singledispatch
    def codegen_expr(self, node):
        raise Exception(f"Nó não suportado no Codegen: {type(node).__name__}")

    @codegen_expr.register
    def _(self, node: ErrorNode):
        return ir.Constant(self.i64_ty, 0)

    @codegen_expr.register
    def _(self, node: NumberExpr):
        self.setup_codegen_state()
        # Suporta hexadecimais (0x...) e decimais normais
        if node.value.startswith('0x') or node.value.startswith('0X'):
            return ir.Constant(self.f64_ty, float(int(node.value, 16))) if node.is_float else ir.Constant(self.i64_ty, int(node.value, 16))
        return ir.Constant(self.f64_ty, float(node.value)) if node.is_float else ir.Constant(self.i64_ty, int(node.value))

    @codegen_expr.register
    def _(self, node: BoolExpr):
        return ir.Constant(ir.IntType(1), 1 if node.value else 0)

    @codegen_expr.register
    def _(self, node: StringExpr):
        return self.create_global_string(node.value)

    @codegen_expr.register
    def _(self, node: UnaryExpr):
        return self.codegen_unary(node)

    @codegen_expr.register
    def _(self, node: DerefExpr):
        return self.codegen_deref(node)

    @codegen_expr.register
    def _(self, node: AddressOfExpr):
        return self.codegen_address_of(node)

    @codegen_expr.register
    def _(self, node: VariableExpr):
        return self.codegen_variable(node)

    @codegen_expr.register
    def _(self, node: BinaryExpr):
        return self.codegen_binary(node)

    @codegen_expr.register
    def _(self, node: IndexExpr):
        return self.codegen_index(node)

    @codegen_expr.register
    def _(self, node: MemberExpr):
        return self.codegen_member(node)

    @codegen_expr.register
    def _(self, node: CallExpr):
        # UFCS: Se for método e 'name' for função global, converte direto
        if node.is_method and node.name in self.functions_table:
            node.is_method = False
        return self.codegen_native_call(node) or self.codegen_user_call(node)

    @codegen_expr.register
    def _(self, node: PropagateExpr):
        return self.codegen_propagate(node)

    @codegen_expr.register
    def _(self, node: ComptimeExpr):
        return self.codegen_comptime(node)

    @codegen_expr.register
    def _(self, node: StructLiteralExpr):
        struct_ty = self.get_llvm_type(node.struct_name)
        ptr = self.builder.alloca(struct_ty, name=node.struct_name.lower() + "_lit")
        
        for field_name, field_expr in node.fields:
            elem_index = self.struct_fields[node.struct_name].get(field_name, 0)
            elem_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, elem_index)], name=field_name + "_ptr")
            val = self.codegen_expr(field_expr)
            self.builder.store(val, elem_ptr)
            
        return ptr

    @codegen_expr.register
    def _(self, node: MatchExpr):
        cond_val = self.codegen_expr(node.condition)
        end_bb = self.builder.append_basic_block(name="match.end")
        incoming = []
        phi_ty = None

        # 1. Match para Strings (if/else chain com strcmp)
        if cond_val.type == self.voidptr_ty:
            strcmp_fn = next((f for f in self.module.functions if f.name == "strcmp"), None)
            if not strcmp_fn:
                strcmp_ty = ir.FunctionType(ir.IntType(32), [self.voidptr_ty, self.voidptr_ty])
                strcmp_fn = ir.Function(self.module, strcmp_ty, name="strcmp")
            
            for val_node, res_node in node.cases:
                if self.builder.block.is_terminated: break
                val_str = self.codegen_expr(val_node)
                cmp_res = self.builder.call(strcmp_fn, [cond_val, val_str], name="strcmp_call")
                is_eq = self.builder.icmp_signed("==", cmp_res, ir.Constant(ir.IntType(32), 0), name="str_eq")
                
                then_bb = self.builder.append_basic_block(name="match.case")
                next_bb = self.builder.append_basic_block(name="match.next")
                self.builder.cbranch(is_eq, then_bb, next_bb)
                
                self.builder.position_at_end(then_bb)
                res_val = self.codegen_expr(res_node)
                if phi_ty is None: phi_ty = res_val.type
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((res_val, self.builder.block))
                    
                self.builder.position_at_end(next_bb)

        # 2. Match para Inteiros (switch nativo)
        elif cond_val.type == self.i64_ty:
            default_bb = self.builder.append_basic_block(name="match.default")
            sw = self.builder.switch(cond_val, default_bb)
            
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

        # 3. Match para Structs (Destructuring)
        elif isinstance(cond_val.type, ir.PointerType) and isinstance(cond_val.type.pointee, ir.IdentifiedStructType):
            struct_name = cond_val.type.pointee.name
            struct_def = self.struct_defs.get(struct_name)
            if not struct_def: raise Exception(f"Struct '{struct_name}' não encontrada para match.")
            
            for val_node, res_node in node.cases:
                if self.builder.block.is_terminated: break
                if not isinstance(val_node, StructLiteralExpr) or val_node.struct_name != struct_name:
                    raise Exception("Match de struct requer Struct Literals do mesmo tipo.")
                    
                cond_bb = self.builder.append_basic_block(name="match.check")
                next_bb = self.builder.append_basic_block(name="match.next")
                self.builder.branch(cond_bb)
                self.builder.position_at_end(cond_bb)
                
                all_match = ir.Constant(ir.IntType(1), 1)
                for field_name, field_val_node in val_node.fields:
                    elem_index = self.struct_fields[struct_name].get(field_name)
                    elem_ptr = self.builder.gep(cond_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, elem_index)], name="match_field_ptr")
                    field_val = self.builder.load(elem_ptr, name="match_field_val")
                    
                    if isinstance(field_val_node, VariableExpr):
                        var_ptr = self.builder.alloca(self.i64_ty, name=field_val_node.name)
                        self.builder.store(field_val, var_ptr)
                        self.symbol_table[field_val_node.name] = var_ptr
                        self.var_types[field_val_node.name] = self.i64_ty
                    else:
                        expected_val = self.codegen_expr(field_val_node)
                        if expected_val.type == self.f64_ty: field_val = self.builder.fptosi(field_val, self.i64_ty, name="f_to_i")
                        is_eq = self.builder.icmp_signed("==", field_val, expected_val, name="field_eq")
                        all_match = self.builder.and_(all_match, is_eq, name="and_match")
                        
                then_bb = self.builder.append_basic_block(name="match.then")
                self.builder.cbranch(all_match, then_bb, next_bb)
                
                self.builder.position_at_end(then_bb)
                res_val = self.codegen_expr(res_node)
                if phi_ty is None: phi_ty = res_val.type
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((res_val, self.builder.block))
                    
                self.builder.position_at_end(next_bb)

        # 4. NOVO: Match para Booleanos
        elif cond_val.type == ir.IntType(1):
            for val_node, res_node in node.cases:
                if self.builder.block.is_terminated: break
                val_bool = self.codegen_expr(val_node)
                is_eq = self.builder.icmp_signed("==", cond_val, val_bool, name="bool_eq")
                
                then_bb = self.builder.append_basic_block(name="match.case")
                next_bb = self.builder.append_basic_block(name="match.next")
                self.builder.cbranch(is_eq, then_bb, next_bb)
                
                self.builder.position_at_end(then_bb)
                res_val = self.codegen_expr(res_node)
                if phi_ty is None: phi_ty = res_val.type
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((res_val, self.builder.block))
                    
                self.builder.position_at_end(next_bb)

        else:
            raise Exception("Match não suportado para este tipo.")

        # Bloco Default
        if node.default and not self.builder.block.is_terminated:
            default_val = self.codegen_expr(node.default)
            if phi_ty is None: phi_ty = default_val.type
            self.builder.branch(end_bb)
            incoming.append((default_val, self.builder.block))
        elif not self.builder.block.is_terminated:
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

    @codegen_expr.register
    def _(self, node: LambdaExpr):
        self.setup_codegen_state()
        func_name = f"__lambda_{self.lambda_counter}"
        self.lambda_counter += 1
        
        # Salva o contexto atual de forma limpa
        ctx = self.save_context()
        
        ret_ty = self.get_llvm_type(node.return_type)
        self.current_ret_ty = ret_ty
        param_types = [self.get_llvm_param_type(p[1]) for p in node.params]
        func_type = ir.FunctionType(ret_ty, param_types)
        func = ir.Function(self.module, func_type, name=func_name)
        block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        self.symbol_table = {}
        self.var_types = {}
        
        for i, param in enumerate(node.params):
            p_name, p_type = param[0], param[1]
            p_ty = self.get_llvm_param_type(p_type)
            ptr = self.builder.alloca(p_ty, name=p_name)
            self.builder.store(func.args[i], ptr)
            self.symbol_table[p_name] = ptr
            self.var_types[p_name] = p_ty
            
        for stmt in node.body:
            self.codegen_stmt(stmt)
            
        if not self.builder.block.is_terminated:
            if ret_ty == ir.VoidType(): self.builder.ret_void()
            else: self.builder.ret(ir.Constant(ret_ty, 0))
            
        # Restaura contexto
        self.restore_context(ctx)
        
        func_ptr = self.builder.bitcast(func, self.voidptr_ty, name="lambda_ptr")
        return func_ptr

    @codegen_expr.register
    def _(self, node: CastExpr):
        val = self.codegen_expr(node.expr)
        target_ty = self.get_llvm_type(node.target_type)
        
        if val.type == target_ty: return val
            
        if val.type == self.i64_ty and target_ty == self.f64_ty:
            return self.builder.sitofp(val, self.f64_ty, name="int_to_float")
        elif val.type == self.f64_ty and target_ty == self.i64_ty:
            return self.builder.fptosi(val, self.i64_ty, name="float_to_int")
        elif isinstance(val.type, ir.PointerType) and target_ty == self.i64_ty:
            return self.builder.ptrtoint(val, self.i64_ty, name="ptr_to_int")
        elif val.type == self.i64_ty and isinstance(target_ty, ir.PointerType):
            return self.builder.inttoptr(val, target_ty, name="int_to_ptr")
        elif isinstance(val.type, ir.PointerType) and isinstance(target_ty, ir.PointerType):
            return self.builder.bitcast(val, target_ty, name="ptr_bitcast")
            
        raise Exception(f"Cast de {val.type} para {target_ty} não suportado.")

    # --- Métodos Auxiliares ---

    def save_context(self):
        return {
            'builder': self.builder,
            'symbol_table': self.symbol_table,
            'var_types': self.var_types,
            'current_ret_ty': getattr(self, 'current_ret_ty', self.i64_ty)
        }

    def restore_context(self, ctx):
        self.builder = ctx['builder']
        self.symbol_table = ctx['symbol_table']
        self.var_types = ctx['var_types']
        self.current_ret_ty = ctx['current_ret_ty']

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
        # NOVO: Operador 'in' para Arrays
        if node.op == 'in' and isinstance(node.right, VariableExpr):
            var_ptr = self.symbol_table.get(node.right.name)
            if var_ptr and isinstance(var_ptr.type.pointee, ir.ArrayType):
                val = self.codegen_expr(node.left)
                arr_len = var_ptr.type.pointee.count
                found = ir.Constant(ir.IntType(1), 0)
                
                end_bb = self.builder.append_basic_block(name="in_loop.end")
                loop_bb = self.builder.append_basic_block(name="in_loop.body")
                self.builder.branch(loop_bb)
                
                self.builder.position_at_end(loop_bb)
                phi = self.builder.phi(ir.IntType(1), name="in_phi")
                phi.add_incoming(found, self.builder.block)
                
                i = self.builder.phi(self.i64_ty, name="in_i")
                i.add_incoming(ir.Constant(self.i64_ty, 0), self.builder.block)
                
                elem_ptr = self.builder.gep(var_ptr, [ir.Constant(self.i32_ty, 0), i], name="in_elem_ptr")
                elem_val = self.builder.load(elem_ptr, name="in_elem_val")
                
                is_eq = self.builder.icmp_signed("==", val, elem_val, name="in_eq")
                next_i = self.builder.add(i, ir.Constant(self.i64_ty, 1), name="in_next_i")
                cond = self.builder.icmp_signed("<", next_i, ir.Constant(self.i64_ty, arr_len), name="in_cond")
                
                then_bb = self.builder.append_basic_block(name="in_loop.then")
                self.builder.cbranch(is_eq, then_bb, end_bb)
                
                self.builder.position_at_end(then_bb)
                self.builder.branch(end_bb)
                incoming_found = ir.Constant(ir.IntType(1), 1)
                
                self.builder.position_at_end(end_bb)
                res_phi = self.builder.phi(ir.IntType(1), name="in_res")
                res_phi.add_incoming(found, self.builder.block)
                res_phi.add_incoming(incoming_found, then_bb)
                return self.builder.zext(res_phi, self.i64_ty, name="in_res_int")

        # Operador 'in' para Ranges
        if node.op == 'in':
            val = self.codegen_expr(node.left)
            start = self.codegen_expr(node.right.left)
            end = self.codegen_expr(node.right.right)
            ge = self.builder.icmp_signed(">=", val, start, name="in_ge")
            lt = self.builder.icmp_signed("<", val, end, name="in_lt")
            return self.builder.zext(self.builder.and_(ge, lt, name="in_res"), self.i64_ty, name="in_int")
            
        if node.op == '..':
            raise Exception("Operador '..' (Range) só pode ser usado em loops 'for' ou slices de array 'arr[1..5]'.")
            
        left = self.codegen_expr(node.left)
        right = self.codegen_expr(node.right)
        
        if left is None or right is None:
            raise Exception(f"Erro no Codegen: Operando None em '{node.op}'.")
            
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
            left = self.to_float_if_needed(left)
            right = self.to_float_if_needed(right)
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
        if left.type == self.i64_ty and right.type == self.voidptr_ty:
            left, right = right, left
            
        if left.type == self.voidptr_ty and right.type == self.voidptr_ty:
            len1 = self.builder.call(self.strlen, [left], name="len1")
            len2 = self.builder.call(self.strlen, [right], name="len2")
            sum_len = self.builder.add(len1, len2, name="sum_len")
            total_len = self.builder.add(sum_len, ir.Constant(self.i64_ty, 1), name="total_len")
            
            buf = self.builder.call(self.malloc, [total_len], name="str_concat_buf")
            self.builder.call(self.strcpy, [buf, left], name="copy_left")
            self.builder.call(self.strcat, [buf, right], name="cat_right")
            return buf

    def codegen_compound_assign(self, op, left, right):
        base_op = op[0]
        if left.type == self.f64_ty or right.type == self.f64_ty:
            left = self.to_float_if_needed(left)
            right = self.to_float_if_needed(right)
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
        if node.is_method and node.name in self.functions_table:
            node.is_method = False
            return self.codegen_user_call(node)

        if node.name in self.functions_table:
            func, func_type = self.functions_table[node.name]
            args = []
            for i, arg_node in enumerate(node.args):
                if isinstance(arg_node, VariableExpr) and isinstance(func_type.args[i], ir.PointerType):
                    var_ptr = self.symbol_table.get(arg_node.name)
                    if var_ptr and isinstance(var_ptr.type.pointee, ir.ArrayType):
                        arg_val = self.builder.bitcast(var_ptr, func_type.args[i], name="array_arg_decay")
                        args.append(arg_val)
                        continue
                    if var_ptr and var_ptr.type.pointee == self.i64_ty and arg_node.name in self.heap_int_arrays:
                        arg_val = self.builder.bitcast(var_ptr, func_type.args[i], name="heap_array_arg_decay")
                        args.append(arg_val)
                        continue

                arg_val = self.codegen_expr(arg_node)
                if isinstance(arg_val.type, ir.ArrayType):
                    ptr_ty = arg_val.type.element.as_pointer()
                    arg_val = self.builder.bitcast(arg_val, ptr_ty, name="array_decay")
                if func_type.args[i] == self.f64_ty and arg_val.type == self.i64_ty: arg_val = self.to_float_if_needed(arg_val)
                elif func_type.args[i] == self.i64_ty.as_pointer() and arg_val.type == self.voidptr_ty: arg_val = self.builder.bitcast(arg_val, self.i64_ty.as_pointer(), name="arg_ptr_cast")
                elif func_type.args[i] == self.voidptr_ty and isinstance(arg_val.type, ir.PointerType) and arg_val.type != self.voidptr_ty: arg_val = self.builder.bitcast(arg_val, self.voidptr_ty, name="arg_void_cast")
                elif func_type.args[i] == self.i64_ty and isinstance(arg_val.type, ir.PointerType):
                    arg_val = self.builder.ptrtoint(arg_val, self.i64_ty, name="arg_ptr_to_int")
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
            enum_ptr = self.builder.alloca(enum_val.type, name="prop_tmp")
            self.builder.store(enum_val, enum_ptr)
        else: enum_ptr = enum_val
        
        tag_ptr = self.builder.gep(enum_ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)])
        tag_val = self.builder.load(tag_ptr, name="prop_tag")
        is_err = self.builder.icmp_signed("!=", tag_val, ir.Constant(self.i32_ty, 0), name="is_err")
        
        then_bb = self.builder.append_basic_block(name="prop.ok")
        else_bb = self.builder.append_basic_block(name="prop.err")
        self.builder.cbranch(is_err, else_bb, then_bb)
        
        self.builder.position_at_end(else_bb)
        self.builder.ret(enum_val)
        
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