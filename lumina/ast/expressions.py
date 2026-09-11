# expressions.py
from dataclasses import dataclass, field
from typing import List, Union, Any, Optional

# ==========================================
# CLASSE BASE PARA O PADRÃO VISITOR
# ==========================================
class Expr:
    """Classe base para todas as expressões."""
    def accept(self, visitor):
        return visitor.visit(self)

# ==========================================
# TIPOS AUXILIARES (Para evitar List[tuple] solto)
# ==========================================
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
    pattern: Any  # Pode ser NumberExpr, VariableExpr, etc.
    body: Any     # Expr ou Stmt
    guard: Optional[Expr] = None # Ex: match x { 1 if x > 0 => ... }


# ==========================================
# LITERAIS E VARIÁVEIS
# ==========================================
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
    """Para strings interpoladas tipo f"Olá {nome}" """
    parts: List[Union[StringExpr, Expr]]

@dataclass
class ArrayExpr(Expr):
    elements: List[Expr]

@dataclass
class MapLiteralExpr(Expr):
    """Literal para dicionários/hash maps: {"chave": valor}"""
    pairs: List[tuple] # (Expr_key, Expr_value)

@dataclass
class TupleExpr(Expr):
    elements: List[Expr]

@dataclass
class VariableExpr(Expr):
    name: str
    line: int = 0
    col: int = 0


# ==========================================
# OPERAÇÕES E CHAMADAS
# ==========================================
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
    callee: Expr  # Pode ser um VariableExpr, MemberExpr, etc.
    args: List[Expr]
    is_method: bool = False

@dataclass
class IndexExpr(Expr):
    obj: Expr
    index: Expr

@dataclass
class MemberExpr(Expr):
    obj: Expr
    member: str
    is_safe: bool = False # Para o operador ?.


# ==========================================
# CONTROLE DE FLUXO COMO EXPRESSÃO
# ==========================================
@dataclass
class BlockExpr(Expr):
    """Um bloco de código que retorna um valor: { stmt1; stmt2; expr_final }"""
    statements: List[Any] # Lista de Stmt
    final_expr: Optional[Expr] = None

@dataclass
class IfExpr(Expr):
    """Um 'if' que retorna um valor (ex: let x = if cond { 1 } else { 2 })"""
    condition: Expr
    then_branch: BlockExpr
    else_branch: Optional[BlockExpr] = None

@dataclass
class MatchExpr(Expr):
    condition: Expr
    cases: List[MatchCase]
    default: Optional[Expr] = None


# ==========================================
# ESTRUTURAS DE DADOS E ORIENTAÇÃO A OBJETOS
# ==========================================
@dataclass
class StructLiteralExpr(Expr):
    struct_name: str
    fields: List[tuple] # (nome_do_campo, Expr)

@dataclass
class LambdaExpr(Expr):
    params: List[Param]
    return_type: str
    body: List[Any] # Lista de Stmts ou um BlockExpr


# ==========================================
# SISTEMA DE TIPOS E METAPROGRAMAÇÃO
# ==========================================
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
    """Operador ? para propagação de erros"""
    val: Expr

@dataclass
class ComptimeExpr(Expr):
    """Metaprogramação executada em tempo de compilação"""
    expr: Expr