from llvmlite import ir
from ..ast import NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, TupleExpr, UnaryExpr, PropagateExpr

class ExpressionCodegen:
    def resolve_member_ptr(self, node: MemberExpr):
        if isinstance(node.obj, VariableExpr):
            ptr = self.symbol_table.get(node.obj.name)
            if not ptr: raise Exception(f"Variável '{node.obj.name}' não declarada.")
            struct_ty = self.var_types.get(node.obj.name)
            if isinstance(struct_ty, ir.PointerType) and isinstance(struct_ty.pointee, ir.IdentifiedStructType):
                struct_ty = struct_ty.pointee
        else:
            ptr = self.codegen_expr(node.obj)
            struct_ty = ptr.type.pointee
            
        elem_index = 0
        for s_name, s_fields in self.struct_fields.items():
            if self.struct_types[s_name] == struct_ty:
                elem_index = s_fields.get(node.member, 0)
                break
        return self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, elem_index)], name="member_ptr", inbounds=True)

    def codegen_expr(self, node):
        if isinstance(node, NumberExpr):
            if node.is_float: return ir.Constant(self.f64_ty, float(node.value))
            if node.value.startswith('0x') or node.value.startswith('0X'):
                return ir.Constant(self.i64_ty, int(node.value, 16))
            return ir.Constant(self.i64_ty, int(node.value))
            
        elif isinstance(node, BoolExpr):
            return ir.Constant(ir.IntType(1), 1 if node.value else 0)
            
        elif isinstance(node, StringExpr): 
            return self.create_global_string(node.value)
            
        elif isinstance(node, UnaryExpr):
            if node.op == 'not':
                val = self.codegen_expr(node.val)
                if val.type != ir.IntType(1):
                    val = self.builder.icmp_signed("!=", val, ir.Constant(val.type, 0), name="not_cond")
                return self.builder.xor(val, ir.Constant(ir.IntType(1), 1), name="not_tmp")
            elif node.op == '-':
                val = self.codegen_expr(node.val)
                if val.type == self.f64_ty: return self.builder.fneg(val, name="fneg_tmp")
                else: return self.builder.neg(val, name="neg_tmp")
            elif node.op == '+':
                return self.codegen_expr(node.val)
            
        elif isinstance(node, AddressOfExpr):
            if isinstance(node.val, VariableExpr):
                if node.val.name in self.functions_table:
                    func, _ = self.functions_table[node.val.name]
                    return self.builder.ptrtoint(func, self.i64_ty, name="fn_ptr_int")
                    
                ptr = self.symbol_table.get(node.val.name)
                if not ptr: raise Exception(f"Variável '{node.val.name}' não declarada.")
                return self.builder.bitcast(ptr, self.voidptr_ty, name="addr_of")
            raise Exception("Endereço de memória só pode ser pego de variáveis ou funções.")
            
        elif isinstance(node, DerefExpr):
            ptr = self.codegen_expr(node.val)
            if ptr.type == self.voidptr_ty:
                ptr = self.builder.bitcast(ptr, self.i64_ty.as_pointer(), name="deref_ptr_cast")
            return self.builder.load(ptr, name="deref_val")
            
        elif isinstance(node, VariableExpr):
            if node.name in self.variant_defs:
                enum_name, index, payload_type = self.variant_defs[node.name]
                enum_ty = self.struct_types[enum_name]
                ptr = self.builder.alloca(enum_ty, name="enum_tmp")
                tag_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)])
                payload_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)])
                self.builder.store(ir.Constant(self.i32_ty, index), tag_ptr)
                self.builder.store(ir.Constant(self.i64_ty, 0), payload_ptr)
                return ptr
                
            ptr = self.symbol_table.get(node.name)
            if not ptr: raise Exception(f"Variável '{node.name}' não declarada.")
            if isinstance(ptr, ir.GlobalVariable):
                return self.builder.load(ptr, name=node.name + "_gval")
            if isinstance(ptr.type.pointee, ir.IdentifiedStructType): return ptr
            return self.builder.load(ptr, name=node.name + "_val")
            
        elif isinstance(node, BinaryExpr):
            left = self.codegen_expr(node.left)
            right = self.codegen_expr(node.right)
            
            if node.op in ('and', 'or'):
                if left.type != ir.IntType(1):
                    left = self.builder.icmp_signed("!=", left, ir.Constant(left.type, 0), name="and_left_cond")
                if right.type != ir.IntType(1):
                    right = self.builder.icmp_signed("!=", right, ir.Constant(right.type, 0), name="and_right_cond")
                if node.op == 'and': return self.builder.and_(left, right, name="and_tmp")
                elif node.op == 'or': return self.builder.or_(left, right, name="or_tmp")
                
            if node.op in ('&', '|', '^', '<<', '>>'):
                if node.op == '&': return self.builder.and_(left, right, name="bw_and_tmp")
                elif node.op == '|': return self.builder.or_(left, right, name="bw_or_tmp")
                elif node.op == '^': return self.builder.xor(left, right, name="bw_xor_tmp")
                elif node.op == '<<': return self.builder.shl(left, right, name="bw_shl_tmp")
                elif node.op == '>>': return self.builder.ashr(left, right, name="bw_shr_tmp")

            if node.op in ('==', '!=') and left.type == self.voidptr_ty and right.type == self.voidptr_ty:
                cmp_res = self.builder.call(self.strcmp, [left, right], name="strcmp_call")
                is_eq = self.builder.icmp_signed("==", cmp_res, ir.Constant(self.i32_ty, 0), name="is_eq")
                if node.op == '==': return is_eq
                elif node.op == '!=': return self.builder.xor(is_eq, ir.Constant(ir.IntType(1), 1), name="is_neq")

            # NOVO: Comparação de Ponteiros (com 0 ou entre si)
            if node.op in ('==', '!=') and isinstance(left.type, ir.PointerType):
                if right.type == self.i64_ty:
                    right = self.builder.inttoptr(right, left.type, name="int_to_ptr_cmp")
                if node.op == '==': return self.builder.icmp_signed("==", left, right, name="ptr_eq_tmp")
                elif node.op == '!=': return self.builder.icmp_signed("!=", left, right, name="ptr_neq_tmp")

            if isinstance(left.type, ir.PointerType) and right.type == self.i64_ty:
                if node.op == '+':
                    return self.builder.gep(left, [right], name="ptr_add_tmp")
                elif node.op == '-':
                    neg_right = self.builder.neg(right, name="neg_idx")
                    return self.builder.gep(left, [neg_right], name="ptr_sub_tmp")
                    
            if node.op == '+' and (isinstance(node.left, StringExpr) or isinstance(node.right, StringExpr) or left.type == self.voidptr_ty or right.type == self.voidptr_ty):
                if right.type == self.i64_ty:
                    int_buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 32), name="int_buf")
                    int_buf_ptr = self.builder.bitcast(int_buf, self.voidptr_ty, name="int_ptr")
                    fmt_int = self.create_global_string("%ld")
                    self.builder.call(self.snprintf, [int_buf_ptr, ir.Constant(self.i64_ty, 32), fmt_int, right], name="int_to_str")
                    right = int_buf_ptr
                if left.type == self.i64_ty and right.type == self.voidptr_ty:
                    left, right = right, left
                if left.type == self.voidptr_ty and right.type == self.voidptr_ty:
                    buf = self.builder.call(self.malloc, [ir.Constant(self.i64_ty, 256)], name="concat_buf")
                    self.builder.call(self.strcpy, [buf, left], name="copy_left")
                    self.builder.call(self.strcat, [buf, right], name="cat_right")
                    return buf

            if node.op in ('+=', '-=', '*=', '/='):
                op = node.op[0]
                if left.type == self.f64_ty or right.type == self.f64_ty:
                    left = self.to_float_if_needed(left)
                    right = self.to_float_if_needed(right)
                    if op == '+': return self.builder.fadd(left, right, name="fadd_assign")
                    elif op == '-': return self.builder.fsub(left, right, name="fsub_assign")
                    elif op == '*': return self.builder.fmul(left, right, name="fmul_assign")
                    elif op == '/': return self.builder.fdiv(left, right, name="fdiv_assign")
                else:
                    if op == '+': return self.builder.add(left, right, name="add_assign")
                    elif op == '-': return self.builder.sub(left, right, name="sub_assign")
                    elif op == '*': return self.builder.mul(left, right, name="mul_assign")
                    elif op == '/': return self.builder.sdiv(left, right, name="div_assign")
                    
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
                
        elif isinstance(node, IndexExpr):
            if isinstance(node.array, VariableExpr):
                if node.array.name in self.array_sizes:
                    arr_ptr = self.symbol_table.get(node.array.name)
                    idx_val = self.codegen_expr(node.index)
                    if idx_val.type != self.i64_ty: idx_val = self.builder.fptosi(idx_val, self.i64_ty, name="idx_int")
                    elem_ptr = self.builder.gep(arr_ptr, [ir.Constant(self.i32_ty, 0), idx_val], name="elem_ptr")
                    return self.builder.load(elem_ptr, name="arr_elem_val")
                else:
                    ptr = self.codegen_expr(node.array)
                    idx_val = self.codegen_expr(node.index)
                    if idx_val.type != self.i64_ty: idx_val = self.builder.fptosi(idx_val, self.i64_ty, name="idx_int")
                    
                    if isinstance(ptr.type, ir.PointerType) and ptr.type.pointee == self.i64_ty:
                        elem_ptr = self.builder.gep(ptr, [idx_val], name="heap_elem_ptr")
                        return self.builder.load(elem_ptr, name="heap_elem_val")
                        
                    elif ptr.type == self.voidptr_ty:
                        char_ptr = self.builder.gep(ptr, [idx_val], name="char_ptr")
                        char_val = self.builder.load(char_ptr, name="char_val")
                        return self.builder.zext(char_val, self.i64_ty, name="char_as_int")
                        
                    else:
                        elem_ptr = self.builder.gep(ptr, [idx_val], name="elem_ptr")
                        return self.builder.load(elem_ptr, name="elem_val")
            else:
                ptr = self.codegen_expr(node.array)
                idx_val = self.codegen_expr(node.index)
                if idx_val.type != self.i64_ty: idx_val = self.builder.fptosi(idx_val, self.i64_ty, name="idx_int")
                if isinstance(ptr.type, ir.PointerType) and isinstance(ptr.type.pointee, ir.ArrayType):
                    elem_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), idx_val], name="nested_elem_ptr")
                else:
                    elem_ptr = self.builder.gep(ptr, [idx_val], name="nested_heap_ptr")
                return self.builder.load(elem_ptr, name="nested_elem_val")
                
        elif isinstance(node, MemberExpr):
            # NOVO: Lógica de Navegação Segura (?.)
            if node.is_safe:
                # 1. Pega o ponteiro da Struct
                obj_ptr = self.codegen_expr(node.obj)
                
                # NOVO: Converte o ponteiro para i64 para comparar com 0 (NULL) de forma segura
                if isinstance(obj_ptr.type, ir.PointerType):
                    obj_int = self.builder.ptrtoint(obj_ptr, self.i64_ty, name="ptr_to_int")
                else:
                    obj_int = obj_ptr
                
                # 2. Verifica se é NULL (zero)
                is_null = self.builder.icmp_signed("==", obj_int, ir.Constant(self.i64_ty, 0), name="null_check")
                
                # 3. Cria blocos de controle de fluxo
                then_bb = self.builder.append_basic_block(name="safe.then")
                else_bb = self.builder.append_basic_block(name="safe.else")
                end_bb = self.builder.append_basic_block(name="safe.end")
                
                self.builder.cbranch(is_null, else_bb, then_bb)
                
                # 4. Se NÃO for nulo (then_bb): Carrega o membro normalmente
                self.builder.position_at_end(then_bb)
                elem_ptr = self.resolve_member_ptr(node)
                member_val = self.builder.load(elem_ptr, name="safe_member_val")
                self.builder.branch(end_bb)
                
                # 5. Se FOR nulo (else_bb): Retorna 0
                self.builder.position_at_end(else_bb)
                null_val = ir.Constant(self.i64_ty, 0)
                self.builder.branch(end_bb)
                
                # 6. Consolida o resultado (PHI Node)
                self.builder.position_at_end(end_bb)
                phi = self.builder.phi(self.i64_ty, name="safe_res")
                phi.add_incoming(member_val, then_bb)
                phi.add_incoming(null_val, else_bb)
                return phi
                
            # Acesso normal (sem ?.)
            obj_ptr = self.resolve_member_ptr(node)
            return self.builder.load(obj_ptr, name="member_val")
            
        elif isinstance(node, CallExpr):
            if node.name == "input":
                buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 256), name="input_buf")
                fmt_str = self.create_global_string("%s")
                self.builder.call(self.scanf, [fmt_str, buf])
                return self.builder.bitcast(buf, self.voidptr_ty)
                
            elif node.name == "atoi":
                arg_val = self.codegen_expr(node.args[0])
                return self.builder.call(self.atoi, [arg_val], name="atoi_call")
                
            elif node.name == "len":
                if isinstance(node.args[0], VariableExpr) and node.args[0].name in self.array_sizes:
                    size = self.array_sizes.get(node.args[0].name, 0)
                    return ir.Constant(self.i64_ty, size)
                else:
                    ptr = self.codegen_expr(node.args[0])
                    if ptr.type == self.voidptr_ty:
                        return self.builder.call(self.strlen, [ptr], name="strlen_call")
                    return ir.Constant(self.i64_ty, 0)
                    
            elif node.name == "free":
                if isinstance(node.args[0], VariableExpr):
                    var_name = node.args[0].name
                    for s in self.cleanup_vars:
                        if var_name in s:
                            s.remove(var_name)
                            break
                ptr = self.codegen_expr(node.args[0])
                if ptr.type != self.voidptr_ty:
                    ptr = self.builder.bitcast(ptr, self.voidptr_ty, name="manual_free_cast")
                self.builder.call(self.free, [ptr], name="free_call")
                return ir.Constant(self.i64_ty, 0)
                
            elif node.name == "alloc":
                size_val = self.codegen_expr(node.args[0])
                size_bytes = self.builder.mul(size_val, ir.Constant(self.i64_ty, 8), name="size_bytes")
                ptr_i8 = self.builder.call(self.malloc, [size_bytes], name="malloc_ptr")
                ptr_i64 = self.builder.bitcast(ptr_i8, self.i64_ty.as_pointer(), name="malloc_ptr_i64")
                return ptr_i64
                
            elif node.name == "alloc_bytes":
                size_val = self.codegen_expr(node.args[0])
                ptr = self.builder.call(self.malloc, [size_val], name="malloc_bytes_ptr")
                return ptr
                
            elif node.name == "argv":
                idx = self.codegen_expr(node.args[0])
                argv_ptr = self.symbol_table.get('argv')
                if not argv_ptr: raise Exception("Variável 'argv' não declarada.")
                argv_val = self.builder.load(argv_ptr, name="argv_val")
                arg_ptr_ptr = self.builder.gep(argv_val, [idx], name="arg_ptr_ptr")
                return self.builder.load(arg_ptr_ptr, name="arg_val")
                
            elif node.name == "read_file":
                filename_ptr = self.codegen_expr(node.args[0])
                mode_str = self.create_global_string("r")
                fp = self.builder.call(self.fopen, [filename_ptr, mode_str], name="file_ptr")
                
                is_null = self.builder.icmp_signed("==", fp, ir.Constant(self.voidptr_ty, None), name="is_null")
                then_bb = self.builder.append_basic_block(name="read_file.exists")
                else_bb = self.builder.append_basic_block(name="read_file.not_exists")
                end_bb = self.builder.append_basic_block(name="read_file.end")
                self.builder.cbranch(is_null, else_bb, then_bb)
                
                self.builder.position_at_end(then_bb)
                buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 4096), name="read_buf")
                buf_ptr = self.builder.bitcast(buf, self.voidptr_ty, name="buf_ptr")
                self.builder.call(self.fgets, [buf_ptr, ir.Constant(self.i32_ty, 4096), fp])
                self.builder.call(self.fclose, [fp])
                self.builder.branch(end_bb)
                
                self.builder.position_at_end(else_bb)
                empty_str = self.create_global_string("")
                self.builder.branch(end_bb)
                
                self.builder.position_at_end(end_bb)
                phi = self.builder.phi(self.voidptr_ty, name="read_file_res")
                phi.add_incoming(buf_ptr, then_bb)
                phi.add_incoming(empty_str, else_bb)
                return phi
                
            elif node.name == "write_file":
                filename_ptr = self.codegen_expr(node.args[0])
                content_ptr = self.codegen_expr(node.args[1])
                mode_str = self.create_global_string("w")
                fp = self.builder.call(self.fopen, [filename_ptr, mode_str], name="file_ptr_w")
                self.builder.call(self.fputs, [content_ptr, fp])
                self.builder.call(self.fclose, [fp])
                return ir.Constant(self.i64_ty, 0)
                
            elif node.name == "int":
                val = self.codegen_expr(node.args[0])
                res = self.builder.call(self.atoi, [val], name="atoi_call")
                opt_ty = self.struct_types.get("Option")
                if not opt_ty: raise Exception("Tipo Option não declarado.")
                ptr = self.builder.alloca(opt_ty, name="opt_tmp")
                is_zero = self.builder.icmp_signed("==", res, ir.Constant(self.i64_ty, 0), name="is_zero")
                tag_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)])
                payload_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)])
                tag_val = self.builder.zext(is_zero, self.i32_ty, name="tag_val")
                self.builder.store(tag_val, tag_ptr)
                self.builder.store(res, payload_ptr)
                return ptr
                
            elif node.name in self.variant_defs:
                enum_name, index, payload_type = self.variant_defs[node.name]
                enum_ty = self.struct_types[enum_name]
                ptr = self.builder.alloca(enum_ty, name="enum_tmp")
                tag_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)])
                payload_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)])
                self.builder.store(ir.Constant(self.i32_ty, index), tag_ptr)
                if node.args:
                    val = self.codegen_expr(node.args[0])
                    if val.type != self.i64_ty:
                        val = self.builder.zext(val, self.i64_ty, name="payload_cast")
                    self.builder.store(val, payload_ptr)
                else:
                    self.builder.store(ir.Constant(self.i64_ty, 0), payload_ptr)
                return ptr
                
            elif node.name == "float":
                val = self.codegen_expr(node.args[0])
                if val.type == self.i64_ty: return self.builder.sitofp(val, self.f64_ty, name="float_cast")
                return val
                
            elif node.name == "str":
                buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 256), name="str_cast_buf")
                buf_ptr = self.builder.bitcast(buf, self.voidptr_ty, name="cast_buf_ptr")
                val = self.codegen_expr(node.args[0])
                if val.type == self.i64_ty:
                    fmt_str = self.create_global_string("%ld")
                    self.builder.call(self.sprintf, [buf_ptr, fmt_str, val])
                elif val.type == self.f64_ty:
                    fmt_str = self.create_global_string("%f")
                    self.builder.call(self.sprintf, [buf_ptr, fmt_str, val])
                return buf_ptr
                
            elif node.name == "chr":
                val = self.codegen_expr(node.args[0])
                buf = self.builder.call(self.malloc, [ir.Constant(self.i64_ty, 2)], name="chr_malloc")
                fmt_str = self.create_global_string("%c")
                self.builder.call(self.sprintf, [buf, fmt_str, val], name="chr_sprintf")
                return buf
                
            elif node.name == "print":
                for arg_node in node.args:
                    if isinstance(arg_node, ArrayExpr):
                        for el in arg_node.elements:
                            arg_val = self.codegen_expr(el)
                            if isinstance(el, StringExpr):
                                fmt_str = self.create_global_string("%s ")
                                self.builder.call(self.printf, [fmt_str, arg_val])
                            else:
                                if arg_val.type == self.f64_ty: fmt_str = self.create_global_string("%f ")
                                else: fmt_str = self.create_global_string("%ld ")
                                self.builder.call(self.printf, [fmt_str, arg_val])
                    else:
                        arg_val = self.codegen_expr(arg_node)
                        if isinstance(arg_node, StringExpr):
                            fmt_str = self.create_global_string("%s ")
                            self.builder.call(self.printf, [fmt_str, arg_val])
                        else:
                            if arg_val.type == self.f64_ty: fmt_str = self.create_global_string("%f ")
                            elif arg_val.type == self.voidptr_ty: fmt_str = self.create_global_string("%s ")
                            else: fmt_str = self.create_global_string("%ld ")
                            self.builder.call(self.printf, [fmt_str, arg_val])
                nl_str = self.create_global_string("\n")
                self.builder.call(self.printf, [nl_str])
                return ir.Constant(self.i64_ty, 0)
                
            elif node.is_method:
                obj_node = node.args[0]
                obj_val = self.codegen_expr(obj_node)
                struct_ty = self.var_types.get(obj_node.name)
                if isinstance(struct_ty, ir.PointerType) and isinstance(struct_ty.pointee, ir.IdentifiedStructType):
                    struct_ty = struct_ty.pointee
                struct_name = struct_ty.name if struct_ty else "Unknown"
                func_name = f"{struct_name}_{node.name}"
                if func_name in self.functions_table:
                    func, func_type = self.functions_table[func_name]
                    args = [obj_val] + [self.codegen_expr(a) for a in node.args[1:]]
                    return self.builder.call(func, args, name=func_name + "_call")
                raise Exception(f"Método '{func_name}' não encontrado.")
                
            elif node.name in self.functions_table:
                func, func_type = self.functions_table[node.name]
                args = []
                for i, arg_node in enumerate(node.args):
                    arg_val = self.codegen_expr(arg_node)
                    if func_type.args[i] == self.f64_ty and arg_val.type == self.i64_ty: 
                        arg_val = self.to_float_if_needed(arg_val)
                    elif func_type.args[i] == self.i64_ty.as_pointer() and arg_val.type == self.voidptr_ty:
                        arg_val = self.builder.bitcast(arg_val, self.i64_ty.as_pointer(), name="arg_ptr_cast")
                    elif func_type.args[i] == self.voidptr_ty and isinstance(arg_val.type, ir.PointerType) and arg_val.type != self.voidptr_ty:
                        arg_val = self.builder.bitcast(arg_val, self.voidptr_ty, name="arg_void_cast")
                    args.append(arg_val)
                
                # NOVO: Se for um retorno direto, usa 'tail call' para ativar o TCO do LLVM!
                tail_flag = getattr(self, 'is_tail_return', False)
                
                # O llvmlite exige que o tail call seja o último instruction do bloco
                # Como logo abaixo virá o ret, isso é seguro.
                call_instr = self.builder.call(func, args, name=node.name + "_call", tail=tail_flag)
                return call_instr

        elif isinstance(node, PropagateExpr):
            # 1. Avalia a expressão (que retorna uma Enum por valor)
            enum_val = self.codegen_expr(node.val)
            
            # NOVO: Se for um valor de Struct (retornado por função), aloca na Stack para usar GEP
            if isinstance(enum_val.type, ir.IdentifiedStructType):
                enum_ptr = self.builder.alloca(enum_val.type, name="prop_tmp")
                self.builder.store(enum_val, enum_ptr)
            else:
                enum_ptr = enum_val # Já é um ponteiro
                
            # 2. Carrega a tag (índice da variante)
            tag_ptr = self.builder.gep(enum_ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)])
            tag_val = self.builder.load(tag_ptr, name="prop_tag")
            
            # 3. Compara se é erro (assumimos que índice >= 1 é erro)
            is_err = self.builder.icmp_signed("!=", tag_val, ir.Constant(self.i32_ty, 0), name="is_err")
            
            # 4. Cria blocos de controle
            then_bb = self.builder.append_basic_block(name="prop.ok")
            else_bb = self.builder.append_basic_block(name="prop.err")
            
            self.builder.cbranch(is_err, else_bb, then_bb)
            
            # 5. Se for ERRO: Retorna a Enum imediatamente da função atual!
            self.builder.position_at_end(else_bb)
            self.builder.ret(enum_val)
            
            # 6. Se for OK: Extrai o payload (valor útil) e continua
            self.builder.position_at_end(then_bb)
            payload_ptr = self.builder.gep(enum_ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)])
            return self.builder.load(payload_ptr, name="prop_val")

        raise Exception(f"Nó não suportado no Codegen: {type(node)}")