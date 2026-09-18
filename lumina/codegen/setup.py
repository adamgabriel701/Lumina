"""Setup inicial: assinaturas libc/GC e globais mutáveis."""
from llvmlite import ir


class SetupMixin:

    # ==================================================================
    # Setup de funções libc/GC
    # ==================================================================
    def setup_libc_functions(self):
        printf_ty = ir.FunctionType(ir.IntType(32), [self.i8_ty.as_pointer()], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, name="printf")

        # Alocador: GC_malloc quando use_gc, malloc (libc) caso contrário.
        # Ambos têm assinatura `i8* (i64)`.
        malloc_ty = ir.FunctionType(self.i8_ty.as_pointer(), [ir.IntType(64)])
        if self.use_gc:
            self.malloc = ir.Function(self.module, malloc_ty, name="GC_malloc")

            gc_init_ty = ir.FunctionType(ir.VoidType(), [])
            self.gc_init = ir.Function(self.module, gc_init_ty, name="GC_init")

            free_ty = ir.FunctionType(ir.VoidType(), [self.i8_ty.as_pointer()])
            self.free = ir.Function(self.module, free_ty, name="GC_free")
        else:
            self.malloc = ir.Function(self.module, malloc_ty, name="malloc")

            free_ty = ir.FunctionType(ir.VoidType(), [self.i8_ty.as_pointer()])
            self.free = ir.Function(self.module, free_ty, name="free")

        strcpy_ty = ir.FunctionType(self.i8_ty.as_pointer(), [self.i8_ty.as_pointer(), self.i8_ty.as_pointer()])
        self.strcpy = ir.Function(self.module, strcpy_ty, name="strcpy")

        strcat_ty = ir.FunctionType(self.i8_ty.as_pointer(), [self.i8_ty.as_pointer(), self.i8_ty.as_pointer()])
        self.strcat = ir.Function(self.module, strcat_ty, name="strcat")

        strlen_ty = ir.FunctionType(ir.IntType(64), [self.i8_ty.as_pointer()])
        self.strlen = ir.Function(self.module, strlen_ty, name="strlen")

        snprintf_ty = ir.FunctionType(
            ir.IntType(32),
            [self.i8_ty.as_pointer(), ir.IntType(64), self.i8_ty.as_pointer()],
            var_arg=True,
        )
        self.snprintf = ir.Function(self.module, snprintf_ty, name="snprintf")

        strstr_ty = ir.FunctionType(self.i8_ty.as_pointer(), [self.i8_ty.as_pointer(), self.i8_ty.as_pointer()])
        self.strstr = ir.Function(self.module, strstr_ty, name="strstr")

        strncmp_ty = ir.FunctionType(
            ir.IntType(32),
            [self.i8_ty.as_pointer(), self.i8_ty.as_pointer(), ir.IntType(64)],
        )
        self.strncmp = ir.Function(self.module, strncmp_ty, name="strncmp")

        atoi_ty = ir.FunctionType(ir.IntType(64), [self.i8_ty.as_pointer()])
        self.atoi = ir.Function(self.module, atoi_ty, name="atoi")

        strcmp_ty = ir.FunctionType(ir.IntType(32), [self.i8_ty.as_pointer(), self.i8_ty.as_pointer()])
        self.strcmp = ir.Function(self.module, strcmp_ty, name="strcmp")

        strncpy_ty = ir.FunctionType(
            self.i8_ty.as_pointer(),
            [self.i8_ty.as_pointer(), self.i8_ty.as_pointer(), ir.IntType(64)],
        )
        self.strncpy = ir.Function(self.module, strncpy_ty, name="strncpy")

        # NOVO: FILE* globals do libc (stdin/stdout/stderr).
        # Declarados como GlobalVariable externa (sem inicializer) —
        # o linker resolve contra o libc.
        for name in ("stdin", "stdout", "stderr"):
            if name not in self.module.globals:
                gv = ir.GlobalVariable(self.module, self.voidptr_ty, name=name)
                gv.linkage = "external"

    # ==================================================================
    # Globais mutáveis (top-level `mut X = 0`)
    # ==================================================================
    def _emit_mutable_global(self, decl):
        """Emite uma GlobalVariable LLVM para `mut X = <literal>` no topo.

        Suporta inicializadores constantes: NumberExpr, BoolExpr.
        Inicializadores complexos (StringExpr, CallExpr, etc.) caem
        para inline (comportamento antigo — não reatribuível).
        """
        from ..ast import NumberExpr, BoolExpr

        name = decl.name

        var_type = decl.var_type
        if var_type is None:
            v = decl.value
            if isinstance(v, NumberExpr):
                var_type = "float" if v.is_float else "int"
            elif isinstance(v, BoolExpr):
                var_type = "bool"
            else:
                self.global_var_decls[name] = decl
                return

        llvm_ty = self.get_llvm_type(var_type)
        if isinstance(llvm_ty, ir.VoidType) or isinstance(llvm_ty, ir.PointerType):
            self.global_var_decls[name] = decl
            return

        gv = ir.GlobalVariable(self.module, llvm_ty, name=f"g_{name}")

        initial = None
        if isinstance(decl.value, NumberExpr):
            if isinstance(llvm_ty, ir.DoubleType):
                initial = ir.Constant(llvm_ty, float(decl.value.value))
            else:
                try:
                    initial = ir.Constant(llvm_ty, int(decl.value.value, 0))
                except (ValueError, TypeError):
                    initial = ir.Constant(llvm_ty, 0)
        elif isinstance(decl.value, BoolExpr):
            initial = ir.Constant(llvm_ty, 1 if decl.value.value else 0)

        if initial is None:
            initial = ir.Constant(llvm_ty, 0)

        gv.initializer = initial
        gv.linkage = "internal"
        self.global_mut_vars[name] = gv
