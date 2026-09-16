from .base import ParserBase
from ..lexer.tokens import TokenType, Token
from ..ast import (
    NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr,
    ArrayExpr, IndexExpr, SliceExpr, MemberExpr, AddressOfExpr, DerefExpr,
    UnaryExpr, PropagateExpr, ComptimeExpr, StructLiteralExpr, CastExpr,
    LambdaExpr, StructLiteralField, Param, InterpolatedStringExpr,
)
from ..errors import LuminaError


class ExpressionParser(ParserBase):
    """Precedência (do mais baixo ao mais alto):

    expression → logical → bitwise_or → bitwise_xor → bitwise_and
    → comparison → shift → range → additive → term → factor → postfix

    Os níveis `bitwise_*` e `shift` foram adicionados para suportar
    `a | b`, `a & b`, `a ^ b`, `a << n`, `a >> n` em expressões comuns
    (não só em tipos). Isso destrava vários exemplos e std/async_fs.lm.
    """

    def parse_expression(self):
        node = self.parse_logical()
        while self.check(TokenType.PIPE):
            next_tok = self.peek(1)
            if not next_tok or next_tok.type != TokenType.GT:
                break
            self.consume()  # PIPE
            self.consume()  # GT
            func_name = self.expect(TokenType.IDENT).value
            callee = VariableExpr(func_name, 0, 0)
            node = CallExpr(callee, [node])
        return node

    def parse_logical(self):
        node = self.parse_bitwise_or()
        while self.check(TokenType.AND) or self.check(TokenType.OR):
            op = self.consume().value
            right = self.parse_bitwise_or()
            node = BinaryExpr(op, node, right)
        return node

    def parse_bitwise_or(self):
        node = self.parse_bitwise_xor()
        while self.check(TokenType.PIPE):
            # Só consome `|` se NÃO for `|>` (que é tratado em parse_expression)
            next_tok = self.peek(1)
            if next_tok and next_tok.type == TokenType.GT:
                break
            op = self.consume().value
            right = self.parse_bitwise_xor()
            node = BinaryExpr(op, node, right)
        return node

    def parse_bitwise_xor(self):
        node = self.parse_bitwise_and()
        while self.check(TokenType.CARET):
            op = self.consume().value
            right = self.parse_bitwise_and()
            node = BinaryExpr(op, node, right)
        return node

    def parse_bitwise_and(self):
        node = self.parse_comparison()
        while self.check(TokenType.AMP):
            # Só consome `&` se NÃO for `&&` (tratado em parse_logical)
            next_tok = self.peek(1)
            if next_tok and next_tok.type == TokenType.AMP:
                break
            op = self.consume().value
            right = self.parse_comparison()
            node = BinaryExpr(op, node, right)
        return node

    def parse_comparison(self):
        node = self.parse_shift()
        ops = [TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE]
        if any(self.check(op) for op in ops) or self.check(TokenType.IN):
            op = self.consume().value
            right = self.parse_shift()
            if any(self.check(op) for op in ops):
                next_op = self.consume().value
                right2 = self.parse_shift()
                left_node = BinaryExpr(op, node, right)
                right_node = BinaryExpr(next_op, right, right2)
                node = BinaryExpr('and', left_node, right_node)
            else:
                node = BinaryExpr(op, node, right)
        return node

    def parse_shift(self):
        node = self.parse_range()
        while self.check(TokenType.SHL) or self.check(TokenType.SHR):
            op = self.consume().value
            right = self.parse_range()
            node = BinaryExpr(op, node, right)
        return node

    def parse_range(self):
        node = self.parse_additive()
        while self.check(TokenType.DOT_DOT):
            self.consume()
            right = self.parse_additive()
            node = BinaryExpr('..', node, right)
        return node

    def parse_additive(self):
        node = self.parse_term()
        while self.check(TokenType.PLUS) or self.check(TokenType.MINUS):
            op = self.consume().value
            right = self.parse_term()
            node = BinaryExpr(op, node, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.check(TokenType.STAR) or self.check(TokenType.SLASH) or self.check(TokenType.PERCENT):
            op = self.consume().value
            right = self.parse_factor()
            node = BinaryExpr(op, node, right)
        return node

    def parse_factor(self):
        token = self.current_token()
        if not token:
            raise LuminaError(
                "Fim inesperado do código",
                filename=self.filename, line=0, col=0, source_code=self.source_code,
            )

        # NOVO: comptime(expr) ou comptime expr
        if self.check(TokenType.COMPTIME):
            self.consume()
            if self.check(TokenType.LPAREN):
                self.consume()
                inner = self.parse_expression()
                self.expect(TokenType.RPAREN)
            else:
                inner = self.parse_factor()
            return self.parse_postfix(ComptimeExpr(inner))

        if self.check(TokenType.MATCH):
            return self.parse_match_expr()
        if self.check(TokenType.DOLLAR):
            self.consume()
            str_token = self.expect(TokenType.STRING)
            s = str_token.value
            if '{' not in s:
                return StringExpr(s)
            parts, current, i = [], "", 0
            while i < len(s):
                if s[i] == '{':
                    if current:
                        parts.append(StringExpr(current))
                    current = ""
                    j = i + 1
                    var_name = ""
                    while j < len(s) and s[j] != '}':
                        var_name += s[j]
                        j += 1
                    parts.append(VariableExpr(var_name, token.line, token.col))
                    i = j + 1
                else:
                    current += s[i]
                    i += 1
            if current:
                parts.append(StringExpr(current))
            return InterpolatedStringExpr(parts)
        if self.check(TokenType.FN):
            self.consume()
            self.expect(TokenType.LPAREN)
            params = []
            if not self.check(TokenType.RPAREN):
                while True:
                    p_name = self.expect(TokenType.IDENT).value
                    self.expect(TokenType.COLON)
                    p_type = self.parse_type()
                    params.append(Param(p_name, p_type, None))
                    if not self.match(TokenType.COMMA):
                        break
            self.expect(TokenType.RPAREN)
            return_type = "void"
            if self.match(TokenType.ARROW):
                return_type = self.parse_type()
            if self.match(TokenType.FAT_ARROW):
                body_expr = self.parse_expression()
                return LambdaExpr(params, return_type, [body_expr])
            elif self.match(TokenType.COLON):
                if self.check(TokenType.NEWLINE):
                    self.expect(TokenType.NEWLINE)
                    self.expect(TokenType.INDENT)
                    body = []
                    while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
                        if self.match(TokenType.NEWLINE):
                            continue
                        body.append(self.parse_statement())
                    self.expect(TokenType.DEDENT)
                    return LambdaExpr(params, return_type, body)
                else:
                    body_expr = self.parse_expression()
                    return LambdaExpr(params, return_type, [body_expr])
            else:
                raise LuminaError(
                    "Esperado '=>' ou ':' no corpo do lambda",
                    filename=self.filename, line=token.line, col=token.col, source_code=self.source_code,
                )
        if self.check(TokenType.MINUS) or self.check(TokenType.PLUS):
            op = self.consume().value
            return UnaryExpr(op, self.parse_factor())
        if self.check(TokenType.NOT):
            self.consume()
            return UnaryExpr('not', self.parse_factor())
        if self.check(TokenType.AMP):
            self.consume()
            return AddressOfExpr(self.parse_factor())
        if self.check(TokenType.STAR):
            self.consume()
            node = DerefExpr(self.parse_factor())
            return self.parse_postfix(node)
        if self.check(TokenType.TRUE) or self.check(TokenType.FALSE):
            val = self.consume().value
            return self.parse_postfix(BoolExpr(val == 'true'))
        if self.match(TokenType.LBRACKET):
            elements = []
            if not self.check(TokenType.RBRACKET):
                while True:
                    elements.append(self.parse_expression())
                    if not self.match(TokenType.COMMA):
                        break
            self.expect(TokenType.RBRACKET)
            return ArrayExpr(elements)
        if self.check(TokenType.NUMBER) or self.check(TokenType.FLOAT):
            self.consume()
            is_float = '.' in token.value
            return self.parse_postfix(NumberExpr(token.value, is_float))
        if self.check(TokenType.STRING):
            str_token = self.consume()
            return self.parse_postfix(StringExpr(str_token.value))
        if self.check(TokenType.IDENT):
            name = self.consume().value
            if not getattr(self, 'no_struct_literal', False) and self.check(TokenType.LBRACE):
                self.consume()
                fields = []
                while not self.check(TokenType.RBRACE):
                    if self.match(TokenType.NEWLINE) or self.match(TokenType.INDENT) or self.match(TokenType.DEDENT):
                        continue
                    field_name = self.expect(TokenType.IDENT).value
                    self.expect(TokenType.COLON)
                    field_val = self.parse_expression()
                    fields.append(StructLiteralField(field_name, field_val))
                    if not self.match(TokenType.COMMA):
                        break
                self.expect(TokenType.RBRACE)
                return StructLiteralExpr(name, fields)
            if self.check(TokenType.LPAREN):
                self.consume()
                args = []
                if not self.check(TokenType.RPAREN):
                    while True:
                        args.append(self.parse_expression())
                        if not self.match(TokenType.COMMA):
                            break
                self.expect(TokenType.RPAREN)
                callee_node = VariableExpr(name, token.line, token.col)
                node = CallExpr(callee_node, args)
            else:
                node = VariableExpr(name, token.line, token.col)
            return self.parse_postfix(node)
        if self.match(TokenType.LPAREN):
            node = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return self.parse_postfix(node)
        if self.check(TokenType.NONE):
            self.consume()
            return NumberExpr('0', False)
        raise LuminaError(
            f"Token inesperado {token.type.name} ('{token.value}')",
            filename=self.filename, line=token.line, col=token.col, source_code=self.source_code,
        )

    def parse_postfix(self, node):
        while True:
            if self.match(TokenType.LBRACKET):
                node = self._parse_slice_or_index(node)
            elif self.check(TokenType.QUESTION) and self.peek(1) and self.peek(1).type == TokenType.DOT:
                self.consume()
                self.consume()
                member_name = self.expect(TokenType.IDENT).value
                if self.check(TokenType.LPAREN):
                    self.consume()
                    member_node = MemberExpr(node, member_name, is_safe=True)
                    args = [node]
                    if not self.check(TokenType.RPAREN):
                        while True:
                            args.append(self.parse_expression())
                            if not self.match(TokenType.COMMA):
                                break
                    self.expect(TokenType.RPAREN)
                    node = CallExpr(member_node, args, is_method=True)
                else:
                    node = MemberExpr(node, member_name, is_safe=True)
            elif self.check(TokenType.DOT):
                self.consume()
                member_name = self.expect(TokenType.IDENT).value
                if self.check(TokenType.LPAREN):
                    self.consume()
                    member_node = MemberExpr(node, member_name, is_safe=False)
                    args = [node]
                    if not self.check(TokenType.RPAREN):
                        while True:
                            args.append(self.parse_expression())
                            if not self.match(TokenType.COMMA):
                                break
                    self.expect(TokenType.RPAREN)
                    node = CallExpr(member_node, args, is_method=True)
                else:
                    node = MemberExpr(node, member_name, is_safe=False)
            else:
                break
        if self.match(TokenType.QUESTION):
            node = PropagateExpr(node)
        if self.check(TokenType.AS):
            self.consume()
            target_type = self.expect(TokenType.IDENT).value
            node = CastExpr(node, target_type)
        return node

    def _parse_slice_or_index(self, base_node):
        """Chamado após consumir `[`. Decide entre IndexExpr e SliceExpr.

        Suporta:
          arr[i]         → IndexExpr
          arr[a..b]      → SliceExpr(a, b)
          arr[a..]       → SliceExpr(a, None)
          arr[..b]       → SliceExpr(None, b)
          arr[..]        → SliceExpr(None, None)

        Usa `parse_additive()` para os bounds (não `parse_expression`),
        para não consumir o `..` como operador binário.
        """
        # Caso: arr[..] ou arr[..end]
        if self.check(TokenType.DOT_DOT):
            self.consume()
            if self.check(TokenType.RBRACKET):
                self.consume()
                return SliceExpr(base_node, None, None)
            end = self.parse_additive()
            self.expect(TokenType.RBRACKET)
            return SliceExpr(base_node, None, end)

        # Caso: arr[i], arr[a..], arr[a..b]
        first = self.parse_additive()
        if self.check(TokenType.DOT_DOT):
            self.consume()
            if self.check(TokenType.RBRACKET):
                self.consume()
                return SliceExpr(base_node, first, None)
            end = self.parse_additive()
            self.expect(TokenType.RBRACKET)
            return SliceExpr(base_node, first, end)

        self.expect(TokenType.RBRACKET)
        return IndexExpr(base_node, first)

    def parse_type(self):
        type_name = self.expect(TokenType.IDENT).value
        if self.check(TokenType.LT):
            self.consume()
            args = [self.parse_type()]
            while self.match(TokenType.COMMA):
                args.append(self.parse_type())
            self._expect_gt_for_type()
            type_name = type_name + "<" + ",".join(args) + ">"
        return type_name

    def parse_type_params(self):
        self.expect(TokenType.LT)
        params = []
        while True:
            params.append(self.expect(TokenType.IDENT).value)
            if self.match(TokenType.COMMA):
                continue
            else:
                break
        self._expect_gt_for_type()
        return params

    def _expect_gt_for_type(self):
        """Consome um '>' no contexto de tipo, tratando '>>' (SHR) como
        dois '>' consecutivos.
        """
        tok = self.current_token()
        if tok is None:
            raise LuminaError(
                "Fim inesperado ao esperar '>'",
                filename=self.filename, line=0, col=0, source_code=self.source_code,
            )

        if tok.type == TokenType.GT:
            self.consume()
            return

        if tok.type == TokenType.SHR:
            first = Token(TokenType.GT, ">", tok.line, tok.col, tok.offset)
            second = Token(TokenType.GT, ">", tok.line, tok.col + 1, tok.offset + 1)
            self.tokens[self.pos] = first
            self.tokens.insert(self.pos + 1, second)
            self.consume()
            return

        self.expect(TokenType.GT)