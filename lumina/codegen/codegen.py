from ..builtins import BUILTIN_FUNCTIONS
from llvmlite import ir

from .expressions import ExpressionCodegen
from .statements import StatementCodegen
from .helpers import HelpersCodegen
from .types import TypesCodegen

from ..ast import Function as AstFunction, Param, TraitDecl
from ..semantic.types import substitute_generic, unify_type


class LLVMCodegen(ExpressionCodegen, StatementCodegen, HelpersCodegen, TypesCodegen):
    def __init__(self, target_triple=None, use_gc=True):
        # Contexto LLVM próprio por instância. Sem isso, `ir.Module()`
        # usa o `global_context` do llvmlite, e tipos identificados
        # (struct/enum) vazam entre instâncias — recompilar a mesma
        # struct dispara "P is already defined". Isso afetava o REPL
        # (que recompila tudo a cada célula). Funções não sofrem
        # porque `ir.Function(self.module, ...)` é criada no módulo,
        # não no context.
        self.context = ir.Context()
        self.module = ir.Module(name="lumina_module", context=self.context)

        # Consistência com o triple do alvo (ou do host, se não
        # especificado). Evita o warning "overriding the module
        # target triple" do clang e é essencial para cross-compile.
        try:
            from llvmlite.binding import get_default_triple
            self.module.triple = target_triple or get_default_triple()
        except Exception:
            pass

        self.use_gc = use_gc

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
        self.global_var_decls = {}   # top-level constants
        self.global_mut_vars = {}    # nome → GlobalVariable

        self.string_counter = 0
        self.lambda_counter = 0
        self.heap_allocs = set()

        self.array_lengths = {}   # nome → N (para `for x in arr`)

        self.builtin_functions = BUILTIN_FUNCTIONS

        # Sprint 2e/8b/8d: controle de loop (continue_bb, break_bb, scope_start)
        self.loop_stack = []
        # Sprint 8b: pilha de defers (escopos + função)
        self.defer_stack = []
        # Sprint 2e: bloco do corpo da função atual (para TCO)
        self.current_body_bb = None

        # Sprint 9a: null check em MemberExpr/IndexExpr quando @safe
        self._safe_mode = False
        # Sprint 9b: macros (@macro) para expansão de AST
        self.macros = {}

        # Sprint 8c: estado do dispatcher SCC em construção
        self._current_scc_slots = None
        self._current_scc_ids = None
        self._current_scc_id_slot = None
        self._current_scc_dispatch_bb = None

        self.setup_libc_functions()
        self.alias_methods = set()   # nomes curtos de trait methods

        self.freed_vars = set()   # populado pelo compile_lumina

        self.closure_vars = set()   # variáveis que seguram closures

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

    # ==================================================================
    # Trait defaults
    # ==================================================================
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

    def _validate_macro(self, fn):
        """Macro deve ter corpo `return <expr>` (1 statement)."""
        from ..errors import LuminaError

        body = fn.body or []
        if len(body) != 1 or type(body[0]).__name__ != 'ReturnStmt':
            raise LuminaError(
                f"Macro '{fn.name}' deve ter corpo `return <expr>` "
                f"(um único statement). Macros multi-statement não são "
                f"suportadas.",
                filename="<macro>",
                line=getattr(fn, 'line', 0) or 0,
                col=getattr(fn, 'col', 0) or 0,
                source_code="",
            )
        if not body[0].values:
            raise LuminaError(
                f"Macro '{fn.name}' deve retornar uma expressão "
                f"(`return <expr>`).",
                filename="<macro>",
                line=getattr(fn, 'line', 0) or 0,
                col=getattr(fn, 'col', 0) or 0,
                source_code="",
            )

    # ==================================================================
    # Geração do módulo
    # ==================================================================
    def generate_module(self, ast):
        # 0. Coleta VarDecls de topo.
        self.global_var_decls = {}
        self.global_mut_vars = {}
        for decl in ast:
            if type(decl).__name__ == 'VarDecl' and getattr(decl, 'value', None) is not None:
                if getattr(decl, 'is_mutable', False):
                    self._emit_mutable_global(decl)
                else:
                    self.global_var_decls[decl.name] = decl

        # 0b. Sprint 9b: coleta macros (@macro). Não são registradas
        # como funções normais — só expandem em call sites.
        # Valida aqui (não só no call site) para que macros malformadas
        # falhem mesmo se nunca chamadas.
        self.macros = {}
        for decl in ast:
            if isinstance(decl, AstFunction):
                attrs = getattr(decl, 'attrs', None) or []
                if 'macro' in attrs:
                    self._validate_macro(decl)
                    self.macros[decl.name] = decl

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
        # TraitDecl NÃO é registrado.
        # Macros NÃO são registradas como funções normais.
        for decl in ast:
            if isinstance(decl, TraitDecl):
                continue
            if hasattr(decl, 'params') and hasattr(decl, 'return_type'):
                if isinstance(decl, AstFunction) and decl.name in self.macros:
                    continue
                self.register_function(decl)
            elif hasattr(decl, 'methods'):
                for method in decl.methods:
                    self.register_function(method)

        # 2.5 Registra aliases `metodo` → `Struct_metodo` para traits.
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

        # 3. Sprint 8c: detecta SCCs de tail calls (mutual recursion)
        # e gera dispatchers.
        sccs = self._compute_tail_call_sccs(ast)
        handled_scc_members = set()
        for scc_id, members in enumerate(sccs):
            funcs = [
                d for d in ast
                if isinstance(d, AstFunction)
                and d.name in members
                and not getattr(d, 'type_params', None)
            ]
            if len(funcs) < 2:
                continue
            if not self._can_dispatcher(funcs):
                continue
            self._materialize_scc_dispatcher(scc_id, funcs)
            handled_scc_members.update(f.name for f in funcs)

        # 3b. Gera o corpo das funções restantes.
        for decl in ast:
            if isinstance(decl, TraitDecl):
                continue
            if hasattr(decl, 'body') and decl.body is not None:
                if getattr(decl, 'type_params', None):
                    continue
                if isinstance(decl, AstFunction) and decl.name in self.macros:
                    continue
                if isinstance(decl, AstFunction) and decl.name in handled_scc_members:
                    continue
                self.generate_function_body(decl)
            elif hasattr(decl, 'methods'):
                for method in decl.methods:
                    if hasattr(method, 'body') and method.body is not None:
                        if getattr(method, 'type_params', None):
                            continue
                        self.generate_function_body(method)

        return str(self.module)

    # ==================================================================
    # Registro de structs/enums/funções
    # ==================================================================
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
        # Layout: { i32 tag, i64 payload_0, ..., i64 payload_{N-1} }
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

        # Sprint 10: aplica atributos LLVM por função
        attrs = getattr(node, 'attrs', None) or []
        self._apply_llvm_attrs(func, attrs)

    def _apply_llvm_attrs(self, func, attrs):
        """Aplica atributos LLVM a uma função (`@inline`, `@noinline`,
        `@cold`, `@hot`).

        Attrs devem ser uma lista de strings (Sprint 9a — `parse_function`
        passa strings, não tuples). Aceita também tuple por robustez.
        """
        # Normaliza: aceita ['inline'] ou [('inline', [])]
        names = set()
        for a in attrs:
            if isinstance(a, tuple):
                names.add(a[0])
            else:
                names.add(a)

        if 'inline' in names and 'noinline' in names:
            from ..errors import LuminaError
            raise LuminaError(
                f"Função '{func.name}' tem @inline e @noinline — conflitante.",
                filename="<codegen>",
                line=0, col=0, source_code="",
            )

        if 'inline' in names:
            func.attributes.add('alwaysinline')
        if 'noinline' in names:
            func.attributes.add('noinline')
        if 'cold' in names:
            func.attributes.add('cold')
        if 'hot' in names:
            # NOTA: o LLVM tem `hot` como STRING attribute, não enum.
            # O llvmlite não expõe API para string attributes em
            # `Function.attributes`. Mapeamos `@hot` para `inlinehint`
            # — mesma intenção semântica ("função quente, boa candidata
            # a inline"). Se o llvmlite ganhar suporte futuro, trocar
            # por string `"hot"`.
            func.attributes.add('inlinehint')

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

    # ==================================================================
    # Sprint 7a: materialize_generic + inferência de type_map
    # ==================================================================
    def materialize_generic(self, gen_def, type_map):
        """Gera cópia especializada de uma função genérica.

        `type_map`: dict {type_param_name: tipo_concreto_lumina}.
        Ex: materialize_generic(put_def, {"T": "int"}) gera `put__int`.
        """
        type_params = getattr(gen_def, 'type_params', None) or []

        def _sanitize(s):
            return s.replace("<", "_").replace(">", "").replace(",", "_").replace(" ", "")
        suffix_parts = [_sanitize(type_map.get(tp, "unknown")) for tp in type_params]
        mangled = f"{gen_def.name}__{'_'.join(suffix_parts)}"

        if mangled in self.functions_table:
            return mangled

        def resolve_lumina(name):
            return substitute_generic(name, type_map)

        ret_lumina = resolve_lumina(gen_def.return_type)
        ret_ty = self.get_llvm_param_type(ret_lumina)

        param_tys = []
        for p in gen_def.params:
            param_lumina = resolve_lumina(p.type_ann)
            param_tys.append(self.get_llvm_param_type(param_lumina))

        func_type = ir.FunctionType(ret_ty, param_tys)
        func = ir.Function(self.module, func_type, name=mangled)
        self.functions_table[mangled] = (func, func_type)
        self.function_defs[mangled] = gen_def

        # Sprint 10: aplica attrs também na cópia especializada
        attrs = getattr(gen_def, 'attrs', None) or []
        self._apply_llvm_attrs(func, attrs)

        # Salva/restaura estado
        old_builder = self.builder
        old_symtab = self.symbol_table
        old_var_types = self.var_types
        old_current = getattr(self, 'current_func_name', None)
        old_body_bb = getattr(self, 'current_body_bb', None)
        old_defer_stack = getattr(self, 'defer_stack', None)
        old_safe = getattr(self, '_safe_mode', False)
        self.defer_stack = []
        self._safe_mode = False   # genéricos não têm attrs

        entry_bb = func.append_basic_block(name=f"{mangled}_entry")
        body_bb = func.append_basic_block(name=f"{mangled}_body")
        self.builder = ir.IRBuilder(entry_bb)
        self.symbol_table = {}
        self.var_types = {}
        self.current_func_name = mangled

        for i, p in enumerate(gen_def.params):
            p_name = p.name
            param_lumina = resolve_lumina(p.type_ann)
            p_ty = func_type.args[i]
            ptr = self.builder.alloca(p_ty, name=p_name)
            self.builder.store(func.args[i], ptr)
            self.symbol_table[p_name] = ptr
            self.var_types[p_name] = param_lumina

        self.builder.branch(body_bb)
        self.builder.position_at_end(body_bb)
        self.current_body_bb = body_bb

        for stmt in gen_def.body:
            if self.builder.block.is_terminated:
                break
            self.visit(stmt)

        if not self.builder.block.is_terminated:
            self._emit_all_defers()
        if not self.builder.block.is_terminated:
            if func_type.return_type == self.void_ty:
                self.builder.ret_void()
            elif isinstance(func_type.return_type, ir.PointerType):
                self.builder.ret(ir.Constant(func_type.return_type, None))
            else:
                self.builder.ret(ir.Constant(func_type.return_type, 0))

        self.builder = old_builder
        self.defer_stack = old_defer_stack
        self.symbol_table = old_symtab
        self.var_types = old_var_types
        self.current_func_name = old_current
        self.current_body_bb = old_body_bb
        self._safe_mode = old_safe

        return mangled

    def _infer_arg_type_lumina(self, arg_node):
        """Best-effort: infere tipo Lumina de um argumento."""
        from ..ast import VariableExpr, NumberExpr, StringExpr, BoolExpr, CallExpr, StructLiteralExpr
        if isinstance(arg_node, VariableExpr):
            return self.var_types.get(arg_node.name)
        if isinstance(arg_node, NumberExpr):
            return "float" if arg_node.is_float else "int"
        if isinstance(arg_node, StringExpr):
            return "str"
        if isinstance(arg_node, BoolExpr):
            return "bool"
        if isinstance(arg_node, StructLiteralExpr):
            return arg_node.struct_name
        if isinstance(arg_node, CallExpr):
            callee_name = None
            if isinstance(arg_node.callee, VariableExpr):
                callee_name = arg_node.callee.name
            elif hasattr(arg_node.callee, 'member'):
                callee_name = arg_node.callee.member
            if callee_name and callee_name in self.function_defs:
                return self.function_defs[callee_name].return_type
            if callee_name:
                lookup = self._find_enum_variant(callee_name)
                if lookup is not None:
                    return lookup[0]
        return None

    def _infer_type_map_lumina(self, gen_def, node):
        """Unifica (param.type_ann, arg_type_lumina) para inferir type_map.

        Retorna dict ou {} se falhar (aí cai no caminho antigo).
        """
        type_map = {}
        for arg_node, param in zip(node.args, gen_def.params):
            arg_type = self._infer_arg_type_lumina(arg_node)
            if arg_type is None:
                return {}
            if not unify_type(param.type_ann, arg_type, type_map):
                return {}
        return type_map

    # ==================================================================
    # Sprint 8c: SCCs de tail calls + dispatcher
    # ==================================================================
    def _compute_tail_call_sccs(self, ast):
        """SCCs do grafo de tail calls entre funções top-level.

        Retorna `[[name1, name2, ...], ...]` — cada sub-lista é um
        SCC com >= 2 membros. Self-recursion (tamanho 1) é tratada
        pelo `_try_tail_call` existente e NÃO aparece aqui.
        """
        from ..ast import (
            CallExpr, VariableExpr, ReturnStmt,
            IfStmt, WhileStmt, ForStmt, MatchStmt, DeferStmt, BenchStmt,
        )

        func_names = set()
        for decl in ast:
            if isinstance(decl, AstFunction) and not getattr(decl, 'type_params', None):
                func_names.add(decl.name)

        graph = {n: set() for n in func_names}

        def walk_tail(stmts, current):
            for s in stmts:
                if s is None:
                    continue
                if isinstance(s, ReturnStmt) and len(s.values) == 1:
                    v = s.values[0]
                    if isinstance(v, CallExpr) and isinstance(v.callee, VariableExpr):
                        if v.callee.name in func_names:
                            graph[current].add(v.callee.name)
                if isinstance(s, IfStmt):
                    walk_tail(s.then_body, current)
                    if s.else_body:
                        walk_tail(s.else_body, current)
                elif isinstance(s, (WhileStmt, ForStmt, DeferStmt, BenchStmt)):
                    walk_tail(s.body, current)
                elif isinstance(s, MatchStmt):
                    for c in s.cases:
                        if len(c) >= 4 and isinstance(c[3], list):
                            walk_tail(c[3], current)
                    if s.default:
                        walk_tail(s.default, current)

        for decl in ast:
            if isinstance(decl, AstFunction) and not getattr(decl, 'type_params', None):
                walk_tail(decl.body, decl.name)

        # Kosaraju
        visited = set()
        order = []
        def dfs1(n):
            visited.add(n)
            for m in graph.get(n, ()):
                if m not in visited:
                    dfs1(m)
            order.append(n)

        for n in func_names:
            if n not in visited:
                dfs1(n)

        rgraph = {n: set() for n in func_names}
        for n, ns in graph.items():
            for m in ns:
                rgraph[m].add(n)

        visited = set()
        sccs = []
        def dfs2(n, comp):
            visited.add(n)
            comp.append(n)
            for m in rgraph.get(n, ()):
                if m not in visited:
                    dfs2(m, comp)

        for n in reversed(order):
            if n not in visited:
                comp = []
                dfs2(n, comp)
                sccs.append(comp)

        return [scc for scc in sccs if len(scc) > 1]

    def _can_dispatcher(self, funcs):
        """Todos os membros do SCC têm assinatura compatível?"""
        if not funcs:
            return False
        sig0 = (
            tuple(p.type_ann for p in funcs[0].params),
            funcs[0].return_type,
        )
        for f in funcs[1:]:
            sig = (
                tuple(p.type_ann for p in f.params),
                f.return_type,
            )
            if sig != sig0:
                return False
        return True

    def _materialize_scc_dispatcher(self, scc_id, funcs):
        """Gera dispatcher + wrappers para um SCC de mutual recursion."""
        sample = funcs[0]
        param_tys = [self.get_llvm_param_type(p.type_ann) for p in sample.params]
        ret_ty = self.get_llvm_param_type(sample.return_type)

        disp_name = f"__scc_{scc_id}"
        disp_fn_ty = ir.FunctionType(ret_ty, [self.i32_ty] + param_tys)
        disp_fn = ir.Function(self.module, disp_fn_ty, name=disp_name)

        old_builder = self.builder
        old_defer_stack_outer = getattr(self, 'defer_stack', None)
        self.defer_stack = []

        # entry: aloca slots e current_id
        entry_bb = disp_fn.append_basic_block(name=f"{disp_name}_entry")
        self.builder = ir.IRBuilder(entry_bb)

        slots = []
        for i, p in enumerate(sample.params):
            slot = self.builder.alloca(param_tys[i], name=f"scc_slot_{i}_{p.name}")
            self.builder.store(disp_fn.args[i + 1], slot)
            slots.append(slot)

        id_slot = self.builder.alloca(self.i32_ty, name=f"{disp_name}_id")
        self.builder.store(disp_fn.args[0], id_slot)

        dispatch_bb = disp_fn.append_basic_block(name=f"{disp_name}_dispatch")
        self.builder.branch(dispatch_bb)

        # dispatch: switch
        self.builder.position_at_end(dispatch_bb)
        id_val = self.builder.load(id_slot, name=f"{disp_name}_id_load")

        bad_bb = disp_fn.append_basic_block(name=f"{disp_name}_bad")
        sw = self.builder.switch(id_val, bad_bb)

        member_bb = {}
        for idx, f in enumerate(funcs):
            bb = disp_fn.append_basic_block(name=f"{disp_name}_{f.name}")
            sw.add_case(ir.Constant(self.i32_ty, idx), bb)
            member_bb[f.name] = bb

        self.builder.position_at_end(bad_bb)
        self.builder.unreachable()

        old_scc_slots = getattr(self, '_current_scc_slots', None)
        old_scc_ids = getattr(self, '_current_scc_ids', None)
        old_scc_id_slot = getattr(self, '_current_scc_id_slot', None)
        old_scc_dispatch = getattr(self, '_current_scc_dispatch_bb', None)

        self._current_scc_slots = {f.name: slots for f in funcs}
        self._current_scc_ids = {f.name: idx for idx, f in enumerate(funcs)}
        self._current_scc_id_slot = id_slot
        self._current_scc_dispatch_bb = dispatch_bb

        # Corpos de cada membro
        for idx, f in enumerate(funcs):
            self.builder.position_at_end(member_bb[f.name])

            old_sym = self.symbol_table
            old_vt = self.var_types
            old_current = getattr(self, 'current_func_name', None)

            # Reset per-membro
            self.defer_stack = []

            self.symbol_table = {p.name: slots[i] for i, p in enumerate(f.params)}
            self.var_types = {p.name: p.type_ann for p in f.params}
            self.current_func_name = f.name

            for stmt in f.body:
                if self.builder.block.is_terminated:
                    break
                self.visit(stmt)

            if not self.builder.block.is_terminated:
                self._emit_all_defers()
            if not self.builder.block.is_terminated:
                if ret_ty == self.void_ty:
                    self.builder.ret_void()
                elif isinstance(ret_ty, ir.PointerType):
                    self.builder.ret(ir.Constant(ret_ty, None))
                else:
                    self.builder.ret(ir.Constant(ret_ty, 0))

            self.symbol_table = old_sym
            self.var_types = old_vt
            self.current_func_name = old_current

        self._current_scc_slots = old_scc_slots
        self._current_scc_ids = old_scc_ids
        self._current_scc_id_slot = old_scc_id_slot
        self._current_scc_dispatch_bb = old_scc_dispatch

        # Wrappers
        for idx, f in enumerate(funcs):
            func, func_type = self.functions_table[f.name]
            wbb = func.append_basic_block(name=f"{f.name}_wrap")
            self.builder = ir.IRBuilder(wbb)
            call_args = [ir.Constant(self.i32_ty, idx)] + list(func.args)
            result = self.builder.call(disp_fn, call_args, name=f"{f.name}_scc_call")
            if func_type.return_type == self.void_ty:
                self.builder.ret_void()
            else:
                self.builder.ret(result)

        self.defer_stack = old_defer_stack_outer
        self.builder = old_builder

    # ==================================================================
    # Corpo de função (com TCO + defers + @safe)
    # ==================================================================
    def generate_function_body(self, node):
        func, func_type = self.functions_table[node.name]

        self.current_func_name = node.name

        old_symtab = self.symbol_table
        old_var_types = self.var_types
        old_body_bb = getattr(self, 'current_body_bb', None)
        old_defer_stack = getattr(self, 'defer_stack', None)
        old_safe = getattr(self, '_safe_mode', False)
        old_closure_vars = self.closure_vars          # NOVO
        self.defer_stack = []
        self.closure_vars = set()                     # NOVO

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
        self.closure_vars = old_closure_vars          # NOVO

    # ==================================================================
    # API de baixo nível
    # ==================================================================
    def codegen_stmt(self, node):
        return self.visit(node)

    def codegen_expr(self, node):
        return self.visit(node)