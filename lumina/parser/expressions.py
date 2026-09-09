from ..ast import NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, TupleExpr, UnaryExpr, PropagateExpr, ComptimeExpr, StructLiteralExpr, MatchExpr, CastExpr
from ..lexer import TokenType
from ..errors import LuminaError

class ExpressionParser:
    def parse_expression(self):
        node = self.parse_logical()
        while self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '|>':
            self.consume()
            func_name = self.consume(TokenType.IDENT).value
            node = CallExpr(func_name, [node])
        return node

    def parse_logical(self):
        node = self.parse_comparison()
        while self.current_token() and self.current_token().type == TokenType.KEYWORD and self.current_token().value in ('and', 'or'):
            op = self.consume().value
            right = self.parse_comparison()
            node = BinaryExpr(op, node, right)
        return node

    def parse_comparison(self):
        node = self.parse_additive()
        while self.current_token() and ((self.current_token().type == TokenType.OP and self.current_token().value in ('==', '!=', '<', '>', '<=', '>=')) or (self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'in')):
            op = self.consume().value
            right = self.parse_additive()
            node = BinaryExpr(op, node, right)
        return node

    def parse_additive(self):
        node = self.parse_term()
        while self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value in ('+', '-', '..'):
            op = self.consume().value
            right = self.parse_term()
            node = BinaryExpr(op, node, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value in ('*', '/', '%'):
            op = self.consume().value
            right = self.parse_factor()
            node = BinaryExpr(op, node, right)
        return node

    def parse_factor(self):
        token = self.current_token()
        
        # Operadores Unários e Acesso à Memória
        if token.type == TokenType.OP and token.value in ('-', '+'):
            op = self.consume().value
            return UnaryExpr(op, self.parse_factor())
        if token.type == TokenType.KEYWORD and token.value == 'not':
            self.consume()
            return UnaryExpr('not', self.parse_factor())
        if token.type == TokenType.OP and token.value == '&':
            self.consume()
            return AddressOfExpr(self.parse_factor())
        if token.type == TokenType.OP and token.value == '*':
            self.consume()
            node = DerefExpr(self.parse_factor())
            # Pode haver acesso após derrefência
            return self.parse_postfix(node)
            
        # Booleanos
        if token.type == TokenType.KEYWORD and token.value in ('true', 'false'):
            self.consume()
            return BoolExpr(token.value == 'true')
            
        # Arrays Literais
        if token.type == TokenType.OP and token.value == '[':
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
            
        # Números
        if token.type == TokenType.NUMBER:
            self.consume()
            is_float = '.' in token.value
            return NumberExpr(token.value, is_float)
            
        # F-strings ($"texto {var}")
        if token.type == TokenType.OP and token.value == '$' and self.peek() and self.peek().type == TokenType.STRING:
            self.consume()
            str_token = self.consume(TokenType.STRING)
            s = str_token.value
            from ..lexer import Lexer
            from .parser import Parser
            parts, current, i = [], "", 0
            while i < len(s):
                if s[i] == '{':
                    if current: parts.append(StringExpr(current))
                    current = ""
                    j = i + 1
                    while j < len(s) and s[j] != '}':
                        current += s[j]
                        j += 1
                    mini_parser = Parser(Lexer(current).tokenize(), self.filename, self.source_code)
                    parts.append(mini_parser.parse_expression())
                    current = ""
                    i = j + 1
                else:
                    current += s[i]
                    i += 1
            if current: parts.append(StringExpr(current))
            if len(parts) == 1 and isinstance(parts[0], StringExpr):
                return parts[0]
            return ArrayExpr(parts)
            
        # Strings
        if token.type == TokenType.STRING:
            self.consume()
            return StringExpr(token.value)
            
        # Comptime
        if token.type == TokenType.KEYWORD and token.value == 'comptime':
            self.consume()
            if self.current_token().type == TokenType.OP and self.current_token().value == '(':
                self.consume()
                expr = self.parse_expression()
                self.consume(TokenType.OP)
                return ComptimeExpr(expr)
            raise LuminaError("Esperado '(' após 'comptime'", self.filename, token.line, token.col, self.source_code)
            
        # Match Expression
        if token.type == TokenType.KEYWORD and token.value == 'match':
            return self.parse_match_expr()
            
        # Identificadores, Chamadas de Função e Struct Literals
        if token.type == TokenType.IDENT or (token.type == TokenType.KEYWORD and token.value == 'print'):
            name = self.consume().value
            
            # Struct Literal (ex: Point { x: 10, y: 20 })
            if not getattr(self, 'no_struct_literal', False) and self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '{':
                self.consume() # '{'
                fields = []
                while not (self.current_token().type == TokenType.OP and self.current_token().value == '}'):
                    if self.current_token().type in (TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT):
                        self.consume()
                        continue
                    field_name = self.consume(TokenType.IDENT).value
                    self.consume(TokenType.OP) # ':'
                    field_val = self.parse_expression()
                    fields.append((field_name, field_val))
                    if self.current_token().type == TokenType.OP and self.current_token().value == ',':
                        self.consume()
                self.consume(TokenType.OP) # '}'
                return StructLiteralExpr(name, fields)
                
            # Chamada de Função (ex: soma(1, 2))
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
                
            return self.parse_postfix(node)
            
        # Expressões entre parênteses
        if token.type == TokenType.OP and token.value == '(':
            self.consume()
            node = self.parse_expression()
            self.consume(TokenType.OP)
            return self.parse_postfix(node)
            
        raise LuminaError(f"Token inesperado {token.type} ('{token.value}')", self.filename, token.line, token.col, self.source_code)

    def parse_postfix(self, node):
        # Acesso a Membros, Indexação e Propagação de Erros
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
            
        # Operador de Propagação de Erros (?)
        if self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '?':
            self.consume()
            node = PropagateExpr(node)
            
        # Casting de Tipos (as)
        if self.current_token() and self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'as':
            self.consume()
            target_type = self.consume(TokenType.IDENT).value
            node = CastExpr(node, target_type)
            
        return node

    def parse_match_expr(self):
        self.consume() # 'match'
        self.no_struct_literal = True
        cond = self.parse_expression()
        self.no_struct_literal = False
        self.consume(TokenType.OP) # '{'
        
        cases = []
        default = None
        
        while not (self.current_token().type == TokenType.OP and self.current_token().value == '}'):
            if self.current_token().type in (TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT):
                self.consume()
                continue
                
            if self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'else':
                self.consume()
                self.consume(TokenType.OP) # '=>'
                default = self.parse_expression()
                if self.current_token().type == TokenType.OP and self.current_token().value == ',':
                    self.consume()
                continue
            else:
                val = self.parse_expression()
                self.consume(TokenType.OP) # '=>'
                res = self.parse_expression()
                cases.append((val, res))
                if self.current_token().type == TokenType.OP and self.current_token().value == ',':
                    self.consume()
                continue
                
        self.consume(TokenType.OP) # '}'
        return MatchExpr(cond, cases, default)