from ..builtins import BUILTIN_FUNCTIONS
from llvmlite import ir

from .expressions import ExpressionCodegen
from .statements import StatementCodegen
from .helpers import HelpersCodegen
from .types import TypesCodegen

from ..ast import Function as AstFunction, Param, TraitDecl


class LLVMCodegen(ExpressionCodegen, StatementCodegen, HelpersCodegen, TypesCodegen):
    def __init__(self):
        self.module = ir.Module(name="lumina_module")

        # Consistência com o triple do host — evita o warning
        # "overriding the module target triple" do clang.
        try:
            from llvmlite.binding import get_default_triple
            self.module.triple = get_default_triple()
        except Exception:
            pass

        self.i64_ty = ir.IntType(64)
        self.i32_ty = ir.IntType(32)
        self.f64_ty = ir.DoubleType()
        self.i8_ty = ir.IntType(8)
        self.voidptr_ty = self.i8_ty.as_pointer()
        self.void_ty = ir.VoidType()

        self.builder = None
        self.functions_table = {}
        self.function_defs = {}
        self.struct_types = {}
        self.struct_fields = {}
        self.struct_defs = {}
        self.symbol_table = {}
        self.var_types = {}
        self.global_var_decls = {}   # NOVO: top-level constants
        self.global_mut_vars = {}    # NOVO: nome → GlobalVariable

        self.string_counter = 0
        self.lambda_counter = 0
        self.heap_allocs = set()

        self.builtin_functions = BUILTIN_FUNCTIONS

        self.setup_libc_functions()
        self.alias_methods = set()   # NOVO: nomes curtos de trait methods

    def setup_libc_functions(self):
        printf_ty = ir.FunctionType(ir.IntType(32), [self.i8_ty.as_pointer()], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, name="printf")

        malloc_ty = ir.FunctionType(self.i8_ty.as_pointer(), [ir.IntType(64)])
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

    def _emit_mutable_global(self, decl):
        """Emite uma GlobalVariable LLVM para `mut X = <literal>` no topo.

        Suporta inicializadores constantes: NumberExpr, BoolExpr.
        Inicializadores complexos (StringExpr, CallExpr, etc.) caem
        para inline (comportamento antigo — não reatribuível).
        """
        from ..ast import NumberExpr, BoolExpr

        name = decl.name

        # Determina tipo
        var_type = decl.var_type
        if var_type is None:
            v = decl.value
            if isinstance(v, NumberExpr):
                var_type = "float" if v.is_float else "int"
            elif isinstance(v, BoolExpr):
                var_type = "bool"
            else:
                # Não suportado como global mutável — cai para inline
                self.global_var_decls[name] = decl
                return

        llvm_ty = self.get_llvm_type(var_type)
        if isinstance(llvm_ty, ir.VoidType) or isinstance(llvm_ty, ir.PointerType):
            # void ou ptr (str) — cai para inline
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

    def _const_from_literal(self, node, llvm_ty):
        """Avalia um literal como constante LLVM. Retorna None se não
        for literal."""
        from ..ast import NumberExpr, BoolExpr
        if isinstance(node, NumberExpr):
            if isinstance(llvm_ty, ir.DoubleType):
                return ir.Constant(llvm_ty, float(node.value))
            return ir.Constant(llvm_ty, int(node.value, 0))
        if isinstance(node, BoolExpr):
            return ir.Constant(llvm_ty, 1 if node.value else 0)
        return None

    def _resolve_trait_defaults(self, ast):
        """Copia métodos default do trait para o ImplBlock que não os sobrescreve.

        Roda ANTES de registrar funções, tanto no semantic quanto no codegen,
        pra que `Struct_metodo` exista nos dois lados.
        """
        traits_by_name = {}
        for decl in ast:
            if hasattr(decl, 'methods') and not hasattr(decl, 'struct_name'):
                traits_by_name[decl.name] = decl

        for decl in ast:
            if not (hasattr(decl, 'methods') and hasattr(decl, 'struct_name')):
                continue
            trait_name = getattr(decl, 'trait_name', None)
            if not trait_name or trait_name not in traits_by_name:
                continue

            trait_def = traits_by_name[trait_name]
            explicit_names = {m.name for m in decl.methods}

            for trait_method in trait_def.methods:
                full_name = f"{decl.struct_name}_{trait_method.name}"
                if full_name in explicit_names:
                    continue
                if not trait_method.body:
                    continue

                default_method = AstFunction(
                    full_name,
                    [Param('self', decl.struct_name)] + list(trait_method.params),
                    trait_method.return_type,
                    list(trait_method.body),
                )
                decl.methods.append(default_method)

    def generate_module(self, ast):
        # 0. Coleta VarDecls de topo.
        #
        #   - `let X = <literal>` (imutável) → inline como constante
        #   - `mut X = <literal>` (mutável)  → GlobalVariable LLVM
        #
        # Top-level `let` continua inline para performance; mutáveis
        # precisam de endereço real (podem ser reatribuídos em runtime).
        self.global_var_decls = {}
        self.global_mut_vars = {}
        for decl in ast:
            if type(decl).__name__ == 'VarDecl' and getattr(decl, 'value', None) is not None:
                if getattr(decl, 'is_mutable', False):
                    self._emit_mutable_global(decl)
                else:
                    self.global_var_decls[decl.name] = decl

        # 1. Pré-registra todas as structs e enums
        for decl in ast:
            if hasattr(decl, 'name') and decl.name in self.struct_defs:
                continue
            if hasattr(decl, 'fields') and not hasattr(decl, 'variants'):
                self.register_struct(decl)
            elif hasattr(decl, 'variants'):
                self.register_enum(decl)

        # 1.5. Resolve métodos default de traits
        self._resolve_trait_defaults(ast)

        # 2. Pré-registra todas as funções e métodos de impls.
        # TraitDecl NÃO é registrado — seus métodos são copiados para
        # os ImplBlocks por `_resolve_trait_defaults`.
        for decl in ast:
            if isinstance(decl, TraitDecl):
                continue
            if hasattr(decl, 'params') and hasattr(decl, 'return_type'):
                self.register_function(decl)
            elif hasattr(decl, 'methods'):
                for method in decl.methods:
                    self.register_function(method)

        # 2.5 Registra aliases `metodo` → `Struct_metodo` para traits.
        # Também marca em `alias_methods` para que o codegen saiba
        # que essas chamadas precisam de `self` como 1º argumento.
        #
        # Importante: pass 2 já registrou o método ABSTRATO do TraitDecl
        # com o nome curto (`name`), e agora o pass 2.5 sobrescreve com
        # a implementação CONCRETA (`English_name`). Por isso NÃO
        # verificamos `short not in functions_table` — sempre
        # sobrescrevemos.
        self.alias_methods = set()
        for decl in ast:
            if not (hasattr(decl, 'methods') and hasattr(decl, 'struct_name')):
                continue
            trait_name = getattr(decl, 'trait_name', None)
            if not trait_name:
                continue
            for method in decl.methods:
                parts = method.name.split('_', 1)
                if len(parts) == 2:
                    short = parts[1]
                    full_entry = self.functions_table.get(method.name)
                    if full_entry:
                        self.functions_table[short] = full_entry
                        self.alias_methods.add(short)

        # 3. Gera o corpo das funções e métodos de impls.
        # TraitDecl NÃO gera corpo — seus métodos default são copiados
        # para os ImplBlocks.
        for decl in ast:
            if isinstance(decl, TraitDecl):
                continue
            if hasattr(decl, 'body') and decl.body is not None:
                if getattr(decl, 'type_params', None):
                    continue
                self.generate_function_body(decl)
            elif hasattr(decl, 'methods'):
                for method in decl.methods:
                    if hasattr(method, 'body') and method.body is not None:
                        if getattr(method, 'type_params', None):
                            continue
                        self.generate_function_body(method)

        return str(self.module)

    def register_struct(self, node):
        if node.name in self.struct_types:
            return
        struct_ty = self.module.context.get_identified_type(node.name)
        self.struct_types[node.name] = struct_ty
        self.struct_defs[node.name] = node

        field_tys = []
        for ft in node.fields.values():
            if ft in self.struct_types:
                field_tys.append(self.struct_types[ft].as_pointer())
            else:
                field_tys.append(self.get_llvm_type(ft))

        struct_ty.set_body(*field_tys)
        self.struct_fields[node.name] = {name: i for i, name in enumerate(node.fields.keys())}

    def _enum_max_payloads(self, node):
        """Descobre o número máximo de payloads entre as variantes de um enum."""
        max_p = 0
        for variant in node.variants:
            if len(variant) < 2:
                continue
            v_payloads = variant[1]
            if isinstance(v_payloads, list):
                max_p = max(max_p, len(v_payloads))
            elif v_payloads is not None:
                max_p = max(max_p, 1)
        return max_p

    def register_enum(self, node):
        if node.name in self.struct_types:
            return
        # Layout: { i32 tag, i64 payload_0, i64 payload_1, ..., i64 payload_{N-1} }
        # N = max payloads entre todas as variantes. Para enums de 1 payload
        # (Result, Option), o layout é idêntico ao antigo {i32, i64}.
        struct_ty = self.module.context.get_identified_type(node.name)
        self.struct_types[node.name] = struct_ty
        self.struct_defs[node.name] = node

        max_p = self._enum_max_payloads(node)
        fields = [ir.IntType(32)] + [ir.IntType(64)] * max_p
        struct_ty.set_body(*fields)

        fields_map = {"tag": 0}
        for i in range(max_p):
            fields_map[f"payload_{i}"] = i + 1
        if max_p >= 1:
            fields_map["payload"] = 1  # alias retrocompatível
        self.struct_fields[node.name] = fields_map

    def register_function(self, node):
        # Funções genéricas NÃO são registradas — materializadas on-demand
        if getattr(node, 'type_params', None):
            self.function_defs[node.name] = node
            return

        func_name = getattr(node, 'module_prefix', '') + node.name if hasattr(node, 'module_prefix') else node.name

        if func_name in self.functions_table:
            return

        ret_ty = self.get_llvm_param_type(node.return_type)
        param_types = []
        for p in node.params:
            p_name, p_type, p_default = p.name, p.type_ann, p.default
            p_ty = self.get_llvm_param_type(p_type)
            param_types.append(p_ty)

        func_type = ir.FunctionType(ret_ty, param_types)
        func = ir.Function(self.module, func_type, name=func_name)
        self.functions_table[func_name] = (func, func_type)
        self.functions_table[node.name] = (func, func_type)
        self.function_defs[node.name] = node

    def _llvm_ty_to_str(self, t):
        if t == self.i64_ty:
            return "int"
        if t == self.f64_ty:
            return "float"
        if t == self.voidptr_ty:
            return "str"
        if isinstance(t, ir.IntType) and t.width == 1:
            return "bool"
        if isinstance(t, ir.PointerType):
            return "ptr"
        return "unknown"

    def materialize_generic(self, gen_def, arg_types):
        """Gera (uma vez) uma cópia especializada da função genérica
        para os tipos concretos em `arg_types`. Retorna o nome mangled.
        """
        mangled = gen_def.name + "__" + "_".join(self._llvm_ty_to_str(t) for t in arg_types)

        if mangled in self.functions_table:
            return mangled

        type_params = getattr(gen_def, 'type_params', None) or []
        type_map = {}
        for p, t in zip(gen_def.params, arg_types):
            if p.type_ann in type_params:
                type_map[p.type_ann] = t

        def resolve_ty(name):
            if name in type_map:
                return type_map[name]
            return self.get_llvm_param_type(name)

        ret_ty = resolve_ty(gen_def.return_type)
        param_tys = [resolve_ty(p.type_ann) for p in gen_def.params]

        func_type = ir.FunctionType(ret_ty, param_tys)
        func = ir.Function(self.module, func_type, name=mangled)
        self.functions_table[mangled] = (func, func_type)
        self.function_defs[mangled] = gen_def

        old_builder = self.builder
        old_symtab = self.symbol_table
        old_var_types = self.var_types
        old_current = getattr(self, 'current_func_name', None)

        block = func.append_basic_block(name=f"{mangled}_entry")
        self.builder = ir.IRBuilder(block)
        self.symbol_table = {}
        self.var_types = {}
        self.current_func_name = mangled

        for i, p in enumerate(gen_def.params):
            p_name = p.name
            p_ty = func_type.args[i]
            ptr = self.builder.alloca(p_ty, name=p_name)
            self.builder.store(func.args[i], ptr)
            self.symbol_table[p_name] = ptr
            self.var_types[p_name] = self._llvm_ty_to_str(p_ty)

        for stmt in gen_def.body:
            self.visit(stmt)

        if not self.builder.block.is_terminated:
            if func_type.return_type == self.void_ty:
                self.builder.ret_void()
            elif isinstance(func_type.return_type, ir.PointerType):
                self.builder.ret(ir.Constant(func_type.return_type, None))
            else:
                self.builder.ret(ir.Constant(func_type.return_type, 0))

        self.builder = old_builder
        self.symbol_table = old_symtab
        self.var_types = old_var_types
        self.current_func_name = old_current

        return mangled

    def generate_function_body(self, node):
        func, func_type = self.functions_table[node.name]

        self.current_func_name = node.name

        old_symtab = self.symbol_table
        old_var_types = self.var_types

        block = func.append_basic_block(name=f"{node.name}_entry")
        self.builder = ir.IRBuilder(block)
        self.symbol_table = {}
        self.var_types = {}

        for i, p in enumerate(node.params):
            p_name, p_type = p.name, p.type_ann
            p_ty = self.get_llvm_param_type(p_type)
            ptr = self.builder.alloca(p_ty, name=p_name)
            self.builder.store(func.args[i], ptr)
            self.symbol_table[p_name] = ptr
            self.var_types[p_name] = p_type

        for stmt in node.body:
            self.visit(stmt)

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

        self.symbol_table = old_symtab
        self.var_types = old_var_types

    def codegen_stmt(self, node):
        return self.visit(node)

    def codegen_expr(self, node):
        return self.visit(node)