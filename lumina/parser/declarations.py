from lumina.errors import LuminaError

from .statements import StatementParser
from ..lexer.tokens import TokenType
from ..ast import (
    Function, StructDecl, EnumDecl, TraitDecl, ImplBlock, ExternDecl,
    ImportStmt, Param, TypeAlias,
)
from ..common.mangle import mangle_method


class DeclarationParser(StatementParser):
    """Declarações de topo: fn, struct, enum, trait, impl, import, extern."""

    def parse_import(self):
        self.consume(TokenType.IMPORT)
        path = self.expect(TokenType.STRING).value
        self.match(TokenType.NEWLINE)
        return ImportStmt(path)

    def parse_type_alias(self):
        """`type Nome[<T1, T2>] = <tipo>` no top level."""
        self.consume(TokenType.TYPE)
        name = self.expect(TokenType.IDENT).value
        type_params = None
        if self.check(TokenType.LT):
            type_params = self.parse_type_params()
        self.expect(TokenType.ASSIGN)
        target = self.parse_type()
        self.match(TokenType.NEWLINE)
        return TypeAlias(name, target, type_params)

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
            ft = self.parse_type()
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
        type_params = None
        if self.check(TokenType.LT):
            type_params = self.parse_type_params()
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
        return EnumDecl(name, variants, type_params)

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

        O `<Tipo>` é preservado completo (ex: `Box<int>`, `Box<T>`) para que
        o semantic possa registrar especializações distintas de um mesmo
        método (`Box_int__greet` vs `Box_str__greet`). O codegen resolve
        `b.greet()` tentando o nome exato primeiro, depois o base.
        """
        self.consume(TokenType.IMPL)
        first_type = self.parse_type()
        trait_name = None
        struct_name = first_type
        if self.check(TokenType.FOR):
            trait_name = first_type
            self.consume()
            struct_name = self.parse_type()

        # NOVO: normaliza `impl Box<T>:` → nome base `Box` (fallback).
        # `impl Getter for Box<int>:` mantém `Box<int>` (especialização).
        # Regra: se TODOS os args do target são type params (letras únicas
        # maiúsculas separadas por vírgula), stripamos o `<...>`.
        if struct_name and "<" in struct_name:
            args_inner = struct_name.split("<", 1)[1].rstrip(">")
            args_list = [a.strip() for a in args_inner.split(",")]
            if args_list and all(
                len(a) == 1 and a.isupper() for a in args_list
            ):
                struct_name = struct_name.split("<")[0]

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
                # Mangling canônico: `Box<int>` → `Box_int_`, então
                # `Box_int__greet`. Métodos com `<T>` genérico ficam sem
                # sufixo de args (`Box_greet`), servindo de base fallback.
                func.name = mangle_method(struct_name, original_name)

                is_operator = (
                    original_name.startswith('__') and original_name.endswith('__')
                )
                if not is_operator:
                    # `self` recebe o tipo completo (Box<int>) para que o
                    # codegen use o LLVM type correto.
                    self_type = struct_name if "<" in struct_name else struct_name
                    func.params.insert(0, Param('self', self_type))

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