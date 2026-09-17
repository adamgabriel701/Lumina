from llvmlite import ir


class FlowMixin:

    # ==================================================================
    # Escopo de defer
    #
    # `_emit_scope_defers` emite SEM deletar (usado em break/continue/
    # return — o path irmão ainda precisa emitir os mesmos defers).
    # `_end_scope` emite E deleta (usado em fallthrough — a partir
    # daqui, o stack não contém mais estes defers).
    # `_emit_all_defers` emite todos os pendentes SEM deletar (return).
    # ==================================================================
    def _begin_scope(self):
        return len(getattr(self, 'defer_stack', []) or [])

    def _emit_scope_defers(self, start):
        stack = getattr(self, 'defer_stack', None)
        if not stack:
            return
        for body in reversed(stack[start:]):
            for stmt in body:
                if self.builder.block.is_terminated:
                    return
                self.visit(stmt)

    def _end_scope(self, start):
        stack = getattr(self, 'defer_stack', None)
        if not stack:
            return
        if not self.builder.block.is_terminated:
            self._emit_scope_defers(start)
        del stack[start:]

    def _emit_all_defers(self):
        self._emit_scope_defers(0)

    # ------------------------------------------------------------------
    # Helper: coerção de tipo antes do store
    # ------------------------------------------------------------------
    def _coerce_val_to(self, val, target_ty, name="val"):
        if val.type == target_ty:
            return val

        if isinstance(val.type, ir.IntType) and isinstance(target_ty, ir.IntType):
            if val.type.width == 1 and target_ty.width > 1:
                return self.builder.zext(val, target_ty, name=f"{name}_zext")
            if val.type.width < target_ty.width:
                return self.builder.sext(val, target_ty, name=f"{name}_sext")
            if val.type.width > target_ty.width:
                return self.builder.trunc(val, target_ty, name=f"{name}_trunc")
            return val

        if isinstance(val.type, ir.IntType) and isinstance(target_ty, ir.DoubleType):
            return self.builder.sitofp(val, target_ty, name=f"{name}_sitofp")

        if isinstance(val.type, ir.DoubleType) and isinstance(target_ty, ir.IntType):
            return self.builder.fptosi(val, target_ty, name=f"{name}_fptosi")

        if target_ty == self.i64_ty and val.type == self.voidptr_ty:
            return self.builder.call(self.atoi, [val], name=f"{name}_atoi")

        if target_ty == self.voidptr_ty and val.type == self.i64_ty:
            int_buf = self.builder.alloca(
                ir.ArrayType(self.i8_ty, 32), name=f"{name}_int_buf"
            )
            int_buf_ptr = self.builder.bitcast(
                int_buf, self.voidptr_ty, name=f"{name}_int_buf_ptr"
            )
            fmt_str = self.create_global_string("%ld")
            self.builder.call(
                self.snprintf,
                [int_buf_ptr, ir.Constant(self.i64_ty, 32), fmt_str, val],
                name=f"{name}_snprintf",
            )
            return int_buf_ptr

        if isinstance(val.type, ir.PointerType) and isinstance(target_ty, ir.IntType):
            return self.builder.ptrtoint(val, target_ty, name=f"{name}_ptrtoint")

        if isinstance(val.type, ir.IntType) and isinstance(target_ty, ir.PointerType):
            return self.builder.inttoptr(val, target_ty, name=f"{name}_inttoptr")

        if isinstance(val.type, ir.PointerType) and isinstance(target_ty, ir.PointerType):
            if (isinstance(val.type.pointee, ir.IdentifiedStructType)
                    and val.type.pointee == target_ty.pointee):
                return self.builder.load(val, name=f"{name}_load")
            return self.builder.bitcast(val, target_ty, name=f"{name}_bitcast")

        if (isinstance(val.type, ir.IdentifiedStructType)
                and isinstance(target_ty, ir.PointerType)
                and val.type == target_ty.pointee):
            tmp = self.builder.alloca(val.type, name=f"{name}_struct_tmp")
            self.builder.store(val, tmp)
            return tmp

        try:
            return self.builder.bitcast(val, target_ty, name=f"{name}_final_cast")
        except Exception:
            return val

    # ------------------------------------------------------------------
    # Assign
    # ------------------------------------------------------------------
    def visit_AssignStmt(self, node):
        val = self.visit(node.value)

        if hasattr(node.target, 'name'):
            gv = getattr(self, 'global_mut_vars', {}).get(node.target.name)
            if gv is not None:
                target_ty = gv.type.pointee
                val = self._coerce_val_to(val, target_ty, name=node.target.name)
                self.builder.store(val, gv)
                return

            ptr = self.symbol_table.get(node.target.name)
            if ptr:
                target_ty = ptr.type.pointee
                val = self._coerce_val_to(val, target_ty, name=node.target.name)
                self.builder.store(val, ptr)

        elif hasattr(node.target, 'member'):
            obj_val = self.visit(node.target.obj)
            if isinstance(obj_val.type, ir.PointerType) and isinstance(obj_val.type.pointee, ir.IdentifiedStructType):
                struct_name = obj_val.type.pointee.name
                field_idx = self.struct_fields[struct_name].get(node.target.member)
                if field_idx is not None:
                    elem_ptr = self.builder.gep(obj_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, field_idx)])
                    target_ty = elem_ptr.type.pointee

                    if val.type != target_ty:
                        if isinstance(val.type, ir.PointerType) and isinstance(target_ty, ir.PointerType):
                            val = self.builder.bitcast(val, target_ty, name="member_ptr_cast")
                        elif isinstance(target_ty, ir.PointerType) and val.type == self.i64_ty:
                            val = self.builder.inttoptr(val, target_ty, name="member_int_to_ptr")
                        elif target_ty == self.i64_ty and isinstance(val.type, ir.PointerType):
                            val = self.builder.ptrtoint(val, self.i64_ty, name="member_ptr_to_int")

                    if (isinstance(val.type, ir.PointerType)
                        and isinstance(val.type.pointee, ir.IdentifiedStructType)
                        and val.type.pointee == target_ty):
                        val = self.builder.load(val, name="member_load_val")

                    if val.type != target_ty:
                        if isinstance(val.type, ir.PointerType) and isinstance(target_ty, ir.PointerType):
                            val_int = self.builder.ptrtoint(val, self.i64_ty, name="member_force_int")
                            val = self.builder.inttoptr(val_int, target_ty, name="member_force_ptr")
                        elif target_ty == self.i64_ty:
                            val = self.builder.ptrtoint(val, self.i64_ty, name="member_force_int2")
                        elif isinstance(target_ty, ir.PointerType):
                            val = self.builder.inttoptr(val, target_ty, name="member_force_ptr2")

                    self.builder.store(val, elem_ptr)

        elif hasattr(node.target, 'index'):
            arr_val = self.visit(node.target.array)
            idx_val = self.visit(node.target.index)
            if isinstance(arr_val.type, ir.PointerType):
                if isinstance(arr_val.type.pointee, ir.ArrayType):
                    elem_ptr = self.builder.gep(arr_val, [ir.Constant(self.i32_ty, 0), idx_val])
                else:
                    elem_ptr = self.builder.gep(arr_val, [idx_val])

                elem_ty = elem_ptr.type.pointee

                if isinstance(elem_ty, ir.IntType) and elem_ty.width < 64:
                    if isinstance(val.type, ir.IntType):
                        if val.type.width > elem_ty.width:
                            val = self.builder.trunc(val, elem_ty, name="idx_trunc")
                        elif val.type.width < elem_ty.width:
                            val = self.builder.sext(val, elem_ty, name="idx_sext")
                    else:
                        if isinstance(val.type, ir.PointerType):
                            val = self.builder.ptrtoint(val, self.i64_ty, name="idx_ptrtoint")
                            val = self.builder.trunc(val, elem_ty, name="idx_trunc")
                        elif val.type == self.f64_ty:
                            val = self.builder.fptosi(val, elem_ty, name="idx_fptosi")
                elif elem_ty == self.f64_ty and val.type == self.i64_ty:
                    val = self.builder.sitofp(val, self.f64_ty, name="idx_sitofp")
                elif isinstance(elem_ty, ir.PointerType) and val.type == self.i64_ty:
                    val = self.builder.inttoptr(val, elem_ty, name="idx_inttoptr")
                elif elem_ty != val.type:
                    elem_ptr_int = self.builder.ptrtoint(elem_ptr, self.i64_ty, name="idx_elem_int")
                    elem_ptr = self.builder.inttoptr(elem_ptr_int, val.type.as_pointer(), name="idx_elem_cast")

                self.builder.store(val, elem_ptr)

    # ------------------------------------------------------------------
    # Return: emite TODOS os defers (do bloco mais interno ao topo)
    # ------------------------------------------------------------------
    def visit_ReturnStmt(self, node):
        if self.builder.block.is_terminated:
            return

        ret_ty = self.functions_table[self.current_func_name][1].return_type

        if ret_ty != self.void_ty and self._try_tail_call(node):
            return

        if ret_ty == self.void_ty:
            for v in node.values:
                self.visit(v)
            self._emit_all_defers()
            self.builder.ret_void()
            return

        if not node.values:
            self._emit_all_defers()
            self.builder.ret_void()
            return

        val = self.visit(node.values[0])

        if val.type != ret_ty:
            if ret_ty == self.f64_ty and val.type == self.i64_ty:
                val = self.builder.sitofp(val, self.f64_ty, name="ret_cast")
            elif ret_ty == self.i64_ty and val.type == self.f64_ty:
                val = self.builder.fptosi(val, self.i64_ty, name="ret_cast")
            elif isinstance(ret_ty, ir.PointerType) and val.type == self.i64_ty:
                val = self.builder.inttoptr(val, ret_ty, name="ret_cast")
            elif ret_ty == self.i64_ty and isinstance(val.type, ir.PointerType):
                val = self.builder.ptrtoint(val, self.i64_ty, name="ret_cast")
            elif isinstance(ret_ty, ir.PointerType) and isinstance(val.type, ir.PointerType):
                if ret_ty != val.type:
                    val = self.builder.bitcast(val, ret_ty, name="ret_ptr_cast")
            elif isinstance(val.type, ir.PointerType) and isinstance(val.type.pointee, ir.IdentifiedStructType):
                if val.type.pointee == ret_ty:
                    val = self.builder.load(val, name="ret_struct_load")

        self._emit_all_defers()
        self.builder.ret(val)

    def visit_DestructureStmt(self, node):
        val = self.visit(node.value)
        if isinstance(val.type, ir.PointerType) and isinstance(val.type.pointee, ir.IdentifiedStructType):
            for i, name in enumerate(node.names):
                elem_ptr = self.builder.gep(val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)])
                field_val = self.builder.load(elem_ptr, name=name)
                var_ptr = self.builder.alloca(field_val.type, name=name)
                self.builder.store(field_val, var_ptr)
                self.symbol_table[name] = var_ptr

    def visit_DeferStmt(self, node):
        if not hasattr(self, 'defer_stack'):
            self.defer_stack = []
        self.defer_stack.append(list(node.body))

    def visit_AssertStmt(self, node):
        cond = self.visit(node.condition)
        if cond.type != ir.IntType(1):
            cond = self.builder.icmp_signed("!=", cond, ir.Constant(cond.type, 0), name="assert_cond")

        ok_bb   = self.builder.append_basic_block(name="assert_ok")
        fail_bb = self.builder.append_basic_block(name="assert_fail")

        self.builder.cbranch(cond, ok_bb, fail_bb)

        self.builder.position_at_end(fail_bb)
        fflush_fn = self.module.globals.get("fflush")
        if fflush_fn is None:
            fflush_ty = ir.FunctionType(ir.IntType(32), [self.i8_ty.as_pointer()])
            fflush_fn = ir.Function(self.module, fflush_ty, name="fflush")
        self.builder.call(fflush_fn, [ir.Constant(self.i8_ty.as_pointer(), None)])

        abort_fn = self.module.globals.get("abort")
        if abort_fn is None:
            abort_ty = ir.FunctionType(ir.VoidType(), [])
            abort_fn = ir.Function(self.module, abort_ty, name="abort")
        self.builder.call(abort_fn, [])
        self.builder.unreachable()

        self.builder.position_at_end(ok_bb)

    def visit_BenchStmt(self, node):
        start = self._begin_scope()
        for stmt in node.body:
            if self.builder.block.is_terminated:
                break
            self.visit(stmt)
        self._end_scope(start)

    def visit_BreakStmt(self, node):
        if not getattr(self, 'loop_stack', None):
            return
        _, break_bb, scope_start = self.loop_stack[-1]
        self._emit_scope_defers(scope_start)      # NÃO deleta
        if not self.builder.block.is_terminated:
            self.builder.branch(break_bb)

    def visit_ContinueStmt(self, node):
        if not getattr(self, 'loop_stack', None):
            return
        continue_bb, _, scope_start = self.loop_stack[-1]
        self._emit_scope_defers(scope_start)      # NÃO deleta
        if not self.builder.block.is_terminated:
            self.builder.branch(continue_bb)

    def _try_tail_call(self, node):
        """TCO para self-recursion direta.

        Emite os defers pendentes antes do branch de volta ao
        body_bb — mesma semântica de `return` normal (Sprint 8b).
        O corpo re-executa e re-empilha seus defers a cada iteração.
        """
        from ...ast import CallExpr as _CallExpr, VariableExpr as _VarExpr
        if len(node.values) != 1:
            return False
        val = node.values[0]
        if not isinstance(val, _CallExpr):
            return False
        if not isinstance(val.callee, _VarExpr):
            return False
        if val.callee.name != getattr(self, 'current_func_name', None):
            return False
        body_bb = getattr(self, 'current_body_bb', None)
        if body_bb is None:
            return False

        fn_def = self.function_defs.get(self.current_func_name)
        if fn_def is None:
            return False

        func, func_type = self.functions_table[self.current_func_name]

        if len(val.args) != len(fn_def.params):
            return False

        arg_vals = []
        for i, arg_node in enumerate(val.args):
            v = self.visit(arg_node)
            expected = func_type.args[i] if i < len(func_type.args) else None
            if expected is not None and v.type != expected:
                v = self._coerce_arg(v, expected, suffix=f"_tco{i}")
            arg_vals.append(v)

        for i, p in enumerate(fn_def.params):
            ptr = self.symbol_table.get(p.name)
            if ptr is None:
                return False
            self.builder.store(arg_vals[i], ptr)

        # NOVO (Sprint 8d): emite defers pendentes antes do branch de
        # TCO. Eles representam "o frame está sendo encerrado"
        # semanticamente — mesma regra de `return self(...)` sem TCO.
        # Limpa a pilha para que a próxima iteração comece com estado
        # fresco (o corpo re-executa `defer ...` que re-empilha).
        self._emit_all_defers()
        if self.builder.block.is_terminated:
            # defer fez return/abort — já terminou o bloco.
            return True

        self.builder.branch(body_bb)
        return True