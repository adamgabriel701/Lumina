"""Resolução de imports e parsing do módulo principal."""
import os
from collections import deque

from lumina.ast import ImportStmt
from lumina.errors import LuminaError
from lumina.lexer import Lexer
from lumina.parser import Parser

from ..utils import Color, paint, arrow, STD_DIR


def parse_module(filename):
    """Parseia o módulo e resolve todos os imports de forma iterativa."""
    abs_path = os.path.abspath(filename)
    queue = deque([abs_path])
    visited = set()
    resolved_ast = []

    prelude_path = os.path.join(STD_DIR, "prelude.lm")
    if os.path.exists(prelude_path):
        queue.appendleft(prelude_path)

    while queue:
        current_file = queue.popleft()
        if current_file in visited:
            continue
        visited.add(current_file)

        try:
            with open(current_file, "r") as f:
                code = f.read()
        except Exception:
            continue

        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens, current_file, code)
        ast = parser.parse()

        for node in ast:
            if isinstance(node, ImportStmt):
                if node.filename.startswith("std/"):
                    clean_name = node.filename.replace("std/", "")
                    if clean_name.endswith(".lm"):
                        clean_name = clean_name[:-3]
                    dep_path = os.path.join(STD_DIR, clean_name + ".lm")
                elif os.path.exists(node.filename if node.filename.endswith(".lm")
                                    else node.filename + ".lm"):
                    dep_path = (node.filename if node.filename.endswith(".lm")
                                else node.filename + ".lm")
                else:
                    mod_path = os.path.join("lumina_modules", node.filename)
                    if not mod_path.endswith(".lm"):
                        mod_path += ".lm"
                    if not os.path.exists(mod_path):
                        raise LuminaError(
                            f"Módulo '{node.filename}' não encontrado.",
                            current_file, 0, 0, code,
                        )
                    dep_path = mod_path

                arrow(f"--> Importando módulo: {paint(node.filename, Color.BOLD)}")
                queue.append(os.path.abspath(dep_path))
            else:
                resolved_ast.append(node)

    return resolved_ast
