from ..ast import VarDecl, DestructureStmt, AssignStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt, MatchStmt, ContinueStmt, DeferStmt, BreakStmt, AssertStmt, BenchStmt, CallExpr, MemberExpr, DerefExpr, IndexExpr, VariableExpr, StringExpr, NumberExpr, BoolExpr, BinaryExpr, StructLiteralExpr, ErrorNode
from ..errors import LuminaError

class StatementAnalyzer:
    def analyze_stmt(self, node):
        if isinstance(node, ErrorNode): return
        if isinstance(node, VarDecl):
            if node.var_type is not None:
                base_type = node.var_type.split('<')[0]
                if base_type not in ("int", "float", "bool", "str", "ptr") and base_type not in self.structs:
                    raise LuminaError(f"Tipo '{node.var_type}' não declarado.", self.filename, 0, 0, self.source_code)
                    
            # Inferência de tipos se o tipo for None
            if node.var_type is None and node.value is not None:
                if isinstance(node.value, StringExpr): node.var_type = "str"
                elif isinstance(node.value, NumberExpr): node.var_type = "float" if node.value.is_float else "int"
                elif isinstance(node.value, BoolExpr): node.var_type = "bool"
                elif isinstance(node.value, StructLiteralExpr): node.var_type = node.value.struct_name
                elif isinstance(node.value, CallExpr):
                    func_name = getattr(node.value.callee, 'name', None) if hasattr(node.value, 'callee') else getattr(node.value, 'name', None)
                    
                    if node.value.is_method:
                        obj_node = node.value.args[0]
                        if isinstance(obj_node, VariableExpr):
                            info = self.get_var_info(obj_node.name)
                            if info:
                                struct_name = info['type'].split('<')[0] if info['type'] else "Unknown"
                                real_method_name = f"{struct_name}_{func_name}"
                                if real_method_name in self.function_defs:
                                    node.var_type = self.function_defs[real_method_name].return_type
                                else:
                                    # Se não achou o def do método, assume o tipo do objeto (comum para builtins como len() que retorna int)
                                    node.var_type = "int" 
                    else:
                        if func_name in self.function_defs: 
                            node.var_type = self.function_defs[func_name].return_type
                        # Se for um builtin como print, não retorna nada útil, deixa como int
                        else: node.var_type = "int"
                            
            if isinstance(node.value, CallExpr) and getattr(node.value.callee, 'name', None) == "alloc": 
                self.heap_allocs.add(node.name)
                
            if node.value: self.visit(node.value)
            self.declare_var(node.name, node.var_type, node.is_mutable)
        elif isinstance(node, DestructureStmt):
            self.visit(node)
            for name in node.names: self.declare_var(name, "int", node.is_mutable)
        elif isinstance(node, AssignStmt):
            if isinstance(node.target, MemberExpr):
                self.check_escape(node.target.obj)
                info = self.get_var_info(node.target.obj.name)
                if not info: raise LuminaError(f"Variável '{node.target.obj.name}' não declarada.", self.filename, 0, 0, self.source_code)
                if not info['mutable']: raise LuminaError(f"Não pode modificar variável imutável '{node.target.obj.name}'.", self.filename, 0, 0, self.source_code)
                base_type = info['type'].split('<')[0] if info['type'] else "Unknown"
                if base_type not in self.struct_defs: raise LuminaError(f"Variável '{node.target.obj.name}' não é uma Struct.", self.filename, 0, 0, self.source_code)
                struct_def = self.struct_defs[base_type]
                if node.target.member not in struct_def.fields: raise LuminaError(f"Campo '{node.target.member}' não existe na Struct '{info['type']}'.", self.filename, 0, 0, self.source_code)
            elif isinstance(node.target, DerefExpr): pass 
            elif isinstance(node.target, IndexExpr): self.check_escape(node.target.array)
            else:
                self.check_escape(node.value)
                info = self.get_var_info(node.target.name)
                if not info: raise LuminaError(f"Variável '{node.target.name}' não declarada.", self.filename, 0, 0, self.source_code)
                if not info['mutable']: raise LuminaError(f"Não pode reatribuir à variável imutável '{node.target.name}'.", self.filename, 0, 0, self.source_code)
            self.check_escape(node.value); self.visit(node.value)
        elif isinstance(node, ReturnStmt):
            for val in node.values: self.check_escape(val); self.visit(val)
        elif isinstance(node, IfStmt):
            self.visit(node.condition); self.push_scope()
            for stmt in node.then_body: self.visit(stmt)
            self.pop_scope()
            if node.else_body:
                self.push_scope()
                for stmt in node.else_body: self.visit(stmt)
                self.pop_scope()
        elif isinstance(node, WhileStmt):
            self.visit(node.condition); self.push_scope()
            for stmt in node.body: self.visit(stmt)
            self.pop_scope()
        elif isinstance(node, ForStmt):
            if node.iterable is not None: self.visit(node.iterable)
            else: self.visit(node.start); self.visit(node.end)
            self.push_scope(); self.declare_var(node.var_name, "int", False)
            for stmt in node.body: self.visit(stmt)
            self.pop_scope()
        elif isinstance(node, MatchStmt):
            self.visit(node.condition)
            for variant_name, var_name, body in node.cases:
                self.push_scope()
                if var_name: self.declare_var(var_name, "int", False)
                for stmt in body: self.visit(stmt)
                self.pop_scope()
            if node.default:
                self.push_scope()
                for stmt in node.default: self.visit(stmt)
                self.pop_scope()
        elif isinstance(node, ContinueStmt): pass
        elif isinstance(node, BreakStmt): pass
        elif isinstance(node, DeferStmt):
            for stmt in node.body: self.visit(stmt)
        elif isinstance(node, AssertStmt): self.visit(node.condition)
        elif isinstance(node, BenchStmt):
            for stmt in node.body: self.visit(stmt)
        else: self.visit(node)
