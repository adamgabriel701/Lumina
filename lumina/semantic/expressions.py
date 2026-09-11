from ..ast import NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, UnaryExpr, PropagateExpr, ComptimeExpr, StructLiteralExpr, MatchExpr, CastExpr, LambdaExpr
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
    best_dist = 3 # Tolerância máxima de 3 edições (trocas/inserções/remoções)
    
    for candidate in possible_names:
        dist = levenshtein(name, candidate)
        if dist < best_dist:
            best_dist = dist
            best_match = candidate
            
    return best_match

class ExpressionAnalyzer:
    def analyze_expr(self, node):
        if isinstance(node, (NumberExpr, BoolExpr, StringExpr)): return
        elif isinstance(node, VariableExpr):
            if not self.get_var_info(node.name):
                # NOVO: Sugere variáveis parecidas
                available_vars = [k for scope in self.scopes for k in scope.keys()]
                suggestion = get_suggestion(node.name, available_vars)
                msg = f"Variável '{node.name}' não declarada."
                if suggestion:
                    msg += f" Você quis dizer '{suggestion}'?"
                raise LuminaError(msg, self.filename, node.line, node.col, self.source_code)
        elif isinstance(node, BinaryExpr):
            self.analyze_expr(node.left); self.analyze_expr(node.right)
            if isinstance(node.left, VariableExpr):
                info = self.get_var_info(node.left.name)
                if info and info['type'] and info['type'].split('<')[0] in self.structs:
                    struct_name = info['type'].split('<')[0]
                    op_map = {'+': '__add__', '-': '__sub__', '*': '__mul__', '/': '__div__', '==': '__eq__'}
                    method_name = op_map.get(node.op)
                    if method_name:
                        real_method_name = f"{struct_name}_{method_name}"
                        if real_method_name not in self.functions:
                            raise LuminaError(f"Operador '{node.op}' não definido para a struct '{struct_name}'.", self.filename, 0, 0, self.source_code)
        elif isinstance(node, CallExpr):
            if node.is_method:
                obj_node = node.args[0]; obj_type = None
                if isinstance(obj_node, VariableExpr):
                    info = self.get_var_info(obj_node.name)
                    if not info: raise LuminaError(f"Variável '{obj_node.name}' não declarada.", self.filename, obj_node.line, obj_node.col, self.source_code)
                    obj_type = info['type']
                elif isinstance(obj_node, StringExpr): obj_type = "str"
                if obj_type == "str":
                    if node.name not in ("contains", "starts_with"):
                        raise LuminaError(f"Método de string '{node.name}' não suportado.", self.filename, 0, 0, self.source_code)
                else:
                    struct_name = obj_type.split('<')[0] if obj_type else "Unknown"
                    real_method_name = f"{struct_name}_{node.name}"
                    if real_method_name not in self.functions:
                        # NOVO: Se não achar, não levanta erro aqui! Pode ser um método padrão de Trait que o Codegen vai injetar.
                        pass 
            elif node.name not in ("print", "input", "atoi", "len", "alloc", "alloc_bytes", "free", "read_file", "write_file", "int", "float", "str", "argv", "chr", "http_response") and node.name not in self.functions:
                # NOVO: Sugere funções parecidas
                suggestion = get_suggestion(node.name, list(self.functions))
                msg = f"Função '{node.name}' não declarada."
                if suggestion:
                    msg += f" Você quis dizer '{suggestion}'?"
                raise LuminaError(msg, self.filename, 0, 0, self.source_code)
            for arg in node.args: self.analyze_expr(arg)
        elif isinstance(node, ArrayExpr):
            for el in node.elements: self.analyze_expr(el)
        elif isinstance(node, IndexExpr):
            if isinstance(node.array, VariableExpr):
                info = self.get_var_info(node.array.name)
                if not info: raise LuminaError(f"Variável '{node.array.name}' não declarada.", self.filename, node.array.line, node.array.col, self.source_code)
            else: self.analyze_expr(node.array)
            self.analyze_expr(node.index)
        elif isinstance(node, MemberExpr):
            if isinstance(node.obj, VariableExpr):
                info = self.get_var_info(node.obj.name)
                if not info: raise LuminaError(f"Variável '{node.obj.name}' não declarada.", self.filename, node.obj.line, node.obj.col, self.source_code)
                current_type = info['type']
            else: current_type = self.analyze_expr(node.obj)
            base_type = current_type.split('<')[0] if current_type else "Unknown"
            if base_type not in self.struct_defs: raise LuminaError(f"Tipo '{current_type}' não é uma Struct.", self.filename, 0, 0, self.source_code)
            struct_def = self.struct_defs[base_type]
            if node.member not in struct_def.fields: raise LuminaError(f"Campo '{node.member}' não existe na Struct '{current_type}'.", self.filename, 0, 0, self.source_code)
            return struct_def.fields[node.member]
        elif isinstance(node, AddressOfExpr):
            if isinstance(node.val, VariableExpr) and node.val.name in self.functions: return
            self.analyze_expr(node.val)
        elif isinstance(node, DerefExpr): self.analyze_expr(node.val)
        elif isinstance(node, UnaryExpr): self.analyze_expr(node.val)
        elif isinstance(node, PropagateExpr): self.analyze_expr(node.val)
        elif isinstance(node, ComptimeExpr): return self.analyze_expr(node.expr)
        # NOVO: Validação de Struct Literal
        elif isinstance(node, StructLiteralExpr):
            if node.struct_name not in self.struct_defs:
                raise LuminaError(f"Struct '{node.struct_name}' não declarada.", self.filename, 0, 0, self.source_code)
            struct_def = self.struct_defs[node.struct_name]
            for field_name, field_expr in node.fields:
                if field_name not in struct_def.fields:
                    raise LuminaError(f"Campo '{field_name}' não existe na Struct '{node.struct_name}'.", self.filename, 0, 0, self.source_code)
                self.analyze_expr(field_expr)
            return node.struct_name # Retorna o tipo da Struct
        # NOVO: Validação do Match Expression
        elif isinstance(node, MatchExpr):
            self.analyze_expr(node.condition)
            for val, res in node.cases:
                # NOVO: Se for um Struct Literal, as variáveis nos campos são bindings (novas variáveis)
                if isinstance(val, StructLiteralExpr):
                    for field_name, field_expr in val.fields:
                        if isinstance(field_expr, VariableExpr):
                            # Declara a variável local para o Codegen saber que ela existe
                            self.declare_var(field_expr.name, "int", True)
                        else:
                            self.analyze_expr(field_expr)
                else:
                    self.analyze_expr(val)
                self.analyze_expr(res)
            if node.default:
                self.analyze_expr(node.default)

        # NOVO: Validação do CastExpr
        elif isinstance(node, CastExpr):
            self.analyze_expr(node.expr)
            if node.target_type not in ("int", "float", "bool", "str", "ptr"):
                base = node.target_type.split('<')[0]
                if base not in self.structs:
                    raise LuminaError(f"Tipo de destino '{node.target_type}' não declarado.", self.filename, 0, 0, self.source_code)
                    
        # NOVO: Validação do LambdaExpr
        elif isinstance(node, LambdaExpr):
            self.push_scope()
            for p_name, p_type, _ in node.params:
                self.declare_var(p_name, p_type, True)
            for stmt in node.body:
                self.analyze_stmt(stmt)
            self.pop_scope()
            