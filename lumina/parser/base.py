from ..lexer.tokens import TokenType
from ..errors import LuminaError


class ParserBase:
    """Primitivas de consumo de tokens.

    Não sabe nada de gramática — apenas como ler e avançar em `self.tokens`.
    """

    def __init__(self, tokens, filename="program.lm", source_code=""):
        self.tokens = tokens
        self.pos = 0
        self.filename = filename
        self.source_code = source_code
        self.no_struct_literal = False

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def peek(self, offset=1):
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return None

    def consume(self, expected_type=None):
        token = self.current_token()
        if token and (expected_type is None or token.type == expected_type):
            self.pos += 1
            return token
        if token:
            raise LuminaError(
                f"Esperado {expected_type.name if expected_type else 'token'}, mas encontrei {token.type.name} ('{token.value}')",
                filename=self.filename, line=token.line, col=token.col, source_code=self.source_code,
            )
        raise LuminaError(
            "Fim inesperado do código",
            filename=self.filename, line=0, col=0, source_code=self.source_code,
        )

    def check(self, t_type: TokenType, t_val: str = None) -> bool:
        t = self.current_token()
        if not t:
            return False
        if t.type != t_type:
            return False
        if t_val is not None and t.value != t_val:
            return False
        return True

    def match(self, t_type: TokenType, t_val: str = None) -> bool:
        if self.check(t_type, t_val):
            self.consume()
            return True
        return False

    def expect(self, t_type: TokenType, t_val: str = None):
        if self.check(t_type, t_val):
            return self.consume()
        t = self.current_token()
        expected = f"{t_type.name}" + (f" ('{t_val}')" if t_val else "")
        found = f"{t.type.name} ('{t.value}')" if t else "EOF"
        raise LuminaError(
            f"Esperado {expected}, mas encontrei {found}",
            filename=self.filename, line=t.line if t else 0,
            col=t.col if t else 0, source_code=self.source_code,
        )
