from ..ast import VarDecl, DeferStmt, AssertStmt, BenchStmt, StructDecl, ImplBlock, EnumDecl, Function, ExternDecl, TraitDecl, DestructureStmt
from ..lexer import TokenType

class DeclarationsParser:
    def parse_type_params(self):
        self.consume() # '<'
        params = []
        while True:
            params.append(self.consume(TokenType.IDENT).value)
            if self.current_token().type == TokenType.OP and self.current_token().value == ',':
                self.consume()
            else:
                break
        self.consume(TokenType.OP) # '>'
        return params

    def parse_type(self):
        type_name = self.consume(TokenType.IDENT).value
        if self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '<':
            self.consume()
            args = [self.parse_type()]
            while self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == ',':
                self.consume(); args.append(self.parse_type())
            self.consume(TokenType.OP)
            type_name = type_name + "<" + ",".join(args) + ">"
        return type_name

    def parse_let(self):
        is_mutable = (self.consume().value == 'mut')
        
        # Destructuring: let (x, y) = expr
        if self.current_token().type == TokenType.OP and self.current_token().value == '(':
            self.consume()
            names = []
            while True:
                names.append(self.consume(TokenType.IDENT).value)
                if self.current_token().type == TokenType.OP and self.current_token().value == ',': self.consume()
                else: break
            self.consume(TokenType.OP); self.consume(TokenType.OP)
            expr = self.parse_expression()
            if self.current_token() and self.current_token().type == TokenType.NEWLINE: self.consume()
            return DestructureStmt(names, expr, is_mutable)
            
        # Declaração normal: let x = expr
        var_token = self.consume(TokenType.IDENT)
        var_name = var_token.value
        var_line, var_col = var_token.line, var_token.col
        var_type = None
        if self.current_token().type == TokenType.OP and self.current_token().value == ':':
            self.consume(); var_type = self.parse_type()
            
        expr = None
        if self.current_token().type == TokenType.OP and self.current_token().value == '=':
            self.consume()
            expr = self.parse_expression()
            
        if self.current_token() and self.current_token().type == TokenType.NEWLINE:
            self.consume(TokenType.NEWLINE)
            
        return VarDecl(var_name, var_type, expr, is_mutable, var_line, var_col)

    def parse_defer(self):
        is_errdefer = False
        if self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'errdefer':
            self.consume()
            is_errdefer = True
        else:
            self.consume() # 'defer'
            
        if self.current_token().type == TokenType.OP and self.current_token().value == ':':
            self.consume(); self.consume(TokenType.NEWLINE); self.consume(TokenType.INDENT)
            body = []
            while self.current_token() and self.current_token().type != TokenType.DEDENT:
                if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
                body.append(self.parse_statement())
            self.consume(TokenType.DEDENT)
            return DeferStmt(body, is_errdefer)
        expr = self.parse_expression(); self.consume(TokenType.NEWLINE)
        return DeferStmt([expr], is_errdefer)

    def parse_assert(self):
        self.consume(); self.consume(TokenType.OP)
        cond = self.parse_expression(); self.consume(TokenType.OP); self.consume(TokenType.NEWLINE)
        return AssertStmt(cond)

    def parse_test(self):
        self.consume()
        test_name = self.consume(TokenType.STRING).value
        self.consume(TokenType.OP); self.consume(TokenType.NEWLINE); self.consume(TokenType.INDENT)
        body = []
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
            body.append(self.parse_statement())
        self.consume(TokenType.DEDENT)
        return Function(f"test_{test_name.replace(' ', '_')}", [], "int", body)

    def parse_bench(self):
        self.consume()
        bench_name = self.consume(TokenType.STRING).value
        self.consume(TokenType.OP); self.consume(TokenType.NEWLINE); self.consume(TokenType.INDENT)
        body = []
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
            body.append(self.parse_statement())
        self.consume(TokenType.DEDENT)
        return BenchStmt(bench_name, body)

    def parse_struct(self):
        self.consume()
        name = self.consume(TokenType.IDENT).value
        type_params = self.parse_type_params() if self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '<' else None
        self.consume(TokenType.OP); self.consume(TokenType.NEWLINE); self.consume(TokenType.INDENT)
        fields = {}
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
            fn = self.consume(TokenType.IDENT).value; self.consume(TokenType.OP)
            ft = self.consume(TokenType.IDENT).value; fields[fn] = ft; self.consume(TokenType.NEWLINE)
        self.consume(TokenType.DEDENT)
        return StructDecl(name, fields, type_params)

    def parse_impl(self):
        self.consume() # 'impl'
        
        first_name = self.consume(TokenType.IDENT).value
        trait_name = None
        struct_name = first_name
        
        if self.current_token() and self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'for':
            trait_name = first_name
            self.consume() # 'for'
            struct_name = self.consume(TokenType.IDENT).value
            
        self.consume(TokenType.OP) # ':'
        self.consume(TokenType.NEWLINE)
        self.consume(TokenType.INDENT)
        methods = []
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
            if self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'fn':
                func = self.parse_function()
                func.name = f"{struct_name}_{func.name}"
                methods.append(func)
        self.consume(TokenType.DEDENT)
        return ImplBlock(struct_name, methods, trait_name)

    def parse_enum(self):
        self.consume()
        name = self.consume(TokenType.IDENT).value
        self.consume(TokenType.OP); self.consume(TokenType.NEWLINE); self.consume(TokenType.INDENT)
        variants = []
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
            vn = self.consume(TokenType.IDENT).value
            pt = None
            if self.current_token().type == TokenType.OP and self.current_token().value == '(':
                self.consume(); pt = self.consume(TokenType.IDENT).value; self.consume(TokenType.OP)
            variants.append((vn, pt)); self.consume(TokenType.NEWLINE)
        self.consume(TokenType.DEDENT)
        return EnumDecl(name, variants)

    def parse_function(self):
        # NOVO: Lê atributos (@inline, @export)
        attrs = []
        while self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '@':
            self.consume()
            attr_name = self.consume(TokenType.IDENT).value
            attrs.append(attr_name)
            
        is_exported = False
        if 'export' in attrs:
            is_exported = True
            
        fn_token = self.consume(TokenType.KEYWORD) # 'fn'
        name_token = self.consume(TokenType.IDENT)
        name = name_token.value
        line, col = name_token.line, name_token.col
        type_params = self.parse_type_params() if self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '<' else None
        params = []
        self.consume(TokenType.OP)
        if self.current_token().type != TokenType.OP or self.current_token().value != ')':
            while True:
                p_name = self.consume(TokenType.IDENT).value; self.consume(TokenType.OP)
                p_type = self.parse_type()
                default_val = None
                if self.current_token().type == TokenType.OP and self.current_token().value == '=':
                    self.consume(); default_val = self.parse_expression()
                params.append((p_name, p_type, default_val))
                if self.current_token().type == TokenType.OP and self.current_token().value == ',': self.consume()
                else: break
        self.consume(TokenType.OP)
        return_type = "void"
        if self.current_token().type == TokenType.OP and self.current_token().value == '->':
            self.consume(); return_type = self.parse_type()
        self.consume(TokenType.OP); self.consume(TokenType.NEWLINE); self.consume(TokenType.INDENT)
        body = []
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
            body.append(self.parse_statement())
        self.consume(TokenType.DEDENT)
        return Function(name, params, return_type, body, type_params, line, col, is_exported, attrs)

    def parse_extern(self):
        self.consume() # 'extern'
        
        is_wasm = False
        if self.current_token() and self.current_token().type == TokenType.STRING:
            if self.consume().value == "wasm":
                is_wasm = True
                
        self.consume(TokenType.KEYWORD) # 'fn'
        name = self.consume(TokenType.IDENT).value
        params = []
        self.consume(TokenType.OP)
        if self.current_token().type != TokenType.OP or self.current_token().value != ')':
            while True:
                p_name = self.consume(TokenType.IDENT).value; self.consume(TokenType.OP)
                p_type = self.consume(TokenType.IDENT).value
                params.append((p_name, p_type))
                if self.current_token().type == TokenType.OP and self.current_token().value == ',': self.consume()
                else: break
        self.consume(TokenType.OP)
        return_type = "void"
        if self.current_token().type == TokenType.OP and self.current_token().value == '->':
            self.consume(); return_type = self.consume(TokenType.IDENT).value
        self.consume(TokenType.NEWLINE)
        return ExternDecl(name, params, return_type, is_wasm)

    def parse_trait(self):
        self.consume() # 'trait'
        name = self.consume(TokenType.IDENT).value
        self.consume(TokenType.OP); self.consume(TokenType.NEWLINE); self.consume(TokenType.INDENT)
        methods = []
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
            if self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'fn':
                self.consume(); m_name = self.consume(TokenType.IDENT).value
                self.consume(TokenType.OP); params = []
                if self.current_token().type != TokenType.OP or self.current_token().value != ')':
                    while True:
                        p_name = self.consume(TokenType.IDENT).value; self.consume(TokenType.OP)
                        p_type = self.parse_type(); params.append((p_name, p_type))
                        if self.current_token().type == TokenType.OP and self.current_token().value == ',': self.consume()
                        else: break
                self.consume(TokenType.OP)
                return_type = "void"
                if self.current_token().type == TokenType.OP and self.current_token().value == '->':
                    self.consume(); return_type = self.parse_type()
                
                # NOVO: Verifica se tem corpo (método padrão) ou apenas assinatura
                body = []
                if self.current_token().type == TokenType.OP and self.current_token().value == ':':
                    self.consume(); self.consume(TokenType.NEWLINE); self.consume(TokenType.INDENT)
                    while self.current_token() and self.current_token().type != TokenType.DEDENT:
                        if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
                        body.append(self.parse_statement())
                    self.consume(TokenType.DEDENT)
                else:
                    self.consume(TokenType.NEWLINE)
                    
                methods.append(Function(m_name, params, return_type, body))
        self.consume(TokenType.DEDENT)
        return TraitDecl(name, methods)