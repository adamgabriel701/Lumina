from llvmlite import ir

from ..ast import (
    NumberExpr, BoolExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr,
    ArrayExpr, IndexExpr, MemberExpr, AddressOfExpr, DerefExpr, UnaryExpr,
    PropagateExpr, ComptimeExpr, StructLiteralExpr, MatchExpr, CastExpr,
    LambdaExpr, StructLiteralField, InterpolatedStringExpr, ErrorNode,
)
from ..ast.visitor import NodeVisitor


class ExpressionCodegen(NodeVisitor):

    def visit_NumberExpr(self, node):
        if node.value.startswith('0x') or node.value.startswith('0X'):
            return ir.Constant(self.f64_ty, float(int(node.value, 16))) if node.is_float else ir.Constant(self.i64_ty, int(node.value, 16))
        return ir.Constant(self.f64_ty, float(node.value)) if node.is_float else ir.Constant(self.i64_ty, int(node.value))

    def visit_BoolExpr(self, node):
        return ir.Constant(ir.IntType(1), 1 if node.value else 0)

    def visit_StringExpr(self, node):
        return self.create_global_string(node.value)

    def visit_InterpolatedStringExpr(self, node):
        # Suporte caso o parser use a nova AST de F-strings
        return self.codegen_fstring(node.parts)

    def visit_ArrayExpr(self, node):
        # Array literal
        elem_ty = self.i64_ty
        if len(node.elements) > 0:
            first_val = self.visit(node.elements[0])
            elem_ty = first_val.type
            # Só usa i64 se o tipo for compatível
            if not isinstance(elem_ty, ir.IntType):
                elem_ty = self.i64_ty

        array_ty = ir.ArrayType(elem_ty, len(node.elements))
        ptr = self.builder.alloca(array_ty, name="array_lit")

        for i, el in enumerate(node.elements):
            el_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)], name=f"arr_el_{i}")
            val = self.visit(el)
            if val.type != elem_ty:
                if isinstance(val.type, ir.PointerType) and isinstance(elem_ty, ir.PointerType):
                    val = self.builder.bitcast(val, elem_ty, name=f"arr_cast_{i}")
                elif isinstance(val.type, ir.IntType) and isinstance(elem_ty, ir.IntType):
                    if val.type.width < elem_ty.width:
                        val = self.builder.sext(val, elem_ty, name=f"arr_sext_{i}")
            self.builder.store(val, el_ptr)
        return ptr

    def codegen_fstring(self, elements):
        """Cria um buffer no stack e concatena todas as partes de uma F-string."""
        buf_size = 1024
        buf_ty = ir.ArrayType(self.i8_ty, buf_size)
        buf_ptr = self.builder.alloca(buf_ty, name="fstr_buf")

        i8_ptr = self.i8_ty.as_pointer()
        buf_i8_ptr = self.builder.bitcast(buf_ptr, i8_ptr, name="fstr_buf_i8")

        self.builder.store(ir.Constant(self.i8_ty, 0), buf_i8_ptr)

        for i, el in enumerate(elements):
            if isinstance(el, StringExpr):
                str_val = self.visit(el)
                self.builder.call(self.strcat, [buf_i8_ptr, str_val], name=f"fstr_cat_{i}")
            else:
                val = self.visit(el)
                if val.type == self.i64_ty:
                    int_buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 32), name=f"fstr_int_buf_{i}")
                    int_buf_ptr = self.builder.bitcast(int_buf, i8_ptr, name=f"fstr_int_ptr_{i}")
                    fmt_str = self.create_global_string("%ld")
                    self.builder.call(self.snprintf, [int_buf_ptr, ir.Constant(self.i64_ty, 32), fmt_str, val], name=f"fstr_snprintf_{i}")
                    self.builder.call(self.strcat, [buf_i8_ptr, int_buf_ptr], name=f"fstr_int_cat_{i}")
                elif val.type == self.voidptr_ty:
                    self.builder.call(self.strcat, [buf_i8_ptr, val], name=f"fstr_str_cat_{i}")

        return buf_i8_ptr

    def visit_VariableExpr(self, node):
        ptr = self.symbol_table.get(node.name)
        if not ptr:
            return ir.Constant(self.i64_ty, 0)
        return self.builder.load(ptr, name=node.name + "_load")

    def visit_BinaryExpr(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if left is None or right is None:
            return ir.Constant(self.i64_ty, 0)

        # Suporte a concatenação de strings com operador +
        if node.op == '+' and left.type == self.voidptr_ty and right.type == self.voidptr_ty:
            len1 = self.builder.call(self.strlen, [left], name="sconcat_len1")
            len2 = self.builder.call(self.strlen, [right], name="sconcat_len2")
            sum_len = self.builder.add(len1, len2, name="sconcat_sum")
            total_len = self.builder.add(sum_len, ir.Constant(self.i64_ty, 1), name="sconcat_total")
            buf = self.builder.call(self.malloc, [total_len], name="sconcat_buf")
            self.builder.call(self.strcpy, [buf, left], name="sconcat_cpy")
            self.builder.call(self.strcat, [buf, right], name="sconcat_cat")
            return buf

        # Coerção: se um lado é string e o outro é int/float, converte o número pra string
        if left.type == self.voidptr_ty and right.type in (self.i64_ty, self.f64_ty):
            if right.type == self.f64_ty:
                fmt = self.create_global_string("%f")
            else:
                fmt = self.create_global_string("%ld")
            buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 64), name="num_to_str")
            buf_ptr = self.builder.bitcast(buf, self.voidptr_ty, name="num_to_str_ptr")
            self.builder.call(self.snprintf, [buf_ptr, ir.Constant(self.i64_ty, 64), fmt, right], name="num_to_str_call")
            right = buf_ptr
        elif right.type == self.voidptr_ty and left.type in (self.i64_ty, self.f64_ty):
            if left.type == self.f64_ty:
                fmt = self.create_global_string("%f")
            else:
                fmt = self.create_global_string("%ld")
            buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 64), name="num_to_str")
            buf_ptr = self.builder.bitcast(buf, self.voidptr_ty, name="num_to_str_ptr")
            self.builder.call(self.snprintf, [buf_ptr, ir.Constant(self.i64_ty, 64), fmt, left], name="num_to_str_call")
            left = buf_ptr

        # Operações Matemáticas
        if node.op in ('+', '-', '*', '/', '%'):
            # Se ambos são strings e o op é '+', já foi tratado acima (concatenação)
            # Se um dos lados é string, não é operação matemática válida
            if left.type == self.voidptr_ty or right.type == self.voidptr_ty:
                return ir.Constant(self.i64_ty, 0)
            if left.type == self.f64_ty or right.type == self.f64_ty:
                left = self.to_float_if_needed(left)
                right = self.to_float_if_needed(right)
                if node.op == '+':
                    return self.builder.fadd(left, right, name="fadd")
                elif node.op == '-':
                    return self.builder.fsub(left, right, name="fsub")
                elif node.op == '*':
                    return self.builder.fmul(left, right, name="fmul")
                elif node.op == '/':
                    return self.builder.fdiv(left, right, name="fdiv")
            else:
                if node.op == '+':
                    return self.builder.add(left, right, name="add")
                elif node.op == '-':
                    return self.builder.sub(left, right, name="sub")
                elif node.op == '*':
                    return self.builder.mul(left, right, name="mul")
                elif node.op == '/':
                    return self.builder.sdiv(left, right, name="div")
                elif node.op == '%':
                    return self.builder.srem(left, right, name="mod")

        # Comparações
        if node.op in ('==', '!=', '<', '>', '<=', '>='):
            if left.type == self.f64_ty or right.type == self.f64_ty:
                left = self.to_float_if_needed(left)
                right = self.to_float_if_needed(right)
                return self.builder.fcmp_ordered(node.op, left, right, name="fcmp")
            else:
                return self.builder.icmp_signed(node.op, left, right, name="icmp")

        return ir.Constant(self.i64_ty, 0)

    def visit_CallExpr(self, node):
        func_name = None
        if isinstance(node.callee, MemberExpr):
            func_name = node.callee.member
        elif isinstance(node.callee, VariableExpr):
            func_name = node.callee.name

        # Se é uma chamada de método (obj.metodo(...)), tenta codegen_method_call primeiro.
        # Se não for método, ou o método não existir pra essa struct, cai pro codegen_user_call.
        if node.is_method:
            return self.codegen_method_call(node, func_name)
        else:
            return self.codegen_user_call(node, func_name)

    def codegen_user_call(self, node, func_name):
        # Chamada indireta via variável local (function pointer / lambda)
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

        # Chamada a função genérica — materializa cópia especializada
        gen_def = self.function_defs.get(func_name)
        if gen_def is not None and getattr(gen_def, 'type_params', None):
            arg_vals = [self.visit(a) for a in node.args]
            arg_types = [v.type for v in arg_vals]

            mangled = self.materialize_generic(gen_def, arg_types)
            func, func_type = self.functions_table[mangled]

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
                final_args.append(a)

            return self.builder.call(func, final_args, name=mangled + "_call")

        # ---- builtins ----
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
            self.builder.call(self.free, [ptr], name="free_call")
            return ir.Constant(self.i64_ty, 0)

        if func_name == "write_file":
            path_val = self.visit(node.args[0])
            content_val = self.visit(node.args[1])
            if not isinstance(path_val.type, ir.PointerType):
                path_val = self.builder.inttoptr(path_val, self.i8_ty.as_pointer(), name="wf_path_cast")
            if not isinstance(content_val.type, ir.PointerType):
                content_val = self.builder.inttoptr(content_val, self.i8_ty.as_pointer(), name="wf_content_cast")

            fopen_ty = ir.FunctionType(self.voidptr_ty, [self.i8_ty.as_pointer(), self.i8_ty.as_pointer()])
            fopen = self.module.globals.get("fopen")
            if fopen is None:
                fopen = ir.Function(self.module, fopen_ty, name="fopen")

            fputs_ty = ir.FunctionType(self.i32_ty, [self.i8_ty.as_pointer(), self.voidptr_ty])
            fputs = self.module.globals.get("fputs")
            if fputs is None:
                fputs = ir.Function(self.module, fputs_ty, name="fputs")

            fclose_ty = ir.FunctionType(self.i32_ty, [self.voidptr_ty])
            fclose = self.module.globals.get("fclose")
            if fclose is None:
                fclose = ir.Function(self.module, fclose_ty, name="fclose")

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
            fopen = self.module.globals.get("fopen")
            if fopen is None:
                fopen = ir.Function(self.module, fopen_ty, name="fopen")

            fseek_ty = ir.FunctionType(self.i32_ty, [self.voidptr_ty, self.i64_ty, self.i32_ty])
            fseek = self.module.globals.get("fseek")
            if fseek is None:
                fseek = ir.Function(self.module, fseek_ty, name="fseek")

            ftell_ty = ir.FunctionType(self.i64_ty, [self.voidptr_ty])
            ftell = self.module.globals.get("ftell")
            if ftell is None:
                ftell = ir.Function(self.module, ftell_ty, name="ftell")

            fread_ty = ir.FunctionType(self.i64_ty, [self.i8_ty.as_pointer(), self.i64_ty, self.i64_ty, self.voidptr_ty])
            fread = self.module.globals.get("fread")
            if fread is None:
                fread = ir.Function(self.module, fread_ty, name="fread")

            fclose_ty = ir.FunctionType(self.i32_ty, [self.voidptr_ty])
            fclose = self.module.globals.get("fclose")
            if fclose is None:
                fclose = ir.Function(self.module, fclose_ty, name="fclose")

            mode_r = self.create_global_string("r")
            fp = self.builder.call(fopen, [path_val, mode_r], name="rf_fopen")

            self.builder.call(fseek, [fp, ir.Constant(self.i64_ty, 0), ir.Constant(self.i32_ty, 2)], name="rf_seek_end")
            size = self.builder.call(ftell, [fp], name="rf_size")
            self.builder.call(fseek, [fp, ir.Constant(self.i64_ty, 0), ir.Constant(self.i32_ty, 0)], name="rf_seek_set")

            size_plus = self.builder.add(size, ir.Constant(self.i64_ty, 1), name="rf_size_plus")
            buf = self.builder.call(self.malloc, [size_plus], name="rf_buf")

            self.builder.call(fread, [buf, ir.Constant(self.i64_ty, 1), size, fp], name="rf_fread")

            end_ptr = self.builder.gep(buf, [size], name="rf_end_ptr")
            self.builder.store(ir.Constant(self.i8_ty, 0), end_ptr)

            self.builder.call(fclose, [fp], name="rf_fclose")
            return buf

        # ---- construtor de enum (genérico, cobre Ok/Err/Some/None + multi-payload) ----
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

        # ---- chamada a função normal ----
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
                if arg_val.type != expected_ty:
                    if isinstance(expected_ty, ir.PointerType) and isinstance(arg_val.type, ir.PointerType):
                        arg_val = self.builder.bitcast(arg_val, expected_ty, name="arg_ptr_cast")
                    elif expected_ty == self.i64_ty and isinstance(arg_val.type, ir.PointerType):
                        arg_val = self.builder.ptrtoint(arg_val, self.i64_ty, name="arg_ptr_to_int")
                    elif isinstance(expected_ty, ir.PointerType) and arg_val.type == self.i64_ty:
                        arg_val = self.builder.inttoptr(arg_val, expected_ty, name="arg_int_to_ptr")
                    elif expected_ty == self.f64_ty and arg_val.type == self.i64_ty:
                        arg_val = self.builder.sitofp(arg_val, self.f64_ty, name="arg_int_to_float")
                    elif expected_ty == self.i64_ty and arg_val.type == self.f64_ty:
                        arg_val = self.builder.fptosi(arg_val, self.i64_ty, name="arg_float_to_int")
                args.append(arg_val)
            return self.builder.call(func, args, name=func_name + "_call")

        # Fallback: retorna 0
        return ir.Constant(self.i64_ty, 0)

    def _find_enum_variant(self, variant_name):
        """Procura `variant_name` em qualquer enum declarado.
        Retorna (enum_name, variant_idx) ou None.
        """
        for enum_name, enum_def in self.struct_defs.items():
            if not hasattr(enum_def, 'variants'):
                continue
            for i, variant in enumerate(enum_def.variants):
                if variant[0] == variant_name:
                    return enum_name, i
        return None

    def _construct_enum(self, enum_name, variant_idx, arg_nodes):
        """Constrói um valor de enum {i32 tag, i64 p0, ..., i64 pN}."""
        struct_ty = self.struct_types[enum_name]
        struct_def = self.struct_defs[enum_name]
        max_p = self._enum_max_payloads(struct_def)

        # Tamanho alinhado: tag (8) + payloads (8 * max_p)
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

        # Tag
        tag_ptr = self.builder.gep(
            enum_ptr,
            [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)],
            name="tag_ptr",
        )
        self.builder.store(ir.Constant(self.i32_ty, variant_idx), tag_ptr)

        # Payloads
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
            real_method_name = f"{struct_name}_{method_name}"
            if real_method_name in self.functions_table:
                func, func_type = self.functions_table[real_method_name]
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

    def visit_MemberExpr(self, node):
        obj_val = self.visit(node.obj)

        # Se não é ponteiro pra struct, não tem como acessar campo
        if not (isinstance(obj_val.type, ir.PointerType)
                and isinstance(obj_val.type.pointee, ir.IdentifiedStructType)):
            return ir.Constant(self.i64_ty, 0)

        struct_name = obj_val.type.pointee.name
        field_idx = self.struct_fields.get(struct_name, {}).get(node.member)
        if field_idx is None:
            return ir.Constant(self.i64_ty, 0)

        if not node.is_safe:
            # Caminho normal
            elem_ptr = self.builder.gep(obj_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, field_idx)])
            return self.builder.load(elem_ptr, name=node.member + "_load")

        # Safe navigation: se obj_val for null, retorna 0; senão, faz o load
        null_ptr = ir.Constant(obj_val.type, None)
        is_null = self.builder.icmp_signed("==", obj_val, null_ptr, name="safe_nav_isnull")

        null_bb = self.builder.append_basic_block(name="safe_nav.null")
        ok_bb = self.builder.append_basic_block(name="safe_nav.ok")
        end_bb = self.builder.append_basic_block(name="safe_nav.end")

        self.builder.cbranch(is_null, null_bb, ok_bb)

        # Ramo null: só vai pro final
        self.builder.position_at_end(null_bb)
        self.builder.branch(end_bb)

        # Ramo ok: faz o load
        self.builder.position_at_end(ok_bb)
        elem_ptr = self.builder.gep(obj_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, field_idx)])
        field_val = self.builder.load(elem_ptr, name=node.member + "_load")
        self.builder.branch(end_bb)

        # Merge
        self.builder.position_at_end(end_bb)
        if isinstance(field_val.type, ir.PointerType):
            default_val = ir.Constant(field_val.type, None)
        else:
            default_val = ir.Constant(field_val.type, 0)
        phi = self.builder.phi(field_val.type, name="safe_nav_result")
        phi.add_incoming(default_val, null_bb)
        phi.add_incoming(field_val, ok_bb)
        return phi

    def visit_IndexExpr(self, node):
        arr_val = self.visit(node.array)

        # --- Slicing: arr[start..end] ---
        if isinstance(node.index, BinaryExpr) and node.index.op == '..':
            start_val = self.visit(node.index.left)
            end_val = self.visit(node.index.right)

            # Cast pra i64 se necessário
            if start_val.type != self.i64_ty:
                start_val = self.builder.sext(start_val, self.i64_ty, name="slice_start_sext")
            if end_val.type != self.i64_ty:
                end_val = self.builder.sext(end_val, self.i64_ty, name="slice_end_sext")

            length = self.builder.sub(end_val, start_val, name="slice_len")

            # String slicing: retorna substring
            if arr_val.type == self.voidptr_ty or (isinstance(arr_val.type, ir.PointerType) and arr_val.type.pointee == self.i8_ty):
                length_plus = self.builder.add(length, ir.Constant(self.i64_ty, 1), name="slice_len_plus")
                buf = self.builder.call(self.malloc, [length_plus], name="slice_buf")
                start_ptr = self.builder.gep(arr_val, [start_val], name="slice_start_ptr")
                self.builder.call(self.strncpy, [buf, start_ptr, length], name="slice_cpy")
                end_ptr = self.builder.gep(buf, [length], name="slice_end_ptr")
                self.builder.store(ir.Constant(self.i8_ty, 0), end_ptr)
                return buf

            # Array slicing (ponteiro): retorna novo array
            elif isinstance(arr_val.type, ir.PointerType):
                # Aloca array de tamanho `length`
                elem_ty = arr_val.type.pointee
                if isinstance(elem_ty, ir.ArrayType):
                    elem_ty = elem_ty.element

                # Buffer: length * sizeof(elem)
                # Por simplicidade, assume i64
                buf_size = self.builder.mul(length, ir.Constant(self.i64_ty, 8), name="slice_arr_size")
                buf = self.builder.call(self.malloc, [buf_size], name="slice_arr_buf")
                buf_ty = self.i64_ty.as_pointer()
                buf = self.builder.bitcast(buf, buf_ty, name="slice_arr_cast")

                # Copia elemento por elemento
                loop_bb = self.builder.append_basic_block(name="slice_loop")
                end_bb = self.builder.append_basic_block(name="slice_end")
                pred_bb = self.builder.block

                self.builder.branch(loop_bb)
                self.builder.position_at_end(loop_bb)

                i = self.builder.phi(self.i64_ty, name="slice_i")
                i.add_incoming(ir.Constant(self.i64_ty, 0), pred_bb)

                # Carrega src[start + i]
                src_idx = self.builder.add(start_val, i, name="slice_src_idx")
                src_ptr = self.builder.gep(arr_val, [src_idx], name="slice_src_ptr")
                val_loaded = self.builder.load(src_ptr, name="slice_val")
                if val_loaded.type != self.i64_ty:
                    if isinstance(val_loaded.type, ir.PointerType):
                        val_loaded = self.builder.ptrtoint(val_loaded, self.i64_ty, name="slice_val_cast")
                    elif val_loaded.type.width < 64:
                        val_loaded = self.builder.sext(val_loaded, self.i64_ty, name="slice_val_sext")

                # Guarda dst[i]
                dst_ptr = self.builder.gep(buf, [i], name="slice_dst_ptr")
                self.builder.store(val_loaded, dst_ptr)

                next_i = self.builder.add(i, ir.Constant(self.i64_ty, 1), name="slice_i_next")
                i.add_incoming(next_i, self.builder.block)

                cond = self.builder.icmp_signed("<", next_i, length, name="slice_cond")
                self.builder.cbranch(cond, loop_bb, end_bb)

                self.builder.position_at_end(end_bb)
                return buf

        # --- Index normal (sem slice) ---
        idx_val = self.visit(node.index)
        if isinstance(arr_val.type, ir.PointerType):
            if isinstance(arr_val.type.pointee, ir.ArrayType):
                elem_ptr = self.builder.gep(arr_val, [ir.Constant(self.i32_ty, 0), idx_val])
                return self.builder.load(elem_ptr, name="arr_idx_load")
            else:
                elem_ptr = self.builder.gep(arr_val, [idx_val])
                return self.builder.load(elem_ptr, name="ptr_idx_load")
        return ir.Constant(self.i64_ty, 0)

    def visit_UnaryExpr(self, node):
        val = self.visit(node.val)
        if node.op == '-':
            return self.builder.neg(val, name="neg") if val.type == self.i64_ty else self.builder.fneg(val, name="fneg")
        elif node.op == 'not':
            zero = ir.Constant(val.type, 0)
            return self.builder.icmp_signed("!=", val, zero, name="not_cond")
        return val

    def visit_AddressOfExpr(self, node):
        # &x retorna o endereço (alloca) da variável x
        if isinstance(node.val, VariableExpr):
            ptr = self.symbol_table.get(node.val.name)
            if ptr:
                return ptr
        # Fallback: visita
        return self.visit(node.val)

    def visit_DerefExpr(self, node):
        ptr = self.visit(node.val)
        if not isinstance(ptr.type, ir.PointerType):
            # Fallback: se não é ponteiro, retorna 0
            return ir.Constant(self.i64_ty, 0)
        return self.builder.load(ptr, name="deref_load")

    def visit_PropagateExpr(self, node):
        result_ptr = self.visit(node.val)

        # Fallback: se não é Result*, só devolve o valor
        if not (isinstance(result_ptr.type, ir.PointerType)
                and isinstance(result_ptr.type.pointee, ir.IdentifiedStructType)):
            return result_ptr

        struct_name = result_ptr.type.pointee.name
        if struct_name != "Result":
            return result_ptr

        # Carrega o tag (0 = Ok, 1 = Err)
        tag_ptr = self.builder.gep(
            result_ptr,
            [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)],
            name="prop_tag_ptr",
        )
        tag_val = self.builder.load(tag_ptr, name="prop_tag")

        is_err = self.builder.icmp_signed(
            "!=", tag_val, ir.Constant(self.i32_ty, 0),
            name="prop_iserr",
        )

        err_bb = self.builder.append_basic_block(name="prop.err")
        ok_bb = self.builder.append_basic_block(name="prop.ok")

        self.builder.cbranch(is_err, err_bb, ok_bb)

        # Ramo Err: faz ret da função atual com o próprio Result
        self.builder.position_at_end(err_bb)
        func_ret_ty = self.functions_table[self.current_func_name][1].return_type
        if result_ptr.type != func_ret_ty:
            if isinstance(func_ret_ty, ir.PointerType):
                ret_val = self.builder.bitcast(result_ptr, func_ret_ty, name="prop_ret_cast")
            else:
                ret_val = self.builder.ptrtoint(result_ptr, func_ret_ty, name="prop_ret_int")
        else:
            ret_val = result_ptr
        self.builder.ret(ret_val)

        # Ramo Ok: extrai o payload (i64)
        self.builder.position_at_end(ok_bb)
        payload_ptr = self.builder.gep(
            result_ptr,
            [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)],
            name="prop_payload_ptr",
        )
        payload_val = self.builder.load(payload_ptr, name="prop_payload")

        return payload_val

    def visit_ComptimeExpr(self, node):
        try:
            val = int(node.expr.value)
            return ir.Constant(self.i64_ty, val)
        except Exception:
            return self.visit(node.expr)

    def visit_StructLiteralExpr(self, node):
        struct_ty = self.get_llvm_type(node.struct_name)
        ptr = self.builder.alloca(struct_ty, name=node.struct_name.lower() + "_lit")

        # Compatível com tuple e dataclass
        for field in node.fields:
            if isinstance(field, tuple):
                fname, fexpr = field
            else:
                fname = field.name
                fexpr = field.value

            elem_index = self.struct_fields[node.struct_name].get(fname, 0)
            elem_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, elem_index)], name=fname + "_ptr")
            val = self.visit(fexpr)
            self.builder.store(val, elem_ptr)
        return ptr

    def visit_CastExpr(self, node):
        val = self.visit(node.expr)
        target_ty = self.get_llvm_type(node.target_type)
        if val.type == target_ty:
            return val
        if val.type == self.i64_ty and target_ty == self.f64_ty:
            return self.builder.sitofp(val, self.f64_ty, name="int_to_float")
        elif val.type == self.f64_ty and target_ty == self.i64_ty:
            return self.builder.fptosi(val, self.i64_ty, name="float_to_int")
        elif isinstance(val.type, ir.PointerType) and target_ty == self.i64_ty:
            return self.builder.ptrtoint(val, self.i64_ty, name="ptr_to_int")
        elif val.type == self.i64_ty and isinstance(target_ty, ir.PointerType):
            return self.builder.inttoptr(val, target_ty, name="int_to_ptr")
        return val

    def visit_LambdaExpr(self, node):
        if not hasattr(self, 'lambda_counter'):
            self.lambda_counter = 0
        func_name = f"__lambda_{self.lambda_counter}"
        self.lambda_counter += 1

        ret_ty = self.get_llvm_param_type(node.return_type)

        param_types = []
        for p in node.params:
            if isinstance(p, tuple):
                p_type = p[1]
            else:
                p_type = p.type_ann
            param_types.append(self.get_llvm_param_type(p_type))

        func_type = ir.FunctionType(ret_ty, param_types)
        func = ir.Function(self.module, func_type, name=func_name)

        old_builder = self.builder
        old_symtab = self.symbol_table
        block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        self.symbol_table = {}

        for i, p in enumerate(node.params):
            if isinstance(p, tuple):
                p_name, p_type = p[0], p[1]
            else:
                p_name, p_type = p.name, p.type_ann

            p_ty = self.get_llvm_param_type(p_type)
            ptr = self.builder.alloca(p_ty, name=p_name)
            self.builder.store(func.args[i], ptr)
            self.symbol_table[p_name] = ptr

        # Body: mistura de Stmt e Expr. Se for Expr (inline), vira `ret expr`.
        from ..ast.expressions import Expr as ExprBase
        for stmt in node.body:
            if isinstance(stmt, ExprBase) and not isinstance(stmt, type(None)):
                val = self.visit(stmt)
                if ret_ty != ir.VoidType() and val.type != ret_ty:
                    if ret_ty == self.i64_ty and val.type == self.f64_ty:
                        val = self.builder.fptosi(val, self.i64_ty, name="lambda_ret_cast")
                    elif ret_ty == self.f64_ty and val.type == self.i64_ty:
                        val = self.builder.sitofp(val, self.f64_ty, name="lambda_ret_cast")
                    elif isinstance(ret_ty, ir.PointerType) and val.type == self.i64_ty:
                        val = self.builder.inttoptr(val, ret_ty, name="lambda_ret_cast")
                    elif ret_ty == self.i64_ty and isinstance(val.type, ir.PointerType):
                        val = self.builder.ptrtoint(val, self.i64_ty, name="lambda_ret_cast")
                self.builder.ret(val)
                break
            else:
                self.visit(stmt)

        if not self.builder.block.is_terminated:
            if ret_ty == ir.VoidType():
                self.builder.ret_void()
            else:
                self.builder.ret(ir.Constant(ret_ty, 0))

        self.builder = old_builder
        self.symbol_table = old_symtab
        return self.builder.bitcast(func, self.voidptr_ty, name="lambda_ptr")

    def visit_MatchExpr(self, node):
        cond_val = self.visit(node.condition)

        # 1. Match para Inteiros
        if cond_val.type == self.i64_ty:
            end_bb = self.builder.append_basic_block(name="match.end")
            default_bb = self.builder.append_basic_block(name="match.default")
            sw = self.builder.switch(cond_val, default_bb)
            incoming = []
            phi_ty = None

            for case in node.cases:
                # Compatível com tuple (velho) e MatchCase (novo)
                if isinstance(case, tuple):
                    val_node, res_node = case
                else:
                    val_node = case.pattern
                    res_node = case.body

                case_bb = self.builder.append_basic_block(name="match.case")
                val = self.visit(val_node)
                sw.add_case(val, case_bb)
                self.builder.position_at_end(case_bb)
                res_val = self.visit(res_node)

                if phi_ty is None:
                    phi_ty = res_val.type
                elif phi_ty != res_val.type:
                    res_val = self.builder.bitcast(res_val, phi_ty, name="case_cast")

                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((res_val, self.builder.block))

            self.builder.position_at_end(default_bb)
            if node.default:
                default_val = self.visit(node.default)
                if phi_ty is None:
                    phi_ty = default_val.type
                elif phi_ty != default_val.type:
                    default_val = self.builder.bitcast(default_val, phi_ty, name="def_cast")

                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((default_val, self.builder.block))
            else:
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((ir.Constant(self.i64_ty, 0), self.builder.block))

            self.builder.position_at_end(end_bb)
            if phi_ty is None:
                phi_ty = self.i64_ty
            phi = self.builder.phi(phi_ty, name="match_res")
            for val, blk in incoming:
                phi.add_incoming(val, blk)
            return phi

        # 2. Match para Strings
        elif cond_val.type == self.voidptr_ty:
            strcmp_fn = next((f for f in self.module.functions if f.name == "strcmp"), None)
            if not strcmp_fn:
                strcmp_ty = ir.FunctionType(ir.IntType(32), [self.voidptr_ty, self.voidptr_ty])
                strcmp_fn = ir.Function(self.module, strcmp_ty, name="strcmp")

            end_bb = self.builder.append_basic_block(name="match_str.end")
            incoming = []
            phi_ty = None

            for case in node.cases:
                if isinstance(case, tuple):
                    val_node, res_node = case
                else:
                    val_node = case.pattern
                    res_node = case.body

                val_str = self.visit(val_node)
                cmp_res = self.builder.call(strcmp_fn, [cond_val, val_str], name="strcmp_call")
                is_eq = self.builder.icmp_signed("==", cmp_res, ir.Constant(ir.IntType(32), 0), name="str_eq")

                then_bb = self.builder.append_basic_block(name="match_str.case")
                next_bb = self.builder.append_basic_block(name="match_str.next")
                self.builder.cbranch(is_eq, then_bb, next_bb)

                self.builder.position_at_end(then_bb)
                res_val = self.visit(res_node)
                if phi_ty is None:
                    phi_ty = res_val.type
                elif phi_ty != res_val.type:
                    res_val = self.builder.bitcast(res_val, phi_ty, name="str_case_cast")

                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((res_val, self.builder.block))

                self.builder.position_at_end(next_bb)

            if node.default:
                default_val = self.visit(node.default)
                if phi_ty is None:
                    phi_ty = default_val.type
                elif phi_ty != default_val.type:
                    default_val = self.builder.bitcast(default_val, phi_ty, name="str_def_cast")

                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((default_val, self.builder.block))
            else:
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((ir.Constant(self.i64_ty, 0), self.builder.block))

            self.builder.position_at_end(end_bb)
            if phi_ty is None:
                phi_ty = self.i64_ty
            phi = self.builder.phi(phi_ty, name="match_str_res")
            for val, blk in incoming:
                phi.add_incoming(val, blk)
            return phi

        # 3. Match para Structs (Destructuring)
        elif isinstance(cond_val.type, ir.PointerType) and isinstance(cond_val.type.pointee, ir.IdentifiedStructType):
            struct_name = cond_val.type.pointee.name
            end_bb = self.builder.append_basic_block(name="match_struct.end")
            incoming = []
            phi_ty = None

            for case in node.cases:
                if isinstance(case, tuple):
                    val_node, res_node = case
                else:
                    val_node = case.pattern
                    res_node = case.body

                if isinstance(val_node, StructLiteralExpr) and val_node.struct_name == struct_name:
                    then_bb = self.builder.append_basic_block(name="match_struct.case")
                    next_bb = self.builder.append_basic_block(name="match_struct.next")

                    self.builder.branch(then_bb)
                    self.builder.position_at_end(then_bb)

                    for field in val_node.fields:
                        if isinstance(field, tuple):
                            fname, fexpr = field
                        else:
                            fname = field.name
                            fexpr = field.value

                        if isinstance(fexpr, VariableExpr):
                            elem_index = self.struct_fields[struct_name].get(fname)
                            if elem_index is not None:
                                elem_ptr = self.builder.gep(cond_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, elem_index)])
                                field_val = self.builder.load(elem_ptr, name="bind_val")
                                var_ptr = self.builder.alloca(field_val.type, name=fexpr.name)
                                self.builder.store(field_val, var_ptr)
                                self.symbol_table[fexpr.name] = var_ptr

                    res_val = self.visit(res_node)
                    if phi_ty is None:
                        phi_ty = res_val.type
                    elif phi_ty != res_val.type:
                        res_val = self.builder.bitcast(res_val, phi_ty, name="struct_case_cast")

                    if not self.builder.block.is_terminated:
                        self.builder.branch(end_bb)
                        incoming.append((res_val, self.builder.block))

                    self.builder.position_at_end(next_bb)

            if node.default:
                default_val = self.visit(node.default)
                if phi_ty is None:
                    phi_ty = default_val.type
                elif phi_ty != default_val.type:
                    default_val = self.builder.bitcast(default_val, phi_ty, name="struct_def_cast")

                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((default_val, self.builder.block))
            else:
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)
                    incoming.append((ir.Constant(self.i64_ty, 0), self.builder.block))

            self.builder.position_at_end(end_bb)
            if phi_ty is None:
                phi_ty = self.i64_ty
            phi = self.builder.phi(phi_ty, name="match_struct_res")
            for val, blk in incoming:
                phi.add_incoming(val, blk)
            return phi

        return ir.Constant(self.i64_ty, 0)

    def generic_visit(self, node):
        return ir.Constant(self.i64_ty, 0)