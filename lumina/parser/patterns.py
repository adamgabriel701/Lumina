from .expressions import ExpressionParser
from ..lexer.tokens import TokenType
from ..ast import (
    MatchExpr, MatchStmt, VariableExpr, NumberExpr, StringExpr,
)
from ..errors import LuminaError


class PatternParser(ExpressionParser):
    """Match / switch — padrões, guards e exaustividade."""

    def _parse_case_pattern(self):
        """Lê o padrão de um `case`:
            `X`, `X(v)`, `X(a, b)`, `n if cond`, `"literal"`, `1`

        Retorna `(variant, bindings, guard)`:
          - variant: str (nome) ou None (self-binding)
          - bindings: None, [name] ou [name1, name2, ...]
          - guard: Expr ou None
        """
        variant = None
        bindings = None
        first_ident = None

        if self.check(TokenType.NUMBER):
            variant = self.consume().value
        elif self.check(TokenType.STRING):
            variant = self.consume().value
        elif self.check(TokenType.IDENT):
            first_ident = self.expect(TokenType.IDENT).value
            variant = first_ident
            if self.check(TokenType.LPAREN):
                self.consume()
                bindings = []
                while True:
                    bindings.append(self.expect(TokenType.IDENT).value)
                    if not self.match(TokenType.COMMA):
                        break
                self.expect(TokenType.RPAREN)
        else:
            t = self.current_token()
            raise LuminaError(
                f"Esperado NUMBER, STRING ou IDENT após 'case', mas encontrei {t.type.name} ('{t.value}')",
                filename=self.filename, line=t.line, col=t.col, source_code=self.source_code,
            )

        # Self-binding: `case n if n > 10:` → n é binding (não variante)
        if first_ident is not None and self.check(TokenType.IF) and bindings is None:
            bindings = [first_ident]
            variant = None

        guard = None
        if self.check(TokenType.IF):
            self.consume()
            guard = self.parse_expression()

        return variant, bindings, guard

    def parse_match_expr(self):
        self.consume(TokenType.MATCH)
        self.no_struct_literal = True
        cond = self.parse_expression()
        self.no_struct_literal = False

        if self.check(TokenType.COLON):
            self.consume()
            self.expect(TokenType.NEWLINE)
            while self.check(TokenType.NEWLINE):
                self.consume()
            self.expect(TokenType.INDENT)
        else:
            self.expect(TokenType.LBRACE)

        cases = []
        default = None
        while not self.check(TokenType.DEDENT) and not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                continue

            if self.check(TokenType.CASE):
                self.consume()
                variant, bindings, guard = self._parse_case_pattern()
                self.expect(TokenType.COLON)
                self.expect(TokenType.NEWLINE)
                while self.check(TokenType.NEWLINE):
                    self.consume()
                self.expect(TokenType.INDENT)
                body = []
                while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
                    if self.match(TokenType.NEWLINE):
                        continue
                    body.append(self.parse_statement())
                self.expect(TokenType.DEDENT)
                binding = bindings[0] if isinstance(bindings, list) and bindings else bindings
                cases.append((VariableExpr(variant or binding or "_", 0, 0), body[0] if body else NumberExpr("0", False)))
            elif self.check(TokenType.ELSE):
                self.consume()
                self.expect(TokenType.FAT_ARROW)
                default = self.parse_expression()
                self.match(TokenType.COMMA)
            else:
                val = self.parse_expression()
                self.expect(TokenType.FAT_ARROW)
                res = self.parse_expression()
                cases.append((val, res))
                self.match(TokenType.COMMA)

        if self.check(TokenType.DEDENT):
            self.consume(TokenType.DEDENT)
        elif self.check(TokenType.RBRACE):
            self.consume(TokenType.RBRACE)
        return MatchExpr(cond, cases, default)

    def parse_match_stmt(self):
        saved_pos = self.pos
        self.consume(TokenType.MATCH)
        self.no_struct_literal = True
        cond = self.parse_expression()
        self.no_struct_literal = False

        is_match_stmt_syntax = False
        if self.check(TokenType.COLON):
            self.consume()
            self.expect(TokenType.NEWLINE)
            while self.check(TokenType.NEWLINE):
                self.consume()
            if self.check(TokenType.INDENT):
                self.consume()
                if self.check(TokenType.CASE) or self.check(TokenType.DEFAULT):
                    is_match_stmt_syntax = True

        if is_match_stmt_syntax:
            return self._parse_match_stmt_cases(cond)

        self.pos = saved_pos
        return self.parse_match_expr()

    def _parse_match_expr_body(self, cond):
        self.expect(TokenType.LBRACE)
        cases = []
        default = None
        while not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
            if self.match(TokenType.NEWLINE) or self.match(TokenType.INDENT) or self.match(TokenType.DEDENT):
                continue
            if self.check(TokenType.ELSE):
                self.consume()
                self.expect(TokenType.FAT_ARROW)
                default = self.parse_expression()
                self.match(TokenType.COMMA)
            else:
                val = self.parse_expression()
                self.expect(TokenType.FAT_ARROW)
                res = self.parse_expression()
                cases.append((val, res))
                self.match(TokenType.COMMA)
        self.expect(TokenType.RBRACE)
        return MatchExpr(cond, cases, default)

    def _parse_match_stmt_cases(self, cond):
        cases = []
        default = None
        while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                continue

            if self.check(TokenType.CASE):
                self.consume()
                variant, bindings, guard = self._parse_case_pattern()
                self.expect(TokenType.COLON)

                if self.check(TokenType.NEWLINE):
                    self.expect(TokenType.NEWLINE)
                    while self.check(TokenType.NEWLINE):
                        self.consume()
                    self.expect(TokenType.INDENT)
                    body = []
                    while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
                        if self.match(TokenType.NEWLINE):
                            continue
                        body.append(self.parse_statement())
                    self.expect(TokenType.DEDENT)
                else:
                    body = [self.parse_statement()]

                cases.append((variant, bindings, guard, body))

            elif self.check(TokenType.DEFAULT):
                self.consume()
                self.expect(TokenType.COLON)

                if self.check(TokenType.NEWLINE):
                    self.expect(TokenType.NEWLINE)
                    while self.check(TokenType.NEWLINE):
                        self.consume()
                    self.expect(TokenType.INDENT)
                    default = []
                    while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
                        if self.match(TokenType.NEWLINE):
                            continue
                        default.append(self.parse_statement())
                    self.expect(TokenType.DEDENT)
                else:
                    default = [self.parse_statement()]
            else:
                t = self.current_token()
                raise LuminaError(
                    f"Esperado 'case' ou 'default' dentro de 'match', mas encontrei {t.type.name} ('{t.value}')",
                    filename=self.filename, line=t.line, col=t.col, source_code=self.source_code,
                )

        self.expect(TokenType.DEDENT)
        return MatchStmt(cond, cases, default)

    def parse_switch(self):
        self.consume(TokenType.SWITCH)
        self.no_struct_literal = True
        cond = self.parse_expression()
        self.no_struct_literal = False

        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        while self.check(TokenType.NEWLINE):
            self.consume()
        self.expect(TokenType.INDENT)

        cases = []
        default = None
        while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                continue

            if self.check(TokenType.CASE):
                self.consume()
                variant, bindings, guard = self._parse_case_pattern()
                self.expect(TokenType.COLON)

                if self.check(TokenType.NEWLINE):
                    self.expect(TokenType.NEWLINE)
                    while self.check(TokenType.NEWLINE):
                        self.consume()
                    self.expect(TokenType.INDENT)
                    body = []
                    while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
                        if self.match(TokenType.NEWLINE):
                            continue
                        body.append(self.parse_statement())
                    self.expect(TokenType.DEDENT)
                else:
                    body = [self.parse_statement()]

                cases.append((variant, bindings, guard, body))

            elif self.check(TokenType.DEFAULT):
                self.consume()
                self.expect(TokenType.COLON)

                if self.check(TokenType.NEWLINE):
                    self.expect(TokenType.NEWLINE)
                    while self.check(TokenType.NEWLINE):
                        self.consume()
                    self.expect(TokenType.INDENT)
                    default = []
                    while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
                        if self.match(TokenType.NEWLINE):
                            continue
                        default.append(self.parse_statement())
                    self.expect(TokenType.DEDENT)
                else:
                    default = [self.parse_statement()]
            else:
                t = self.current_token()
                raise LuminaError(
                    f"Esperado 'case' ou 'default' dentro de 'switch', mas encontrei {t.type.name} ('{t.value}')",
                    filename=self.filename, line=t.line, col=t.col, source_code=self.source_code,
                )

        self.expect(TokenType.DEDENT)
        return MatchStmt(cond, cases, default)
