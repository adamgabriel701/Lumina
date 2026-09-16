from ..builtins import BUILTIN_FUNCTIONS
from lumina.ast.statements import ErrorNode
from ..ast import (
    Function, ExternDecl, StructDecl, EnumDecl, ImplBlock,
    VarDecl, VariableExpr, TraitDecl, MatchStmt, Param,
)
from ..errors import LuminaError
from .expressions import ExpressionAnalyzer
from .statements import StatementAnalyzer


class SemanticAnalyzer(ExpressionAnalyzer, StatementAnalyzer):
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

    # ------------------------------------------------------------------
    # @derive(Eq, Debug)
    # ------------------------------------------------------------------
    def _expand_derives(self, declarations):
        """Expande @derive(Eq, Debug, ...) em métodos sintetizados
        adicionados como ImplBlocks.

        Estes ImplBlocks são injetados em `declarations` para que as
        próximas fases (registro de funções, análise) os vejam.
        """
        from ..ast import ImplBlock

        new_impls = []
        for decl in declarations:
            attrs = getattr(decl, 'attrs', None)
            if not attrs:
                continue
            if not hasattr(decl, 'fields'):
                continue  # só struct

            struct_name = decl.name
            methods = []

            for attr_name, attr_args in attrs:
                if attr_name != 'derive':
                    continue
                for deriv in attr_args:
                    if deriv == 'Eq':
                        methods.append(self._gen_eq(struct_name, decl))
                    elif deriv == 'Debug':
                        methods.append(self._gen_debug(struct_name, decl))

            if methods:
                new_impls.append(ImplBlock(struct_name, methods))

        declarations.extend(new_impls)

    def _gen_eq(self, struct_name, struct_decl):
        """Gera: fn {Struct}___eq__(a: Struct, b: Struct) -> int

        Nome já mangled porque o codegen procura `{Struct}___eq__`
        na `functions_table`.
        """
        from ..ast import (
            Function, Param, BinaryExpr, VariableExpr, MemberExpr,
            ReturnStmt, IfStmt, NumberExpr,
        )

        a_var = VariableExpr('a', 0, 0)
        b_var = VariableExpr('b', 0, 0)

        # Compara cada campo: a.f1 == b.f1 and a.f2 == b.f2 and ...
        conditions = []
        for fname in struct_decl.fields.keys():
            a_field = MemberExpr(a_var, fname)
            b_field = MemberExpr(b_var, fname)
            conditions.append(BinaryExpr('==', a_field, b_field))

        if not conditions:
            cond = NumberExpr('1', False)  # struct vazia: sempre igual
        elif len(conditions) == 1:
            cond = conditions[0]
        else:
            cond = conditions[0]
            for c in conditions[1:]:
                cond = BinaryExpr('and', cond, c)

        then_body = [ReturnStmt([NumberExpr('1', False)])]
        if_stmt = IfStmt(cond, then_body, None)
        return_stmt = ReturnStmt([NumberExpr('0', False)])

        # Mangled: `Struct + ___ + eq__` = `Struct___eq__`
        mangled_name = f"{struct_name}___eq__"

        return Function(
            mangled_name,
            [Param('a', struct_name), Param('b', struct_name)],
            'int',
            [if_stmt, return_stmt],
        )

    def _gen_debug(self, struct_name, struct_decl):
        """Gera: fn {Struct}___debug__(p: Struct) -> str

        Nome já mangled porque o codegen procura `{Struct}___debug__`.
        """
        from ..ast import (
            Function, Param, ReturnStmt, StringExpr, BinaryExpr,
            VariableExpr, MemberExpr,
        )

        p_var = VariableExpr('p', 0, 0)
        parts = [StringExpr(f"{struct_name} {{ ")]

        for i, fname in enumerate(struct_decl.fields.keys()):
            if i > 0:
                parts.append(StringExpr(", "))
            parts.append(StringExpr(f"{fname}: "))
            field_access = MemberExpr(p_var, fname)
            parts.append(field_access)

        parts.append(StringExpr(" }"))

        # Concatenação: "P1" + v1 + "P2" + v2 ...
        expr = parts[0]
        for p in parts[1:]:
            expr = BinaryExpr('+', expr, p)

        # Mangled: `Struct + ___ + debug__` = `Struct___debug__`
        mangled_name = f"{struct_name}___debug__"

        return Function(
            mangled_name,
            [Param('p', struct_name)],
            'str',
            [ReturnStmt([expr])],
        )

    # ------------------------------------------------------------------
    # Trait defaults
    # ------------------------------------------------------------------
    def _resolve_trait_defaults(self, declarations):
        traits_by_name = {}
        for decl in declarations:
            if isinstance(decl, TraitDecl):
                traits_by_name[decl.name] = decl

        # Passo 1: registra aliases `metodo` → `Struct_metodo`.
        for decl in declarations:
            if not isinstance(decl, ImplBlock):
                continue
            trait_name = getattr(decl, 'trait_name', None)
            if not trait_name or trait_name not in traits_by_name:
                continue
            trait_def = traits_by_name[trait_name]
            for trait_method in trait_def.methods:
                full_name = f"{decl.struct_name}_{trait_method.name}"
                if full_name not in self.functions:
                    self.functions.add(full_name)
                self.functions.add(trait_method.name)
                # Function "fake" com params vazios. O `self` é
                # implícito no call site.
                if trait_method.name not in self.function_defs:
                    self.function_defs[trait_method.name] = Function(
                        trait_method.name,
                        [],
                        trait_method.return_type,
                        [],
                    )

        # Passo 2: copia métodos default para o ImplBlock que não os sobrescreve.
        for decl in declarations:
            if not isinstance(decl, ImplBlock):
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

                default_method = Function(
                    full_name,
                    [Param('self', decl.struct_name)] + list(trait_method.params),
                    trait_method.return_type,
                    list(trait_method.body),
                )
                decl.methods.append(default_method)

    # ------------------------------------------------------------------
    # Análise principal
    # ------------------------------------------------------------------
    def analyze(self, declarations):
        self._expand_derives(declarations)
        self._resolve_trait_defaults(declarations)

        # ------------------------------------------------------------------
        # Passada 1: registrar símbolos (funções, structs, enums, traits)
        # ------------------------------------------------------------------
        for decl in declarations:
            if isinstance(decl, ErrorNode):
                continue
            if isinstance(decl, (Function, ExternDecl)):
                self.functions.add(decl.name)
                if isinstance(decl, Function):
                    self.function_defs[decl.name] = decl
                    if hasattr(decl, 'line'):
                        self.definition_locations[decl.name] = (self.filename, decl.line, decl.col)
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
                        (d for d in declarations if isinstance(d, TraitDecl) and d.name == decl.trait_name),
                        None,
                    )
                    if not trait_def:
                        raise LuminaError(
                            f"Trait '{decl.trait_name}' não declarada.",
                            self.filename, 0, 0, self.source_code,
                        )

                    for trait_method in trait_def.methods:
                        expected_name = f"{decl.struct_name}_{trait_method.name}"
                        if expected_name not in self.functions and not trait_method.body:
                            raise LuminaError(
                                f"Struct '{decl.struct_name}' não implementa o método '{trait_method.name}' exigido pelo Trait '{decl.trait_name}'.",
                                self.filename, getattr(decl, 'line', 0), getattr(decl, 'col', 0), self.source_code,
                            )
                        impl_method = self.function_defs.get(expected_name)
                        if impl_method and impl_method.return_type != trait_method.return_type:
                            raise LuminaError(
                                f"Assinatura incorreta para '{trait_method.name}'. Esperado retorno '{trait_method.return_type}', mas obteve '{impl_method.return_type}'.",
                                self.filename, getattr(decl, 'line', 0), getattr(decl, 'col', 0), self.source_code,
                            )

        # ------------------------------------------------------------------
        # Passada 2: processar VarDecls de topo (globais) ANTES das funções.
        # ------------------------------------------------------------------
        for decl in declarations:
            if isinstance(decl, VarDecl):
                if decl.var_type is not None:
                    base_type = decl.var_type.split('<')[0]
                    if base_type not in ("int", "float", "bool", "str", "ptr", "fn") and base_type not in self.structs:
                        raise LuminaError(
                            f"Tipo '{decl.var_type}' não declarado.",
                            self.filename, getattr(decl, 'line', 0), getattr(decl, 'col', 0), self.source_code,
                        )
                if decl.value:
                    self.visit(decl.value)
                self.declare_var(decl.name, decl.var_type, decl.is_mutable)
                if hasattr(decl, 'line'):
                    self.definition_locations[decl.name] = (self.filename, decl.line, decl.col)

        # ------------------------------------------------------------------
        # Passada 3: analisar corpos de funções e métodos de impl.
        # TraitDecl NÃO entra aqui — os métodos default já foram copiados
        # para os ImplBlocks por `_resolve_trait_defaults`.
        # ------------------------------------------------------------------
        for decl in declarations:
            if isinstance(decl, Function):
                self.analyze_function(decl)
            elif isinstance(decl, ImplBlock):
                for method in decl.methods:
                    self.analyze_function(method)

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

    def check_escape(self, node):
        if isinstance(node, VariableExpr) and node.name in self.heap_allocs:
            self.escapes.add(node.name)

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

    def analyze_stmt(self, node):
        if isinstance(node, MatchStmt):
            cond_type = self.visit(node.condition)
            if cond_type and cond_type in self.struct_defs:
                struct_def = self.struct_defs[cond_type]
                if hasattr(struct_def, 'variants'):
                    if not node.default:
                        covered_variants = [c[0] for c in node.cases]
                        all_variants = [v[0] for v in struct_def.variants]
                        if not set(all_variants).issubset(set(covered_variants)):
                            raise LuminaError(
                                "Match não exaustivo. Faltam variantes ou um ramo 'default'.",
                                self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code,
                            )

        super().analyze_stmt(node)