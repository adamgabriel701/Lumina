from llvmlite import ir
from ..ast import IfStmt, WhileStmt, ForStmt, MatchStmt, ContinueStmt, BreakStmt

class ControlFlowCodegen:
    def codegen_if(self, node: IfStmt):
        cond_val = self.codegen_expr(node.condition)
        if cond_val.type != ir.IntType(1): cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(self.i64_ty, 0), name="if_cond")
        then_bb = self.builder.append_basic_block(name="if.then")
        else_bb = self.builder.append_basic_block(name="if.else") if node.else_body else None
        end_bb = self.builder.append_basic_block(name="if.end")
        if else_bb: self.builder.cbranch(cond_val, then_bb, else_bb)
        else: self.builder.cbranch(cond_val, then_bb, end_bb)
        
        self.builder.position_at_end(then_bb)
        self.cleanup_vars.append(set())
        for stmt in node.then_body: self.codegen_stmt(stmt)
        if not self.builder.block.is_terminated:
            self.cleanup_block(self.cleanup_vars.pop())
            self.builder.branch(end_bb)
        else:
            self.cleanup_vars.pop()
            
        if else_bb:
            self.builder.position_at_end(else_bb)
            self.cleanup_vars.append(set())
            for stmt in node.else_body: self.codegen_stmt(stmt)
            if not self.builder.block.is_terminated:
                self.cleanup_block(self.cleanup_vars.pop())
                self.builder.branch(end_bb)
            else:
                self.cleanup_vars.pop()
        self.builder.position_at_end(end_bb)

    def codegen_while(self, node: WhileStmt):
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
        old_break = self.break_block
        self.continue_block = cond_bb
        self.break_block = end_bb
        
        for stmt in node.body: self.codegen_stmt(stmt)
        self.continue_block = old_continue
        self.break_block = old_break
        
        if not self.builder.block.is_terminated:
            self.cleanup_block(self.cleanup_vars.pop())
            self.builder.branch(cond_bb)
        else:
            self.cleanup_vars.pop()
        self.builder.position_at_end(end_bb)

    def codegen_for(self, node: ForStmt):
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
        inc_bb = self.builder.append_basic_block(name="for.inc")
        end_bb = self.builder.append_basic_block(name="for.end")
        
        self.builder.branch(cond_bb)
        self.builder.position_at_end(cond_bb)
        curr_val = self.builder.load(ptr, name=node.var_name + "_val")
        cond = self.builder.icmp_signed("<", curr_val, end_val, name="for_cond")
        self.builder.cbranch(cond, body_bb, end_bb)
        
        self.builder.position_at_end(body_bb)
        self.cleanup_vars.append(set())
        old_continue = self.continue_block
        old_break = self.break_block
        self.continue_block = inc_bb
        self.break_block = end_bb
        
        for stmt in node.body: self.codegen_stmt(stmt)
        self.continue_block = old_continue
        self.break_block = old_break
        
        if not self.builder.block.is_terminated:
            self.cleanup_block(self.cleanup_vars.pop())
            self.builder.branch(inc_bb)
        else:
            self.cleanup_vars.pop()
            
        self.builder.position_at_end(inc_bb)
        next_val = self.builder.add(curr_val, ir.Constant(self.i64_ty, 1), name="for_next")
        self.builder.store(next_val, ptr)
        self.builder.branch(cond_bb)
        
        self.builder.position_at_end(end_bb)

    def codegen_match(self, node: MatchStmt):
        cond_val = self.codegen_expr(node.condition)
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
            if var_name:
                payload_ptr = self.builder.gep(cond_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)])
                payload_val = self.builder.load(payload_ptr, name=var_name + "_val")
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
            self.builder.branch(end_bb)
            
        self.builder.position_at_end(end_bb)
