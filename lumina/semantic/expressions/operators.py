"""Operadores: binário, unário, endereço, deref, propagação de erro."""
from ...ast import (
    BinaryExpr, UnaryExpr, AddressOfExpr, DerefExpr, PropagateExpr,
    VariableExpr,
)
from ...errors import LuminaError
from ..types import is_assignable


class OperatorsMixin:

    def visit_BinaryExpr(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if node.op in ('==', '!=', '<', '>', '<=', '>='):
            if left_type and right_type and left_type != right_type:
                if not (is_assignable(left_type, right_type)
                        or is_assignable(right_type, left_type)):
                    raise LuminaError(
                        f"Tipos incompatíveis na comparação: "
                        f"'{left_type}' e '{right_type}'",
                        self.filename, getattr(node, 'line', 0),
                        getattr(node, 'col', 0), self.source_code,
                    )
            return "bool"

        if node.op in ('and', 'or'):
            if left_type != "bool" or right_type != "bool":
                raise LuminaError(
                    f"Operador lógico '{node.op}' requer operandos 'bool'",
                    self.filename, getattr(node, 'line', 0),
                    getattr(node, 'col', 0), self.source_code,
                )
            return "bool"

        if left_type and left_type.split('<')[0] in self.structs:
            struct_name = left_type.split('<')[0]
            op_map = {
                '+': '__add__', '-': '__sub__', '*': '__mul__',
                '/': '__div__', '==': '__eq__',
            }
            method_name = op_map.get(node.op)
            if method_name:
                real_method_name = f"{struct_name}_{method_name}"
                if real_method_name not in self.functions:
                    raise LuminaError(
                        f"Operador '{node.op}' não definido para a struct "
                        f"'{struct_name}'.",
                        self.filename, getattr(node, 'line', 0),
                        getattr(node, 'col', 0), self.source_code,
                    )
        return left_type

    def visit_UnaryExpr(self, node):
        self.visit(node.val)
        return None

    def visit_AddressOfExpr(self, node):
        if isinstance(node.val, VariableExpr) and node.val.name in self.functions:
            return "ptr"
        self.visit(node.val)
        return "ptr"

    def visit_DerefExpr(self, node):
        self.visit(node.val)
        return None

    def visit_PropagateExpr(self, node):
        self.visit(node.val)
        if (not hasattr(self, 'current_ret_type')
                or not self.current_ret_type.startswith("Result")):
            raise LuminaError(
                "Operador '?' só pode ser usado em funções que retornam 'Result'.",
                self.filename, getattr(node, 'line', 0),
                getattr(node, 'col', 0), self.source_code,
            )
        return None
