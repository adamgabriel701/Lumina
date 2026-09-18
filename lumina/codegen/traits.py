"""Resolução de métodos default de traits e validação de macros."""
from ..ast import Function as AstFunction, Param
from ..errors import LuminaError
from ..common.mangle import mangle_method


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
                full_name = mangle_method(decl.struct_name, trait_method.name)
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
        """Validação mínima de uma macro declarada.

        Uma macro pode ter corpo:
          - `return <expr>`             → usável como expressão (`nome(args)`)
          - múltiplos statements        → usável só em statement (`nome!(args)`)

        Como a mesma macro pode ser usada de duas formas, NÃO validamos
        `return <expr>` aqui — quem decide é o call site:
          - `_expand_macro_expr` exige `return <expr>` quando chamada como
            expressão.
          - `_expand_macro_stmt` aceita qualquer corpo.

        Aqui só garantimos que o corpo não está vazio.
        """
        body = fn.body or []
        if len(body) == 0:
            raise LuminaError(
                f"Macro '{fn.name}' tem corpo vazio.",
                filename="<macro>",
                line=getattr(fn, 'line', 0) or 0,
                col=getattr(fn, 'col', 0) or 0,
                source_code="",
            )
        