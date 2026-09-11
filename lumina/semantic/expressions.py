from ..ast import (
    NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, 
    ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, UnaryExpr, 
    PropagateExpr, ComptimeExpr, StructLiteralExpr, MatchExpr, CastExpr, LambdaExpr
)
from ..errors import LuminaError

def get_suggestion(name, possible_names):
    """Calcula a distância de Levenshtein para sugerir nomes parecidos."""
    def levenshtein(s1, s2):
        if len(s1) < len(s2):
            return levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    best_match = None
    best_dist = 3 # Tolerância máxima de 3 edições
    for candidate in possible_names:
        dist = levenshtein(name, candidate)
        if dist < best_dist:
            best_dist = dist
            best_match = candidate
    return best_match

class ExpressionAnalyzer:
    
    def analyze_expr(self, node):
        """Analisa uma expressão e retorna o seu tipo (se aplicável)."""
        
        # Literais e Variáveis
        if isinstance(node, NumberExpr): return "int" if not node.is_float else "float"
        elif isinstance(node, BoolExpr): return "bool"
        elif isinstance(node, StringExpr): return "str"
        elif isinstance(node, VariableExpr):
            info = self.get_var_info(node.name)
            if not info:
                available_vars = [k for scope in self.scopes for k in scope.keys()]
                suggestion = get_suggestion(node.name, available_vars)
                msg = f"Variável '{node.name}' não declarada."
                if suggestion:
                    msg += f" Você quis dizer '{suggestion}'?"
                raise LuminaError(msg, self.filename, node.line, node.col, self.source_code)
            return info['type']

        # Operações
        elif isinstance(node, BinaryExpr):
            left_type = self.analyze_expr(node.left)
            self.analyze_expr(node.right)
            
            # Operadores sobrecarregados em Structs
            if left_type and left_type.split('<')[0] in self.structs:
                struct_name = left_type.split('<')[0]
                op_map = {'+': '__add__', '-': '__sub__', '*': '__mul__', '/': '__div__', '==': '__eq__'}
                method_name = op_map.get(node.op)
                if method_name:
                    real_method_name = f"{struct_name}_{method_name}"
                    if real_method_name not in self.functions:
                        raise LuminaError(
                            f"Operador '{node.op}' não definido para a struct '{struct_name}'.", 
                            self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code
                        )
            return left_type

        elif isinstance(node, UnaryExpr):
            self.analyze_expr(node.val)
            return None

        # Acesso e Chamadas
        elif isinstance(node, CallExpr):
            func_name = None
            if isinstance(node.callee, VariableExpr):
                func_name = node.callee.name
                
                if node.is_method:
                    obj_node = node.args[0]
                    obj_type = self.analyze_expr(obj_node)
                    
                    if obj_type == "str":
                        if func_name not in ("contains", "starts_with"):
                            raise LuminaError(f"Método de string '{func_name}' não suportado.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
                    elif obj_type and obj_type != "Unknown":
                        struct_name = obj_type.split('<')[0]
                        real_method_name = f"{struct_name}_{func_name}"
                        if real_method_name not in self.functions:
                            raise LuminaError(
                                f"Método '{func_name}' não implementado para a struct '{struct_name}'.", 
                                self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code
                            )
                elif func_name not in self.builtin_functions and func_name not in self.functions:
                    suggestion = get_suggestion(func_name, list(self.functions) + list(self.builtin_functions))
                    msg = f"Função '{func_name}' não declarada."
                    if suggestion:
                        msg += f" Você quis dizer '{suggestion}'?"
                    raise LuminaError(msg, self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
                    
            for arg in node.args: 
                self.analyze_expr(arg)
            return None

        elif isinstance(node, IndexExpr):
            self.analyze_expr(node.array)
            self.analyze_expr(node.index)
            return None

        elif isinstance(node, MemberExpr):
            current_type = self.analyze_expr(node.obj)
            base_type = current_type.split('<')[0] if current_type else "Unknown"
            if base_type not in self.struct_defs: 
                raise LuminaError(f"Tipo '{current_type}' não é uma Struct.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            struct_def = self.struct_defs[base_type]
            if node.member not in struct_def.fields: 
                raise LuminaError(f"Campo '{node.member}' não existe na Struct '{current_type}'.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            return struct_def.fields[node.member]

        # Estruturas de Dados
        elif isinstance(node, ArrayExpr):
            for el in node.elements: self.analyze_expr(el)
            return "array"
            
        elif isinstance(node, StructLiteralExpr):
            if node.struct_name not in self.struct_defs:
                raise LuminaError(f"Struct '{node.struct_name}' não declarada.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            struct_def = self.struct_defs[node.struct_name]
            defined_fields = set(struct_def.fields.keys())
            passed_fields = set()
            for field_name, field_expr in node.fields:
                if field_name not in struct_def.fields:
                    raise LuminaError(f"Campo '{field_name}' não existe na Struct '{node.struct_name}'.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
                self.analyze_expr(field_expr)
                passed_fields.add(field_name)
            missing = defined_fields - passed_fields
            if missing:
                raise LuminaError(f"Campos faltando na inicialização da Struct '{node.struct_name}': {', '.join(missing)}", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            return node.struct_name

        # Controle de Memória e Ponteiros
        elif isinstance(node, AddressOfExpr):
            if isinstance(node.val, VariableExpr) and node.val.name in self.functions:
                return "ptr"
            self.analyze_expr(node.val)
            return "ptr"

        elif isinstance(node, DerefExpr):
            self.analyze_expr(node.val)
            return None

        # Controle de Fluxo como Expressão
        elif isinstance(node, MatchExpr):
            self.analyze_expr(node.condition)
            for val, res in node.cases:
                self.push_scope()
                if isinstance(val, StructLiteralExpr):
                    for field_name, field_expr in val.fields:
                        if isinstance(field_expr, VariableExpr):
                            field_type = self.struct_defs[val.struct_name].fields.get(field_name, "int")
                            self.declare_var(field_expr.name, field_type, True)
                        else:
                            self.analyze_expr(field_expr)
                else:
                    self.analyze_expr(val)
                self.analyze_expr(res)
                self.pop_scope()
            if node.default:
                self.analyze_expr(node.default)
            return None

        # Outras Expressões
        elif isinstance(node, PropagateExpr):
            self.analyze_expr(node.val)
            if not hasattr(self, 'current_ret_type') or not self.current_ret_type.startswith("Result"):
                raise LuminaError("Operador '?' só pode ser usado em funções que retornam 'Result'.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            return None

        elif isinstance(node, ComptimeExpr):
            return self.analyze_expr(node.expr)

        elif isinstance(node, CastExpr):
            self.analyze_expr(node.expr)
            if node.target_type not in ("int", "float", "bool", "str", "ptr"):
                base = node.target_type.split('<')[0]
                if base not in self.structs:
                    raise LuminaError(f"Tipo de destino '{node.target_type}' não declarado.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            return node.target_type

        elif isinstance(node, LambdaExpr):
            self.push_scope()
            for p_name, p_type, _ in node.params:
                self.declare_var(p_name, p_type, True)
            for stmt in node.body:
                self.analyze_stmt(stmt)
            self.pop_scope()
            return "fn"

        raise NotImplementedError(f"Análise semântica não implementada para {type(node).__name__}")