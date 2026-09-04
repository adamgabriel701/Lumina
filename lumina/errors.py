class LuminaError(Exception):
    def __init__(self, message, filename, line=0, col=0, source_code=""):
        self.message = message
        self.filename = filename
        self.line = line
        self.col = col
        self.source_code = source_code
        super().__init__(self.format_error())

    def format_error(self):
        # Se não temos linha/coluna, usa formato simples
        if self.line == 0:
            return f"\nErro: {self.message}\n  --> {self.filename}\n"
        
        lines = self.source_code.split('\n')
        # Pega a linha do erro (array é 0-indexed, linha é 1-indexed)
        line_str = lines[self.line - 1] if self.line - 1 < len(lines) else ""
        
        line_num_str = str(self.line)
        padding = " " * len(line_num_str)
        
        # Calcula os espaços para colocar a seta ^ na coluna exata
        caret_padding = " " * (self.col - 1)
        
        # Códigos de cor ANSI
        RED = '\033[91m'
        BOLD = '\033[1m'
        CYAN = '\033[96m'
        RESET = '\033[0m'
        
        error_str = f"\n{BOLD}Erro:{RESET} {self.message}\n"
        error_str += f"  {CYAN}-->{RESET} {self.filename}:{self.line}:{self.col}\n"
        error_str += f"  {padding} |\n"
        error_str += f"  {line_num_str} | {line_str}\n"
        error_str += f"  {padding} | {RED}{caret_padding}^{RESET}\n"
        
        return error_str
