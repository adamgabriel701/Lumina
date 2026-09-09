from ..ast import VarDecl, DestructureStmt, AssignStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt, MatchStmt, ContinueStmt, DeferStmt, BreakStmt, AssertStmt, BenchStmt, CallExpr, MemberExpr, DerefExpr, IndexExpr, VariableExpr, StringExpr, NumberExpr, BoolExpr, BinaryExpr, StructLiteralExpr
from ..errors import LuminaError

class StatementAnalyzer:
    def analyze_stmt(self, node):
        if isinstance(node, VarDecl):
            if node.var_type is not None:
                base_type = node.var_type.split('<')[0]
                if base_type not in ("int", "float", "bool", "str", "ptr") and base_type not in self.structs:
                    raise LuminaError(f"Tipo '{node.var_type}' não declarado.", self.filename, 0, 0, self.source_code)
            if node.var_type is None and node.value is not None:
                if isinstance(node.value, StringExpr): node.var_type = "str"
                elif isinstance(node.value, NumberExpr): node.var_type = "float" if node.value.is_float else "int"
                elif isinstance(node.value, BoolExpr): node.var_type = "bool"
                elif isinstance(node.value, CallExpr):
                    if node.value.is_method:
                        obj_node = node.value.args[0]
                        if isinstance(obj_node, VariableExpr):
                            info = self.get_var_info(obj_node.name)
                            if info:
                                # NOVO: Descobre o nome real do método (ex: Square_get_area)
                                struct_name = info['type'].split('<')[0] if info['type'] else "Unknown"
                                real_method_name = f"{struct_name}_{node.value.name}"
                                # NOVO: Procura o tipo de retorno do método na tabela de funções!
                                if real_method_name in self.function_defs:
                                    node.var_type = self.function_defs[real_method_name].return_type
                                else:
                                    node.var_type = info['type'] # Fallback
                    else:
                        func_name = node.value.name
                        if func_name in self.function_defs: node.var_type = self.function_defs[func_name].return_type
                elif isinstance(node.value, BinaryExpr):
                    if isinstance(node.value.left, VariableExpr):
                        info = self.get_var_info(node.value.left.name)
                        if info and info['type'] and info['type'].split('<')[0] in self.structs:
                            struct_name = info['type'].split('<')[0]
                            op_map = {'+': '__add__', '-': '__sub__', '*': '__mul__', '/': '__div__', '==': '__eq__'}
                            method_name = op_map.get(node.value.op)
                            if method_name:
                                real_method_name = f"{struct_name}_{method_name}"
                                if real_method_name in self.function_defs: node.var_type = self.function_defs[real_method_name].return_type
                # NOVO: Inferência para Struct Literals (ex: let p = Point { x: 10, y: 20 })
                elif isinstance(node.value, StructLiteralExpr):
                    node.var_type = node.value.struct_name
            if isinstance(node.value, CallExpr) and node.value.name == "alloc": self.heap_allocs.add(node.name)
            if node.value: self.analyze_expr(node.value)
            self.declare_var(node.name, node.var_type, node.is_mutable)
        elif isinstance(node, DestructureStmt):
            self.analyze_expr(node.value)
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
            self.check_escape(node.value); self.analyze_expr(node.value)
        elif isinstance(node, ReturnStmt):
            for val in node.values: self.check_escape(val); self.analyze_expr(val)
        elif isinstance(node, IfStmt):
            self.analyze_expr(node.condition); self.push_scope()
            for stmt in node.then_body: self.analyze_stmt(stmt)
            self.pop_scope()
            if node.else_body:
                self.push_scope()
                for stmt in node.else_body: self.analyze_stmt(stmt)
                self.pop_scope()
        elif isinstance(node, WhileStmt):
            self.analyze_expr(node.condition); self.push_scope()
            for stmt in node.body: self.analyze_stmt(stmt)
            self.pop_scope()
        elif isinstance(node, ForStmt):
            if node.iterable is not None: self.analyze_expr(node.iterable)
            else: self.analyze_expr(node.start); self.analyze_expr(node.end)
            self.push_scope(); self.declare_var(node.var_name, "int", False)
            for stmt in node.body: self.analyze_stmt(stmt)
            self.pop_scope()
        elif isinstance(node, MatchStmt):
            self.analyze_expr(node.condition)
            for variant_name, var_name, body in node.cases:
                self.push_scope()
                if var_name: self.declare_var(var_name, "int", False)
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
        elif isinstance(node, AssertStmt): self.analyze_expr(node.condition)
        elif isinstance(node, BenchStmt):
            for stmt in node.body: self.analyze_stmt(stmt)
        else: self.analyze_expr(node)
