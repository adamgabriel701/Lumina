"""Análise semântica de statements.

O método `analyze_stmt` é o dispatcher de entrada — ele decide qual
mixin trata cada tipo de statement. É também o método sobrescrito por
`SemanticAnalyzer` para adicionar a checagem de exaustividade de match.

Mixins:
  - HelpersMixin     — _require_assignable, _require_bool, _find_enum_of_variant, _infer_binary_type
  - VarDeclMixin     — VarDecl, DestructureStmt, AssignStmt
  - ControlMixin     — IfStmt, WhileStmt, ForStmt
  - MatchStmtMixin   — MatchStmt (bindings + guards + escopo)
  - FlowMixin        — ReturnStmt, DeferStmt, AssertStmt, BenchStmt
"""
from ...ast import (
    VarDecl, DestructureStmt, AssignStmt, ReturnStmt, IfStmt, WhileStmt,
    ForStmt, MatchStmt, ContinueStmt, DeferStmt, BreakStmt, AssertStmt,
    BenchStmt, ErrorNode,
)

from .helpers import HelpersMixin
from .var_decl import VarDeclMixin
from .control import ControlMixin
from .match import MatchStmtMixin
from .flow import FlowMixin


class StatementAnalyzer(
    HelpersMixin,
    VarDeclMixin,
    ControlMixin,
    MatchStmtMixin,
    FlowMixin,
):
    """Dispatcher + mixins de análise de statements."""

    def analyze_stmt(self, node):
        if isinstance(node, ErrorNode):
            return

        if isinstance(node, VarDecl):
            return self._analyze_var_decl(node)

        if isinstance(node, DestructureStmt):
            return self._analyze_destructure(node)

        if isinstance(node, AssignStmt):
            return self._analyze_assign(node)

        if isinstance(node, ReturnStmt):
            return self._analyze_return(node)

        if isinstance(node, IfStmt):
            return self._analyze_if(node)

        if isinstance(node, WhileStmt):
            return self._analyze_while(node)

        if isinstance(node, ForStmt):
            return self._analyze_for(node)

        if isinstance(node, MatchStmt):
            return self._analyze_match_stmt(node)

        if isinstance(node, ContinueStmt):
            return

        if isinstance(node, BreakStmt):
            return

        if isinstance(node, DeferStmt):
            return self._analyze_defer(node)

        if isinstance(node, AssertStmt):
            return self._analyze_assert(node)

        if isinstance(node, BenchStmt):
            return self._analyze_bench(node)

        # Fallback: delega para o visitor (cobre IfExpr, MatchExpr,
        # literais como Expr-statement, etc.)
        return self.visit(node)
