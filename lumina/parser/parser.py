from .declarations import DeclarationParser
from ..lexer.tokens import TokenType
from ..errors import LuminaError


class Parser(DeclarationParser):
    """Orquestrador — combina todos os mixins via MRO.

    A cadeia de herança é:
      DeclarationParser → StatementParser → PatternParser → ExpressionParser → ParserBase

    Cada camada só depende da anterior (e é chamada de cima pra baixo), então
    não há dependência circular.
    """

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
                    filename=self.filename, line=t.line, col=t.col, source_code=self.source_code,
                )

            if is_export and hasattr(decl, 'is_exported'):
                decl.is_exported = True

            declarations.append(decl)

        return declarations