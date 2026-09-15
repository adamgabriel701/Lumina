from .patterns import PatternParser
from ..lexer.tokens import TokenType
from ..ast import (
    VarDecl, DestructureStmt, AssignStmt, ReturnStmt, IfStmt, WhileStmt,
    ForStmt, BreakStmt, ContinueStmt, DeferStmt, AssertStmt, BenchStmt,
    Function,
)


class StatementParser(PatternParser):
    """Statements e estruturas de controle."""

    def parse_statement(self):
        token = self.current_token()
        if not token:
            return None
        if token.type == TokenType.NEWLINE:
            self.consume()
            return self.parse_statement()
        if token.type == TokenType.LET or token.type == TokenType.MUT:
            return self.parse_let()
        elif token.type == TokenType.RETURN:
            return self.parse_return()
        elif token.type == TokenType.IF:
            return self.parse_if()
        elif token.type == TokenType.WHILE:
            return self.parse_while()
        elif token.type == TokenType.FOR:
            return self.parse_for()
        elif token.type == TokenType.BREAK:
            self.consume()
            self.match(TokenType.NEWLINE)
            return BreakStmt()
        elif token.type == TokenType.CONTINUE:
            self.consume()
            self.match(TokenType.NEWLINE)
            return ContinueStmt()
        elif token.type == TokenType.IMPORT:
            return self.parse_import()
        elif token.type == TokenType.EXTERN:
            return self.parse_extern()
        elif token.type == TokenType.DEFER:
            return self.parse_defer()
        elif token.type == TokenType.ASSERT:
            return self.parse_assert()
        elif token.type == TokenType.BENCH:
            return self.parse_bench()
        elif token.type == TokenType.TEST:
            return self.parse_test()
        elif token.type == TokenType.MATCH:
            return self.parse_match_stmt()
        elif token.type == TokenType.SWITCH:
            return self.parse_switch()
        elif (token.type == TokenType.IDENT
              and self.peek(1) and self.peek(1).type == TokenType.COLON_ASSIGN):
            var_token = self.consume()
            self.consume()
            value = self.parse_expression()
            self.match(TokenType.NEWLINE)
            return VarDecl(var_token.value, None, value, True, var_token.line, var_token.col)
        else:
            expr = self.parse_expression()
            if self.check(TokenType.ASSIGN):
                self.consume()
                value = self.parse_expression()
                self.match(TokenType.NEWLINE)
                return AssignStmt(expr, value)
            self.match(TokenType.NEWLINE)
            return expr

    def parse_let(self):
        if self.check(TokenType.MUT):
            is_mutable = True
            self.consume()
        else:
            is_mutable = False
            self.expect(TokenType.LET)
        if self.check(TokenType.LPAREN):
            self.consume()
            names = []
            while True:
                names.append(self.expect(TokenType.IDENT).value)
                if self.match(TokenType.COMMA):
                    continue
                else:
                    break
            self.expect(TokenType.RPAREN)
            self.expect(TokenType.ASSIGN)
            expr = self.parse_expression()
            self.match(TokenType.NEWLINE)
            return DestructureStmt(names, expr, is_mutable)
        var_token = self.expect(TokenType.IDENT)
        var_name = var_token.value
        var_line, var_col = var_token.line, var_token.col
        var_type = None
        if self.match(TokenType.COLON):
            var_type = self.parse_type()
        expr = None
        if self.match(TokenType.ASSIGN):
            expr = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return VarDecl(var_name, var_type, expr, is_mutable, var_line, var_col)

    def parse_return(self):
        self.consume(TokenType.RETURN)
        values = []
        if not self.check(TokenType.NEWLINE) and not self.check(TokenType.DEDENT):
            values.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                values.append(self.parse_expression())
        self.match(TokenType.NEWLINE)
        return ReturnStmt(values)

    def parse_if(self):
        self.consume(TokenType.IF)
        condition = self.parse_expression()
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        while self.check(TokenType.NEWLINE):
            self.consume()
        self.expect(TokenType.INDENT)
        then_body = []
        while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                continue
            then_body.append(self.parse_statement())
        self.expect(TokenType.DEDENT)
        else_body = None
        if self.check(TokenType.ELSE) or self.check(TokenType.ELIF):
            self.consume()
            if self.check(TokenType.IF):
                else_body = [self.parse_if()]
            else:
                self.expect(TokenType.COLON)
                self.expect(TokenType.NEWLINE)
                while self.check(TokenType.NEWLINE):
                    self.consume()
                self.expect(TokenType.INDENT)
                else_body = []
                while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
                    if self.match(TokenType.NEWLINE):
                        continue
                    else_body.append(self.parse_statement())
                self.expect(TokenType.DEDENT)
        return IfStmt(condition, then_body, else_body)

    def parse_while(self):
        self.consume(TokenType.WHILE)
        condition = self.parse_expression()
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
        return WhileStmt(condition, body)

    def parse_for(self):
        self.consume(TokenType.FOR)
        var_name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.IN)
        start = None
        end = None
        iterable = None
        first_expr = self.parse_additive()
        if self.check(TokenType.DOT_DOT):
            self.consume()
            start = first_expr
            end = self.parse_additive()
        else:
            iterable = first_expr
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
        return ForStmt(var_name, start, end, iterable, body)

    def parse_defer(self):
        self.consume(TokenType.DEFER)
        if self.match(TokenType.COLON):
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
            return DeferStmt(body, False)
        expr = self.parse_expression()
        self.match(TokenType.NEWLINE)
        return DeferStmt([expr], False)

    def parse_assert(self):
        self.consume(TokenType.ASSERT)
        self.expect(TokenType.LPAREN)
        cond = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.match(TokenType.NEWLINE)
        return AssertStmt(cond)

    def parse_test(self):
        self.consume(TokenType.TEST)
        test_name = self.expect(TokenType.STRING).value
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
        return Function(f"test_{test_name.replace(' ', '_')}", [], "int", body)

    def parse_bench(self):
        self.consume(TokenType.BENCH)
        bench_name = self.expect(TokenType.STRING).value
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
        return BenchStmt(bench_name, body)
