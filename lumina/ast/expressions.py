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
    # Mistura de StringExpr (literais) e Expr (interpolações).
    # O parser de $"..." produz essa estrutura.
    parts: List[Expr]


@dataclass
class ArrayExpr(Expr):
    # No semantic, `let x = [...]` infere var_type = "ptr"
    elements: List[Expr]


@dataclass
class MapPair:
    key: Expr
    value: Expr


@dataclass
class MapLiteralExpr(Expr):
    pairs: List[MapPair]


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
class SliceExpr(Expr):
    """`arr[start..end]` com bounds opcionais.

    Campos:
      - array: expressão que produz o array/string
      - start: Optional[Expr] — None significa "do início"
      - end:   Optional[Expr] — None significa "até o fim"

    Substitui `IndexExpr(array, BinaryExpr('..', start, end))`.
    Destrava `arr[..]`, `arr[a..]`, `arr[..b]`.
    """
    array: Expr
    start: Optional[Expr] = None
    end: Optional[Expr] = None


@dataclass
class MemberExpr(Expr):
    obj: Expr
    member: str
    # Se True, é navegação segura (`?.`) — codegen faz null check
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
    # 2-tuple: (pattern, result). Diferente do MatchStmt que usa 4-tuple.
    cases: List[MatchCase]
    default: Optional[Expr] = None


@dataclass
class StructLiteralField:
    name: str
    value: Expr


@dataclass
class StructLiteralExpr(Expr):
    struct_name: str
    fields: List[StructLiteralField]


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
    # Semantic infere var_type = "ptr" pra `let p = &x`
    val: Expr


@dataclass
class DerefExpr(Expr):
    val: Expr


@dataclass
class PropagateExpr(Expr):
    # `expr?` — unwrap de Result. Payload sempre tratado como i64 por enquanto.
    val: Expr


@dataclass
class NoneExpr(Expr):
    """Literal `none` — variante None de Option<T>.

    Substitui o antigo `NumberExpr('0')` que o parser emitia.
    No semantic, tem tipo "Option" (sem args) para permitir
    `let x: Option<int> = none`.

    No codegen, constrói Option::None (tag=1, payload=0) se o
    enum Option estiver declarado (vem do prelude).
    """
    pass


@dataclass
class ComptimeExpr(Expr):
    expr: Expr
    folded: Optional[Expr] = None   # preenchido pelo semantic