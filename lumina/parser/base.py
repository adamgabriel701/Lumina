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
        # Comentários acumulados e ainda não anexados a um nó.
        # O parser chama `_skip_comments()` antes de criar nós e
        # `_take_comments()` depois, anexando o resultado ao nó.
        self.pending_comments = []

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
        if t_type == TokenType.NEWLINE:
            self._skip_trailing_comment()
        # NOVO: comentários podem aparecer antes do INDENT (ex: primeira
        # linha de um bloco é um comentário). Skipa antes de checar.
        if t_type == TokenType.INDENT:
            self._skip_newlines_and_comments()
        if self.check(t_type, t_val):
            self.consume()
            return True
        return False

    def expect(self, t_type: TokenType, t_val: str = None):
        if t_type == TokenType.NEWLINE:
            self._skip_trailing_comment()
        # NOVO: idem acima.
        if t_type == TokenType.INDENT:
            self._skip_newlines_and_comments()
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

    # ------------------------------------------------------------------
    # Comentários
    # ------------------------------------------------------------------
    def _skip_trailing_comment(self):
        """Se o token atual é COMMENT e o próximo é NEWLINE,
        consome o COMMENT (guardando em pending_comments).

        Isso permite que comentários inline (`x = 1  # comment`) sejam
        capturados antes do NEWLINE que o parser espera.
        """
        if (self.current_token()
                and self.current_token().type == TokenType.COMMENT):
            next_t = self.peek(1)
            if next_t and next_t.type == TokenType.NEWLINE:
                self.pending_comments.append(self.current_token().value)
                self.consume()

    def _skip_comments(self):
        """Consome COMMENT tokens à frente, guardando os textos em
        `pending_comments`.
        """
        while self.current_token() and self.current_token().type == TokenType.COMMENT:
            self.pending_comments.append(self.current_token().value)
            self.consume()

    def _skip_newlines_and_comments(self):
        """Consome NEWLINE e COMMENT em qualquer ordem.

        Chamado no início de `parse_statement` e no topo de `parse()`.
        Comentários vão para `pending_comments`.
        """
        while self.current_token() and (
            self.check(TokenType.NEWLINE) or self.check(TokenType.COMMENT)
        ):
            if self.check(TokenType.COMMENT):
                self.pending_comments.append(self.current_token().value)
            self.consume()

    def _take_comments(self):
        """Retorna e limpa a lista de comentários pendentes."""
        result = list(self.pending_comments)
        self.pending_comments.clear()
        return result