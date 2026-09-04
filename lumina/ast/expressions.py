from dataclasses import dataclass
from typing import List

@dataclass
class NumberExpr:
    value: str
    is_float: bool = False

@dataclass
class BoolExpr:
    value: bool

@dataclass
class StringExpr:
    value: str

@dataclass
class VariableExpr:
    name: str
    line: int = 0
    col: int = 0

@dataclass
class BinaryExpr:
    op: str
    left: any
    right: any

@dataclass
class CallExpr:
    name: str
    args: List[any]
    is_method: bool = False

@dataclass
class ArrayExpr:
    elements: List[any]

@dataclass
class IndexExpr:
    array: any
    index: any

@dataclass
class MemberExpr:
    obj: any
    member: str

@dataclass
class AddressOfExpr:
    val: any

@dataclass
class DerefExpr:
    val: any

@dataclass
class TupleExpr:
    elements: List[any]

@dataclass
class UnaryExpr:
    op: str
    val: any