from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class VarDecl:
    name: str
    var_type: Optional[str]
    value: any
    is_mutable: bool = False

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

@dataclass
class MatchStmt:
    condition: any
    cases: List[tuple]
    default: Optional[List[any]]

@dataclass
class StructDecl:
    name: str
    fields: Dict[str, str]

@dataclass
class Function:
    name: str
    params: List[tuple]
    return_type: str
    body: List[any]

@dataclass
class ImplBlock:
    struct_name: str
    methods: List[Function]

@dataclass
class ImportStmt:
    filename: str

@dataclass
class ExternDecl:
    name: str
    params: List[tuple]
    return_type: str

@dataclass
class EnumDecl:
    name: str
    variants: List[tuple]