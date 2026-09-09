from ..ast import IfStmt, WhileStmt, ForStmt, MatchStmt, ArrayExpr, VariableExpr, BinaryExpr
from ..lexer import TokenType

class ControlFlowParser:
    def parse_if(self):
        self.consume()
        condition = self.parse_expression()
        self.consume(TokenType.OP)
        self.consume(TokenType.NEWLINE)
        self.consume(TokenType.INDENT)
        then_body = []
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
            then_body.append(self.parse_statement())
        self.consume(TokenType.DEDENT)
        else_body = None
        if self.current_token() and self.current_token().type == TokenType.KEYWORD and self.current_token().value in ('else', 'elif'):
            if self.current_token().value == 'elif':
                else_body = [self.parse_if()]
            else:
                self.consume(); self.consume(TokenType.OP); self.consume(TokenType.NEWLINE); self.consume(TokenType.INDENT)
                else_body = []
                while self.current_token() and self.current_token().type != TokenType.DEDENT:
                    if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
                    else_body.append(self.parse_statement())
                self.consume(TokenType.DEDENT)
        return IfStmt(condition, then_body, else_body)

    def parse_while(self):
        self.consume()
        condition = self.parse_expression()
        self.consume(TokenType.OP)
        self.consume(TokenType.NEWLINE)
        self.consume(TokenType.INDENT)
        body = []
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
            body.append(self.parse_statement())
        self.consume(TokenType.DEDENT)
        return WhileStmt(condition, body)

    def parse_for(self):
        self.consume() # 'for'
        var_name = self.consume(TokenType.IDENT).value
        self.consume(TokenType.KEYWORD) # 'in'
        
        # Lê a expressão completa (pode ser um range `0..10` ou um array `arr`)
        expr = self.parse_expression()
        
        self.consume(TokenType.OP) # ':'
        self.consume(TokenType.NEWLINE)
        self.consume(TokenType.INDENT)
        body = []
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
            body.append(self.parse_statement())
        self.consume(TokenType.DEDENT)
        
        # NOVO: Se for um range (BinaryExpr com op '..')
        if isinstance(expr, BinaryExpr) and expr.op == '..':
            return ForStmt(var_name, expr.left, expr.right, body)
            
        # Se não, é um iterador (array ou string)
        else:
            return ForStmt(var_name, None, None, body, iterable=expr)

    def parse_match(self):
        self.consume()
        condition = self.parse_expression()
        self.consume(TokenType.OP); self.consume(TokenType.NEWLINE); self.consume(TokenType.INDENT)
        cases, default = [], None
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
            if self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'case':
                self.consume()
                variant_name = self.consume(TokenType.IDENT).value
                var_name = None
                if self.current_token().type == TokenType.OP and self.current_token().value == '(':
                    self.consume(); var_name = self.consume(TokenType.IDENT).value; self.consume(TokenType.OP)
                self.consume(TokenType.OP); self.consume(TokenType.NEWLINE); self.consume(TokenType.INDENT)
                body = []
                while self.current_token() and self.current_token().type != TokenType.DEDENT:
                    if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
                    body.append(self.parse_statement())
                self.consume(TokenType.DEDENT)
                cases.append((variant_name, var_name, body))
            elif self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'default':
                self.consume(); self.consume(TokenType.OP); self.consume(TokenType.NEWLINE); self.consume(TokenType.INDENT)
                default = []
                while self.current_token() and self.current_token().type != TokenType.DEDENT:
                    if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
                    default.append(self.parse_statement())
                self.consume(TokenType.DEDENT)
        self.consume(TokenType.DEDENT)
        return MatchStmt(condition, cases, default)