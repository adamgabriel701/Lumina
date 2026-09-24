"""Method calls, construtor de enums e lookup de variante.

`codegen_method_call` resolve `obj.metodo(args)` procurando primeiro
`{Struct}_{metodo}` e caindo para `{Base}_{metodo}` quando a struct é
genérica monomorphizada (`Box_int_` → `Box`).

`_construct_enum` constrói uma instância de enum no heap.
`_find_enum_variant` procura o enum que contém uma variante.
"""
from llvmlite import ir

# PATCH: importa o mangler canônico (antes havia um `_mangle_name`
# duplicado dentro desta classe, idêntico a `mangle_type`).
from ...common.mangle import mangle_type
from ..constants import I64_BYTES, MIN_ENUM_SIZE   # ← NOVO


class MethodCallsMixin:

    def codegen_method_call(self, node, method_name):
        obj_node = node.args[0]
        obj_val = self.visit(obj_node)

        # `obj.campo_fn(args)` — o "método" é um campo fn-typed.
        # Carrega o valor do campo e faz indirect call via _call_closure.
        if (isinstance(obj_val.type, ir.PointerType)
                and isinstance(obj_val.type.pointee, ir.IdentifiedStructType)):
            struct_name = obj_val.type.pointee.name
            fields_map = self.struct_fields.get(struct_name, {})
            if method_name in fields_map:
                field_idx = fields_map[method_name]
                elem_ptr = self.builder.gep(
                    obj_val,
                    [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, field_idx)],
                    name=f"field_{method_name}_ptr",
                )
                field_ty = elem_ptr.type.pointee
                # Só trata como campo fn se for voidptr (fat pointer)
                if field_ty == self.voidptr_ty:
                    closure_val = self.builder.load(elem_ptr, name=f"field_{method_name}_load")

                    # Desempacota {fn_ptr, env_ptr} e chama
                    closure_i8pp = self.builder.bitcast(
                        closure_val, self.voidptr_ty.as_pointer(),
                        name=f"field_{method_name}_c8pp",
                    )
                    fn_raw = self.builder.load(closure_i8pp, name=f"field_{method_name}_fn")
                    env_slot = self.builder.gep(
                        closure_i8pp, [ir.Constant(self.i64_ty, 1)],
                        name=f"field_{method_name}_env_slot",
                    )
                    env_raw = self.builder.load(env_slot, name=f"field_{method_name}_env")

                    n = len(node.args) - 1  # excluindo obj
                    fn_ty = ir.FunctionType(
                        self.i64_ty, [self.voidptr_ty] + [self.i64_ty] * n,
                    )
                    fn_ptr = self.builder.bitcast(
                        fn_raw, fn_ty.as_pointer(),
                        name=f"field_{method_name}_cast",
                    )

                    call_args = [env_raw]
                    for arg_node in node.args[1:]:
                        a = self.visit(arg_node)
                        if a.type != self.i64_ty:
                            if isinstance(a.type, ir.IntType):
                                a = self.builder.sext(a, self.i64_ty, name="field_arg_sext")
                            elif a.type == self.f64_ty:
                                a = self.builder.fptosi(a, self.i64_ty, name="field_arg_fptosi")
                            elif isinstance(a.type, ir.PointerType):
                                a = self.builder.ptrtoint(a, self.i64_ty, name="field_arg_ptr")
                        call_args.append(a)

                    return self.builder.call(
                        fn_ptr, call_args, name=f"field_{method_name}_call",
                    )

        if isinstance(obj_val.type, ir.PointerType) and isinstance(
            obj_val.type.pointee, ir.IdentifiedStructType,
        ):
            struct_name = obj_val.type.pointee.name  # ex: "Box_int_"

            # Candidatos: nome exato primeiro, depois base.
            # Ex: `struct_name = "Box_int_"`, `method = "greet"`:
            #   candidates = ["Box_int__greet", "Box_greet"]
            candidates = [f"{struct_name}_{method_name}"]
            base = struct_name
            if "_" in base:
                base = base.split("_")[0]
            if base != struct_name:
                candidates.append(f"{base}_{method_name}")

            real_method_name = None
            used_base = False
            for c in candidates:
                if c in self.functions_table:
                    real_method_name = c
                    used_base = (c == f"{base}_{method_name}")
                    break

            if real_method_name is not None:
                func, func_type = self.functions_table[real_method_name]
                # Se caímos no método do base, `self` do método é `Box*` mas
                # `obj_val` é `Box_int_*`. Bitcast.
                if used_base and len(func_type.args) >= 1:
                    expected_self = func_type.args[0]
                    if obj_val.type != expected_self:
                        obj_val = self.builder.bitcast(
                            obj_val, expected_self, name="self_base_cast",
                        )
                args = [obj_val]
                for arg_node in node.args[1:]:
                    args.append(self.visit(arg_node))
                return self.builder.call(func, args, name=real_method_name + "_call")

        if obj_val.type == self.voidptr_ty:
            if method_name == "len":
                return self.builder.call(self.strlen, [obj_val], name="str_len")
            elif method_name == "contains":
                target_str = self.visit(node.args[1])
                res_ptr = self.builder.call(
                    self.strstr, [obj_val, target_str], name="str_strstr",
                )
                zero_ptr = ir.Constant(self.voidptr_ty, None)
                return self.builder.icmp_signed(
                    "!=", res_ptr, zero_ptr, name="str_contains_res",
                )
            elif method_name == "starts_with":
                target_str = self.visit(node.args[1])
                len_target = self.builder.call(
                    self.strlen, [target_str], name="starts_len",
                )
                cmp_res = self.builder.call(
                    self.strncmp, [obj_val, target_str, len_target], name="starts_cmp",
                )
                zero = ir.Constant(ir.IntType(32), 0)
                return self.builder.icmp_signed(
                    "==", cmp_res, zero, name="starts_res",
                )
            elif method_name in ("upper", "lower"):
                len_val = self.builder.call(self.strlen, [obj_val], name="case_len")
                total_len = self.builder.add(
                    len_val, ir.Constant(self.i64_ty, 1), name="case_total",
                )
                buf = self.builder.call(self.malloc, [total_len], name="case_buf")

                loop_bb = self.builder.append_basic_block(name="case_loop")
                end_bb = self.builder.append_basic_block(name="case_end")

                pred_bb = self.builder.block
                self.builder.branch(loop_bb)
                self.builder.position_at_end(loop_bb)

                i = self.builder.phi(self.i64_ty, name="case_i")
                i.add_incoming(ir.Constant(self.i64_ty, 0), pred_bb)

                char_ptr = self.builder.gep(buf, [i], name="case_char_ptr")
                char_val = self.builder.load(char_ptr, name="case_char")

                if method_name == "upper":
                    offset = ir.Constant(ir.IntType(8), ord('A') - ord('a'))
                else:
                    offset = ir.Constant(ir.IntType(8), ord('a') - ord('A'))

                lower_a = ir.Constant(ir.IntType(8), ord('a'))
                lower_z = ir.Constant(ir.IntType(8), ord('z'))

                is_lower = self.builder.icmp_signed(
                    ">=", char_val, lower_a, name="is_ge_a",
                )
                is_upper = self.builder.icmp_signed(
                    "<=", char_val, lower_z, name="is_le_z",
                )
                is_alpha = self.builder.and_(is_lower, is_upper, name="is_alpha")

                new_char = self.builder.add(char_val, offset, name="new_char")
                final_char = self.builder.select(
                    is_alpha, new_char, char_val, name="final_char",
                )
                self.builder.store(final_char, char_ptr)

                next_i = self.builder.add(
                    i, ir.Constant(self.i64_ty, 1), name="case_next",
                )
                i.add_incoming(next_i, self.builder.block)

                cond = self.builder.icmp_signed(
                    "<", next_i, len_val, name="case_cond",
                )
                self.builder.cbranch(cond, loop_bb, end_bb)

                self.builder.position_at_end(end_bb)
                null_ptr = self.builder.gep(buf, [len_val], name="case_null_ptr")
                self.builder.store(ir.Constant(self.i8_ty, 0), null_ptr)
                return buf

        raise Exception(f"Método '{method_name}' não encontrado no Codegen.")

    def _find_enum_variant(self, variant_name):
        """Retorna `(enum_base_name, variant_idx)` para a variante, ou None.

        PATCH: adiciona cache e normaliza para o nome **base**.

        Antes, a função varria `self.struct_defs.items()` a cada chamada.
        Como `get_or_create_monomorphized_enum` registra a mesma `base_decl`
        sob 2 chaves extras (`Box<int>`, `Box_int_`), a iteração era:
          - O(n_enums + n_monomorphizações) em vez de O(n_enums)
          - Não-determinística quanto ao nome retornado. Se a chave
            `"Custom<int>"` fosse encontrada antes de `"Custom"`, o
            chamador (`codegen_user_call`) construía
            `f"{enum_name}<{args}>"` = `"Custom<int><str>"` → quebra.

        A iteração agora filtra `enum_name == enum_def.name`, garantindo
        que só a **base** entra no cache. As especializações são derivadas
        pelo chamador via `_infer_enum_type_args`.

        Cache é populado na primeira chamada e nunca invalidado — todos
        os enums são registrados em `generate_module` (passo 1) antes de
        qualquer lookup acontecer em corpos de função (passo 3b).
        """
        cache = getattr(self, '_variant_cache', None)
        if cache is None:
            cache = {}
            for enum_name, enum_def in self.struct_defs.items():
                if not hasattr(enum_def, 'variants'):
                    continue
                # Só a chave canônica base: `enum_def.name` é o nome
                # declarado (`"Box"`), não as especializações
                # (`"Box<int>"`, `"Box_int_"`).
                if enum_name != enum_def.name:
                    continue
                for i, variant in enumerate(enum_def.variants):
                    cache[variant[0]] = (enum_name, i)
            self._variant_cache = cache
        return cache.get(variant_name)

    def _construct_enum(self, enum_name, variant_idx, arg_nodes):
        # Monomorphiza on-demand se for genérico.
        if "<" in enum_name and enum_name not in self.struct_types:
            self.get_or_create_monomorphized_enum(enum_name)

        struct_ty = self.struct_types[enum_name]
        struct_def = self.struct_defs[enum_name]
        max_p = self._enum_max_payloads(struct_def)

        # Tipos concretos dos slots (elements[0] é o tag).
        payload_tys = list(struct_ty.elements[1:]) if struct_ty.elements else []

        struct_size = I64_BYTES + max_p * I64_BYTES
        if struct_size < MIN_ENUM_SIZE:
            struct_size = MIN_ENUM_SIZE

        # PATCH: usa o mangler canônico. Antes chamava `self._mangle_name`,
        # que era uma cópia local de `mangle_type`.
        mangled = mangle_type(enum_name)

        enum_ptr = self.builder.call(
            self.malloc, [ir.Constant(self.i64_ty, struct_size)],
            name=f"{mangled}_lit",
        )
        enum_ptr = self.builder.bitcast(
            enum_ptr, struct_ty.as_pointer(),
            name=f"{mangled}_cast",
        )

        tag_ptr = self.builder.gep(
            enum_ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)],
            name="tag_ptr",
        )
        self.builder.store(ir.Constant(self.i32_ty, variant_idx), tag_ptr)

        for i in range(max_p):
            payload_ptr = self.builder.gep(
                enum_ptr,
                [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i + 1)],
                name=f"payload_ptr_{i}",
            )
            target_ty = payload_tys[i] if i < len(payload_tys) else self.i64_ty
            if i < len(arg_nodes):
                val = self.visit(arg_nodes[i])
                val = self._coerce_for_store(val, target_ty, name_hint=f"payload_{i}")
                self.builder.store(val, payload_ptr)
            else:
                self.builder.store(self._zero_for_type(target_ty), payload_ptr)

        return enum_ptr