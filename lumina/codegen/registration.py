"""Registro de structs, enums e funções no módulo LLVM.

Também contém a aplicação de atributos LLVM (`@inline`, `@cold`, ...)
e o helper `_llvm_ty_to_str` usado por outros mixins.
"""
from llvmlite import ir
from ..common.mangle import mangle_type


class RegistrationMixin:

    # ==================================================================
    # Registro de structs/enums/funções
    # ==================================================================
    def register_struct(self, node):
        if node.name in self.struct_types:
            return
        struct_ty = self.module.context.get_identified_type(node.name)
        self.struct_types[node.name] = struct_ty
        self.struct_defs[node.name] = node

        field_tys = []
        for ft in node.fields.values():
            if ft in self.struct_types:
                field_tys.append(self.struct_types[ft].as_pointer())
            else:
                field_tys.append(self.get_llvm_type(ft))

        struct_ty.set_body(*field_tys)
        self.struct_fields[node.name] = {
            name: i for i, name in enumerate(node.fields.keys())
        }

    def _enum_max_payloads(self, node):
        """Descobre o número máximo de payloads entre as variantes de um enum."""
        max_p = 0
        for variant in node.variants:
            if len(variant) < 2:
                continue
            v_payloads = variant[1]
            if isinstance(v_payloads, list):
                max_p = max(max_p, len(v_payloads))
            elif v_payloads is not None:
                max_p = max(max_p, 1)
        return max_p

    def register_enum(self, node):
        if node.name in self.struct_types:
            return

        # Enums genéricos não são registrados direto — monomorphizados
        # on-demand por `get_or_create_monomorphized_enum`.
        if getattr(node, 'type_params', None):
            self.struct_defs[node.name] = node
            return

        struct_ty = self.module.context.get_identified_type(node.name)
        self.struct_types[node.name] = struct_ty
        self.struct_defs[node.name] = node

        max_p = self._enum_max_payloads(node)
        fields = [ir.IntType(32)] + [ir.IntType(64)] * max_p
        struct_ty.set_body(*fields)

        fields_map = {"tag": 0}
        for i in range(max_p):
            fields_map[f"payload_{i}"] = i + 1
        if max_p >= 1:
            fields_map["payload"] = 1
        self.struct_fields[node.name] = fields_map

    def register_function(self, node):
        if getattr(node, 'type_params', None):
            self.function_defs[node.name] = node
            return

        func_name = (
            getattr(node, 'module_prefix', '') + node.name
            if hasattr(node, 'module_prefix') else node.name
        )

        if func_name in self.functions_table:
            return

        ret_ty = self.get_llvm_param_type(node.return_type)
        param_types = []
        for p in node.params:
            p_name, p_type, p_default = p.name, p.type_ann, p.default
            p_ty = self.get_llvm_param_type(p_type)
            param_types.append(p_ty)

        func_type = ir.FunctionType(ret_ty, param_types)
        func = ir.Function(self.module, func_type, name=func_name)
        self.functions_table[func_name] = (func, func_type)
        self.functions_table[node.name] = (func, func_type)
        self.function_defs[node.name] = node

        # Sprint 10: aplica atributos LLVM por função
        attrs = getattr(node, 'attrs', None) or []
        self._apply_llvm_attrs(func, attrs)

    def _apply_llvm_attrs(self, func, attrs):
        """Aplica atributos LLVM a uma função (`@inline`, `@noinline`,
        `@cold`, `@hot`).

        Attrs devem ser uma lista de strings (Sprint 9a — `parse_function`
        passa strings, não tuples). Aceita também tuple por robustez.
        """
        # Normaliza: aceita ['inline'] ou [('inline', [])]
        names = set()
        for a in attrs:
            if isinstance(a, tuple):
                names.add(a[0])
            else:
                names.add(a)

        if 'inline' in names and 'noinline' in names:
            from ..errors import LuminaError
            raise LuminaError(
                f"Função '{func.name}' tem @inline e @noinline — conflitante.",
                filename="<codegen>",
                line=0, col=0, source_code="",
            )

        if 'inline' in names:
            func.attributes.add('alwaysinline')
        if 'noinline' in names:
            func.attributes.add('noinline')
        if 'cold' in names:
            func.attributes.add('cold')
        if 'hot' in names:
            # NOTA: o LLVM tem `hot` como STRING attribute, não enum.
            # O llvmlite não expõe API para string attributes em
            # `Function.attributes`. Mapeamos `@hot` para `inlinehint`
            # — mesma intenção semântica ("função quente, boa candidata
            # a inline"). Se o llvmlite ganhar suporte futuro, trocar
            # por string `"hot"`.
            func.attributes.add('inlinehint')

    def _llvm_ty_to_str(self, t):
        if t == self.i64_ty:
            return "int"
        if t == self.f64_ty:
            return "float"
        if t == self.voidptr_ty:
            return "str"
        if isinstance(t, ir.IntType) and t.width == 1:
            return "bool"
        if isinstance(t, ir.PointerType):
            return "ptr"
        return "unknown"
