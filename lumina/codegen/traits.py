"""Resolução de métodos default de traits e validação de macros."""
from ..ast import Function as AstFunction, Param
from ..errors import LuminaError


class TraitsMixin:

    # ==================================================================
    # Trait defaults
    # ==================================================================
    def _resolve_trait_defaults(self, ast):
        """Copia métodos default do trait para o ImplBlock que não os sobrescreve.

        Roda ANTES de registrar funções, tanto no semantic quanto no codegen,
        pra que `Struct_metodo` exista nos dois lados.
        """
        traits_by_name = {}
        for decl in ast:
            if hasattr(decl, 'methods') and not hasattr(decl, 'struct_name'):
                traits_by_name[decl.name] = decl

        for decl in ast:
            if not (hasattr(decl, 'methods') and hasattr(decl, 'struct_name')):
                continue
            trait_name = getattr(decl, 'trait_name', None)
            if not trait_name or trait_name not in traits_by_name:
                continue

            trait_def = traits_by_name[trait_name]
            explicit_names = {m.name for m in decl.methods}

            for trait_method in trait_def.methods:
                full_name = f"{decl.struct_name}_{trait_method.name}"
                if full_name in explicit_names:
                    continue
                if not trait_method.body:
                    continue

                default_method = AstFunction(
                    full_name,
                    [Param('self', decl.struct_name)] + list(trait_method.params),
                    trait_method.return_type,
                    list(trait_method.body),
                )
                decl.methods.append(default_method)

    # ==================================================================
    # Validação de macros
    # ==================================================================
    def _validate_macro(self, fn):
        """Macro deve ter corpo `return <expr>` (1 statement)."""
        body = fn.body or []
        if len(body) != 1 or type(body[0]).__name__ != 'ReturnStmt':
            raise LuminaError(
                f"Macro '{fn.name}' deve ter corpo `return <expr>` "
                f"(um único statement). Macros multi-statement não são "
                f"suportadas.",
                filename="<macro>",
                line=getattr(fn, 'line', 0) or 0,
                col=getattr(fn, 'col', 0) or 0,
                source_code="",
            )
        if not body[0].values:
            raise LuminaError(
                f"Macro '{fn.name}' deve retornar uma expressão "
                f"(`return <expr>`).",
                filename="<macro>",
                line=getattr(fn, 'line', 0) or 0,
                col=getattr(fn, 'col', 0) or 0,
                source_code="",
            )
