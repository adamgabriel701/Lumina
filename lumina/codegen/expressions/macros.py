"""Expansão de macros (@macro) em compile-time.

Uma macro é uma Function com attr 'macro'. Seu corpo deve ser
UM único ReturnStmt cujo values[0] é uma expressão. No call site,
o codegen substitui VariableExpr(param) pelo arg AST e visita.

Sem statement expansion (if/while/etc.) — só expressões. Multi-
statement macros ficam para uma sprint futura.
"""
import copy

from ...ast import (
    VariableExpr, BinaryExpr, UnaryExpr, CallExpr, MemberExpr,
    IndexExpr, SliceExpr, CastExpr, AddressOfExpr, DerefExpr,
    StructLiteralExpr, NumberExpr, StringExpr, BoolExpr,
    NoneExpr, NilExpr, LambdaExpr, PropagateExpr, ComptimeExpr,
    InterpolatedStringExpr, ArrayExpr, MatchExpr, StructLiteralField,
)


class MacrosMixin:

    def _is_macro(self, name):
        return name in getattr(self, 'macros', {})

    def _expand_macro_expr(self, macro_fn, arg_nodes):
        """Expande macro_fn com os args. Retorna Expr substituído."""
        params = macro_fn.params

        if len(arg_nodes) != len(params):
            from ...errors import LuminaError
            raise LuminaError(
                f"Macro '{macro_fn.name}' espera {len(params)} args, "
                f"recebeu {len(arg_nodes)}.",
                self.filename if hasattr(self, 'filename') else '<repl>',
                getattr(macro_fn, 'line', 0), getattr(macro_fn, 'col', 0), '',
            )

        # Corpo precisa ser 1 ReturnStmt
        body = macro_fn.body
        return_stmts = [s for s in body if type(s).__name__ == 'ReturnStmt']
        if len(body) != 1 or not return_stmts or not return_stmts[0].values:
            from ...errors import LuminaError
            raise LuminaError(
                f"Macro '{macro_fn.name}' deve ter corpo `return <expr>` "
                f"(um único statement). Macros multi-statement não são "
                f"suportadas.",
                self.filename if hasattr(self, 'filename') else '<repl>',
                getattr(macro_fn, 'line', 0), getattr(macro_fn, 'col', 0), '',
            )

        expr = return_stmts[0].values[0]

        # mapping param_name → arg AST
        mapping = {p.name: arg for p, arg in zip(params, arg_nodes)}

        return self._substitute_in_expr(expr, mapping)

    def _substitute_in_expr(self, expr, mapping):
        """Deep-copy de `expr` com VariableExpr(name) → mapping[name]."""
        if isinstance(expr, VariableExpr):
            if expr.name in mapping:
                return copy.deepcopy(mapping[expr.name])
            return copy.deepcopy(expr)

        # Folhas
        if isinstance(expr, (NumberExpr, StringExpr, BoolExpr,
                             NoneExpr, NilExpr)):
            return copy.deepcopy(expr)

        # Binários
        if isinstance(expr, BinaryExpr):
            return BinaryExpr(
                expr.op,
                self._substitute_in_expr(expr.left, mapping),
                self._substitute_in_expr(expr.right, mapping),
            )

        # Unários
        if isinstance(expr, UnaryExpr):
            return UnaryExpr(
                expr.op,
                self._substitute_in_expr(expr.val, mapping),
            )

        # Chamadas
        if isinstance(expr, CallExpr):
            return CallExpr(
                self._substitute_in_expr(expr.callee, mapping),
                [self._substitute_in_expr(a, mapping) for a in expr.args],
                expr.is_method,
            )

        # Membros
        if isinstance(expr, MemberExpr):
            return MemberExpr(
                self._substitute_in_expr(expr.obj, mapping),
                expr.member,
                expr.is_safe,
            )

        # Index
        if isinstance(expr, IndexExpr):
            return IndexExpr(
                self._substitute_in_expr(expr.array, mapping),
                self._substitute_in_expr(expr.index, mapping),
            )

        # Slice
        if isinstance(expr, SliceExpr):
            return SliceExpr(
                self._substitute_in_expr(expr.array, mapping),
                self._substitute_in_expr(expr.start, mapping) if expr.start else None,
                self._substitute_in_expr(expr.end, mapping) if expr.end else None,
            )

        # Cast
        if isinstance(expr, CastExpr):
            return CastExpr(
                self._substitute_in_expr(expr.expr, mapping),
                expr.target_type,
            )

        # Ptr
        if isinstance(expr, AddressOfExpr):
            return AddressOfExpr(self._substitute_in_expr(expr.val, mapping))

        if isinstance(expr, DerefExpr):
            return DerefExpr(self._substitute_in_expr(expr.val, mapping))

        if isinstance(expr, PropagateExpr):
            return PropagateExpr(self._substitute_in_expr(expr.val, mapping))

        # Struct literal
        if isinstance(expr, StructLiteralExpr):
            new_fields = [
                StructLiteralField(
                    f.name,
                    self._substitute_in_expr(f.value, mapping),
                )
                for f in expr.fields
            ]
            return StructLiteralExpr(expr.struct_name, new_fields)

        # Array literal
        if isinstance(expr, ArrayExpr):
            return ArrayExpr(
                [self._substitute_in_expr(e, mapping) for e in expr.elements]
            )

        # Interpolação
        if isinstance(expr, InterpolatedStringExpr):
            return InterpolatedStringExpr(
                [self._substitute_in_expr(e, mapping) for e in expr.parts]
            )

        # Comptime
        if isinstance(expr, ComptimeExpr):
            inner = self._substitute_in_expr(expr.expr, mapping)
            return ComptimeExpr(inner)

        # Fallback: deepcopy sem substituição
        # (cobre LambdaExpr, MatchExpr, etc. — não esperados em macros
        # por enquanto)
        return copy.deepcopy(expr)
