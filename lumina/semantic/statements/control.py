"""IfStmt, WhileStmt, ForStmt — controle de fluxo com escopo de bloco."""
from ...ast import IfStmt, WhileStmt, ForStmt


class ControlMixin:

    def _analyze_if(self, node):
        cond_type = self.visit(node.condition)
        self._require_bool(cond_type, context="Condição de 'if'")

        self.push_scope()
        for stmt in node.then_body:
            self.analyze_stmt(stmt)
        self.pop_scope()

        if node.else_body:
            self.push_scope()
            for stmt in node.else_body:
                self.analyze_stmt(stmt)
            self.pop_scope()

    def _analyze_while(self, node):
        cond_type = self.visit(node.condition)
        self._require_bool(cond_type, context="Condição de 'while'")

        self.push_scope()
        for stmt in node.body:
            self.analyze_stmt(stmt)
        self.pop_scope()

    def _analyze_for(self, node):
        if node.iterable is not None:
            self.visit(node.iterable)
        else:
            self.visit(node.start)
            self.visit(node.end)

        self.push_scope()

        # FIX (P-10-5): usa `index_var` em vez de `"," in var_name`.
        if node.index_var is not None:
            self.declare_var(node.index_var, "int", False)
        self.declare_var(node.var_name, "int", False)

        for stmt in node.body:
            self.analyze_stmt(stmt)
        self.pop_scope()