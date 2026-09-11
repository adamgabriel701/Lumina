from enum import Enum, auto
from typing import Dict

class TokenType(Enum):
    # Literais e Identificadores
    NUMBER = auto()
    FLOAT = auto()
    STRING = auto()
    IDENT = auto()
    
    # Palavras-Chave (Keywords)
    LET = auto()
    CONST = auto()
    FN = auto()
    RETURN = auto()
    IF = auto()
    ELIF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    BREAK = auto()
    CONTINUE = auto()
    DEFER = auto()
    MATCH = auto()
    STRUCT = auto()
    IMPL = auto()
    TRAIT = auto()
    ENUM = auto()
    IMPORT = auto()
    EXTERN = auto()
    ASSERT = auto()
    BENCH = auto()
    COMPTIME = auto()
    TRUE = auto()
    FALSE = auto()
    NONE = auto()
    
    # Operadores Aritméticos e Lógicos
    PLUS = auto()        # +
    MINUS = auto()       # -
    STAR = auto()        # *
    SLASH = auto()       # /
    PERCENT = auto()     # %
    BANG = auto()        # !
    
    # Operadores Bitwise
    AMP = auto()         # &
    PIPE = auto()        # |
    CARET = auto()       # ^
    TILDE = auto()       # ~
    SHL = auto()         # <<
    SHR = auto()         # >>
    
    # Operadores de Atribuição
    ASSIGN = auto()      # =
    PLUS_ASSIGN = auto() # +=
    MINUS_ASSIGN = auto() # -=
    STAR_ASSIGN = auto() # *=
    SLASH_ASSIGN = auto() # /=
    
    # Operadores de Comparação
    EQ = auto()          # ==
    NEQ = auto()         # !=
    LT = auto()          # <
    GT = auto()          # >
    LTE = auto()         # <=
    GTE = auto()         # >=
    AND = auto()         # and
    OR = auto()          # or
    
    # Pontuação e Delimitadores
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    LBRACKET = auto()   # [
    RBRACKET = auto()   # ]
    COMMA = auto()      # ,
    DOT = auto()        # .
    COLON = auto()      # :
    DOUBLE_COLON = auto() # ::
    SEMICOLON = auto()  # ;
    ARROW = auto()      # ->
    FAT_ARROW = auto()  # =>
    QUESTION = auto()   # ?
    
    # Controle de Escopo Pythonico
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()

class Token:
    # __slots__ reduz o uso de memória (bom para compiladores que geram milhares de tokens)
    __slots__ = ('type', 'value', 'line', 'col', 'offset')

    def __init__(self, type: TokenType, value: str, line: int = 0, col: int = 0, offset: int = 0):
        self.type = type
        self.value = value
        self.line = line
        self.col = col
        self.offset = offset  # Posição absoluta no arquivo (excelente para LSP e erros precisos)

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', L:{self.line}, C:{self.col})"

# Mapeamento para o Lexer converter IDENT em KEYWORD automaticamente
KEYWORDS: Dict[str, TokenType] = {
    "let": TokenType.LET,
    "const": TokenType.CONST,
    "fn": TokenType.FN,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "elif": TokenType.ELIF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "defer": TokenType.DEFER,
    "match": TokenType.MATCH,
    "struct": TokenType.STRUCT,
    "impl": TokenType.IMPL,
    "trait": TokenType.TRAIT,
    "enum": TokenType.ENUM,
    "import": TokenType.IMPORT,
    "extern": TokenType.EXTERN,
    "assert": TokenType.ASSERT,
    "bench": TokenType.BENCH,
    "comptime": TokenType.COMPTIME,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "none": TokenType.NONE,
    "and": TokenType.AND,
    "or": TokenType.OR,
}