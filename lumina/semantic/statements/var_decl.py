"""VarDecl, DestructureStmt, AssignStmt — declarações e atribuições."""
from ...ast import (
    VarDecl, DestructureStmt, AssignStmt, CallExpr, MemberExpr,
    VariableExpr, StringExpr, NumberExpr, BoolExpr, BinaryExpr,
    StructLiteralExpr, ArrayExpr, AddressOfExpr, PropagateExpr,
    LambdaExpr, NoneExpr, ComptimeExpr, NilExpr, TupleExpr,
    DerefExpr, SliceExpr, IndexExpr,
)
from ...builtins import BUILTIN_RET
from ...errors import LuminaError
from ...semantic.types import parse_fn_type  # ou ajuste relativo


class VarDeclMixin:

    # ------------------------------------------------------------------
    # VarDecl
    # ------------------------------------------------------------------
    def _analyze_var_decl(self, node):
        if node.var_type is not None:
            base_type = node.var_type.split('<')[0]
            is_fn_sig = base_type.startswith("fn(")
            if (base_type not in ("int", "float", "bool", "str", "ptr", "fn")
                    and not is_fn_sig
                    and base_type not in self.structs):
                raise LuminaError(
                    f"Tipo '{node.var_type}' não declarado.",
                    self.filename, 0, 0, self.source_code,
                )

        if node.var_type is None and node.value is not None:
            self._infer_var_decl_type(node)

        if (isinstance(node.value, CallExpr)
                and getattr(node.value.callee, 'name', None) == "alloc"):
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

    def _infer_var_decl_type(self, node):
        """Infere `node.var_type` para `VarDecl` sem anotação.

        Cobre: MemberExpr, BinaryExpr, NoneExpr, NilExpr, ComptimeExpr,
        StringExpr, NumberExpr, BoolExpr, StructLiteralExpr, LambdaExpr,
        ArrayExpr, TupleExpr, AddressOfExpr, DerefExpr, PropagateExpr,
        SliceExpr, IndexExpr, CallExpr.
        """
        if isinstance(node.value, MemberExpr):
            field_type = self.visit(node.value)
            if field_type:
                node.var_type = field_type

        elif isinstance(node.value, BinaryExpr):
            node.var_type = self._infer_binary_type(node.value)

        elif isinstance(node.value, NoneExpr):
            node.var_type = "Option"

        elif isinstance(node.value, NilExpr):
            node.var_type = "ptr"

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
            param_types = [p.type_ann for p in node.value.params]
            node.var_type = (
                f"fn({','.join(param_types)}) -> {node.value.return_type}"
            )

        elif isinstance(node.value, VariableExpr):
            info = self.get_var_info(node.value.name)
            if info and info.get('type'):
                node.var_type = info['type']
            elif node.value.name in self.functions:
                fn_def = self.function_defs.get(node.value.name)
                if fn_def:
                    params = [p.type_ann for p in fn_def.params]
                    node.var_type = (
                        f"fn({','.join(params)}) -> {fn_def.return_type}"
                    )

        elif isinstance(node.value, ArrayExpr):
            node.var_type = "ptr"

        elif isinstance(node.value, TupleExpr):
            node.var_type = "ptr"

        elif isinstance(node.value, AddressOfExpr):
            node.var_type = "ptr"

        elif isinstance(node.value, DerefExpr):
            node.var_type = "int"

        elif isinstance(node.value, PropagateExpr):
            node.var_type = "int"

        elif isinstance(node.value, SliceExpr):
            # Preserva o tipo da fonte: slice de str → str,
            # slice de array → ptr. Sem isso, `s[a..b]` vira "ptr"
            # (i64*) e `s[a..b] == outra_str` compara endereços.
            node.var_type = self.visit(node.value)

        elif isinstance(node.value, IndexExpr):
            node.var_type = "int"

        elif isinstance(node.value, CallExpr):
            node.var_type = self._infer_call_expr_type(node.value)

    def _infer_call_expr_type(self, call_node):
        func_name = None
        _callee = getattr(call_node, 'callee', None)
        if isinstance(_callee, MemberExpr):
            func_name = _callee.member
        elif isinstance(_callee, VariableExpr):
            func_name = _callee.name

        # Chamada via variável fn-typed: deriva retorno da assinatura.
        if not call_node.is_method and func_name:
            info = self.get_var_info(func_name)
            if info and info.get('type'):
                sig = parse_fn_type(info['type'])
                if sig is not None:
                    _, ret_type = sig
                    return ret_type if ret_type != "void" else None

        if call_node.is_method:
            obj_node = call_node.args[0]
            if isinstance(obj_node, VariableExpr):
                info = self.get_var_info(obj_node.name)
                if info:
                    struct_name = (info['type'].split('<')[0]
                                   if info['type'] else "Unknown")
                    real_method_name = f"{struct_name}_{func_name}"
                    if real_method_name in self.function_defs:
                        return self.function_defs[real_method_name].return_type
                    return "int"

        if func_name in self.function_defs:
            fn_def = self.function_defs[func_name]
            ret_t = fn_def.return_type
            type_params = getattr(fn_def, 'type_params', None) or []

            if ret_t in type_params:
                inferred = "int"
                for arg_node, param in zip(call_node.args, fn_def.params):
                    if param.type_ann == ret_t:
                        at = self.visit(arg_node)
                        if at:
                            inferred = at
                        break
                return inferred
            return ret_t

        enum_name = self._find_enum_of_variant(func_name)
        if enum_name is not None:
            return enum_name
        return BUILTIN_RET.get(func_name, "int")

    # ------------------------------------------------------------------
    # DestructureStmt
    # ------------------------------------------------------------------
    def _analyze_destructure(self, node):
        self.visit(node.value)
        for name in node.names:
            self.declare_var(name, "int", node.is_mutable)

    # ------------------------------------------------------------------
    # AssignStmt
    # ------------------------------------------------------------------
    def _analyze_assign(self, node):
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
                        f"Não pode modificar variável imutável "
                        f"'{node.target.obj.name}'.",
                        self.filename, 0, 0, self.source_code,
                    )
                base_type = (info['type'].split('<')[0]
                             if info['type'] else "Unknown")
                if base_type not in self.struct_defs:
                    raise LuminaError(
                        f"Variável '{node.target.obj.name}' não é uma Struct.",
                        self.filename, 0, 0, self.source_code,
                    )
                struct_def = self.struct_defs[base_type]
                if node.target.member not in struct_def.fields:
                    raise LuminaError(
                        f"Campo '{node.target.member}' não existe na Struct "
                        f"'{info['type']}'.",
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
                    f"Não pode reatribuir à variável imutável "
                    f"'{node.target.name}'.",
                    self.filename, 0, 0, self.source_code,
                )
            target_type = info['type']

        self.check_escape(node.value)
        value_type = self.visit(node.value)

        if target_type is not None and value_type is not None:
            self._require_assignable(target_type, value_type, context="atribuição")
