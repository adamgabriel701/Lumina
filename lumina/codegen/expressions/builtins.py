"""Builtins simples: I/O de console, memória, conversões.

Cada builtin retorna o valor LLVM gerado, ou `None` se o nome não
corresponde a nenhum builtin desta categoria. O dispatcher em `calls.py`
chama este método e, se receber `None`, tenta os builtins de arquivo
(`io_builtins.py`) e depois a resolução normal de função.
"""
from llvmlite import ir


class BuiltinsMixin:

    def _call_builtin_impl(self, func_name, node):
        if func_name == "print":
            for i, arg_node in enumerate(node.args):
                val = self.visit(arg_node)
                if i > 0:
                    self.builder.call(
                        self.printf, [self.create_global_string(" ")], name="print_sep",
                    )
                if val.type == self.i64_ty:
                    self.builder.call(
                        self.printf, [self.create_global_string("%ld"), val],
                        name="print_call",
                    )
                elif val.type == self.f64_ty:
                    self.builder.call(
                        self.printf, [self.create_global_string("%f"), val],
                        name="print_call",
                    )
                elif val.type == self.i32_ty:
                    self.builder.call(
                        self.printf, [self.create_global_string("%d"), val],
                        name="print_call",
                    )
                elif isinstance(val.type, ir.IntType) and val.type.width == 1:
                    true_str = self.create_global_string("true")
                    false_str = self.create_global_string("false")
                    val = self.builder.select(val, true_str, false_str, name="print_bool")
                    self.builder.call(
                        self.printf, [self.create_global_string("%s"), val],
                        name="print_call",
                    )
                elif isinstance(val.type, ir.IntType) and val.type.width < 64:
                    val = self.builder.zext(val, self.i64_ty, name="print_zext")
                    self.builder.call(
                        self.printf, [self.create_global_string("%ld"), val],
                        name="print_call",
                    )
                else:
                    if isinstance(val.type, ir.PointerType) and val.type != self.voidptr_ty:
                        val = self.builder.bitcast(val, self.voidptr_ty, name="print_cast")
                    self.builder.call(
                        self.printf, [self.create_global_string("%s"), val],
                        name="print_call",
                    )
            self.builder.call(
                self.printf, [self.create_global_string("\n")], name="print_nl",
            )
            return ir.Constant(self.i64_ty, 0)

        if func_name == "len":
            arg = self.visit(node.args[0])
            if arg.type == self.voidptr_ty or (
                isinstance(arg.type, ir.PointerType) and arg.type.pointee == self.i8_ty
            ):
                return self.builder.call(self.strlen, [arg], name="len_str")
            return ir.Constant(self.i64_ty, 0)

        if func_name == "alloc":
            n = self.visit(node.args[0])
            if n.type != self.i64_ty:
                n = self.builder.sext(n, self.i64_ty, name="alloc_sext")
            size = self.builder.mul(n, ir.Constant(self.i64_ty, 8), name="alloc_size")
            return self.builder.call(self.malloc, [size], name="alloc_call")

        if func_name == "alloc_bytes":
            n = self.visit(node.args[0])
            if n.type != self.i64_ty:
                n = self.builder.sext(n, self.i64_ty, name="alloc_bytes_sext")
            return self.builder.call(self.malloc, [n], name="alloc_bytes_call")

        if func_name == "free":
            ptr = self.visit(node.args[0])
            if not isinstance(ptr.type, ir.PointerType):
                ptr = self.builder.inttoptr(ptr, self.voidptr_ty, name="free_cast")
            elif ptr.type != self.voidptr_ty:
                ptr = self.builder.bitcast(ptr, self.voidptr_ty, name="free_bitcast")
            self.builder.call(self.free, [ptr], name="free_call")
            return ir.Constant(self.i64_ty, 0)

        if func_name == "chr":
            c = self.visit(node.args[0])
            if c.type != self.i64_ty:
                c = self.builder.sext(c, self.i64_ty, name="chr_sext")
            c_i8 = self.builder.trunc(c, self.i8_ty, name="chr_trunc")
            buf = self.builder.call(
                self.malloc, [ir.Constant(self.i64_ty, 2)], name="chr_buf",
            )
            buf_i8 = self.builder.bitcast(buf, self.i8_ty.as_pointer(), name="chr_i8_ptr")
            self.builder.store(c_i8, buf_i8)
            null_ptr = self.builder.gep(
                buf_i8, [ir.Constant(self.i64_ty, 1)], name="chr_null_ptr",
            )
            self.builder.store(ir.Constant(self.i8_ty, 0), null_ptr)
            return buf_i8

        if func_name == "atoi":
            s = self.visit(node.args[0])
            if not isinstance(s.type, ir.PointerType):
                s = self.builder.inttoptr(s, self.voidptr_ty, name="atoi_cast")
            return self.builder.call(self.atoi, [s], name="atoi_call")

        if func_name == "black_box":
            v = self.visit(node.args[0])
            if v.type != self.i64_ty:
                if isinstance(v.type, ir.PointerType):
                    v = self.builder.ptrtoint(v, self.i64_ty, name="bb_ptoi")
                elif v.type == self.f64_ty:
                    v = self.builder.bitcast(v, self.i64_ty, name="bb_bitcast")
                elif isinstance(v.type, ir.IntType) and v.type.width < 64:
                    v = self.builder.sext(v, self.i64_ty, name="bb_sext")
            asm_ty = ir.FunctionType(self.i64_ty, [self.i64_ty])
            asm = ir.InlineAsm(asm_ty, "", "=r,0", side_effect=True)
            return self.builder.call(asm, [v], name="black_box_call")

        if func_name == "int":
            v = self.visit(node.args[0])
            if v.type == self.voidptr_ty:
                return self.builder.call(self.atoi, [v], name="int_from_str")
            return v

        if func_name == "float":
            v = self.visit(node.args[0])
            if v.type == self.i64_ty:
                return self.builder.sitofp(v, self.f64_ty, name="float_from_int")
            return v

        if func_name == "str":
            v = self.visit(node.args[0])
            if v.type == self.voidptr_ty:
                return v
            if v.type == self.f64_ty:
                fmt = self.create_global_string("%f")
            elif v.type == self.i64_ty:
                fmt = self.create_global_string("%ld")
            else:
                return v
            buf = self._fn_emit_alloca("str_buf", ir.ArrayType(self.i8_ty, 32))
            buf_ptr = self.builder.bitcast(buf, self.voidptr_ty, name="str_buf_ptr")
            self.builder.call(
                self.snprintf,
                [buf_ptr, ir.Constant(self.i64_ty, 32), fmt, v],
                name="str_snprintf",
            )
            return buf_ptr

        # FILE* globals do libc
        if func_name in ("stdin", "stdout", "stderr"):
            gv = self.module.globals.get(func_name)
            if gv is None:
                gv = ir.GlobalVariable(self.module, self.voidptr_ty, name=func_name)
                gv.linkage = "external"
            return self.builder.load(gv, name=f"{func_name}_load")

        if func_name == "fgets":
            buf = self.visit(node.args[0])
            size = self.visit(node.args[1])
            stream = self.visit(node.args[2])
            if not isinstance(buf.type, ir.PointerType):
                buf = self.builder.inttoptr(buf, self.i8_ty.as_pointer(), name="fgets_buf")
            if size.type != self.i32_ty:
                size = self.builder.trunc(size, self.i32_ty, name="fgets_size")
            if not isinstance(stream.type, ir.PointerType):
                stream = self.builder.inttoptr(stream, self.i8_ty.as_pointer(), name="fgets_stream")
            fgets_ty = ir.FunctionType(
                self.voidptr_ty, [self.i8_ty.as_pointer(), self.i32_ty, self.voidptr_ty],
            )
            fgets_fn = self.module.globals.get("fgets") or ir.Function(
                self.module, fgets_ty, name="fgets",
            )
            return self.builder.call(fgets_fn, [buf, size, stream], name="fgets_call")

        if func_name == "fputs":
            s = self.visit(node.args[0])
            stream = self.visit(node.args[1])
            if not isinstance(s.type, ir.PointerType):
                s = self.builder.inttoptr(s, self.i8_ty.as_pointer(), name="fputs_s")
            if not isinstance(stream.type, ir.PointerType):
                stream = self.builder.inttoptr(stream, self.voidptr_ty, name="fputs_stream")
            fputs_ty = ir.FunctionType(self.i32_ty, [self.i8_ty.as_pointer(), self.voidptr_ty])
            fputs_fn = self.module.globals.get("fputs") or ir.Function(
                self.module, fputs_ty, name="fputs",
            )
            return self.builder.call(fputs_fn, [s, stream], name="fputs_call")

        if func_name == "fflush":
            stream = self.visit(node.args[0])
            if not isinstance(stream.type, ir.PointerType):
                stream = self.builder.inttoptr(stream, self.voidptr_ty, name="fflush_stream")
            fflush_ty = ir.FunctionType(self.i32_ty, [self.voidptr_ty])
            fflush_fn = self.module.globals.get("fflush") or ir.Function(
                self.module, fflush_ty, name="fflush",
            )
            return self.builder.call(fflush_fn, [stream], name="fflush_call")

        if func_name == "getchar":
            getchar_ty = ir.FunctionType(self.i32_ty, [])
            getchar_fn = self.module.globals.get("getchar") or ir.Function(
                self.module, getchar_ty, name="getchar",
            )
            raw = self.builder.call(getchar_fn, [], name="getchar_call")
            return self.builder.sext(raw, self.i64_ty, name="getchar_sext")

        # ==================================================================
        # FIX P: `argv(i)` com bounds-check.
        #
        # Antes: `elem_ptr = gep(argv, [idx])`, `load` cego. Se o programa
        # rodava sem argumentos (argc=1), `argv(1)` lia `argv[1] = NULL`
        # e retornava NULL. Chamadas subsequentes como `len(argv(1))`
        # faziam `strlen(NULL)` → SIGSEGV.
        #
        # Isso afetava TODOS os benchmarks parametrizados por argv
        # (`fib.lm`, `primes.lm`, etc.) quando rodados sem argumentos.
        #
        # Agora: 3 guards em runtime. Se qualquer for verdadeiro, retorna
        # "" (empty string) em vez de NULL:
        #   1. `argv == NULL` — main ainda não rodou (JIT, REPL edge case)
        #   2. `idx < 0`       — índice negativo é sempre inválido
        #   3. `idx >= argc`   — fora do alcance (inclui o NULL terminador)
        #
        # Retornar "" em vez de NULL é importante porque `len("")` funciona
        # (retorna 0), enquanto `len(NULL)` é UB.
        # ==================================================================
        if func_name == "argv":
            idx = self.visit(node.args[0])
            if idx.type != self.i64_ty:
                idx = self.builder.sext(idx, self.i64_ty, name="argv_sext")

            # Fallback seguro: string vazia. Uma por call site — o linker
            # deduplica se rodar via clang; via lumina-ld, o custo é
            # alguns bytes a mais por `argv(i)`.
            empty_str = self.create_global_string("")

            argv_gv = self.module.globals.get("__lumina_argv")
            if argv_gv is None:
                # Sem `main` registrado: não há como argv estar setado.
                return empty_str

            argv_val = self.builder.load(argv_gv, name="argv_load")
            argv_ptr_ty = self.i8_ty.as_pointer().as_pointer()

            # Guard 1: argv == NULL.
            null_ptr = ir.Constant(argv_ptr_ty, None)
            is_null = self.builder.icmp_signed(
                "==", argv_val, null_ptr, name="argv_isnull",
            )

            # Guard 2: idx < 0.
            zero = ir.Constant(self.i64_ty, 0)
            is_neg = self.builder.icmp_signed(
                "<", idx, zero, name="argv_isneg",
            )

            invalid = self.builder.or_(is_null, is_neg, name="argv_invalid")

            # Guard 3: idx >= argc (só se `__lumina_argc` estiver
            # disponível — só existe se `main` foi registrado).
            argc_gv = self.module.globals.get("__lumina_argc")
            if argc_gv is not None:
                argc_i32 = self.builder.load(argc_gv, name="argc_load")
                argc_i64 = self.builder.sext(argc_i32, self.i64_ty, name="argc_sext")
                is_oob = self.builder.icmp_signed(
                    ">=", idx, argc_i64, name="argv_oob",
                )
                invalid = self.builder.or_(
                    invalid, is_oob, name="argv_invalid2",
                )

            empty_bb = self.builder.append_basic_block(name="argv_empty")
            ok_bb    = self.builder.append_basic_block(name="argv_ok")
            end_bb   = self.builder.append_basic_block(name="argv_end")

            self.builder.cbranch(invalid, empty_bb, ok_bb)

            self.builder.position_at_end(empty_bb)
            self.builder.branch(end_bb)

            self.builder.position_at_end(ok_bb)
            elem_ptr = self.builder.gep(argv_val, [idx], name="argv_elem_ptr")
            real_result = self.builder.load(elem_ptr, name="argv_elem")
            self.builder.branch(end_bb)

            self.builder.position_at_end(end_bb)
            phi = self.builder.phi(self.voidptr_ty, name="argv_result")
            phi.add_incoming(empty_str, empty_bb)
            phi.add_incoming(real_result, ok_bb)
            return phi

        return None