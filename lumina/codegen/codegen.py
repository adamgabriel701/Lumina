from llvmlite import ir
from ..ast import Function, StructDecl, ArrayExpr, ImplBlock, CallExpr, ExternDecl, EnumDecl, VarDecl, StringExpr
from .builtins import BuiltinManager
from .expressions import ExpressionCodegen
from .statements import StatementCodegen

class LLVMCodegen(ExpressionCodegen, StatementCodegen):
    def __init__(self):
        self.module = ir.Module(name="lumina_module")
        self.module.triple = "x86_64-pc-linux-gnu"
        self.builder = None
        self.symbol_table = {}
        self.var_types = {}
        self.string_counter = 0
        self.functions_table = {}
        self.array_sizes = {} 
        self.cleanup_vars = [set()]
        self.freed_vars = set()
        
        self.printf, self.scanf, self.atoi, self.sprintf, self.malloc, self.free, self.fopen, self.fgets, self.fputs, self.fclose, self.strlen, self.strcat, self.strdup, self.snprintf, self.strcpy, self.strcmp = BuiltinManager.setup_builtins(self.module)
        
        self.i64_ty = ir.IntType(64)
        self.f64_ty = ir.DoubleType()
        self.i32_ty = ir.IntType(32)
        self.i8_ty = ir.IntType(8)
        self.voidptr_ty = self.i8_ty.as_pointer()
        self.struct_types = {}
        self.struct_fields = {} 
        self.variant_defs = {}
        self.heap_int_arrays = set()
        self.continue_block = None
        self.break_block = None
        self.deferred_stmts = []

    # MÉTODO PARA CRIAR ENUMS ATUALIZADO
    def create_enum(self, node: EnumDecl):
        # Usa IdentifiedStructType para ser compatível com a checagem do VariableExpr
        enum_ty = self.module.context.get_identified_type(node.name)
        enum_ty.set_body(self.i32_ty, self.i64_ty)
        self.struct_types[node.name] = enum_ty
        
        for i, (var_name, payload_type) in enumerate(node.variants):
            self.variant_defs[var_name] = (node.name, i, payload_type)

    def create_global_string(self, text):
        name = f"str_{self.string_counter}"
        self.string_counter += 1
        b = bytearray(text, 'utf-8') + b"\0"
        ty = ir.ArrayType(self.i8_ty, len(b))
        gv = ir.GlobalVariable(self.module, ty, name=name)
        gv.global_constant = True
        gv.initializer = ir.Constant(ty, b)
        
        # CORREÇÃO: Se não houver builder (escopo global), retorna o ponteiro genérico (i8*) direto
        if self.builder is None:
            return gv
        return self.builder.bitcast(gv, self.voidptr_ty)

    def to_float_if_needed(self, val):
        if val.type == self.i64_ty:
            return self.builder.sitofp(val, self.f64_ty, name="int_to_float")
        return val

    # NOVO: Método para limpar variáveis de um escopo
    def cleanup_block(self, vars_set):
        # O Garbage Collector (Boehm GC) agora cuida da memória!
        # Não precisamos mais inserir chamadas de 'free' automáticas (RAII).
        vars_set.clear()

    def get_llvm_type(self, type_name):
        if type_name == "int": return self.i64_ty
        elif type_name == "float": return self.f64_ty
        elif type_name == "str": return self.voidptr_ty 
        # NOVO: ptr é um ponteiro nativo para inteiros (i64*)
        elif type_name == "ptr": return self.i64_ty.as_pointer()
        elif type_name in self.struct_types: return self.struct_types[type_name]
        return self.i64_ty

    def get_llvm_param_type(self, type_name):
        if type_name in self.struct_types: 
            return self.struct_types[type_name].as_pointer()
        return self.get_llvm_type(type_name)

    # NOVO MÉTODO: Tipos dos campos da Struct (Structs aninhadas viram ponteiros!)
    def get_llvm_field_type(self, type_name):
        if type_name in self.struct_types: 
            return self.struct_types[type_name].as_pointer()
        return self.get_llvm_type(type_name)

    def generate_module(self, declarations):
        for decl in declarations:
            if isinstance(decl, StructDecl): self.create_struct(decl)
            elif isinstance(decl, EnumDecl): self.create_enum(decl)
            
        # NOVO: Gera variáveis globais antes das funções
        for decl in declarations:
            if isinstance(decl, VarDecl):
                self.create_global_var(decl)
                
        for decl in declarations:
            if isinstance(decl, Function): self.create_function(decl)
            elif isinstance(decl, ImplBlock):
                for method in decl.methods: self.create_function(method)
            elif isinstance(decl, ExternDecl): self.create_extern(decl)
        return str(self.module)

    # NOVO MÉTODO PARA VARIÁVEIS GLOBAIS
    def create_global_var(self, node):
        if not hasattr(self, 'global_symbols'): 
            self.global_symbols = {}
            self.global_types = {}
            
        if isinstance(node.value, CallExpr) and node.value.name == "alloc":
            ptr = ir.GlobalVariable(self.module, self.i64_ty.as_pointer(), name=node.name)
            ptr.global_constant = False
            ptr.initializer = ir.Constant(self.i64_ty.as_pointer(), None)
            self.global_symbols[node.name] = ptr
            self.global_types[node.name] = self.i64_ty.as_pointer()
            if not hasattr(self, 'global_allocs'): self.global_allocs = []
            self.global_allocs.append(node)
        elif isinstance(node.value, CallExpr) and node.value.name == "alloc_bytes":
            ptr = ir.GlobalVariable(self.module, self.voidptr_ty, name=node.name)
            ptr.global_constant = False
            ptr.initializer = ir.Constant(self.voidptr_ty, None)
            self.global_symbols[node.name] = ptr
            self.global_types[node.name] = self.voidptr_ty
            if not hasattr(self, 'global_allocs'): self.global_allocs = []
            self.global_allocs.append(node)
            
        # NOVO: Trata strings globais (let file = "dados.txt")
        elif isinstance(node.value, StringExpr):
            ptr = ir.GlobalVariable(self.module, self.voidptr_ty, name=node.name)
            ptr.global_constant = False
            ptr.initializer = ir.Constant(self.voidptr_ty, None) # Null pointer temporário
            self.global_symbols[node.name] = ptr
            self.global_types[node.name] = self.voidptr_ty
            if not hasattr(self, 'global_allocs'): self.global_allocs = []
            self.global_allocs.append(node)
            
        else:
            val = self.codegen_expr(node.value) if node.value else ir.Constant(self.i64_ty, 0)
            var_ty = val.type
            if node.var_type == "float":
                var_ty = self.f64_ty
                val = self.to_float_if_needed(val)
            ptr = ir.GlobalVariable(self.module, var_ty, name=node.name)
            ptr.global_constant = False
            ptr.initializer = val
            self.global_symbols[node.name] = ptr
            self.global_types[node.name] = var_ty

    # NOVO MÉTODO PARA FUNÇÕES EXTERNAS
    def create_extern(self, node: ExternDecl):
        ret_ty = self.get_llvm_type(node.return_type)
        param_types = [self.get_llvm_param_type(p_type) for _, p_type in node.params]
        func_type = ir.FunctionType(ret_ty, param_types)
        func = ir.Function(self.module, func_type, name=node.name)
        self.functions_table[node.name] = (func, func_type)

    def create_struct(self, node: StructDecl):
        struct_ty = self.module.context.get_identified_type(node.name)
        self.struct_types[node.name] = struct_ty
        field_tys = [self.get_llvm_field_type(t) for t in node.fields.values()]
        struct_ty.set_body(*field_tys)
        self.struct_fields[node.name] = {name: i for i, name in enumerate(node.fields.keys())}


    def create_function(self, func_node: Function):
        if func_node.name == "main":
            ret_ty = self.i64_ty
            param_types = [self.i32_ty, self.i8_ty.as_pointer().as_pointer()]
            func_type = ir.FunctionType(ret_ty, param_types)
            func = ir.Function(self.module, func_type, name="main")
            block = func.append_basic_block(name="entry")
            self.builder = ir.IRBuilder(block)
            
            # Limpa escopos locais e recarrega globais
            self.symbol_table = {}
            self.var_types = {}
            self.cleanup_vars = [set()]
            self.freed_vars = set()
            self.deferred_stmts = []
            
            # NOVO: Recarrega variáveis globais na tabela de símbolos local
            if hasattr(self, 'global_symbols'):
                self.symbol_table.update(self.global_symbols)
                self.var_types.update(self.global_types)
            
            if len(func_node.params) >= 1:
                p_name = func_node.params[0][0]
                ptr = self.builder.alloca(self.i32_ty, name=p_name)
                self.builder.store(func.args[0], ptr)
                self.symbol_table[p_name] = ptr
                self.var_types[p_name] = self.i32_ty
                
            if len(func_node.params) >= 2:
                p_name = func_node.params[1][0]
                ptr = self.builder.alloca(self.i8_ty.as_pointer().as_pointer(), name=p_name)
                self.builder.store(func.args[1], ptr)
                self.symbol_table[p_name] = ptr
                self.var_types[p_name] = self.i8_ty.as_pointer().as_pointer()
                
            # Inicializa variáveis globais alocadas (alloc/alloc_bytes)
            if hasattr(self, 'global_allocs'):
                for node in self.global_allocs:
                    val = self.codegen_expr(node.value)
                    global_ptr = self.symbol_table.get(node.name)
                    if global_ptr:
                        self.builder.store(val, global_ptr)
        else:
            ret_ty = self.get_llvm_type(func_node.return_type)
            param_types = [self.get_llvm_param_type(p_type) for _, p_type in func_node.params]
            func_type = ir.FunctionType(ret_ty, param_types)
            func = ir.Function(self.module, func_type, name=func_node.name)
            block = func.append_basic_block(name="entry")
            self.builder = ir.IRBuilder(block)
            
            # Limpa escopos locais e recarrega globais
            self.symbol_table = {}
            self.var_types = {}
            self.cleanup_vars = [set()]
            self.freed_vars = set()
            self.deferred_stmts = []
            
            # NOVO: Recarrega variáveis globais na tabela de símbolos local
            if hasattr(self, 'global_symbols'):
                self.symbol_table.update(self.global_symbols)
                self.var_types.update(self.global_types)
            
            for i, (p_name, p_type) in enumerate(func_node.params):
                p_ty = self.get_llvm_param_type(p_type)
                if isinstance(p_ty, ir.PointerType) and isinstance(p_ty.pointee, ir.IdentifiedStructType):
                    self.symbol_table[p_name] = func.args[i]
                    self.var_types[p_name] = p_ty
                else:
                    ptr = self.builder.alloca(p_ty, name=p_name)
                    self.builder.store(func.args[i], ptr)
                    self.symbol_table[p_name] = ptr
                    self.var_types[p_name] = p_ty
                    
        if func_node.name != "main":
            func.attributes.add('alwaysinline')
            func.attributes.add('nounwind')
        else:
            func.attributes.add('nounwind')

        self.functions_table[func_node.name] = (func, func_type)
        for stmt in func_node.body:
            self.codegen_stmt(stmt)
        if not self.builder.block.is_terminated:
            for scope in self.cleanup_vars:
                self.cleanup_block(scope)
            self.builder.ret(ir.Constant(ret_ty, 0))