from ..ast import NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, UnaryExpr
from ..ast import ReturnStmt, Function, VarDecl, AssignStmt, IfStmt, WhileStmt, ForStmt, MatchStmt, StructDecl, ImplBlock, ExternDecl, EnumDecl, ContinueStmt, DeferStmt
from ..errors import LuminaError

class SemanticAnalyzer:
    def __init__(self, filename="program.lm", source_code=""):
        self.scopes = [{}]
        self.functions = set()
        self.structs = set()
        self.struct_defs = {}
        self.filename = filename
        self.source_code = source_code

    def analyze(self, declarations):
        for decl in declarations:
            # NOVO: Registra funções normais E externas importadas de outros módulos
            if isinstance(decl, (Function, ExternDecl)):
                self.functions.add(decl.name)
            elif isinstance(decl, StructDecl):
                self.structs.add(decl.name)
                self.struct_defs[decl.name] = decl
            elif isinstance(decl, EnumDecl):
                self.structs.add(decl.name)
                # Registra os construtores (ex: Some, None) como funções válidas
                for v_name, _ in decl.variants:
                    self.functions.add(v_name)
            elif isinstance(decl, ImplBlock):
                for method in decl.methods:
                    self.functions.add(method.name)
                    
        for decl in declarations:
            if isinstance(decl, Function):
                self.analyze_function(decl)

    def push_scope(self): self.scopes.append({})
    def pop_scope(self): self.scopes.pop()
    def declare_var(self, name, var_type, is_mutable): 
        self.scopes[-1][name] = {'type': var_type, 'mutable': is_mutable}
    def get_var_info(self, name):
        for scope in reversed(self.scopes):
            if name in scope: return scope[name]
        return None

    def analyze_function(self, node: Function):
        self.scopes = [{}]
        for p_name, p_type in node.params:
            self.declare_var(p_name, p_type, True)
        for stmt in node.body:
            self.analyze_stmt(stmt)

    def analyze_stmt(self, node):
        if isinstance(node, VarDecl):
            if node.var_type is not None and node.var_type not in ("int", "float", "bool", "str") and node.var_type not in self.structs:
                raise LuminaError(f"Tipo '{node.var_type}' não declarado.", self.filename, 0, 0, self.source_code)
            if node.value: self.analyze_expr(node.value)
            self.declare_var(node.name, node.var_type, node.is_mutable)
        elif isinstance(node, AssignStmt):
            if isinstance(node.target, MemberExpr):
                info = self.get_var_info(node.target.obj.name)
                if not info: raise LuminaError(f"Variável '{node.target.obj.name}' não declarada.", self.filename, 0, 0, self.source_code)
                if not info['mutable']: raise LuminaError(f"Não pode modificar variável imutável '{node.target.obj.name}'.", self.filename, 0, 0, self.source_code)
                if info['type'] not in self.struct_defs: raise LuminaError(f"Variável '{node.target.obj.name}' não é uma Struct.", self.filename, 0, 0, self.source_code)
                struct_def = self.struct_defs[info['type']]
                if node.target.member not in struct_def.fields:
                    raise LuminaError(f"Campo '{node.target.member}' não existe na Struct '{info['type']}'.", self.filename, 0, 0, self.source_code)
            elif isinstance(node.target, DerefExpr):
                pass 
            elif isinstance(node.target, IndexExpr):
                self.analyze_expr(node.target)
            else:
                info = self.get_var_info(node.target.name)
                if not info: raise LuminaError(f"Variável '{node.target.name}' não declarada.", self.filename, 0, 0, self.source_code)
                if not info['mutable']: raise LuminaError(f"Não pode reatribuir à variável imutável '{node.target.name}'.", self.filename, 0, 0, self.source_code)
            self.analyze_expr(node.value)
        elif isinstance(node, ReturnStmt):
            for val in node.values: self.analyze_expr(val)
        elif isinstance(node, IfStmt):
            self.analyze_expr(node.condition)
            self.push_scope()
            for stmt in node.then_body: self.analyze_stmt(stmt)
            self.pop_scope()
            if node.else_body:
                self.push_scope()
                for stmt in node.else_body: self.analyze_stmt(stmt)
                self.pop_scope()
        elif isinstance(node, WhileStmt):
            self.analyze_expr(node.condition)
            self.push_scope()
            for stmt in node.body: self.analyze_stmt(stmt)
            self.pop_scope()
        elif isinstance(node, ForStmt):
            self.analyze_expr(node.start)
            self.analyze_expr(node.end)
            self.push_scope()
            self.declare_var(node.var_name, "int", False)
            for stmt in node.body: self.analyze_stmt(stmt)
            self.pop_scope()
        elif isinstance(node, MatchStmt):
            self.analyze_expr(node.condition)
            # CORREÇÃO: Agora desempacota 3 valores (variant_name, var_name, body)
            for variant_name, var_name, body in node.cases:
                self.push_scope()
                # Se houver extração de variável (ex: case Some(x):), declara a variável x
                if var_name:
                    self.declare_var(var_name, "int", False) # Simplificado para int
                for stmt in body: self.analyze_stmt(stmt)
                self.pop_scope()
            if node.default:
                self.push_scope()
                for stmt in node.default: self.analyze_stmt(stmt)
                self.pop_scope()
        # NOVO: Continue
        elif isinstance(node, ContinueStmt):
            pass
            
        # NOVO: Defer
        elif isinstance(node, DeferStmt):
            for stmt in node.body:
                self.analyze_stmt(stmt)
        else:
            self.analyze_expr(node)

    def analyze_expr(self, node):
        if isinstance(node, (NumberExpr, BoolExpr, StringExpr)): return
        elif isinstance(node, VariableExpr):
            if not self.get_var_info(node.name):
                # NOVO: Erro Semântico com Linha e Coluna exatas!
                raise LuminaError(f"Variável '{node.name}' não declarada.", self.filename, node.line, node.col, self.source_code)
        elif isinstance(node, BinaryExpr):
            self.analyze_expr(node.left)
            self.analyze_expr(node.right)
        elif isinstance(node, CallExpr):
            if node.is_method:
                obj_node = node.args[0]
                if isinstance(obj_node, VariableExpr):
                    info = self.get_var_info(obj_node.name)
                    if not info: raise LuminaError(f"Variável '{obj_node.name}' não declarada.", self.filename, obj_node.line, obj_node.col, self.source_code)
                    struct_name = info['type']
                    real_method_name = f"{struct_name}_{node.name}"
                    if real_method_name not in self.functions:
                        raise LuminaError(f"Método '{node.name}' não declarado na struct '{struct_name}'.", self.filename, 0, 0, self.source_code)
            elif node.name not in ("print", "input", "atoi", "len", "alloc", "alloc_bytes", "free", "read_file", "write_file", "int", "float", "str", "argv", "chr") and node.name not in self.functions:
                raise LuminaError(f"Função '{node.name}' não declarada.", self.filename, 0, 0, self.source_code)
            for arg in node.args: self.analyze_expr(arg)
        elif isinstance(node, ArrayExpr):
            for el in node.elements: self.analyze_expr(el)
        elif isinstance(node, IndexExpr):
            if isinstance(node.array, VariableExpr):
                info = self.get_var_info(node.array.name)
                if not info: raise LuminaError(f"Variável '{node.array.name}' não declarada.", self.filename, node.array.line, node.array.col, self.source_code)
            else:
                self.analyze_expr(node.array)
            self.analyze_expr(node.index)
        elif isinstance(node, MemberExpr):
            if isinstance(node.obj, VariableExpr):
                info = self.get_var_info(node.obj.name)
                if not info: raise LuminaError(f"Variável '{node.obj.name}' não declarada.", self.filename, node.obj.line, node.obj.col, self.source_code)
                current_type = info['type']
            else:
                current_type = self.analyze_expr(node.obj)
                
            if current_type not in self.struct_defs: 
                raise LuminaError(f"Tipo '{current_type}' não é uma Struct.", self.filename, 0, 0, self.source_code)
                
            struct_def = self.struct_defs[current_type]
            if node.member not in struct_def.fields:
                raise LuminaError(f"Campo '{node.member}' não existe na Struct '{current_type}'.", self.filename, 0, 0, self.source_code)
                
            return struct_def.fields[node.member]
            
        elif isinstance(node, AddressOfExpr):
            # NOVO: Se for o nome de uma função (ex: &worker), está tudo bem!
            if isinstance(node.val, VariableExpr) and node.val.name in self.functions:
                return
            # Senão, analisa como expressão normal (ex: &minha_variavel)
            self.analyze_expr(node.val)
        elif isinstance(node, DerefExpr):
            self.analyze_expr(node.val)
        elif isinstance(node, UnaryExpr):
            self.analyze_expr(node.val)