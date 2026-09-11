from .tokens import Token, TokenType, KEYWORDS

class Lexer:
    def __init__(self, source: str, filename: str = "<string>"):
        self.source = source.replace('\r\n', '\n').replace('\r', '\n')
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
        self.indent_stack = [0]
        self.paren_depth = 0
        self.at_line_start = True

    def error(self, msg):
        raise SyntaxError(f"{self.filename}: Linha {self.line}, Coluna {self.col}: {msg}")

    def peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return '\0'

    def advance(self):
        c = self.peek()
        self.pos += 1
        if c == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return c

    def add_token(self, type: TokenType, value: str, line=None, col=None):
        self.tokens.append(Token(type, value, line or self.line, col or self.col, self.pos))

    def tokenize(self):
        while self.pos < len(self.source):
            if self.paren_depth > 0:
                self._skip_whitespace()
                while self.peek() == '\n':
                    self.advance()
            else:
                if self.at_line_start:
                    self._handle_indent()
                    if self.peek() == '\0': break
                else:
                    self._skip_whitespace()
                    if self.peek() == '\n':
                        self.advance()
                        self.add_token(TokenType.NEWLINE, "\n")
                        self.at_line_start = True
                        continue
                    elif self.peek() == '\0':
                        break

            if self.pos >= len(self.source):
                break

            c = self.peek()

            if c == '#':
                while self.peek() not in ('\n', '\0'):
                    self.advance()
                continue

            if c.isdigit():
                self._number()
                self.at_line_start = False
                continue

            if c == 'f' and self.peek(1) == '"':
                self.advance()
                self._string(interpolated=True)
                self.at_line_start = False
                continue

            if c == '"':
                self._string(interpolated=False)
                self.at_line_start = False
                continue

            if c.isalpha() or c == '_':
                start_col = self.col
                self._identifier(start_col)
                self.at_line_start = False
                continue

            self._operator()
            self.at_line_start = False

        if self.tokens and self.tokens[-1].type != TokenType.NEWLINE:
            self.add_token(TokenType.NEWLINE, "\n")
            
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.add_token(TokenType.DEDENT, "")
            
        self.add_token(TokenType.EOF, "")
        return self.tokens

    def _skip_whitespace(self):
        while self.peek() in (' ', '\t'):
            self.advance()

    def _handle_indent(self):
        self._skip_whitespace()
        
        if self.peek() == '\n':
            self.advance()
            self.add_token(TokenType.NEWLINE, "\n")
            self.at_line_start = True
            return
            
        if self.peek() == '\0':
            self.at_line_start = False
            return
            
        indent = self.col - 1
        if indent > self.indent_stack[-1]:
            self.indent_stack.append(indent)
            self.add_token(TokenType.INDENT, "")
        elif indent < self.indent_stack[-1]:
            while indent < self.indent_stack[-1]:
                self.indent_stack.pop()
                self.add_token(TokenType.DEDENT, "")
                
        self.at_line_start = False

    def _number(self):
        num_str = ""
        is_float = False

        if self.peek() == '0' and self.peek(1) in ('x', 'X'):
            num_str += self.advance() + self.advance()
            while self.peek().isalnum():
                num_str += self.advance()
            self.add_token(TokenType.NUMBER, num_str)
            return

        while self.peek().isdigit():
            num_str += self.advance()

        if self.peek() == '.' and self.peek(1).isdigit():
            is_float = True
            num_str += self.advance()
            while self.peek().isdigit():
                num_str += self.advance()

        if self.peek() in ('e', 'E'):
            is_float = True
            num_str += self.advance()
            if self.peek() in ('+', '-'):
                num_str += self.advance()
            while self.peek().isdigit():
                num_str += self.advance()

        if is_float:
            self.add_token(TokenType.FLOAT, num_str)
        else:
            self.add_token(TokenType.NUMBER, num_str)

    def _string(self, interpolated=False):
        self.advance()
        val = ""
        if interpolated:
            while self.peek() != '"' and self.peek() != '\0':
                if self.peek() == '\\':
                    val += self.advance()
                    if self.peek() != '\0': val += self.advance()
                else:
                    val += self.advance()
            if self.peek() == '\0': self.error("String não terminada")
            self.advance()
            self.add_token(TokenType.STRING, "f" + '"' + val + '"')
        else:
            while self.peek() != '"' and self.peek() != '\0':
                if self.peek() == '\\':
                    val += self.advance()
                    if self.peek() != '\0': val += self.advance()
                elif self.peek() == '\n':
                    self.error("String não terminada")
                else:
                    val += self.advance()
            if self.peek() == '\0': self.error("String não terminada")
            self.advance()
            self.add_token(TokenType.STRING, val)

    def _identifier(self, start_col):
        ident = ""
        while self.peek().isalnum() or self.peek() == '_':
            ident += self.advance()

        if ident in KEYWORDS:
            self.add_token(KEYWORDS[ident], ident, self.line, start_col)
        else:
            self.add_token(TokenType.IDENT, ident, self.line, start_col)

    def _operator(self):
        c = self.peek()
        c2 = self.peek(1)

        if c == '(':
            self.paren_depth += 1; self.advance(); self.add_token(TokenType.LPAREN, "(")
        elif c == ')':
            self.paren_depth -= 1; self.advance(); self.add_token(TokenType.RPAREN, ")")
        elif c == '[':
            self.paren_depth += 1; self.advance(); self.add_token(TokenType.LBRACKET, "[")
        elif c == ']':
            self.paren_depth -= 1; self.advance(); self.add_token(TokenType.RBRACKET, "]")
        elif c == '{':
            self.paren_depth += 1; self.advance(); self.add_token(TokenType.LBRACE, "{")
        elif c == '}':
            self.paren_depth -= 1; self.advance(); self.add_token(TokenType.RBRACE, "}")
        elif c == ',':
            self.advance(); self.add_token(TokenType.COMMA, ",")
        elif c == ':':
            if c2 == ':': self.advance(); self.advance(); self.add_token(TokenType.DOUBLE_COLON, "::")
            else: self.advance(); self.add_token(TokenType.COLON, ":")
        elif c == ';':
            self.advance(); self.add_token(TokenType.SEMICOLON, ";")
        elif c == '@':
            self.advance(); self.add_token(TokenType.AT, "@")
        elif c == '$':
            self.advance(); self.add_token(TokenType.DOLLAR, "$")
        elif c == '?':
            self.advance(); self.add_token(TokenType.QUESTION, "?")
        elif c == '.':
            if c2 == '.': self.advance(); self.advance(); self.add_token(TokenType.DOT_DOT, "..")
            else: self.advance(); self.add_token(TokenType.DOT, ".")
        elif c == '+':
            if c2 == '=': self.advance(); self.advance(); self.add_token(TokenType.PLUS_ASSIGN, "+=")
            else: self.advance(); self.add_token(TokenType.PLUS, "+")
        elif c == '-':
            if c2 == '=': self.advance(); self.advance(); self.add_token(TokenType.MINUS_ASSIGN, "-=")
            elif c2 == '>': self.advance(); self.advance(); self.add_token(TokenType.ARROW, "->")
            else: self.advance(); self.add_token(TokenType.MINUS, "-")
        elif c == '*':
            if c2 == '=': self.advance(); self.advance(); self.add_token(TokenType.STAR_ASSIGN, "*=")
            else: self.advance(); self.add_token(TokenType.STAR, "*")
        elif c == '/':
            if c2 == '=': self.advance(); self.advance(); self.add_token(TokenType.SLASH_ASSIGN, "/=")
            else: self.advance(); self.add_token(TokenType.SLASH, "/")
        elif c == '%':
            self.advance(); self.add_token(TokenType.PERCENT, "%")
        elif c == '=':
            if c2 == '=': self.advance(); self.advance(); self.add_token(TokenType.EQ, "==")
            elif c2 == '>': self.advance(); self.advance(); self.add_token(TokenType.FAT_ARROW, "=>")
            else: self.advance(); self.add_token(TokenType.ASSIGN, "=")
        elif c == '!':
            if c2 == '=': self.advance(); self.advance(); self.add_token(TokenType.NEQ, "!=")
            else: self.advance(); self.add_token(TokenType.BANG, "!")
        elif c == '<':
            if c2 == '=': self.advance(); self.advance(); self.add_token(TokenType.LTE, "<=")
            elif c2 == '<': self.advance(); self.advance(); self.add_token(TokenType.SHL, "<<")
            else: self.advance(); self.add_token(TokenType.LT, "<")
        elif c == '>':
            if c2 == '=': self.advance(); self.advance(); self.add_token(TokenType.GTE, ">=")
            elif c2 == '>': self.advance(); self.advance(); self.add_token(TokenType.SHR, ">>")
            else: self.advance(); self.add_token(TokenType.GT, ">")
        elif c == '&':
            if c2 == '=': self.advance(); self.advance(); self.add_token(TokenType.AMP_ASSIGN, "&=")
            elif c2 == '&': self.advance(); self.advance(); self.add_token(TokenType.AND, "&&")
            else: self.advance(); self.add_token(TokenType.AMP, "&")
        elif c == '|':
            if c2 == '=': self.advance(); self.advance(); self.add_token(TokenType.PIPE_ASSIGN, "|=")
            elif c2 == '|': self.advance(); self.advance(); self.add_token(TokenType.OR, "||")
            else: self.advance(); self.add_token(TokenType.PIPE, "|")
        elif c == '^':
            if c2 == '=': self.advance(); self.advance(); self.add_token(TokenType.CARET_ASSIGN, "^=")
            else: self.advance(); self.add_token(TokenType.CARET, "^")
        elif c == '~':
            self.advance(); self.add_token(TokenType.TILDE, "~")
        else:
            self.error(f"Caractere inesperado: '{c}'")