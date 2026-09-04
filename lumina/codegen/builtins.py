from llvmlite import ir

class BuiltinManager:
    @staticmethod
    def setup_builtins(module):
        voidptr_ty = ir.IntType(8).as_pointer()
        i32_ty = ir.IntType(32)
        i64_ty = ir.IntType(64)
        
        # I/O Padrão
        printf_ty = ir.FunctionType(i32_ty, [voidptr_ty], var_arg=True)
        printf = ir.Function(module, printf_ty, name="printf")
        scanf_ty = ir.FunctionType(i32_ty, [voidptr_ty], var_arg=True)
        scanf = ir.Function(module, scanf_ty, name="scanf")
        
        # Strings
        sprintf_ty = ir.FunctionType(i32_ty, [voidptr_ty, voidptr_ty], var_arg=True)
        sprintf = ir.Function(module, sprintf_ty, name="sprintf")
        atoi_ty = ir.FunctionType(i64_ty, [voidptr_ty])
        atoi = ir.Function(module, atoi_ty, name="atoi")
        strlen_ty = ir.FunctionType(i64_ty, [voidptr_ty])
        strlen_fn = ir.Function(module, strlen_ty, name="strlen")
        
        # Memória - NOVO: Usando GC_malloc do Boehm GC
        malloc_ty = ir.FunctionType(voidptr_ty, [i64_ty])
        malloc_fn = ir.Function(module, malloc_ty, name="GC_malloc")
        
        # Mantemos o free apenas para compatibilidade, mas o GC ignora ele
        free_ty = ir.FunctionType(ir.VoidType(), [voidptr_ty])
        free_fn = ir.Function(module, free_ty, name="free")
        
        # Manipulação de Arquivos
        fopen_ty = ir.FunctionType(voidptr_ty, [voidptr_ty, voidptr_ty])
        fopen = ir.Function(module, fopen_ty, name="fopen")
        fgets_ty = ir.FunctionType(voidptr_ty, [voidptr_ty, i32_ty, voidptr_ty])
        fgets = ir.Function(module, fgets_ty, name="fgets")
        fputs_ty = ir.FunctionType(i32_ty, [voidptr_ty, voidptr_ty])
        fputs = ir.Function(module, fputs_ty, name="fputs")
        fclose_ty = ir.FunctionType(ir.VoidType(), [voidptr_ty])
        fclose = ir.Function(module, fclose_ty, name="fclose")
        
        return printf, scanf, atoi, sprintf, malloc_fn, free_fn, fopen, fgets, fputs, fclose, strlen_fn