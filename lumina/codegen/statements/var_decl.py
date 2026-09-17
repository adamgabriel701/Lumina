from llvmlite import ir
from ...ast import CallExpr, ArrayExpr


class VarDeclMixin:

    def _zero_and_store_struct(self, ptr, struct_ty, name):
        """Aloca storage pra uma struct sem valor inicial e zera todos os campos."""
        zero_fields = []
        for ft in struct_ty.elements:
            if isinstance(ft, ir.PointerType):
                zero_fields.append(ir.Constant(ft, None))
            elif isinstance(ft, ir.DoubleType):
                zero_fields.append(ir.Constant(ft, 0.0))
            elif isinstance(ft, ir.IntType):
                zero_fields.append(ir.Constant(ft, 0))
            else:
                zero_fields.append(ir.Constant(ft, None))
        try:
            zero_val = ir.Constant(struct_ty, zero_fields)
        except Exception:
            zero_val = None

        ptr_pointee = ptr.type.pointee

        if ptr_pointee == struct_ty:
            if zero_val is not None:
                self.builder.store(zero_val, ptr)
            return

        try:
            n_fields = len(struct_ty.elements)
        except Exception:
            n_fields = 4
        size = 8 * n_fields if n_fields > 0 else 8
        raw = self.builder.call(
            self.malloc,
            [ir.Constant(self.i64_ty, size)],
            name=name + "_storage_raw",
        )
        storage = self.builder.bitcast(
            raw, struct_ty.as_pointer(), name=name + "_storage"
        )
        if zero_val is not None:
            try:
                self.builder.store(zero_val, storage)
            except Exception:
                pass

        if storage.type != ptr_pointee:
            if isinstance(ptr_pointee, ir.PointerType):
                storage = self.builder.bitcast(storage, ptr_pointee, name=name + "_cast")
            else:
                storage_int = self.builder.ptrtoint(storage, self.i64_ty, name=name + "_int")
                storage = self.builder.inttoptr(storage_int, ptr_pointee, name=name + "_cast")
        self.builder.store(storage, ptr)

    def _try_stack_alloc(self, node):
        """Tenta alocar `alloc(N)`/`alloc_bytes(N)` no stack.

        Condições para sucesso:
          - value é CallExpr de `alloc`/`alloc_bytes`
          - N é literal inteiro conhecido em compile-time
          - N > 0 e N <= LIMIT (evita estourar o stack)
          - o nome NÃO está em `self.escapes` nem `self.freed_vars`

        Retorna True se a alocação foi feita; False caso contrário.
        """
        if not isinstance(node.value, CallExpr):
            return False
        if getattr(node.value, 'is_method', False):
            return False

        callee = getattr(node.value.callee, 'name', None)
        if callee not in ('alloc', 'alloc_bytes'):
            return False

        escapes = getattr(self, 'escapes', set())
        freed = getattr(self, 'freed_vars', set())
        if node.name in escapes or node.name in freed:
            return False

        args = node.value.args
        if not args:
            return False
        from ...ast import NumberExpr
        if not isinstance(args[0], NumberExpr):
            return False
        if args[0].is_float:
            return False
        try:
            n = int(args[0].value, 0)
        except (ValueError, TypeError):
            return False

        LIMIT = 4096
        if n <= 0 or n > LIMIT:
            return False

        elem_ty = self.i64_ty if callee == 'alloc' else self.i8_ty
        arr_ty = ir.ArrayType(elem_ty, n)
        arr_ptr = self.builder.alloca(arr_ty, name=node.name + "_stack")

        zero = ir.Constant(self.i32_ty, 0)
        first_elem = self.builder.gep(
            arr_ptr, [zero, zero], name=node.name + "_first",
        )

        slot_ty = elem_ty.as_pointer()
        slot = self.builder.alloca(slot_ty, name=node.name)
        self.builder.store(first_elem, slot)

        self.symbol_table[node.name] = slot
        self.var_types[node.name] = "ptr"
        return True

    def visit_VarDecl(self, node):
        # Escape analysis: alloc(N) com N constante e sem escape vira alloca.
        if self._try_stack_alloc(node):
            # Mesmo no caso stack, registra tamanho de array literal
            # (para `for x in arr`, embora `alloc` não seja um array literal,
            # mantém o comportamento consistente).
            return

        val = self.visit(node.value) if node.value else None
        var_type = node.var_type if node.var_type else "int"

        callee_name = (
            getattr(node.value.callee, 'name', None)
            if isinstance(node.value, CallExpr) else None
        )
        is_alloc_call = callee_name == "alloc"
        is_alloc_bytes_call = callee_name == "alloc_bytes"

        is_struct_like = (
            (var_type in self.struct_types and not var_type.endswith("*"))
            or ("<" in var_type and var_type.split("<")[0] in self.struct_defs)
        )

        if is_alloc_call:
            llvm_ty = self.i64_ty.as_pointer()
        elif is_alloc_bytes_call:
            llvm_ty = self.i8_ty.as_pointer()
        elif is_struct_like:
            struct_ty = self.get_llvm_type(var_type)
            llvm_ty = struct_ty.as_pointer()
        else:
            llvm_ty = self.get_llvm_type(var_type)

        if val is not None and isinstance(val.type, ir.PointerType) and isinstance(val.type.pointee, ir.IdentifiedStructType):
            struct_name = val.type.pointee.name
            if var_type == struct_name or var_type == "int" or var_type == "ptr":
                llvm_ty = val.type

        elif val is not None and isinstance(val.type, ir.IdentifiedStructType):
            llvm_ty = val.type

        ptr = self.builder.alloca(llvm_ty, name=node.name)
        self.symbol_table[node.name] = ptr
        self.var_types[node.name] = var_type

        if val is not None:
            if is_alloc_call:
                val = self.builder.bitcast(val, self.i64_ty.as_pointer(), name="alloc_bitcast")
                self.builder.store(val, ptr)
            elif isinstance(val.type, ir.PointerType) and isinstance(ptr.type.pointee, ir.PointerType):
                val = self.builder.bitcast(val, ptr.type.pointee, name="ptr_cast")
                self.builder.store(val, ptr)
            elif val.type == ptr.type.pointee:
                self.builder.store(val, ptr)
            elif isinstance(val.type, ir.IdentifiedStructType) and ptr.type.pointee == val.type.as_pointer():
                tmp = self.builder.alloca(val.type, name="struct_tmp")
                self.builder.store(val, tmp)
                self.builder.store(tmp, ptr)
            elif ptr.type.pointee == self.i64_ty and val.type == self.voidptr_ty:
                res = self.builder.call(self.atoi, [val], name="str_to_int_call")
                self.builder.store(res, ptr)
            elif ptr.type.pointee == self.voidptr_ty and val.type == self.i64_ty:
                int_buf = self.builder.alloca(ir.ArrayType(self.i8_ty, 32), name="int_to_str_buf")
                int_buf_ptr = self.builder.bitcast(int_buf, self.voidptr_ty, name="int_str_ptr")
                fmt_str = self.create_global_string("%ld")
                self.builder.call(self.snprintf, [int_buf_ptr, ir.Constant(self.i64_ty, 32), fmt_str, val], name="int_to_str_call")
                self.builder.store(int_buf_ptr, ptr)
            elif ptr.type.pointee == self.i64_ty and val.type == self.f64_ty:
                val = self.builder.fptosi(val, self.i64_ty, name="float_to_int_store")
                self.builder.store(val, ptr)
            elif ptr.type.pointee == self.f64_ty and val.type == self.i64_ty:
                val = self.builder.sitofp(val, self.f64_ty, name="int_to_float_store")
                self.builder.store(val, ptr)
            else:
                target_ty = ptr.type.pointee
                if isinstance(val.type, ir.IntType) and isinstance(target_ty, ir.IntType):
                    if val.type.width < target_ty.width:
                        # i1 (bool) → zext; outros → sext
                        if val.type.width == 1:
                            val = self.builder.zext(val, target_ty, name="zext_cast")
                        else:
                            val = self.builder.sext(val, target_ty, name="sext_cast")
                    else:
                        val = self.builder.trunc(val, target_ty, name="trunc_cast")
                elif isinstance(val.type, ir.PointerType) and isinstance(target_ty, ir.IntType):
                    val = self.builder.ptrtoint(val, target_ty, name="ptrtoint_cast")
                elif isinstance(val.type, ir.IntType) and isinstance(target_ty, ir.PointerType):
                    val = self.builder.inttoptr(val, target_ty, name="inttoptr_cast")
                elif isinstance(val.type, ir.PointerType) and isinstance(target_ty, ir.PointerType):
                    val = self.builder.bitcast(val, target_ty, name="ptr_bitcast")
                else:
                    try:
                        val = self.builder.bitcast(val, target_ty, name="final_cast")
                    except Exception:
                        pass
                self.builder.store(val, ptr)

        elif is_struct_like:
            struct_ty = self.get_llvm_type(var_type)
            self._zero_and_store_struct(ptr, struct_ty, node.name)

        else:
            try:
                if isinstance(ptr.type.pointee, ir.PointerType):
                    zero = ir.Constant(ptr.type.pointee, None)
                elif isinstance(ptr.type.pointee, ir.DoubleType):
                    zero = ir.Constant(ptr.type.pointee, 0.0)
                else:
                    zero = ir.Constant(ptr.type.pointee, 0)
                self.builder.store(zero, ptr)
            except Exception:
                pass

        # NOVO: registra tamanho de array literal para `for x in arr`.
        # É aqui porque `visit_ArrayExpr` retorna um `i64*` (alloca do
        # `ArrayType`), e o `pointee` do slot é `i64`, não `ArrayType`.
        # Sem este registro, `for x in arr` não sabe o N.
        if isinstance(node.value, ArrayExpr):
            self.array_lengths[node.name] = len(node.value.elements)

        if is_alloc_call or is_alloc_bytes_call:
            self.heap_allocs.add(node.name)