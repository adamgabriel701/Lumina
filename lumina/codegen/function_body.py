"""Corpo de função — geração de IR para o corpo de `fn`."""
from llvmlite import ir

from .context import push_context, normalize_attrs


class FunctionBodyMixin:

    def generate_function_body(self, node):
        func = self.functions_table[node.name][0]
        func_type = self.functions_table[node.name][1]

        # `attrs` é `List[str]` no parser atual. `normalize_attrs`
        # aceita ambos formatos e devolve `List[Tuple[str, List]]`.
        attrs_norm = normalize_attrs(getattr(node, 'attrs', None))
        is_safe = any(name == 'safe' for name, _args in attrs_norm)

        entry_bb = func.append_basic_block(name=f"{node.name}_entry")
        body_bb = func.append_basic_block(name=f"{node.name}_body")

        fresh_builder = ir.IRBuilder(entry_bb)

        with push_context(
            self,
            builder=fresh_builder,
            symbol_table={},
            var_types={},
            current_func_name=node.name,
            current_body_bb=body_bb,
            defer_stack=[],
            closure_vars=set(),
            _safe_mode=is_safe,
            _current_scc_slots=None,
            _current_scc_ids=None,
            _current_scc_id_slot=None,
            _current_scc_dispatch_bb=None,
        ):
            if node.name == "main" and self.use_gc:
                gc_init = self.module.globals.get("GC_init")
                if gc_init is not None:
                    self.builder.call(gc_init, [], name="gc_init_call")

            if node.name == "main":
                argc_gv = self.module.globals.get("__lumina_argc")
                argv_gv = self.module.globals.get("__lumina_argv")
                if argc_gv is not None:
                    self.builder.store(func.args[0], argc_gv)
                if argv_gv is not None:
                    self.builder.store(func.args[1], argv_gv)

            for i, p in enumerate(node.params):
                p_name = p.name
                p_type = p.type_ann
                p_ty = self.get_llvm_param_type(p_type)
                ptr = self.builder.alloca(p_ty, name=p_name)
                self.builder.store(func.args[i], ptr)
                self.symbol_table[p_name] = ptr
                self.var_types[p_name] = p_type

            self.builder.branch(body_bb)
            self.builder.position_at_end(body_bb)

            for stmt in node.body:
                self.visit(stmt)

            if not self.builder.block.is_terminated:
                ret_ty = func_type.return_type
                if isinstance(ret_ty, ir.VoidType):
                    self.builder.ret_void()
                elif isinstance(ret_ty, ir.LiteralStructType):
                    zero_fields = [ir.Constant(ft, 0) for ft in ret_ty.elements]
                    self.builder.ret(ir.Constant(ret_ty, zero_fields))
                else:
                    self.builder.ret(self._zero_for_type(ret_ty))