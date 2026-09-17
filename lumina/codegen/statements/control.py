from llvmlite import ir
from ...ast import BinaryExpr, VariableExpr, ArrayExpr


class ControlMixin:

    def visit_IfStmt(self, node):
        cond_val = self.visit(node.condition)
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(cond_val.type, 0), name="if_cond")

        then_bb = self.builder.append_basic_block(name="if_then")
        else_bb = self.builder.append_basic_block(name="if_else")
        end_bb = self.builder.append_basic_block(name="if_end")

        self.builder.cbranch(cond_val, then_bb, else_bb)

        self.builder.position_at_end(then_bb)
        start_then = self._begin_scope()
        for stmt in node.then_body:
            if self.builder.block.is_terminated:
                break
            self.visit(stmt)
        if not self.builder.block.is_terminated:
            self._end_scope(start_then)
        else:
            del self.defer_stack[start_then:]
        then_term = self.builder.block.is_terminated
        if not then_term:
            self.builder.branch(end_bb)

        self.builder.position_at_end(else_bb)
        if node.else_body:
            start_else = self._begin_scope()
            for stmt in node.else_body:
                if self.builder.block.is_terminated:
                    break
                self.visit(stmt)
            if not self.builder.block.is_terminated:
                self._end_scope(start_else)
            else:
                del self.defer_stack[start_else:]
        else_term = self.builder.block.is_terminated
        if not else_term:
            self.builder.branch(end_bb)

        if then_term and else_term:
            self.builder.position_at_end(end_bb)
            self.builder.unreachable()
            return

        self.builder.position_at_end(end_bb)

    def visit_WhileStmt(self, node):
        cond_bb = self.builder.append_basic_block(name="while_cond")
        body_bb = self.builder.append_basic_block(name="while_body")
        end_bb = self.builder.append_basic_block(name="while_end")

        self.builder.branch(cond_bb)

        self.builder.position_at_end(cond_bb)
        cond_val = self.visit(node.condition)
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(cond_val.type, 0), name="while_cond")
        self.builder.cbranch(cond_val, body_bb, end_bb)

        self.builder.position_at_end(body_bb)
        start = self._begin_scope()
        self.loop_stack.append((cond_bb, end_bb, start))

        for stmt in node.body:
            if self.builder.block.is_terminated:
                break
            self.visit(stmt)
        self.loop_stack.pop()

        if not self.builder.block.is_terminated:
            self._end_scope(start)
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_bb)

        self.builder.position_at_end(end_bb)

    def visit_ForStmt(self, node):
        # `for x in arr:` — iterable que NÃO é um range `..`.
        if node.iterable is not None and not (
            isinstance(node.iterable, BinaryExpr) and node.iterable.op == '..'
        ):
            return self._visit_for_iterable(node)

        # `for i in a..b:` — comportamento original.
        if node.iterable is not None and isinstance(node.iterable, BinaryExpr) and node.iterable.op == '..':
            start_val = self.visit(node.iterable.left)
            end_val = self.visit(node.iterable.right)
        else:
            start_val = self.visit(node.start) if node.start else ir.Constant(self.i64_ty, 0)
            end_val = self.visit(node.end) if node.end else ir.Constant(self.i64_ty, 0)

        if start_val.type != self.i64_ty:
            start_val = self.builder.fptosi(start_val, self.i64_ty, name="for_start_cast")
        if end_val.type != self.i64_ty:
            end_val = self.builder.fptosi(end_val, self.i64_ty, name="for_end_cast")

        var_ptr = self.builder.alloca(self.i64_ty, name=node.var_name)
        self.symbol_table[node.var_name] = var_ptr
        self.var_types[node.var_name] = "int"

        self.builder.store(start_val, var_ptr)

        cond_bb = self.builder.append_basic_block(name="for_cond")
        body_bb = self.builder.append_basic_block(name="for_body")
        inc_bb  = self.builder.append_basic_block(name="for_inc")
        end_bb  = self.builder.append_basic_block(name="for_end")

        self.builder.branch(cond_bb)

        self.builder.position_at_end(cond_bb)
        current_val = self.builder.load(var_ptr, name="for_curr")
        cond = self.builder.icmp_signed("<", current_val, end_val, name="for_cond")
        self.builder.cbranch(cond, body_bb, end_bb)

        self.builder.position_at_end(body_bb)
        start = self._begin_scope()
        self.loop_stack.append((inc_bb, end_bb, start))

        for stmt in node.body:
            if self.builder.block.is_terminated:
                break
            self.visit(stmt)
        self.loop_stack.pop()

        if not self.builder.block.is_terminated:
            self._end_scope(start)
        if not self.builder.block.is_terminated:
            self.builder.branch(inc_bb)

        self.builder.position_at_end(inc_bb)
        cur2 = self.builder.load(var_ptr, name="for_curr_inc")
        next_val = self.builder.add(cur2, ir.Constant(self.i64_ty, 1), name="for_next")
        self.builder.store(next_val, var_ptr)
        self.builder.branch(cond_bb)

        self.builder.position_at_end(end_bb)

    def _visit_for_iterable(self, node):
        """`for x in <iterable>:` — itera sobre cada elemento.

        Casos:
          1. Variável com array literal conhecido (via `array_lengths`):
             `let arr = [1, 2, 3]; for x in arr` — N conhecido, GEP simples.
          2. Array literal inline: `for x in [1, 2, 3]` — `alloca` de
             `ArrayType`, `pointee.count` = N, GEP duplo `[0, idx]`.
          3. String: `for c in "abc"` — strlen em runtime, GEP simples,
             elemento `i8`.
          4. Outros tipos: loop vazio (N=0) — não crasha.
        """

        # --- Caso 0: `for i, x in arr` — índice + valor ---
        if "," in node.var_name:
            idx_name, val_name = node.var_name.split(",", 1)
            idx_name = idx_name.strip()
            val_name = val_name.strip()

            lengths = getattr(self, 'array_lengths', {})
            if isinstance(node.iterable, VariableExpr) and node.iterable.name in lengths:
                n = lengths[node.iterable.name]
                arr_val = self.visit(node.iterable)
                len_val = ir.Constant(self.i64_ty, n)
                elem_ty = self.i64_ty
                use_array_gep = False
            else:
                arr_val = self.visit(node.iterable)
                if (isinstance(arr_val.type, ir.PointerType)
                        and isinstance(arr_val.type.pointee, ir.ArrayType)):
                    n = arr_val.type.pointee.count
                    elem_ty = arr_val.type.pointee.element
                    len_val = ir.Constant(self.i64_ty, n)
                    use_array_gep = True
                elif arr_val.type == self.voidptr_ty:
                    len_val = self.builder.call(self.strlen, [arr_val], name="forin_strlen")
                    elem_ty = self.i8_ty
                    use_array_gep = False
                else:
                    len_val = ir.Constant(self.i64_ty, 0)
                    elem_ty = self.i64_ty
                    use_array_gep = False

            idx_ptr = self.builder.alloca(self.i64_ty, name=f"__for_idx_{idx_name}")
            self.builder.store(ir.Constant(self.i64_ty, 0), idx_ptr)

            elem_ptr = self.builder.alloca(elem_ty, name=val_name)
            self.symbol_table[val_name] = elem_ptr
            self.var_types[val_name] = self._llvm_ty_to_str(elem_ty)

            # O índice é o próprio idx_ptr.
            idx_slot = self.builder.alloca(self.i64_ty, name=idx_name)
            self.symbol_table[idx_name] = idx_slot
            self.var_types[idx_name] = "int"

            cond_bb = self.builder.append_basic_block(name="forin_cond")
            body_bb = self.builder.append_basic_block(name="forin_body")
            inc_bb  = self.builder.append_basic_block(name="forin_inc")
            end_bb  = self.builder.append_basic_block(name="forin_end")

            self.builder.branch(cond_bb)

            self.builder.position_at_end(cond_bb)
            cur = self.builder.load(idx_ptr, name="forin_cur")
            self.builder.store(cur, idx_slot)
            cond = self.builder.icmp_signed("<", cur, len_val, name="forin_cond")
            self.builder.cbranch(cond, body_bb, end_bb)

            self.builder.position_at_end(body_bb)
            if use_array_gep:
                ep = self.builder.gep(
                    arr_val, [ir.Constant(self.i32_ty, 0), cur],
                    name="forin_ep",
                )
            else:
                ep = self.builder.gep(arr_val, [cur], name="forin_ep")
            raw = self.builder.load(ep, name="forin_elem")
            raw = self._normalize_loaded(raw, name_hint="forin")
            if raw.type != elem_ty:
                if isinstance(raw.type, ir.IntType) and isinstance(elem_ty, ir.IntType):
                    if raw.type.width > elem_ty.width:
                        raw = self.builder.trunc(raw, elem_ty, name="forin_trunc")
                    elif raw.type.width < elem_ty.width:
                        raw = self.builder.zext(raw, elem_ty, name="forin_zext")
            self.builder.store(raw, elem_ptr)

            start = self._begin_scope()
            self.loop_stack.append((inc_bb, end_bb, start))
            for stmt in node.body:
                if self.builder.block.is_terminated:
                    break
                self.visit(stmt)
            self.loop_stack.pop()
            if not self.builder.block.is_terminated:
                self._end_scope(start)
            if not self.builder.block.is_terminated:
                self.builder.branch(inc_bb)

            self.builder.position_at_end(inc_bb)
            cur2 = self.builder.load(idx_ptr, name="forin_cur_inc")
            nxt = self.builder.add(cur2, ir.Constant(self.i64_ty, 1), name="forin_next")
            self.builder.store(nxt, idx_ptr)
            self.builder.branch(cond_bb)

            self.builder.position_at_end(end_bb)
            return

        # --- Caso 1: variável com array literal registrado ---
        if isinstance(node.iterable, VariableExpr):
            lengths = getattr(self, 'array_lengths', {})
            if node.iterable.name in lengths:
                n = lengths[node.iterable.name]
                arr_val = self.visit(node.iterable)
                len_val = ir.Constant(self.i64_ty, n)
                elem_ty = self.i64_ty
                return self._emit_forin_loop(
                    node, arr_val, len_val, elem_ty, use_array_gep=False
                )

        arr_val = self.visit(node.iterable)

        # --- Caso 2: array literal inline (alloca de ArrayType) ---
        if isinstance(arr_val.type, ir.PointerType) and isinstance(arr_val.type.pointee, ir.ArrayType):
            n = arr_val.type.pointee.count
            elem_ty = arr_val.type.pointee.element
            return self._emit_forin_loop(
                node, arr_val, ir.Constant(self.i64_ty, n), elem_ty,
                use_array_gep=True,
            )

        # --- Caso 3: string ---
        if arr_val.type == self.voidptr_ty:
            len_val = self.builder.call(self.strlen, [arr_val], name="forin_strlen")
            return self._emit_forin_loop(
                node, arr_val, len_val, self.i8_ty, use_array_gep=False
            )

        # --- Caso 4: não suportado — loop vazio ---
        return self._emit_forin_loop(
            node, arr_val, ir.Constant(self.i64_ty, 0), self.i64_ty,
            use_array_gep=False,
        )

    def _emit_forin_loop(self, node, arr_val, len_val, elem_ty, use_array_gep):
        """Emite o loop `forin` propriamente dito.

        `arr_val`: ponteiro para o primeiro elemento ou array.
        `len_val`: i64 — número de iterações.
        `elem_ty`: tipo LLVM do elemento.
        `use_array_gep`: True se `arr_val` é `ArrayType*` (precisa GEP
            com 2 índices); False se é `i64*`/`i8*` (GEP com 1 índice).
        """
        idx_ptr = self.builder.alloca(self.i64_ty, name=f"__for_idx_{node.var_name}")
        self.builder.store(ir.Constant(self.i64_ty, 0), idx_ptr)

        elem_ptr = self.builder.alloca(elem_ty, name=node.var_name)
        self.symbol_table[node.var_name] = elem_ptr
        self.var_types[node.var_name] = self._llvm_ty_to_str(elem_ty)

        cond_bb = self.builder.append_basic_block(name="forin_cond")
        body_bb = self.builder.append_basic_block(name="forin_body")
        inc_bb  = self.builder.append_basic_block(name="forin_inc")
        end_bb  = self.builder.append_basic_block(name="forin_end")

        self.builder.branch(cond_bb)

        self.builder.position_at_end(cond_bb)
        cur = self.builder.load(idx_ptr, name="forin_cur")
        cond = self.builder.icmp_signed("<", cur, len_val, name="forin_cond")
        self.builder.cbranch(cond, body_bb, end_bb)

        self.builder.position_at_end(body_bb)
        if use_array_gep:
            ep = self.builder.gep(
                arr_val,
                [ir.Constant(self.i32_ty, 0), cur],
                name="forin_ep",
            )
        else:
            ep = self.builder.gep(arr_val, [cur], name="forin_ep")

        raw = self.builder.load(ep, name="forin_elem")
        raw = self._normalize_loaded(raw, name_hint="forin")
        if raw.type != elem_ty:
            if isinstance(raw.type, ir.IntType) and isinstance(elem_ty, ir.IntType):
                if raw.type.width > elem_ty.width:
                    raw = self.builder.trunc(raw, elem_ty, name="forin_trunc")
                elif raw.type.width < elem_ty.width:
                    raw = self.builder.zext(raw, elem_ty, name="forin_zext")
        self.builder.store(raw, elem_ptr)

        start = self._begin_scope()
        self.loop_stack.append((inc_bb, end_bb, start))
        for stmt in node.body:
            if self.builder.block.is_terminated:
                break
            self.visit(stmt)
        self.loop_stack.pop()
        if not self.builder.block.is_terminated:
            self._end_scope(start)
        if not self.builder.block.is_terminated:
            self.builder.branch(inc_bb)

        self.builder.position_at_end(inc_bb)
        cur2 = self.builder.load(idx_ptr, name="forin_cur_inc")
        nxt = self.builder.add(cur2, ir.Constant(self.i64_ty, 1), name="forin_next")
        self.builder.store(nxt, idx_ptr)
        self.builder.branch(cond_bb)

        self.builder.position_at_end(end_bb)