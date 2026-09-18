"""MatchStmt — análise de cases com bindings, guards e escopo."""
from ...ast import MatchStmt


class MatchStmtMixin:

    def _analyze_match_stmt(self, node):
        cond_type = self.visit(node.condition)

        for case in node.cases:
            variant_name, var_name, guard, body = case
            self.push_scope()

            if var_name:
                names = var_name if isinstance(var_name, list) else [var_name]
                if variant_name is None:
                    binding_type = cond_type or "int"
                else:
                    binding_type = "int"
                for name in names:
                    self.declare_var(name, binding_type, False)

            if guard:
                guard_type = self.visit(guard)
                self._require_bool(guard_type, context="Guard de 'case'")

            for stmt in body:
                self.analyze_stmt(stmt)

            self.pop_scope()

        if node.default:
            self.push_scope()
            for stmt in node.default:
                self.analyze_stmt(stmt)
            self.pop_scope()
