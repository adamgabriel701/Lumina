from ..lexer.tokens import TokenType
from .expressions import ExpressionParser
from .statements import StatementParser
from ..ast import StructDecl, ImplBlock, ImportStmt, ExternDecl, EnumDecl, TraitDecl, VarDecl, Function
from ..errors import LuminaError

class Parser(ExpressionParser, StatementParser):
    def __init__(self, tokens, filename="program.lm", source_code=""):
        self.tokens = tokens
        self.pos = 0
        self.filename = filename
        self.source_code = source_code
        self.no_struct_literal = False

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def peek(self, offset=1):
        if self.pos + offset < len(self.tokens): return self.tokens[self.pos + offset]
        return None

    def consume(self, expected_type=None):
        token = self.current_token()
        if token and (expected_type is None or token.type == expected_type):
            self.pos += 1
            return token
        if token:
            raise LuminaError(
                f"Esperado {expected_type}, mas encontrei {token.type} ('{token.value}')", 
                filename=self.filename, line=token.line, col=token.col, code=self.source_code
            )
        raise LuminaError("Fim inesperado do código", filename=self.filename, line=0, col=0, code=self.source_code)

    def parse(self):
        declarations = []
        while self.current_token() and not self.check(TokenType.EOF):
            if self.check(TokenType.KEYWORD, 'fn') or self.check(TokenType.KEYWORD, 'export'):
                declarations.append(self.parse_function())
            elif self.check(TokenType.KEYWORD, 'struct'):
                declarations.append(self.parse_struct())
            elif self.check(TokenType.KEYWORD, 'enum'):
                declarations.append(self.parse_enum())
            elif self.check(TokenType.KEYWORD, 'impl'):
                declarations.append(self.parse_impl())
            elif self.check(TokenType.KEYWORD, 'trait'):
                declarations.append(self.parse_trait())
            elif self.check(TokenType.KEYWORD, 'let') or self.check(TokenType.KEYWORD, 'mut') or \
                 self.check(TokenType.KEYWORD, 'test') or self.check(TokenType.KEYWORD, 'bench') or \
                 self.check(TokenType.KEYWORD, 'import') or self.check(TokenType.KEYWORD, 'extern'):
                declarations.append(self.parse_statement())
            else:
                # CORREÇÃO: Antes o parser engolia tokens inválidos silenciosamente.
                # Agora ele acusa o erro de sintaxe explicitamente.
                t = self.current_token()
                raise LuminaError(
                    f"Declaração de nível superior inválida: {t.type.name} ('{t.value}')", 
                    filename=self.filename, line=t.line, col=t.col, code=self.source_code
                )
                
        return declarations