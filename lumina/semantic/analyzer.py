from ..ast import NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, UnaryExpr, PropagateExpr
from ..ast import ReturnStmt, Function, VarDecl, AssignStmt, IfStmt, WhileStmt, ForStmt, MatchStmt, StructDecl, ImplBlock, ExternDecl, EnumDecl, ContinueStmt, DeferStmt, BreakStmt, AssertStmt, BenchStmt
from ..errors import LuminaError

class SemanticAnalyzer:
    def __init__(self, filename="program.lm", source_code=""):
        self.scopes = [{}]
        self.functions = set()
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
            elif isinstance(decl, StructDecl):
                self.structs.add(decl.name)
                self.struct_defs[decl.name] = decl
            elif isinstance(decl, EnumDecl):
                self.structs.add(decl.name)
                for v_name, _ in decl.variants:
                    self.functions.add(v_name)
            elif isinstance(decl, ImplBlock):
                for method in decl.methods:
                    self.functions.add(method.name)
                    
        for decl in declarations:
            if isinstance(decl, VarDecl):
                if decl.var_type is not None:
                    base_type = decl.var_type.split('<')[0]
                    if base_type not in ("int", "float", "bool", "str", "ptr") and base_type not in self.structs:
                        raise LuminaError(f"Tipo '{decl.var_type}' não declarado.")
                if decl.value: self.analyze_expr(decl.value)
                self.declare_var(decl.name, decl.var_type, decl.is_mutable)
            elif isinstance(decl, Function):
                self.analyze_function(decl)

    def push_scope(self): self.scopes.append({})
    def pop_scope(self): self.scopes.pop()
    def declare_var(self, name, var_type, is_mutable): 
        self.scopes[-1][name] = {'type': var_type, 'mutable': is_mutable}
    def get_var_info(self, name):
        for scope in reversed(self.scopes):
            if name in scope: return scope[name]
        return None

    def check_escape(self, node):
        if isinstance(node, VariableExpr) and node.name in self.heap_allocs:
            self.escapes.add(node.name)

    def analyze_function(self, node: Function):
        global_scope = self.scopes[0] if self.scopes else {}
        self.scopes = [global_scope.copy()]
        
        for p_name, p_type in node.params:
            self.declare_var(p_name, p_type, True)
        for stmt in node.body:
            self.analyze_stmt(stmt)

    def analyze_stmt(self, node):
        if isinstance(node, VarDecl):
            if node.var_type is not None:
                base_type = node.var_type.split('<')[0]
                if base_type not in ("int", "float", "bool", "str", "ptr") and base_type not in self.structs:
                    raise LuminaError(f"Tipo '{node.var_type}' não declarado.")
                    
            if isinstance(node.value, CallExpr) and node.value.name == "alloc":
                self.heap_allocs.add(node.name)
                
            if node.value: self.analyze_expr(node.value)
            self.declare_var(node.name, node.var_type, node.is_mutable)
            
        elif isinstance(node, AssignStmt):
            if isinstance(node.target, MemberExpr):
                self.check_escape(node.target.obj)
                info = self.get_var_info(node.target.obj.name)
                if not info: raise LuminaError(f"Variável '{node.target.obj.name}' não declarada.")
                if not info['mutable']: raise LuminaError(f"Não pode modificar variável imutável '{node.target.obj.name}'.")
                base_type = info['type'].split('<')[0] if info['type'] else "Unknown"
                if base_type not in self.struct_defs: raise LuminaError(f"Variável '{node.target.obj.name}' não é uma Struct.")
                struct_def = self.struct_defs[base_type]
                if node.target.member not in struct_def.fields:
                    raise LuminaError(f"Campo '{node.target.member}' não existe na Struct '{info['type']}'.")
            elif isinstance(node.target, DerefExpr):
                pass 
            elif isinstance(node.target, IndexExpr):
                self.check_escape(node.target.array)
            else:
                self.check_escape(node.value)
                info = self.get_var_info(node.target.name)
                if not info: raise LuminaError(f"Variável '{node.target.name}' não declarada.")
                if not info['mutable']: raise LuminaError(f"Não pode reatribuir à variável imutável '{node.target.name}'.")
            self.check_escape(node.value)
            self.analyze_expr(node.value)
            
        elif isinstance(node, ReturnStmt):
            for val in node.values:
                self.check_escape(val)
                self.analyze_expr(val)
                
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
            for variant_name, var_name, body in node.cases:
                self.push_scope()
                if var_name:
                    self.declare_var(var_name, "int", False)
                for stmt in body: self.analyze_stmt(stmt)
                self.pop_scope()
            if node.default:
                self.push_scope()
                for stmt in node.default: self.analyze_stmt(stmt)
                self.pop_scope()
                
        elif isinstance(node, ContinueStmt): pass
        elif isinstance(node, BreakStmt): pass
        elif isinstance(node, DeferStmt):
            for stmt in node.body: self.analyze_stmt(stmt)
        elif isinstance(node, AssertStmt):
            self.analyze_expr(node.condition)
        elif isinstance(node, BenchStmt):
            for stmt in node.body: self.analyze_stmt(stmt)
        else:
            self.analyze_expr(node)

    def analyze_expr(self, node):
        if isinstance(node, (NumberExpr, BoolExpr, StringExpr)): return
        elif isinstance(node, VariableExpr):
            if not self.get_var_info(node.name):
                raise LuminaError(f"Variável '{node.name}' não declarada.")
        elif isinstance(node, BinaryExpr):
            self.analyze_expr(node.left)
            self.analyze_expr(node.right)
        elif isinstance(node, CallExpr):
            if node.is_method:
                obj_node = node.args[0]
                if isinstance(obj_node, VariableExpr):
                    info = self.get_var_info(obj_node.name)
                    if not info: raise LuminaError(f"Variável '{obj_node.name}' não declarada.")
                    struct_name = info['type'].split('<')[0] if info['type'] else "Unknown"
                    real_method_name = f"{struct_name}_{node.name}"
                    if real_method_name not in self.functions:
                        raise LuminaError(f"Método '{node.name}' não declarado na struct '{struct_name}'.")
            elif node.name not in ("print", "input", "atoi", "len", "alloc", "alloc_bytes", "free", "read_file", "write_file", "int", "float", "str", "argv", "chr") and node.name not in self.functions:
                raise LuminaError(f"Função '{node.name}' não declarada.")
            for arg in node.args: self.analyze_expr(arg)
        elif isinstance(node, ArrayExpr):
            for el in node.elements: self.analyze_expr(el)
        elif isinstance(node, IndexExpr):
            if isinstance(node.array, VariableExpr):
                info = self.get_var_info(node.array.name)
                if not info: raise LuminaError(f"Variável '{node.array.name}' não declarada.")
            else:
                self.analyze_expr(node.array)
            self.analyze_expr(node.index)
        elif isinstance(node, MemberExpr):
            if isinstance(node.obj, VariableExpr):
                info = self.get_var_info(node.obj.name)
                if not info: raise LuminaError(f"Variável '{node.obj.name}' não declarada.")
                current_type = info['type']
            else:
                current_type = self.analyze_expr(node.obj)
                
            base_type = current_type.split('<')[0] if current_type else "Unknown"
            if base_type not in self.struct_defs: 
                raise LuminaError(f"Tipo '{current_type}' não é uma Struct.")
                
            struct_def = self.struct_defs[base_type]
            if node.member not in struct_def.fields:
                raise LuminaError(f"Campo '{node.member}' não existe na Struct '{current_type}'.")
                
            return struct_def.fields[node.member]
            
        elif isinstance(node, AddressOfExpr):
            if isinstance(node.val, VariableExpr) and node.val.name in self.functions:
                return
            self.analyze_expr(node.val)
        elif isinstance(node, DerefExpr):
            self.analyze_expr(node.val)
        elif isinstance(node, UnaryExpr):
            self.analyze_expr(node.val)
        elif isinstance(node, PropagateExpr):
            self.analyze_expr(node.val)