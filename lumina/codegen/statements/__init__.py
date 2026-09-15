from ...ast.visitor import NodeVisitor

from .var_decl import VarDeclMixin
from .control import ControlMixin
from .flow import FlowMixin
from .match import MatchStmtMixin


class StatementCodegen(
    VarDeclMixin,
    ControlMixin,
    FlowMixin,
    MatchStmtMixin,
    NodeVisitor,
):
    """Combina todos os visitors de statement via MRO."""
    pass