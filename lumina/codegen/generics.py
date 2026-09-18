"""Monomorphization e inferência de type_map para chamadas genéricas."""
from llvmlite import ir

from ..semantic.types import substitute_generic, unify_type


class GenericsMixin:

    def materialize_generic(self, gen_def, type_map):
        """Gera cópia especializada de uma função genérica.

        `type_map`: dict {type_param_name: tipo_concreto_lumina}.
        Ex: materialize_generic(put_def, {"T": "int"}) gera `put__int`.
        """
        type_params = getattr(gen_def, 'type_params', None) or []

        def _sanitize(s):
            return s.replace("<", "_").replace(">", "").replace(",", "_").replace(" ", "")
        suffix_parts = [_sanitize(type_map.get(tp, "unknown")) for tp in type_params]
        mangled = f"{gen_def.name}__{'_'.join(suffix_parts)}"

        if mangled in self.functions_table:
            return mangled

        def resolve_lumina(name):
            return substitute_generic(name, type_map)

        ret_lumina = resolve_lumina(gen_def.return_type)
        ret_ty = self.get_llvm_param_type(ret_lumina)

        param_tys = []
        for p in gen_def.params:
            param_lumina = resolve_lumina(p.type_ann)
            param_tys.append(self.get_llvm_param_type(param_lumina))

        func_type = ir.FunctionType(ret_ty, param_tys)
        func = ir.Function(self.module, func_type, name=mangled)
        self.functions_table[mangled] = (func, func_type)
        self.function_defs[mangled] = gen_def

        # Sprint 10: aplica attrs também na cópia especializada
        attrs = getattr(gen_def, 'attrs', None) or []
        self._apply_llvm_attrs(func, attrs)

        # Salva/restaura estado
        old_builder = self.builder
        old_symtab = self.symbol_table
        old_var_types = self.var_types
        old_current = getattr(self, 'current_func_name', None)
        old_body_bb = getattr(self, 'current_body_bb', None)
        old_defer_stack = getattr(self, 'defer_stack', None)
        old_safe = getattr(self, '_safe_mode', False)
        old_closure_vars = self.closure_vars
        self.defer_stack = []
        self._safe_mode = False   # genéricos não têm attrs
        self.closure_vars = set()

        entry_bb = func.append_basic_block(name=f"{mangled}_entry")
        body_bb = func.append_basic_block(name=f"{mangled}_body")
        self.builder = ir.IRBuilder(entry_bb)
        self.symbol_table = {}
        self.var_types = {}
        self.current_func_name = mangled

        for i, p in enumerate(gen_def.params):
            p_name = p.name
            param_lumina = resolve_lumina(p.type_ann)
            p_ty = func_type.args[i]
            ptr = self.builder.alloca(p_ty, name=p_name)
            self.builder.store(func.args[i], ptr)
            self.symbol_table[p_name] = ptr
            self.var_types[p_name] = param_lumina

        self.builder.branch(body_bb)
        self.builder.position_at_end(body_bb)
        self.current_body_bb = body_bb

        for stmt in gen_def.body:
            if self.builder.block.is_terminated:
                break
            self.visit(stmt)

        if not self.builder.block.is_terminated:
            self._emit_all_defers()
        if not self.builder.block.is_terminated:
            if func_type.return_type == self.void_ty:
                self.builder.ret_void()
            elif isinstance(func_type.return_type, ir.PointerType):
                self.builder.ret(ir.Constant(func_type.return_type, None))
            else:
                self.builder.ret(ir.Constant(func_type.return_type, 0))

        self.builder = old_builder
        self.defer_stack = old_defer_stack
        self.symbol_table = old_symtab
        self.var_types = old_var_types
        self.current_func_name = old_current
        self.current_body_bb = old_body_bb
        self._safe_mode = old_safe
        self.closure_vars = old_closure_vars

        return mangled

    def _infer_arg_type_lumina(self, arg_node):
        """Best-effort: infere tipo Lumina de um argumento."""
        from ..ast import (
            VariableExpr, NumberExpr, StringExpr, BoolExpr,
            CallExpr, StructLiteralExpr,
        )
        if isinstance(arg_node, VariableExpr):
            return self.var_types.get(arg_node.name)
        if isinstance(arg_node, NumberExpr):
            return "float" if arg_node.is_float else "int"
        if isinstance(arg_node, StringExpr):
            return "str"
        if isinstance(arg_node, BoolExpr):
            return "bool"
        if isinstance(arg_node, StructLiteralExpr):
            return arg_node.struct_name
        if isinstance(arg_node, CallExpr):
            callee_name = None
            if isinstance(arg_node.callee, VariableExpr):
                callee_name = arg_node.callee.name
            elif hasattr(arg_node.callee, 'member'):
                callee_name = arg_node.callee.member
            if callee_name and callee_name in self.function_defs:
                return self.function_defs[callee_name].return_type
            if callee_name:
                lookup = self._find_enum_variant(callee_name)
                if lookup is not None:
                    return lookup[0]
        return None

    def _infer_type_map_lumina(self, gen_def, node):
        """Unifica (param.type_ann, arg_type_lumina) para inferir type_map.

        Retorna dict ou {} se falhar (aí cai no caminho antigo).
        """
        type_map = {}
        for arg_node, param in zip(node.args, gen_def.params):
            arg_type = self._infer_arg_type_lumina(arg_node)
            if arg_type is None:
                return {}
            if not unify_type(param.type_ann, arg_type, type_map):
                return {}
        return type_map
