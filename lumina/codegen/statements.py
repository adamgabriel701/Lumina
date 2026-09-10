from llvmlite import ir
from ..ast import VarDecl, AssignStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt, MatchStmt, MemberExpr, ArrayExpr, DerefExpr, IndexExpr, VariableExpr, CallExpr, ContinueStmt, DeferStmt, BreakStmt, AssertStmt, BenchStmt, DestructureStmt, NumberExpr
from .control_flow import ControlFlowCodegen

class StatementCodegen(ControlFlowCodegen):
    def codegen_stmt(self, node):
        # NOVO: Atualiza a linha de debug para o nó atual
        if hasattr(self, 'is_debug') and self.is_debug and hasattr(self, 'current_line'):
            loc = self.module.add_debug_info("DILocation", {
                "line": getattr(node, 'line', 0),
                "column": getattr(node, 'col', 1),
                "scope": self.builder.debug_metadata
            })
            self.builder.debug_loc = loc

        if isinstance(node, VarDecl): self.codegen_var_decl(node)
        elif isinstance(node, DestructureStmt): self.codegen_destructure(node)
        elif isinstance(node, AssignStmt): self.codegen_assign(node)
        elif isinstance(node, ReturnStmt): self.codegen_return(node)
        elif isinstance(node, IfStmt): self.codegen_if(node)
        elif isinstance(node, WhileStmt): self.codegen_while(node)
        elif isinstance(node, ForStmt): self.codegen_for(node)
        elif isinstance(node, MatchStmt): self.codegen_match(node)
        elif isinstance(node, ContinueStmt):
            if self.continue_block: self.cleanup_block(self.cleanup_vars[-1]); self.builder.branch(self.continue_block)
        elif isinstance(node, BreakStmt):
            if self.break_block: self.cleanup_block(self.cleanup_vars[-1]); self.builder.branch(self.break_block)
        elif isinstance(node, DeferStmt): self.deferred_stmts.append(node.body)
        elif isinstance(node, AssertStmt): self.codegen_assert(node)
        elif isinstance(node, BenchStmt): self.codegen_bench(node)
        else: self.codegen_expr(node)

    def codegen_var_decl(self, node):

        # NOVO: Verificação blindada de Structs pelo nome do tipo
        is_struct = False
        if node.var_type:
            base_type = node.var_type.split('<')[0]
            if base_type in self.struct_types or '<' in node.var_type:
                is_struct = True
                
        # 1. Se for uma Struct explícita (ex: mut sq: Square)
        if is_struct:
            var_ty = self.get_llvm_type(node.var_type)
            ptr = self.builder.alloca(var_ty, name=node.name)
            self.symbol_table[node.name] = ptr
            self.var_types[node.name] = var_ty
            # Só inicializa se houver um valor (ex: = Point { x: 10 })
            if node.value:
                val = self.codegen_expr(node.value)
                if isinstance(val.type, ir.PointerType) and isinstance(val.type.pointee, ir.IdentifiedStructType):
                    val = self.builder.load(val, name="struct_val")
                self.builder.store(val, ptr)
            return  # RETURN PRECOCE!
            
        # 2. Se for um Array estático (ex: let arr = [1, 2, 3])
        if isinstance(node.value, ArrayExpr):
            arr_ty = ir.ArrayType(self.i64_ty, len(node.value.elements))
            ptr = self.builder.alloca(arr_ty, name=node.name)
            self.var_types[node.name] = arr_ty
            self.symbol_table[node.name] = ptr
            self.array_sizes[node.name] = len(node.value.elements)
            for i, el in enumerate(node.value.elements):
                el_val = self.codegen_expr(el)
                if el_val.type == self.f64_ty: el_val = self.builder.fptosi(el_val, self.i64_ty, name="to_int")
                elif isinstance(el_val.type, ir.PointerType): el_val = self.builder.ptrtoint(el_val, self.i64_ty, name="ptr_to_int")
                self.builder.store(el_val, self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)]))
            return  # RETURN PRECOCE!
            
        # 3. Tipos primitivos e Ponteiros
        val = self.codegen_expr(node.value) if node.value else ir.Constant(self.i64_ty, 0)
        
        # NOVO: Se a função retornar void, não tenta alocar, retorna 0
        if val is None or isinstance(val.type, ir.VoidType):
            ptr = self.builder.alloca(self.i64_ty, name=node.name)
            self.builder.store(ir.Constant(self.i64_ty, 0), ptr)
            self.symbol_table[node.name] = ptr
            self.var_types[node.name] = self.i64_ty
            return
            
        # Se o valor já for um ponteiro para Struct (ex: retorno de função), usa o ponteiro direto
        if isinstance(val.type, ir.PointerType) and isinstance(val.type.pointee, ir.IdentifiedStructType):
            self.symbol_table[node.name] = val
            self.var_types[node.name] = val.type
            return  # RETURN PRECOCE!
            
        actual_ty = val.type
        if node.var_type is not None: actual_ty = self.get_llvm_type(node.var_type)
        
        if val.type == self.i64_ty and isinstance(actual_ty, ir.PointerType): val = self.builder.inttoptr(val, actual_ty, name="int_to_ptr")
        elif val.type == self.f64_ty and actual_ty == self.i64_ty: val = self.builder.fptosi(val, self.i64_ty, name="float_to_int")
        elif val.type == self.i64_ty and actual_ty == self.f64_ty: val = self.to_float_if_needed(val)
        
        ptr = self.builder.alloca(actual_ty, name=node.name)
        self.builder.store(val, ptr)
        self.symbol_table[node.name] = ptr
        self.var_types[node.name] = actual_ty
        
        if isinstance(node.value, CallExpr) and node.value.name == "alloc":
            if node.name not in self.escapes:
                stack_ptr = self.builder.alloca(self.i64_ty, size=self.codegen_expr(node.value.args[0]), name=node.name + "_stack")
                self.symbol_table[node.name] = stack_ptr
                self.var_types[node.name] = self.i64_ty.as_pointer()
                self.heap_int_arrays.add(node.name)
            else:
                self.cleanup_vars[-1].add(node.name)
                self.heap_int_arrays.add(node.name)

    def codegen_destructure(self, node):
        val = self.codegen_expr(node.value)
        if isinstance(val.type, ir.PointerType) and val.type.pointee == self.i64_ty:
            for i, name in enumerate(node.names):
                elem_val = self.builder.load(self.builder.gep(val, [ir.Constant(self.i64_ty, i)], name=f"destruct_{i}"), name=name + "_val")
                ptr = self.builder.alloca(self.i64_ty, name=name); self.builder.store(elem_val, ptr)
                self.symbol_table[name] = ptr; self.var_types[name] = self.i64_ty
        elif isinstance(val.type, ir.ArrayType):
            for i, name in enumerate(node.names):
                elem_val = self.builder.load(self.builder.gep(val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)], name=f"destruct_{i}"), name=name + "_val")
                ptr = self.builder.alloca(self.i64_ty, name=name); self.builder.store(elem_val, ptr)
                self.symbol_table[name] = ptr; self.var_types[name] = self.i64_ty

    def codegen_assign(self, node):
        if isinstance(node.target, DerefExpr):
            ptr = self.codegen_expr(node.target.val)
            if ptr.type == self.voidptr_ty: ptr = self.builder.bitcast(ptr, self.i64_ty.as_pointer(), name="ptr_cast")
            val = self.codegen_expr(node.value)
            if val.type == self.f64_ty: val = self.builder.fptosi(val, self.i64_ty, name="to_int")
            self.builder.store(val, ptr)
        elif isinstance(node.target, IndexExpr):
            if isinstance(node.target.array, VariableExpr) and node.target.array.name in self.array_sizes:
                arr_ptr = self.symbol_table.get(node.target.array.name); idx_val = self.codegen_expr(node.target.index)
                if idx_val.type == self.f64_ty: idx_val = self.builder.fptosi(idx_val, self.i64_ty, name="idx_int")
                elem_ptr = self.builder.gep(arr_ptr, [ir.Constant(self.i32_ty, 0), idx_val], name="assign_elem_ptr")
                val = self.codegen_expr(node.value)
                if val.type == self.f64_ty: val = self.builder.fptosi(val, self.i64_ty, name="to_int")
                # NOVO: Se for um ponteiro sendo armazenado em um array de inteiros (i64)
                elif isinstance(val.type, ir.PointerType) and arr_ptr.type.pointee == self.i64_ty: 
                    val = self.builder.ptrtoint(val, self.i64_ty, name="ptr_to_int_arr")
                self.builder.store(val, elem_ptr)
            else:
                ptr = self.codegen_expr(node.target.array); idx_val = self.codegen_expr(node.target.index)
                if idx_val.type == self.f64_ty: idx_val = self.builder.fptosi(idx_val, self.i64_ty, name="idx_int")
                elif isinstance(idx_val.type, ir.PointerType): idx_val = self.builder.ptrtoint(idx_val, self.i64_ty, name="ptr_to_int")
                val = self.codegen_expr(node.value)
                
                if isinstance(ptr.type, ir.PointerType) and ptr.type.pointee == self.i64_ty: 
                    elem_ptr = self.builder.gep(ptr, [idx_val], name="heap_assign_ptr")
                    # NOVO: Se for um ponteiro sendo armazenado em um array de inteiros (i64)
                    if isinstance(val.type, ir.PointerType):
                        val = self.builder.ptrtoint(val, self.i64_ty, name="ptr_to_int_heap")
                elif ptr.type == self.voidptr_ty:
                    if val.type == self.i64_ty: val = self.builder.trunc(val, self.i8_ty, name="byte_trunc")
                    elem_ptr = self.builder.gep(ptr, [idx_val], name="heap_assign_ptr")
                else: 
                    elem_ptr = self.builder.gep(ptr, [idx_val], name="heap_assign_ptr")
                self.builder.store(val, elem_ptr)
        elif isinstance(node.target, MemberExpr):
            obj_ptr = self.resolve_member_ptr(node.target); val = self.codegen_expr(node.value)
            if isinstance(val.type, ir.PointerType) and isinstance(obj_ptr.type.pointee, ir.PointerType): val = self.builder.bitcast(val, obj_ptr.type.pointee, name="ptr_cast")
            self.builder.store(val, obj_ptr)
        else:
            ptr = self.symbol_table.get(node.target.name)
            if not ptr: raise Exception(f"Variável '{node.target.name}' não declarada.")
            val = self.codegen_expr(node.value); var_ty = self.var_types[node.target.name]
            if val.type == self.i64_ty and isinstance(var_ty, ir.PointerType): val = self.builder.inttoptr(val, var_ty, name="assign_int_to_ptr")
            elif val.type == self.f64_ty and var_ty == self.i64_ty: val = self.builder.fptosi(val, self.i64_ty, name="assign_float_to_int")
            elif val.type == self.i64_ty and var_ty == self.f64_ty: val = self.to_float_if_needed(val)
            self.builder.store(val, ptr)

    def codegen_return(self, node):
        for body in reversed(self.deferred_stmts):
            for stmt in body: self.codegen_stmt(stmt)
        self.deferred_stmts.clear()
        if hasattr(self, 'current_ret_ty') and self.current_ret_ty == ir.VoidType():
            if len(node.values) == 1 and isinstance(node.values[0], NumberExpr) and node.values[0].value == "0":
                for scope in self.cleanup_vars: self.cleanup_block(scope)
                self.builder.ret_void(); return
        self.is_tail_return = True; val = self.codegen_expr(node.values[0]); self.is_tail_return = False
        
        if isinstance(val.type, ir.PointerType) and isinstance(val.type.pointee, ir.IdentifiedStructType): 
            val = self.builder.load(val, name="ret_val")
            
        if hasattr(self, 'current_ret_ty') and isinstance(self.current_ret_ty, ir.PointerType) and val.type == self.i64_ty: 
            val = ir.Constant(self.current_ret_ty, None)
            
        # NOVO: Se a função espera i32 (ex: WASM) mas o valor é i64, trunca para i32
        if hasattr(self, 'current_ret_ty') and isinstance(self.current_ret_ty, ir.IntType) and isinstance(val.type, ir.IntType):
            if val.type.width != self.current_ret_ty.width:
                val = self.builder.trunc(val, self.current_ret_ty, name="ret_trunc")
        elif hasattr(self, 'current_ret_ty') and isinstance(self.current_ret_ty, ir.IntType) and isinstance(val.type, ir.PointerType):
            val = self.builder.ptrtoint(val, self.current_ret_ty, name="ret_ptr_to_int")
            
        for scope in self.cleanup_vars: self.cleanup_block(scope)
        self.builder.ret(val)

    def codegen_assert(self, node):
        cond_val = self.codegen_expr(node.condition)
        if cond_val.type != ir.IntType(1): cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(self.i64_ty, 0), name="assert_cond")
        then_bb, fail_bb, end_bb = self.builder.append_basic_block(name="assert.pass"), self.builder.append_basic_block(name="assert.fail"), self.builder.append_basic_block(name="assert.end")
        self.builder.cbranch(cond_val, then_bb, fail_bb)
        
        # Se a condição for FALSA (assert falhou)
        self.builder.position_at_end(fail_bb)
        self.builder.call(self.printf, [self.create_global_string("Assertion Failed!\n")])
        
        # NOVO: Pega a função exit da tabela, ou cria e registra se não existir
        exit_func = None
        if "exit" in self.functions_table:
            exit_func = self.functions_table["exit"][0]
        else:
            exit_ty = ir.FunctionType(ir.VoidType(), [ir.IntType(32)])
            exit_func = ir.Function(self.module, exit_ty, name="exit")
            self.functions_table["exit"] = (exit_func, exit_ty)
            
        self.builder.call(exit_func, [ir.Constant(ir.IntType(32), 1)])
        self.builder.unreachable()
        
        # Se a condição for VERDADEIRA (assert passou)
        self.builder.position_at_end(then_bb)
        self.builder.branch(end_bb)
        self.builder.position_at_end(end_bb)

    def codegen_bench(self, node):
        clock_fn = self.functions_table.get("clock")
        if not clock_fn: clock_fn = (ir.Function(self.module, ir.FunctionType(self.i64_ty, []), name="clock"), None)
        start_time = self.builder.call(clock_fn[0], [], name="bench_start")
        for stmt in node.body: self.codegen_stmt(stmt)
        end_time = self.builder.call(clock_fn[0], [], name="bench_end")
        diff = self.builder.sub(end_time, start_time, name="bench_diff")
        diff_f = self.builder.sitofp(diff, self.f64_ty, name="bench_diff_f")
        sec = self.builder.fdiv(diff_f, ir.Constant(self.f64_ty, 1000000.0), name="bench_sec")
        self.builder.call(self.printf, [self.create_global_string("Benchmark '" + node.name + "': ")])
        self.builder.call(self.printf, [self.create_global_string("%f segundos\n"), sec])