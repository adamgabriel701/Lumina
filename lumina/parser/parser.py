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
                f"Esperado {expected_type}, mas encontrei {token.type} ('{token.value}')", 
                filename=self.filename, line=token.line, col=token.col, source_code=self.source_code
            )
        raise LuminaError("Fim inesperado do código", filename=self.filename, line=0, col=0, source_code=self.source_code)

    def parse(self):
        declarations = []
        while self.current_token() and not self.check(TokenType.EOF):
            if self.check(TokenType.NEWLINE):
                self.consume()
                continue
                
            if self.check(TokenType.FN) or self.check(TokenType.EXPORT):
                declarations.append(self.parse_function())
            elif self.check(TokenType.STRUCT):
                declarations.append(self.parse_struct())
            elif self.check(TokenType.ENUM):
                declarations.append(self.parse_enum())
            elif self.check(TokenType.IMPL):
                declarations.append(self.parse_impl())
            elif self.check(TokenType.TRAIT):
                declarations.append(self.parse_trait())
            elif self.check(TokenType.LET) or self.check(TokenType.MUT) or \
                 self.check(TokenType.TEST) or self.check(TokenType.BENCH) or \
                 self.check(TokenType.IMPORT) or self.check(TokenType.EXTERN):
                declarations.append(self.parse_statement())
            else:
                t = self.current_token()
                raise LuminaError(
                    f"Declaração de nível superior inválida: {t.type.name} ('{t.value}')", 
                    filename=self.filename, line=t.line, col=t.col, source_code=self.source_code
                )
                
        return declarations