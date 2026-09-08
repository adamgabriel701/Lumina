from llvmlite import ir
from ..ast import VarDecl, AssignStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt, MemberExpr, ArrayExpr, MatchStmt, DerefExpr, IndexExpr, VariableExpr, CallExpr, ContinueStmt, DeferStmt, BreakStmt, AssertStmt
from .control_flow import ControlFlowCodegen

class StatementCodegen(ControlFlowCodegen):
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
                if isinstance(node.value, CallExpr) and node.value.name == "alloc":
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
                if var_ty == self.f64_ty and val.type == self.i64_ty: val = self.to_float_if_needed(val)
                self.builder.store(val, ptr)
                if isinstance(node.value, CallExpr) and node.value.name == "alloc":
                    self.heap_int_arrays.add(node.target.name)

        elif isinstance(node, ReturnStmt):
            for body in reversed(self.deferred_stmts):
                for stmt in body: self.codegen_stmt(stmt)
            self.deferred_stmts.clear()
            
            val = self.codegen_expr(node.values[0])
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
            
        else:
            self.codegen_expr(node)