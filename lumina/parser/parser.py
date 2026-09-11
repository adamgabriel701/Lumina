from ..lexer.tokens import TokenType
from .expressions import ExpressionParser
from .statements import StatementParser
from ..ast import StructDecl, ImplBlock, ImportStmt, ExternDecl, EnumDecl, TraitDecl, VarDecl, Function
from ..errors import LuminaError

class Parser(ExpressionParser, StatementParser):
    def __init__(self, tokens, filename="program.lm", source_code=""):
        self.tokens = tokens
        self.pos = 0
        self.filename = filename
        self.source_code = source_code
        self.no_struct_literal = False # NOVO: Flag para desativar Struct Literals no match

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def peek(self, offset=1):
        if self.pos + offset < len(self.tokens): return self.tokens[self.pos + offset]
        return None

    def consume(self, expected_type=None):
        token = self.current_token()
        if token and (expected_type is None or token.type == expected_type):
            self.pos += 1
            return token
        if token: 
            raise LuminaError(f"Esperado {expected_type}, mas encontrei {token.type} ('{token.value}')", self.filename, token.line, token.col, self.source_code)
        raise LuminaError("Fim inesperado do código", self.filename, 0, 0, self.source_code)

    def parse(self):
        declarations = []
        while self.current_token() and self.current_token().type != TokenType.EOF:
            try:
                if self.current_token().type == TokenType.KEYWORD and self.current_token().value in ('fn', 'export'):
                    declarations.append(self.parse_function())
                elif self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'struct':
                    declarations.append(self.parse_struct())
                elif self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'enum':
                    declarations.append(self.parse_enum())
                elif self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'impl':
                    declarations.append(self.parse_impl())
                elif self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'trait':
                    declarations.append(self.parse_trait())
                elif self.current_token().type == TokenType.KEYWORD and self.current_token().value in ('let', 'mut', 'test', 'bench', 'import', 'extern'):
                    declarations.append(self.parse_statement())
                else:
                    self.consume()
            except LuminaError as e:
                # NOVO: Em vez de parar tudo, registra o erro e pula para a próxima declaração
                # O LSP vai pegar esse erro da AST e reportar, mas continuará parseando o resto!
                from ..ast import ErrorNode
                declarations.append(ErrorNode(e.message, e.line, e.col))
                
                # Sincroniza: pula tokens até achar um 'fn', 'let', 'struct' ou fim do arquivo
                while self.current_token() and self.current_token().type != TokenType.EOF:
                    if self.current_token().type == TokenType.KEYWORD and self.current_token().value in ('fn', 'let', 'mut', 'struct', 'enum', 'impl', 'trait', 'import', 'extern', 'export'):
                        break
                    self.consume()
                    
        return declarations