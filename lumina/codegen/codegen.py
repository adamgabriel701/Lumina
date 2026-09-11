from llvmlite import ir

from lumina.ast.statements import TraitDecl
from ..ast import Function, StructDecl, ArrayExpr, ImplBlock, CallExpr, ExternDecl, EnumDecl, VarDecl, StringExpr, NumberExpr, BoolExpr, BinaryExpr, VariableExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, TupleExpr, UnaryExpr, PropagateExpr, ComptimeExpr
from .builtins import BuiltinManager
from .helpers import HelpersCodegen
from .types import TypesCodegen
from .access import AccessCodegen
from .expressions import ExpressionCodegen
from .native import NativeCallCodegen
from .statements import StatementCodegen

class LLVMCodegen(HelpersCodegen, TypesCodegen, AccessCodegen, ExpressionCodegen, NativeCallCodegen, StatementCodegen):
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
        self.is_tail_return = False
        self.escapes = set()
        self.global_symbols = {}
        self.global_types = {}
        self.lambda_counter = 0
        
        # NOVO: Estado do Debug Info (DWARF)
        # Precisa ser definido antes do bloco 'if' abaixo
        self.is_debug = getattr(self, 'is_debug', False)
        self.di_cu = None
        self.di_file = None
        
        if self.is_debug:
            self.module.add_debug_info("Dwarf Version", "4")
            self.module.add_debug_info("Debug Info Version", "3")
            self.di_file = self.module.add_debug_info("DIFile", {
                "filename": "lumina_module.lm",
                "directory": "/"
            })
            self.di_cu = self.module.add_debug_info("DICompileUnit", {
                "language": ir.DIToken("DW_LANG_C99"),
                "file": self.di_file,
                "producer": "Lumina Compiler",
                "runtimeVersion": 0,
                "isOptimized": True,
                "emissionKind": ir.DIToken("FullDebug"),
            })

    def generate_module(self, declarations):
        self.struct_defs = {d.name: d for d in declarations if isinstance(d, StructDecl)}
        self.function_defs = {d.name: d for d in declarations if isinstance(d, Function)}
        self.trait_defs = {d.name: d for d in declarations if isinstance(d, TraitDecl)} # Garanta que isto está aqui
        
        for decl in declarations:
            if isinstance(decl, StructDecl): self.create_struct(decl)
            elif isinstance(decl, EnumDecl): self.create_enum(decl)
            
        for decl in declarations:
            if isinstance(decl, VarDecl): self.create_global_var(decl)
            
        # 1. Cria os protótipos de todas as funções declaradas
        for decl in declarations:
            if isinstance(decl, Function): self.create_function_prototype(decl)
            elif isinstance(decl, ImplBlock):
                for method in decl.methods: self.create_function_prototype(method)
            elif isinstance(decl, ExternDecl): self.create_extern(decl)
                
        # NOVO: 1.5. Injeta e cria protótipos dos métodos padrão de Traits ANTES de gerar qualquer corpo!
        for decl in declarations:
            if isinstance(decl, ImplBlock) and decl.trait_name:
                trait_def = self.trait_defs.get(decl.trait_name)
                if trait_def:
                    for trait_method in trait_def.methods:
                        expected_name = f"{decl.struct_name}_{trait_method.name}"
                        if expected_name not in self.function_defs and trait_method.body:
                            trait_method.name = expected_name
                            self.function_defs[expected_name] = trait_method
                            self.create_function_prototype(trait_method)
                            
        # 2. Gera os corpos (IR) de todas as funções (incluindo as injetadas)
        for decl in declarations:
            if isinstance(decl, Function): self.generate_function_body(decl)
            elif isinstance(decl, ImplBlock):
                for method in decl.methods: self.generate_function_body(method)
                
        # Gera os corpos dos métodos padrão injetados
        for decl in declarations:
            if isinstance(decl, ImplBlock) and decl.trait_name:
                trait_def = self.trait_defs.get(decl.trait_name)
                if trait_def:
                    for trait_method in trait_def.methods:
                        expected_name = f"{decl.struct_name}_{trait_method.name}"
                        if expected_name not in [m.name for m in decl.methods] and trait_method.body:
                            self.generate_function_body(trait_method)
                            
        return str(self.module)

    def cleanup_block(self, vars_set): vars_set.clear()

    def create_struct(self, node):
        if node.name in self.struct_types: return  # NOVO: Evita redefinir a mesma struct
        
        struct_ty = self.module.context.get_identified_type(node.name)
        self.struct_types[node.name] = struct_ty
        field_tys = [self.get_llvm_field_type(t) for t in node.fields.values()]
        struct_ty.set_body(*field_tys)
        self.struct_fields[node.name] = {name: i for i, name in enumerate(node.fields.keys())}

    def create_enum(self, node):
        if node.name in self.struct_types: return
        enum_ty = self.module.context.get_identified_type(node.name)
        enum_ty.set_body(self.i32_ty, self.i64_ty) # Tag e Payload (sempre i64, cabem int e ptr)
        self.struct_types[node.name] = enum_ty
        for i, (var_name, payload_type) in enumerate(node.variants):
            self.variant_defs[var_name] = (node.name, i, payload_type)

    def create_extern(self, node):
        # Se a função já foi declarada, não duplica
        for func in self.module.functions:
            if func.name == node.name: return
            
        ret_ty = self.get_llvm_type(node.return_type)
        param_types = [self.get_llvm_param_type(p_type) for _, p_type in node.params]
        func_type = ir.FunctionType(ret_ty, param_types)
        func = ir.Function(self.module, func_type, name=node.name)
        
        # NOVO: Se for um import do WASM, adiciona o atributo de import
        if getattr(node, 'is_wasm', False):
            # wasm-ld procura por funções externas não definidas no módulo
            pass # O linker resolve isso automaticamente se passarmos --allow-undefined
            
        self.functions_table[node.name] = (func, func_type)

    def create_global_var(self, node):
        if not hasattr(self, 'global_symbols'): 
            self.global_symbols = {}
            self.global_types = {}
            
        if isinstance(node.value, CallExpr) and node.value.name in ("alloc", "alloc_bytes"):
            # NOVO: Se for alloc, é um ponteiro de int (i64*). Se for alloc_bytes, é void* (i8*)
            is_alloc = node.value.name == "alloc"
            ptr_ty = self.i64_ty.as_pointer() if is_alloc else self.voidptr_ty
            
            ptr = ir.GlobalVariable(self.module, ptr_ty, name=node.name)
            ptr.global_constant = False
            ptr.initializer = ir.Constant(ptr_ty, None)
            self.global_symbols[node.name] = ptr
            self.global_types[node.name] = ptr_ty
            
            if not hasattr(self, 'global_allocs'): self.global_allocs = []
            self.global_allocs.append(node)
            
        elif isinstance(node.value, StringExpr):
            ptr = ir.GlobalVariable(self.module, self.voidptr_ty, name=node.name)
            ptr.global_constant = False
            ptr.initializer = ir.Constant(self.voidptr_ty, None)
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

    def create_function(self, func_node: Function):
        if func_node.name == "main":
            is_wasm = getattr(self, 'is_wasm', False)
            ret_ty = self.i32_ty if is_wasm else self.i64_ty
            self.current_ret_ty = ret_ty
            
            if is_wasm:
                param_types = []
            else:
                param_types = [self.i32_ty, self.i8_ty.as_pointer().as_pointer()]
                
            func_type = ir.FunctionType(ret_ty, param_types)
            func = ir.Function(self.module, func_type, name="main")
            block = func.append_basic_block(name="entry"); self.builder = ir.IRBuilder(block)
            self.symbol_table = {}; self.var_types = {}
            self.cleanup_vars = [set()]; self.freed_vars = set(); self.deferred_stmts = []
            
            # NOVO: Debug Info para o main
            if self.is_debug and self.di_cu:
                di_sp = self.module.add_debug_info("DISubprogram", {
                    "name": "main", "linkageName": "main",
                    "scope": self.di_cu, "file": self.di_file,
                    "line": func_node.line, "type": None,
                    "isLocal": False, "isDefinition": True, "scopeLine": func_node.line,
                    "isOptimized": True, "unit": self.di_cu,
                })
                func.set_metadata("dbg", di_sp)
                self.builder.debug_metadata = di_sp

            if hasattr(self, 'global_symbols'):
                self.symbol_table.update(self.global_symbols); self.var_types.update(self.global_types)
                
            if not is_wasm:
                ptr_argc = self.builder.alloca(self.i32_ty, name="argc_ptr")
                self.builder.store(func.args[0], ptr_argc)
                self.symbol_table['argc'] = ptr_argc
                self.var_types['argc'] = self.i32_ty
                
                ptr_argv = self.builder.alloca(self.i8_ty.as_pointer().as_pointer(), name="argv_ptr")
                self.builder.store(func.args[1], ptr_argv)
                self.symbol_table['argv'] = ptr_argv
                self.var_types['argv'] = self.i8_ty.as_pointer().as_pointer()
                
                if len(func_node.params) >= 1:
                    p_name = func_node.params[0][0]
                    self.symbol_table[p_name] = ptr_argc
                    self.var_types[p_name] = self.i32_ty
                if len(func_node.params) >= 2:
                    p_name = func_node.params[1][0]
                    self.symbol_table[p_name] = ptr_argv
                    self.var_types[p_name] = self.i8_ty.as_pointer().as_pointer()

            if hasattr(self, 'global_allocs'):
                for node in self.global_allocs:
                    val = self.codegen_expr(node.value); global_ptr = self.symbol_table.get(node.name)
                    if global_ptr: self.builder.store(val, global_ptr)
        else:
            ret_ty = self.get_llvm_type(func_node.return_type); self.current_ret_ty = ret_ty
            param_types = [self.get_llvm_param_type(p[1]) for p in func_node.params]
            func_type = ir.FunctionType(ret_ty, param_types)
            func = ir.Function(self.module, func_type, name=func_node.name)
            block = func.append_basic_block(name="entry"); self.builder = ir.IRBuilder(block)
            self.symbol_table = {}; self.var_types = {}
            self.cleanup_vars = [set()]; self.freed_vars = set(); self.deferred_stmts = []
            
            # NOVO: Debug Info para funções normais
            if self.is_debug and self.di_cu:
                di_sp = self.module.add_debug_info("DISubprogram", {
                    "name": func_node.name, "linkageName": func_node.name,
                    "scope": self.di_cu, "file": self.di_file,
                    "line": func_node.line, "type": None,
                    "isLocal": False, "isDefinition": True, "scopeLine": func_node.line,
                    "isOptimized": True, "unit": self.di_cu,
                })
                func.set_metadata("dbg", di_sp)
                self.builder.debug_metadata = di_sp

            if hasattr(self, 'global_symbols'):
                self.symbol_table.update(self.global_symbols); self.var_types.update(self.global_types)
            for i, param in enumerate(func_node.params):
                p_name, p_type = param[0], param[1]; p_ty = self.get_llvm_param_type(p_type)
                if isinstance(p_ty, ir.PointerType) and isinstance(p_ty.pointee, ir.IdentifiedStructType):
                    self.symbol_table[p_name] = func.args[i]; self.var_types[p_name] = p_ty
                else:
                    ptr = self.builder.alloca(p_ty, name=p_name); self.builder.store(func.args[i], ptr)
                    self.symbol_table[p_name] = ptr; self.var_types[p_name] = p_ty
                    
        if func_node.name != "main": func.attributes.add('alwaysinline'); func.attributes.add('nounwind')
        else: func.attributes.add('nounwind')
        self.functions_table[func_node.name] = (func, func_type)
        for stmt in func_node.body: self.codegen_stmt(stmt)
        
        if not self.builder.block.is_terminated:
            for scope in self.cleanup_vars: self.cleanup_block(scope)
            if ret_ty == ir.VoidType(): self.builder.ret_void()
            elif isinstance(ret_ty, ir.PointerType): self.builder.ret(ir.Constant(ret_ty, None))
            else: self.builder.ret(ir.Constant(ret_ty, 0))

    def create_function_prototype(self, func_node: Function):
        if func_node.name == "main":
            is_wasm = getattr(self, 'is_wasm', False)
            ret_ty = self.i32_ty if is_wasm else self.i64_ty
            if is_wasm:
                param_types = []
            else:
                param_types = [self.i32_ty, self.i8_ty.as_pointer().as_pointer()]
            func_type = ir.FunctionType(ret_ty, param_types)
            func = ir.Function(self.module, func_type, name="main")
            self.functions_table[func_node.name] = (func, func_type)
        else:
            ret_ty = self.get_llvm_type(func_node.return_type)
            param_types = [self.get_llvm_param_type(p[1]) for p in func_node.params]
            func_type = ir.FunctionType(ret_ty, param_types)
            func = ir.Function(self.module, func_type, name=func_node.name)
            if func_node.name != "main": 
                func.attributes.add('alwaysinline')
                func.attributes.add('nounwind')
            self.functions_table[func_node.name] = (func, func_type)

    def generate_function_body(self, func_node: Function):
        func, func_type = self.functions_table[func_node.name]
        block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        
        self.current_ret_ty = func_type.return_type
        self.symbol_table = {}; self.var_types = {}
        self.cleanup_vars = [set()]; self.freed_vars = set(); self.deferred_stmts = []
        
        # NOVO: Guarda o contexto da struct atual (ex: "English" em "English_greet")
        self.current_struct_name = None
        if "_" in func_node.name:
            parts = func_node.name.split("_")
            base_name = parts[0]
            if base_name in self.struct_defs:
                self.current_struct_name = base_name

        if self.is_debug and self.di_cu:
            di_sp = self.module.add_debug_info("DISubprogram", {
                "name": func_node.name, "linkageName": func_node.name,
                "scope": self.di_cu, "file": self.di_file,
                "line": getattr(func_node, 'line', 0), "type": None,
                "isLocal": False, "isDefinition": True, "scopeLine": getattr(func_node, 'line', 0),
                "isOptimized": True, "unit": self.di_cu,
            })
            func.set_metadata("dbg", di_sp)
            self.builder.debug_metadata = di_sp

        if hasattr(self, 'global_symbols'):
            self.symbol_table.update(self.global_symbols); self.var_types.update(self.global_types)
            
        if func_node.name == "main":
            is_wasm = getattr(self, 'is_wasm', False)
            if not is_wasm:
                ptr_argc = self.builder.alloca(self.i32_ty, name="argc_ptr")
                self.builder.store(func.args[0], ptr_argc)
                self.symbol_table['argc'] = ptr_argc
                self.var_types['argc'] = self.i32_ty
                
                ptr_argv = self.builder.alloca(self.i8_ty.as_pointer().as_pointer(), name="argv_ptr")
                self.builder.store(func.args[1], ptr_argv)
                self.symbol_table['argv'] = ptr_argv
                self.var_types['argv'] = self.i8_ty.as_pointer().as_pointer()
                
                if len(func_node.params) >= 1:
                    p_name = func_node.params[0][0]
                    self.symbol_table[p_name] = ptr_argc
                    self.var_types[p_name] = self.i32_ty
                if len(func_node.params) >= 2:
                    p_name = func_node.params[1][0]
                    self.symbol_table[p_name] = ptr_argv
                    self.var_types[p_name] = self.i8_ty.as_pointer().as_pointer()

            if hasattr(self, 'global_allocs'):
                for node in self.global_allocs:
                    val = self.codegen_expr(node.value); global_ptr = self.symbol_table.get(node.name)
                    if global_ptr: self.builder.store(val, global_ptr)
        else:
            for i, param in enumerate(func_node.params):
                p_name, p_type = param[0], param[1]; p_ty = self.get_llvm_param_type(p_type)
                if isinstance(p_ty, ir.PointerType) and isinstance(p_ty.pointee, ir.IdentifiedStructType):
                    self.symbol_table[p_name] = func.args[i]; self.var_types[p_name] = p_ty
                else:
                    ptr = self.builder.alloca(p_ty, name=p_name); self.builder.store(func.args[i], ptr)
                    self.symbol_table[p_name] = ptr; self.var_types[p_name] = p_ty
                    
        for stmt in func_node.body: self.codegen_stmt(stmt)
        
        if not self.builder.block.is_terminated:
            for scope in self.cleanup_vars: self.cleanup_block(scope)
            if self.current_ret_ty == ir.VoidType(): self.builder.ret_void()
            elif isinstance(self.current_ret_ty, ir.PointerType): self.builder.ret(ir.Constant(self.current_ret_ty, None))
            else: self.builder.ret(ir.Constant(self.current_ret_ty, 0))