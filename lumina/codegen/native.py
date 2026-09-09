from llvmlite import ir
from ..ast import CallExpr, ArrayExpr, StringExpr, VariableExpr

class NativeCallCodegen:
    def codegen_native_call(self, node: CallExpr):
        if node.is_method: return self.codegen_native_method(node)
        if node.name == "input":
            buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 256), name="input_buf")
            self.builder.call(self.scanf, [self.create_global_string("%s"), buf])
            return self.builder.bitcast(buf, self.voidptr_ty)
        elif node.name == "atoi": return self.builder.call(self.atoi, [self.codegen_expr(node.args[0])], name="atoi_call")
        elif node.name == "len":
            if isinstance(node.args[0], VariableExpr) and node.args[0].name in self.array_sizes: return ir.Constant(self.i64_ty, self.array_sizes[node.args[0].name])
            ptr = self.codegen_expr(node.args[0])
            return self.builder.call(self.strlen, [ptr], name="strlen_call") if ptr.type == self.voidptr_ty else ir.Constant(self.i64_ty, 0)
        elif node.name == "free":
            if isinstance(node.args[0], VariableExpr):
                for s in self.cleanup_vars:
                    if node.args[0].name in s: s.remove(node.args[0].name); break
            ptr = self.codegen_expr(node.args[0])
            if ptr.type != self.voidptr_ty: ptr = self.builder.bitcast(ptr, self.voidptr_ty, name="manual_free_cast")
            self.builder.call(self.free, [ptr], name="free_call"); return ir.Constant(self.i64_ty, 0)
        elif node.name == "alloc":
            size_bytes = self.builder.mul(self.codegen_expr(node.args[0]), ir.Constant(self.i64_ty, 8), name="size_bytes")
            return self.builder.bitcast(self.builder.call(self.malloc, [size_bytes], name="malloc_ptr"), self.i64_ty.as_pointer(), name="malloc_ptr_i64")
        elif node.name == "alloc_bytes": return self.builder.call(self.malloc, [self.codegen_expr(node.args[0])], name="malloc_bytes_ptr")
        elif node.name == "argv": return self.builder.load(self.builder.gep(self.builder.load(self.symbol_table['argv'], name="argv_val"), [self.codegen_expr(node.args[0])], name="arg_ptr_ptr"), name="arg_val")
        elif node.name == "read_file": return self.codegen_read_file(node)
        elif node.name == "write_file":
            fp = self.builder.call(self.fopen, [self.codegen_expr(node.args[0]), self.create_global_string("w")], name="file_ptr_w")
            self.builder.call(self.fputs, [self.codegen_expr(node.args[1]), fp]); self.builder.call(self.fclose, [fp]); return ir.Constant(self.i64_ty, 0)
        elif node.name == "int": return self.codegen_int_cast(node)
        elif node.name in self.variant_defs: return self.codegen_enum_ctor(node)
        elif node.name == "float":
            val = self.codegen_expr(node.args[0])
            return self.builder.sitofp(val, self.f64_ty, name="float_cast") if val.type == self.i64_ty else val
        elif node.name == "str": return self.codegen_str_cast(node)
        elif node.name == "chr":
            buf = self.builder.call(self.malloc, [ir.Constant(self.i64_ty, 2)], name="chr_malloc")
            self.builder.call(self.sprintf, [buf, self.create_global_string("%c"), self.codegen_expr(node.args[0])], name="chr_sprintf")
            return buf
        elif node.name == "print": return self.codegen_print(node)
        return None

    def codegen_native_method(self, node: CallExpr):
        obj_val = self.codegen_expr(node.args[0])
        if obj_val.type == self.voidptr_ty: return self.codegen_str_method(node, obj_val)
        struct_ty = self.var_types.get(node.args[0].name) if isinstance(node.args[0], VariableExpr) else None
        if isinstance(struct_ty, ir.PointerType) and isinstance(struct_ty.pointee, ir.IdentifiedStructType): struct_ty = struct_ty.pointee
        struct_name = struct_ty.name if struct_ty else "Unknown"
        func_name = f"{struct_name}_{node.name}"
        if func_name in self.functions_table:
            func, func_type = self.functions_table[func_name]
            return self.builder.call(func, [obj_val] + [self.codegen_expr(a) for a in node.args[1:]], name=func_name + "_call")
        raise Exception(f"Método nativo '{node.name}' não encontrado.")

    def codegen_str_method(self, node, obj_val):
        arg_val = self.codegen_expr(node.args[1])
        if node.name == "contains":
            strstr_fn = next((f for f in self.module.functions if f.name == "strstr"), ir.Function(self.module, ir.FunctionType(self.voidptr_ty, [self.voidptr_ty, self.voidptr_ty]), name="strstr"))
            res = self.builder.call(strstr_fn, [obj_val, arg_val], name="strstr_call")
            return self.builder.zext(self.builder.icmp_signed("!=", res, ir.Constant(self.voidptr_ty, None), name="str_found"), self.i64_ty, name="str_found_int")
        elif node.name == "starts_with":
            strncmp_fn = next((f for f in self.module.functions if f.name == "strncmp"), ir.Function(self.module, ir.FunctionType(ir.IntType(32), [self.voidptr_ty, self.voidptr_ty, self.i64_ty]), name="strncmp"))
            prefix_len = self.builder.call(self.strlen, [arg_val], name="prefix_len")
            cmp_res = self.builder.call(strncmp_fn, [obj_val, arg_val, prefix_len], name="strncmp_call")
            return self.builder.zext(self.builder.icmp_signed("==", cmp_res, ir.Constant(ir.IntType(32), 0), name="str_eq"), self.i64_ty, name="str_eq_int")
        raise Exception(f"Método de string '{node.name}' não suportado.")

    def codegen_read_file(self, node):
        fp = self.builder.call(self.fopen, [self.codegen_expr(node.args[0]), self.create_global_string("r")], name="file_ptr")
        is_null = self.builder.icmp_signed("==", fp, ir.Constant(self.voidptr_ty, None), name="is_null")
        then_bb, else_bb, end_bb = self.builder.append_basic_block(name="read_file.exists"), self.builder.append_basic_block(name="read_file.not_exists"), self.builder.append_basic_block(name="read_file.end")
        self.builder.cbranch(is_null, else_bb, then_bb)
        self.builder.position_at_end(then_bb)
        buf_ptr = self.builder.bitcast(self.builder.alloca(ir.ArrayType(self.i8_ty, 4096), name="read_buf"), self.voidptr_ty, name="buf_ptr")
        self.builder.call(self.fgets, [buf_ptr, ir.Constant(self.i32_ty, 4096), fp]); self.builder.call(self.fclose, [fp]); self.builder.branch(end_bb)
        self.builder.position_at_end(else_bb)
        empty_str = self.create_global_string(""); self.builder.branch(end_bb)
        self.builder.position_at_end(end_bb)
        phi = self.builder.phi(self.voidptr_ty, name="read_file_res"); phi.add_incoming(buf_ptr, then_bb); phi.add_incoming(empty_str, else_bb)
        return phi

    def codegen_int_cast(self, node):
        res = self.builder.call(self.atoi, [self.codegen_expr(node.args[0])], name="atoi_call")
        opt_ty = self.struct_types.get("Option")
        if not opt_ty: raise Exception("Tipo Option não declarado.")
        ptr = self.builder.alloca(opt_ty, name="opt_tmp")
        is_zero = self.builder.icmp_signed("==", res, ir.Constant(self.i64_ty, 0), name="is_zero")
        self.builder.store(self.builder.zext(is_zero, self.i32_ty, name="tag_val"), self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)]))
        self.builder.store(res, self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)]))
        return ptr

    def codegen_enum_ctor(self, node):
        enum_name, index, _ = self.variant_defs[node.name]
        ptr = self.builder.alloca(self.struct_types[enum_name], name="enum_tmp")
        self.builder.store(ir.Constant(self.i32_ty, index), self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)]))
        payload_ptr = self.builder.gep(ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)])
        if node.args:
            val = self.codegen_expr(node.args[0])
            if val.type != self.i64_ty: val = self.builder.zext(val, self.i64_ty, name="payload_cast")
            self.builder.store(val, payload_ptr)
        else: self.builder.store(ir.Constant(self.i64_ty, 0), payload_ptr)
        return ptr

    def codegen_str_cast(self, node):
        buf_ptr = self.builder.bitcast(self.builder.alloca(ir.ArrayType(self.i8_ty, 256), name="str_cast_buf"), self.voidptr_ty, name="cast_buf_ptr")
        val = self.codegen_expr(node.args[0])
        if val.type == self.i64_ty: self.builder.call(self.sprintf, [buf_ptr, self.create_global_string("%ld"), val])
        elif val.type == self.f64_ty: self.builder.call(self.sprintf, [buf_ptr, self.create_global_string("%f"), val])
        return buf_ptr

    def codegen_print(self, node):
        for arg_node in node.args:
            if isinstance(arg_node, ArrayExpr):
                for el in arg_node.elements: self._print_val(el, self.codegen_expr(el))
            else: self._print_val(arg_node, self.codegen_expr(arg_node))
        self.builder.call(self.printf, [self.create_global_string("\n")])
        return ir.Constant(self.i64_ty, 0)

    def _print_val(self, arg_node, arg_val):
        if isinstance(arg_node, StringExpr): self.builder.call(self.printf, [self.create_global_string("%s "), arg_val])
        else:
            fmt = "%f " if arg_val.type == self.f64_ty else ("%s " if arg_val.type == self.voidptr_ty else "%ld ")
            self.builder.call(self.printf, [self.create_global_string(fmt), arg_val])