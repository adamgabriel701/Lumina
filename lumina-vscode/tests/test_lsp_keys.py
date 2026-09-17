"""Testes da qualificação de nomes no LSP.

O hover deve reportar o tipo correto de variáveis locais homônimas
em funções diferentes. Antes do fix, o segundo `i` (em outra função)
herdava o tipo do primeiro `i`.

Estes testes importam `validate_and_extract_symbols` diretamente,
sem passar pelo protocolo JSON-RPC.
"""
import os
import pathlib
import sys

import pytest

# Torna `lumina_lsp` importável
LSP_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LSP_DIR))

from lumina_lsp import (  # noqa: E402
    validate_and_extract_symbols, SK_VARIABLE,
)


def test_locals_use_qualified_keys():
    src = (
        'fn a() -> int:\n'
        '    let i = 10\n'
        '    return i\n'
        '\n'
        'fn b() -> int:\n'
        '    let i = 3.14\n'
        '    return 0\n'
        '\n'
        'fn main() -> int:\n'
        '    return 0\n'
    )
    (_, _, defs, details, _, _, _, scope) = validate_and_extract_symbols(src)

    # Ambos `i` devem existir como chaves qualificadas
    assert "a::i" in details, f"a::i ausente. details={list(details.keys())}"
    assert "b::i" in details, f"b::i ausente. details={list(details.keys())}"

    # E com tipos corretos
    assert details["a::i"]["detail"] == "i: int"
    assert details["b::i"]["detail"] == "i: float"

    # Unqualified `i` NÃO deve existir (evita ambiguidade)
    assert "i" not in details, "chave simples 'i' deveria ser qualificada"


def test_scope_map_built():
    src = (
        'fn foo() -> int:\n'
        '    let x = 1\n'
        '    return x\n'
        '\n'
        'fn bar() -> int:\n'
        '    return 0\n'
    )
    (_, _, _, _, _, _, _, scope) = validate_and_extract_symbols(src)
    names = [name for _, name in scope]
    assert "foo" in names
    assert "bar" in names


def test_scope_map_used_for_hover_lookup():
    """Simula o lookup `_lookup` sem instanciar LuminaLSP.

    IMPORTANTE: a fonte precisa ser semanticamente válida, senão o
    `validate_and_extract_symbols` pára no LuminaError e não roda a
    passada que atualiza `detail` com o tipo inferido.
    """
    src = (
        'fn a() -> int:\n'
        '    let i = 10\n'
        '    return i\n'
        '\n'
        'fn b() -> float:\n'         # ← era `int`, mas `let i = 3.14` retorna float
        '    let i = 3.14\n'
        '    return i\n'
    )
    (_, _, _, details, _, _, _, scope) = validate_and_extract_symbols(src)

    def _enclosing_func(line):
        target = line + 1
        best = None
        for start, name in scope:
            if start <= target:
                best = name
            else:
                break
        return best

    def _lookup(word, line):
        func = _enclosing_func(line)
        if func:
            q = f"{func}::{word}"
            if q in details:
                return details[q]
        return details.get(word)

    # Linha 1 (0-based): `let i = 10` em a
    info_a = _lookup("i", 1)
    assert info_a is not None
    assert info_a["detail"] == "i: int"

    # Linha 5 (0-based): `let i = 3.14` em b
    info_b = _lookup("i", 5)
    assert info_b is not None
    assert info_b["detail"] == "i: float"


def test_top_level_symbols_unqualified():
    src = (
        'struct P:\n'
        '    x: int\n'
        '\n'
        'fn main() -> int:\n'
        '    return 0\n'
    )
    (_, _, _, details, _, _, _, _) = validate_and_extract_symbols(src)
    assert "P" in details
    assert "main" in details
    # Nenhuma chave qualificada para top-level
    assert not any("::" in k for k in details), (
        f"top-level não deve ter chaves qualificadas: {list(details.keys())}"
    )


def test_method_locals_qualified_by_method_name():
    """Métodos de impl usam nome mangled (`Struct_metodo`).

    O parser faz `func.name = f"{struct_name}_{original_name}"` em
    `parse_impl`. O LSP herda esse nome — é consistente com o resto
    do compilador (o codegen procura `S_inc`, não `inc`).
    """
    src = (
        'struct S:\n'
        '    n: int\n'
        '\n'
        'impl S:\n'
        '    fn inc() -> int:\n'
        '        let step = 1\n'
        '        return step\n'
    )
    (_, _, _, details, _, _, _, scope) = validate_and_extract_symbols(src)
    # Método mangled
    assert "S_inc" in details
    # Local qualificado pelo nome mangled
    assert "S_inc::step" in details
    assert details["S_inc::step"]["detail"] == "step: int"

def test_locals_type_inferred_after_semantic():
    """O tipo de `let i = 10` deve virar `int` após o semantic rodar,
    mesmo que o VarDecl tenha começado sem tipo explícito."""
    src = (
        'fn f() -> int:\n'
        '    let n = 42\n'
        '    let f = 3.14\n'
        '    let s = "oi"\n'
        '    let b = true\n'
        '    return n\n'
    )
    (_, _, _, details, _, _, _, _) = validate_and_extract_symbols(src)

    assert "f::n" in details
    assert details["f::n"]["detail"] == "n: int"
    assert details["f::f"]["detail"] == "f: float"
    assert details["f::s"]["detail"] == "s: str"
    assert details["f::b"]["detail"] == "b: bool"