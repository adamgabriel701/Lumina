from llvmlite import ir
from ..ast import ReturnStmt, VarDecl, AssignStmt, IfStmt, WhileStmt, ForStmt, MemberExpr, ArrayExpr, MatchStmt, DerefExpr, IndexExpr, VariableExpr, CallExpr, ContinueStmt, DeferStmt

class StatementCodegen:
    def codegen_stmt(self, node):
        if isinstance(node, VarDecl):
            if node.var_type in self.struct_types:
                struct_ty = self.struct_types[node.var_type]
                ptr = self.builder.alloca(struct_ty, name=node.name)
                self.symbol_table[node.name] = ptr
                self.var_types[node.name] = struct_ty
            elif isinstance(node.value, ArrayExpr):
                num_elements = len(node.value.elements)
                arr_ty = ir.ArrayType(self.i64_ty, num_elements)
                ptr = self.builder.alloca(arr_ty, name=node.name)
                self.var_types[node.name] = arr_ty
                self.symbol_table[node.name] = ptr
                self.array_sizes[node.name] = num_elements
                for i, el in enumerate(node.value.elements):
                    el_val = self.codegen_expr(el)
                    if el_val.type != self.i64_ty: el_val = self.builder.fptosi(el_val, self.i64_ty, name="to_int")
                    elem_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)])
                    self.builder.store(el_val, elem_ptr)
            else:
                val = self.codegen_expr(node.value) if node.value else ir.Constant(self.i64_ty, 0)
                var_ty = val.type
                if node.var_type == "float":
                    var_ty = self.f64_ty
                    val = self.to_float_if_needed(val)
                ptr = self.builder.alloca(var_ty, name=node.name)
                self.builder.store(val, ptr)
                self.symbol_table[node.name] = ptr
                self.var_types[node.name] = var_ty
                
                # NOVO: Se a variável recebeu um alloc, adiciona ao escopo para auto-free
                if isinstance(node.value, CallExpr) and node.value.name == "alloc":
                    self.cleanup_vars[-1].add(node.name)
                    # NOVO: Marca como array de inteiros no Heap
                    self.heap_int_arrays.add(node.name)

        elif isinstance(node, AssignStmt):
            if isinstance(node.target, DerefExpr):
                ptr = self.codegen_expr(node.target.val)
                if ptr.type == self.voidptr_ty:
                    ptr = self.builder.bitcast(ptr, self.i64_ty.as_pointer(), name="ptr_cast")
                val = self.codegen_expr(node.value)
                self.builder.store(val, ptr)
            elif isinstance(node.target, IndexExpr):
                # Se for array da pilha (Stack)
                if isinstance(node.target.array, VariableExpr) and node.target.array.name in self.array_sizes:
                    arr_ptr = self.symbol_table.get(node.target.array.name)
                    idx_val = self.codegen_expr(node.target.index)
                    if idx_val.type != self.i64_ty: idx_val = self.builder.fptosi(idx_val, self.i64_ty, name="idx_int")
                    elem_ptr = self.builder.gep(arr_ptr, [ir.Constant(self.i32_ty, 0), idx_val], name="assign_elem_ptr")
                    val = self.codegen_expr(node.value)
                    self.builder.store(val, elem_ptr)
                else:
                    # Se for array do Heap
                    ptr = self.codegen_expr(node.target.array)
                    idx_val = self.codegen_expr(node.target.index)
                    if idx_val.type != self.i64_ty: idx_val = self.builder.fptosi(idx_val, self.i64_ty, name="idx_int")
                    
                    val = self.codegen_expr(node.value)
                    
                    # NOVO: Verifica o tipo do ponteiro para saber se é array de bytes ou de inteiros
                    if ptr.type == self.voidptr_ty:
                        # É um array de bytes (alloc_bytes)
                        if val.type == self.i64_ty:
                            val = self.builder.trunc(val, self.i8_ty, name="byte_trunc")
                    # Se for i64* (alloc), não faz nada, salva o i64 direto
                    
                    elem_ptr = self.builder.gep(ptr, [idx_val], name="heap_assign_ptr")
                    self.builder.store(val, elem_ptr)
            elif isinstance(node.target, MemberExpr):
                obj_ptr = self.resolve_member_ptr(node.target)
                val = self.codegen_expr(node.value)
                if isinstance(val.type, ir.PointerType) and isinstance(obj_ptr.type.pointee, ir.PointerType):
                    val = self.builder.bitcast(val, obj_ptr.type.pointee, name="ptr_cast")
                self.builder.store(val, obj_ptr)
            else:
                ptr = self.symbol_table.get(node.target.name)
                if not ptr: raise Exception(f"Variável '{node.target.name}' não declarada.")
                val = self.codegen_expr(node.value)
                var_ty = self.var_types[node.target.name]
                if var_ty == self.f64_ty and val.type == self.i64_ty: val = self.to_float_if_needed(val)
                self.builder.store(val, ptr)
                
                # NOVO: Se a reatribuição for um alloc, marca como array do Heap
                if isinstance(node.value, CallExpr) and node.value.name == "alloc":
                    self.heap_int_arrays.add(node.target.name)

        elif isinstance(node, ReturnStmt):
            # NOVO: Executa todos os 'defer' antes de retornar!
            for body in reversed(self.deferred_stmts):
                for stmt in body: self.codegen_stmt(stmt)
            self.deferred_stmts.clear()
            
            val = self.codegen_expr(node.values[0])
            if isinstance(val.type, ir.PointerType) and isinstance(val.type.pointee, ir.IdentifiedStructType):
                val = self.builder.load(val, name="ret_val")
            for scope in self.cleanup_vars:
                self.cleanup_block(scope)
            self.builder.ret(val)

        elif isinstance(node, IfStmt):
            cond_val = self.codegen_expr(node.condition)
            if cond_val.type != ir.IntType(1): cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(self.i64_ty, 0), name="if_cond")
            then_bb = self.builder.append_basic_block(name="if.then")
            else_bb = self.builder.append_basic_block(name="if.else") if node.else_body else None
            end_bb = self.builder.append_basic_block(name="if.end")
            if else_bb: self.builder.cbranch(cond_val, then_bb, else_bb)
            else: self.builder.cbranch(cond_val, then_bb, end_bb)
            
            self.builder.position_at_end(then_bb)
            self.cleanup_vars.append(set()) # Empilha escopo
            for stmt in node.then_body: self.codegen_stmt(stmt)
            if not self.builder.block.is_terminated:
                self.cleanup_block(self.cleanup_vars.pop()) # Limpa antes de sair
                self.builder.branch(end_bb)
            else:
                self.cleanup_vars.pop()
                
            if else_bb:
                self.builder.position_at_end(else_bb)
                self.cleanup_vars.append(set()) # Empilha escopo
                for stmt in node.else_body: self.codegen_stmt(stmt)
                if not self.builder.block.is_terminated:
                    self.cleanup_block(self.cleanup_vars.pop()) # Limpa antes de sair
                    self.builder.branch(end_bb)
                else:
                    self.cleanup_vars.pop()
            self.builder.position_at_end(end_bb)

        elif isinstance(node, WhileStmt):
            cond_bb = self.builder.append_basic_block(name="while.cond")
            body_bb = self.builder.append_basic_block(name="while.body")
            end_bb = self.builder.append_basic_block(name="while.end")
            self.builder.branch(cond_bb)
            self.builder.position_at_end(cond_bb)
            cond_val = self.codegen_expr(node.condition)
            if cond_val.type != ir.IntType(1): cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(self.i64_ty, 0), name="while_cond")
            self.builder.cbranch(cond_val, body_bb, end_bb)
            
            self.builder.position_at_end(body_bb)
            self.cleanup_vars.append(set())
            old_continue = self.continue_block
            self.continue_block = cond_bb # NOVO: Continue pula para a condição
            
            for stmt in node.body: self.codegen_stmt(stmt)
            self.continue_block = old_continue # Restaura
            
            if not self.builder.block.is_terminated:
                self.cleanup_block(self.cleanup_vars.pop())
                self.builder.branch(cond_bb)
            else:
                self.cleanup_vars.pop()
            self.builder.position_at_end(end_bb)

        elif isinstance(node, ForStmt):
            ptr = self.builder.alloca(self.i64_ty, name=node.var_name)
            start_val = self.codegen_expr(node.start)
            if start_val.type != self.i64_ty: start_val = self.builder.fptosi(start_val, self.i64_ty, name="for_start_int")
            self.builder.store(start_val, ptr)
            self.symbol_table[node.var_name] = ptr
            self.var_types[node.var_name] = self.i64_ty
            end_val = self.codegen_expr(node.end)
            if end_val.type != self.i64_ty: end_val = self.builder.fptosi(end_val, self.i64_ty, name="for_end_int")

            cond_bb = self.builder.append_basic_block(name="for.cond")
            body_bb = self.builder.append_basic_block(name="for.body")
            inc_bb = self.builder.append_basic_block(name="for.inc") # NOVO: Bloco de incremento
            end_bb = self.builder.append_basic_block(name="for.end")
            
            self.builder.branch(cond_bb)
            self.builder.position_at_end(cond_bb)
            curr_val = self.builder.load(ptr, name=node.var_name + "_val")
            cond = self.builder.icmp_signed("<", curr_val, end_val, name="for_cond")
            self.builder.cbranch(cond, body_bb, end_bb)
            
            self.builder.position_at_end(body_bb)
            self.cleanup_vars.append(set())
            old_continue = self.continue_block
            self.continue_block = inc_bb # NOVO: Continue pula para o incremento
            
            for stmt in node.body: self.codegen_stmt(stmt)
            self.continue_block = old_continue # Restaura
            
            if not self.builder.block.is_terminated:
                self.cleanup_block(self.cleanup_vars.pop())
                self.builder.branch(inc_bb)
            else:
                self.cleanup_vars.pop()
                
            # NOVO: Bloco de Incremento
            self.builder.position_at_end(inc_bb)
            next_val = self.builder.add(curr_val, ir.Constant(self.i64_ty, 1), name="for_next")
            self.builder.store(next_val, ptr)
            self.builder.branch(cond_bb)
            
            self.builder.position_at_end(end_bb)
            
        elif isinstance(node, MatchStmt):
            cond_val = self.codegen_expr(node.condition)
            # cond_val é um ponteiro para {i32, i64}
            tag_ptr = self.builder.gep(cond_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)])
            tag_val = self.builder.load(tag_ptr, name="enum_tag")
            
            default_bb = self.builder.append_basic_block(name="match.default")
            end_bb = self.builder.append_basic_block(name="match.end")
            sw = self.builder.switch(tag_val, default_bb)
            
            for variant_name, var_name, body in node.cases:
                if variant_name not in self.variant_defs:
                    raise Exception(f"Variante '{variant_name}' não existe.")
                    
                enum_name, index, payload_type = self.variant_defs[variant_name]
                case_bb = self.builder.append_basic_block(name=f"match.case_{variant_name}")
                sw.add_case(ir.Constant(self.i32_ty, index), case_bb)
                
                self.builder.position_at_end(case_bb)
                
                # NOVO: Se houver extração (case Some(x):), carrega o payload e cria a variável x
                if var_name:
                    payload_ptr = self.builder.gep(cond_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)])
                    payload_val = self.builder.load(payload_ptr, name=var_name + "_val")
                    
                    # Para simplificar, todas as variants guardam i64 (int ou ptr). Alocamos como i64.
                    var_ptr = self.builder.alloca(self.i64_ty, name=var_name)
                    self.builder.store(payload_val, var_ptr)
                    self.symbol_table[var_name] = var_ptr
                    self.var_types[var_name] = self.i64_ty
                    
                self.cleanup_vars.append(set())
                for stmt in body: self.codegen_stmt(stmt)
                if not self.builder.block.is_terminated:
                    self.cleanup_block(self.cleanup_vars.pop())
                    self.builder.branch(end_bb)
                else:
                    self.cleanup_vars.pop()
                    
            self.builder.position_at_end(default_bb)
            if node.default:
                self.cleanup_vars.append(set())
                for stmt in node.default: self.codegen_stmt(stmt)
                if not self.builder.block.is_terminated:
                    self.cleanup_block(self.cleanup_vars.pop())
                    self.builder.branch(end_bb)
                else:
                    self.cleanup_vars.pop()
            else:
                # NOVO: Se não houver default, o bloco default pula direto para o fim
                self.builder.branch(end_bb)
                
            self.builder.position_at_end(end_bb)
        # NOVO: Continue
        elif isinstance(node, ContinueStmt):
            if self.continue_block:
                self.cleanup_block(self.cleanup_vars[-1])
                self.builder.branch(self.continue_block)
                
        # NOVO: Defer (Guarda os statements para rodar no fim)
        elif isinstance(node, DeferStmt):
            self.deferred_stmts.append(node.body)
            
        else:
            self.codegen_expr(node)