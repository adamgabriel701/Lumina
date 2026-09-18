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
    variants: List[tuple]
    line: int = 0
    col: int = 0


@dataclass
class TraitDecl(Stmt):
    name: str
    methods: List[Any]
    line: int = 0
    col: int = 0


@dataclass
class ImplBlock(Stmt):
    struct_name: str
    methods: List[Any]
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
    type_params: Optional[List[str]] = None
    line: int = 0
    col: int = 0
    is_exported: bool = False
    attrs: Optional[List[str]] = None


@dataclass
class ExternDecl(Stmt):
    name: str
    params: List[tuple]
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


@dataclass
class MacroCallStmt(Stmt):
    """Invocação de macro em posição de statement.

    Sintaxe: `nome!(arg1, arg2, ...)`. Diferente de `nome(args)` (que
    é uma chamada de função/expressão), esta forma inlina o corpo
    inteiro da macro no call site, permitindo corpos multi-statement.

    A macro é resolvida em compile-time pelo codegen; a substituição
    de parâmetros é feita em `_substitute_in_stmt` e `_substitute_in_expr`.
    """
    name: str
    args: List[Expr]
    line: int = 0
    col: int = 0

@dataclass
class TypeAlias(Stmt):
    """`type Nome = <tipo>` — alias de tipo.

    O `target_type` pode ser um primitivo, nome de struct, `fn(...) -> R`,
    ou qualquer combinação (inclusive genéricos aninhados). A expansão
    acontece na passada 0 do semantic: os tipos usados no AST são
    reescritos antes da análise, então o resto do pipeline nunca vê
    aliases.
    """
    name: str
    target_type: str
    line: int = 0
    col: int = 0