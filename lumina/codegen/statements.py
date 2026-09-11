from llvmlite import ir

from ..ast import (
    VarDecl, AssignStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt, 
    BreakStmt, ContinueStmt, MatchStmt, DeferStmt, AssertStmt, 
    BenchStmt, DestructureStmt, CallExpr, BinaryExpr
)
from ..ast.visitor import NodeVisitor

class StatementCodegen(NodeVisitor):
    
    def visit_VarDecl(self, node):
        # 1. Avalia a expressão para obter o valor LLVM
        val = self.visit(node.value) if node.value else None
        
        # 2. Pega o tipo inferido pelo Analisador Semântico
        var_type = node.var_type if node.var_type else "int"
            
        # 3. Calcula o tipo LLVM correto para alocação
        # Se for uma Struct, aloca um ponteiro para ela
        if var_type in self.struct_types and not var_type.endswith("*"):
            llvm_ty = self.struct_types[var_type].as_pointer()
        else:
            llvm_ty = self.get_llvm_type(var_type)
            
        # 4. Aloca o ponteiro na memória local
        ptr = self.builder.alloca(llvm_ty, name=node.name)
        self.symbol_table[node.name] = ptr
        self.var_types[node.name] = var_type
        
        # 5. Se houver valor, armazena com segurança
        if val is not None:
            # Fallback de segurança: Se a variável é i64 mas o valor é i8* (string), 
            # converte a string para inteiro antes de armazenar.
            if llvm_ty == self.i64_ty and val.type == self.voidptr_ty:
                # Tenta converter string para int (atoi)
                res = self.builder.call(self.atoi, [val], name="str_to_int_call")
                self.builder.store(res, ptr)
            # Fallback de segurança: Se a variável é string (i8*) mas o valor é i64 (int),
            # converte o int para string antes de armazenar.
            elif llvm_ty == self.voidptr_ty and val.type == self.i64_ty:
                int_buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 32), name="int_to_str_buf")
                int_buf_ptr = self.builder.bitcast(int_buf, self.voidptr_ty, name="int_str_ptr")
                fmt_str = self.create_global_string("%ld")
                self.builder.call(self.snprintf, [int_buf_ptr, ir.Constant(self.i64_ty, 32), fmt_str, val], name="int_to_str_call")
                self.builder.store(int_buf_ptr, ptr)
            else:
                # Armazenamento normal
                self.builder.store(val, ptr)

        # Marca para o GC se for uma alocação
        if isinstance(node.value, CallExpr) and getattr(node.value.callee, 'name', None) == "alloc":
            self.heap_allocs.add(node.name)

    def visit_AssignStmt(self, node):
        val = self.visit(node.value)
        
        if hasattr(node.target, 'name'): # VariableExpr
            ptr = self.symbol_table.get(node.target.name)
            if ptr:
                if val.type == self.f64_ty and ptr.type.pointee == self.i64_ty:
                    val = self.builder.fptosi(val, self.i64_ty, name="assign_cast")
                self.builder.store(val, ptr)

        elif hasattr(node.target, 'member'): # MemberExpr
            obj_val = self.visit(node.target.obj)
            if isinstance(obj_val.type, ir.PointerType) and isinstance(obj_val.type.pointee, ir.IdentifiedStructType):
                struct_name = obj_val.type.pointee.name
                field_idx = self.struct_fields[struct_name].get(node.target.member)
                if field_idx is not None:
                    elem_ptr = self.builder.gep(obj_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, field_idx)])
                    self.builder.store(val, elem_ptr)

        elif hasattr(node.target, 'index'): # IndexExpr
            arr_val = self.visit(node.target.array)
            idx_val = self.visit(node.target.index)
            if isinstance(arr_val.type, ir.PointerType) and isinstance(arr_val.type.pointee, ir.ArrayType):
                elem_ptr = self.builder.gep(arr_val, [ir.Constant(self.i32_ty, 0), idx_val])
                self.builder.store(val, elem_ptr)

    def visit_ReturnStmt(self, node):
        if not node.values:
            self.builder.ret_void()
            return
            
        val = self.visit(node.values[0])
        ret_ty = self.functions_table[self.current_func_name][1].return_type
        
        if val.type != ret_ty:
            if ret_ty == self.f64_ty and val.type == self.i64_ty:
                val = self.builder.sitofp(val, self.f64_ty, name="ret_cast")
            elif ret_ty == self.i64_ty and val.type == self.f64_ty:
                val = self.builder.fptosi(val, self.i64_ty, name="ret_cast")
                
        self.builder.ret(val)

    def visit_IfStmt(self, node):
        cond_val = self.visit(node.condition)
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(cond_val.type, 0), name="if_cond")
            
        then_bb = self.builder.append_basic_block(name="if.then")
        else_bb = self.builder.append_basic_block(name="if.else")
        end_bb = self.builder.append_basic_block(name="if.end")
        
        self.builder.cbranch(cond_val, then_bb, else_bb)
        
        # Then block
        self.builder.position_at_end(then_bb)
        for stmt in node.then_body:
            self.visit(stmt)
        # CORREÇÃO: Garante que o bloco then termina antes de ir para o end_bb
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)
            
        # Else block
        self.builder.position_at_end(else_bb)
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
        # CORREÇÃO: Garante que o bloco else termina antes de ir para o end_bb
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)
            
        self.builder.position_at_end(end_bb)

    def visit_WhileStmt(self, node):
        cond_bb = self.builder.append_basic_block(name="while.cond")
        body_bb = self.builder.append_basic_block(name="while.body")
        end_bb = self.builder.append_basic_block(name="while.end")
        
        self.builder.branch(cond_bb)
        
        self.builder.position_at_end(cond_bb)
        cond_val = self.visit(node.condition)
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(cond_val.type, 0), name="while_cond")
        self.builder.cbranch(cond_val, body_bb, end_bb)
        
        self.builder.position_at_end(body_bb)
        for stmt in node.body:
            self.visit(stmt)
            
        # CORREÇÃO CRÍTICA: Adiciona o pulo de volta para o condition block
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_bb)
            
        self.builder.position_at_end(end_bb)

    def visit_ForStmt(self, node):
        if node.iterable is not None and isinstance(node.iterable, BinaryExpr) and node.iterable.op == '..':
            start_val = self.visit(node.iterable.left)
            end_val = self.visit(node.iterable.right)
        else:
            start_val = self.visit(node.start) if node.start else ir.Constant(self.i64_ty, 0)
            end_val = self.visit(node.end) if node.end else ir.Constant(self.i64_ty, 0)
        
        if start_val.type != self.i64_ty:
            start_val = self.builder.fptosi(start_val, self.i64_ty, name="for_start_cast")
        if end_val.type != self.i64_ty:
            end_val = self.builder.fptosi(end_val, self.i64_ty, name="for_end_cast")
            
        var_ptr = self.builder.alloca(self.i64_ty, name=node.var_name)
        self.symbol_table[node.var_name] = var_ptr
        self.var_types[node.var_name] = "int"
        
        self.builder.store(start_val, var_ptr)
        
        cond_bb = self.builder.append_basic_block(name="for.cond")
        body_bb = self.builder.append_basic_block(name="for.body")
        end_bb = self.builder.append_basic_block(name="for.end")
        
        self.builder.branch(cond_bb)
        
        self.builder.position_at_end(cond_bb)
        current_val = self.builder.load(var_ptr, name="for_curr")
        cond = self.builder.icmp_signed("<", current_val, end_val, name="for_cond")
        self.builder.cbranch(cond, body_bb, end_bb)
        
        self.builder.position_at_end(body_bb)
        for stmt in node.body:
            self.visit(stmt)
            
        # CORREÇÃO CRÍTICA: Se o corpo do loop não terminou com 'return' ou 'break', 
        # nós adicionamos a instrução para ir para a próxima iteração.
        if not self.builder.block.is_terminated:
            next_val = self.builder.add(current_val, ir.Constant(self.i64_ty, 1), name="for_next")
            self.builder.store(next_val, var_ptr)
            self.builder.branch(cond_bb)
            
        self.builder.position_at_end(end_bb)

    def visit_MatchStmt(self, node):
        # Lowering básico de match statement (switch em inteiros)
        cond_val = self.visit(node.condition)
        if cond_val.type == self.i64_ty:
            end_bb = self.builder.append_basic_block(name="match.end")
            default_bb = self.builder.append_basic_block(name="match.default")
            sw = self.builder.switch(cond_val, default_bb)
            
            for val_node, var_name, body in node.cases:
                case_bb = self.builder.append_basic_block(name="match.case")
                val = self.visit(val_node)
                sw.add_case(val, case_bb)
                self.builder.position_at_end(case_bb)
                
                if var_name:
                    var_ptr = self.builder.alloca(self.i64_ty, name=var_name)
                    self.symbol_table[var_name] = var_ptr
                    
                for stmt in body:
                    self.visit(stmt)
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    
            self.builder.position_at_end(default_bb)
            if node.default:
                for stmt in node.default:
                    self.visit(stmt)
            if not self.builder.block.is_terminated:
                self.builder.branch(end_bb)
                
            self.builder.position_at_end(end_bb)

    def visit_DeferStmt(self, node):
        for stmt in node.body: self.visit(stmt)

    def visit_AssertStmt(self, node):
        self.visit(node.condition)

    def visit_BenchStmt(self, node):
        for stmt in node.body: self.visit(stmt)

    def visit_DestructureStmt(self, node):
        val = self.visit(node.value)
        if isinstance(val.type, ir.PointerType) and isinstance(val.type.pointee, ir.IdentifiedStructType):
            for i, name in enumerate(node.names):
                elem_ptr = self.builder.gep(val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)])
                field_val = self.builder.load(elem_ptr, name=name)
                var_ptr = self.builder.alloca(field_val.type, name=name)
                self.builder.store(field_val, var_ptr)
                self.symbol_table[name] = var_ptr

    # Stubs para não quebrar o codegen
    def visit_BreakStmt(self, node): pass
    def visit_ContinueStmt(self, node): pass

    def generic_visit(self, node):
        # Se não for um statement, tenta avaliar como expressão
        self.visit(node)