from ..ast import NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, UnaryExpr, PropagateExpr, ComptimeExpr, StructLiteralExpr, MatchExpr, CastExpr
from ..errors import LuminaError

class ExpressionAnalyzer:
    def analyze_expr(self, node):
        if isinstance(node, (NumberExpr, BoolExpr, StringExpr)): return
        elif isinstance(node, VariableExpr):
            if not self.get_var_info(node.name):
                raise LuminaError(f"Variável '{node.name}' não declarada.", self.filename, node.line, node.col, self.source_code)
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
                self.analyze_expr(val)
                self.analyze_expr(res)
            if node.default:
                self.analyze_expr(node.default)

        # NOVO: Validação do CastExpr
        elif isinstance(node, CastExpr):
            self.analyze_expr(node.expr)
            # Apenas valida se o tipo alvo existe
            if node.target_type not in ("int", "float", "bool", "str", "ptr"):
                base = node.target_type.split('<')[0]
                if base not in self.structs:
                    raise LuminaError(f"Tipo de destino '{node.target_type}' não declarado.", self.filename, 0, 0, self.source_code)