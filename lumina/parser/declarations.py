from .statements import StatementParser
from ..lexer.tokens import TokenType
from ..ast import (
    Function, StructDecl, EnumDecl, TraitDecl, ImplBlock, ExternDecl,
    ImportStmt, Param,
)


class DeclarationParser(StatementParser):
    """Declarações de topo: fn, struct, enum, trait, impl, import, extern."""

    def parse_import(self):
        self.consume(TokenType.IMPORT)
        path = self.expect(TokenType.STRING).value
        self.match(TokenType.NEWLINE)
        return ImportStmt(path)

    def parse_extern(self):
        self.consume(TokenType.EXTERN)
        is_wasm = False
        if self.check(TokenType.STRING):
            if self.consume().value == "wasm":
                is_wasm = True
        self.expect(TokenType.FN)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.LPAREN)
        params = []
        if not self.check(TokenType.RPAREN):
            while True:
                p_name = self.expect(TokenType.IDENT).value
                self.expect(TokenType.COLON)
                p_type = self.expect(TokenType.IDENT).value
                params.append(Param(p_name, p_type))
                if self.match(TokenType.COMMA):
                    continue
                else:
                    break
        self.expect(TokenType.RPAREN)
        return_type = "void"
        if self.match(TokenType.ARROW):
            return_type = self.expect(TokenType.IDENT).value
        self.match(TokenType.NEWLINE)
        return ExternDecl(name, params, return_type, is_wasm)

    def parse_struct(self):
        self.consume(TokenType.STRUCT)
        name = self.expect(TokenType.IDENT).value
        type_params = self.parse_type_params() if self.check(TokenType.LT) else None
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        while self.check(TokenType.NEWLINE):
            self.consume()
        self.expect(TokenType.INDENT)
        fields = {}
        while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                continue
            fn = self.expect(TokenType.IDENT).value
            self.expect(TokenType.COLON)
            ft = self.expect(TokenType.IDENT).value
            fields[fn] = ft
            self.match(TokenType.NEWLINE)
        self.match(TokenType.DEDENT)
        return StructDecl(name, fields, type_params)

    def parse_enum(self):
        self.consume(TokenType.ENUM)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        while self.check(TokenType.NEWLINE):
            self.consume()
        self.expect(TokenType.INDENT)
        variants = []
        while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                continue
            if self.check(TokenType.ENUM) or self.check(TokenType.STRUCT) or self.check(TokenType.FN):
                break
            vn = self.expect(TokenType.IDENT).value
            payloads = []
            if self.check(TokenType.LPAREN):
                self.consume()
                while True:
                    payloads.append(self.parse_type())
                    if not self.match(TokenType.COMMA):
                        break
                self.expect(TokenType.RPAREN)
            variants.append((vn, payloads))
            self.match(TokenType.NEWLINE)
        self.match(TokenType.DEDENT)
        return EnumDecl(name, variants)

    def parse_trait(self):
        self.consume(TokenType.TRAIT)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        while self.check(TokenType.NEWLINE):
            self.consume()
        self.expect(TokenType.INDENT)
        methods = []
        while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                continue
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
                        params.append(Param(p_name, p_type))
                        if self.match(TokenType.COMMA):
                            continue
                        else:
                            break
                self.expect(TokenType.RPAREN)
                return_type = "void"
                if self.match(TokenType.ARROW):
                    return_type = self.parse_type()
                body = []
                if self.check(TokenType.COLON):
                    self.consume()
                    self.expect(TokenType.NEWLINE)
                    while self.check(TokenType.NEWLINE):
                        self.consume()
                    self.expect(TokenType.INDENT)
                    while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
                        if self.match(TokenType.NEWLINE):
                            continue
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
        if self.check(TokenType.FOR):
            trait_name = first_name
            self.consume()
            struct_name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        while self.check(TokenType.NEWLINE):
            self.consume()
        self.expect(TokenType.INDENT)
        methods = []
        while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                continue
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
                if self.match(TokenType.ASSIGN):
                    default_val = self.parse_expression()
                params.append(Param(p_name, p_type, default_val))
                if self.match(TokenType.COMMA):
                    continue
                else:
                    break
        self.expect(TokenType.RPAREN)
        return_type = "void"
        if self.match(TokenType.ARROW):
            return_type = self.parse_type()
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
        return Function(name, params, return_type, body, type_params, line, col, is_exported, attrs)
