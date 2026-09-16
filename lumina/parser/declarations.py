from lumina.errors import LuminaError

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
        # Atributos já foram lidos em `parse()` e estão em `_pending_attrs`.
        # (parse() consome `@nome` e `@nome(args)` antes de delegar.)
        attrs = getattr(self, '_pending_attrs', []) or []

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
            # Consome NEWLINEs e COMMENTs (comentários dentro da struct)
            self._skip_newlines_and_comments()
            if self.check(TokenType.DEDENT) or self.check(TokenType.EOF):
                break
            self._take_comments()  # descarta por ora
            fn = self.expect(TokenType.IDENT).value
            self.expect(TokenType.COLON)
            ft = self.expect(TokenType.IDENT).value
            fields[fn] = ft
            self.match(TokenType.NEWLINE)
        self.match(TokenType.DEDENT)

        decl = StructDecl(name, fields, type_params)
        if attrs:
            decl.attrs = attrs
        return decl

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
            # Consome NEWLINEs e COMMENTs (comentários dentro do enum)
            self._skip_newlines_and_comments()
            if self.check(TokenType.DEDENT) or self.check(TokenType.EOF):
                break
            if self.check(TokenType.ENUM) or self.check(TokenType.STRUCT) or self.check(TokenType.FN):
                break
            self._take_comments()
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
            # Consome NEWLINEs e COMMENTs (comentários dentro do trait)
            self._skip_newlines_and_comments()
            if self.check(TokenType.DEDENT) or self.check(TokenType.EOF):
                break
            leading = self._take_comments()
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
                        stmt = self.parse_statement()
                        if stmt is not None:
                            body.append(stmt)
                    self.expect(TokenType.DEDENT)
                else:
                    self.match(TokenType.NEWLINE)

                _fn = Function(m_name, params, return_type, body)
                if leading:
                    _fn.leading_comments = leading
                methods.append(_fn)
            else:
                t = self.current_token()
                raise LuminaError(
                    f"Token inesperado em 'trait': {t.type.name} ('{t.value}'). "
                    f"Esperado 'fn' ou 'newline'.",
                    self.filename, t.line, t.col, self.source_code,
                )
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
            self._skip_newlines_and_comments()
            if self.check(TokenType.DEDENT) or self.check(TokenType.EOF):
                break
            leading = self._take_comments()
            if self.check(TokenType.FN):
                func = self.parse_function()

                # Guarda o nome original (antes do mangling) para
                # detectar métodos de operador (__add__, __eq__, ...).
                original_name = func.name
                func.name = f"{struct_name}_{original_name}"

                # Operadores recebem os 2 operandos EXPLICITAMENTE
                # (ex: `fn __add__(a: Vector2, b: Vector2)`).
                # Métodos normais recebem `self` implicitamente.
                is_operator = (
                    original_name.startswith('__') and original_name.endswith('__')
                )
                if not is_operator:
                    func.params.insert(0, Param('self', struct_name))

                if leading:
                    func.leading_comments = leading
                methods.append(func)
            else:
                t = self.current_token()
                raise LuminaError(
                    f"Token inesperado em 'impl': {t.type.name} ('{t.value}'). "
                    f"Esperado 'fn' ou 'newline'.",
                    self.filename, t.line, t.col, self.source_code,
                )
        self.expect(TokenType.DEDENT)
        return ImplBlock(struct_name, methods, trait_name)

    def parse_function(self):
        # Atributos já foram lidos em `parse()` e estão em `_pending_attrs`.
        pending = getattr(self, '_pending_attrs', []) or []
        attrs = [name for (name, _args) in pending]
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
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
        self.expect(TokenType.DEDENT)
        return Function(name, params, return_type, body, type_params, line, col, is_exported, attrs)