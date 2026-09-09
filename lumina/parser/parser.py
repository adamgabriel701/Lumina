from ..lexer.tokens import TokenType
from .expressions import ExpressionParser
from .statements import StatementParser
from ..ast import StructDecl, ImplBlock, ImportStmt, ExternDecl, EnumDecl, TraitDecl, Function
from ..errors import LuminaError

class Parser(ExpressionParser, StatementParser):
    def __init__(self, tokens, filename="program.lm", source_code=""):
        self.tokens = tokens
        self.pos = 0
        self.filename = filename
        self.source_code = source_code

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
            raise LuminaError(
                f"Esperado {expected_type}, mas encontrei {token.type} ('{token.value}')",
                self.filename, token.line, token.col, self.source_code
            )
        raise LuminaError("Fim inesperado do código", self.filename, 0, 0, self.source_code)

    def parse(self):
        declarations = []
        while self.current_token() and self.current_token().type != TokenType.EOF:
            if self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'fn':
                declarations.append(self.parse_function())
            elif self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'struct':
                declarations.append(self.parse_struct())
            elif self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'enum':
                declarations.append(self.parse_enum())
            elif self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'impl':
                declarations.append(self.parse_impl())
            elif self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'import':
                declarations.append(self.parse_statement())
            elif self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'extern':
                declarations.append(self.parse_extern())
            elif self.current_token().type == TokenType.KEYWORD and self.current_token().value in ('let', 'mut'):
                declarations.append(self.parse_statement())
            elif self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'test':
                declarations.append(self.parse_statement())
            elif self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'bench':
                declarations.append(self.parse_statement())
            # NOVO: Aceita declaração de Traits
            elif self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'trait':
                declarations.append(self.parse_trait())
            else:
                self.consume()
        return declarations

    # NOVO MÉTODO PARA PARSE DE TRAIT
    def parse_trait(self):
        self.consume() # 'trait'
        name = self.consume(TokenType.IDENT).value
        self.consume(TokenType.OP) # ':'
        self.consume(TokenType.NEWLINE)
        self.consume(TokenType.INDENT)
        
        methods = []
        while self.current_token() and self.current_token().type != TokenType.DEDENT:
            if self.current_token().type == TokenType.NEWLINE: 
                self.consume()
                continue
            if self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'fn':
                # Lê a assinatura da função (sem corpo)
                self.consume() # 'fn'
                m_name = self.consume(TokenType.IDENT).value
                self.consume(TokenType.OP) # '('
                params = []
                if self.current_token().type != TokenType.OP or self.current_token().value != ')':
                    while True:
                        p_name = self.consume(TokenType.IDENT).value
                        self.consume(TokenType.OP) # ':'
                        p_type = self.consume(TokenType.IDENT).value
                        params.append((p_name, p_type))
                        if self.current_token().type == TokenType.OP and self.current_token().value == ',':
                            self.consume()
                        else:
                            break
                self.consume(TokenType.OP) # ')'
                return_type = "void"
                if self.current_token().type == TokenType.OP and self.current_token().value == '->':
                    self.consume()
                    return_type = self.consume(TokenType.IDENT).value
                self.consume(TokenType.NEWLINE)
                
                # Cria uma Function com corpo vazio (apenas assinatura)
                methods.append(Function(m_name, params, return_type, []))
                
        self.consume(TokenType.DEDENT)
        return TraitDecl(name, methods)