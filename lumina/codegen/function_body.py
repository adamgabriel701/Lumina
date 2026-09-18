"""Geração do corpo de uma função (entry/body blocks, TCO, @safe, closures)."""
from llvmlite import ir


class FunctionBodyMixin:

    # ==================================================================
    # Corpo de função (com TCO + defers + @safe + closures)
    # ==================================================================
    def generate_function_body(self, node):
        func, func_type = self.functions_table[node.name]

        self.current_func_name = node.name

        old_symtab = self.symbol_table
        old_var_types = self.var_types
        old_body_bb = getattr(self, 'current_body_bb', None)
        old_defer_stack = getattr(self, 'defer_stack', None)
        old_safe = getattr(self, '_safe_mode', False)
        old_closure_vars = self.closure_vars
        self.defer_stack = []
        self.closure_vars = set()

        # Sprint 9a: ativa modo @safe se a função tem @safe
        attrs = getattr(node, 'attrs', None) or []
        self._safe_mode = 'safe' in attrs

        # entry_bb: alloca + store dos args + branch para body_bb.
        # body_bb: onde o corpo é emitido. TCO salta de volta para cá.
        entry_bb = func.append_basic_block(name=f"{node.name}_entry")
        body_bb = func.append_basic_block(name=f"{node.name}_body")

        self.builder = ir.IRBuilder(entry_bb)
        self.symbol_table = {}
        self.var_types = {}

        for i, p in enumerate(node.params):
            p_name, p_type = p.name, p.type_ann
            p_ty = self.get_llvm_param_type(p_type)
            ptr = self.builder.alloca(p_ty, name=p_name)
            self.builder.store(func.args[i], ptr)
            self.symbol_table[p_name] = ptr
            self.var_types[p_name] = p_type

        # Injeta GC_init() no topo de main, antes de qualquer alocação
        # do usuário. Garante que a GC está pronta quando o programa começa.
        if self.use_gc and node.name == "main":
            self.builder.call(self.gc_init, [], name="gc_init_call")

        # NOVO: salva argc/argv em globais para o builtin `argv(i)`.
        # Só se aplica ao `main` sem params (o único que recebe a assinatura
        # C `i32 (i32, i8**)`).
        if (node.name == "main"
                and len(node.params) == 0
                and len(func.args) == 2):
            argc_gv = self.module.globals.get("__lumina_argc")
            argv_gv = self.module.globals.get("__lumina_argv")
            if argc_gv is not None:
                self.builder.store(func.args[0], argc_gv)
            if argv_gv is not None:
                self.builder.store(func.args[1], argv_gv)

        self.builder.branch(body_bb)

        self.builder.position_at_end(body_bb)
        self.current_body_bb = body_bb

        for stmt in node.body:
            if self.builder.block.is_terminated:
                break
            self.visit(stmt)

        if not self.builder.block.is_terminated:
            # Sprint 8b: emite defers pendentes antes do ret de
            # fallthrough. Cobre `fn f(): defer print("x")` sem
            # `return` explícito.
            self._emit_all_defers()

        if not self.builder.block.is_terminated:
            if func_type.return_type == self.void_ty:
                self.builder.ret_void()
            elif isinstance(func_type.return_type, ir.IdentifiedStructType):
                zero_fields = [ir.Constant(ft, 0) for ft in func_type.return_type.elements]
                self.builder.ret(ir.Constant(func_type.return_type, zero_fields))
            elif isinstance(func_type.return_type, ir.PointerType):
                self.builder.ret(ir.Constant(func_type.return_type, None))
            else:
                self.builder.ret(ir.Constant(func_type.return_type, 0))

        self.current_body_bb = old_body_bb
        self.defer_stack = old_defer_stack
        self.symbol_table = old_symtab
        self.var_types = old_var_types
        self._safe_mode = old_safe
        self.closure_vars = old_closure_vars
