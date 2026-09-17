from llvmlite import ir
from ...ast import VariableExpr, MemberExpr


class CallsMixin:

    def visit_CallExpr(self, node):
        func_name = None
        if isinstance(node.callee, MemberExpr):
            func_name = node.callee.member
        elif isinstance(node.callee, VariableExpr):
            func_name = node.callee.name

        if node.is_method:
            return self.codegen_method_call(node, func_name)
        else:
            return self.codegen_user_call(node, func_name)

    def _coerce_arg(self, arg_val, expected_ty, suffix=""):
        """Coage um arg para o tipo esperado. Usado em chamadas normais
        e no preenchimento de defaults.
        """
        if arg_val.type == expected_ty:
            return arg_val
        if isinstance(expected_ty, ir.PointerType) and isinstance(arg_val.type, ir.PointerType):
            return self.builder.bitcast(arg_val, expected_ty, name=f"arg_ptr_cast{suffix}")
        if expected_ty == self.i64_ty and isinstance(arg_val.type, ir.PointerType):
            return self.builder.ptrtoint(arg_val, self.i64_ty, name=f"arg_ptr_to_int{suffix}")
        if isinstance(expected_ty, ir.PointerType) and arg_val.type == self.i64_ty:
            return self.builder.inttoptr(arg_val, expected_ty, name=f"arg_int_to_ptr{suffix}")
        if expected_ty == self.f64_ty and arg_val.type == self.i64_ty:
            return self.builder.sitofp(arg_val, self.f64_ty, name=f"arg_int_to_float{suffix}")
        if expected_ty == self.i64_ty and arg_val.type == self.f64_ty:
            return self.builder.fptosi(arg_val, self.i64_ty, name=f"arg_float_to_int{suffix}")
        if isinstance(expected_ty, ir.IntType) and isinstance(arg_val.type, ir.IntType):
            if arg_val.type.width < expected_ty.width:
                if arg_val.type.width == 1:
                    return self.builder.zext(arg_val, expected_ty, name=f"arg_zext{suffix}")
                return self.builder.sext(arg_val, expected_ty, name=f"arg_sext{suffix}")
            return self.builder.trunc(arg_val, expected_ty, name=f"arg_trunc{suffix}")
        return arg_val

    def _zero_for_type(self, ty):
        """Retorna um zero constante do tipo LLVM."""
        if isinstance(ty, ir.PointerType):
            return ir.Constant(ty, None)
        if isinstance(ty, ir.DoubleType):
            return ir.Constant(ty, 0.0)
        if isinstance(ty, ir.IntType):
            return ir.Constant(ty, 0)
        return ir.Constant(ty, 0)

    def codegen_user_call(self, node, func_name):
        # 0. Macro (@macro) → expande AST no call site
        if func_name in getattr(self, 'macros', {}):
            macro_fn = self.macros[func_name]
            expanded = self._expand_macro_expr(macro_fn, node.args)
            return self.visit(expanded)

        # 1. Chamada indireta via variável local (function pointer / lambda)
        if (func_name not in self.functions_table
                and func_name not in self.builtin_functions
                and func_name in self.symbol_table):
            fn_slot = self.symbol_table[func_name]
            fn_ptr_raw = self.builder.load(fn_slot, name=f"{func_name}_load")

            fn_ty = ir.FunctionType(self.i64_ty, [self.i64_ty])
            if fn_ptr_raw.type != fn_ty.as_pointer():
                if fn_ptr_raw.type == self.voidptr_ty:
                    fn_ptr = self.builder.bitcast(fn_ptr_raw, fn_ty.as_pointer(), name=f"{func_name}_cast")
                else:
                    fn_int = self.builder.ptrtoint(fn_ptr_raw, self.i64_ty, name=f"{func_name}_int")
                    fn_ptr = self.builder.inttoptr(fn_int, fn_ty.as_pointer(), name=f"{func_name}_cast")
            else:
                fn_ptr = fn_ptr_raw

            call_args = []
            for arg_node in node.args:
                a = self.visit(arg_node)
                if a.type != self.i64_ty:
                    if isinstance(a.type, ir.IntType):
                        a = self.builder.sext(a, self.i64_ty, name="ind_arg_sext")
                    elif a.type == self.f64_ty:
                        a = self.builder.fptosi(a, self.i64_ty, name="ind_arg_fptosi")
                    elif isinstance(a.type, ir.PointerType):
                        a = self.builder.ptrtoint(a, self.i64_ty, name="ind_arg_ptr")
                call_args.append(a)

            return self.builder.call(fn_ptr, call_args, name=f"{func_name}_indirect")

        # 2. Chamada a função genérica → materializa cópia especializada
        gen_def = self.function_defs.get(func_name)
        if gen_def is not None and getattr(gen_def, 'type_params', None):
            type_map = self._infer_type_map_lumina(gen_def, node)

            if type_map:
                mangled = self.materialize_generic(gen_def, type_map)
                arg_vals = None
            else:
                arg_vals = [self.visit(a) for a in node.args]
                arg_types = [v.type for v in arg_vals]
                legacy_map = {}
                for p, t in zip(gen_def.params, arg_types):
                    if p.type_ann in (gen_def.type_params or []):
                        legacy_map[p.type_ann] = self._llvm_ty_to_str(t)
                mangled = self.materialize_generic(gen_def, legacy_map)

            func, func_type = self.functions_table[mangled]

            if arg_vals is None:
                arg_vals = [self.visit(a) for a in node.args]

            final_args = []
            for i, a in enumerate(arg_vals):
                expected = func_type.args[i] if i < len(func_type.args) else None
                if expected is not None and a.type != expected:
                    if isinstance(expected, ir.IntType) and isinstance(a.type, ir.IntType):
                        if a.type.width < expected.width:
                            a = self.builder.sext(a, expected, name="gen_arg_sext")
                        else:
                            a = self.builder.trunc(a, expected, name="gen_arg_trunc")
                    elif expected == self.f64_ty and a.type == self.i64_ty:
                        a = self.builder.sitofp(a, self.f64_ty, name="gen_arg_itof")
                    elif expected == self.i64_ty and a.type == self.f64_ty:
                        a = self.builder.fptosi(a, self.i64_ty, name="gen_arg_ftoi")
                    elif isinstance(expected, ir.PointerType) and a.type == self.i64_ty:
                        a = self.builder.inttoptr(a, expected, name="gen_arg_itop")
                    elif expected == self.i64_ty and isinstance(a.type, ir.PointerType):
                        a = self.builder.ptrtoint(a, self.i64_ty, name="gen_arg_ptoi")
                    elif isinstance(expected, ir.PointerType) and isinstance(a.type, ir.PointerType):
                        a = self.builder.bitcast(a, expected, name="gen_arg_bitcast")
                final_args.append(a)

            return self.builder.call(func, final_args, name=mangled + "_call")

        # 3. Builtins
        if func_name == "print":
            for i, arg_node in enumerate(node.args):
                val = self.visit(arg_node)
                if i > 0:
                    self.builder.call(self.printf, [self.create_global_string(" ")], name="print_sep")
                if val.type == self.i64_ty:
                    self.builder.call(self.printf, [self.create_global_string("%ld"), val], name="print_call")
                elif val.type == self.f64_ty:
                    self.builder.call(self.printf, [self.create_global_string("%f"), val], name="print_call")
                elif val.type == self.i32_ty:
                    self.builder.call(self.printf, [self.create_global_string("%d"), val], name="print_call")
                elif isinstance(val.type, ir.IntType) and val.type.width == 1:
                    true_str = self.create_global_string("true")
                    false_str = self.create_global_string("false")
                    val = self.builder.select(val, true_str, false_str, name="print_bool")
                    self.builder.call(self.printf, [self.create_global_string("%s"), val], name="print_call")
                elif isinstance(val.type, ir.IntType) and val.type.width < 64:
                    val = self.builder.zext(val, self.i64_ty, name="print_zext")
                    self.builder.call(self.printf, [self.create_global_string("%ld"), val], name="print_call")
                else:
                    if isinstance(val.type, ir.PointerType) and val.type != self.voidptr_ty:
                        val = self.builder.bitcast(val, self.voidptr_ty, name="print_cast")
                    self.builder.call(self.printf, [self.create_global_string("%s"), val], name="print_call")
            self.builder.call(self.printf, [self.create_global_string("\n")], name="print_nl")
            return ir.Constant(self.i64_ty, 0)

        if func_name == "len":
            arg = self.visit(node.args[0])
            if arg.type == self.voidptr_ty or (isinstance(arg.type, ir.PointerType) and arg.type.pointee == self.i8_ty):
                return self.builder.call(self.strlen, [arg], name="len_str")
            return ir.Constant(self.i64_ty, 0)

        if func_name == "alloc":
            n = self.visit(node.args[0])
            if n.type != self.i64_ty:
                n = self.builder.sext(n, self.i64_ty, name="alloc_sext")
            size = self.builder.mul(n, ir.Constant(self.i64_ty, 8), name="alloc_size")
            return self.builder.call(self.malloc, [size], name="alloc_call")

        if func_name == "alloc_bytes":
            n = self.visit(node.args[0])
            if n.type != self.i64_ty:
                n = self.builder.sext(n, self.i64_ty, name="alloc_bytes_sext")
            return self.builder.call(self.malloc, [n], name="alloc_bytes_call")

        if func_name == "free":
            ptr = self.visit(node.args[0])
            if not isinstance(ptr.type, ir.PointerType):
                ptr = self.builder.inttoptr(ptr, self.voidptr_ty, name="free_cast")
            elif ptr.type != self.voidptr_ty:
                ptr = self.builder.bitcast(ptr, self.voidptr_ty, name="free_bitcast")
            self.builder.call(self.free, [ptr], name="free_call")
            return ir.Constant(self.i64_ty, 0)

        if func_name == "chr":
            c = self.visit(node.args[0])
            if c.type != self.i64_ty:
                c = self.builder.sext(c, self.i64_ty, name="chr_sext")
            c_i8 = self.builder.trunc(c, self.i8_ty, name="chr_trunc")
            buf = self.builder.call(
                self.malloc,
                [ir.Constant(self.i64_ty, 2)],
                name="chr_buf",
            )
            buf_i8 = self.builder.bitcast(buf, self.i8_ty.as_pointer(), name="chr_i8_ptr")
            self.builder.store(c_i8, buf_i8)
            null_ptr = self.builder.gep(
                buf_i8, [ir.Constant(self.i64_ty, 1)],
                name="chr_null_ptr",
            )
            self.builder.store(ir.Constant(self.i8_ty, 0), null_ptr)
            return buf_i8

        if func_name == "atoi":
            s = self.visit(node.args[0])
            if not isinstance(s.type, ir.PointerType):
                s = self.builder.inttoptr(s, self.voidptr_ty, name="atoi_cast")
            return self.builder.call(self.atoi, [s], name="atoi_call")

        if func_name == "int":
            v = self.visit(node.args[0])
            if v.type == self.voidptr_ty:
                return self.builder.call(self.atoi, [v], name="int_from_str")
            return v

        if func_name == "float":
            v = self.visit(node.args[0])
            if v.type == self.i64_ty:
                return self.builder.sitofp(v, self.f64_ty, name="float_from_int")
            return v

        if func_name == "str":
            v = self.visit(node.args[0])
            if v.type == self.voidptr_ty:
                return v
            if v.type == self.f64_ty:
                fmt = self.create_global_string("%f")
            elif v.type == self.i64_ty:
                fmt = self.create_global_string("%ld")
            else:
                return v
            buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 32), name="str_buf")
            buf_ptr = self.builder.bitcast(buf, self.voidptr_ty, name="str_buf_ptr")
            self.builder.call(
                self.snprintf,
                [buf_ptr, ir.Constant(self.i64_ty, 32), fmt, v],
                name="str_snprintf",
            )
            return buf_ptr

        if func_name == "write_file":
            path_val = self.visit(node.args[0])
            content_val = self.visit(node.args[1])
            if not isinstance(path_val.type, ir.PointerType):
                path_val = self.builder.inttoptr(path_val, self.i8_ty.as_pointer(), name="wf_path_cast")
            if not isinstance(content_val.type, ir.PointerType):
                content_val = self.builder.inttoptr(content_val, self.i8_ty.as_pointer(), name="wf_content_cast")

            fopen_ty = ir.FunctionType(self.voidptr_ty, [self.i8_ty.as_pointer(), self.i8_ty.as_pointer()])
            fopen = self.module.globals.get("fopen") or ir.Function(self.module, fopen_ty, name="fopen")

            fputs_ty = ir.FunctionType(self.i32_ty, [self.i8_ty.as_pointer(), self.voidptr_ty])
            fputs = self.module.globals.get("fputs") or ir.Function(self.module, fputs_ty, name="fputs")

            fclose_ty = ir.FunctionType(self.i32_ty, [self.voidptr_ty])
            fclose = self.module.globals.get("fclose") or ir.Function(self.module, fclose_ty, name="fclose")

            mode_w = self.create_global_string("w")
            fp = self.builder.call(fopen, [path_val, mode_w], name="wf_fopen")
            self.builder.call(fputs, [content_val, fp], name="wf_fputs")
            self.builder.call(fclose, [fp], name="wf_fclose")
            return ir.Constant(self.i64_ty, 0)

        if func_name == "read_file":
            path_val = self.visit(node.args[0])
            if not isinstance(path_val.type, ir.PointerType):
                path_val = self.builder.inttoptr(path_val, self.i8_ty.as_pointer(), name="rf_path_cast")

            fopen_ty = ir.FunctionType(self.voidptr_ty, [self.i8_ty.as_pointer(), self.i8_ty.as_pointer()])
            fopen = self.module.globals.get("fopen") or ir.Function(self.module, fopen_ty, name="fopen")

            fseek_ty = ir.FunctionType(self.i32_ty, [self.voidptr_ty, self.i64_ty, self.i32_ty])
            fseek = self.module.globals.get("fseek") or ir.Function(self.module, fseek_ty, name="fseek")

            ftell_ty = ir.FunctionType(self.i64_ty, [self.voidptr_ty])
            ftell = self.module.globals.get("ftell") or ir.Function(self.module, ftell_ty, name="ftell")

            fread_ty = ir.FunctionType(self.i64_ty, [self.i8_ty.as_pointer(), self.i64_ty, self.i64_ty, self.voidptr_ty])
            fread = self.module.globals.get("fread") or ir.Function(self.module, fread_ty, name="fread")

            fclose_ty = ir.FunctionType(self.i32_ty, [self.voidptr_ty])
            fclose = self.module.globals.get("fclose") or ir.Function(self.module, fclose_ty, name="fclose")

            mode_r = self.create_global_string("r")
            fp = self.builder.call(fopen, [path_val, mode_r], name="rf_fopen")

            # Null check: fopen retorna NULL se o arquivo não existe.
            fp_int = self.builder.ptrtoint(fp, self.i64_ty, name="rf_fp_int")
            is_null = self.builder.icmp_signed(
                "==", fp_int, ir.Constant(self.i64_ty, 0),
                name="rf_is_null",
            )

            null_bb = self.builder.append_basic_block(name="rf_null")
            ok_bb = self.builder.append_basic_block(name="rf_ok")
            end_bb = self.builder.append_basic_block(name="rf_end")

            self.builder.cbranch(is_null, null_bb, ok_bb)

            # Caminho null: retorna string vazia
            self.builder.position_at_end(null_bb)
            empty_str = self.create_global_string("")
            empty_ptr = self.builder.bitcast(empty_str, self.i8_ty.as_pointer(), name="rf_empty")
            self.builder.branch(end_bb)

            # Caminho normal: fseek → ftell → fseek → fread → fclose
            self.builder.position_at_end(ok_bb)
            self.builder.call(
                fseek,
                [fp, ir.Constant(self.i64_ty, 0), ir.Constant(self.i32_ty, 2)],
                name="rf_seek_end",
            )
            size = self.builder.call(ftell, [fp], name="rf_size")
            self.builder.call(
                fseek,
                [fp, ir.Constant(self.i64_ty, 0), ir.Constant(self.i32_ty, 0)],
                name="rf_seek_set",
            )

            size_plus = self.builder.add(size, ir.Constant(self.i64_ty, 1), name="rf_size_plus")
            buf = self.builder.call(self.malloc, [size_plus], name="rf_buf")

            self.builder.call(
                fread,
                [buf, ir.Constant(self.i64_ty, 1), size, fp],
                name="rf_fread",
            )

            end_ptr = self.builder.gep(buf, [size], name="rf_end_ptr")
            self.builder.store(ir.Constant(self.i8_ty, 0), end_ptr)

            self.builder.call(fclose, [fp], name="rf_fclose")
            self.builder.branch(end_bb)

            # Merge point: phi escolhe empty ou buf
            self.builder.position_at_end(end_bb)
            result = self.builder.phi(self.i8_ty.as_pointer(), name="rf_result")
            result.add_incoming(empty_ptr, null_bb)
            result.add_incoming(buf, ok_bb)
            return result

        # 4. Construtor de enum
        enum_name = None
        variant_idx = None

        STANDARD_VARIANTS = {
            "Ok": ("Result", 0),
            "Err": ("Result", 1),
            "Some": ("Option", 0),
            "None": ("Option", 1),
        }
        if func_name in STANDARD_VARIANTS:
            candidate_name, candidate_idx = STANDARD_VARIANTS[func_name]
            if candidate_name in self.struct_types:
                enum_name, variant_idx = candidate_name, candidate_idx

        if enum_name is None:
            lookup = self._find_enum_variant(func_name)
            if lookup is not None:
                enum_name, variant_idx = lookup

        if enum_name is not None:
            return self._construct_enum(enum_name, variant_idx, node.args)

        # 4.5 Alias de método (trait default)
        if func_name in getattr(self, 'alias_methods', set()):
            entry = self.functions_table[func_name]
            if isinstance(entry, tuple):
                func, func_type = entry
                self_ptr = self.symbol_table.get('self')
                if self_ptr is not None and len(func_type.args) >= 1:
                    self_val = self.builder.load(self_ptr, name="self_load")
                    args = [self_val]
                    for arg_node in node.args:
                        args.append(self.visit(arg_node))
                    final_args = []
                    for i, a in enumerate(args):
                        expected = func_type.args[i] if i < len(func_type.args) else None
                        if expected is not None and a.type != expected:
                            a = self._coerce_arg(a, expected, suffix=f"_alias_{i}")
                        final_args.append(a)
                    return self.builder.call(func, final_args, name=func_name + "_alias_call")

        # 5. Função normal
        if func_name in self.functions_table:
            func, func_type = self.functions_table[func_name]
            args = []
            arg_list = node.args
            if node.is_method and len(arg_list) > len(func_type.args):
                arg_list = arg_list[1:]

            for i, arg_node in enumerate(arg_list):
                arg_val = self.visit(arg_node)
                if isinstance(arg_val.type, ir.ArrayType):
                    arg_val = self.builder.bitcast(arg_val, self.voidptr_ty, name="array_decay")
                if i >= len(func_type.args):
                    args.append(arg_val)
                    continue
                expected_ty = func_type.args[i]
                arg_val = self._coerce_arg(arg_val, expected_ty)
                args.append(arg_val)

            fn_def = self.function_defs.get(func_name)
            if fn_def is not None and len(args) < len(func_type.args):
                for i in range(len(args), len(func_type.args)):
                    expected_ty = func_type.args[i]
                    param = fn_def.params[i] if i < len(fn_def.params) else None
                    if param is not None and getattr(param, 'default', None) is not None:
                        default_val = self.visit(param.default)
                        default_val = self._coerce_arg(default_val, expected_ty, suffix="_def")
                        args.append(default_val)
                    else:
                        args.append(self._zero_for_type(expected_ty))

            return self.builder.call(func, args, name=func_name + "_call")

        # Fallback
        return ir.Constant(self.i64_ty, 0)

    def _find_enum_variant(self, variant_name):
        for enum_name, enum_def in self.struct_defs.items():
            if not hasattr(enum_def, 'variants'):
                continue
            for i, variant in enumerate(enum_def.variants):
                if variant[0] == variant_name:
                    return enum_name, i
        return None

    def _construct_enum(self, enum_name, variant_idx, arg_nodes):
        struct_ty = self.struct_types[enum_name]
        struct_def = self.struct_defs[enum_name]
        max_p = self._enum_max_payloads(struct_def)

        struct_size = 8 + max_p * 8
        if struct_size < 16:
            struct_size = 16

        enum_ptr = self.builder.call(
            self.malloc,
            [ir.Constant(self.i64_ty, struct_size)],
            name=f"{enum_name.lower()}_lit",
        )
        enum_ptr = self.builder.bitcast(
            enum_ptr, struct_ty.as_pointer(),
            name=f"{enum_name.lower()}_cast",
        )

        tag_ptr = self.builder.gep(
            enum_ptr,
            [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)],
            name="tag_ptr",
        )
        self.builder.store(ir.Constant(self.i32_ty, variant_idx), tag_ptr)

        for i in range(max_p):
            payload_ptr = self.builder.gep(
                enum_ptr,
                [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i + 1)],
                name=f"payload_ptr_{i}",
            )
            if i < len(arg_nodes):
                val = self.visit(arg_nodes[i])
                if val.type != self.i64_ty:
                    if isinstance(val.type, ir.PointerType):
                        val = self.builder.ptrtoint(val, self.i64_ty, name=f"payload_cast_{i}")
                    elif val.type == self.f64_ty:
                        val = self.builder.fptosi(val, self.i64_ty, name=f"payload_cast_{i}")
                    elif isinstance(val.type, ir.IntType):
                        val = self.builder.sext(val, self.i64_ty, name=f"payload_cast_{i}")
                self.builder.store(val, payload_ptr)
            else:
                self.builder.store(ir.Constant(self.i64_ty, 0), payload_ptr)

        return enum_ptr

    def codegen_method_call(self, node, method_name):
        obj_node = node.args[0]
        obj_val = self.visit(obj_node)

        if isinstance(obj_val.type, ir.PointerType) and isinstance(obj_val.type.pointee, ir.IdentifiedStructType):
            struct_name = obj_val.type.pointee.name

            # Candidatos: nome exato primeiro ("Box_int__get"), depois o
            # base ("Box_get").
            candidates = [f"{struct_name}_{method_name}"]
            base = struct_name.split("<")[0]
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

                # Se caímos no método do base, o `self` do método tem
                # tipo `Box*`, mas `obj_val` é `Box_int_*`. São tipos
                # identificados LLVM distintos (mesmo layout, sem
                # herança), então o call exige bitcast.
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
                res_ptr = self.builder.call(self.strstr, [obj_val, target_str], name="str_strstr")
                zero_ptr = ir.Constant(self.voidptr_ty, None)
                return self.builder.icmp_signed("!=", res_ptr, zero_ptr, name="str_contains_res")
            elif method_name == "starts_with":
                target_str = self.visit(node.args[1])
                len_target = self.builder.call(self.strlen, [target_str], name="starts_len")
                cmp_res = self.builder.call(self.strncmp, [obj_val, target_str, len_target], name="starts_cmp")
                zero = ir.Constant(ir.IntType(32), 0)
                return self.builder.icmp_signed("==", cmp_res, zero, name="starts_res")
            elif method_name in ("upper", "lower"):
                len_val = self.builder.call(self.strlen, [obj_val], name="case_len")
                total_len = self.builder.add(len_val, ir.Constant(self.i64_ty, 1), name="case_total")
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

                is_lower = self.builder.icmp_signed(">=", char_val, lower_a, name="is_ge_a")
                is_upper = self.builder.icmp_signed("<=", char_val, lower_z, name="is_le_z")
                is_alpha = self.builder.and_(is_lower, is_upper, name="is_alpha")

                new_char = self.builder.add(char_val, offset, name="new_char")
                final_char = self.builder.select(is_alpha, new_char, char_val, name="final_char")
                self.builder.store(final_char, char_ptr)

                next_i = self.builder.add(i, ir.Constant(self.i64_ty, 1), name="case_next")
                i.add_incoming(next_i, self.builder.block)

                cond = self.builder.icmp_signed("<", next_i, len_val, name="case_cond")
                self.builder.cbranch(cond, loop_bb, end_bb)

                self.builder.position_at_end(end_bb)
                null_ptr = self.builder.gep(buf, [len_val], name="case_null_ptr")
                self.builder.store(ir.Constant(self.i8_ty, 0), null_ptr)
                return buf

        raise Exception(f"Método '{method_name}' não encontrado no Codegen.")