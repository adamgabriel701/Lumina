from lumina.ast.statements import ErrorNode
from ..ast import Function, ExternDecl, StructDecl, EnumDecl, ImplBlock, VarDecl, VariableExpr, TraitDecl, MatchStmt
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
        
        # NOVO: Centralização das funções nativas (builtins)
        self.builtin_functions = {
            "print", "input", "atoi", "len", "alloc", "alloc_bytes", "free", 
            "read_file", "write_file", "int", "float", "str", "argv", "chr", 
            "http_response"
        }

    def analyze(self, declarations):
        # Fase 1: Registrar todas as definições globais
        for decl in declarations:
            if isinstance(decl, ErrorNode): continue
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
                self.struct_defs[decl.name] = decl # Enums são tratados como Structs no codegen
                for v_name, _ in decl.variants: 
                    self.functions.add(v_name)
            elif isinstance(decl, ImplBlock):
                for method in decl.methods:
                    self.functions.add(method.name)
                    self.function_defs[method.name] = method
                    
                if decl.trait_name:
                    trait_def = next((d for d in declarations if isinstance(d, TraitDecl) and d.name == decl.trait_name), None)
                    if not trait_def:
                        raise LuminaError(f"Trait '{decl.trait_name}' não declarada.", self.filename, 0, 0, self.source_code)
                        
                    for trait_method in trait_def.methods:
                        expected_name = f"{decl.struct_name}_{trait_method.name}"
                        if expected_name not in self.functions and not trait_method.body:
                            raise LuminaError(
                                f"Struct '{decl.struct_name}' não implementa o método '{trait_method.name}' exigido pelo Trait '{decl.trait_name}'.", 
                                self.filename, getattr(decl, 'line', 0), getattr(decl, 'col', 0), self.source_code
                            )
                        impl_method = self.function_defs.get(expected_name)
                        if impl_method and impl_method.return_type != trait_method.return_type:
                            raise LuminaError(
                                f"Assinatura incorreta para '{trait_method.name}'. Esperado retorno '{trait_method.return_type}', mas obteve '{impl_method.return_type}'.", 
                                self.filename, getattr(decl, 'line', 0), getattr(decl, 'col', 0), self.source_code
                            )

        # Fase 2: Analisar o corpo das declarações
        for decl in declarations:
            if isinstance(decl, VarDecl):
                if decl.var_type is not None:
                    base_type = decl.var_type.split('<')[0]
                    if base_type not in ("int", "float", "bool", "str", "ptr") and base_type not in self.structs:
                        raise LuminaError(
                            f"Tipo '{decl.var_type}' não declarado.", 
                            self.filename, getattr(decl, 'line', 0), getattr(decl, 'col', 0), self.source_code
                        )
                if decl.value: 
                    self.analyze_expr(decl.value)
                self.declare_var(decl.name, decl.var_type, decl.is_mutable)
                if hasattr(decl, 'line'):
                    self.definition_locations[decl.name] = (self.filename, decl.line, decl.col)
                    
            elif isinstance(decl, Function): 
                self.analyze_function(decl)

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
        # CORREÇÃO: Salva e restaura a pilha de escopos
        saved_scopes = self.scopes
        global_scope = saved_scopes[0] if saved_scopes else {}
        self.scopes = [global_scope.copy()]
        
        try:
            self.current_ret_type = node.return_type
            # ATUALIZADO: Usa Param dataclass
            for param in node.params: 
                self.declare_var(param.name, param.type_ann, True)
                
            for stmt in node.body: 
                self.analyze_stmt(stmt)
        finally:
            # CORREÇÃO: Restaura escopos anteriores
            self.scopes = saved_scopes

    def analyze_stmt(self, node):
        # Checagem de exaustividade do Pattern Matching (MatchStmt)
        if isinstance(node, MatchStmt):
            cond_type = self.analyze_expr(node.condition)
            if cond_type and cond_type in self.struct_defs:
                struct_def = self.struct_defs[cond_type]
                if hasattr(struct_def, 'variants'): # É um Enum
                    if not node.default:
                        covered_variants = [c[0] for c in node.cases]
                        all_variants = [v[0] for v in struct_def.variants]
                        if not set(all_variants).issubset(set(covered_variants)):
                            raise LuminaError(
                                "Match não exaustivo. Faltam variantes ou um ramo 'default'.", 
                                self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code
                            )
                            
        # Chama o analisador de statements da classe pai
        super().analyze_stmt(node)