from ..ast import (
    NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, 
    ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, UnaryExpr, 
    PropagateExpr, ComptimeExpr, StructLiteralExpr, MatchExpr, CastExpr, LambdaExpr, StructLiteralField
)
from ..ast.visitor import NodeVisitor
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
    best_dist = 3
    for candidate in possible_names:
        dist = levenshtein(name, candidate)
        if dist < best_dist:
            best_dist = dist
            best_match = candidate
    return best_match

class ExpressionAnalyzer(NodeVisitor):
    
    def visit_NumberExpr(self, node): return "int" if not node.is_float else "float"
    def visit_BoolExpr(self, node): return "bool"
    def visit_StringExpr(self, node): return "str"

    def visit_VariableExpr(self, node):
        info = self.get_var_info(node.name)
        if not info:
            available_vars = [k for scope in self.scopes for k in scope.keys()]
            suggestion = get_suggestion(node.name, available_vars)
            msg = f"Variável '{node.name}' não declarada."
            if suggestion:
                msg += f" Você quis dizer '{suggestion}'?"
            raise LuminaError(msg, self.filename, node.line, node.col, self.source_code)
        return info['type']

    def visit_BinaryExpr(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        
        if node.op in ('==', '!=', '<', '>', '<=', '>='):
            if left_type and right_type and left_type != right_type:
                raise LuminaError(f"Tipos incompatíveis na comparação: '{left_type}' e '{right_type}'", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            return "bool"
            
        if node.op in ('and', 'or'):
            if left_type != "bool" or right_type != "bool":
                raise LuminaError(f"Operador lógico '{node.op}' requer operandos 'bool'", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            return "bool"
        
        if left_type and left_type.split('<')[0] in self.structs:
            struct_name = left_type.split('<')[0]
            op_map = {'+': '__add__', '-': '__sub__', '*': '__mul__', '/': '__div__', '==': '__eq__'}
            method_name = op_map.get(node.op)
            if method_name:
                real_method_name = f"{struct_name}_{method_name}"
                if real_method_name not in self.functions:
                    raise LuminaError(f"Operador '{node.op}' não definido para a struct '{struct_name}'.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
        return left_type

    def visit_CallExpr(self, node):
        func_name = None
        if isinstance(node.callee, MemberExpr):
            func_name = node.callee.member
        elif isinstance(node.callee, VariableExpr):
            func_name = node.callee.name
            
        if node.is_method:
            if not node.args:
                raise LuminaError(f"Chamada de método '{func_name}' sem objeto alvo.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            obj_node = node.args[0]
            obj_type = self.visit(obj_node)
            if not obj_type: return None
            if obj_type == "str":
                if func_name not in ("contains", "starts_with", "len", "upper", "lower"):
                    raise LuminaError(f"Método de string '{func_name}' não suportado.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            elif obj_type != "Unknown":
                struct_name = obj_type.split('<')[0]
                real_method_name = f"{struct_name}_{func_name}"
                if real_method_name not in self.functions:
                    raise LuminaError(f"Método '{func_name}' não implementado para a struct '{struct_name}'.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
        else:
            if func_name not in self.builtin_functions and func_name not in self.functions:
                suggestion = get_suggestion(func_name, list(self.functions) + list(self.builtin_functions))
                msg = f"Função '{func_name}' não declarada."
                if suggestion: msg += f" Você quis dizer '{suggestion}'?"
                raise LuminaError(msg, self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            
            # NOVO: Checa aridade e tipos
            if func_name in self.function_defs:
                fn_def = self.function_defs[func_name]
                if len(node.args) != len(fn_def.params):
                    raise LuminaError(f"Função '{func_name}' espera {len(fn_def.params)} args, recebeu {len(node.args)}.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
                for arg_node, param in zip(node.args, fn_def.params):
                    arg_type = self.visit(arg_node)
                    p_name, p_type = param.name, param.type_ann
                    if arg_type and p_type and arg_type != p_type:
                        raise LuminaError(f"Tipo inválido para parâmetro '{p_name}': esperado '{p_type}', obteve '{arg_type}'.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            return None
            
        for arg in node.args:
            self.visit(arg)
        return None

    def visit_ArrayExpr(self, node):
        for el in node.elements:
            self.visit(el)
        return "array"

    def visit_IndexExpr(self, node):
        self.visit(node.array)
        self.visit(node.index)
        return None

    def visit_MemberExpr(self, node):
        current_type = self.visit(node.obj)
        base_type = current_type.split('<')[0] if current_type else "Unknown"
        
        if base_type not in self.struct_defs:
            raise LuminaError(f"Tipo '{current_type}' não é uma Struct/Enum ou não possui membros.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            
        struct_def = self.struct_defs[base_type]
        
        # NOVO: Trata Structs vs Enums
        if hasattr(struct_def, 'fields') and node.member in struct_def.fields:
            return struct_def.fields[node.member]
        elif hasattr(struct_def, 'variants') and any(v[0] == node.member for v in struct_def.variants):
            return base_type
        else:
            raise LuminaError(f"Campo '{node.member}' não existe na Struct/Enum '{current_type}'.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)

    def visit_AddressOfExpr(self, node):
        if isinstance(node.val, VariableExpr) and node.val.name in self.functions:
            return "ptr"
        self.visit(node.val)
        return "ptr"

    def visit_DerefExpr(self, node):
        self.visit(node.val)
        return None

    def visit_UnaryExpr(self, node):
        self.visit(node.val)
        return None

    def visit_PropagateExpr(self, node):
        self.visit(node.val)
        if not hasattr(self, 'current_ret_type') or not self.current_ret_type.startswith("Result"):
            raise LuminaError(
                "Operador '?' só pode ser usado em funções que retornam 'Result'.", 
                self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code
            )
        return None

    def visit_ComptimeExpr(self, node):
        return self.visit(node.expr)

    def visit_StructLiteralExpr(self, node):
        if node.struct_name not in self.struct_defs:
            raise LuminaError(f"Struct '{node.struct_name}' não declarada.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            
        struct_def = self.struct_defs[node.struct_name]
        defined_fields = set(struct_def.fields.keys())
        passed_fields = set()
        
        # ATUALIZADO: Usa StructLiteralField
        for field in node.fields:
            if field.name not in struct_def.fields:
                raise LuminaError(f"Campo '{field.name}' não existe na Struct '{node.struct_name}'.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            self.visit(field.value)
            passed_fields.add(field.name)
            
        missing = defined_fields - passed_fields
        if missing:
            raise LuminaError(f"Campos faltando na inicialização da Struct '{node.struct_name}': {', '.join(missing)}", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
        return node.struct_name

    def visit_MatchExpr(self, node):
        self.visit(node.condition)
        
        for val, res in node.cases:
            self.push_scope()
            if isinstance(val, StructLiteralExpr):
                # Proteção contra KeyError
                if val.struct_name not in self.struct_defs:
                    raise LuminaError(f"Struct '{val.struct_name}' não declarada.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
                    
                # ATUALIZADO: Usa StructLiteralField
                for field in val.fields:
                    if isinstance(field.value, VariableExpr):
                        field_type = self.struct_defs[val.struct_name].fields.get(field.name, "int")
                        self.declare_var(field.value.name, field_type, True)
                    else:
                        self.visit(field.value)
            else:
                self.visit(val)
            self.visit(res)
            self.pop_scope()
            
        if node.default:
            self.visit(node.default)
        return None

    def visit_CastExpr(self, node):
        self.visit(node.expr)
        if node.target_type not in ("int", "float", "bool", "str", "ptr"):
            base = node.target_type.split('<')[0]
            if base not in self.structs:
                raise LuminaError(
                    f"Tipo de destino '{node.target_type}' não declarado.", 
                    self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code
                )
        return node.target_type

    def visit_LambdaExpr(self, node):
        self.push_scope()
        # ATUALIZADO: Usa Param dataclass
        for param in node.params:
            self.declare_var(param.name, param.type_ann, True)
        for stmt in node.body:
            self.analyze_stmt(stmt)
        self.pop_scope()
        return "fn"

    def generic_visit(self, node):
        # Não levanta erro, apenas retorna None para não travar a análise
        return None