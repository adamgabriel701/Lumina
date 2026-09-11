from ..ast import (
    NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, 
    ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, TupleExpr, 
    UnaryExpr, PropagateExpr, ComptimeExpr, StructLiteralExpr, MatchExpr, 
    CastExpr, LambdaExpr
)
from ..lexer.tokens import TokenType, KEYWORDS
from ..errors import LuminaError

class ExpressionParser:
    
    # --- Helpers de Navegação ---
    def check(self, t_type: TokenType, t_val: str = None) -> bool:
        t = self.current_token()
        if not t: return False
        if t.type != t_type: return False
        if t_val is not None and t.value != t_val: return False
        return True

    def match(self, t_type: TokenType, t_val: str = None) -> bool:
        if self.check(t_type, t_val):
            self.consume()
            return True
        return False

    def expect(self, t_type: TokenType, t_val: str = None):
        if self.check(t_type, t_val):
            return self.consume()
        
        t = self.current_token()
        expected = f"{t_type.name}" + (f" ('{t_val}')" if t_val else "")
        found = f"{t.type.name} ('{t.value}')" if t else "EOF"
        raise LuminaError(
            f"Esperado {expected}, mas encontrei {found}", 
            filename=self.filename, line=t.line if t else 0, col=t.col if t else 0, code=self.source_code
        )

    # --- Regras de Precedência ---
    def parse_expression(self):
        node = self.parse_logical()
        # UFCS Pipe Operator |>
        while self.check(TokenType.OP, '|>'):
            self.consume()
            func_name = self.expect(TokenType.IDENT).value
            node = CallExpr(func_name, [node])
        return node

    def parse_logical(self):
        node = self.parse_comparison()
        while self.check(TokenType.KEYWORD, 'and') or self.check(TokenType.KEYWORD, 'or'):
            op = self.consume().value
            right = self.parse_comparison()
            node = BinaryExpr(op, node, right)
        return node

    def parse_comparison(self):
        node = self.parse_range()
        comparison_ops = [TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE]
        
        while any(self.check(op) for op in comparison_ops) or self.check(TokenType.KEYWORD, 'in'):
            op = self.consume().value
            right = self.parse_range()
            node = BinaryExpr(op, node, right)
        return node

    def parse_range(self):
        node = self.parse_additive()
        while self.check(TokenType.OP, '..'):
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
            raise LuminaError("Fim inesperado do código", filename=self.filename, line=0, col=0, code=self.source_code)
        
        # Lambdas
        if self.check(TokenType.KEYWORD, 'fn'):
            self.consume() # 'fn'
            self.expect(TokenType.LPAREN)
            params = []
            if not self.check(TokenType.RPAREN):
                while True:
                    p_name = self.expect(TokenType.IDENT).value
                    self.expect(TokenType.COLON)
                    p_type = self.parse_type()
                    params.append((p_name, p_type, None))
                    if not self.match(TokenType.COMMA): break
            self.expect(TokenType.RPAREN)
            
            return_type = "void"
            if self.match(TokenType.ARROW):
                return_type = self.parse_type()
                
            # Corpo do Lambda (Expressão ou Bloco)
            if self.match(TokenType.FAT_ARROW):
                body_expr = self.parse_expression()
                return LambdaExpr(params, return_type, [body_expr]) # Lambda de expressão única
            elif self.match(TokenType.COLON):
                self.expect(TokenType.NEWLINE)
                self.expect(TokenType.INDENT)
                body = []
                while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
                    if self.match(TokenType.NEWLINE): continue
                    body.append(self.parse_statement())
                self.expect(TokenType.DEDENT)
                return LambdaExpr(params, return_type, body)
            else:
                raise LuminaError("Esperado '=>' ou ':' no corpo do lambda", filename=self.filename, line=token.line, col=token.col, code=self.source_code)
        
        # Unários e Ponteiros
        if self.check(TokenType.MINUS) or self.check(TokenType.PLUS):
            op = self.consume().value
            return UnaryExpr(op, self.parse_factor())
        if self.check(TokenType.KEYWORD, 'not'):
            self.consume()
            return UnaryExpr('not', self.parse_factor())
        if self.check(TokenType.OP, '&'):
            self.consume()
            return AddressOfExpr(self.parse_factor())
        if self.check(TokenType.OP, '*'):
            self.consume()
            node = DerefExpr(self.parse_factor())
            return self.parse_postfix(node)
            
        # Booleanos
        if self.check(TokenType.KEYWORD, 'true') or self.check(TokenType.KEYWORD, 'false'):
            val = self.consume().value
            return BoolExpr(val == 'true')
            
        # Arrays Literais
        if self.match(TokenType.LBRACKET):
            elements = []
            if not self.check(TokenType.RBRACKET):
                while True:
                    elements.append(self.parse_expression())
                    if not self.match(TokenType.COMMA): break
            self.expect(TokenType.RBRACKET)
            return ArrayExpr(elements)
            
        # Números
        if self.check(TokenType.NUMBER):
            self.consume()
            is_float = '.' in token.value
            return NumberExpr(token.value, is_float)
            
        # F-strings ($"texto {var}")
        if self.check(TokenType.OP, '$') and self.peek() and self.peek().type == TokenType.STRING:
            self.consume() # '$'
            str_token = self.expect(TokenType.STRING)
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
        if self.check(TokenType.STRING):
            self.consume()
            return StringExpr(token.value)
            
        # Comptime
        if self.check(TokenType.KEYWORD, 'comptime'):
            self.consume()
            self.expect(TokenType.LPAREN)
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return ComptimeExpr(expr)
            
        # Match Expression
        if self.check(TokenType.KEYWORD, 'match'):
            return self.parse_match_expr()
            
        # Identificadores, Chamadas de Função e Struct Literals
        if self.check(TokenType.IDENT) or self.check(TokenType.KEYWORD, 'print'):
            name = self.consume().value
            
            # Struct Literal
            if not getattr(self, 'no_struct_literal', False) and self.check(TokenType.LBRACE):
                self.consume() # '{'
                fields = []
                while not self.check(TokenType.RBRACE):
                    if self.match(TokenType.NEWLINE) or self.match(TokenType.INDENT) or self.match(TokenType.DEDENT):
                        continue
                    field_name = self.expect(TokenType.IDENT).value
                    self.expect(TokenType.COLON)
                    field_val = self.parse_expression()
                    fields.append((field_name, field_val))
                    if not self.match(TokenType.COMMA): break
                self.expect(TokenType.RBRACE)
                return StructLiteralExpr(name, fields)
                
            # Chamada de Função
            if self.check(TokenType.LPAREN):
                self.consume()
                args = []
                if not self.check(TokenType.RPAREN):
                    while True:
                        args.append(self.parse_expression())
                        if not self.match(TokenType.COMMA): break
                self.expect(TokenType.RPAREN)
                node = CallExpr(name, args)
            else:
                node = VariableExpr(name, token.line, token.col)
                
            return self.parse_postfix(node)
            
        # Expressões entre parênteses
        if self.match(TokenType.LPAREN):
            node = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return self.parse_postfix(node)
            
        raise LuminaError(
            f"Token inesperado {token.type.name} ('{token.value}')", 
            filename=self.filename, line=token.line, col=token.col, code=self.source_code
        )

    def parse_postfix(self, node):
        while True:
            # Indexação arr[0]
            if self.match(TokenType.LBRACKET):
                # NOVO: Suporte a indexação reversa arr[^1]
                if self.match(TokenType.CARET):
                    index_expr = self.parse_expression()
                    # Simula: arr_len - index_expr
                    len_expr = BinaryExpr('/', node, NumberExpr('0')) # Placeholder para pegar length no codegen
                    index_expr = BinaryExpr('-', len_expr, index_expr)
                else:
                    index_expr = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                node = IndexExpr(node, index_expr)
                
            # Acesso a Membros e Métodos obj.x, obj?.x
            elif self.check(TokenType.OP, '.') or self.check(TokenType.OP, '?.'):
                op = self.consume().value
                member_name = self.expect(TokenType.IDENT).value
                is_safe = (op == '?.')
                
                if self.check(TokenType.LPAREN):
                    self.consume()
                    # CORREÇÃO CRÍTICA: Aqui o 'node' (objeto) DEVE ser o primeiro argumento
                    args = [node]
                    if not self.check(TokenType.RPAREN):
                        while True:
                            args.append(self.parse_expression())
                            if not self.match(TokenType.COMMA): break
                    self.expect(TokenType.RPAREN)
                    node = CallExpr(member_name, args, is_method=True)
                else:
                    node = MemberExpr(node, member_name, is_safe=is_safe)
            else:
                break
            
        # Operador de Propagação de Erros (?)
        if self.match(TokenType.QUESTION):
            node = PropagateExpr(node)
            
        # Casting de Tipos (as)
        if self.check(TokenType.KEYWORD, 'as'):
            self.consume()
            target_type = self.expect(TokenType.IDENT).value
            node = CastExpr(node, target_type)
            
        return node

    def parse_match_expr(self):
        self.consume() # 'match'
        self.no_struct_literal = True
        cond = self.parse_expression()
        self.no_struct_literal = False
        self.expect(TokenType.LBRACE)
        
        cases = []
        default = None
        
        while not self.check(TokenType.RBRACE):
            if self.match(TokenType.NEWLINE) or self.match(TokenType.INDENT) or self.match(TokenType.DEDENT):
                continue
                
            if self.check(TokenType.KEYWORD, 'else'):
                self.consume()
                self.expect(TokenType.FAT_ARROW)
                default = self.parse_expression()
                self.match(TokenType.COMMA)
                continue
            else:
                val = self.parse_expression()
                self.expect(TokenType.FAT_ARROW)
                res = self.parse_expression()
                cases.append((val, res))
                self.match(TokenType.COMMA)
                continue
                
        self.expect(TokenType.RBRACE)
        return MatchExpr(cond, cases, default)