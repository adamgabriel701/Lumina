"""Composition root do codegen LLVM.

Os métodos foram divididos em mixins por área (setup, registration,
generics, traits, tco, function_body). A MRO abaixo garante que
`self.<qualquer_coisa>` resolve para a implementação correta.

Ordem da MRO (da esquerda para a direita):
  1. ExpressionCodegen     — visitors de expressão (literals, operators, ...)
  2. StatementCodegen      — visitors de statement (var_decl, control, flow, match)
  3. HelpersCodegen        — create_global_string, to_float_if_needed
  4. TypesCodegen          — get_llvm_type, get_llvm_param_type, monomorphized structs
  5. SetupMixin            — setup_libc_functions, _emit_mutable_global
  6. RegistrationMixin     — register_*, _apply_llvm_attrs, _llvm_ty_to_str
  7. GenericsMixin         — materialize_generic, _infer_type_map_lumina
  8. TraitsMixin           — _resolve_trait_defaults, _validate_macro
  9. TCOMixin              — SCCs + dispatcher
 10. FunctionBodyMixin     — generate_function_body
"""
from ..builtins import BUILTIN_FUNCTIONS
from llvmlite import ir

from .expressions import ExpressionCodegen
from .statements import StatementCodegen
from .helpers import HelpersCodegen
from .types import TypesCodegen
from .setup import SetupMixin
from .registration import RegistrationMixin
from .generics import GenericsMixin
from .traits import TraitsMixin
from .tco import TCOMixin
from .function_body import FunctionBodyMixin

from ..ast import Function as AstFunction, TraitDecl, ExternDecl


class LLVMCodegen(
    ExpressionCodegen,
    StatementCodegen,
    HelpersCodegen,
    TypesCodegen,
    SetupMixin,
    RegistrationMixin,
    GenericsMixin,
    TraitsMixin,
    TCOMixin,
    FunctionBodyMixin,
):

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
        self._fn_wrappers = {}      # cache de wrappers i64(i8*, i64...) p/ fn nomeadas
        self.heap_allocs = set()

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

        # NOVO: array_lengths mapeia nome → N (para `for x in arr`).
        # Populado em visit_VarDecl quando `value` é ArrayExpr ou
        # alloc(N) com N literal.
        self.array_lengths = {}

        # NOVO: vars com `free(x)` explícito. Escape analysis não
        # coloca no stack.
        self.freed_vars = set()

        # NOVO: vars que seguram closures (bloco {fn_ptr, env_ptr}).
        # Chamadas a essas vars desempacotam o env antes de invocar.
        self.closure_vars = set()

        self.setup_libc_functions()
        self.alias_methods = set()   # nomes curtos de trait methods

        self.macros = {}

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

        # 0b. Coleta macros (@macro). Não são registradas como funções
        # normais — só expandem em call sites. Valida aqui (não só no
        # call site) para que macros malformadas falhem mesmo se nunca
        # chamadas.
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
        #
        # Externs que colidem com builtins NÃO são registrados: o codegen
        # de builtin (calls.py) declara a função com a assinatura C
        # correta — ex: `fgets`' `size` é i32 (int do C), mas Lumina
        # `int` é i64. Registrar o extern criaria uma declaração
        # conflitante no módulo e `builder.call(...)` falharia com
        # "Type of #N arg mismatch".
        for decl in ast:
            if isinstance(decl, TraitDecl):
                continue
            if hasattr(decl, 'params') and hasattr(decl, 'return_type'):
                if isinstance(decl, AstFunction) and decl.name in self.macros:
                    continue
                if isinstance(decl, ExternDecl) and decl.name in self.builtin_functions:
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

        # 3. Detecta SCCs de tail calls (mutual recursion) e gera dispatchers.
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
    # API de baixo nível
    # ==================================================================
    def codegen_stmt(self, node):
        return self.visit(node)

    def codegen_expr(self, node):
        return self.visit(node)