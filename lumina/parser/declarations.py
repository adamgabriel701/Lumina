from ..ast import VarDecl, AssignStmt, Function, StructDecl, ImplBlock, ImportStmt, ExternDecl, EnumDecl, BinaryExpr, VariableExpr, DeferStmt, NumberExpr, AssertStmt
from ..lexer import TokenType

class DeclarationsParser:
    def parse_let(self):
        token = self.current_token()
        is_mutable = (token.value == 'mut')
        self.consume()
        var_name = self.consume(TokenType.IDENT).value
        var_type = None
        if self.current_token().type == TokenType.OP and self.current_token().value == ':':
            self.consume()
            var_type = self.consume(TokenType.IDENT).value
        expr = None
        if self.current_token().type == TokenType.OP and self.current_token().value == '=':
            self.consume()
            expr = self.parse_expression()
        self.consume(TokenType.NEWLINE)
        return VarDecl(var_name, var_type, expr, is_mutable)

    def parse_defer(self):
        self.consume() # 'defer'
        if self.current_token().type == TokenType.OP and self.current_token().value == ':':
            self.consume()
            self.consume(TokenType.NEWLINE)
            self.consume(TokenType.INDENT)
            body = []
            while self.current_token() and self.current_token().type != TokenType.DEDENT:
                if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
                body.append(self.parse_statement())
            self.consume(TokenType.DEDENT)
            return DeferStmt(body)
        else:
            expr = self.parse_expression()
            self.consume(TokenType.NEWLINE)
            return DeferStmt([expr])

    def parse_assert(self):
        self.consume() # 'assert'
        self.consume(TokenType.OP) # '('
        cond = self.parse_expression()
        self.consume(TokenType.OP) # ')'
        self.consume(TokenType.NEWLINE)
        return AssertStmt(cond)

    def parse_test(self):
        self.consume() # 'test'
        test_name = self.consume(TokenType.STRING).value
        self.consume(TokenType.OP) # ':'
        self.consume(TokenType.NEWLINE)
        self.consume(TokenType.INDENT)
        body = []
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
            body.append(self.parse_statement())
        self.consume(TokenType.DEDENT)
        return Function(f"test_{test_name.replace(' ', '_')}", [], "int", body)

    def parse_struct(self):
        self.consume()
        name = self.consume(TokenType.IDENT).value
        self.consume(TokenType.OP)
        self.consume(TokenType.NEWLINE)
        self.consume(TokenType.INDENT)
        fields = {}
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
            field_name = self.consume(TokenType.IDENT).value
            self.consume(TokenType.OP)
            field_type = self.consume(TokenType.IDENT).value
            fields[field_name] = field_type
            self.consume(TokenType.NEWLINE)
        self.consume(TokenType.DEDENT)
        return StructDecl(name, fields)

    def parse_impl(self):
        self.consume()
        struct_name = self.consume(TokenType.IDENT).value
        self.consume(TokenType.OP)
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
        return ImplBlock(struct_name, methods)

    def parse_enum(self):
        self.consume()
        name = self.consume(TokenType.IDENT).value
        self.consume(TokenType.OP)
        self.consume(TokenType.NEWLINE)
        self.consume(TokenType.INDENT)
        
        variants = []
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: 
                self.consume()
                continue
                
            var_name = self.consume(TokenType.IDENT).value
            payload_type = None
            if self.current_token().type == TokenType.OP and self.current_token().value == '(':
                self.consume()
                payload_type = self.consume(TokenType.IDENT).value
                self.consume(TokenType.OP)
                
            variants.append((var_name, payload_type))
            self.consume(TokenType.NEWLINE)
            
        self.consume(TokenType.DEDENT)
        return EnumDecl(name, variants)

    def parse_function(self):
        self.consume(TokenType.KEYWORD)
        name = self.consume(TokenType.IDENT).value
        params = []
        self.consume(TokenType.OP)
        if self.current_token().type != TokenType.OP or self.current_token().value != ')':
            while True:
                p_name = self.consume(TokenType.IDENT).value
                self.consume(TokenType.OP)
                p_type = self.consume(TokenType.IDENT).value
                params.append((p_name, p_type))
                if self.current_token().type == TokenType.OP and self.current_token().value == ',': self.consume()
                else: break
        self.consume(TokenType.OP)
        return_type = "void"
        if self.current_token().type == TokenType.OP and self.current_token().value == '->':
            self.consume()
            return_type = self.consume(TokenType.IDENT).value
        self.consume(TokenType.OP); self.consume(TokenType.NEWLINE); self.consume(TokenType.INDENT)
        body = []
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: self.consume(); continue
            body.append(self.parse_statement())
        self.consume(TokenType.DEDENT)
        return Function(name, params, return_type, body)

    def parse_extern(self):
        self.consume()
        self.consume(TokenType.KEYWORD)
        name = self.consume(TokenType.IDENT).value
        
        params = []
        self.consume(TokenType.OP)
        if self.current_token().type != TokenType.OP or self.current_token().value != ')':
            while True:
                p_name = self.consume(TokenType.IDENT).value
                self.consume(TokenType.OP)
                p_type = self.consume(TokenType.IDENT).value
                params.append((p_name, p_type))
                if self.current_token().type == TokenType.OP and self.current_token().value == ',':
                    self.consume()
                else:
                    break
        self.consume(TokenType.OP)
        
        return_type = "void"
        if self.current_token().type == TokenType.OP and self.current_token().value == '->':
            self.consume()
            return_type = self.consume(TokenType.IDENT).value
            
        self.consume(TokenType.NEWLINE)
        return ExternDecl(name, params, return_type)
