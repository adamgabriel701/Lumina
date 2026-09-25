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
    fields: Dict[str, str]
    type_params: Optional[List[str]] = None
    line: int = 0
    col: int = 0


@dataclass
class EnumDecl(Stmt):
    name: str
    variants: List[tuple]
    type_params: Optional[List[str]] = None
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


# FIX (Fase 10b / P-10-2): `x op= y` era desaçucarado para
# `x = x op y` no parser, o que avalia `x` DUAS vezes. Quando `x`
# é `arr[i]` e `i` tem efeitos colaterais (ex: `arr[f()]`), `f()`
# era chamada duas vezes — uma no target, outra dentro do value.
#
# Novo nó preserva a forma `op=` até o codegen, que resolve o
# endereço do lvalue UMA vez, carrega, computa e escreve de volta.
#
# Sintaxe coberta: `+=`, `-=`, `*=`, `/=`, `&=`, `|=`, `^=`.
@dataclass
class CompoundAssignStmt(Stmt):
    target: Expr
    op: str          # '+', '-', '*', '/', '&', '|', '^'
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


# FIX (Fase 10b / P-10-5): o parser codificava `for i, x in arr:`
# como `var_name = "i,x"` — uma string com vírgula. Funcionava por
# acaso, mas era frágil (`.split(",")` no codegen, `.strip()` para
# remover espaços, impossível de validar em compile-time).
#
# `index_var` é o novo campo: `for i, x in arr` → `var_name="x"`,
# `index_var="i"`. `for x in arr` → `var_name="x"`, `index_var=None`.
#
# É backwards-compatible para construções existentes (default=None).
@dataclass
class ForStmt(Stmt):
    var_name: str
    start: Optional[Expr]
    end: Optional[Expr]
    iterable: Optional[Expr]
    body: List[Any]
    index_var: Optional[str] = None   # NOVO


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
    message: str
    line: int = 0
    col: int = 0


@dataclass
class MacroCallStmt(Stmt):
    name: str
    args: List[Expr]
    line: int = 0
    col: int = 0


@dataclass
class TypeAlias(Stmt):
    name: str
    target_type: str
    type_params: Optional[List[str]] = None
    line: int = 0
    col: int = 0