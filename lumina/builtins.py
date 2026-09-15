"""Fonte única de verdade para funções nativas (builtins).

Estas funções são reconhecidas pelo semantic e pelo codegen sem precisar
de declaração prévia. A lista é consumida em:
  - lumina/semantic/analyzer.py  → valida chamadas
  - lumina/codegen/codegen.py    → evita confundir lambda com builtin

Usar frozenset para deixar claro que é imutável e evitar divergência
entre os dois consumidores.
"""

BUILTIN_FUNCTIONS = frozenset({
    "print",
    "input",
    "atoi",
    "len",
    "alloc",
    "alloc_bytes",
    "free",
    "read_file",
    "write_file",
    "int",
    "float",
    "str",
    "argv",
    "chr",
    "http_response",
})
