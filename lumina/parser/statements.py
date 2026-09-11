from lumina.errors import LuminaError

from ..ast import VarDecl, AssignStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt, StructDecl, VariableExpr, MatchStmt, ImplBlock, DerefExpr, MemberExpr, IndexExpr, ImportStmt, ExternDecl, EnumDecl, BinaryExpr, ContinueStmt, DeferStmt, NumberExpr, BreakStmt, AssertStmt, BenchStmt, TraitDecl, DestructureStmt
from ..lexer import TokenType
from .declarations import DeclarationsParser
from .control_flow import ControlFlowParser

class StatementParser(DeclarationsParser, ControlFlowParser):
    def parse_statement(self):
        try:
            token = self.current_token()
            if token.type == TokenType.KEYWORD and token.value == 'struct': return self.parse_struct()
            elif token.type == TokenType.KEYWORD and token.value == 'impl': return self.parse_impl()
            elif token.type == TokenType.KEYWORD and token.value == 'return':
                self.consume()
                if self.current_token() and self.current_token().type == TokenType.NEWLINE:
                    self.consume(); return ReturnStmt([NumberExpr("0")])
                values = [self.parse_expression()]
                while self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == ',':
                    self.consume(); values.append(self.parse_expression())
                self.consume(TokenType.NEWLINE); return ReturnStmt(values)
            elif token.type == TokenType.KEYWORD and token.value in ('let', 'mut'): return self.parse_let()
            elif token.type == TokenType.KEYWORD and token.value in ('if', 'elif'): return self.parse_if()
            elif token.type == TokenType.KEYWORD and token.value == 'while': return self.parse_while()
            elif token.type == TokenType.KEYWORD and token.value == 'for': return self.parse_for()
            elif token.type == TokenType.KEYWORD and token.value == 'match': return self.parse_match()
            elif token.type == TokenType.KEYWORD and token.value == 'switch': return self.parse_switch()
            elif token.type == TokenType.OP and token.value == '*':
                node = self.parse_expression()
                if self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value == '=':
                    self.consume(); expr = self.parse_expression(); self.consume(TokenType.NEWLINE); return AssignStmt(node, expr)
                self.consume(TokenType.NEWLINE); return node
            elif token.type == TokenType.IDENT and self.peek() and self.peek().type == TokenType.OP and self.peek().value in ('=', '+=', '-=', '*=', '/=', ':='):
                name = self.consume(TokenType.IDENT).value; op = self.consume().value; expr = self.parse_expression(); self.consume(TokenType.NEWLINE)
                if op != '=' and op != ':=': expr = BinaryExpr(op, VariableExpr(name), expr)
                return VarDecl(name, None, expr, True)
            elif token.type == TokenType.IDENT and self.peek() and self.peek().type == TokenType.OP and self.peek().value in ('[', '.'):
                node = self.parse_expression()
                if self.current_token() and self.current_token().type == TokenType.OP and self.current_token().value in ('=', '+=', '-=', '*=', '/='):
                    op = self.consume().value; expr = self.parse_expression(); self.consume(TokenType.NEWLINE)
                    if op != '=': expr = BinaryExpr(op, node, expr)
                    return AssignStmt(node, expr)
                self.consume(TokenType.NEWLINE); return node
            elif token.type == TokenType.KEYWORD and token.value == 'import':
                self.consume(); filename = self.consume(TokenType.STRING).value; self.consume(TokenType.NEWLINE); return ImportStmt(filename)
            elif token.type == TokenType.KEYWORD and token.value == 'extern': return self.parse_extern()
            elif token.type == TokenType.KEYWORD and token.value == 'continue': self.consume(); self.consume(TokenType.NEWLINE); return ContinueStmt()
            elif token.type == TokenType.KEYWORD and token.value == 'break': self.consume(); self.consume(TokenType.NEWLINE); return BreakStmt()
            elif token.type == TokenType.KEYWORD and token.value == 'defer': return self.parse_defer()
            elif token.type == TokenType.KEYWORD and token.value == 'assert': return self.parse_assert()
            elif token.type == TokenType.KEYWORD and token.value == 'test': return self.parse_test()
            elif token.type == TokenType.KEYWORD and token.value == 'bench': return self.parse_bench()
            elif token.type == TokenType.KEYWORD and token.value == 'trait': return self.parse_trait()
            else:
                expr = self.parse_expression(); self.consume(TokenType.NEWLINE); return expr
        except LuminaError as e:
            # NOVO: Recuperação de erro dentro de funções
            from ..ast import ErrorNode
            # Sincroniza: pula tokens até achar uma nova linha ou fim do bloco
            while self.current_token() and self.current_token().type not in (TokenType.NEWLINE, TokenType.DEDENT, TokenType.EOF):
                self.consume()
            if self.current_token() and self.current_token().type == TokenType.NEWLINE:
                self.consume()
            return ErrorNode(e.message, e.line, e.col)