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
        # `for i, x in arr:` — declara ambos os nomes.
        if "," in node.var_name:
            idx_name, val_name = node.var_name.split(",", 1)
            self.declare_var(idx_name.strip(), "int", False)
            self.declare_var(val_name.strip(), "int", False)
        else:
            self.declare_var(node.var_name, "int", False)

        for stmt in node.body:
            self.analyze_stmt(stmt)
        self.pop_scope()
