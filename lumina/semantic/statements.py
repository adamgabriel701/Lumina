"""Análise semântica de statements.

Notas de decisão:
  * `ArrayExpr` → var_type = "ptr" (codegen trata como i64*)
  * `AddressOfExpr` → var_type = "ptr"
  * `DerefExpr` → var_type = "int"
  * `PropagateExpr` → var_type = "int"
  * `LambdaExpr` → var_type = "fn"
  * Funções genéricas: se o return_type é um type_param (T), infere pelos args

Bug corrigido: corpos de IfStmt/WhileStmt/ForStmt/MatchStmt agora usam
`analyze_stmt` (não `visit`), que faz a análise semântica real. Antes,
var decls dentro desses blocos não eram registradas no escopo.
"""
from ..ast import (
    VarDecl, DestructureStmt, AssignStmt, ReturnStmt, IfStmt, WhileStmt,
    ForStmt, MatchStmt, ContinueStmt, DeferStmt, BreakStmt, AssertStmt,
    BenchStmt, CallExpr, MemberExpr, DerefExpr, IndexExpr, VariableExpr,
    StringExpr, NumberExpr, BoolExpr, BinaryExpr, StructLiteralExpr,
    ArrayExpr, AddressOfExpr, PropagateExpr, LambdaExpr, ErrorNode,
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
        # Aceita `bool` e `int` (0 = false, != 0 = true) — o codegen
        # já converte i64 → i1 no cbranch. Isso é idiomático em C, Python,
        # JS, e a maioria dos exemplos Lumina usa `if <int>`.
        if cond_type in ("bool", "int", None, "Unknown"):
            return
        raise LuminaError(
            f"{context} deve ser 'bool' ou 'int', obteve '{cond_type}'.",
            self.filename, line, col, self.source_code,
        )

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
                if isinstance(node.value, StringExpr):
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
                elif isinstance(node.value, IndexExpr):
                    if isinstance(node.value.index, BinaryExpr) and node.value.index.op == '..':
                        node.var_type = "ptr"
                    else:
                        node.var_type = "int"
                elif isinstance(node.value, CallExpr):
                    func_name = getattr(node.value.callee, 'name', None) if hasattr(node.value, 'callee') else getattr(node.value, 'name', None)

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
        # IfStmt  ← BUG CORRIGIDO: analyze_stmt em vez de visit
        # ------------------------------------------------------------------
        elif isinstance(node, IfStmt):
            cond_type = self.visit(node.condition)
            self._require_bool(cond_type, context="Condição de 'if'")

            self.push_scope()
            for stmt in node.then_body:
                self.analyze_stmt(stmt)   # ← NÃO é self.visit
            self.pop_scope()

            if node.else_body:
                self.push_scope()
                for stmt in node.else_body:
                    self.analyze_stmt(stmt)   # ← NÃO é self.visit
                self.pop_scope()

        # ------------------------------------------------------------------
        # WhileStmt  ← BUG CORRIGIDO
        # ------------------------------------------------------------------
        elif isinstance(node, WhileStmt):
            cond_type = self.visit(node.condition)
            self._require_bool(cond_type, context="Condição de 'while'")

            self.push_scope()
            for stmt in node.body:
                self.analyze_stmt(stmt)   # ← CORRIGIDO
            self.pop_scope()

        # ------------------------------------------------------------------
        # ForStmt  ← BUG CORRIGIDO
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
                self.analyze_stmt(stmt)   # ← CORRIGIDO
            self.pop_scope()

        # ------------------------------------------------------------------
        # MatchStmt  ← BUG CORRIGIDO
        # ------------------------------------------------------------------
        elif isinstance(node, MatchStmt):
            self.visit(node.condition)
            for case in node.cases:
                variant_name, var_name, guard, body = case
                self.push_scope()
                if var_name:
                    if isinstance(var_name, list):
                        for name in var_name:
                            self.declare_var(name, "int", False)
                    else:
                        self.declare_var(var_name, "int", False)
                if guard:
                    guard_type = self.visit(guard)
                    self._require_bool(guard_type, context="Guard de 'case'")
                for stmt in body:
                    self.analyze_stmt(stmt)   # ← CORRIGIDO
                self.pop_scope()
            if node.default:
                self.push_scope()
                for stmt in node.default:
                    self.analyze_stmt(stmt)   # ← CORRIGIDO
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