from ..ast import NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, TupleExpr, UnaryExpr
from ..errors import LuminaError
from ..lexer import TokenType

class ExpressionParser:
    def parse_expression(self):
        # Operadores lógicos têm a menor precedência
        node = self.parse_logical()
        return node

    def parse_logical(self):
        node = self.parse_comparison()
        while self.current_token() and self.current_token().type == TokenType.KEYWORD and self.current_token().value in ('and', 'or'):
            op = self.consume().value
            right = self.parse_comparison()
            node = BinaryExpr(op, node, right)
        return node

    # NOVO: Método restaurado para cuidar do >, <, ==, etc
    def parse_comparison(self):
        node = self.parse_additive()
        while self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value in ('==', '!=', '<', '>', '<=', '>='):
            op = self.consume().value
            right = self.parse_additive()
            node = BinaryExpr(op, node, right)
        return node

    def parse_additive(self):
        node = self.parse_term()
        while self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value in ('+', '-'):
            op = self.consume().value
            right = self.parse_term()
            # NOVO: Constant Folding (Soma e Subtração)
            if isinstance(node, NumberExpr) and isinstance(right, NumberExpr) and not node.is_float and not right.is_float:
                if op == '+': node = NumberExpr(str(int(node.value) + int(right.value)))
                elif op == '-': node = NumberExpr(str(int(node.value) - int(right.value)))
            else:
                node = BinaryExpr(op, node, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value in ('*', '/', '%'):
            op = self.consume().value
            right = self.parse_factor()
            # NOVO: Constant Folding (Multiplicação, Divisão e Módulo)
            if isinstance(node, NumberExpr) and isinstance(right, NumberExpr) and not node.is_float and not right.is_float:
                if op == '*': node = NumberExpr(str(int(node.value) * int(right.value)))
                elif op == '/': node = NumberExpr(str(int(node.value) // int(right.value)))
                elif op == '%': node = NumberExpr(str(int(node.value) % int(right.value)))
            else:
                node = BinaryExpr(op, node, right)
        return node

    def parse_factor(self):
        token = self.current_token()
        
        # NOVO: Operador NOT
        if token.type == TokenType.KEYWORD and token.value == 'not':
            self.consume()
            return UnaryExpr('not', self.parse_factor())
            
        if token.type == TokenType.OP and token.value == '&':
            self.consume()
            return AddressOfExpr(self.parse_factor())
        elif token.type == TokenType.OP and token.value == '*':
            self.consume()
            return DerefExpr(self.parse_factor())
            
        elif token.type == TokenType.KEYWORD and token.value in ('true', 'false'):
            self.consume()
            return BoolExpr(token.value == 'true')
            
        elif token.type == TokenType.OP and token.value == '[':
            self.consume()
            elements = []
            if self.current_token().type != TokenType.OP or self.current_token().value != ']':
                while True:
                    elements.append(self.parse_expression())
                    if self.current_token().type == TokenType.OP and self.current_token().value == ',':
                        self.consume()
                    else:
                        break
            self.consume(TokenType.OP)
            return ArrayExpr(elements)
            
        elif token.type == TokenType.NUMBER:
            self.consume()
            is_float = '.' in token.value
            return NumberExpr(token.value, is_float)
            
        elif token.type == TokenType.STRING:
            self.consume()
            return StringExpr(token.value)
            
        elif token.type == TokenType.IDENT or (token.type == TokenType.KEYWORD and token.value == 'print'):
            name = self.consume().value
            
            if self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '(':
                self.consume()
                args = []
                if self.current_token().type != TokenType.OP or self.current_token().value != ')':
                    while True:
                        args.append(self.parse_expression())
                        if self.current_token().type == TokenType.OP and self.current_token().value == ',':
                            self.consume()
                        else:
                            break
                self.consume(TokenType.OP)
                return CallExpr(name, args)
                
            node = VariableExpr(name, token.line, token.col)
            
            while True:
                if self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '[':
                    self.consume()
                    index = self.parse_expression()
                    self.consume(TokenType.OP)
                    node = IndexExpr(node, index)
                elif self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '.':
                    self.consume()
                    member_name = self.consume(TokenType.IDENT).value
                    if self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '(':
                        self.consume()
                        args = [node]
                        if self.current_token().type != TokenType.OP or self.current_token().value != ')':
                            while True:
                                args.append(self.parse_expression())
                                if self.current_token().type == TokenType.OP and self.current_token().value == ',':
                                    self.consume()
                                else:
                                    break
                        self.consume(TokenType.OP)
                        node = CallExpr(member_name, args, is_method=True)
                    else:
                        node = MemberExpr(node, member_name)
                else:
                    break
                
            return node
            
        elif token.type == TokenType.OP and token.value == '(':
            self.consume()
            expr = self.parse_expression()
            self.consume(TokenType.OP)
            return expr
            
        raise LuminaError(f"Token inesperado {token.type} ('{token.value}')", self.filename, token.line, token.col, self.source_code)