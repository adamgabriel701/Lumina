"""Expansão de `@derive(...)`.

  - Eq        → `fn {Struct}___eq__(a, b) -> bool`
  - PartialEq → `__eq__` E `__ne__` (habilita `==` e `!=`)
  - Debug     → `fn {Struct}___debug__(p) -> str`
  - Display   → alias de Debug
  - Clone     → `fn {Struct}_clone(self) -> {Struct}`
  - Default   → `fn new_{Struct}() -> {Struct}` (função livre)

Chamado no topo de `SemanticAnalyzer.analyze`, antes de qualquer
outra análise. Modifica `declarations` in-place, inserindo ImplBlocks
e Functions sintéticas.
"""
from ..ast import (
    Function, Param, ImplBlock,
    AssignStmt, MemberExpr, VariableExpr, ReturnStmt, VarDecl,
    BinaryExpr, CallExpr, IfStmt, BoolExpr, NumberExpr, StringExpr,
    UnaryExpr,
)


class DerivesMixin:

    def _expand_derives(self, declarations):
        """Expande @derive(Eq, Debug, Default, Clone, Display) em
        métodos sintetizados (ImplBlocks) e funções livres.
        """
        new_decls = []
        for decl in declarations:
            attrs = getattr(decl, 'attrs', None)
            if not attrs:
                continue
            if not hasattr(decl, 'fields'):
                continue  # só struct

            struct_name = decl.name
            methods = []   # métodos → ImplBlock
            free_fns = []  # funções livres → Function

            # Coleta todos os derives do @derive(...)
            derives = set()
            for attr_name, attr_args in attrs:
                if attr_name != 'derive':
                    continue
                for deriv in attr_args:
                    derives.add(deriv)

            # NOTA: `PartialEq` gera __eq__ E __ne__ (equivalente ao `==`
            # e `!=`). `Eq` gera apenas __eq__ (Rust-style: Eq é um
            # marcador que requer PartialEq, mas em Lumina simplificamos
            # para "só igualdade").
            if 'Eq' in derives or 'PartialEq' in derives:
                methods.append(self._gen_eq(struct_name, decl))
            if 'PartialEq' in derives:
                methods.append(self._gen_ne(struct_name, decl))
            if 'Debug' in derives or 'Display' in derives:
                methods.append(self._gen_debug(struct_name, decl))
            if 'Clone' in derives:
                methods.append(self._gen_clone(struct_name, decl))
            if 'Default' in derives:
                free_fns.append(self._gen_default(struct_name, decl))

            if methods:
                new_decls.append(ImplBlock(struct_name, methods))
            new_decls.extend(free_fns)

        declarations.extend(new_decls)

    def _gen_eq(self, struct_name, struct_decl):
        """Gera: fn {Struct}___eq__(a, b) -> bool

        Nome mangled porque o codegen procura `{Struct}___eq__`.
        Retorna `bool` (i1) para que `print(p1 == p2)` mostre
        `true`/`false`.
        """
        a_var = VariableExpr('a', 0, 0)
        b_var = VariableExpr('b', 0, 0)

        # Compara cada campo: a.f1 == b.f1 and a.f2 == b.f2 and ...
        conditions = []
        for fname in struct_decl.fields.keys():
            a_field = MemberExpr(a_var, fname)
            b_field = MemberExpr(b_var, fname)
            conditions.append(BinaryExpr('==', a_field, b_field))

        if not conditions:
            cond = BoolExpr(True)  # struct vazia: sempre igual
        elif len(conditions) == 1:
            cond = conditions[0]
        else:
            cond = conditions[0]
            for c in conditions[1:]:
                cond = BinaryExpr('and', cond, c)

        then_body = [ReturnStmt([BoolExpr(True)])]
        if_stmt = IfStmt(cond, then_body, None)
        return_stmt = ReturnStmt([BoolExpr(False)])

        mangled_name = f"{struct_name}___eq__"

        return Function(
            mangled_name,
            [Param('a', struct_name), Param('b', struct_name)],
            'bool',
            [if_stmt, return_stmt],
        )

    def _gen_ne(self, struct_name, struct_decl):
        """Gera: fn {Struct}___ne__(a, b) -> bool

        Uso: `a != b`
        """
        a_var = VariableExpr('a', 0, 0)
        b_var = VariableExpr('b', 0, 0)

        # Chama __eq__(a, b)
        eq_callee = VariableExpr(f'{struct_name}___eq__', 0, 0)
        eq_call = CallExpr(eq_callee, [a_var, b_var])

        # if not __eq__(a, b): return True
        not_eq = UnaryExpr('not', eq_call)
        then_body = [ReturnStmt([BoolExpr(True)])]
        if_stmt = IfStmt(not_eq, then_body, None)

        # return False
        return_stmt = ReturnStmt([BoolExpr(False)])

        mangled_name = f"{struct_name}___ne__"

        return Function(
            mangled_name,
            [Param('a', struct_name), Param('b', struct_name)],
            'bool',
            [if_stmt, return_stmt],
        )

    def _gen_debug(self, struct_name, struct_decl):
        """Gera: fn {Struct}___debug__(p: Struct) -> str

        Nome já mangled porque o codegen procura `{Struct}___debug__`.
        """
        p_var = VariableExpr('p', 0, 0)
        parts = [StringExpr(f"{struct_name} {{ ")]

        for i, fname in enumerate(struct_decl.fields.keys()):
            if i > 0:
                parts.append(StringExpr(", "))
            parts.append(StringExpr(f"{fname}: "))
            field_access = MemberExpr(p_var, fname)
            parts.append(field_access)

        parts.append(StringExpr(" }"))

        # Concatenação: "P1" + v1 + "P2" + v2 ...
        expr = parts[0]
        for p in parts[1:]:
            expr = BinaryExpr('+', expr, p)

        mangled_name = f"{struct_name}___debug__"

        return Function(
            mangled_name,
            [Param('p', struct_name)],
            'str',
            [ReturnStmt([expr])],
        )

    def _gen_clone(self, struct_name, struct_decl):
        """Gera: fn {Struct}_clone(self) -> {Struct}

        Uso: `let copia = p.clone()`
        Nome mangled porque o `codegen_method_call` procura por
        `Struct_clone`.
        """
        result_var = 'result'
        result_decl = VarDecl(result_var, struct_name, None, True)

        body = [result_decl]
        self_var = VariableExpr('self', 0, 0)
        result_ref = VariableExpr(result_var, 0, 0)

        # result.f1 = self.f1 ; result.f2 = self.f2 ; ...
        for fname in struct_decl.fields.keys():
            lhs = MemberExpr(result_ref, fname)
            rhs = MemberExpr(self_var, fname)
            body.append(AssignStmt(lhs, rhs))

        body.append(ReturnStmt([VariableExpr(result_var, 0, 0)]))

        mangled_name = f"{struct_name}_clone"
        return Function(mangled_name, [Param('self', struct_name)], struct_name, body)

    def _gen_default(self, struct_name, struct_decl):
        """Gera: fn new_{Struct}() -> {Struct} com todos os campos
        zerados (0 / 0.0 / false / "" / null).

        Uso: `let p = new_Ponto()`
        """
        result_var = 'result'
        result_decl = VarDecl(result_var, struct_name, None, True)

        body = [result_decl]
        result_ref = VariableExpr(result_var, 0, 0)

        for fname, ftype in struct_decl.fields.items():
            lhs = MemberExpr(result_ref, fname)

            # Valor zero por tipo
            if ftype == "float":
                rhs = NumberExpr("0.0", is_float=True)
            elif ftype == "bool":
                rhs = BoolExpr(False)
            elif ftype == "str":
                rhs = StringExpr("")
            else:
                rhs = NumberExpr("0", is_float=False)

            body.append(AssignStmt(lhs, rhs))

        body.append(ReturnStmt([VariableExpr(result_var, 0, 0)]))

        return Function(f"new_{struct_name}", [], struct_name, body)
