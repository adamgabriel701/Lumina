from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from .expressions import Expr, Param


class Stmt:
    """Classe base para todos os statements."""
    def accept(self, visitor):
        return visitor.visit(self)


# ==========================================
# DECLARAÇÕES DE ESTRUTURAS E TRAITS
# ==========================================
@dataclass
class StructDecl(Stmt):
    name: str
    fields: Dict[str, str]  # Nome do campo -> Tipo
    type_params: Optional[List[str]] = None
    line: int = 0
    col: int = 0


@dataclass
class EnumDecl(Stmt):
    name: str
    # variants: List[(nome, [tipos])]
    #   - [tipos] é lista de strings (type names)
    #   - [] (vazio)     → variante sem payload (ex: None, Zero)
    #   - [T]            → single-payload (ex: Some(T), Ok(T))
    #   - [T1, T2, ...]  → multi-payload (ex: Dois(int, int))
    variants: List[tuple]
    line: int = 0
    col: int = 0

@dataclass
class TraitDecl(Stmt):
    name: str
    methods: List[Any]  # Lista de Function
    line: int = 0
    col: int = 0


@dataclass
class ImplBlock(Stmt):
    struct_name: str
    methods: List[Any]  # Lista de Function
    trait_name: Optional[str] = None
    line: int = 0
    col: int = 0


# ==========================================
# DECLARAÇÕES DE VARIÁVEIS E FUNÇÕES
# ==========================================
@dataclass
class VarDecl(Stmt):
    name: str
    var_type: Optional[str]
    value: Optional[Expr]
    is_mutable: bool
    line: int = 0
    col: int = 0


@dataclass
class DestructureStmt(Stmt):
    names: List[str]
    value: Expr
    is_mutable: bool


@dataclass
class Function(Stmt):
    name: str
    params: List[Param]
    return_type: str
    body: List[Any]
    # Se type_params não é None, é uma função genérica — só é materializada
    # on-demand pelo codegen (monomorphization leve).
    type_params: Optional[List[str]] = None
    line: int = 0
    col: int = 0
    is_exported: bool = False
    attrs: Optional[List[str]] = None


@dataclass
class ExternDecl(Stmt):
    name: str
    params: List[tuple]  # (Nome, Tipo) — diferente de Function, é tuple mesmo
    return_type: str
    is_wasm: bool = False
    line: int = 0
    col: int = 0


@dataclass
class ImportStmt(Stmt):
    filename: str
    line: int = 0
    col: int = 0


# ==========================================
# CONTROLE DE FLUXO
# ==========================================
@dataclass
class AssignStmt(Stmt):
    target: Expr
    value: Expr


@dataclass
class ReturnStmt(Stmt):
    values: List[Expr]
    line: int = 0
    col: int = 0


@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_body: List[Any]
    else_body: Optional[List[Any]] = None


@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: List[Any]


@dataclass
class ForStmt(Stmt):
    var_name: str
    start: Optional[Expr]
    end: Optional[Expr]
    iterable: Optional[Expr]
    body: List[Any]


@dataclass
class MatchStmt(Stmt):
    condition: Expr
    # 4-tuple: (variant, binding, guard, body).
    # NÃO usar MatchCase aqui — o parser e o codegen dependem da tuple.
    # (MatchExpr em expressions.py usa MatchCase; MatchStmt não.)
    cases: List[tuple]
    default: Optional[List[Any]] = None


# ==========================================
# UTILITÁRIOS E TESTES
# ==========================================
@dataclass
class BreakStmt(Stmt):
    pass


@dataclass
class ContinueStmt(Stmt):
    pass


@dataclass
class DeferStmt(Stmt):
    body: List[Any]
    is_errdefer: bool = False


@dataclass
class AssertStmt(Stmt):
    condition: Expr


@dataclass
class BenchStmt(Stmt):
    name: str
    body: List[Any]


@dataclass
class ErrorNode(Stmt):
    """Nó especial para erros de parsing, permitindo o parser continuar"""
    message: str
    line: int = 0
    col: int = 0