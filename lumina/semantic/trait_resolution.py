"""Resolução de métodos default de traits.

Roda ANTES da análise de corpos, copiando métodos default do TraitDecl
para dentro de cada ImplBlock que não os sobrescreve — para que
`Struct_metodo` exista tanto no semantic quanto no codegen.
"""
from ..ast import Function, Param, ImplBlock, TraitDecl


class TraitResolutionMixin:

    def _resolve_trait_defaults(self, declarations):
        traits_by_name = {}
        for decl in declarations:
            if isinstance(decl, TraitDecl):
                traits_by_name[decl.name] = decl

        # Passo 1: registra aliases `metodo` → `Struct_metodo`.
        for decl in declarations:
            if not isinstance(decl, ImplBlock):
                continue
            trait_name = getattr(decl, 'trait_name', None)
            if not trait_name or trait_name not in traits_by_name:
                continue
            trait_def = traits_by_name[trait_name]
            for trait_method in trait_def.methods:
                full_name = f"{decl.struct_name}_{trait_method.name}"
                if full_name not in self.functions:
                    self.functions.add(full_name)
                self.functions.add(trait_method.name)
                # Function "fake" com params vazios. O `self` é
                # implícito no call site.
                if trait_method.name not in self.function_defs:
                    self.function_defs[trait_method.name] = Function(
                        trait_method.name,
                        [],
                        trait_method.return_type,
                        [],
                    )

        # Passo 2: copia métodos default para o ImplBlock que não os sobrescreve.
        for decl in declarations:
            if not isinstance(decl, ImplBlock):
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

                default_method = Function(
                    full_name,
                    [Param('self', decl.struct_name)] + list(trait_method.params),
                    trait_method.return_type,
                    list(trait_method.body),
                )
                decl.methods.append(default_method)
