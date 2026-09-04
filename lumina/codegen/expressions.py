from llvmlite import ir
from ..ast import NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, TupleExpr, UnaryExpr

class ExpressionCodegen:
    # NOVO MÉTODO AUXILIAR RECURSIVO
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
            return ir.Constant(self.i64_ty, int(node.value))
        elif isinstance(node, BoolExpr):
            return ir.Constant(ir.IntType(1), 1 if node.value else 0)
        elif isinstance(node, StringExpr): 
            return self.create_global_string(node.value)
            
        # NOVO: Operador NOT
        elif isinstance(node, UnaryExpr):
            if node.op == 'not':
                val = self.codegen_expr(node.val)
                # Garante que o valor é um booleano (i1) antes de inverter
                if val.type != ir.IntType(1):
                    val = self.builder.icmp_signed("!=", val, ir.Constant(val.type, 0), name="not_cond")
                # Inverte o booleano (XOR com True)
                return self.builder.xor(val, ir.Constant(ir.IntType(1), 1), name="not_tmp")
            
        elif isinstance(node, AddressOfExpr):
            if isinstance(node.val, VariableExpr):
                ptr = self.symbol_table.get(node.val.name)
                if not ptr: raise Exception(f"Variável '{node.val.name}' não declarada.")
                return self.builder.bitcast(ptr, self.voidptr_ty, name="addr_of")
            raise Exception("Endereço de memória só pode ser pego de variáveis.")
            
        elif isinstance(node, DerefExpr):
            ptr = self.codegen_expr(node.val)
            if ptr.type == self.voidptr_ty:
                ptr = self.builder.bitcast(ptr, self.i64_ty.as_pointer(), name="deref_ptr_cast")
            return self.builder.load(ptr, name="deref_val")
            
        elif isinstance(node, VariableExpr):
            # NOVO: Se a "variável" for na verdade um construtor de Enum sem argumentos (ex: None)
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
            if isinstance(ptr.type.pointee, ir.IdentifiedStructType): return ptr
            return self.builder.load(ptr, name=node.name + "_val")
            
        elif isinstance(node, BinaryExpr):
            left = self.codegen_expr(node.left)
            right = self.codegen_expr(node.right)
            
            # NOVO: Operadores Lógicos (and, or)
            if node.op in ('and', 'or'):
                # Garante que ambos os lados são i1 (booleanos no LLVM)
                if left.type != ir.IntType(1):
                    left = self.builder.icmp_signed("!=", left, ir.Constant(left.type, 0), name="and_left_cond")
                if right.type != ir.IntType(1):
                    right = self.builder.icmp_signed("!=", right, ir.Constant(right.type, 0), name="and_right_cond")
                    
                if node.op == 'and': return self.builder.and_(left, right, name="and_tmp")
                elif node.op == 'or': return self.builder.or_(left, right, name="or_tmp")
            
            # Concatenação de String
            if node.op == '+' and (isinstance(node.left, StringExpr) or isinstance(node.right, StringExpr)):
                buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 256), name="str_concat_buf")
                buf_ptr = self.builder.bitcast(buf, self.voidptr_ty, name="buf_ptr")
                
                if left.type == self.voidptr_ty and right.type == self.i64_ty:
                    fmt_str = self.create_global_string("%s%d")
                    self.builder.call(self.sprintf, [buf_ptr, fmt_str, left, right], name="sprintf_str_int")
                elif left.type == self.i64_ty and right.type == self.voidptr_ty:
                    fmt_str = self.create_global_string("%d%s")
                    self.builder.call(self.sprintf, [buf_ptr, fmt_str, left, right], name="sprintf_int_str")
                else:
                    fmt_str = self.create_global_string("%s%s")
                    self.builder.call(self.sprintf, [buf_ptr, fmt_str, left, right], name="sprintf_str_str")
                    
                return buf_ptr
            
            # Atribuição Composta (+=, -=, etc)
            if node.op in ('+=', '-=', '*=', '/='):
                op = node.op[0] # Pega o primeiro caractere: '+', '-', '*', '/'
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
            
            # Aritmética de Ponteiros (ptr + int)
            if isinstance(left.type, ir.PointerType) and right.type == self.i64_ty:
                if node.op == '+':
                    return self.builder.gep(left, [right], name="ptr_add_tmp")
                elif node.op == '-':
                    neg_right = self.builder.neg(right, name="neg_idx")
                    return self.builder.gep(left, [neg_right], name="ptr_sub_tmp")
                    
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
                    if ptr.type == self.voidptr_ty:
                        ptr = self.builder.bitcast(ptr, self.i64_ty.as_pointer(), name="heap_cast")
                    elem_ptr = self.builder.gep(ptr, [idx_val], name="heap_elem_ptr")
                    return self.builder.load(elem_ptr, name="heap_elem_val")
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
                arr_name = node.args[0].name
                size = self.array_sizes.get(arr_name, 0)
                return ir.Constant(self.i64_ty, size)
            elif node.name == "free":
                # NOVO: Se o usuário chamou free manualmente, remove da pilha de auto-free
                if isinstance(node.args[0], VariableExpr):
                    var_name = node.args[0].name
                    for s in self.cleanup_vars:
                        if var_name in s:
                            s.remove(var_name)
                            break
                ptr = self.codegen_expr(node.args[0])
                self.builder.call(self.free, [ptr], name="free_call")
                return ir.Constant(self.i64_ty, 0)
            elif node.name == "alloc":
                size_val = self.codegen_expr(node.args[0])
                size_bytes = self.builder.mul(size_val, ir.Constant(self.i64_ty, 8), name="size_bytes")
                ptr = self.builder.call(self.malloc, [size_bytes], name="malloc_ptr")
                return ptr
                
            # NOVO: Lê argumentos da linha de comando (argv)
            elif node.name == "argv":
                idx = self.codegen_expr(node.args[0])
                argv_ptr = self.symbol_table.get('argv')
                if not argv_ptr: raise Exception("Variável 'argv' não declarada.")
                argv_val = self.builder.load(argv_ptr, name="argv_val")
                arg_ptr_ptr = self.builder.gep(argv_val, [idx], name="arg_ptr_ptr")
                return self.builder.load(arg_ptr_ptr, name="arg_val")
                
            # NOVO: Lê um arquivo do disco
            elif node.name == "read_file":
                filename_ptr = self.codegen_expr(node.args[0])
                mode_str = self.create_global_string("r")
                fp = self.builder.call(self.fopen, [filename_ptr, mode_str], name="file_ptr")
                buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 4096), name="read_buf")
                buf_ptr = self.builder.bitcast(buf, self.voidptr_ty, name="buf_ptr")
                self.builder.call(self.fgets, [buf_ptr, ir.Constant(self.i32_ty, 4096), fp])
                self.builder.call(self.fclose, [fp])
                return buf_ptr
                
            # NOVO: Escreve em um arquivo do disco
            elif node.name == "write_file":
                filename_ptr = self.codegen_expr(node.args[0])
                content_ptr = self.codegen_expr(node.args[1])
                mode_str = self.create_global_string("w")
                fp = self.builder.call(self.fopen, [filename_ptr, mode_str], name="file_ptr_w")
                self.builder.call(self.fputs, [content_ptr, fp])
                self.builder.call(self.fclose, [fp])
                return ir.Constant(self.i64_ty, 0)
                
            # NOVO: Casts de Tipo
            elif node.name == "int":
                val = self.codegen_expr(node.args[0])
                # int("abc") -> None
                # int("42")  -> Some(42)
                # Como não temos a função strtol do C com checagem de erro aqui, 
                # vamos simplificar convertendo com atoi. Se for 0, dizemos que é None.
                res = self.builder.call(self.atoi, [val], name="atoi_call")
                
                # Cria a struct Option na memória
                opt_ty = self.struct_types.get("Option")
                if not opt_ty: raise Exception("Tipo Option não declarado.")
                ptr = self.builder.alloca(opt_ty, name="opt_tmp")
                
                # Se res == 0, assumimos que falhou (None). Senão, Some(res).
                is_zero = self.builder.icmp_signed("==", res, ir.Constant(self.i64_ty, 0), name="is_zero")
                
                tag_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)])
                payload_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)])
                
                # Tag: 0 para None, 1 para Some
                tag_val = self.builder.zext(is_zero, self.i32_ty, name="tag_val")
                self.builder.store(tag_val, tag_ptr)
                self.builder.store(res, payload_ptr)
                return ptr
            # NOVO: Construtores de Enum (Some, None, Ok, Err)
            elif node.name in self.variant_defs:
                enum_name, index, payload_type = self.variant_defs[node.name]
                enum_ty = self.struct_types[enum_name]
                
                ptr = self.builder.alloca(enum_ty, name="enum_tmp")
                tag_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)])
                payload_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)])
                
                self.builder.store(ir.Constant(self.i32_ty, index), tag_ptr)
                
                # Se tiver argumento (ex: Some(10)), guardamos no payload
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
                    fmt_str = self.create_global_string("%d")
                    self.builder.call(self.sprintf, [buf_ptr, fmt_str, val])
                elif val.type == self.f64_ty:
                    fmt_str = self.create_global_string("%f")
                    self.builder.call(self.sprintf, [buf_ptr, fmt_str, val])
                return buf_ptr
                
            elif node.name == "print":
                for arg_node in node.args:
                    arg_val = self.codegen_expr(arg_node)
                    if isinstance(arg_node, StringExpr):
                        fmt_str = self.create_global_string("%s ")
                        self.builder.call(self.printf, [fmt_str, arg_val])
                    else:
                        if arg_val.type == self.f64_ty: fmt_str = self.create_global_string("%f ")
                        elif arg_val.type == self.voidptr_ty: fmt_str = self.create_global_string("%s ")
                        else: fmt_str = self.create_global_string("%d ")
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
                    if func_type.args[i] == self.f64_ty and arg_val.type == self.i64_ty: arg_val = self.to_float_if_needed(arg_val)
                    args.append(arg_val)
                return self.builder.call(func, args, name=node.name + "_call")
                
        raise Exception(f"Nó não suportado no Codegen: {type(node)}")