from dataclasses import dataclass
from typing import List, Union, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .statements import Stmt

class Expr:
    """Classe base para todas as expressões."""
    def accept(self, visitor):
        return visitor.visit(self)

@dataclass
class Param:
    name: str
    type_ann: str
    default: Optional[Expr] = None

@dataclass
class StructField:
    name: str
    type_ann: str
    default: Optional[Expr] = None

@dataclass
class MatchCase:
    pattern: Any
    body: Union["Stmt", Expr]
    guard: Optional[Expr] = None

@dataclass
class NumberExpr(Expr):
    value: str
    is_float: bool = False

@dataclass
class BoolExpr(Expr):
    value: bool

@dataclass
class StringExpr(Expr):
    value: str

@dataclass
class InterpolatedStringExpr(Expr):
    parts: List[Expr]  # Simplificado

@dataclass
class ArrayExpr(Expr):
    elements: List[Expr]

@dataclass
class MapPair:
    key: Expr
    value: Expr

@dataclass
class MapLiteralExpr(Expr):
    pairs: List[MapPair]  # Removido tuple

@dataclass
class TupleExpr(Expr):
    elements: List[Expr]

@dataclass
class VariableExpr(Expr):
    name: str
    line: int = 0
    col: int = 0

@dataclass
class BinaryExpr(Expr):
    op: str
    left: Expr
    right: Expr

@dataclass
class UnaryExpr(Expr):
    op: str
    val: Expr

@dataclass
class CallExpr(Expr):
    callee: Expr
    args: List[Expr]
    is_method: bool = False

@dataclass
class IndexExpr(Expr):
    array: Expr
    index: Expr

@dataclass
class MemberExpr(Expr):
    obj: Expr
    member: str
    is_safe: bool = False

@dataclass
class BlockExpr(Expr):
    statements: List["Stmt"]
    final_expr: Optional[Expr] = None

@dataclass
class IfExpr(Expr):
    condition: Expr
    then_branch: BlockExpr
    else_branch: Optional[BlockExpr] = None

@dataclass
class MatchExpr(Expr):
    condition: Expr
    cases: List[MatchCase]
    default: Optional[Expr] = None

@dataclass
class StructLiteralField:
    name: str
    value: Expr

@dataclass
class StructLiteralExpr(Expr):
    struct_name: str
    fields: List[StructLiteralField]  # Removido tuple

@dataclass
class LambdaExpr(Expr):
    params: List[Param]
    return_type: str
    body: List[Any]

@dataclass
class CastExpr(Expr):
    expr: Expr
    target_type: str

@dataclass
class AddressOfExpr(Expr):
    val: Expr

@dataclass
class DerefExpr(Expr):
    val: Expr

@dataclass
class PropagateExpr(Expr):
    val: Expr

@dataclass
class ComptimeExpr(Expr):
    expr: Expr