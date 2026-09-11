from llvmlite import ir

from .expressions import ExpressionCodegen
from .statements import StatementCodegen
from .helpers import HelpersCodegen
from .types import TypesCodegen

class LLVMCodegen(ExpressionCodegen, StatementCodegen, HelpersCodegen, TypesCodegen):
    def __init__(self):
        # Contexto e Módulo LLVM
        self.module = ir.Module(name="lumina_module")
        
        # Tipos básicos
        self.i64_ty = ir.IntType(64)
        self.i32_ty = ir.IntType(32)
        self.f64_ty = ir.DoubleType()
        self.i8_ty = ir.IntType(8)
        self.voidptr_ty = self.i8_ty.as_pointer()
        self.void_ty = ir.VoidType()
        
        # Estado do Builder e Tabelas de Símbolos
        self.builder = None
        self.functions_table = {}      # Nome -> (ir.Function, ir.FunctionType)
        self.function_defs = {}       # Nome -> AST Function node
        self.struct_types = {}        # Nome -> ir.IdentifiedStructType
        self.struct_fields = {}       # Nome -> {field_name: index}
        self.struct_defs = {}         # Nome -> AST StructDecl node
        self.symbol_table = {}        # Variável -> ir.AllocaInstr
        self.var_types = {}           # Variável -> Tipo (str)
        
        # Contadores e Helpers
        self.string_counter = 0
        self.lambda_counter = 0
        self.heap_allocs = set()
        
        # Registra as funções padrão da libc (printf, malloc, etc.)
        self.setup_libc_functions()
        
    def setup_libc_functions(self):
        # printf(format, ...) -> int
        printf_ty = ir.FunctionType(ir.IntType(32), [self.i8_ty.as_pointer()], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, name="printf")
        
        # malloc(size) -> void*
        malloc_ty = ir.FunctionType(self.i8_ty.as_pointer(), [ir.IntType(64)])
        self.malloc = ir.Function(self.module, malloc_ty, name="malloc")
        
        # free(void*) -> void
        free_ty = ir.FunctionType(ir.VoidType(), [self.i8_ty.as_pointer()])
        self.free = ir.Function(self.module, free_ty, name="free")
        
        # strcpy(dest, src) -> char*
        strcpy_ty = ir.FunctionType(self.i8_ty.as_pointer(), [self.i8_ty.as_pointer(), self.i8_ty.as_pointer()])
        self.strcpy = ir.Function(self.module, strcpy_ty, name="strcpy")
        
        # strcat(dest, src) -> char*
        strcat_ty = ir.FunctionType(self.i8_ty.as_pointer(), [self.i8_ty.as_pointer(), self.i8_ty.as_pointer()])
        self.strcat = ir.Function(self.module, strcat_ty, name="strcat")
        
        # strlen(str) -> size_t
        strlen_ty = ir.FunctionType(ir.IntType(64), [self.i8_ty.as_pointer()])
        self.strlen = ir.Function(self.module, strlen_ty, name="strlen")
        
        # snprintf(buf, size, format, ...) -> int
        snprintf_ty = ir.FunctionType(ir.IntType(32), [self.i8_ty.as_pointer(), ir.IntType(64), self.i8_ty.as_pointer()], var_arg=True)
        self.snprintf = ir.Function(self.module, snprintf_ty, name="snprintf")

    def generate_module(self, ast):
        # 1. Pré-registra todas as structs e enums
        for decl in ast:
            if hasattr(decl, 'name') and decl.name in self.struct_defs:
                continue
            if hasattr(decl, 'fields') and not hasattr(decl, 'variants'): # É um StructDecl
                self.register_struct(decl)
            elif hasattr(decl, 'variants'): # É um EnumDecl
                self.register_enum(decl)
                
        # 2. Pré-registra todas as funções e métodos de traits/impls
        for decl in ast:
            if hasattr(decl, 'params') and hasattr(decl, 'return_type'): # É uma Function ou ExternDecl
                self.register_function(decl)
                
        # 3. Gera o corpo das funções
        for decl in ast:
            if hasattr(decl, 'body') and decl.body is not None: # É uma Function
                self.generate_function_body(decl)
                
        return str(self.module)

    def register_struct(self, node):
        if node.name in self.struct_types: return
        struct_ty = self.module.context.get_identified_type(node.name)
        self.struct_types[node.name] = struct_ty
        self.struct_defs[node.name] = node
        
        field_tys = [self.get_llvm_type(ft) for ft in node.fields.values()]
        struct_ty.set_body(*field_tys)
        self.struct_fields[node.name] = {name: i for i, name in enumerate(node.fields.keys())}

    def register_enum(self, node):
        if node.name in self.struct_types: return
        # Enums são representados como uma struct contendo um tag (i32) e um union (i64)
        struct_ty = self.module.context.get_identified_type(node.name)
        self.struct_types[node.name] = struct_ty
        self.struct_defs[node.name] = node
        struct_ty.set_body(ir.IntType(32), ir.IntType(64))
        self.struct_fields[node.name] = {"tag": 0, "payload": 1}

    def register_function(self, node):
        if node.name in self.functions_table: return
        
        ret_ty = self.get_llvm_type(node.return_type)
        param_types = []
        for p_name, p_type, p_default in node.params:
            p_ty = self.get_llvm_param_type(p_type)
            param_types.append(p_ty)
            
        func_type = ir.FunctionType(ret_ty, param_types)
        func = ir.Function(self.module, func_type, name=node.name)
        self.functions_table[node.name] = (func, func_type)
        self.function_defs[node.name] = node

    def generate_function_body(self, node):
        func, func_type = self.functions_table[node.name]
        
        # NOVO: Define o nome da função atual para o ReturnStmt saber o tipo de retorno
        self.current_func_name = node.name
        
        # Salva o escopo anterior
        old_symtab = self.symbol_table
        old_var_types = self.var_types
        
        block = func.append_basic_block(name=f"{node.name}.entry")
        self.builder = ir.IRBuilder(block)
        self.symbol_table = {}
        self.var_types = {}
        
        # Aloca e armazena os parâmetros na memória local
        for i, (p_name, p_type, _) in enumerate(node.params):
            p_ty = self.get_llvm_param_type(p_type)
            ptr = self.builder.alloca(p_ty, name=p_name)
            self.builder.store(func.args[i], ptr)
            self.symbol_table[p_name] = ptr
            self.var_types[p_name] = p_type
            
        # Gera os statements da função
        for stmt in node.body:
            self.codegen_stmt(stmt)
            
        # Adiciona um return vazio/0 se a função não terminar explicitamente
        if not self.builder.block.is_terminated:
            if func_type.return_type == self.void_ty:
                self.builder.ret_void()
            else:
                self.builder.ret(ir.Constant(func_type.return_type, 0))
                
        # Restaura o escopo
        self.symbol_table = old_symtab
        self.var_types = old_var_types