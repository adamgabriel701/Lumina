import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional

# Detecção automática de suporte a cores ANSI
def _supports_color():
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

HAS_COLOR = _supports_color()

class Colors:
    RED = '\033[91m' if HAS_COLOR else ''
    BOLD = '\033[1m' if HAS_COLOR else ''
    CYAN = '\033[96m' if HAS_COLOR else ''
    YELLOW = '\033[93m' if HAS_COLOR else ''
    BLUE = '\033[94m' if HAS_COLOR else ''
    RESET = '\033[0m' if HAS_COLOR else ''

@dataclass
class LuminaError(Exception):
    message: str
    filename: str
    line: int = 0
    col: int = 0
    source_code: str = ""
    end_col: Optional[int] = None  # NOVO: Para sublinhar intervalos maiores que 1 caractere
    notes: List[str] = field(default_factory=list)  # NOVO: Para dicas extras
    context_lines: int = 1  # NOVO: Quantas linhas antes do erro mostrar

    def __post_init__(self):
        super().__init__(self.format_error())

    def add_note(self, note_msg: str):
        """Adiciona uma nota de ajuda ao erro (estilo Rust)"""
        self.notes.append(note_msg)

    def format_error(self) -> str:
        # Formato simples, sem localização no código
        if self.line == 0 or not self.source_code:
            error_str = f"\n{Colors.BOLD}erro:{Colors.RESET} {self.message}\n"
            if self.filename:
                error_str += f"  {Colors.CYAN}-->{Colors.RESET} {self.filename}\n"
            for note in self.notes:
                error_str += f"  {Colors.BLUE}nota:{Colors.RESET} {note}\n"
            return error_str
        
        lines = self.source_code.split('\n')
        line_idx = self.line - 1
        
        if line_idx >= len(lines):
            return f"\n{Colors.BOLD}erro:{Colors.RESET} {self.message} (Linha fora do alcance)\n"
            
        line_str = lines[line_idx]
        
        # Determina o tamanho da seta / sublinhado
        start_col = max(1, self.col)
        end_col = self.end_col if self.end_col else start_col + 1
        
        # Se for apenas um caractere, usa ^. Se for maior, usa ^^^^
        underline_len = max(1, end_col - start_col)
        underline = "^" * underline_len
        
        padding = " " * len(str(self.line))
        caret_padding = " " * (start_col - 1)
        
        # Destaca a palavra exata na linha de código (se o sublinhado for na mesma palavra)
        highlighted_line = (
            line_str[:start_col-1] + 
            Colors.BOLD + Colors.RED + line_str[start_col-1:end_col-1] + Colors.RESET + 
            line_str[end_col-1:]
        )
        
        error_str = f"\n{Colors.BOLD}erro:{Colors.RESET} {self.message}\n"
        error_str += f"  {Colors.CYAN}-->{Colors.RESET} {self.filename}:{self.line}:{start_col}\n"
        error_str += f"  {padding} |\n"
        
        # Linha de contexto anterior (se existir)
        if self.context_lines > 0 and line_idx > 0:
            prev_line_num = self.line - 1
            prev_line = lines[line_idx - 1]
            prev_pad = " " * len(str(prev_line_num))
            error_str += f"  {Colors.YELLOW}{prev_line_num}{Colors.RESET} {Colors.YELLOW}|{Colors.RESET} {prev_line}\n"
        
        # Linha do erro
        error_str += f"  {Colors.YELLOW}{self.line}{Colors.RESET} {Colors.YELLOW}|{Colors.RESET} {highlighted_line}\n"
        # Seta de erro
        error_str += f"  {padding} {Colors.YELLOW}|{Colors.RESET} {caret_padding}{Colors.BOLD}{Colors.RED}{underline}{Colors.RESET}\n"
        
        # Notas anexas
        for note in self.notes:
            error_str += f"  {padding} {Colors.YELLOW}={Colors.RESET} {Colors.BLUE}nota:{Colors.RESET} {note}\n"
            
        return error_str