from functools import singledispatch
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
    
    @singledispatch
    def analyze_expr(self, node):
        """Método padrão para nós não implementados."""
        raise NotImplementedError(f"Análise semântica não implementada para {type(node).__name__}")

    @analyze_expr.register
    def _(self, node: NumberExpr): return "int" if not node.is_float else "float"

    @analyze_expr.register
    def _(self, node: BoolExpr): return "bool"

    @analyze_expr.register
    def _(self, node: StringExpr): return "str"

    @analyze_expr.register
    def _(self, node: VariableExpr):
        info = self.get_var_info(node.name)
        if not info:
            available_vars = [k for scope in self.scopes for k in scope.keys()]
            suggestion = get_suggestion(node.name, available_vars)
            msg = f"Variável '{node.name}' não declarada."
            if suggestion:
                msg += f" Você quis dizer '{suggestion}'?"
            raise LuminaError(msg, self.filename, node.line, node.col, self.source_code)
        return info['type']

    @analyze_expr.register
    def _(self, node: BinaryExpr):
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

    @analyze_expr.register
    def _(self, node: CallExpr):
        # Métodos (a.b())
        if node.is_method:
            obj_node = node.args[0]
            obj_type = self.analyze_expr(obj_node)
            
            if obj_type == "str":
                if node.name not in ("contains", "starts_with"):
                    raise LuminaError(f"Método de string '{node.name}' não suportado.", self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            elif obj_type and obj_type != "Unknown":
                struct_name = obj_type.split('<')[0]
                real_method_name = f"{struct_name}_{node.name}"
                if real_method_name not in self.functions:
                    # Antes o código fazia 'pass' e ignorava. Agora acusa o erro!
                    raise LuminaError(
                        f"Método '{node.name}' não implementado para a struct '{struct_name}'.", 
                        self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code
                    )
        # Funções globais e Builtins
        elif node.name not in self.builtin_functions and node.name not in self.functions:
            suggestion = get_suggestion(node.name, list(self.functions) + list(self.builtin_functions))
            msg = f"Função '{node.name}' não declarada."
            if suggestion:
                msg += f" Você quis dizer '{suggestion}'?"
            raise LuminaError(msg, self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code)
            
        for arg in node.args: 
            self.analyze_expr(arg)
        return None

    @analyze_expr.register
    def _(self, node: ArrayExpr):
        for el in node.elements: 
            self.analyze_expr(el)
        return "array"

    @analyze_expr.register
    def _(self, node: IndexExpr):
        self.analyze_expr(node.array)
        self.analyze_expr(node.index)
        return None

    @analyze_expr.register
    def _(self, node: MemberExpr):
        current_type = self.analyze_expr(node.obj)
        base_type = current_type.split('<')[0] if current_type else "Unknown"
        
        if base_type not in self.struct_defs: 
            raise LuminaError(
                f"Tipo '{current_type}' não é uma Struct ou não possui membros.", 
                self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code
            )
            
        struct_def = self.struct_defs[base_type]
        if node.member not in struct_def.fields: 
            raise LuminaError(
                f"Campo '{node.member}' não existe na Struct '{current_type}'.", 
                self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code
            )
        return struct_def.fields[node.member]

    @analyze_expr.register
    def _(self, node: AddressOfExpr):
        # Se for endereço de função, não precisa declarar variável
        if isinstance(node.val, VariableExpr) and node.val.name in self.functions:
            return "ptr"
        self.analyze_expr(node.val)
        return "ptr"

    @analyze_expr.register
    def _(self, node: DerefExpr):
        self.analyze_expr(node.val)
        return None # O tipo exato dependeria de uma tabela de ponteiros mais detalhada

    @analyze_expr.register
    def _(self, node: UnaryExpr):
        self.analyze_expr(node.val)
        return None

    @analyze_expr.register
    def _(self, node: PropagateExpr):
        self.analyze_expr(node.val)
        if not hasattr(self, 'current_ret_type') or not self.current_ret_type.startswith("Result"):
            raise LuminaError(
                "Operador '?' só pode ser usado em funções que retornam 'Result'.", 
                self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code
            )
        return None

    @analyze_expr.register
    def _(self, node: ComptimeExpr):
        return self.analyze_expr(node.expr)

    @analyze_expr.register
    def _(self, node: StructLiteralExpr):
        if node.struct_name not in self.struct_defs:
            raise LuminaError(
                f"Struct '{node.struct_name}' não declarada.", 
                self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code
            )
            
        struct_def = self.struct_defs[node.struct_name]
        defined_fields = set(struct_def.fields.keys())
        passed_fields = set()
        
        for field_name, field_expr in node.fields:
            if field_name not in struct_def.fields:
                raise LuminaError(
                    f"Campo '{field_name}' não existe na Struct '{node.struct_name}'.", 
                    self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code
                )
            self.analyze_expr(field_expr)
            passed_fields.add(field_name)
            
        # Verifica campos obrigatórios que não foram passados
        missing = defined_fields - passed_fields
        if missing:
            raise LuminaError(
                f"Campos faltando na inicialização da Struct '{node.struct_name}': {', '.join(missing)}", 
                self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code
            )
        return node.struct_name

    @analyze_expr.register
    def _(self, node: MatchExpr):
        cond_type = self.analyze_expr(node.condition)
        
        for val, res in node.cases:
            # CORREÇÃO CRÍTICA: Abre um escopo local para os bindings do caso
            self.push_scope()
            
            # Destructuring de Structs: Point { x: a, y: b } declara 'a' e 'b'
            if isinstance(val, StructLiteralExpr):
                for field_name, field_expr in val.fields:
                    if isinstance(field_expr, VariableExpr):
                        # Declara a variável vinculada como o tipo do campo da struct
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

    @analyze_expr.register
    def _(self, node: CastExpr):
        self.analyze_expr(node.expr)
        if node.target_type not in ("int", "float", "bool", "str", "ptr"):
            base = node.target_type.split('<')[0]
            if base not in self.structs:
                raise LuminaError(
                    f"Tipo de destino '{node.target_type}' não declarado.", 
                    self.filename, getattr(node, 'line', 0), getattr(node, 'col', 0), self.source_code
                )
        return node.target_type

    @analyze_expr.register
    def _(self, node: LambdaExpr):
        # CORREÇÃO: O escopo do lambda é isolado, mas enxerga o escopo externo (closure)
        self.push_scope()
        for p_name, p_type, _ in node.params:
            self.declare_var(p_name, p_type, True)
        for stmt in node.body:
            self.analyze_stmt(stmt)
        self.pop_scope()
        return "fn"