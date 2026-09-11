# visitor.py
from functools import singledispatch
from expressions import (
    Expr, NumberExpr, StringExpr, VariableExpr, 
    BinaryExpr, UnaryExpr, CallExpr, MemberExpr, 
    PropagateExpr, LambdaExpr
)

class Visitor:
    def visit(self, expr: Expr):
        # O singledispatch chama a função correta baseada no tipo de 'expr'
        return self._visit(expr)

    # O método padrão, caso encontre um nó que não tem handler específico
    @singledispatch
    def _visit(self, expr: Expr):
        raise NotImplementedError(f"Nenhuma visita definida para o nó do tipo: {type(expr).__name__}")

    # --- Handlers para cada tipo de Expressão ---

    @_visit.register
    def _(self, expr: NumberExpr):
        # Lógica para visitar um número
        # Ex: converter para int/float e retornar
        print(f"Visitando NumberExpr: {expr.value}")
        return float(expr.value) if expr.is_float else int(expr.value)

    @_visit.register
    def _(self, expr: StringExpr):
        # Lógica para visitar string
        print(f"Visitando StringExpr: {expr.value}")
        return expr.value

    @_visit.register
    def _(self, expr: VariableExpr):
        # Lógica para resolver variável (ex: buscar na tabela de símbolos)
        print(f"Visitando VariableExpr: {expr.name}")
        return f"<var:{expr.name}>"

    @_visit.register
    def _(self, expr: BinaryExpr):
        # A ordem importa! Visitamos esquerda, depois direita, depois aplicamos o operador
        print(f"Visitando BinaryExpr: {expr.op}")
        left_val = self.visit(expr.left)
        right_val = self.visit(expr.right)
        
        # Exemplo de avaliação simples (um interpretador real teria checagens de tipo aqui)
        if expr.op == '+': return left_val + right_val
        if expr.op == '-': return left_val - right_val
        # ... outros operadores ...

    @_visit.register
    def _(self, expr: UnaryExpr):
        print(f"Visitando UnaryExpr: {expr.op}")
        val = self.visit(expr.val)
        if expr.op == '-': return -val
        if expr.op == '!': return not val
        return val

    @_visit.register
    def _(self, expr: CallExpr):
        print(f"Visitando CallExpr")
        # Em um interpretador: avalia a função 'callee', avalia os 'args', e executa
        callee = self.visit(expr.callee)
        args = [self.visit(arg) for arg in expr.args]
        # return callee(*args)
        return None

    @_visit.register
    def _(self, expr: MemberExpr):
        print(f"Visitando MemberExpr: .{expr.member}")
        obj = self.visit(expr.obj)
        # Lógica de acesso a campo/método de struct
        # return getattr(obj, expr.member)
        return None

    @_visit.register
    def _(self, expr: PropagateExpr):
        print(f"Visitando PropagateExpr (?)")
        val = self.visit(expr.val)
        # Se for erro, propaga. Se não, extrai o valor.
        return val

    @_visit.register
    def _(self, expr: LambdaExpr):
        print(f"Visitando LambdaExpr")
        # Em um interpretador, você criaria um closure (ambiente capturado + corpo da função)
        return None
