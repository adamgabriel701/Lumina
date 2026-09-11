from llvmlite import ir

from ..ast import (
    VarDecl, AssignStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt, 
    BreakStmt, ContinueStmt, MatchStmt, DeferStmt, AssertStmt, 
    BenchStmt, DestructureStmt, VariableExpr, AddressOfExpr,
    DerefExpr, TupleExpr, BinaryExpr, UnaryExpr, CallExpr,
    IndexExpr, MemberExpr
)

class StatementCodegen:
    
    def codegen_stmt(self, node):
        if isinstance(node, VarDecl):
            self.codegen_var_decl(node)
        elif isinstance(node, AssignStmt):
            self.codegen_assign(node)
        elif isinstance(node, ReturnStmt):
            self.codegen_return(node)
        elif isinstance(node, IfStmt):
            self.codegen_if(node)
        elif isinstance(node, WhileStmt):
            self.codegen_while(node)
        elif isinstance(node, ForStmt):
            self.codegen_for(node)
        elif isinstance(node, MatchStmt):
            self.codegen_match_stmt(node)
        elif isinstance(node, (BreakStmt, ContinueStmt)):
            pass # Requer conhecimento dos blocos atuais (BB stack)
        elif isinstance(node, DeferStmt):
            for stmt in node.body: self.codegen_stmt(stmt)
        elif isinstance(node, AssertStmt):
            self.codegen_expr(node.condition)
        elif isinstance(node, BenchStmt):
            for stmt in node.body: self.codegen_stmt(stmt)
        elif isinstance(node, DestructureStmt):
            self.codegen_destructure(node)
        else:
            # Se não for um Statement, tenta avaliar como Expressão
            self.codegen_expr(node)

    def codegen_var_decl(self, node):
        if node.var_type is None and node.value is not None:
            # Inferência básica de tipo a partir do valor
            val = self.codegen_expr(node.value)
            var_type = "int"
            if val.type == self.f64_ty: var_type = "float"
            elif val.type == self.voidptr_ty: var_type = "str"
        else:
            var_type = node.var_type
            val = self.codegen_expr(node.value) if node.value else None
            
        llvm_ty = self.get_llvm_type(var_type)
        ptr = self.builder.alloca(llvm_ty, name=node.name)
        self.symbol_table[node.name] = ptr
        self.var_types[node.name] = var_type
        
        if val is not None:
            # Auto-cast de int para float se necessário
            if llvm_ty == self.f64_ty and val.type == self.i64_ty:
                val = self.to_float_if_needed(val)
            self.builder.store(val, ptr)
            
        # Marca para o GC se for uma alocação
        if isinstance(node.value, CallExpr) and getattr(node.value.callee, 'name', None) == "alloc":
            self.heap_allocs.add(node.name)

    def codegen_assign(self, node):
        val = self.codegen_expr(node.value)
        
        if isinstance(node.target, VariableExpr):
            ptr = self.symbol_table.get(node.target.name)
            if ptr:
                if val.type == self.f64_ty and ptr.type.pointee == self.i64_ty:
                    val = self.builder.fptosi(val, self.i64_ty, name="float_to_int_assign")
                elif val.type == self.i64_ty and ptr.type.pointee == self.f64_ty:
                    val = self.builder.sitofp(val, self.f64_ty, name="int_to_float_assign")
                self.builder.store(val, ptr)
                
        elif isinstance(node.target, MemberExpr):
            obj_val = self.codegen_expr(node.target.obj)
            if isinstance(obj_val.type, ir.PointerType) and isinstance(obj_val.type.pointee, ir.IdentifiedStructType):
                struct_name = obj_val.type.pointee.name
                field_idx = self.struct_fields[struct_name].get(node.target.member)
                if field_idx is not None:
                    elem_ptr = self.builder.gep(obj_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, field_idx)])
                    self.builder.store(val, elem_ptr)
                    
        elif isinstance(node.target, IndexExpr):
            arr_val = self.codegen_expr(node.target.array)
            idx_val = self.codegen_expr(node.target.index)
            if isinstance(arr_val.type, ir.PointerType) and isinstance(arr_val.type.pointee, ir.ArrayType):
                elem_ptr = self.builder.gep(arr_val, [ir.Constant(self.i32_ty, 0), idx_val])
                self.builder.store(val, elem_ptr)

    def codegen_return(self, node):
        if not node.values:
            self.builder.ret_void()
            return
            
        val = self.codegen_expr(node.values[0])
        ret_ty = self.functions_table[self.current_func_name][1].return_type
        
        if val.type != ret_ty:
            if ret_ty == self.f64_ty and val.type == self.i64_ty:
                val = self.builder.sitofp(val, self.f64_ty, name="ret_cast")
            elif ret_ty == self.i64_ty and val.type == self.f64_ty:
                val = self.builder.fptosi(val, self.i64_ty, name="ret_cast")
                
        self.builder.ret(val)

    def codegen_if(self, node):
        cond_val = self.codegen_expr(node.condition)
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(cond_val.type, 0), name="if_cond")
            
        then_bb = self.builder.append_basic_block(name="if.then")
        else_bb = self.builder.append_basic_block(name="if.else")
        end_bb = self.builder.append_basic_block(name="if.end")
        
        self.builder.cbranch(cond_val, then_bb, else_bb)
        
        # Then block
        self.builder.position_at_end(then_bb)
        for stmt in node.then_body:
            self.codegen_stmt(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)
            
        # Else block
        self.builder.position_at_end(else_bb)
        if node.else_body:
            for stmt in node.else_body:
                self.codegen_stmt(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)
            
        self.builder.position_at_end(end_bb)

    def codegen_while(self, node):
        cond_bb = self.builder.append_basic_block(name="while.cond")
        body_bb = self.builder.append_basic_block(name="while.body")
        end_bb = self.builder.append_basic_block(name="while.end")
        
        self.builder.branch(cond_bb)
        
        # Condition block
        self.builder.position_at_end(cond_bb)
        cond_val = self.codegen_expr(node.condition)
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(cond_val.type, 0), name="while_cond")
        self.builder.cbranch(cond_val, body_bb, end_bb)
        
        # Body block
        self.builder.position_at_end(body_bb)
        for stmt in node.body:
            self.codegen_stmt(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_bb)
            
        self.builder.position_at_end(end_bb)

    def codegen_for(self, node):
        # Lowering simples para: for i in 0..10
        start_val = self.codegen_expr(node.start)
        end_val = self.codegen_expr(node.end)
        
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
            self.codegen_stmt(stmt)
            
        if not self.builder.block.is_terminated:
            next_val = self.builder.add(current_val, ir.Constant(self.i64_ty, 1), name="for_next")
            self.builder.store(next_val, var_ptr)
            self.builder.branch(cond_bb)
            
        self.builder.position_at_end(end_bb)

    def codegen_destructure(self, node):
        # Lida com: let (x, y) = point
        val = self.codegen_expr(node.value)
        if isinstance(val.type, ir.PointerType) and isinstance(val.type.pointee, ir.IdentifiedStructType):
            struct_name = val.type.pointee.name
            for i, name in enumerate(node.names):
                elem_ptr = self.builder.gep(val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)])
                field_val = self.builder.load(elem_ptr, name=name)
                var_ptr = self.builder.alloca(field_val.type, name=name)
                self.builder.store(field_val, var_ptr)
                self.symbol_table[name] = var_ptr

    def codegen_match_stmt(self, node):
        # Lowering básico para switch statement em inteiros
        cond_val = self.codegen_expr(node.condition)
        if cond_val.type == self.i64_ty:
            end_bb = self.builder.append_basic_block(name="match.end")
            default_bb = self.builder.append_basic_block(name="match.default")
            sw = self.builder.switch(cond_val, default_bb)
            
            for val_node, var_name, body in node.cases:
                case_bb = self.builder.append_basic_block(name="match.case")
                val = self.codegen_expr(val_node)
                sw.add_case(val, case_bb)
                self.builder.position_at_end(case_bb)
                
                if var_name:
                    var_ptr = self.builder.alloca(self.i64_ty, name=var_name)
                    self.symbol_table[var_name] = var_ptr
                    
                for stmt in body:
                    self.codegen_stmt(stmt)
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    
            self.builder.position_at_end(default_bb)
            if node.default:
                for stmt in node.default:
                    self.codegen_stmt(stmt)
            if not self.builder.block.is_terminated:
                self.builder.branch(end_bb)
                
            self.builder.position_at_end(end_bb)