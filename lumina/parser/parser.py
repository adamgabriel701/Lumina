from ..lexer.tokens import TokenType
from .mixins import LuminaParserMixin
from ..errors import LuminaError

class Parser(LuminaParserMixin):
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
                f"Esperado {expected_type.name if expected_type else 'token'}, mas encontrei {token.type.name} ('{token.value}')", 
                filename=self.filename, line=token.line, col=token.col, source_code=self.source_code
            )
        raise LuminaError("Fim inesperado do código", filename=self.filename, line=0, col=0, source_code=self.source_code)

    def parse(self):
        declarations = []
        while self.current_token() and not self.check(TokenType.EOF):
            if self.check(TokenType.NEWLINE):
                self.consume()
                continue
                
            is_export = False
            if self.check(TokenType.EXPORT):
                is_export = True
                self.consume()
                
            decl = None
            if self.check(TokenType.FN):
                decl = self.parse_function()
            elif self.check(TokenType.STRUCT):
                decl = self.parse_struct()
            elif self.check(TokenType.ENUM):
                decl = self.parse_enum()
            elif self.check(TokenType.IMPL):
                decl = self.parse_impl()
            elif self.check(TokenType.TRAIT):
                decl = self.parse_trait()
            elif self.check(TokenType.LET) or self.check(TokenType.MUT) or \
                 self.check(TokenType.CONST) or \
                 self.check(TokenType.TEST) or self.check(TokenType.BENCH) or \
                 self.check(TokenType.IMPORT) or self.check(TokenType.EXTERN):
                decl = self.parse_statement()
            else:
                t = self.current_token()
                raise LuminaError(
                    f"Declaração de nível superior inválida: {t.type.name} ('{t.value}')", 
                    filename=self.filename, line=t.line, col=t.col, source_code=self.source_code
                )
                
            if is_export and hasattr(decl, 'is_exported'):
                decl.is_exported = True
                
            declarations.append(decl)
                
        return declarations