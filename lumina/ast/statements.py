from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class VarDecl:
    name: str
    var_type: Optional[str]
    value: any
    is_mutable: bool = False
    line: int = 0
    col: int = 0

@dataclass
class AssignStmt:
    target: any
    value: any

@dataclass
class ReturnStmt:
    values: List[any]

@dataclass
class IfStmt:
    condition: any
    then_body: List[any]
    else_body: Optional[List[any]]

@dataclass
class WhileStmt:
    condition: any
    body: List[any]

@dataclass
class ForStmt:
    var_name: str
    start: any
    end: any
    body: List[any]
    iterable: any = None

@dataclass
class MatchStmt:
    condition: any
    cases: List[tuple]
    default: Optional[List[any]]

@dataclass
class StructDecl:
    name: str
    fields: Dict[str, str]
    type_params: Optional[List[str]] = None

@dataclass
class Function:
    name: str
    params: List[tuple]
    return_type: str
    body: List[any]
    type_params: Optional[List[str]] = None
    line: int = 0
    col: int = 0
    is_exported: bool = False # NOVO

@dataclass
class ImplBlock:
    struct_name: str
    methods: List[Function]
    trait_name: Optional[str] = None # NOVO

@dataclass
class ImportStmt:
    filename: str

@dataclass
class ExternDecl:
    name: str
    params: List[tuple]
    return_type: str
    is_wasm: bool = False # NOVO

@dataclass
class EnumDecl:
    name: str
    variants: List[tuple] 

@dataclass
class ContinueStmt:
    pass

@dataclass
class DeferStmt:
    body: List[any]

@dataclass
class BreakStmt:
    pass

@dataclass
class AssertStmt:
    condition: any

@dataclass
class BenchStmt:
    name: str
    body: List[any]

@dataclass
class TraitDecl:
    name: str
    methods: List[Function]

@dataclass
class DestructureStmt:
    names: List[str]
    value: any
    is_mutable: bool = False