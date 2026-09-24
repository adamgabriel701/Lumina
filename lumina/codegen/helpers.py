from llvmlite import ir
from .constants import CLOSURE_BLOCK_SIZE   # ← NOVO


class HelpersCodegen:
    def create_global_string(self, text):
        # Evita erros se chamado antes do setup
        if not hasattr(self, 'string_counter'):
            self.string_counter = 0

        name = f"str_{self.string_counter}"
        self.string_counter += 1
        b = bytearray(text, 'utf-8') + b"\0"
        ty = ir.ArrayType(self.i8_ty, len(b))
        gv = ir.GlobalVariable(self.module, ty, name=name)
        gv.global_constant = True
        gv.initializer = ir.Constant(ty, b)
        if self.builder is None:
            return gv
        return self.builder.bitcast(gv, self.voidptr_ty)

    def to_float_if_needed(self, val):
        if val.type == self.i64_ty:
            return self.builder.sitofp(val, self.f64_ty, name="int_to_float")
        return val

    # ==================================================================
    # Fat pointers para valores `fn`
    #
    # Todos os valores `fn` em Lumina são `{fn_ptr, env_ptr}`. Lambdas com
    # captura usam env != NULL; lambdas sem captura e funções nomeadas usam
    # env = NULL. A invocação sempre passa pelo `_call_closure` (calls.py),
    # que desempacota.
    # ==================================================================
    def _make_fn_wrapper(self, raw_func, name_hint):
        """Gera `i64 __wrapper(i8* env, i64 a1, ..., i64 aN)` que ignora o
        env e chama `raw_func` com os args convertidos.
        """
        inner_ret = raw_func.function_type.return_type
        inner_params = list(raw_func.function_type.args)
        n = len(inner_params)

        wrapper_param_tys = [self.voidptr_ty] + [self.i64_ty] * n
        wrapper_ty = ir.FunctionType(self.i64_ty, wrapper_param_tys)
        wrapper = ir.Function(self.module, wrapper_ty, name=f"{name_hint}__wrapper")

        entry = wrapper.append_basic_block(name="entry")
        builder = ir.IRBuilder(entry)

        call_args = []
        for i, pt in enumerate(inner_params):
            a = wrapper.args[i + 1]
            if a.type != pt:
                if pt == self.f64_ty:
                    a = builder.sitofp(a, pt, name=f"arg{i}_itof")
                elif isinstance(pt, ir.PointerType):
                    a = builder.inttoptr(a, pt, name=f"arg{i}_itop")
                elif isinstance(pt, ir.IntType) and pt.width < 64:
                    a = builder.trunc(a, pt, name=f"arg{i}_trunc")
            call_args.append(a)

        result = builder.call(raw_func, call_args)

        if inner_ret == self.void_ty:
            builder.ret(ir.Constant(self.i64_ty, 0))
        elif result.type == self.i64_ty:
            builder.ret(result)
        elif result.type == self.f64_ty:
            builder.ret(builder.fptosi(result, self.i64_ty, name="ret_ftoi"))
        elif isinstance(result.type, ir.PointerType):
            builder.ret(builder.ptrtoint(result, self.i64_ty, name="ret_ptoi"))
        elif isinstance(result.type, ir.IntType) and result.type.width < 64:
            builder.ret(builder.sext(result, self.i64_ty, name="ret_sext"))
        else:
            builder.ret(ir.Constant(self.i64_ty, 0))

        return wrapper

    def _wrap_fn_as_closure(self, raw_func, name_hint="fn"):
        """Retorna um bloco `{wrapper_fn, NULL}` no heap.

        Usado para (a) funções nomeadas usadas como valor e (b) lambdas
        sem captura — qualquer caso onde não há env para capturar.
        O wrapper gerado adapta a assinatura `i64(i8*, i64, ...)` à
        assinatura original da função.
        """
        key = raw_func.name
        wrapper = self._fn_wrappers.get(key)
        if wrapper is None:
            wrapper = self._make_fn_wrapper(raw_func, key)
            self._fn_wrappers[key] = wrapper

        block = self.builder.call(
            self.malloc,
            [ir.Constant(self.i64_ty, CLOSURE_BLOCK_SIZE)],
            name=f"{name_hint}_closure",
        )
        block_i8pp = self.builder.bitcast(
            block, self.voidptr_ty.as_pointer(), name=f"{name_hint}_i8pp",
        )
        fn_as_ptr = self.builder.bitcast(wrapper, self.voidptr_ty, name=f"{name_hint}_fn")
        self.builder.store(fn_as_ptr, block_i8pp)
        env_slot = self.builder.gep(
            block_i8pp, [ir.Constant(self.i64_ty, 1)],
            name=f"{name_hint}_env_slot",
        )
        self.builder.store(ir.Constant(self.voidptr_ty, None), env_slot)
        return block