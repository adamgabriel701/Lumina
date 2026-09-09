from llvmlite import ir
from ..ast import VarDecl, AssignStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt, MemberExpr, ArrayExpr, MatchStmt, DerefExpr, IndexExpr, VariableExpr, CallExpr, ContinueStmt, DeferStmt, BreakStmt, AssertStmt, BenchStmt, NumberExpr, BinaryExpr
from .control_flow import ControlFlowCodegen

class StatementCodegen(ControlFlowCodegen):
    def codegen_stmt(self, node):
        if isinstance(node, VarDecl):
            # NOVO: Resolve o tipo real da variável (suporta Monomorphization Box<int>)
            var_ty = self.get_llvm_type(node.var_type) if node.var_type else None
            
            # Se for uma Struct (normal ou monomorfizada)
            if var_ty and isinstance(var_ty, ir.IdentifiedStructType):
                ptr = self.builder.alloca(var_ty, name=node.name)
                self.symbol_table[node.name] = ptr
                self.var_types[node.name] = var_ty
                if node.value:
                    val = self.codegen_expr(node.value)
                    self.builder.store(val, ptr)
                    
            # Se for um Array estático [1, 2, 3]
            elif isinstance(node.value, ArrayExpr):
                num_elements = len(node.value.elements)
                arr_ty = ir.ArrayType(self.i64_ty, num_elements)
                ptr = self.builder.alloca(arr_ty, name=node.name)
                self.var_types[node.name] = arr_ty
                self.symbol_table[node.name] = ptr
                self.array_sizes[node.name] = num_elements
                for i, el in enumerate(node.value.elements):
                    el_val = self.codegen_expr(el)
                    # NOVO: Lida com Floats e Ponteiros ao inicializar arrays
                    if el_val.type == self.f64_ty:
                        el_val = self.builder.fptosi(el_val, self.i64_ty, name="to_int")
                    elif isinstance(el_val.type, ir.PointerType):
                        el_val = self.builder.ptrtoint(el_val, self.i64_ty, name="ptr_to_int")
                    elem_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)])
                    self.builder.store(el_val, elem_ptr)
                    
            # Tipos primitivos e Ponteiros
            else:
                val = self.codegen_expr(node.value) if node.value else ir.Constant(self.i64_ty, 0)
                actual_ty = val.type
                
                # Se o tipo foi explicitado (ex: mut curr: ptr), usa o tipo declarado
                if node.var_type is not None:
                    actual_ty = self.get_llvm_type(node.var_type)
                    
                # Conversões de tipo (Casting)
                if val.type == self.i64_ty and isinstance(actual_ty, ir.PointerType):
                    val = self.builder.inttoptr(val, actual_ty, name="int_to_ptr")
                elif val.type == self.f64_ty and actual_ty == self.i64_ty:
                    val = self.builder.fptosi(val, self.i64_ty, name="float_to_int")
                elif val.type == self.i64_ty and actual_ty == self.f64_ty:
                    val = self.to_float_if_needed(val)
                    
                ptr = self.builder.alloca(actual_ty, name=node.name)
                self.builder.store(val, ptr)
                self.symbol_table[node.name] = ptr
                self.var_types[node.name] = actual_ty
                
                # Escape Analysis e Auto-Free
                if isinstance(node.value, CallExpr) and node.value.name == "alloc":
                    if node.name not in self.escapes:
                        size_val = self.codegen_expr(node.value.args[0])
                        stack_ptr = self.builder.alloca(self.i64_ty, size=size_val, name=node.name + "_stack")
                        self.symbol_table[node.name] = stack_ptr
                        self.var_types[node.name] = self.i64_ty.as_pointer()
                        self.heap_int_arrays.add(node.name)
                    else:
                        self.cleanup_vars[-1].add(node.name)
                        self.heap_int_arrays.add(node.name)

        elif isinstance(node, AssignStmt):
            if isinstance(node.target, DerefExpr):
                ptr = self.codegen_expr(node.target.val)
                if ptr.type == self.voidptr_ty:
                    ptr = self.builder.bitcast(ptr, self.i64_ty.as_pointer(), name="ptr_cast")
                val = self.codegen_expr(node.value)
                self.builder.store(val, ptr)
            elif isinstance(node.target, IndexExpr):
                if isinstance(node.target.array, VariableExpr) and node.target.array.name in self.array_sizes:
                    arr_ptr = self.symbol_table.get(node.target.array.name)
                    idx_val = self.codegen_expr(node.target.index)
                    if idx_val.type != self.i64_ty: idx_val = self.builder.fptosi(idx_val, self.i64_ty, name="idx_int")
                    elem_ptr = self.builder.gep(arr_ptr, [ir.Constant(self.i32_ty, 0), idx_val], name="assign_elem_ptr")
                    val = self.codegen_expr(node.value)
                    self.builder.store(val, elem_ptr)
                else:
                    ptr = self.codegen_expr(node.target.array)
                    idx_val = self.codegen_expr(node.target.index)
                    if idx_val.type != self.i64_ty: idx_val = self.builder.fptosi(idx_val, self.i64_ty, name="idx_int")
                    val = self.codegen_expr(node.value)
                    if isinstance(ptr.type, ir.PointerType) and ptr.type.pointee == self.i64_ty:
                        elem_ptr = self.builder.gep(ptr, [idx_val], name="heap_assign_ptr")
                        # NOVO: Se estiver salvando um ponteiro num array de inteiros, converte para int
                        if isinstance(val.type, ir.PointerType):
                            val = self.builder.ptrtoint(val, self.i64_ty, name="ptr_to_int")
                        self.builder.store(val, elem_ptr)
                    elif ptr.type == self.voidptr_ty:
                        if val.type == self.i64_ty:
                            val = self.builder.trunc(val, self.i8_ty, name="byte_trunc")
                        elem_ptr = self.builder.gep(ptr, [idx_val], name="heap_assign_ptr")
                        self.builder.store(val, elem_ptr)
                    else:
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
                
                # NOVO: Conversões de tipo (Casting) na reatribuição
                if val.type == self.i64_ty and isinstance(var_ty, ir.PointerType):
                    # Se leu um i64 do array, mas a variável é um ptr, converte int -> ptr
                    val = self.builder.inttoptr(val, var_ty, name="assign_int_to_ptr")
                elif val.type == self.f64_ty and var_ty == self.i64_ty:
                    val = self.builder.fptosi(val, self.i64_ty, name="assign_float_to_int")
                elif val.type == self.i64_ty and var_ty == self.f64_ty:
                    val = self.to_float_if_needed(val)
                    
                self.builder.store(val, ptr)
                if isinstance(node.value, CallExpr) and node.value.name == "alloc":
                    self.heap_int_arrays.add(node.target.name)

        elif isinstance(node, ReturnStmt):
            for body in reversed(self.deferred_stmts):
                for stmt in body: self.codegen_stmt(stmt)
            self.deferred_stmts.clear()
            
            # NOVO: Se a função for void e for um 'return' vazio, usa ret_void()!
            if hasattr(self, 'current_ret_ty') and self.current_ret_ty == ir.VoidType():
                # Verifica se é o NumberExpr("0") que o Parser cria para returns vazios
                if len(node.values) == 1 and isinstance(node.values[0], NumberExpr) and node.values[0].value == "0":
                    for scope in self.cleanup_vars:
                        self.cleanup_block(scope)
                    self.builder.ret_void()
                    return
                    
            self.is_tail_return = True
            val = self.codegen_expr(node.values[0])
            self.is_tail_return = False
            
            if hasattr(self, 'current_ret_ty') and isinstance(self.current_ret_ty, ir.PointerType) and val.type == self.i64_ty:
                val = ir.Constant(self.current_ret_ty, None)
                
            if isinstance(val.type, ir.PointerType) and isinstance(val.type.pointee, ir.IdentifiedStructType):
                val = self.builder.load(val, name="ret_val")
            for scope in self.cleanup_vars:
                self.cleanup_block(scope)
            self.builder.ret(val)

        elif isinstance(node, IfStmt): self.codegen_if(node)
        elif isinstance(node, WhileStmt): self.codegen_while(node)
        elif isinstance(node, ForStmt): self.codegen_for(node)
        elif isinstance(node, MatchStmt): self.codegen_match(node)
            
        elif isinstance(node, ContinueStmt):
            if self.continue_block:
                self.cleanup_block(self.cleanup_vars[-1])
                self.builder.branch(self.continue_block)
                
        elif isinstance(node, BreakStmt):
            if self.break_block:
                self.cleanup_block(self.cleanup_vars[-1])
                self.builder.branch(self.break_block)
                
        elif isinstance(node, DeferStmt):
            self.deferred_stmts.append(node.body)
            
        elif isinstance(node, AssertStmt):
            cond_val = self.codegen_expr(node.condition)
            if cond_val.type != ir.IntType(1):
                cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(self.i64_ty, 0), name="assert_cond")
                
            then_bb = self.builder.append_basic_block(name="assert.pass")
            fail_bb = self.builder.append_basic_block(name="assert.fail")
            end_bb = self.builder.append_basic_block(name="assert.end")
            
            self.builder.cbranch(cond_val, then_bb, fail_bb)
            
            self.builder.position_at_end(fail_bb)
            err_msg = self.create_global_string("Assertion Failed!\n")
            self.builder.call(self.printf, [err_msg])
            
            exit_fn = self.functions_table.get("exit")
            if not exit_fn:
                exit_ty = ir.FunctionType(ir.VoidType(), [ir.IntType(32)])
                exit_fn = (ir.Function(self.module, exit_ty, name="exit"), exit_ty)
                self.functions_table["exit"] = exit_fn
            self.builder.call(exit_fn[0], [ir.Constant(ir.IntType(32), 1)])
            self.builder.unreachable()
            
            self.builder.position_at_end(then_bb)
            self.builder.branch(end_bb)
            
            self.builder.position_at_end(end_bb)

        # NOVO: BenchStmt
        elif isinstance(node, BenchStmt):
            # Declara clock() do C (retorna clock_t, que é um long/int)
            clock_fn = self.functions_table.get("clock")
            if not clock_fn:
                clock_ty = ir.FunctionType(self.i64_ty, [])
                clock_fn = (ir.Function(self.module, clock_ty, name="clock"), clock_ty)
                self.functions_table["clock"] = clock_fn
            
            # Constante CLOCKS_PER_SEC (geralmente 1000000 no Linux)
            cps = ir.Constant(self.i64_ty, 1000000)
            
            # Pega o tempo inicial
            start_time = self.builder.call(clock_fn[0], [], name="bench_start")
            
            # Executa o corpo do benchmark (APENAS 1 VEZ)
            for stmt in node.body:
                self.codegen_stmt(stmt)
            
            # Pega o tempo final
            end_time = self.builder.call(clock_fn[0], [], name="bench_end")
            
            diff = self.builder.sub(end_time, start_time, name="bench_diff")
            
            # NOVO: Converte para float (f64) para obter precisão decimal
            diff_f = self.builder.sitofp(diff, self.f64_ty, name="bench_diff_f")
            
            # Divide por CLOCKS_PER_SEC (1.000.000) para obter segundos
            sec = self.builder.fdiv(diff_f, ir.Constant(self.f64_ty, 1000000.0), name="bench_sec")
            
            print_msg = self.create_global_string("Benchmark '" + node.name + "': ")
            self.builder.call(self.printf, [print_msg])
            
            # Imprime em segundos com casa decimal
            fmt_sec = self.create_global_string("%f segundos\n")
            self.builder.call(self.printf, [fmt_sec, sec])

        else:
            self.codegen_expr(node)