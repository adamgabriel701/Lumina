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
            buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 32), name="str_buf")
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
            # getchar() do libc retorna i32 (int do C, com EOF = -1).
            # Lumina's `int` é i64, então sign-extend para casar com
            # o tipo de retorno declarado (`-> int`). `sext` preserva
            # o -1 do EOF.
            return self.builder.sext(raw, self.i64_ty, name="getchar_sext")

        return None
