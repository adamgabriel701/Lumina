from .expressions import ExpressionParser
from ..lexer.tokens import TokenType
from ..ast import (
    MatchExpr, MatchStmt, VariableExpr, NumberExpr, StringExpr,
    StructLiteralExpr, StructLiteralField,
)
from ..errors import LuminaError


class PatternParser(ExpressionParser):
    """Match / switch — padrões, guards e exaustividade."""

    # ==================================================================
    # Helpers compartilhados (usados por match expr, match stmt e switch)
    # ==================================================================
    def _parse_case_body(self):
        """Parseia o corpo de um `case`/`default`."""
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
            return body

        stmt = self.parse_statement()
        return [stmt] if stmt is not None else []

    def _parse_case_clause(self):
        """Parseia `case <pattern>:` seguido do corpo."""
        self.consume(TokenType.CASE)
        variant, bindings, guard = self._parse_case_pattern()
        self.expect(TokenType.COLON)
        body = self._parse_case_body()
        return (variant, bindings, guard, body)

    def _parse_default_clause(self):
        """Parseia `default:` seguido do corpo."""
        self.consume(TokenType.DEFAULT)
        self.expect(TokenType.COLON)
        return self._parse_case_body()

    def _parse_cases_block(self):
        """Parseia uma sequência de `case X:` / `default:` até DEDENT."""
        cases = []
        default = None
        while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                continue
            if self.check(TokenType.CASE):
                cases.append(self._parse_case_clause())
            elif self.check(TokenType.DEFAULT):
                default = self._parse_default_clause()
            else:
                t = self.current_token()
                raise LuminaError(
                    f"Esperado 'case' ou 'default' dentro de 'match', "
                    f"mas encontrei {t.type.name} ('{t.value}')",
                    filename=self.filename, line=t.line, col=t.col,
                    source_code=self.source_code,
                )
        self.expect(TokenType.DEDENT)
        return cases, default

    # ==================================================================
    # Case pattern parsing
    # ==================================================================
    def _parse_case_pattern(self):
        """Lê o padrão de um `case` e retorna `(variants, bindings, guard)`."""
        variants = [self._parse_single_pattern()]

        while self.check(TokenType.PIPE):
            next_tok = self.peek(1)
            if next_tok and next_tok.type == TokenType.GT:
                break
            self.consume()
            variants.append(self._parse_single_pattern())

        bindings = None
        for i, v in enumerate(variants):
            if isinstance(v, tuple):
                variant_val, variant_binding = v
                variants[i] = variant_val
                if variant_binding is not None:
                    if bindings is not None or len(variants) > 1:
                        t = self.current_token()
                        raise LuminaError(
                            "Multi-pattern com binding não é suportado. Use cases separados.",
                            self.filename, t.line, t.col, self.source_code,
                        )
                    bindings = variant_binding

        if (len(variants) == 1
                and isinstance(variants[0], str)
                and variants[0] not in ("_",)):
            try:
                int(variants[0])
            except (ValueError, TypeError):
                if self.check(TokenType.IF) and bindings is None:
                    bindings = [variants[0]]
                    variants = [None]

        if len(variants) == 1 and variants[0] == "_":
            variants = [None]

        guard = None
        if self.check(TokenType.IF):
            self.consume()
            guard = self.parse_expression()

        variant = variants[0] if len(variants) == 1 else variants
        return variant, bindings, guard

    def _parse_single_pattern(self):
        """Parse um único padrão (sem considerar `|`)."""
        if self.check(TokenType.NUMBER):
            return self.consume().value, None

        if self.check(TokenType.STRING):
            return StringExpr(self.consume().value), None

        if self.check(TokenType.IDENT):
            name = self.expect(TokenType.IDENT).value
            if name == "_":
                return None, None

            # Pattern de Struct: Ponto { x, y: 0 }
            if self.check(TokenType.LBRACE):
                self.consume()  # LBRACE
                fields = []
                struct_bindings = []
                while not self.check(TokenType.RBRACE):
                    fname = self.expect(TokenType.IDENT).value
                    if self.check(TokenType.COLON):
                        self.consume()
                        val = self.parse_expression()
                        fields.append(StructLiteralField(fname, val))
                        # Se for uma variável simples, consideramos como binding
                        if isinstance(val, VariableExpr):
                            struct_bindings.append(val.name)
                    else:
                        # `x` sozinho equivale a `x: x`
                        fields.append(StructLiteralField(fname, VariableExpr(fname, 0, 0)))
                        struct_bindings.append(fname)
                    if not self.match(TokenType.COMMA):
                        break
                self.expect(TokenType.RBRACE)
                return StructLiteralExpr(name, fields), struct_bindings

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

    # ==================================================================
    # Match expression — `match x { case 1 => ... }`
    # ==================================================================
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
        while (not self.check(TokenType.DEDENT)
               and not self.check(TokenType.RBRACE)
               and not self.check(TokenType.EOF)):
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
                binding = (bindings[0]
                           if isinstance(bindings, list) and bindings
                           else bindings)
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

    # ==================================================================
    # Match statement — `match x: case 1: ...`
    # ==================================================================
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
            cases, default = self._parse_cases_block()
            return MatchStmt(cond, cases, default)

        self.pos = saved_pos
        return self.parse_match_expr()

    # ==================================================================
    # Switch statement — mesmo comportamento de match-stmt
    # ==================================================================
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

        cases, default = self._parse_cases_block()
        return MatchStmt(cond, cases, default)
