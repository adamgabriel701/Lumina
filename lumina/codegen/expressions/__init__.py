from llvmlite import ir
from ...ast.visitor import NodeVisitor

from .literals import LiteralsMixin
from .operators import OperatorsMixin
from .members import MembersMixin
from .calls import CallsMixin
from .aggregates import AggregatesMixin
from .match import MatchExprMixin


class ExpressionCodegen(
    LiteralsMixin,
    OperatorsMixin,
    MembersMixin,
    CallsMixin,
    AggregatesMixin,
    MatchExprMixin,
    NodeVisitor,
):
    """Combina todos os visitors de expressão via MRO."""

    def generic_visit(self, node):
        # Fallback silencioso: nós sem visit_X retornam 0 (i64).
        return ir.Constant(self.i64_ty, 0)