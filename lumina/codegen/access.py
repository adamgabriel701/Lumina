from llvmlite import ir
from ..ast import VariableExpr, IndexExpr, MemberExpr, DerefExpr, AddressOfExpr, BinaryExpr, CallExpr, NumberExpr, StringExpr, BoolExpr

class AccessCodegen:
    def resolve_member_ptr(self, node):
        if isinstance(node.obj, VariableExpr):
            ptr = self.symbol_table.get(node.obj.name)
            if not ptr: raise Exception(f"Variável '{node.obj.name}' não declarada.")
            struct_ty = self.var_types.get(node.obj.name)
            if isinstance(struct_ty, ir.PointerType) and isinstance(struct_ty.pointee, ir.IdentifiedStructType): struct_ty = struct_ty.pointee
        else:
            ptr = self.codegen_expr(node.obj); struct_ty = ptr.type.pointee
        elem_index = 0
        for s_name, s_fields in self.struct_fields.items():
            if self.struct_types[s_name] == struct_ty: elem_index = s_fields.get(node.member, 0); break
        return self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, elem_index)], name="member_ptr", inbounds=True)

    def codegen_variable(self, node):
        if node.name in self.variant_defs:
            enum_name, index, _ = self.variant_defs[node.name]
            ptr = self.builder.alloca(self.struct_types[enum_name], name="enum_tmp")
            self.builder.store(ir.Constant(self.i32_ty, index), self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)]))
            self.builder.store(ir.Constant(self.i64_ty, 0), self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)]))
            return ptr
            
        ptr = self.symbol_table.get(node.name)
        if not ptr: raise Exception(f"Variável '{node.name}' não declarada.")
        
        if isinstance(ptr, ir.GlobalVariable): 
            return self.builder.load(ptr, name=node.name + "_gval")
            
        if isinstance(ptr.type.pointee, ir.IdentifiedStructType): 
            return ptr
            
        # NOVO: Se for um array dinâmico alocado (i64*), retorna o ponteiro direto para permitir indexação t1[0]
        if node.name in self.heap_int_arrays:
            return ptr
            
        return self.builder.load(ptr, name=node.name + "_val")

    def codegen_member(self, node):
        obj_ptr = self.resolve_member_ptr(node)
        if node.is_safe:
            obj_int = self.builder.ptrtoint(obj_ptr, self.i64_ty, name="ptr_to_int")
            is_null = self.builder.icmp_signed("==", obj_int, ir.Constant(self.i64_ty, 0), name="null_check")
            then_bb, else_bb, end_bb = self.builder.append_basic_block(name="safe.then"), self.builder.append_basic_block(name="safe.else"), self.builder.append_basic_block(name="safe.end")
            self.builder.cbranch(is_null, else_bb, then_bb)
            self.builder.position_at_end(then_bb); member_val = self.builder.load(obj_ptr, name="safe_member_val"); self.builder.branch(end_bb)
            self.builder.position_at_end(else_bb); null_val = ir.Constant(self.i64_ty, 0); self.builder.branch(end_bb)
            self.builder.position_at_end(end_bb); phi = self.builder.phi(self.i64_ty, name="safe_res"); phi.add_incoming(member_val, then_bb); phi.add_incoming(null_val, else_bb)
            return phi
        return self.builder.load(obj_ptr, name="member_val")

    def codegen_index(self, node):
        # NOVO: Suporte a Slicing de Strings (ex: text[1..5])
        if isinstance(node.index, BinaryExpr) and node.index.op == '..':
            ptr = self.codegen_expr(node.array)
            # Só faz sentido para strings (voidptr)
            if ptr.type == self.voidptr_ty:
                start_val = self.codegen_expr(node.index.left)
                end_val = self.codegen_expr(node.index.right)
                
                # Calcula o tamanho da fatia (end - start)
                slice_len = self.builder.sub(end_val, start_val, name="slice_len")
                # Adiciona 1 byte para o null terminator \0
                alloc_size = self.builder.add(slice_len, ir.Constant(self.i64_ty, 1), name="slice_alloc_size")
                
                # Aloca memória para a nova string
                buf = self.builder.call(self.malloc, [alloc_size], name="slice_buf")
                
                # Calcula o ponteiro de origem (ptr + start)
                src_ptr = self.builder.gep(ptr, [start_val], name="slice_src")
                
                # Usa strncpy para copiar exatamente o tamanho da fatia
                strncpy_fn = next((f for f in self.module.functions if f.name == "strncpy"), None)
                if not strncpy_fn:
                    strncpy_ty = ir.FunctionType(self.voidptr_ty, [self.voidptr_ty, self.voidptr_ty, self.i64_ty])
                    strncpy_fn = ir.Function(self.module, strncpy_ty, name="strncpy")
                
                self.builder.call(strncpy_fn, [buf, src_ptr, slice_len], name="strncpy_call")
                
                # Adiciona o null terminator no final da nova string
                null_ptr = self.builder.gep(buf, [slice_len], name="slice_null_ptr")
                self.builder.store(ir.Constant(self.i8_ty, 0), null_ptr)
                
                return buf

        # Fallback para o comportamento original de indexação
        if isinstance(node.array, VariableExpr) and node.array.name in self.array_sizes:
            arr_ptr = self.symbol_table.get(node.array.name); idx_val = self.codegen_expr(node.index)
            if idx_val.type == self.f64_ty: idx_val = self.builder.fptosi(idx_val, self.i64_ty, name="idx_int")
            elif isinstance(idx_val.type, ir.PointerType): idx_val = self.builder.ptrtoint(idx_val, self.i64_ty, name="ptr_to_int")
            return self.builder.load(self.builder.gep(arr_ptr, [ir.Constant(self.i32_ty, 0), idx_val], name="elem_ptr"), name="arr_elem_val")
            
        ptr = self.codegen_expr(node.array); idx_val = self.codegen_expr(node.index)
        if idx_val.type == self.f64_ty: idx_val = self.builder.fptosi(idx_val, self.i64_ty, name="idx_int")
        elif isinstance(idx_val.type, ir.PointerType): idx_val = self.builder.ptrtoint(idx_val, self.i64_ty, name="ptr_to_int")
        if isinstance(ptr.type, ir.PointerType) and ptr.type.pointee == self.i64_ty: return self.builder.load(self.builder.gep(ptr, [idx_val], name="heap_elem_ptr"), name="heap_elem_val")
        elif ptr.type == self.voidptr_ty: return self.builder.zext(self.builder.load(self.builder.gep(ptr, [idx_val], name="char_ptr"), name="char_val"), self.i64_ty, name="char_as_int")
        return self.builder.load(self.builder.gep(ptr, [idx_val], name="elem_ptr"), name="elem_val")

    def codegen_deref(self, node):
        ptr = self.codegen_expr(node.val)
        if ptr.type == self.voidptr_ty: ptr = self.builder.bitcast(ptr, self.i64_ty.as_pointer(), name="deref_ptr_cast")
        return self.builder.load(ptr, name="deref_val")

    def codegen_address_of(self, node):
        # NOVO: Suporta pegar o endereço de um campo de struct (ex: &c.mutex)
        if isinstance(node.val, MemberExpr):
            ptr = self.resolve_member_ptr(node.val)
            # NOVO: FFI sempre espera ponteiros genéricos (i64*), então faz bitcast
            return self.builder.bitcast(ptr, self.i64_ty.as_pointer(), name="member_addr_cast")
            
        if isinstance(node.val, VariableExpr):
            if node.val.name in self.functions_table: 
                return self.builder.ptrtoint(self.functions_table[node.val.name][0], self.i64_ty, name="fn_ptr_int")
            ptr = self.symbol_table.get(node.val.name)
            if not ptr: raise Exception(f"Variável '{node.val.name}' não declarada.")
            return self.builder.bitcast(ptr, self.ivoidptr_ty, name="addr_of")
        raise Exception("Endereço de memória só pode ser pego de variáveis ou funções.")