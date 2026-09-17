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
            self._skip_newlines_and_comments()
            if self.check(TokenType.DEDENT) or self.check(TokenType.EOF):
                break
            self._take_comments()
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
        """Parseia `impl <Tipo>:` ou `impl <Trait> for <Tipo>:`.

        Suporta tipos genéricos:
          - `impl Box<T>:`         → struct_name = "Box"
          - `impl Vector<T>:`      → struct_name = "Vector"
          - `impl Greeter for English:`  → trait_name = "Greeter", struct = "English"

        O `<T>` é descartado porque o codegen sempre registra os métodos
        com o nome base (`Box_get`, `Vector_push`, ...). Chamadas via
        `b.get()` em `Box<int>` são resolvidas em `codegen_method_call`
        tentando o nome exato primeiro, depois o base.
        """
        self.consume(TokenType.IMPL)
        first_type = self.parse_type()
        trait_name = None
        struct_name = first_type
        if self.check(TokenType.FOR):
            trait_name = first_type
            self.consume()
            struct_name = self.parse_type()
        # Descarta args genéricos do nome para registro.
        if "<" in struct_name:
            struct_name = struct_name.split("<")[0]
        if trait_name and "<" in trait_name:
            trait_name = trait_name.split("<")[0]

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

                original_name = func.name
                func.name = f"{struct_name}_{original_name}"

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