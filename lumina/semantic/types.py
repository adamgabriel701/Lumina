"""Regras de compatibilidade de tipos do Lumina.

Única fonte de verdade para `is_assignable`. Consumida por VarDecl,
AssignStmt, ReturnStmt e (futuramente) por validação de argumentos.
"""

PRIMITIVES = {"int", "float", "bool", "str", "ptr", "fn", "void"}


def _base(t: str) -> str:
    """Remove args de generic: 'Box<int>' -> 'Box'."""
    return t.split("<", 1)[0] if t else t


def _is_type_param(t: str) -> bool:
    """Um type param genérico é uma letra maiúscula sozinha (T, U, V, ...)."""
    return bool(t) and len(t) == 1 and t.isupper()


def is_assignable(target: str, value: str) -> bool:
    """True se um valor do tipo `value` pode ser atribuído a `target`.

    Regras:
      - Tipos iguais → True.
      - Type param (T, U, ...) → aceita qualquer coisa.
      - Option ↔ Option<X> (compatibilidade sem args).
      - int → float (promoção implícita).
      - int ↔ ptr (casts implícitos para ponteiros).
      - array → ptr (arrays decaem para ponteiros).
      - none/null → qualquer ptr, struct, fn, str, ou Option.
      - Box<int> → Box<int> (mesma base + mesmos args) → True.
      - Desconhecido (None) → True.
    """
    if target is None or value is None:
        return True
    if target == value:
        return True

    # Type param genérico aceita qualquer tipo concreto.
    if _is_type_param(target):
        return True

    # NOVO (A): Option (sem args) ↔ Option<X>
    if target.startswith("Option") and value == "Option":
        return True
    if value.startswith("Option") and target == "Option":
        return True

    # Promoção numérica
    if target == "float" and value == "int":
        return True

    # int ↔ ptr
    if target == "ptr" and value in ("int", "ptr"):
        return True
    if target == "int" and value == "ptr":
        return True

    # fn ↔ str ↔ ptr (todos são i8* no codegen)
    if target in ("str", "ptr", "fn") and value in ("str", "ptr", "fn"):
        return True

    # Arrays decaem para ponteiros
    if target == "ptr" and value == "array":
        return True
    if target == "array" and value == "ptr":
        return True

    # null é compatível com ponteiros, str, fn, structs e Option
    if value in ("none", "None", "null"):
        return (
            target in ("ptr", "fn", "str", "Option")
            or target.startswith("Option")
            or _base(target) not in PRIMITIVES
        )

    # Generics: mesma base + mesmos args (ou um lado sem args)
    if "<" in target or "<" in value:
        if _base(target) != _base(value):
            return False
        if target == _base(target) or value == _base(value):
            return True
        return target.replace(" ", "") == value.replace(" ", "")

    return False


def check_assignable(target: str, value: str, err_ctx) -> None:
    """Levanta LuminaError se não for atribuível.

    `err_ctx` é uma tupla (filename, line, col, source_code).
    """
    if is_assignable(target, value):
        return
    from ..errors import LuminaError
    filename, line, col, source = err_ctx
    raise LuminaError(
        f"Tipos incompatíveis: esperado '{target}', obteve '{value}'.",
        filename, line, col, source,
    )