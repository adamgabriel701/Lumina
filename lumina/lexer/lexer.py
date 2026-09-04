import re
from .tokens import TokenType, Token

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
                continue
            
            indent = len(clean_line) - len(stripped)
            if indent > self.indent_stack[-1]:
                self.tokens.append(Token(TokenType.INDENT, '', line_num, indent))
                self.indent_stack.append(indent)
            elif indent < self.indent_stack[-1]:
                while indent < self.indent_stack[-1]:
                    self.indent_stack.pop()
                    self.tokens.append(Token(TokenType.DEDENT, '', line_num, indent))
            
            i = 0
            while i < len(stripped):
                c = stripped[i]
                col = indent + i + 1
                
                if c == ' ':
                    i += 1
                    continue
                elif c == '"':
                    j = i + 1
                    # NOVO: Processa caracteres de escape (\n, \r, \t, etc)
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
                        
                    self.tokens.append(Token(TokenType.STRING, raw_str, line_num, col))
                    i = j + 1
                    continue
                elif c.isdigit():
                    j = i
                    while j < len(stripped) and stripped[j].isdigit(): j += 1
                    if j < len(stripped) and stripped[j] == '.' and j+1 < len(stripped) and stripped[j+1].isdigit():
                        j += 1
                        while j < len(stripped) and stripped[j].isdigit(): j += 1
                    self.tokens.append(Token(TokenType.NUMBER, stripped[i:j], line_num, col))
                    i = j
                    continue
                elif c.isalpha() or c == '_':
                    j = i
                    while j < len(stripped) and (stripped[j].isalnum() or stripped[j] == '_'): j += 1
                    word = stripped[i:j]
                    if word in ('fn', 'let', 'mut', 'if', 'elif', 'else', 'while', 'for', 'in', 'struct', 'impl', 'import', 'extern', 'enum', 'return', 'print', 'true', 'false', 'match', 'case', 'default', 'and', 'or', 'not', 'continue'):
                        self.tokens.append(Token(TokenType.KEYWORD, word, line_num, col))
                    else:
                        self.tokens.append(Token(TokenType.IDENT, word, line_num, col))
                    i = j
                    continue
                elif i + 1 < len(stripped) and stripped[i:i+2] in ('==', '!=', '<=', '>=', '->', '..', '+=', '-=', '*=', '/='):
                    self.tokens.append(Token(TokenType.OP, stripped[i:i+2], line_num, col))
                    i += 2
                    continue
                else:
                    self.tokens.append(Token(TokenType.OP, c, line_num, col))
                    i += 1
            
            self.tokens.append(Token(TokenType.NEWLINE, '', line_num, indent + 1))
            
        while self.indent_stack[-1] > 0:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, '', len(lines), 1))
            
        self.tokens.append(Token(TokenType.EOF, '', len(lines), 1))
        return self.tokens