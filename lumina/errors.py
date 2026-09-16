from dataclasses import dataclass, field
from typing import List, Optional

from .common.colors import Color as Colors  # reaproveita a paleta única


@dataclass
class LuminaError(Exception):
    message: str
    filename: str
    line: int = 0
    col: int = 0
    source_code: str = ""
    end_col: Optional[int] = None
    notes: List[str] = field(default_factory=list)
    context_lines: int = 1

    def __post_init__(self):
        Exception.__init__(self, self.format_error())

    def add_note(self, note_msg: str):
        self.notes.append(note_msg)
        # Re-formata para refletir notas adicionadas depois
        Exception.__init__(self, self.format_error())

    def to_dict(self) -> dict:
        """Retorna o erro como dict estruturado (para JSON, LSP, etc)."""
        return {
            "type": "error",
            "message": self.message,
            "filename": self.filename,
            "line": self.line,
            "col": self.col,
            "end_col": self.end_col,
            "notes": list(self.notes),
        }

    def to_json(self) -> str:
        """Retorna o erro como JSON de uma linha (ideal para CLI)."""
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def format_error(self) -> str:
        C = Colors

        if self.line == 0 or not self.source_code:
            s = f"\n{C.BOLD}erro:{C.RESET} {self.message}\n"
            if self.filename:
                s += f"  {C.CYAN}-->{C.RESET} {self.filename}\n"
            for note in self.notes:
                s += f"  {C.BLUE}nota:{C.RESET} {note}\n"
            return s

        lines = self.source_code.split("\n")
        line_idx = self.line - 1

        if line_idx < 0 or line_idx >= len(lines):
            return f"\n{C.BOLD}erro:{C.RESET} {self.message} (Linha fora do alcance)\n"

        # expandtabs(4) alinha com o lexer
        line_str = lines[line_idx].expandtabs(4)

        start_col = max(1, self.col)
        end_col = max(start_col + 1, self.end_col or start_col + 1)

        underline = "^" * (end_col - start_col)
        padding = " " * len(str(self.line))
        caret_padding = " " * (start_col - 1)

        highlighted = (
            line_str[: start_col - 1]
            + C.BOLD + C.RED + line_str[start_col - 1 : end_col - 1] + C.RESET
            + line_str[end_col - 1 :]
        )

        s = f"\n{C.BOLD}erro:{C.RESET} {self.message}\n"
        s += f"  {C.CYAN}-->{C.RESET} {self.filename}:{self.line}:{start_col}\n"
        s += f"  {padding} |\n"

        if self.context_lines > 0 and line_idx > 0:
            s += f"  {C.YELLOW}{self.line - 1}{C.RESET} {C.YELLOW}|{C.RESET} {lines[line_idx - 1].expandtabs(4)}\n"

        s += f"  {C.YELLOW}{self.line}{C.RESET} {C.YELLOW}|{C.RESET} {highlighted}\n"
        s += f"  {padding} {C.YELLOW}|{C.RESET} {caret_padding}{C.BOLD}{C.RED}{underline}{C.RESET}\n"

        for note in self.notes:
            s += f"  {padding} {C.YELLOW}={C.RESET} {C.BLUE}nota:{C.RESET} {note}\n"

        return s