from ..lexer.tokens import TokenType
from ..ast import (
    NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, 
    ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, TupleExpr, 
    UnaryExpr, PropagateExpr, ComptimeExpr, StructLiteralExpr, MatchExpr, 
    CastExpr, LambdaExpr,
    VarDecl, DeferStmt, AssertStmt, BenchStmt, StructDecl, ImplBlock, EnumDecl, 
    Function, ExternDecl, TraitDecl, DestructureStmt, AssignStmt, ReturnStmt, 
    IfStmt, WhileStmt, ForStmt, BreakStmt, ContinueStmt, ImportStmt
)
from ..errors import LuminaError

class LuminaParserMixin:
    
    # --- HELPERS ---
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
        raise LuminaError(f"Esperado {expected}, mas encontrei {found}", filename=self.filename, line=t.line if t else 0, col=t.col if t else 0, source_code=self.source_code)

    # --- EXPRESSÕES ---
    def parse_expression(self):
        node = self.parse_logical()
        while self.check(TokenType.PIPE, '|>'):
            self.consume()
            func_name = self.expect(TokenType.IDENT).value
            node = CallExpr(func_name, [node])
        return node

    def parse_logical(self):
        node = self.parse_comparison()
        while self.check(TokenType.AND) or self.check(TokenType.OR):
            op = self.consume().value
            right = self.parse_comparison()
            node = BinaryExpr(op, node, right)
        return node

    def parse_comparison(self):
        node = self.parse_range()
        ops = [TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE]
        while any(self.check(op) for op in ops) or self.check(TokenType.IN):
            op = self.consume().value
            right = self.parse_range()
            node = BinaryExpr(op, node, right)
        return node

    def parse_range(self):
        node = self.parse_additive()
        while self.check(TokenType.DOT):
            self.consume()
            if self.check(TokenType.DOT):
                self.consume()
                right = self.parse_additive()
                node = BinaryExpr('..', node, right)
            else:
                break
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
        if not token: raise LuminaError("Fim inesperado do código", filename=self.filename, line=0, col=0, source_code=self.source_code)
        
        if self.check(TokenType.FN):
            self.consume()
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
            if self.match(TokenType.ARROW): return_type = self.parse_type()
            
            if self.match(TokenType.FAT_ARROW):
                body_expr = self.parse_expression()
                return LambdaExpr(params, return_type, [body_expr])
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
                raise LuminaError("Esperado '=>' ou ':' no corpo do lambda", filename=self.filename, line=token.line, col=token.col, source_code=self.source_code)
            
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
            return BoolExpr(val == 'true')
            
        if self.match(TokenType.LBRACKET):
            elements = []
            if not self.check(TokenType.RBRACKET):
                while True:
                    elements.append(self.parse_expression())
                    if not self.match(TokenType.COMMA): break
            self.expect(TokenType.RBRACKET)
            return ArrayExpr(elements)
            
        if self.check(TokenType.NUMBER):
            self.consume()
            is_float = '.' in token.value
            return NumberExpr(token.value, is_float)
            
        # NOVO: Lida com literais de String diretamente
        if self.check(TokenType.STRING):
            str_token = self.consume()
            return StringExpr(str_token.value)
            
        if self.check(TokenType.IDENT):
            name = self.consume().value
            
            # Struct Literal (ex: Point { x: 10, y: 20 })
            if not getattr(self, 'no_struct_literal', False) and self.check(TokenType.LBRACE):
                self.consume() # '{'
                fields = []
                while not self.check(TokenType.RBRACE):
                    if self.match(TokenType.NEWLINE) or self.match(TokenType.INDENT) or self.match(TokenType.DEDENT): continue
                    field_name = self.expect(TokenType.IDENT).value
                    self.expect(TokenType.COLON)
                    field_val = self.parse_expression()
                    fields.append((field_name, field_val))
                    if not self.match(TokenType.COMMA): break
                self.expect(TokenType.RBRACE)
                return StructLiteralExpr(name, fields)
                
            # Chamada de Função (ex: soma(1, 2) ou print("Hello"))
            if self.check(TokenType.LPAREN):
                self.consume() # '('
                args = []
                if not self.check(TokenType.RPAREN):
                    while True:
                        args.append(self.parse_expression())
                        if not self.match(TokenType.COMMA): break
                self.expect(TokenType.RPAREN)
                # CORREÇÃO: Cria um VariableExpr para o callee
                callee_node = VariableExpr(name, token.line, token.col)
                node = CallExpr(callee_node, args)
            else:
                node = VariableExpr(name, token.line, token.col)
                
            return self.parse_postfix(node)
            
        # NOVO: Lida com expressões entre parênteses, como (1 + 2) ou ("string")
        if self.match(TokenType.LPAREN):
            node = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return self.parse_postfix(node)
            
        raise LuminaError(f"Token inesperado {token.type.name} ('{token.value}')", filename=self.filename, line=token.line, col=token.col, source_code=self.source_code)

    def parse_postfix(self, node):
        while True:
            if self.match(TokenType.LBRACKET):
                index_expr = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                node = IndexExpr(node, index_expr)
            elif self.check(TokenType.DOT):
                self.consume()
                member_name = self.expect(TokenType.IDENT).value
                if self.check(TokenType.LPAREN):
                    self.consume()
                    args = [node]
                    if not self.check(TokenType.RPAREN):
                        while True:
                            args.append(self.parse_expression())
                            if not self.match(TokenType.COMMA): break
                    self.expect(TokenType.RPAREN)
                    node = CallExpr(member_name, args, is_method=True)
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

    # --- DECLARAÇÕES E STATEMENTS ---
    def parse_type(self):
        type_name = self.expect(TokenType.IDENT).value
        if self.check(TokenType.LT):
            self.consume()
            args = [self.parse_type()]
            while self.match(TokenType.COMMA):
                args.append(self.parse_type())
            self.expect(TokenType.GT)
            type_name = type_name + "<" + ",".join(args) + ">"
        return type_name

    def parse_type_params(self):
        self.expect(TokenType.LT)
        params = []
        while True:
            params.append(self.expect(TokenType.IDENT).value)
            if self.match(TokenType.COMMA): continue
            else: break
        self.expect(TokenType.GT)
        return params

    def parse_let(self):
        is_mutable = self.match(TokenType.MUT)
        if self.check(TokenType.LPAREN):
            self.consume()
            names = []
            while True:
                names.append(self.expect(TokenType.IDENT).value)
                if self.match(TokenType.COMMA): continue
                else: break
            self.expect(TokenType.RPAREN)
            self.expect(TokenType.ASSIGN)
            expr = self.parse_expression()
            self.match(TokenType.NEWLINE)
            return DestructureStmt(names, expr, is_mutable)
            
        var_token = self.expect(TokenType.IDENT)
        var_name = var_token.value
        var_line, var_col = var_token.line, var_token.col
        var_type = None
        if self.match(TokenType.COLON): var_type = self.parse_type()
        
        expr = None
        if self.match(TokenType.ASSIGN): expr = self.parse_expression()
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
        self.expect(TokenType.INDENT)
        then_body = []
        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.NEWLINE): continue
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
                self.expect(TokenType.INDENT)
                else_body = []
                while not self.check(TokenType.DEDENT):
                    if self.match(TokenType.NEWLINE): continue
                    else_body.append(self.parse_statement())
                self.expect(TokenType.DEDENT)
        return IfStmt(condition, then_body, else_body)

    def parse_while(self):
        self.consume(TokenType.WHILE)
        condition = self.parse_expression()
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)
        body = []
        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.NEWLINE): continue
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
        first_expr = self.parse_expression()
        if self.check(TokenType.DOT):
            self.consume()
            if self.check(TokenType.DOT):
                self.consume()
                start = first_expr
                end = self.parse_expression()
            else:
                iterable = first_expr
        else:
            iterable = first_expr
            
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)
        body = []
        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.NEWLINE): continue
            body.append(self.parse_statement())
        self.expect(TokenType.DEDENT)
        return ForStmt(var_name, start, end, iterable, body)

    def parse_statement(self):
        token = self.current_token()
        if not token: return None
        
        if token.type == TokenType.LET or token.type == TokenType.MUT: return self.parse_let()
        elif token.type == TokenType.RETURN: return self.parse_return()
        elif token.type == TokenType.IF: return self.parse_if()
        elif token.type == TokenType.WHILE: return self.parse_while()
        elif token.type == TokenType.FOR: return self.parse_for()
        elif token.type == TokenType.BREAK: self.consume(); self.match(TokenType.NEWLINE); return BreakStmt()
        elif token.type == TokenType.CONTINUE: self.consume(); self.match(TokenType.NEWLINE); return ContinueStmt()
        elif token.type == TokenType.IMPORT: return self.parse_import()
        elif token.type == TokenType.EXTERN: return self.parse_extern()
        elif token.type == TokenType.DEFER: return self.parse_defer()
        elif token.type == TokenType.ASSERT: return self.parse_assert()
        elif token.type == TokenType.BENCH: return self.parse_bench()
        elif token.type == TokenType.TEST: return self.parse_test()
        else:
            expr = self.parse_expression()
            if self.check(TokenType.ASSIGN):
                self.consume()
                value = self.parse_expression()
                self.match(TokenType.NEWLINE)
                return AssignStmt(expr, value)
            self.match(TokenType.NEWLINE)
            return expr

    def parse_import(self):
        self.consume(TokenType.IMPORT)
        path = self.expect(TokenType.STRING).value
        self.match(TokenType.NEWLINE)
        return ImportStmt(path)

    def parse_extern(self):
        self.consume(TokenType.EXTERN)
        is_wasm = False
        if self.check(TokenType.STRING):
            if self.consume().value == "wasm": is_wasm = True
        self.expect(TokenType.FN)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.LPAREN)
        params = []
        if not self.check(TokenType.RPAREN):
            while True:
                p_name = self.expect(TokenType.IDENT).value
                self.expect(TokenType.COLON)
                p_type = self.expect(TokenType.IDENT).value
                params.append((p_name, p_type))
                if self.match(TokenType.COMMA): continue
                else: break
        self.expect(TokenType.RPAREN)
        return_type = "void"
        if self.match(TokenType.ARROW): return_type = self.expect(TokenType.IDENT).value
        self.match(TokenType.NEWLINE)
        return ExternDecl(name, params, return_type, is_wasm)

    def parse_defer(self):
        self.consume(TokenType.DEFER)
        if self.match(TokenType.COLON):
            self.expect(TokenType.NEWLINE)
            self.expect(TokenType.INDENT)
            body = []
            while not self.check(TokenType.DEDENT):
                if self.match(TokenType.NEWLINE): continue
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
        self.expect(TokenType.INDENT)
        body = []
        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.NEWLINE): continue
            body.append(self.parse_statement())
        self.expect(TokenType.DEDENT)
        return Function(f"test_{test_name.replace(' ', '_')}", [], "int", body)

    def parse_bench(self):
        self.consume(TokenType.BENCH)
        bench_name = self.expect(TokenType.STRING).value
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)
        body = []
        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.NEWLINE): continue
            body.append(self.parse_statement())
        self.expect(TokenType.DEDENT)
        return BenchStmt(bench_name, body)

    def parse_struct(self):
        self.consume(TokenType.STRUCT)
        name = self.expect(TokenType.IDENT).value
        type_params = self.parse_type_params() if self.check(TokenType.LT) else None
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)
        fields = {}
        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.NEWLINE): continue
            fn = self.expect(TokenType.IDENT).value
            self.expect(TokenType.COLON)
            ft = self.expect(TokenType.IDENT).value
            fields[fn] = ft
            self.match(TokenType.NEWLINE)
        self.expect(TokenType.DEDENT)
        return StructDecl(name, fields, type_params)

    def parse_enum(self):
        self.consume(TokenType.ENUM)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)
        variants = []
        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.NEWLINE): continue
            vn = self.expect(TokenType.IDENT).value
            pt = None
            if self.check(TokenType.LPAREN):
                self.consume()
                pt = self.expect(TokenType.IDENT).value
                self.expect(TokenType.RPAREN)
            variants.append((vn, pt))
            self.match(TokenType.NEWLINE)
        self.expect(TokenType.DEDENT)
        return EnumDecl(name, variants)

    def parse_trait(self):
        self.consume(TokenType.TRAIT)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)
        methods = []
        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.NEWLINE): continue
            if self.check(TokenType.FN):
                self.consume()
                m_name = self.expect(TokenType.IDENT).value
                self.expect(TokenType.LPAREN)
                params = []
                if not self.check(TokenType.RPAREN):
                    while True:
                        p_name = self.expect(TokenType.IDENT).value
                        self.expect(TokenType.COLON)
                        p_type = self.parse_type()
                        params.append((p_name, p_type))
                        if self.match(TokenType.COMMA): continue
                        else: break
                self.expect(TokenType.RPAREN)
                return_type = "void"
                if self.match(TokenType.ARROW): return_type = self.parse_type()
                body = []
                if self.check(TokenType.COLON):
                    self.consume()
                    self.expect(TokenType.NEWLINE)
                    self.expect(TokenType.INDENT)
                    while not self.check(TokenType.DEDENT):
                        if self.match(TokenType.NEWLINE): continue
                        body.append(self.parse_statement())
                    self.expect(TokenType.DEDENT)
                else:
                    self.match(TokenType.NEWLINE)
                methods.append(Function(m_name, params, return_type, body))
        self.expect(TokenType.DEDENT)
        return TraitDecl(name, methods)

    def parse_impl(self):
        self.consume(TokenType.IMPL)
        first_name = self.expect(TokenType.IDENT).value
        trait_name = None
        struct_name = first_name
        
        if self.check(TokenType.FOR): # <--- CORRIGIDO
            trait_name = first_name
            self.consume()
            struct_name = self.expect(TokenType.IDENT).value
            
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)
        methods = []
        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.NEWLINE): continue
            if self.check(TokenType.FN):
                func = self.parse_function()
                func.name = f"{struct_name}_{func.name}"
                methods.append(func)
        self.expect(TokenType.DEDENT)
        return ImplBlock(struct_name, methods, trait_name)

    def parse_function(self):
        attrs = []
        while self.check(TokenType.AT):
            self.consume()
            attr_name = self.expect(TokenType.IDENT).value
            attrs.append(attr_name)
        is_exported = 'export' in attrs
        
        self.expect(TokenType.FN)
        name_token = self.expect(TokenType.IDENT)
        name = name_token.value
        line, col = name_token.line, name_token.col
        type_params = self.parse_type_params() if self.check(TokenType.LT) else None
        
        self.expect(TokenType.LPAREN)
        params = []
        if not self.check(TokenType.RPAREN):
            while True:
                p_name = self.expect(TokenType.IDENT).value
                self.expect(TokenType.COLON)
                p_type = self.parse_type()
                default_val = None
                if self.match(TokenType.ASSIGN): default_val = self.parse_expression()
                params.append((p_name, p_type, default_val))
                if self.match(TokenType.COMMA): continue
                else: break
        self.expect(TokenType.RPAREN)
        
        return_type = "void"
        if self.match(TokenType.ARROW): return_type = self.parse_type()
            
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)
        body = []
        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.NEWLINE): continue
            body.append(self.parse_statement())
        self.expect(TokenType.DEDENT)
        return Function(name, params, return_type, body, type_params, line, col, is_exported, attrs)