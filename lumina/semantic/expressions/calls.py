"""Chamadas: resolução de kwargs, builtins, métodos, genéricos."""
from ...ast import CallExpr, MemberExpr, VariableExpr
from ...builtins import BUILTIN_RET
from ...errors import LuminaError
from ..types import is_assignable, substitute_generic, unify_type
from .helpers import get_suggestion


class CallsMixin:

    def _resolve_kwargs(self, node, fn_def, skip_self=False):
        """Converte `node.kwargs` em `node.args` posicionais.

        Modifica `node` in-place. Após isso, o codegen só vê positional args.
        Parâmetros não fornecidos são preenchidos com seu default — se não
        houver default, é erro.
        """
        if not node.kwargs:
            return
        if fn_def is None:
            return

        params = fn_def.params
        if skip_self and params:
            params = params[1:]

        param_names = [p.name for p in params]
        n = len(param_names)

        positional = list(node.args)
        base = positional[1:] if skip_self else positional

        if len(base) > n:
            return  # deixa o codegen reclamar

        new_args = [None] * n
        for i, a in enumerate(base):
            new_args[i] = a

        for name, val in node.kwargs:
            if name not in param_names:
                raise LuminaError(
                    f"Parâmetro '{name}' não existe.",
                    self.filename, 0, 0, self.source_code,
                )
            idx = param_names.index(name)
            if new_args[idx] is not None:
                raise LuminaError(
                    f"Argumento duplicado para '{name}'.",
                    self.filename, 0, 0, self.source_code,
                )
            new_args[idx] = val

        # Preenche buracos com o default do param. Se não houver,
        # é erro de argumento obrigatório faltando.
        final_args = []
        for i in range(n):
            if new_args[i] is not None:
                final_args.append(new_args[i])
            else:
                default = getattr(params[i], 'default', None)
                if default is None:
                    raise LuminaError(
                        f"Parâmetro '{params[i].name}' é obrigatório.",
                        self.filename, 0, 0, self.source_code,
                    )
                final_args.append(default)

        if skip_self:
            node.args = [positional[0]] + final_args
        else:
            node.args = final_args
        node.kwargs = []

    def visit_CallExpr(self, node):
        func_name = None
        if isinstance(node.callee, MemberExpr):
            func_name = node.callee.member
        elif isinstance(node.callee, VariableExpr):
            func_name = node.callee.name

        # Resolve named arguments em posicional.
        if node.kwargs:
            if node.is_method:
                obj_node = node.args[0]
                obj_type = self.visit(obj_node)
                fn_def = None
                if obj_type and obj_type != "Unknown":
                    struct_name = obj_type.split('<')[0]
                    real_name = f"{struct_name}_{func_name}"
                    fn_def = self.function_defs.get(real_name)
                self._resolve_kwargs(node, fn_def, skip_self=True)
            else:
                fn_def = self.function_defs.get(func_name)
                self._resolve_kwargs(node, fn_def, skip_self=False)

        # Builtins com tipo de retorno conhecido (fonte única:
        # lumina/builtins.py::BUILTIN_RET). Sem isso, o VarDecl infere
        # "int" por padrão e `buf = alloc_bytes(N)` acaba batendo em
        # campos `str`/`ptr`; `fgets` retornaria int e `r == nil`
        # falharia.
        if not node.is_method:
            if func_name in BUILTIN_RET:
                for arg in node.args:
                    self.visit(arg)
                return BUILTIN_RET[func_name]

        if node.is_method:
            if not node.args:
                raise LuminaError(
                    f"Chamada de método '{func_name}' sem objeto alvo.",
                    self.filename, getattr(node, 'line', 0),
                    getattr(node, 'col', 0), self.source_code,
                )
            obj_node = node.args[0]
            obj_type = self.visit(obj_node)
            if not obj_type:
                return None
            if obj_type == "str":
                if func_name not in ("contains", "starts_with", "len",
                                     "upper", "lower"):
                    raise LuminaError(
                        f"Método de string '{func_name}' não suportado.",
                        self.filename, getattr(node, 'line', 0),
                        getattr(node, 'col', 0), self.source_code,
                    )
            elif obj_type != "Unknown":
                struct_name = obj_type.split('<')[0]
                real_method_name = f"{struct_name}_{func_name}"
                if real_method_name not in self.functions:
                    raise LuminaError(
                        f"Método '{func_name}' não implementado para a struct "
                        f"'{struct_name}'.",
                        self.filename, getattr(node, 'line', 0),
                        getattr(node, 'col', 0), self.source_code,
                    )
        else:
            # Chamada indireta via function pointer local.
            # Caso `f: fn` em parâmetro, ou `let f = fn(...)`. O codegen
            # já suporta chamadas indiretas, mas o semantic precisa
            # reconhecer o tipo `fn`.
            info = self.get_var_info(func_name) if func_name else None
            if info is not None and info.get('type') == 'fn':
                for arg in node.args:
                    self.visit(arg)
                # Tipo de retorno de function pointer é desconhecido.
                return None

            if (func_name not in self.builtin_functions
                    and func_name not in self.functions):
                suggestion = get_suggestion(
                    func_name,
                    list(self.functions) + list(self.builtin_functions),
                )
                msg = f"Função '{func_name}' não declarada."
                if suggestion:
                    msg += f" Você quis dizer '{suggestion}'?"
                raise LuminaError(
                    msg, self.filename, getattr(node, 'line', 0),
                    getattr(node, 'col', 0), self.source_code,
                )

            if func_name in self.function_defs:
                fn_def = self.function_defs[func_name]

                required = sum(
                    1 for p in fn_def.params
                    if getattr(p, 'default', None) is None
                )
                n_args = len(node.args)
                if not (required <= n_args <= len(fn_def.params)):
                    if required == len(fn_def.params):
                        raise LuminaError(
                            f"Função '{func_name}' espera {required} args, "
                            f"recebeu {n_args}.",
                            self.filename, getattr(node, 'line', 0),
                            getattr(node, 'col', 0), self.source_code,
                        )
                    else:
                        raise LuminaError(
                            f"Função '{func_name}' espera entre {required} e "
                            f"{len(fn_def.params)} args, recebeu {n_args}.",
                            self.filename, getattr(node, 'line', 0),
                            getattr(node, 'col', 0), self.source_code,
                        )

                type_params = getattr(fn_def, 'type_params', None) or []

                if type_params:
                    # Infere type_map unificando (param_type, arg_type)
                    type_map = {}
                    for arg_node, param in zip(node.args, fn_def.params):
                        arg_type = self.visit(arg_node)
                        if arg_type is None:
                            continue
                        unify_type(param.type_ann, arg_type, type_map)

                    # Valida com tipo substituído
                    for arg_node, param in zip(node.args, fn_def.params):
                        arg_type = self.visit(arg_node)
                        if arg_type is None:
                            continue
                        expected = substitute_generic(param.type_ann, type_map)
                        # Se ainda tem type params não resolvidos, aceita
                        # (não dá para validar sem contexto)
                        if expected != param.type_ann and expected.isupper():
                            continue
                        if not is_assignable(expected, arg_type):
                            raise LuminaError(
                                f"Tipo inválido para parâmetro '{param.name}': "
                                f"esperado '{expected}', obteve '{arg_type}'.",
                                self.filename, getattr(node, 'line', 0),
                                getattr(node, 'col', 0), self.source_code,
                            )
                else:
                    # Comportamento antigo (sem type params)
                    for arg_node, param in zip(node.args, fn_def.params):
                        arg_type = self.visit(arg_node)
                        p_name, p_type = param.name, param.type_ann
                        if (arg_type and p_type
                                and not is_assignable(p_type, arg_type)):
                            raise LuminaError(
                                f"Tipo inválido para parâmetro '{p_name}': "
                                f"esperado '{p_type}', obteve '{arg_type}'.",
                                self.filename, getattr(node, 'line', 0),
                                getattr(node, 'col', 0), self.source_code,
                            )

            # Rastreia variáveis liberadas com `free()`.
            # Usado pelo escape analysis para NÃO colocar no stack.
            if func_name == "free" and node.args:
                arg0 = node.args[0]
                if isinstance(arg0, VariableExpr):
                    self.freed_vars.add(arg0.name)

        for arg in node.args:
            self.visit(arg)
        return None
