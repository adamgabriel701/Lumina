from llvmlite import ir
from ...ast import BinaryExpr


class ControlMixin:

    def visit_IfStmt(self, node):
        cond_val = self.visit(node.condition)
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(cond_val.type, 0), name="if_cond")

        then_bb = self.builder.append_basic_block(name="if_then")
        else_bb = self.builder.append_basic_block(name="if_else")
        end_bb = self.builder.append_basic_block(name="if_end")

        self.builder.cbranch(cond_val, then_bb, else_bb)

        self.builder.position_at_end(then_bb)
        for stmt in node.then_body:
            self.visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)

        self.builder.position_at_end(else_bb)
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)

        self.builder.position_at_end(end_bb)

    def visit_WhileStmt(self, node):
        cond_bb = self.builder.append_basic_block(name="while_cond")
        body_bb = self.builder.append_basic_block(name="while_body")
        end_bb = self.builder.append_basic_block(name="while_end")

        self.builder.branch(cond_bb)

        self.builder.position_at_end(cond_bb)
        cond_val = self.visit(node.condition)
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(cond_val.type, 0), name="while_cond")
        self.builder.cbranch(cond_val, body_bb, end_bb)

        self.builder.position_at_end(body_bb)
        for stmt in node.body:
            self.visit(stmt)

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

        cond_bb = self.builder.append_basic_block(name="for_cond")
        body_bb = self.builder.append_basic_block(name="for_body")
        end_bb = self.builder.append_basic_block(name="for_end")

        self.builder.branch(cond_bb)

        self.builder.position_at_end(cond_bb)
        current_val = self.builder.load(var_ptr, name="for_curr")
        cond = self.builder.icmp_signed("<", current_val, end_val, name="for_cond")
        self.builder.cbranch(cond, body_bb, end_bb)

        self.builder.position_at_end(body_bb)
        for stmt in node.body:
            self.visit(stmt)

        if not self.builder.block.is_terminated:
            next_val = self.builder.add(current_val, ir.Constant(self.i64_ty, 1), name="for_next")
            self.builder.store(next_val, var_ptr)
            self.builder.branch(cond_bb)

        self.builder.position_at_end(end_bb)
