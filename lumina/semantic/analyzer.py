"""Orquestrador da análise semântica.

O trabalho pesado está dividido em:
  - `ExpressionAnalyzer` (em `expressions/`) — type checking de expressões
  - `StatementAnalyzer` (em `statements/`) — type checking de statements
  - `DerivesMixin` (em `derives.py`) — expansão de `@derive(...)`
  - `TraitResolutionMixin` (em `trait_resolution.py`) — métodos default

A classe `SemanticAnalyzer` apenas orquestra a ordem das passadas e
mantém o registro global de macros (`@macro`) para validar invocações
`nome!(args)`.
"""
from ..builtins import BUILTIN_FUNCTIONS
from lumina.ast.statements import ErrorNode
from ..ast import (
    Function, ExternDecl, StructDecl, EnumDecl, ImplBlock,
    VarDecl, VariableExpr, TraitDecl, MatchStmt, TypeAlias,
    IfStmt, WhileStmt, ForStmt, DeferStmt, BenchStmt,
)
from ..errors import LuminaError
from .expressions import ExpressionAnalyzer
from .statements import StatementAnalyzer
from .derives import DerivesMixin
from .trait_resolution import TraitResolutionMixin
from .types import expand_type_alias


class SemanticAnalyzer(
    ExpressionAnalyzer,
    StatementAnalyzer,
    DerivesMixin,
    TraitResolutionMixin,
):

    def __init__(self, filename="program.lm", source_code=""):
        self.scopes = [{}]
        self.functions = set()
        self.function_defs = {}
        self.structs = set()
        self.struct_defs = {}
        self.filename = filename
        self.source_code = source_code
        self.heap_allocs = set()
        self.escapes = set()
        self.definition_locations = {}

        self.builtin_functions = BUILTIN_FUNCTIONS

        self.freed_vars = set()
        self.macros = {}   # name → Function (com attr 'macro')
        self.type_aliases = {}

    # ------------------------------------------------------------------
    # Análise principal
    # ------------------------------------------------------------------
    def analyze(self, declarations):
        self._expand_derives(declarations)
        self._resolve_trait_defaults(declarations)

        # Passada 0: coletar e expandir type aliases.
        # A expansão mutaciona os tipos no AST (params, retornos, fields,
        # payloads de enum, etc.) para que o resto do pipeline nunca
        # veja aliases.
        self.type_aliases = {}
        for decl in declarations:
            if isinstance(decl, TypeAlias):
                self.type_aliases[decl.name] = decl.target_type

        if self.type_aliases:
            self._expand_type_aliases(declarations)

        # Passada 0: coletar macros. Necessário para validar invocações
        # `nome!(args)` (MacroCallStmt) e permitir que a análise dos
        # corpos de macros aconteça como funções normais.
        self.macros = {}
        for decl in declarations:
            if isinstance(decl, Function):
                attrs = getattr(decl, 'attrs', None) or []
                if 'macro' in attrs:
                    self.macros[decl.name] = decl

        # Passada 1: registrar símbolos.
        for decl in declarations:
            if isinstance(decl, ErrorNode):
                continue
            if isinstance(decl, (Function, ExternDecl)):
                self.functions.add(decl.name)
                self.function_defs[decl.name] = decl
                if hasattr(decl, 'line'):
                    self.definition_locations[decl.name] = (
                        self.filename, decl.line, decl.col,
                    )
            elif isinstance(decl, StructDecl):
                self.structs.add(decl.name)
                self.struct_defs[decl.name] = decl
            elif isinstance(decl, EnumDecl):
                self.structs.add(decl.name)
                self.struct_defs[decl.name] = decl
                for v_name, _ in decl.variants:
                    self.functions.add(v_name)
            elif isinstance(decl, ImplBlock):
                for method in decl.methods:
                    self.functions.add(method.name)
                    self.function_defs[method.name] = method

                if decl.trait_name:
                    trait_def = next(
                        (d for d in declarations
                         if isinstance(d, TraitDecl) and d.name == decl.trait_name),
                        None,
                    )
                    if not trait_def:
                        raise LuminaError(
                            f"Trait '{decl.trait_name}' não declarada.",
                            self.filename, 0, 0, self.source_code,
                        )

                    for trait_method in trait_def.methods:
                        expected_name = f"{decl.struct_name}_{trait_method.name}"
                        if (expected_name not in self.functions
                                and not trait_method.body):
                            raise LuminaError(
                                f"Struct '{decl.struct_name}' não implementa o "
                                f"método '{trait_method.name}' exigido pelo "
                                f"Trait '{decl.trait_name}'.",
                                self.filename, getattr(decl, 'line', 0),
                                getattr(decl, 'col', 0), self.source_code,
                            )
                        impl_method = self.function_defs.get(expected_name)
                        if (impl_method
                                and impl_method.return_type != trait_method.return_type):
                            raise LuminaError(
                                f"Assinatura incorreta para "
                                f"'{trait_method.name}'. Esperado retorno "
                                f"'{trait_method.return_type}', mas obteve "
                                f"'{impl_method.return_type}'.",
                                self.filename, getattr(decl, 'line', 0),
                                getattr(decl, 'col', 0), self.source_code,
                            )

        # Passada 2: VarDecls de topo (globais)
        for decl in declarations:
            if isinstance(decl, VarDecl):
                if decl.var_type is not None:
                    base_type = decl.var_type.split('<')[0]
                    is_fn_sig = base_type.startswith("fn(")
                    if (base_type not in ("int", "float", "bool", "str", "ptr", "fn")
                            and not is_fn_sig
                            and base_type not in self.structs):
                        raise LuminaError(
                            f"Tipo '{decl.var_type}' não declarado.",
                            self.filename, getattr(decl, 'line', 0),
                            getattr(decl, 'col', 0), self.source_code,
                        )
                if decl.value:
                    self.visit(decl.value)
                self.declare_var(decl.name, decl.var_type, decl.is_mutable)
                if hasattr(decl, 'line'):
                    self.definition_locations[decl.name] = (
                        self.filename, decl.line, decl.col,
                    )

        # Passada 3: corpos de funções e métodos de impl.
        for decl in declarations:
            if isinstance(decl, Function):
                self.analyze_function(decl)
            elif isinstance(decl, ImplBlock):
                for method in decl.methods:
                    self.analyze_function(method)

    # ------------------------------------------------------------------
    # Escopo
    # ------------------------------------------------------------------
    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def declare_var(self, name, var_type, is_mutable):
        self.scopes[-1][name] = {'type': var_type, 'mutable': is_mutable}

    def get_var_info(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _expand_type_aliases(self, declarations):
        """Reescreve todos os tipos do AST expandindo type aliases.

        Roda em todas as declarações top-level e recursa nos corpos
        de função para pegar VarDecls locais (`let x: Alias = ...`).
        """
        aliases = self.type_aliases

        def expand(t):
            return expand_type_alias(t, aliases)

        def expand_params(params):
            for p in params:
                p.type_ann = expand(p.type_ann)

        def walk_stmts(stmts):
            """Percorre statements expandindo tipos em VarDecl,
            DestructureStmt (nada a fazer), e recursando em blocos."""
            for s in stmts:
                if s is None:
                    continue
                if isinstance(s, VarDecl) and s.var_type is not None:
                    s.var_type = expand(s.var_type)
                elif isinstance(s, IfStmt):
                    walk_stmts(s.then_body)
                    if s.else_body:
                        walk_stmts(s.else_body)
                elif isinstance(s, WhileStmt):
                    walk_stmts(s.body)
                elif isinstance(s, ForStmt):
                    walk_stmts(s.body)
                elif isinstance(s, MatchStmt):
                    for c in s.cases:
                        if len(c) >= 4 and isinstance(c[3], list):
                            walk_stmts(c[3])
                    if s.default:
                        walk_stmts(s.default)
                elif isinstance(s, DeferStmt):
                    walk_stmts(s.body)
                elif isinstance(s, BenchStmt):
                    walk_stmts(s.body)

        for decl in declarations:
            if isinstance(decl, Function):
                expand_params(decl.params)
                decl.return_type = expand(decl.return_type)
                walk_stmts(decl.body)
            elif isinstance(decl, ExternDecl):
                new_params = []
                for p in decl.params:
                    if isinstance(p, tuple) and len(p) >= 2:
                        new_params.append((p[0], expand(p[1])))
                    else:
                        new_params.append(p)
                decl.params = new_params
                decl.return_type = expand(decl.return_type)
            elif isinstance(decl, StructDecl):
                for fname, ftype in list(decl.fields.items()):
                    decl.fields[fname] = expand(ftype)
            elif isinstance(decl, EnumDecl):
                new_variants = []
                for vname, payloads in decl.variants:
                    if isinstance(payloads, list):
                        new_variants.append((vname, [expand(t) for t in payloads]))
                    elif payloads:
                        new_variants.append((vname, expand(payloads)))
                    else:
                        new_variants.append((vname, payloads))
                decl.variants = new_variants
            elif isinstance(decl, (TraitDecl, ImplBlock)):
                for m in decl.methods:
                    expand_params(m.params)
                    m.return_type = expand(m.return_type)
                    walk_stmts(m.body)
            elif isinstance(decl, VarDecl):
                if decl.var_type is not None:
                    decl.var_type = expand(decl.var_type)

    def check_escape(self, node):
        if isinstance(node, VariableExpr) and node.name in self.heap_allocs:
            self.escapes.add(node.name)

    # ------------------------------------------------------------------
    # Análise de funções
    # ------------------------------------------------------------------
    def analyze_function(self, node: Function):
        saved_scopes = self.scopes
        global_scope = saved_scopes[0] if saved_scopes else {}
        self.scopes = [global_scope.copy()]

        saved_func_name = getattr(self, 'current_func_name', None)
        saved_ret_type = getattr(self, 'current_ret_type', None)

        try:
            self.current_ret_type = node.return_type
            self.current_func_name = node.name

            for param in node.params:
                self.declare_var(param.name, param.type_ann, True)

            for stmt in node.body:
                self.analyze_stmt(stmt)
        finally:
            self.scopes = saved_scopes
            self.current_func_name = saved_func_name
            self.current_ret_type = saved_ret_type

    # ------------------------------------------------------------------
    # Análise de MatchStmt (exaustividade)
    # ------------------------------------------------------------------
    def analyze_stmt(self, node):
        if isinstance(node, MatchStmt):
            cond_type = self.visit(node.condition)
            if cond_type and cond_type in self.struct_defs:
                struct_def = self.struct_defs[cond_type]
                if hasattr(struct_def, 'variants'):
                    if not node.default:
                        covered = []
                        for c in node.cases:
                            v = c[0]
                            if isinstance(v, list):
                                covered.extend(v)
                            elif v is not None:
                                covered.append(v)

                        all_variants = [v[0] for v in struct_def.variants]
                        missing = set(all_variants) - set(covered)
                        has_wildcard = any(c[0] is None for c in node.cases)
                        if missing and not has_wildcard:
                            raise LuminaError(
                                "Match não exaustivo. Faltam variantes ou um "
                                "ramo 'default'.",
                                self.filename, getattr(node, 'line', 0),
                                getattr(node, 'col', 0), self.source_code,
                            )

        super().analyze_stmt(node)