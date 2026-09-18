"""Mangling canônico de tipos para nomes de símbolos.

Usado pelo parser (nome de métodos de impl), semantic (registro de
métodos) e codegen (nome de tipos LLVM identificados). Manter uma
única função garante que `impl Trait for Box<int>` registra
`Box_int__metodo` e que `codegen_method_call` acha.
"""


def mangle_type(type_name: str) -> str:
    """'Box<int>' → 'Box_int_'; 'Box<int,str>' → 'Box_int_str_'; 'int' → 'int'."""
    if not type_name or "<" not in type_name:
        return type_name
    return type_name.replace("<", "_").replace(">", "_").replace(",", "_").replace(" ", "")


def mangle_method(struct_name: str, method_name: str) -> str:
    """Nome completo de um método de impl: `Box<int>` + `greet` → `Box_int__greet`."""
    return f"{mangle_type(struct_name)}_{method_name}"
