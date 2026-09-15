"""Regras de compatibilidade de tipos do Lumina."""

PRIMITIVES = {"int", "float", "bool", "str", "ptr", "fn", "void"}


def _base(t: str) -> str:
    return t.split("<", 1)[0] if t else t


def _is_type_param(t: str) -> bool:
    return bool(t) and len(t) == 1 and t.isupper()


def is_assignable(target: str, value: str) -> bool:
    if target is None or value is None:
        return True
    if target == value:
        return True

    if _is_type_param(target):
        return True

    # Promoção numérica
    if target == "float" and value == "int":
        return True

    # int ↔ ptr
    if target == "ptr" and value in ("int", "ptr"):
        return True
    if target == "int" and value == "ptr":
        return True

    # NOVO: fn (function pointer) representa i8* no codegen.
    # É compatível com str/ptr e vice-versa.
    if target in ("str", "ptr", "fn") and value in ("str", "ptr", "fn"):
        return True

    # Arrays decaem para ponteiros
    if target == "ptr" and value == "array":
        return True
    if target == "array" and value == "ptr":
        return True

    # null é compatível com ponteiros, str, fn e structs
    if value in ("none", "None", "null"):
        return target in ("ptr", "fn", "str") or _base(target) not in PRIMITIVES

    # Generics
    if "<" in target or "<" in value:
        if _base(target) != _base(value):
            return False
        return target.replace(" ", "") == value.replace(" ", "")

    return False


def check_assignable(target: str, value: str, err_ctx) -> None:
    if is_assignable(target, value):
        return
    from ..errors import LuminaError
    filename, line, col, source = err_ctx
    raise LuminaError(
        f"Tipos incompatíveis: esperado '{target}', obteve '{value}'.",
        filename, line, col, source,
    )