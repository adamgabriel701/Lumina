from llvmlite import ir

from ..ast import (
    VarDecl, AssignStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt,
    BreakStmt, ContinueStmt, MatchStmt, DeferStmt, AssertStmt,
    BenchStmt, DestructureStmt, CallExpr, BinaryExpr,
)
from ..ast.visitor import NodeVisitor


class StatementCodegen(NodeVisitor):

    def _zero_and_store_struct(self, ptr, struct_ty, name):
        """Aloca storage pra uma struct sem valor inicial e zera todos os campos.

        Dois casos:
          * ptr.type.pointee == struct_ty*  → scheme padrão: aloca storage e guarda ponteiro
          * ptr.type.pointee == struct_ty   → ptr guarda a struct por valor: store direto
        """
        # Valor zero da struct
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

        # Caso: ptr já guarda a struct por valor
        if ptr_pointee == struct_ty:
            if zero_val is not None:
                self.builder.store(zero_val, ptr)
            return

        # Caso normal: aloca storage no stack e aponta ptr pra ele
        storage = self.builder.alloca(struct_ty, name=name + "_storage")
        if zero_val is not None:
            try:
                self.builder.store(zero_val, storage)
            except Exception:
                pass

        if storage.type != ptr_pointee:
            if isinstance(ptr_pointee, ir.PointerType):
                storage = self.builder.bitcast(storage, ptr_pointee, name=name + "_cast")
            else:
                # Fallback: converte pra inteiro e de volta
                storage_int = self.builder.ptrtoint(storage, self.i64_ty, name=name + "_int")
                storage = self.builder.inttoptr(storage_int, ptr_pointee, name=name + "_cast")
        self.builder.store(storage, ptr)

    def visit_VarDecl(self, node):
        val = self.visit(node.value) if node.value else None
        var_type = node.var_type if node.var_type else "int"

        is_alloc_call = (
            isinstance(node.value, CallExpr)
            and getattr(node.value.callee, 'name', None) in ("alloc", "alloc_bytes")
        )

        # NOVO: trata struct genérica ("Box<int>") como não-genérica
        is_struct_like = (
            (var_type in self.struct_types and not var_type.endswith("*"))
            or ("<" in var_type and var_type.split("<")[0] in self.struct_defs)
        )

        if is_alloc_call:
            llvm_ty = self.i64_ty.as_pointer()
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
            # Struct sem valor → storage real + zero
            struct_ty = self.get_llvm_type(var_type)
            self._zero_and_store_struct(ptr, struct_ty, node.name)

        else:
            # Sem valor e sem struct: zera o slot
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

        if is_alloc_call:
            self.heap_allocs.add(node.name)

    def visit_AssignStmt(self, node):
        val = self.visit(node.value)

        if hasattr(node.target, 'name'):
            ptr = self.symbol_table.get(node.target.name)
            if ptr:
                if val.type == self.f64_ty and ptr.type.pointee == self.i64_ty:
                    val = self.builder.fptosi(val, self.i64_ty, name="assign_cast")
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

                if val.type != elem_ptr.type.pointee:
                    elem_ptr_int = self.builder.ptrtoint(elem_ptr, self.i64_ty, name="idx_elem_int")
                    elem_ptr = self.builder.inttoptr(elem_ptr_int, val.type.as_pointer(), name="idx_elem_cast")
                self.builder.store(val, elem_ptr)

    def visit_ReturnStmt(self, node):
        if self.builder.block.is_terminated:
            return

        if not node.values:
            self.builder.ret_void()
            return

        val = self.visit(node.values[0])
        ret_ty = self.functions_table[self.current_func_name][1].return_type

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
        self.builder.ret(val)

    def visit_IfStmt(self, node):
        cond_val = self.visit(node.condition)
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(cond_val.type, 0), name="if_cond")

        then_bb = self.builder.append_basic_block(name="if.then")
        else_bb = self.builder.append_basic_block(name="if.else")
        end_bb = self.builder.append_basic_block(name="if.end")

        self.builder.cbranch(cond_val, then_bb, else_bb)

        self.builder.position_at_end(then_bb)
        for stmt in node.then_body:
            self.visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)

        self.builder.position_at_end(else_bb)
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)

        self.builder.position_at_end(end_bb)

    def visit_WhileStmt(self, node):
        cond_bb = self.builder.append_basic_block(name="while.cond")
        body_bb = self.builder.append_basic_block(name="while.body")
        end_bb = self.builder.append_basic_block(name="while.end")

        self.builder.branch(cond_bb)

        self.builder.position_at_end(cond_bb)
        cond_val = self.visit(node.condition)
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(cond_val.type, 0), name="while_cond")
        self.builder.cbranch(cond_val, body_bb, end_bb)

        self.builder.position_at_end(body_bb)
        for stmt in node.body:
            self.visit(stmt)

        if not self.builder.block.is_terminated:
            self.builder.branch(cond_bb)

        self.builder.position_at_end(end_bb)

    def visit_ForStmt(self, node):
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

        cond_bb = self.builder.append_basic_block(name="for.cond")
        body_bb = self.builder.append_basic_block(name="for.body")
        end_bb = self.builder.append_basic_block(name="for.end")

        self.builder.branch(cond_bb)

        self.builder.position_at_end(cond_bb)
        current_val = self.builder.load(var_ptr, name="for_curr")
        cond = self.builder.icmp_signed("<", current_val, end_val, name="for_cond")
        self.builder.cbranch(cond, body_bb, end_bb)

        self.builder.position_at_end(body_bb)
        for stmt in node.body:
            self.visit(stmt)

        if not self.builder.block.is_terminated:
            next_val = self.builder.add(current_val, ir.Constant(self.i64_ty, 1), name="for_next")
            self.builder.store(next_val, var_ptr)
            self.builder.branch(cond_bb)

        self.builder.position_at_end(end_bb)

    def visit_MatchStmt(self, node):
        # MatchStmt.cases é 4-tuple (variant, binding, guard, body).
        has_guard = any(len(c) >= 4 and c[2] is not None for c in node.cases)

        cond_val = self.visit(node.condition)
        end_bb = self.builder.append_basic_block(name="match.end")

        if has_guard:
            self._codegen_match_with_guard(node, cond_val, end_bb)
            return

        # Caso 1: match sobre i64 (switch clássico)
        if cond_val.type == self.i64_ty:
            default_bb = self.builder.append_basic_block(name="match.default")
            sw = self.builder.switch(cond_val, default_bb)

            for case in node.cases:
                if len(case) == 4:
                    val_node, var_name, _guard, body = case
                else:
                    val_node, var_name, body = case
                case_bb = self.builder.append_basic_block(name="match.case")
                if isinstance(val_node, str):
                    try:
                        val = ir.Constant(self.i64_ty, int(val_node))
                    except ValueError:
                        continue
                else:
                    val = self.visit(val_node)
                sw.add_case(val, case_bb)
                self.builder.position_at_end(case_bb)
                if var_name:
                    if isinstance(var_name, list):
                        for name in var_name:
                            var_ptr = self.builder.alloca(self.i64_ty, name=name)
                            self.symbol_table[name] = var_ptr
                    else:
                        var_ptr = self.builder.alloca(self.i64_ty, name=var_name)
                        self.symbol_table[var_name] = var_ptr
                for stmt in body:
                    self.visit(stmt)
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)

            self.builder.position_at_end(default_bb)
            if node.default:
                for stmt in node.default:
                    self.visit(stmt)
            if not self.builder.block.is_terminated:
                self.builder.branch(end_bb)
            self.builder.position_at_end(end_bb)
            return

        # Caso 2: match sobre enum (struct {i32 tag, i64 payload})
        if isinstance(cond_val.type, ir.PointerType) and isinstance(cond_val.type.pointee, ir.IdentifiedStructType):
            struct_name = cond_val.type.pointee.name
            if struct_name not in self.struct_defs:
                return
            struct_def = self.struct_defs[struct_name]
            if not hasattr(struct_def, 'variants'):
                return

            variant_map = {v[0]: i for i, v in enumerate(struct_def.variants)}

            tag_ptr = self.builder.gep(cond_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)], name="match_tag_ptr")
            tag_val = self.builder.load(tag_ptr, name="match_tag")

            payload_ptr = self.builder.gep(cond_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)], name="match_payload_ptr")

            default_bb = self.builder.append_basic_block(name="match.default")
            sw = self.builder.switch(tag_val, default_bb)

            for case in node.cases:
                if len(case) == 4:
                    variant_name, var_name, _guard, body = case
                else:
                    variant_name, var_name, body = case
                if variant_name not in variant_map:
                    continue
                case_idx = variant_map[variant_name]
                case_bb = self.builder.append_basic_block(name=f"match.{variant_name.lower()}")
                sw.add_case(ir.Constant(self.i32_ty, case_idx), case_bb)
                self.builder.position_at_end(case_bb)

                if var_name:
                    if isinstance(var_name, list):
                        for i, name in enumerate(var_name):
                            pp = self.builder.gep(
                                cond_val,
                                [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i + 1)],
                                name=f"payload_ptr_{name}",
                            )
                            payload_val = self.builder.load(pp, name=f"payload_{name}")
                            var_ptr = self.builder.alloca(self.i64_ty, name=name)
                            self.builder.store(payload_val, var_ptr)
                            self.symbol_table[name] = var_ptr
                    else:
                        payload_val = self.builder.load(payload_ptr, name="payload_load")
                        var_ptr = self.builder.alloca(self.i64_ty, name=var_name)
                        self.builder.store(payload_val, var_ptr)
                        self.symbol_table[var_name] = var_ptr

                for stmt in body:
                    self.visit(stmt)
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_bb)

            self.builder.position_at_end(default_bb)
            if node.default:
                for stmt in node.default:
                    self.visit(stmt)
            if not self.builder.block.is_terminated:
                self.builder.branch(end_bb)
            self.builder.position_at_end(end_bb)
            return

    def _codegen_match_with_guard(self, node, cond_val, end_bb):
        """Match com guards: usa if/else encadeado.

        Quando o case é self-binding (`case n if n > 10:`), o binding `n` precisa
        estar disponível DENTRO do guard, então declaramos o binding ANTES de
        avaliar a condição.
        """
        for i, case in enumerate(node.cases):
            if len(case) == 4:
                variant, binding, guard, body = case
            else:
                variant, binding, body = case
                guard = None

            test_bb = self.builder.append_basic_block(name=f"match.guard_test.{i}")
            body_bb = self.builder.append_basic_block(name=f"match.guard_body.{i}")
            next_bb = self.builder.append_basic_block(name=f"match.guard_next.{i}")

            self.builder.branch(test_bb)
            self.builder.position_at_end(test_bb)

            # Self-binding: `n` recebe cond_val aqui, antes do guard
            if variant is None and binding:
                binding_name = binding[0] if isinstance(binding, list) else binding
                var_ptr = self.builder.alloca(cond_val.type, name=binding_name)
                self.builder.store(cond_val, var_ptr)
                self.symbol_table[binding_name] = var_ptr

            if variant is None:
                pattern_match = ir.Constant(ir.IntType(1), 1)
            elif cond_val.type == self.i64_ty:
                if isinstance(variant, str):
                    try:
                        case_val = ir.Constant(self.i64_ty, int(variant))
                        pattern_match = self.builder.icmp_signed("==", cond_val, case_val, name=f"match_eq_{i}")
                    except ValueError:
                        self.builder.branch(next_bb)
                        self.builder.position_at_end(next_bb)
                        continue
                else:
                    case_val = self.visit(variant)
                    pattern_match = self.builder.icmp_signed("==", cond_val, case_val, name=f"match_eq_{i}")
            else:
                pattern_match = ir.Constant(ir.IntType(1), 1)

            if guard:
                self.builder.position_at_end(test_bb)
                guard_val = self.visit(guard)
                if guard_val.type != ir.IntType(1):
                    guard_val = self.builder.icmp_signed("!=", guard_val, ir.Constant(guard_val.type, 0), name=f"guard_cond_{i}")
                final_cond = self.builder.and_(pattern_match, guard_val, name=f"match_and_{i}")
            else:
                final_cond = pattern_match

            self.builder.cbranch(final_cond, body_bb, next_bb)

            self.builder.position_at_end(body_bb)

            if binding and variant is not None:
                names = binding if isinstance(binding, list) else [binding]
                if isinstance(cond_val.type, ir.PointerType) and isinstance(cond_val.type.pointee, ir.IdentifiedStructType):
                    for i, name in enumerate(names):
                        pp = self.builder.gep(
                            cond_val,
                            [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i + 1)],
                            name=f"payload_ptr_{i}",
                        )
                        payload_val = self.builder.load(pp, name=f"payload_{i}")
                        var_ptr = self.builder.alloca(self.i64_ty, name=name)
                        self.builder.store(payload_val, var_ptr)
                        self.symbol_table[name] = var_ptr
                else:
                    for name in names:
                        var_ptr = self.builder.alloca(self.i64_ty, name=name)
                        self.builder.store(cond_val, var_ptr)
                        self.symbol_table[name] = var_ptr

            for stmt in body:
                self.visit(stmt)
            if not self.builder.block.is_terminated:
                self.builder.branch(end_bb)

            self.builder.position_at_end(next_bb)

        if node.default:
            for stmt in node.default:
                self.visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_bb)

        self.builder.position_at_end(end_bb)

    def visit_DeferStmt(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_AssertStmt(self, node):
        self.visit(node.condition)

    def visit_BenchStmt(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_DestructureStmt(self, node):
        val = self.visit(node.value)
        if isinstance(val.type, ir.PointerType) and isinstance(val.type.pointee, ir.IdentifiedStructType):
            for i, name in enumerate(node.names):
                elem_ptr = self.builder.gep(val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)])
                field_val = self.builder.load(elem_ptr, name=name)
                var_ptr = self.builder.alloca(field_val.type, name=name)
                self.builder.store(field_val, var_ptr)
                self.symbol_table[name] = var_ptr

    def visit_BreakStmt(self, node):
        pass

    def visit_ContinueStmt(self, node):
        pass

    def generic_visit(self, node):
        self.visit(node)