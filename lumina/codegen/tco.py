"""Tail Call Optimization: SCCs de mutual recursion + dispatcher.

O dispatcher `__scc_N` recebe `(id, params_comuns)` e faz `switch` sobre
`id` para o bloco de cada membro do SCC. Cada membro reescreve seus
próprios slots de parâmetro e salta de volta para `dispatch_bb` — sem
novo frame.

PATCH: `_materialize_scc_dispatcher` agora usa `push_context` em vez de
salvar/restaurar campos manualmente. Além disso, corrige um bug latente:
`var_types` era inicializado como **set** em vez de **dict**, quebrando
`_infer_arg_type_lumina` (que chama `.get()`) quando um membro do SCC
chamava função genérica.
"""
from llvmlite import ir

from .context import push_context


class TCOMixin:

    # ==================================================================
    # SCCs de tail calls + dispatcher
    # ==================================================================
    def _compute_tail_call_sccs(self, ast):
        """SCCs do grafo de tail calls entre funções top-level.

        Retorna `[[name1, name2, ...], ...]` — cada sub-lista é um
        SCC com >= 2 membros. Self-recursion (tamanho 1) é tratada
        pelo `_try_tail_call` existente e NÃO aparece aqui.
        """
        from ..ast import (
            CallExpr, VariableExpr, ReturnStmt,
            IfStmt, WhileStmt, ForStmt, MatchStmt, DeferStmt, BenchStmt,
        )
        from ..ast import Function as AstFunction

        func_names = set()
        for decl in ast:
            if isinstance(decl, AstFunction) and not getattr(decl, 'type_params', None):
                func_names.add(decl.name)

        graph = {n: set() for n in func_names}

        def walk_tail(stmts, current):
            for s in stmts:
                if s is None:
                    continue
                if isinstance(s, ReturnStmt) and len(s.values) == 1:
                    v = s.values[0]
                    if isinstance(v, CallExpr) and isinstance(v.callee, VariableExpr):
                        if v.callee.name in func_names:
                            graph[current].add(v.callee.name)
                if isinstance(s, IfStmt):
                    walk_tail(s.then_body, current)
                    if s.else_body:
                        walk_tail(s.else_body, current)
                elif isinstance(s, (WhileStmt, ForStmt, DeferStmt, BenchStmt)):
                    walk_tail(s.body, current)
                elif isinstance(s, MatchStmt):
                    for c in s.cases:
                        if len(c) >= 4 and isinstance(c[3], list):
                            walk_tail(c[3], current)
                    if s.default:
                        walk_tail(s.default, current)

        for decl in ast:
            if isinstance(decl, AstFunction) and not getattr(decl, 'type_params', None):
                walk_tail(decl.body, decl.name)

        # Kosaraju
        visited = set()
        order = []
        def dfs1(n):
            visited.add(n)
            for m in graph.get(n, ()):
                if m not in visited:
                    dfs1(m)
            order.append(n)

        for n in func_names:
            if n not in visited:
                dfs1(n)

        rgraph = {n: set() for n in func_names}
        for n, ns in graph.items():
            for m in ns:
                rgraph[m].add(n)

        visited = set()
        sccs = []
        def dfs2(n, comp):
            visited.add(n)
            comp.append(n)
            for m in rgraph.get(n, ()):
                if m not in visited:
                    dfs2(m, comp)

        for n in reversed(order):
            if n not in visited:
                comp = []
                dfs2(n, comp)
                sccs.append(comp)

        return [scc for scc in sccs if len(scc) > 1]

    def _can_dispatcher(self, funcs):
        """Todos os membros do SCC têm assinatura compatível?"""
        if not funcs:
            return False
        sig0 = (
            tuple(p.type_ann for p in funcs[0].params),
            funcs[0].return_type,
        )
        for f in funcs[1:]:
            sig = (
                tuple(p.type_ann for p in f.params),
                f.return_type,
            )
            if sig != sig0:
                return False
        return True

    def _materialize_scc_dispatcher(self, scc_id, funcs):
        """Gera dispatcher + wrappers para um SCC de mutual recursion.

        Estrutura:
          - `__scc_N(i32 id, <params>)` — dispatcher com switch sobre `id`.
          - Para cada `f` do SCC:
              - bloco `__scc_N_<f>` com o corpo, usando `push_context`.
              - wrapper `f_wrap` que chama `__scc_N(idx_f, ...)`.

        PATCH: refatorado para usar `push_context`, e `var_types` agora é
        um **dict** (`{name: type}`) em vez de um **set** (`{type}`).
        """
        sample = funcs[0]
        param_tys = [self.get_llvm_param_type(p.type_ann) for p in sample.params]
        ret_ty = self.get_llvm_param_type(sample.return_type)

        disp_name = f"__scc_{scc_id}"
        disp_fn_ty = ir.FunctionType(ret_ty, [self.i32_ty] + param_tys)
        disp_fn = ir.Function(self.module, disp_fn_ty, name=disp_name)

        # Salva builder externo — restaurado no final.
        old_builder = self.builder

        # ------------------------------------------------------------------
        # Setup do dispatcher (entry + slots + dispatch bb).
        # Feito com um builder próprio, fora do push_context — não é
        # "corpo de função" no sentido do codegen, é boilerplate.
        # ------------------------------------------------------------------
        entry_bb = disp_fn.append_basic_block(name=f"{disp_name}_entry")
        self.builder = ir.IRBuilder(entry_bb)

        slots = []
        for i, p in enumerate(sample.params):
            slot = self.builder.alloca(param_tys[i], name=f"scc_slot_{i}_{p.name}")
            self.builder.store(disp_fn.args[i + 1], slot)
            slots.append(slot)

        id_slot = self.builder.alloca(self.i32_ty, name=f"{disp_name}_id")
        self.builder.store(disp_fn.args[0], id_slot)

        dispatch_bb = disp_fn.append_basic_block(name=f"{disp_name}_dispatch")
        self.builder.branch(dispatch_bb)

        self.builder.position_at_end(dispatch_bb)
        id_val = self.builder.load(id_slot, name=f"{disp_name}_id_load")

        bad_bb = disp_fn.append_basic_block(name=f"{disp_name}_bad")
        sw = self.builder.switch(id_val, bad_bb)

        member_bb = {}
        for idx, f in enumerate(funcs):
            bb = disp_fn.append_basic_block(name=f"{disp_name}_{f.name}")
            sw.add_case(ir.Constant(self.i32_ty, idx), bb)
            member_bb[f.name] = bb

        self.builder.position_at_end(bad_bb)
        self.builder.unreachable()

        scc_slots = {f.name: slots for f in funcs}
        scc_ids = {f.name: idx for idx, f in enumerate(funcs)}

        # ------------------------------------------------------------------
        # Corpos de cada membro — cada um em um `push_context` próprio.
        #
        # PATCH: `var_types` agora é `{param_name: type_ann}` (dict) em
        # vez de `{type_ann}` (set). O bug era silencioso até um membro
        # do SCC chamar função genérica, o que dispara
        # `_infer_arg_type_lumina` → `var_types.get(name)` → crash.
        # ------------------------------------------------------------------
        for idx, f in enumerate(funcs):
            member_builder = ir.IRBuilder(member_bb[f.name])

            with push_context(
                self,
                builder=member_builder,
                symbol_table={p.name: slots[i] for i, p in enumerate(f.params)},
                var_types={p.name: p.type_ann for p in f.params},
                current_func_name=f.name,
                current_body_bb=None,
                defer_stack=[],
                closure_vars=set(),
                _safe_mode=False,
                _current_scc_slots=scc_slots,
                _current_scc_ids=scc_ids,
                _current_scc_id_slot=id_slot,
                _current_scc_dispatch_bb=dispatch_bb,
                _fn_entry_block=member_bb[f.name],  # PATCH
                _fn_return_type=ret_ty,             # PATCH
            ):
                for stmt in f.body:
                    if self.builder.block.is_terminated:
                        break
                    self.visit(stmt)

                if not self.builder.block.is_terminated:
                    self._emit_all_defers()
                if not self.builder.block.is_terminated:
                    if ret_ty == self.void_ty:
                        self.builder.ret_void()
                    elif isinstance(ret_ty, ir.PointerType):
                        self.builder.ret(ir.Constant(ret_ty, None))
                    else:
                        self.builder.ret(ir.Constant(ret_ty, 0))

        # ------------------------------------------------------------------
        # Wrappers: cada `f` original vira um stub que chama o dispatcher
        # com o `id` do membro. Emitidos fora do push_context — é
        # boilerplate de 3 instruções, não corpo de função.
        # ------------------------------------------------------------------
        for idx, f in enumerate(funcs):
            func, func_type = self.functions_table[f.name]
            wbb = func.append_basic_block(name=f"{f.name}_wrap")
            self.builder = ir.IRBuilder(wbb)
            call_args = [ir.Constant(self.i32_ty, idx)] + list(func.args)
            result = self.builder.call(disp_fn, call_args, name=f"{f.name}_scc_call")
            if func_type.return_type == self.void_ty:
                self.builder.ret_void()
            else:
                self.builder.ret(result)

        # Restaura builder externo.
        self.builder = old_builder