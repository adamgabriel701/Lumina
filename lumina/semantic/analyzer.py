from ..ast import Function, ExternDecl, StructDecl, EnumDecl, ImplBlock, VarDecl, VariableExpr, TraitDecl
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

    def analyze(self, declarations):
        for decl in declarations:
            if isinstance(decl, (Function, ExternDecl)):
                self.functions.add(decl.name)
                if isinstance(decl, Function): self.function_defs[decl.name] = decl
            elif isinstance(decl, StructDecl):
                self.structs.add(decl.name); self.struct_defs[decl.name] = decl
            elif isinstance(decl, EnumDecl):
                self.structs.add(decl.name)
                for v_name, _ in decl.variants: self.functions.add(v_name)
            elif isinstance(decl, ImplBlock):
                for method in decl.methods:
                    self.functions.add(method.name)
                    self.function_defs[method.name] = method
                    
                # NOVO: Verificação de Traits
                if decl.trait_name:
                    # Encontra a definição do Trait
                    trait_def = None
                    for d in declarations:
                        if isinstance(d, TraitDecl) and d.name == decl.trait_name:
                            trait_def = d
                            break
                            
                    if not trait_def:
                        raise LuminaError(f"Trait '{decl.trait_name}' não declarado.", self.filename, 0, 0, self.source_code)
                        
                    # Verifica se todos os métodos do Trait foram implementados
                    impl_method_names = {m.name.split('_')[1] for m in decl.methods}
                    for trait_method in trait_def.methods:
                        expected_name = f"{decl.struct_name}_{trait_method.name}"
                        if expected_name not in self.functions:
                            raise LuminaError(f"Struct '{decl.struct_name}' não implementa o método '{trait_method.name}' exigido pelo Trait '{decl.trait_name}'.", self.filename, 0, 0, self.source_code)
        for decl in declarations:
            if isinstance(decl, VarDecl):
                if decl.var_type is not None:
                    base_type = decl.var_type.split('<')[0]
                    if base_type not in ("int", "float", "bool", "str", "ptr") and base_type not in self.structs:
                        raise LuminaError(f"Tipo '{decl.var_type}' não declarado.", self.filename, 0, 0, self.source_code)
                if decl.value: self.analyze_expr(decl.value)
                self.declare_var(decl.name, decl.var_type, decl.is_mutable)
            elif isinstance(decl, Function): self.analyze_function(decl)

    def push_scope(self): self.scopes.append({})
    def pop_scope(self): self.scopes.pop()
    def declare_var(self, name, var_type, is_mutable): self.scopes[-1][name] = {'type': var_type, 'mutable': is_mutable}
    def get_var_info(self, name):
        for scope in reversed(self.scopes):
            if name in scope: return scope[name]
        return None

    def check_escape(self, node):
        if isinstance(node, VariableExpr) and node.name in self.heap_allocs: self.escapes.add(node.name)

    def analyze_function(self, node: Function):
        global_scope = self.scopes[0] if self.scopes else {}
        self.scopes = [global_scope.copy()]
        for p_name, p_type, _ in node.params: self.declare_var(p_name, p_type, True)
        for stmt in node.body: self.analyze_stmt(stmt)