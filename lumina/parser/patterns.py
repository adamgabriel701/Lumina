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

            `X`, `X(v)`, `X(a, b)`, `1 | 2 | 3`, `_`, `n if cond`,
            `"literal"`, `1`, `"a" | "b"`

        Retorna `(variants, bindings, guard)`:
          - variants: `None` (wildcard/self-binding), `str`/`StringExpr`
            (single), ou `list` (multi-pattern via `|`)
          - bindings: None, [name] ou [name1, name2, ...]
          - guard: Expr ou None

        Multi-pattern com bindings é rejeitado: em `case A(x) | B(x):`
        os bindings seriam ambíguos (x tem sentido diferente em cada
        variante). Use cases separados nesse caso.
        """
        # Primeiro padrão
        variants = [self._parse_single_pattern()]

        # Alternativas via `|`
        while self.check(TokenType.PIPE):
            # Não consumir `|>` (pipe operator) como separador
            next_tok = self.peek(1)
            if next_tok and next_tok.type == TokenType.GT:
                break
            self.consume()  # PIPE
            variants.append(self._parse_single_pattern())

        # Se algum padrão tem binding, tratamos como single (não-multi)
        # — caso contrário, `case X(a, b):` seria interpretado como
        # multi-pattern com 1 elemento.
        bindings = None
        for i, v in enumerate(variants):
            if isinstance(v, tuple):
                variant_val, variant_binding = v
                variants[i] = variant_val
                if variant_binding is not None:
                    if bindings is not None or len(variants) > 1:
                        # Multi-pattern com bindings
                        t = self.current_token()
                        raise LuminaError(
                            "Multi-pattern com binding não é suportado "
                            "(ex: `case A(x) | B(x):`). Use cases separados.",
                            self.filename, t.line, t.col, self.source_code,
                        )
                    bindings = variant_binding

        # Heurística de self-binding: `case n if cond:` → n vira binding
        # (só quando há 1 variante e ela é um identificador não-numérico)
        if (len(variants) == 1
                and isinstance(variants[0], str)
                and variants[0] not in ("_",)):
            try:
                int(variants[0])
            except (ValueError, TypeError):
                if self.check(TokenType.IF) and bindings is None:
                    bindings = [variants[0]]
                    variants = [None]

        # Wildcard: `case _:` vira variant=None, binding=None
        if len(variants) == 1 and variants[0] == "_":
            variants = [None]

        # Guard
        guard = None
        if self.check(TokenType.IF):
            self.consume()
            guard = self.parse_expression()

        # Unwrap single; mantém lista em multi
        variant = variants[0] if len(variants) == 1 else variants
        return variant, bindings, guard

    def _parse_single_pattern(self):
        """Parse um único padrão (sem considerar `|`).

        Retorna `(variant, binding)`:
          - variant: str (nome ou número), StringExpr, ou None (wildcard)
          - binding: None, [names], ou lista de nomes
        """
        if self.check(TokenType.NUMBER):
            return self.consume().value, None

        if self.check(TokenType.STRING):
            return StringExpr(self.consume().value), None

        if self.check(TokenType.IDENT):
            name = self.expect(TokenType.IDENT).value
            if name == "_":
                return None, None
            if self.check(TokenType.LPAREN):
                self.consume()
                bindings = []
                while True:
                    bindings.append(self.expect(TokenType.IDENT).value)
                    if not self.match(TokenType.COMMA):
                        break
                self.expect(TokenType.RPAREN)
                return name, bindings
            return name, None

        t = self.current_token()
        raise LuminaError(
            f"Esperado NUMBER, STRING ou IDENT após 'case', mas encontrei "
            f"{t.type.name} ('{t.value}')",
            filename=self.filename, line=t.line, col=t.col,
            source_code=self.source_code,
        )

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
                    stmt = self.parse_statement()
                    if stmt is not None:
                        body.append(stmt)
                self.expect(TokenType.DEDENT)
                binding = bindings[0] if isinstance(bindings, list) and bindings else bindings
                # `variant` pode ser StringExpr (literal) — extrai o texto
                # para o VariableExpr que o MatchExpr usa.
                if isinstance(variant, StringExpr):
                    variant_name = variant.value
                else:
                    variant_name = variant or binding or "_"
                cases.append((
                    VariableExpr(variant_name, 0, 0),
                    body[0] if body else NumberExpr("0", False),
                ))
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
                        stmt = self.parse_statement()
                        if stmt is not None:
                            body.append(stmt)
                    self.expect(TokenType.DEDENT)
                else:
                    stmt = self.parse_statement()
                    body = [stmt] if stmt is not None else []

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
                        stmt = self.parse_statement()
                        if stmt is not None:
                            default.append(stmt)
                    self.expect(TokenType.DEDENT)
                else:
                    stmt = self.parse_statement()
                    default = [stmt] if stmt is not None else []
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
                        stmt = self.parse_statement()
                        if stmt is not None:
                            body.append(stmt)
                    self.expect(TokenType.DEDENT)
                else:
                    stmt = self.parse_statement()
                    body = [stmt] if stmt is not None else []

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
                        stmt = self.parse_statement()
                        if stmt is not None:
                            default.append(stmt)
                    self.expect(TokenType.DEDENT)
                else:
                    stmt = self.parse_statement()
                    default = [stmt] if stmt is not None else []
            else:
                t = self.current_token()
                raise LuminaError(
                    f"Esperado 'case' ou 'default' dentro de 'switch', mas encontrei {t.type.name} ('{t.value}')",
                    filename=self.filename, line=t.line, col=t.col, source_code=self.source_code,
                )

        self.expect(TokenType.DEDENT)
        return MatchStmt(cond, cases, default)