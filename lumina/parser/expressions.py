from ..ast import NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, TupleExpr, UnaryExpr, PropagateExpr
from ..errors import LuminaError
from ..lexer import TokenType

class ExpressionParser:
    def parse_expression(self):
        node = self.parse_logical()
        
        # NOVO: Operador Pipe (|>)
        while self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '|>':
            self.consume() # Consome '|>'
            func_name = self.consume(TokenType.IDENT).value
            # Transforma `dados |> func` em `func(dados)`
            node = CallExpr(func_name, [node])
            
        return node

    def parse_logical(self):
        node = self.parse_bitwise()
        while self.current_token() and self.current_token().type == TokenType.KEYWORD and self.current_token().value in ('and', 'or'):
            op = self.consume().value
            right = self.parse_bitwise()
            node = BinaryExpr(op, node, right)
        return node

    # NOVO: Operadores Bitwise (&, |, ^, <<, >>)
    def parse_bitwise(self):
        node = self.parse_comparison()
        while self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value in ('&', '|', '^', '<<', '>>'):
            op = self.consume().value
            right = self.parse_comparison()
            node = BinaryExpr(op, node, right)
        return node

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
            # Constant Folding
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
            # Constant Folding
            if isinstance(node, NumberExpr) and isinstance(right, NumberExpr) and not node.is_float and not right.is_float:
                if op == '*': node = NumberExpr(str(int(node.value) * int(right.value)))
                elif op == '/': node = NumberExpr(str(int(node.value) // int(right.value)))
                elif op == '%': node = NumberExpr(str(int(node.value) % int(right.value)))
            else:
                node = BinaryExpr(op, node, right)
        return node

    def parse_factor(self):
        token = self.current_token()
        
        # Operador Unário (- e +)
        if token.type == TokenType.OP and token.value in ('-', '+'):
            op = self.consume().value
            return UnaryExpr(op, self.parse_factor())
            
        # Operador NOT
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
            
        # NOVO: F-string com prefixo $ ($"texto {var}")
        elif token.type == TokenType.OP and token.value == '$' and self.peek() and self.peek().type == TokenType.STRING:
            self.consume() # Consome o '$'
            str_token = self.consume(TokenType.STRING)
            s = str_token.value
            
            from ..lexer import Lexer
            from .parser import Parser
            
            parts = []
            current = ""
            i = 0
            while i < len(s):
                if s[i] == '{':
                    if current: parts.append(StringExpr(current))
                    current = ""
                    j = i + 1
                    while j < len(s) and s[j] != '}':
                        current += s[j]
                        j += 1
                        
                    mini_lexer = Lexer(current)
                    mini_parser = Parser(mini_lexer.tokenize(), self.filename, self.source_code)
                    parts.append(mini_parser.parse_expression())
                    current = ""
                    i = j + 1
                else:
                    current += s[i]
                    i += 1
            if current: parts.append(StringExpr(current))
            
            # Se só tiver uma parte e for string, retorna como StringExpr normal
            if len(parts) == 1 and isinstance(parts[0], StringExpr):
                return parts[0]
            return ArrayExpr(parts)
            
        elif token.type == TokenType.STRING:
            self.consume()
            # NOVO: Strings normais não são mais quebradas em Arrays por causa de {}
            return StringExpr(token.value)
            
        elif token.type == TokenType.IDENT or (token.type == TokenType.KEYWORD and token.value == 'print'):
            name = self.consume().value
            
            # NOVO: Atribui a 'node' em vez de retornar imediatamente
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
                node = CallExpr(name, args)
            else:
                node = VariableExpr(name, token.line, token.col)
            
            # Loop de Acesso (. e [])
            while True:
                if self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '[':
                    self.consume()
                    index = self.parse_expression()
                    self.consume(TokenType.OP)
                    node = IndexExpr(node, index)
                elif self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value in ('.', '?.'):
                    op = self.consume().value
                    member_name = self.consume(TokenType.IDENT).value
                    is_safe = (op == '?.')
                    
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
                        node = MemberExpr(node, member_name, is_safe=is_safe)
                else:
                    break
            
            # NOVO: Operador de Propagação de Erros (?)
            if self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '?':
                self.consume()
                node = PropagateExpr(node)
                
            return node
            
        elif token.type == TokenType.OP and token.value == '(':
            self.consume()
            expr = self.parse_expression()
            self.consume(TokenType.OP)
            return expr
            
        raise LuminaError(f"Token inesperado {token.type} ('{token.value}')", self.filename, token.line, token.col, self.source_code)