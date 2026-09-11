from llvmlite import ir
from ..ast import (
    NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, 
    ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, UnaryExpr, 
    PropagateExpr, ComptimeExpr, StructLiteralExpr, MatchExpr, CastExpr, LambdaExpr,
    StructLiteralField, ErrorNode
)
from ..ast.visitor import NodeVisitor

class ExpressionCodegen(NodeVisitor):
    
    def visit_NumberExpr(self, node):
        if node.value.startswith('0x') or node.value.startswith('0X'):
            return ir.Constant(self.f64_ty, float(int(node.value, 16))) if node.is_float else ir.Constant(self.i64_ty, int(node.value, 16))
        return ir.Constant(self.f64_ty, float(node.value)) if node.is_float else ir.Constant(self.i64_ty, int(node.value))

    def visit_BoolExpr(self, node):
        return ir.Constant(ir.IntType(1), 1 if node.value else 0)

    def visit_StringExpr(self, node):
        return self.create_global_string(node.value)

    def visit_InterpolatedStringExpr(self, node):
        # Suporte caso o parser use a nova AST de F-strings
        return self.codegen_fstring(node.parts)

    def visit_ArrayExpr(self, node):
        # Se for uma F-string simulada (ArrayExpr com StringExpr e outras exprs)
        if len(node.elements) > 1:
            return self.codegen_fstring(node.elements)
            
        # Array normal
        elem_ty = self.i64_ty
        if len(node.elements) > 0:
            first_val = self.visit(node.elements[0])
            elem_ty = first_val.type
            if elem_ty != self.voidptr_ty:
                elem_ty = self.i64_ty
                
        array_ty = ir.ArrayType(elem_ty, len(node.elements))
        ptr = self.builder.alloca(array_ty, name="array_lit")
        
        for i, el in enumerate(node.elements):
            el_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)], name=f"arr_el_{i}")
            val = self.visit(el)
            if val.type != elem_ty:
                val = self.builder.bitcast(val, elem_ty, name=f"arr_cast_{i}")
            self.builder.store(val, el_ptr)
        return ptr

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

    def visit_VariableExpr(self, node):
        ptr = self.symbol_table.get(node.name)
        if not ptr: return ir.Constant(self.i64_ty, 0)
        return self.builder.load(ptr, name=node.name + "_load")

    def visit_BinaryExpr(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        if left is None or right is None: return ir.Constant(self.i64_ty, 0)
        
        # Suporte a concatenação de strings com operador +
        if node.op == '+' and left.type == self.voidptr_ty and right.type == self.voidptr_ty:
            len1 = self.builder.call(self.strlen, [left], name="sconcat_len1")
            len2 = self.builder.call(self.strlen, [right], name="sconcat_len2")
            sum_len = self.builder.add(len1, len2, name="sconcat_sum")
            total_len = self.builder.add(sum_len, ir.Constant(self.i64_ty, 1), name="sconcat_total")
            buf = self.builder.call(self.malloc, [total_len], name="sconcat_buf")
            self.builder.call(self.strcpy, [buf, left], name="sconcat_cpy")
            self.builder.call(self.strcat, [buf, right], name="sconcat_cat")
            return buf

        # Operações Matemáticas
        if node.op in ('+', '-', '*', '/', '%'):
            if left.type == self.f64_ty or right.type == self.f64_ty:
                left = self.to_float_if_needed(left)
                right = self.to_float_if_needed(right)
                if node.op == '+': return self.builder.fadd(left, right, name="fadd")
                elif node.op == '-': return self.builder.fsub(left, right, name="fsub")
                elif node.op == '*': return self.builder.fmul(left, right, name="fmul")
                elif node.op == '/': return self.builder.fdiv(left, right, name="fdiv")
            else:
                if node.op == '+': return self.builder.add(left, right, name="add")
                elif node.op == '-': return self.builder.sub(left, right, name="sub")
                elif node.op == '*': return self.builder.mul(left, right, name="mul")
                elif node.op == '/': return self.builder.sdiv(left, right, name="div")
                elif node.op == '%': return self.builder.srem(left, right, name="mod")
                
        # Comparações
        if node.op in ('==', '!=', '<', '>', '<=', '>='):
            if left.type == self.f64_ty or right.type == self.f64_ty:
                left = self.to_float_if_needed(left)
                right = self.to_float_if_needed(right)
                return self.builder.fcmp_ordered(node.op, left, right, name="fcmp")
            else:
                return self.builder.icmp_signed(node.op, left, right, name="icmp")
                
        return ir.Constant(self.i64_ty, 0)

    def visit_CallExpr(self, node):
        func_name = None
        if isinstance(node.callee, MemberExpr):
            func_name = node.callee.member
        elif isinstance(node.callee, VariableExpr):
            func_name = node.callee.name
            
        is_method = node.is_method
        if is_method and func_name in self.functions_table:
            is_method = False
            
        if is_method:
            return self.codegen_method_call(node, func_name)
        else:
            return self.codegen_user_call(node, func_name)

    def codegen_user_call(self, node, func_name):
        if func_name == "print":
            if len(node.args) >= 1:
                val = self.visit(node.args[0])
                # CORREÇÃO: Tratamento de tipo seguro para a função print
                if val.type == self.i64_ty:
                    self.builder.call(self.printf, [self.create_global_string("%ld\n"), val], name="print_call")
                elif val.type == self.f64_ty:
                    self.builder.call(self.printf, [self.create_global_string("%f\n"), val], name="print_call")
                else:
                    if isinstance(val.type, ir.PointerType) and val.type != self.voidptr_ty:
                        val = self.builder.bitcast(val, self.voidptr_ty, name="print_cast")
                    self.builder.call(self.printf, [self.create_global_string("%s\n"), val], name="print_call")
            return ir.Constant(self.i64_ty, 0)
            
        if func_name in self.functions_table:
            func, func_type = self.functions_table[func_name]
            args = []
            for i, arg_node in enumerate(node.args):
                arg_val = self.visit(arg_node)
                if isinstance(arg_val.type, ir.ArrayType):
                    arg_val = self.builder.bitcast(arg_val, self.voidptr_ty, name="array_decay")
                if func_type.args[i] == self.f64_ty and arg_val.type == self.i64_ty:
                    arg_val = self.to_float_if_needed(arg_val)
                args.append(arg_val)
            return self.builder.call(func, args, name=func_name + "_call")
        raise Exception(f"Função '{func_name}' não encontrada na tabela do Codegen.")

    def codegen_method_call(self, node, method_name):
        obj_node = node.args[0]
        obj_val = self.visit(obj_node)
        
        if isinstance(obj_val.type, ir.PointerType) and isinstance(obj_val.type.pointee, ir.IdentifiedStructType):
            struct_name = obj_val.type.pointee.name
            real_method_name = f"{struct_name}_{method_name}"
            if real_method_name in self.functions_table:
                func, func_type = self.functions_table[real_method_name]
                args = [obj_val]
                for arg_node in node.args[1:]:
                    args.append(self.visit(arg_node))
                return self.builder.call(func, args, name=real_method_name + "_call")
                
        if obj_val.type == self.voidptr_ty:
            if method_name == "len":
                return self.builder.call(self.strlen, [obj_val], name="str_len")
            elif method_name == "contains":
                target_str = self.visit(node.args[1])
                res_ptr = self.builder.call(self.strstr, [obj_val, target_str], name="str_strstr")
                zero_ptr = ir.Constant(self.voidptr_ty, None)
                return self.builder.icmp_signed("!=", res_ptr, zero_ptr, name="str_contains_res")
            elif method_name == "starts_with":
                target_str = self.visit(node.args[1])
                len_target = self.builder.call(self.strlen, [target_str], name="starts_len")
                cmp_res = self.builder.call(self.strncmp, [obj_val, target_str, len_target], name="starts_cmp")
                zero = ir.Constant(ir.IntType(32), 0)
                return self.builder.icmp_signed("==", cmp_res, zero, name="starts_res")
            elif method_name in ("upper", "lower"):
                len_val = self.builder.call(self.strlen, [obj_val], name="case_len")
                total_len = self.builder.add(len_val, ir.Constant(self.i64_ty, 1), name="case_total")
                buf = self.builder.call(self.malloc, [total_len], name="case_buf")
                
                loop_bb = self.builder.append_basic_block(name="case_loop")
                end_bb = self.builder.append_basic_block(name="case_end")
                
                pred_bb = self.builder.block 
                self.builder.branch(loop_bb)
                self.builder.position_at_end(loop_bb)
                
                i = self.builder.phi(self.i64_ty, name="case_i")
                i.add_incoming(ir.Constant(self.i64_ty, 0), pred_bb) 
                
                char_ptr = self.builder.gep(buf, [i], name="case_char_ptr")
                char_val = self.builder.load(char_ptr, name="case_char")
                
                if method_name == "upper":
                    offset = ir.Constant(ir.IntType(8), ord('A') - ord('a'))
                else:
                    offset = ir.Constant(ir.IntType(8), ord('a') - ord('A'))
                    
                lower_a = ir.Constant(ir.IntType(8), ord('a'))
                lower_z = ir.Constant(ir.IntType(8), ord('z'))
                
                is_lower = self.builder.icmp_signed(">=", char_val, lower_a, name="is_ge_a")
                is_upper = self.builder.icmp_signed("<=", char_val, lower_z, name="is_le_z")
                is_alpha = self.builder.and_(is_lower, is_upper, name="is_alpha")
                
                new_char = self.builder.add(char_val, offset, name="new_char")
                final_char = self.builder.select(is_alpha, new_char, char_val, name="final_char")
                self.builder.store(final_char, char_ptr)
                
                next_i = self.builder.add(i, ir.Constant(self.i64_ty, 1), name="case_next")
                i.add_incoming(next_i, self.builder.block)
                
                cond = self.builder.icmp_signed("<", next_i, len_val, name="case_cond")
                self.builder.cbranch(cond, loop_bb, end_bb)
                self.builder.position_at_end(end_bb)
                
                null_ptr = self.builder.gep(buf, [len_val], name="case_null_ptr")
                self.builder.store(ir.Constant(self.i8_ty, 0), null_ptr)
                return buf
                
        raise Exception(f"Método '{method_name}' não encontrado no Codegen.")

    def visit_MemberExpr(self, node):
        obj_val = self.visit(node.obj)
        if isinstance(obj_val.type, ir.PointerType) and isinstance(obj_val.type.pointee, ir.IdentifiedStructType):
            struct_name = obj_val.type.pointee.name
            field_idx = self.struct_fields[struct_name].get(node.member)
            if field_idx is not None:
                elem_ptr = self.builder.gep(obj_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, field_idx)])
                return self.builder.load(elem_ptr, name=node.member + "_load")
        return ir.Constant(self.i64_ty, 0)

    def visit_IndexExpr(self, node):
        arr_val = self.visit(node.array)
        idx_val = self.visit(node.index)
        if isinstance(arr_val.type, ir.PointerType):
            if isinstance(arr_val.type.pointee, ir.ArrayType):
                elem_ptr = self.builder.gep(arr_val, [ir.Constant(self.i32_ty, 0), idx_val])
                return self.builder.load(elem_ptr, name="arr_idx_load")
            else:
                elem_ptr = self.builder.gep(arr_val, [idx_val])
                return self.builder.load(elem_ptr, name="ptr_idx_load")
        return ir.Constant(self.i64_ty, 0)

    def visit_UnaryExpr(self, node):
        val = self.visit(node.val)
        if node.op == '-':
            return self.builder.neg(val, name="neg") if val.type == self.i64_ty else self.builder.fneg(val, name="fneg")
        elif node.op == 'not':
            zero = ir.Constant(val.type, 0)
            return self.builder.icmp_signed("!=", val, zero, name="not_cond")
        return val

    def visit_AddressOfExpr(self, node):
        return self.visit(node.val) 

    def visit_DerefExpr(self, node):
        ptr = self.visit(node.val)
        return self.builder.load(ptr, name="deref_load")

    def visit_PropagateExpr(self, node):
        return self.visit(node.val)

    def visit_ComptimeExpr(self, node):
        try:
            val = int(node.expr.value)
            return ir.Constant(self.i64_ty, val)
        except:
            return self.visit(node.expr)

    def visit_StructLiteralExpr(self, node):
        struct_ty = self.get_llvm_type(node.struct_name)
        ptr = self.builder.alloca(struct_ty, name=node.struct_name.lower() + "_lit")
        
        # Compatível com tuple e dataclass
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

    def visit_CastExpr(self, node):
        val = self.visit(node.expr)
        target_ty = self.get_llvm_type(node.target_type)
        if val.type == target_ty: return val
        if val.type == self.i64_ty and target_ty == self.f64_ty: return self.builder.sitofp(val, self.f64_ty, name="int_to_float")
        elif val.type == self.f64_ty and target_ty == self.i64_ty: return self.builder.fptosi(val, self.i64_ty, name="float_to_int")
        elif isinstance(val.type, ir.PointerType) and target_ty == self.i64_ty: return self.builder.ptrtoint(val, self.i64_ty, name="ptr_to_int")
        elif val.type == self.i64_ty and isinstance(target_ty, ir.PointerType): return self.builder.inttoptr(val, target_ty, name="int_to_ptr")
        return val

    def visit_LambdaExpr(self, node):
        if not hasattr(self, 'lambda_counter'): self.lambda_counter = 0
        func_name = f"__lambda_{self.lambda_counter}"
        self.lambda_counter += 1
        
        ret_ty = self.get_llvm_type(node.return_type)
        
        # Compatível com tuple e dataclass
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
            
        for stmt in node.body:
            self.codegen_stmt(stmt)
            
        if not self.builder.block.is_terminated:
            if ret_ty == ir.VoidType(): self.builder.ret_void()
            else: self.builder.ret(ir.Constant(ret_ty, 0))
            
        self.builder = old_builder
        self.symbol_table = old_symtab
        return self.builder.bitcast(func, self.voidptr_ty, name="lambda_ptr")

    def visit_MatchExpr(self, node):
        cond_val = self.visit(node.condition)
        
        # 1. Match para Inteiros
        if cond_val.type == self.i64_ty:
            end_bb = self.builder.append_basic_block(name="match.end")
            default_bb = self.builder.append_basic_block(name="match.default")
            sw = self.builder.switch(cond_val, default_bb)
            incoming = []
            phi_ty = None
            
            for case in node.cases:
                # Compatível com tuple (velho) e MatchCase (novo)
                if isinstance(case, tuple):
                    val_node, res_node = case
                else:
                    val_node = case.pattern
                    res_node = case.body
                    
                case_bb = self.builder.append_basic_block(name="match.case")
                val = self.visit(val_node)
                sw.add_case(val, case_bb)
                self.builder.position_at_end(case_bb)
                res_val = self.visit(res_node)
                
                if phi_ty is None: phi_ty = res_val.type
                elif phi_ty != res_val.type: 
                    res_val = self.builder.bitcast(res_val, phi_ty, name="case_cast")
                    
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((res_val, self.builder.block))
                    
            self.builder.position_at_end(default_bb)
            if node.default:
                default_val = self.visit(node.default)
                if phi_ty is None: phi_ty = default_val.type
                elif phi_ty != default_val.type: 
                    default_val = self.builder.bitcast(default_val, phi_ty, name="def_cast")
                    
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((default_val, self.builder.block))
            else:
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((ir.Constant(self.i64_ty, 0), self.builder.block))
                    
            self.builder.position_at_end(end_bb)
            if phi_ty is None: phi_ty = self.i64_ty
            phi = self.builder.phi(phi_ty, name="match_res")
            for val, blk in incoming: phi.add_incoming(val, blk)
            return phi
            
        # 2. Match para Strings
        elif cond_val.type == self.voidptr_ty:
            strcmp_fn = next((f for f in self.module.functions if f.name == "strcmp"), None)
            if not strcmp_fn:
                strcmp_ty = ir.FunctionType(ir.IntType(32), [self.voidptr_ty, self.voidptr_ty])
                strcmp_fn = ir.Function(self.module, strcmp_ty, name="strcmp")
                
            end_bb = self.builder.append_basic_block(name="match_str.end")
            incoming = []
            phi_ty = None
            
            for case in node.cases:
                if isinstance(case, tuple):
                    val_node, res_node = case
                else:
                    val_node = case.pattern
                    res_node = case.body
                    
                val_str = self.visit(val_node)
                cmp_res = self.builder.call(strcmp_fn, [cond_val, val_str], name="strcmp_call")
                is_eq = self.builder.icmp_signed("==", cmp_res, ir.Constant(ir.IntType(32), 0), name="str_eq")
                
                then_bb = self.builder.append_basic_block(name="match_str.case")
                next_bb = self.builder.append_basic_block(name="match_str.next")
                self.builder.cbranch(is_eq, then_bb, next_bb)
                
                self.builder.position_at_end(then_bb)
                res_val = self.visit(res_node)
                if phi_ty is None: phi_ty = res_val.type
                elif phi_ty != res_val.type: 
                    res_val = self.builder.bitcast(res_val, phi_ty, name="str_case_cast")
                    
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((res_val, self.builder.block))
                    
                self.builder.position_at_end(next_bb)
                
            if node.default:
                default_val = self.visit(node.default)
                if phi_ty is None: phi_ty = default_val.type
                elif phi_ty != default_val.type: 
                    default_val = self.builder.bitcast(default_val, phi_ty, name="str_def_cast")
                    
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((default_val, self.builder.block))
            else:
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((ir.Constant(self.i64_ty, 0), self.builder.block))
                    
            self.builder.position_at_end(end_bb)
            if phi_ty is None: phi_ty = self.i64_ty
            phi = self.builder.phi(phi_ty, name="match_str_res")
            for val, blk in incoming: phi.add_incoming(val, blk)
            return phi

        # 3. Match para Structs (Destructuring)
        elif isinstance(cond_val.type, ir.PointerType) and isinstance(cond_val.type.pointee, ir.IdentifiedStructType):
            struct_name = cond_val.type.pointee.name
            end_bb = self.builder.append_basic_block(name="match_struct.end")
            incoming = []
            phi_ty = None
            
            for case in node.cases:
                if isinstance(case, tuple):
                    val_node, res_node = case
                else:
                    val_node = case.pattern
                    res_node = case.body
                    
                if isinstance(val_node, StructLiteralExpr) and val_node.struct_name == struct_name:
                    then_bb = self.builder.append_basic_block(name="match_struct.case")
                    next_bb = self.builder.append_basic_block(name="match_struct.next")
                    
                    self.builder.branch(then_bb)
                    self.builder.position_at_end(then_bb)
                    
                    for field in val_node.fields:
                        if isinstance(field, tuple):
                            fname, fexpr = field
                        else:
                            fname = field.name
                            fexpr = field.value
                            
                        if isinstance(fexpr, VariableExpr):
                            elem_index = self.struct_fields[struct_name].get(fname)
                            if elem_index is not None:
                                elem_ptr = self.builder.gep(cond_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, elem_index)])
                                field_val = self.builder.load(elem_ptr, name="bind_val")
                                var_ptr = self.builder.alloca(field_val.type, name=fexpr.name)
                                self.builder.store(field_val, var_ptr)
                                self.symbol_table[fexpr.name] = var_ptr
                                
                    res_val = self.visit(res_node)
                    if phi_ty is None: phi_ty = res_val.type
                    elif phi_ty != res_val.type: 
                        res_val = self.builder.bitcast(res_val, phi_ty, name="struct_case_cast")
                        
                    if not self.builder.block.is_terminated:
                        self.builder.branch(end_bb)
                        incoming.append((res_val, self.builder.block))
                        
                    self.builder.position_at_end(next_bb)
                    
            if node.default:
                default_val = self.visit(node.default)
                if phi_ty is None: phi_ty = default_val.type
                elif phi_ty != default_val.type: 
                    default_val = self.builder.bitcast(default_val, phi_ty, name="struct_def_cast")
                    
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((default_val, self.builder.block))
            else:
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((ir.Constant(self.i64_ty, 0), self.builder.block))
                    
            self.builder.position_at_end(end_bb)
            if phi_ty is None: phi_ty = self.i64_ty
            phi = self.builder.phi(phi_ty, name="match_struct_res")
            for val, blk in incoming: phi.add_incoming(val, blk)
            return phi

        return ir.Constant(self.i64_ty, 0)

    def generic_visit(self, node):
        return ir.Constant(self.i64_ty, 0)