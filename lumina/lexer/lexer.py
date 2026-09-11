import re

from lumina.errors import LuminaError
from .tokens import TokenType, Token, KEYWORDS

class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.indent_stack = [0]

    def tokenize(self):
        # Remove comentários multi-linha
        self.code = re.sub(r'/\*.*?\*/', '', self.code, flags=re.DOTALL)
        lines = self.code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Remove comentários inline (#) que não estão dentro de strings
            in_string = False
            clean_line = ""
            for c in line:
                if c == '"': in_string = not in_string
                if c == '#' and not in_string: break
                clean_line += c
            
            stripped = clean_line.lstrip()
            if not stripped or stripped.startswith('#'):
                # Mesmo em linhas vazias, precisamos emitir NEWLINE para o parser não travar
                if stripped == "":
                    self.tokens.append(Token(TokenType.NEWLINE, '', line_num, 1, 0))
                continue
            
            indent = len(clean_line) - len(stripped)
            if indent > self.indent_stack[-1]:
                self.tokens.append(Token(TokenType.INDENT, '', line_num, indent, 0))
                self.indent_stack.append(indent)
            elif indent < self.indent_stack[-1]:
                while indent < self.indent_stack[-1]:
                    self.indent_stack.pop()
                    self.tokens.append(Token(TokenType.DEDENT, '', line_num, indent, 0))
            
            i = 0
            while i < len(stripped):
                c = stripped[i]
                col = indent + i + 1
                
                if c == ' ':
                    i += 1
                    continue
                    
                # F-strings (prefixo $)
                elif c == '$':
                    self.tokens.append(Token(TokenType.OP, '$', line_num, col, 0))
                    i += 1
                    continue
                    
                # Strings
                elif c == '"':
                    j = i + 1
                    raw_str = ""
                    while j < len(stripped) and stripped[j] != '"':
                        if stripped[j] == '\\' and j + 1 < len(stripped):
                            next_char = stripped[j+1]
                            if next_char == 'n':
                                raw_str += '\n'
                                j += 2
                                continue
                            elif next_char == 'r':
                                raw_str += '\r'
                                j += 2
                                continue
                            elif next_char == 't':
                                raw_str += '\t'
                                j += 2
                                continue
                            elif next_char == '\\':
                                raw_str += '\\'
                                j += 2
                                continue
                            elif next_char == '"':
                                raw_str += '"'
                                j += 2
                                continue
                        raw_str += stripped[j]
                        j += 1
                        
                    self.tokens.append(Token(TokenType.STRING, raw_str, line_num, col, 0))
                    i = j + 1
                    continue
                    
                # Números (Hexadecimal e Decimal/Float)
                elif c.isdigit():
                    j = i
                    if c == '0' and j + 1 < len(stripped) and (stripped[j+1] == 'x' or stripped[j+1] == 'X'):
                        j += 2
                        while j < len(stripped) and (stripped[j].isdigit() or stripped[j] in 'abcdefABCDEF'): j += 1
                        self.tokens.append(Token(TokenType.NUMBER, stripped[i:j], line_num, col, 0))
                        i = j
                        continue
                        
                    while j < len(stripped) and stripped[j].isdigit(): j += 1
                    if j < len(stripped) and stripped[j] == '.' and j+1 < len(stripped) and stripped[j+1].isdigit():
                        j += 1
                        while j < len(stripped) and stripped[j].isdigit(): j += 1
                    self.tokens.append(Token(TokenType.NUMBER, stripped[i:j], line_num, col, 0))
                    i = j
                    continue
                    
                # Identificadores e Palavras-Chave
                elif c.isalpha() or c == '_':
                    j = i
                    while j < len(stripped) and (stripped[j].isalnum() or stripped[j] == '_'): j += 1
                    word = stripped[i:j]
                    
                    # Removido o hack do print, agora ele é lido como IDENT normal
                    token_type = KEYWORDS.get(word, TokenType.IDENT)
                    self.tokens.append(Token(token_type, word, line_num, col, 0))
                    i = j
                    continue
                    
                # Operadores de 2 caracteres
                elif i + 1 < len(stripped) and stripped[i:i+2] in ('==', '!=', '<=', '>=', '->', '..', '+=', '-=', '*=', '/=', '|>', '<<', '>>', '?.', '=>', ':='):
                    op_map = {
                        '==': TokenType.EQ, '!=': TokenType.NEQ, '<=': TokenType.LTE, '>=': TokenType.GTE,
                        '->': TokenType.ARROW, '..': TokenType.DOT, '+=': TokenType.PLUS_ASSIGN, 
                        '-=': TokenType.MINUS_ASSIGN, '*=': TokenType.STAR_ASSIGN, '/=': TokenType.SLASH_ASSIGN,
                        '|>': TokenType.PIPE, '<<': TokenType.SHL, '>>': TokenType.SHR, 
                        '?.': TokenType.DOT, '=>': TokenType.FAT_ARROW, ':=': TokenType.ASSIGN
                    }
                    op_str = stripped[i:i+2]
                    # CORREÇÃO: Em vez de usar TokenType.OP como fallback, disparamos um erro se o operador não for reconhecido
                    if op_str in op_map:
                        self.tokens.append(Token(op_map[op_str], op_str, line_num, col, 0))
                    else:
                        raise LuminaError(f"Operador desconhecido: '{op_str}'", self.filename if hasattr(self, 'filename') else "lexer", line_num, col, self.code)
                    i += 2
                    continue
                    
                # Operadores e Pontuação de 1 caractere
                elif c == '@':
                    self.tokens.append(Token(TokenType.OP, '@', line_num, col, 0))
                    i += 1
                    continue
                elif c == '?':
                    self.tokens.append(Token(TokenType.QUESTION, '?', line_num, col, 0))
                    i += 1
                    continue
                    
                # Mapeamento direto de símbolos simples para seus respectivos Tokens
                else:
                    single_ops = {
                        '+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.STAR, '/': TokenType.SLASH,
                        '%': TokenType.PERCENT, '!': TokenType.BANG, '&': TokenType.AMP, '|': TokenType.PIPE,
                        '^': TokenType.CARET, '~': TokenType.TILDE, '=': TokenType.ASSIGN,
                        '<': TokenType.LT, '>': TokenType.GT, '(': TokenType.LPAREN, ')': TokenType.RPAREN,
                        '{': TokenType.LBRACE, '}': TokenType.RBRACE, '[': TokenType.LBRACKET, ']': TokenType.RBRACKET,
                        ',': TokenType.COMMA, '.': TokenType.DOT, ':': TokenType.COLON, ';': TokenType.SEMICOLON,
                        '@': TokenType.AT
                    }
                    
                    if c in single_ops:
                        self.tokens.append(Token(single_ops[c], c, line_num, col, 0))
                        i += 1
                        continue
                    
                    # Se chegou até aqui, é um caractere ilegal
                    raise LuminaError(f"Caractere inesperado no código: '{c}'", getattr(self, 'filename', "lexer"), line_num, col, self.code)
            
            self.tokens.append(Token(TokenType.NEWLINE, '', line_num, indent + 1, 0))
            
        while self.indent_stack[-1] > 0:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, '', len(lines), 1, 0))
            
        self.tokens.append(Token(TokenType.EOF, '', len(lines), 1, 0))
        return self.tokens