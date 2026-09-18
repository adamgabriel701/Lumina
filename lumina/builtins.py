"""Fonte única de verdade para funções nativas (builtins).

Estas funções são reconhecidas pelo semantic e pelo codegen sem precisar
de declaração prévia. Consumido em:
  - lumina/semantic/analyzer.py  → valida chamadas
  - lumina/semantic/expressions.py / statements.py → tipo de retorno
  - lumina/codegen/codegen.py    → evita registrar externs duplicados
  - lumina/codegen/expressions/calls.py → branch de codegen
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
    # FILE* globals do libc
    "stdin",
    "stdout",
    "stderr",
    # I/O de stream
    "fgets",
    "fputs",
    "fflush",
    "getchar",
})


# Tipos de retorno dos builtins (linguagem Lumina).
#
# Fonte única de verdade — antes este dict estava duplicado em
# lumina/semantic/statements.py e lumina/semantic/expressions.py,
# o que causava divergência (`chr`/`atoi` foram adicionados só no
# codegen uma vez; `stdin`/`stdout`/`stderr` ficaram de fora do
# semantic por completo).
#
# Convenção:
#   - "void"  → sem valor útil (print, free, write_file)
#   - "int"   → i64
#   - "float" → f64
#   - "str"   → i8* (strings e FILE*)
#   - "ptr"   → i8* (buffers genéricos)
BUILTIN_RET = {
    "print": "void",
    "input": "str",
    "atoi": "int",
    "len": "int",
    "alloc": "ptr",
    "alloc_bytes": "ptr",
    "free": "void",
    "read_file": "str",
    "write_file": "void",
    "int": "int",
    "float": "float",
    "str": "str",
    "argv": "str",
    "chr": "str",
    "http_response": "str",
    # FILE* globals do libc — devolvem FILE* (tratamos como str)
    "stdin": "str",
    "stdout": "str",
    "stderr": "str",
    # I/O de stream do libc
    "fgets": "str",
    "fputs": "int",
    "fflush": "int",
    "getchar": "int",
}