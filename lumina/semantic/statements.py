"""Análise semântica de statements.

Notas de decisão:
  * `BinaryExpr` → var_type inferido pelo operador e tipos dos lados
  * `ArrayExpr` → var_type = "ptr"
  * `AddressOfExpr` → var_type = "ptr"
  * `DerefExpr` → var_type = "int"
  * `PropagateExpr` → var_type = "int"
  * `LambdaExpr` → var_type = "fn"
  * `NoneExpr` → var_type = "Option"
  * `ComptimeExpr` → var_type inferido pelo valor dobrado
  * `SliceExpr` → var_type = "ptr"
  * Funções genéricas: se o return_type é um type_param (T), infere pelos args

Bug corrigido: corpos de IfStmt/WhileStmt/ForStmt/MatchStmt usam
`analyze_stmt` (não `visit`), que faz a análise semântica real.
"""
from ..ast import (
    VarDecl, DestructureStmt, AssignStmt, ReturnStmt, IfStmt, WhileStmt,
    ForStmt, MatchStmt, ContinueStmt, DeferStmt, BreakStmt, AssertStmt,
    BenchStmt, CallExpr, MemberExpr, DerefExpr, SliceExpr, IndexExpr,
    VariableExpr, StringExpr, NumberExpr, BoolExpr, BinaryExpr,
    StructLiteralExpr, ArrayExpr, AddressOfExpr, PropagateExpr, LambdaExpr,
    NoneExpr, ComptimeExpr, ErrorNode,
)
from ..errors import LuminaError
from .types import is_assignable


class StatementAnalyzer:
    """Análise semântica de statements."""

    def _require_assignable(self, target_type, value_type, context, line=0, col=0):
        if target_type is None or value_type is None:
            return
        if is_assignable(target_type, value_type):
            return
        raise LuminaError(
            f"Tipo inválido em {context}: esperado '{target_type}', obteve '{value_type}'.",
            self.filename, line, col, self.source_code,
        )

    def _require_bool(self, cond_type, context, line=0, col=0):
        if cond_type in ("bool", "int", None, "Unknown"):
            return
        raise LuminaError(
            f"{context} deve ser 'bool' ou 'int', obteve '{cond_type}'.",
            self.filename, line, col, self.source_code,
        )

    def _find_enum_of_variant(self, variant_name):
        """Retorna o nome do enum que contém `variant_name`, ou None."""
        for enum_name, enum_def in self.struct_defs.items():
            if not hasattr(enum_def, 'variants'):
                continue
            for v in enum_def.variants:
                if v[0] == variant_name:
                    return enum_name
        return None

    def _infer_binary_type(self, node: BinaryExpr):
        """Infere o tipo de uma expressão binária.

        Regras (heurísticas — olha o tipo dos lados, não o valor):
          - Comparações (==, !=, <, >, <=, >=) → "bool"
          - `and`/`or` → "bool"
          - `+` com str de um lado → "str"
          - Se algum lado é float → "float"
          - Se algum lado é struct → o tipo da struct (sobrecarga)
          - Caso contrário → "int"
        """
        # Comparações e lógicos → bool
        if node.op in ('==', '!=', '<', '>', '<=', '>='):
            return "bool"
        if node.op in ('and', 'or'):
            return "bool"

        lt = self.visit(node.left)
        rt = self.visit(node.right)

        # Concatenação de string
        if node.op == '+' and (lt == "str" or rt == "str"):
            return "str"

        # Structs: assume que o overload retorna a mesma struct
        if lt and lt.split('<')[0] in self.structs:
            return lt
        if rt and rt.split('<')[0] in self.structs:
            return rt

        # Promoção numérica
        if lt == "float" or rt == "float":
            return "float"

        return "int"

    def analyze_stmt(self, node):
        if isinstance(node, ErrorNode):
            return

        # ------------------------------------------------------------------
        # VarDecl
        # ------------------------------------------------------------------
        if isinstance(node, VarDecl):
            if node.var_type is not None:
                base_type = node.var_type.split('<')[0]
                if base_type not in ("int", "float", "bool", "str", "ptr", "fn") and base_type not in self.structs:
                    raise LuminaError(
                        f"Tipo '{node.var_type}' não declarado.",
                        self.filename, 0, 0, self.source_code,
                    )

            if node.var_type is None and node.value is not None:
                # 1) MemberExpr: infere pelo tipo do campo
                # 2) BinaryExpr: infere pelo operador
                # 3) NoneExpr: Option
                # 4) ComptimeExpr: infere pelo valor dobrado
                # 5) Os literais de sempre
                # 6) CallExpr: return_type / genérico / enum
                if isinstance(node.value, MemberExpr):
                    field_type = self.visit(node.value)
                    if field_type:
                        node.var_type = field_type
                elif isinstance(node.value, BinaryExpr):
                    node.var_type = self._infer_binary_type(node.value)
                elif isinstance(node.value, NoneExpr):
                    node.var_type = "Option"
                elif isinstance(node.value, ComptimeExpr):
                    folded = self._constant_fold(node.value.expr)
                    if folded is not None:
                        node.value.folded = folded
                        if isinstance(folded, NumberExpr):
                            node.var_type = "float" if folded.is_float else "int"
                        elif isinstance(folded, BoolExpr):
                            node.var_type = "bool"
                        elif isinstance(folded, StringExpr):
                            node.var_type = "str"
                elif isinstance(node.value, StringExpr):
                    node.var_type = "str"
                elif isinstance(node.value, NumberExpr):
                    node.var_type = "float" if node.value.is_float else "int"
                elif isinstance(node.value, BoolExpr):
                    node.var_type = "bool"
                elif isinstance(node.value, StructLiteralExpr):
                    node.var_type = node.value.struct_name
                elif isinstance(node.value, LambdaExpr):
                    node.var_type = "fn"
                elif isinstance(node.value, ArrayExpr):
                    node.var_type = "ptr"
                elif isinstance(node.value, AddressOfExpr):
                    node.var_type = "ptr"
                elif isinstance(node.value, DerefExpr):
                    node.var_type = "int"
                elif isinstance(node.value, PropagateExpr):
                    node.var_type = "int"
                elif isinstance(node.value, SliceExpr):
                    node.var_type = "ptr"
                elif isinstance(node.value, IndexExpr):
                    node.var_type = "int"
                elif isinstance(node.value, CallExpr):
                    # NOVO: extrai nome da função corretamente para MemberExpr
                    # (ex: `p.clone()` → func_name = 'clone').
                    func_name = None
                    _callee = getattr(node.value, 'callee', None)
                    if isinstance(_callee, MemberExpr):
                        func_name = _callee.member
                    elif isinstance(_callee, VariableExpr):
                        func_name = _callee.name

                    if node.value.is_method:
                        obj_node = node.value.args[0]
                        if isinstance(obj_node, VariableExpr):
                            info = self.get_var_info(obj_node.name)
                            if info:
                                struct_name = info['type'].split('<')[0] if info['type'] else "Unknown"
                                real_method_name = f"{struct_name}_{func_name}"
                                if real_method_name in self.function_defs:
                                    node.var_type = self.function_defs[real_method_name].return_type
                                else:
                                    node.var_type = "int"
                    else:
                        if func_name in self.function_defs:
                            fn_def = self.function_defs[func_name]
                            ret_t = fn_def.return_type
                            type_params = getattr(fn_def, 'type_params', None) or []

                            if ret_t in type_params:
                                inferred = "int"
                                for arg_node, param in zip(node.value.args, fn_def.params):
                                    if param.type_ann == ret_t:
                                        at = self.visit(arg_node)
                                        if at:
                                            inferred = at
                                        break
                                node.var_type = inferred
                            else:
                                node.var_type = ret_t
                        else:
                            enum_name = self._find_enum_of_variant(func_name)
                            if enum_name is not None:
                                node.var_type = enum_name
                            else:
                                node.var_type = "int"

            if isinstance(node.value, CallExpr) and getattr(node.value.callee, 'name', None) == "alloc":
                self.heap_allocs.add(node.name)

            value_type = None
            if node.value:
                value_type = self.visit(node.value)

            if node.var_type is not None and value_type is not None:
                self._require_assignable(
                    node.var_type, value_type,
                    context=f"declaração de '{node.name}'",
                    line=getattr(node, 'line', 0),
                    col=getattr(node, 'col', 0),
                )

            self.declare_var(node.name, node.var_type, node.is_mutable)

        # ------------------------------------------------------------------
        # DestructureStmt
        # ------------------------------------------------------------------
        elif isinstance(node, DestructureStmt):
            self.visit(node.value)
            for name in node.names:
                self.declare_var(name, "int", node.is_mutable)

        # ------------------------------------------------------------------
        # AssignStmt
        # ------------------------------------------------------------------
        elif isinstance(node, AssignStmt):
            target_type = None

            if isinstance(node.target, MemberExpr):
                self.check_escape(node.target.obj)
                if isinstance(node.target.obj, VariableExpr):
                    info = self.get_var_info(node.target.obj.name)
                    if not info:
                        raise LuminaError(
                            f"Variável '{node.target.obj.name}' não declarada.",
                            self.filename, 0, 0, self.source_code,
                        )
                    if not info['mutable']:
                        raise LuminaError(
                            f"Não pode modificar variável imutável '{node.target.obj.name}'.",
                            self.filename, 0, 0, self.source_code,
                        )
                    base_type = info['type'].split('<')[0] if info['type'] else "Unknown"
                    if base_type not in self.struct_defs:
                        raise LuminaError(
                            f"Variável '{node.target.obj.name}' não é uma Struct.",
                            self.filename, 0, 0, self.source_code,
                        )
                    struct_def = self.struct_defs[base_type]
                    if node.target.member not in struct_def.fields:
                        raise LuminaError(
                            f"Campo '{node.target.member}' não existe na Struct '{info['type']}'.",
                            self.filename, 0, 0, self.source_code,
                        )
                    target_type = struct_def.fields[node.target.member]
                else:
                    self.visit(node.target.obj)

            elif isinstance(node.target, DerefExpr):
                pass

            elif isinstance(node.target, IndexExpr):
                self.check_escape(node.target.array)

            else:
                self.check_escape(node.value)
                info = self.get_var_info(node.target.name)
                if not info:
                    raise LuminaError(
                        f"Variável '{node.target.name}' não declarada.",
                        self.filename, 0, 0, self.source_code,
                    )
                if not info['mutable']:
                    raise LuminaError(
                        f"Não pode reatribuir à variável imutável '{node.target.name}'.",
                        self.filename, 0, 0, self.source_code,
                    )
                target_type = info['type']

            self.check_escape(node.value)
            value_type = self.visit(node.value)

            if target_type is not None and value_type is not None:
                self._require_assignable(target_type, value_type, context="atribuição")

        # ------------------------------------------------------------------
        # ReturnStmt
        # ------------------------------------------------------------------
        elif isinstance(node, ReturnStmt):
            expected = getattr(self, 'current_ret_type', None)
            is_single = len(node.values) == 1

            for val in node.values:
                self.check_escape(val)
                actual = self.visit(val)
                if is_single and expected and expected != "void" and actual:
                    self._require_assignable(
                        expected, actual,
                        context=f"retorno de '{getattr(self, 'current_func_name', 'função')}'",
                    )

        # ------------------------------------------------------------------
        # IfStmt
        # ------------------------------------------------------------------
        elif isinstance(node, IfStmt):
            cond_type = self.visit(node.condition)
            self._require_bool(cond_type, context="Condição de 'if'")

            self.push_scope()
            for stmt in node.then_body:
                self.analyze_stmt(stmt)
            self.pop_scope()

            if node.else_body:
                self.push_scope()
                for stmt in node.else_body:
                    self.analyze_stmt(stmt)
                self.pop_scope()

        # ------------------------------------------------------------------
        # WhileStmt
        # ------------------------------------------------------------------
        elif isinstance(node, WhileStmt):
            cond_type = self.visit(node.condition)
            self._require_bool(cond_type, context="Condição de 'while'")

            self.push_scope()
            for stmt in node.body:
                self.analyze_stmt(stmt)
            self.pop_scope()

        # ------------------------------------------------------------------
        # ForStmt
        # ------------------------------------------------------------------
        elif isinstance(node, ForStmt):
            if node.iterable is not None:
                self.visit(node.iterable)
            else:
                self.visit(node.start)
                self.visit(node.end)
            self.push_scope()
            self.declare_var(node.var_name, "int", False)
            for stmt in node.body:
                self.analyze_stmt(stmt)
            self.pop_scope()

        # ------------------------------------------------------------------
        # MatchStmt
        # ------------------------------------------------------------------
        elif isinstance(node, MatchStmt):
            cond_type = self.visit(node.condition)

            # Tipo do binding:
            #   - `case s if cond`: variant_name is None → binding é
            #     self-binding. O PARSER sempre empacota como lista
            #     (`binding = [first_ident]`), então `isinstance(...,list)`
            #     é True. Tipo = cond_type.
            #   - `case X(v):`        → payload de enum (i64) → "int"
            #   - `case X(a, b):`     → múltiplos payloads (i64) → "int"
            for case in node.cases:
                variant_name, var_name, guard, body = case
                self.push_scope()

                if var_name:
                    names = var_name if isinstance(var_name, list) else [var_name]
                    if variant_name is None:
                        # Self-binding: herda o tipo do cond
                        binding_type = cond_type or "int"
                    else:
                        # Payload de variante de enum
                        binding_type = "int"
                    for name in names:
                        self.declare_var(name, binding_type, False)

                if guard:
                    guard_type = self.visit(guard)
                    self._require_bool(guard_type, context="Guard de 'case'")

                for stmt in body:
                    self.analyze_stmt(stmt)

                self.pop_scope()

            if node.default:
                self.push_scope()
                for stmt in node.default:
                    self.analyze_stmt(stmt)
                self.pop_scope()

        # ------------------------------------------------------------------
        # Outros
        # ------------------------------------------------------------------
        elif isinstance(node, ContinueStmt):
            pass

        elif isinstance(node, BreakStmt):
            pass

        elif isinstance(node, DeferStmt):
            for stmt in node.body:
                self.analyze_stmt(stmt)

        elif isinstance(node, AssertStmt):
            cond_type = self.visit(node.condition)
            self._require_bool(cond_type, context="Condição de 'assert'")

        elif isinstance(node, BenchStmt):
            for stmt in node.body:
                self.analyze_stmt(stmt)

        else:
            self.visit(node)