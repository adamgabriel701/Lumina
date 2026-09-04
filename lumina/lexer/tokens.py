from enum import Enum, auto

class TokenType(Enum):
    NUMBER = auto()
    STRING = auto()
    IDENT = auto()
    KEYWORD = auto()
    OP = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()

class Token:
    def __init__(self, type, value, line=0, col=0):
        self.type = type
        self.value = value
        self.line = line
        self.col = col
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}')"