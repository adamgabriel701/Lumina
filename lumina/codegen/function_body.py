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

        # Inicializa o estado do codegen para esta função
        self._reset_function_codegen_state()
        self._fn_entry_block = entry_bb
        self._fn_return_type = func_type.return_type

        # O builder começa no bloco de entrada.
        # Todos os allocas feitos aqui (parâmetros) ficam no topo da função.
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
            # ------------------------------------------------------------------
            # Fase 1 — entry_bb: setup de frame.
            #
            # Aqui só vão coisas que precisam estar no topo da função:
            #   - GC_init (uma vez, antes de qualquer alocação)
            #   - store argc/argv (para o builtin `argv(i)`)
            #   - allocas dos parâmetros
            #
            # `_fn_emit_alloca` (chamado durante o body) insere seus
            # `alloca` no INÍCIO deste bloco — antes do GC_init e dos
            # stores. Isso é o correto: todos os allocas de uma função
            # ficam no mesmo frame.
            # ------------------------------------------------------------------
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

            # Aloca os parâmetros no bloco de entrada (entry_bb)
            for i, p in enumerate(node.params):
                p_name = p.name
                p_type = p.type_ann
                p_ty = self.get_llvm_param_type(p_type)
                ptr = self.builder.alloca(p_ty, name=p_name)
                self.builder.store(func.args[i], ptr)
                self.symbol_table[p_name] = ptr
                self.var_types[p_name] = p_type

            # Pula para o bloco do corpo.
            self.builder.branch(body_bb)
            self.builder.position_at_end(body_bb)

            # ------------------------------------------------------------------
            # Fase 2 — body_bb: init runtime de globais, depois user code.
            #
            # PATCH: o init dos `mut X = <não-literal>` foi movido de
            # `entry_bb` para `body_bb`.
            #
            # Motivo: `_fn_emit_alloca` insere allocas no INÍCIO do
            # `entry_bb` via `position_at_start`. Isso colocava os
            # allocas de temporários ANTES dos `call malloc` que
            # inicializam `g_memory`/`g_V`/`g_screen`. Com `-O2`, o
            # LLVM reordenava stores/loads entre as duas fases e o
            # `chip8` lia `g_screen` como null (SIGSEGV na 14ª linha
            # de `draw_screen`, ~896 bytes lidos).
            #
            # Movendo o init para `body_bb`, ele roda DEPOIS do
            # `br body_bb` e antes de qualquer user code. Como está
            # no mesmo bloco dos loads subsequentes, o LLVM não pode
            # reordená-los.
            #
            # Ordem = ordem de declaração no AST. Isso garante que
            # dependências entre globais funcionem:
            #   `mut screen = alloc_bytes(screen_width * screen_height)`
            # roda depois de `let screen_width = 64` estar disponível.
            # ------------------------------------------------------------------
            if node.name == "main":
                for gv, init_expr in getattr(self, '_deferred_globals', []):
                    try:
                        val = self.visit(init_expr)
                        target_ty = gv.type.pointee
                        val = self._coerce_val_to(val, target_ty, name=gv.name)
                        self.builder.store(val, gv)
                    except Exception:
                        # Se a init falhar (tipo inesperado, símbolo
                        # não resolvido em compile-time), segue — o
                        # global fica com o zero-init. Preferimos
                        # compilar o resto do programa do que abortar
                        # por causa de uma init isolada.
                        pass

            # ------------------------------------------------------------------
            # Fase 3 — user code.
            # ------------------------------------------------------------------
            for stmt in node.body:
                self.visit(stmt)

            # Hook: garante terminador no bloco (add `ret` no fim se
            # o body terminar sem um).
            self._fn_ensure_terminator()