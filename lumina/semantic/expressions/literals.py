"""Literais e acessos: Number, Bool, String, None, Nil, Variable,
Member, Index, Slice, Cast.
"""
from ...ast import (
    NumberExpr, BoolExpr, StringExpr, NoneExpr, NilExpr,
    VariableExpr, MemberExpr, IndexExpr, SliceExpr, CastExpr,
)
from ...errors import LuminaError
from .helpers import get_suggestion


class LiteralsMixin:

    def visit_NumberExpr(self, node):
        return "int" if not node.is_float else "float"

    def visit_BoolExpr(self, node):
        return "bool"

    def visit_StringExpr(self, node):
        return "str"

    def visit_NoneExpr(self, node):
        # `none` tem tipo Option (sem args). O tipo concreto
        # (Option<int>, ...) é inferido pelo contexto via is_assignable.
        return "Option"

    def visit_NilExpr(self, node):
        # `nil` é null pointer — tipo "nil" que is_assignable
        # aceita para ptr/str/fn/struct.
        return "nil"

    def visit_VariableExpr(self, node):
        info = self.get_var_info(node.name)
        if not info:
            # Variante sem payload (ex: `Red`, `Stop`) → constrói.
            enum_name = self._find_enum_of_variant(
                node.name, require_no_payload=True
            )
            if enum_name is not None:
                return enum_name

            # Variante COM payload usada bare (ex: `Some`) → erro.
            if node.name in self.functions:
                if self._find_enum_of_variant(node.name) is not None:
                    raise LuminaError(
                        f"Variante '{node.name}' espera payload. "
                        f"Use `{node.name}(...)`.",
                        self.filename, node.line, node.col, self.source_code,
                    )
                # Nome de função usado como valor (fn pointer).
                return "fn"

            available_vars = [k for scope in self.scopes for k in scope.keys()]
            suggestion = get_suggestion(node.name, available_vars)
            msg = f"Variável '{node.name}' não declarada."
            if suggestion:
                msg += f" Você quis dizer '{suggestion}'?"
            raise LuminaError(
                msg, self.filename, node.line, node.col, self.source_code,
            )
        return info['type']

    def visit_MemberExpr(self, node):
        current_type = self.visit(node.obj)
        base_type = current_type.split('<')[0] if current_type else "Unknown"

        if base_type not in self.struct_defs:
            raise LuminaError(
                f"Tipo '{current_type}' não é uma Struct/Enum ou não possui membros.",
                self.filename, getattr(node, 'line', 0),
                getattr(node, 'col', 0), self.source_code,
            )

        struct_def = self.struct_defs[base_type]

        if hasattr(struct_def, 'fields') and node.member in struct_def.fields:
            return struct_def.fields[node.member]
        elif (hasattr(struct_def, 'variants')
              and any(v[0] == node.member for v in struct_def.variants)):
            return base_type
        else:
            raise LuminaError(
                f"Campo '{node.member}' não existe na Struct/Enum '{current_type}'.",
                self.filename, getattr(node, 'line', 0),
                getattr(node, 'col', 0), self.source_code,
            )

    def visit_IndexExpr(self, node):
        self.visit(node.array)
        self.visit(node.index)
        return None

    def visit_SliceExpr(self, node):
        arr_type = self.visit(node.array)
        if node.start:
            self.visit(node.start)
        if node.end:
            self.visit(node.end)
        # Slice de str → str; slice de array → ptr.
        if arr_type == "str":
            return "str"
        return "ptr"

    def visit_CastExpr(self, node):
        self.visit(node.expr)
        if node.target_type not in ("int", "float", "bool", "str", "ptr"):
            base = node.target_type.split('<')[0]
            if base not in self.structs:
                raise LuminaError(
                    f"Tipo de destino '{node.target_type}' não declarado.",
                    self.filename, getattr(node, 'line', 0),
                    getattr(node, 'col', 0), self.source_code,
                )
        return node.target_type
