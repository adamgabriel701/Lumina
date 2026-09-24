from llvmlite import ir
from ...ast import (
    StringExpr, VariableExpr, StructLiteralExpr,
    StructLiteralField, LambdaExpr, TupleExpr,
)
from ..context import push_context
from ..constants import I64_BYTES, CLOSURE_BLOCK_SIZE   # ← NOVO


class AggregatesMixin:

    def _coerce_for_store(self, val, target_ty, name_hint="field"):
        if val.type == target_ty:
            return val

        if isinstance(val.type, ir.IntType) and isinstance(target_ty, ir.IntType):
            if val.type.width < target_ty.width:
                if val.type.width == 1:
                    return self.builder.zext(val, target_ty, name=f"{name_hint}_zext")
                return self.builder.sext(val, target_ty, name=f"{name_hint}_sext")
            return self.builder.trunc(val, target_ty, name=f"{name_hint}_trunc")

        if isinstance(val.type, ir.PointerType) and isinstance(target_ty, ir.IntType):
            return self.builder.ptrtoint(val, target_ty, name=f"{name_hint}_ptrtoint")
        if isinstance(val.type, ir.IntType) and isinstance(target_ty, ir.PointerType):
            return self.builder.inttoptr(val, target_ty, name=f"{name_hint}_inttoptr")

        if isinstance(val.type, ir.PointerType) and isinstance(target_ty, ir.PointerType):
            return self.builder.bitcast(val, target_ty, name=f"{name_hint}_bitcast")

        if val.type == self.i64_ty and target_ty == self.f64_ty:
            return self.builder.sitofp(val, target_ty, name=f"{name_hint}_sitofp")
        if val.type == self.f64_ty and target_ty == self.i64_ty:
            return self.builder.fptosi(val, target_ty, name=f"{name_hint}_fptosi")

        return val

    def visit_ArrayExpr(self, node):
        elem_ty = self.i64_ty
        if len(node.elements) > 0:
            first_val = self.visit(node.elements[0])
            elem_ty = first_val.type
            if not isinstance(elem_ty, ir.IntType):
                elem_ty = self.i64_ty

        array_ty = ir.ArrayType(elem_ty, len(node.elements))
        ptr = self.builder.alloca(array_ty, name="array_lit")

        for i, el in enumerate(node.elements):
            el_ptr = self.builder.gep(
                ptr,
                [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)],
                name=f"arr_el_{i}",
            )
            val = self.visit(el)
            val = self._coerce_for_store(val, elem_ty, name_hint=f"arr_{i}")
            self.builder.store(val, el_ptr)
        return ptr

    def visit_TupleExpr(self, node):
        """`(a, b, c)` — LiteralStructType heterogêneo."""
        elem_tys = []
        elem_vals = []
        for el in node.elements:
            v = self.visit(el)
            elem_tys.append(v.type)
            elem_vals.append(v)

        if not elem_tys:
            return ir.Constant(self.voidptr_ty, None)

        struct_ty = ir.LiteralStructType(elem_tys)
        ptr = self.builder.alloca(struct_ty, name="tuple_lit")
        for i, v in enumerate(elem_vals):
            ep = self.builder.gep(
                ptr,
                [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)],
                name=f"tuple_el_{i}_ptr",
            )
            self.builder.store(v, ep)
        return ptr

    def visit_StructLiteralExpr(self, node):
        struct_ty = self.get_llvm_type(node.struct_name)
        ptr = self.builder.alloca(struct_ty, name=node.struct_name.lower() + "_lit")

        for field in node.fields:
            if isinstance(field, tuple):
                fname, fexpr = field
            else:
                fname = field.name
                fexpr = field.value

            elem_index = self.struct_fields[node.struct_name].get(fname, 0)
            elem_ptr = self.builder.gep(
                ptr,
                [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, elem_index)],
                name=fname + "_ptr",
            )
            val = self.visit(fexpr)
            target_ty = elem_ptr.type.pointee
            val = self._coerce_for_store(val, target_ty, name_hint=fname)
            self.builder.store(val, elem_ptr)
        return ptr

    # ==================================================================
    # Lambdas
    # ==================================================================
    def visit_LambdaExpr(self, node):
        """Toda lambda é uma closure `{fn_ptr, env_ptr}`.

        Mesmo sem capturas, o env é uma struct vazia e o chamador
        sempre desempacka via `_call_closure`. Isso unifica o ABI de
        `fn` (fat pointer) e destrava closures com captura passadas
        como callbacks.
        """
        return self._emit_lambda_closure(node)

    def _emit_lambda_closure(self, node):
        """Lambda com capturas.

        Emite:
          1. Env struct (LiteralStructType) alocado no heap.
          2. Função `i64 __closure_N(i8* env, i64 a1, ..., i64 aN)`.
          3. Bloco closure `{i8* fn, i8* env}` alocado no heap.
        Retorna ponteiro para o bloco closure (i8*).

        Refatoração (Fase 1):
          Antes, 6 campos (`builder`, `symbol_table`, `var_types`,
          `defer_stack`, `closure_vars`, `current_func_name` +
          `current_body_bb`) eram salvos/restaurados manualmente, sem
          cobrir `_safe_mode` e sem garantia em caso de exceção. Agora
          usa `push_context`, que restaura TUDO (inclusive em exception).
        """
        free = list(node.free_vars)

        # Captura o conjunto de closure_vars do escopo EXTERNO antes de
        # entrar no novo contexto (push_context restaura este estado).
        outer_closure_vars = set(self.closure_vars)

        # 1) Tipos dos campos do env + ponteiros externos para os valores
        env_field_tys = []
        env_field_ptrs = []
        for name in free:
            outer_ptr = self.symbol_table.get(name)
            if outer_ptr is None:
                env_field_tys.append(self.i64_ty)
                env_field_ptrs.append(None)
            else:
                env_field_tys.append(outer_ptr.type.pointee)
                env_field_ptrs.append(outer_ptr)

        env_ty = ir.LiteralStructType(env_field_tys)

        # 2) Aloca env
        n = len(env_field_tys)
        env_size = max(CLOSURE_BLOCK_SIZE, I64_BYTES * n)
        env_raw = self.builder.call(
            self.malloc,
            [ir.Constant(self.i64_ty, env_size)],
            name=f"closure_env_{self.lambda_counter}",
        )
        env_typed = self.builder.bitcast(
            env_raw, env_ty.as_pointer(),
            name=f"closure_env_typed_{self.lambda_counter}",
        )

        # 3) Copia os valores capturados (usa symbol_table do ESCOPO EXTERNO)
        for i, name in enumerate(free):
            outer_ptr = env_field_ptrs[i]
            if outer_ptr is None:
                continue
            val = self.builder.load(outer_ptr, name=f"capture_{name}")
            field_ptr = self.builder.gep(
                env_typed,
                [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)],
                name=f"env_field_{name}",
            )
            self.builder.store(val, field_ptr)

        # 4) Emite a função
        func_name = f"__closure_{self.lambda_counter}"
        self.lambda_counter += 1

        param_tys = [self.voidptr_ty] + [self.i64_ty] * len(node.params)
        func_ty = ir.FunctionType(self.i64_ty, param_tys)
        func = ir.Function(self.module, func_ty, name=func_name)

        # Registra antes de emitir o corpo (permite recursão)
        self.functions_table[func_name] = (func, func_ty)

        block = func.append_basic_block(name="entry")
        inner_builder = ir.IRBuilder(block)

        # Herda `_safe_mode` do escopo externo (comportamento anterior)
        inherit_safe = getattr(self, '_safe_mode', False)

        with push_context(
            self,
            builder=inner_builder,
            symbol_table={},
            var_types={},
            current_func_name=func_name,
            current_body_bb=None,
            defer_stack=[],
            closure_vars=set(),
            _safe_mode=inherit_safe,
            _current_scc_slots=None,
            _current_scc_ids=None,
            _current_scc_id_slot=None,
            _current_scc_dispatch_bb=None,
            _fn_entry_block=block,              # PATCH
            _fn_return_type=self.i64_ty,        # PATCH
        ):
            # 4a) Bind env → symbol_table
            env_i8p = func.args[0]
            env_typed_inner = self.builder.bitcast(
                env_i8p, env_ty.as_pointer(), name="env_typed_inner",
            )
            for i, name in enumerate(free):
                field_ty = env_field_tys[i]
                fp = self.builder.gep(
                    env_typed_inner,
                    [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)],
                    name=f"env_{name}_ptr",
                )
                val = self.builder.load(fp, name=f"env_{name}")
                slot = self.builder.alloca(field_ty, name=name)
                self.builder.store(val, slot)
                self.symbol_table[name] = slot
                self.var_types[name] = self._llvm_ty_to_str(field_ty)
                if name in outer_closure_vars:
                    self.closure_vars.add(name)

            # 4b) Bind params (i64 → tipo real)
            for i, p in enumerate(node.params):
                p_name = p.name if hasattr(p, 'name') else p[0]
                p_type = p.type_ann if hasattr(p, 'type_ann') else p[1]
                p_ty = self.get_llvm_param_type(p_type)
                arg_val = func.args[i + 1]
                if arg_val.type != p_ty:
                    if p_ty == self.f64_ty:
                        arg_val = self.builder.sitofp(arg_val, p_ty, name=f"p_{p_name}_itof")
                    elif isinstance(p_ty, ir.PointerType):
                        arg_val = self.builder.inttoptr(arg_val, p_ty, name=f"p_{p_name}_itop")
                    elif isinstance(p_ty, ir.IntType) and p_ty.width < 64:
                        arg_val = self.builder.trunc(arg_val, p_ty, name=f"p_{p_name}_trunc")
                slot = self.builder.alloca(p_ty, name=p_name)
                self.builder.store(arg_val, slot)
                self.symbol_table[p_name] = slot
                self.var_types[p_name] = p_type

            # 4c) Body
            from ...ast.expressions import Expr as ExprBase
            for stmt in node.body:
                if isinstance(stmt, ExprBase):
                    val = self.visit(stmt)
                    if val.type != self.i64_ty:
                        val = self._coerce_for_store(
                            val, self.i64_ty, name_hint="closure_ret"
                        )
                    self.builder.ret(val)
                    break
                else:
                    self.visit(stmt)

            if not self.builder.block.is_terminated:
                self.builder.ret(ir.Constant(self.i64_ty, 0))

        # 5) Bloco closure {fn, env} — emitido no ESCOPO EXTERNO
        closure_raw = self.builder.call(
            self.malloc,
            [ir.Constant(self.i64_ty, CLOSURE_BLOCK_SIZE)],
            name=f"closure_{func_name}",
        )
        closure_i8pp = self.builder.bitcast(
            closure_raw, self.voidptr_ty.as_pointer(), name="closure_i8pp",
        )
        fn_as_ptr = self.builder.bitcast(func, self.voidptr_ty, name="fn_as_ptr")
        self.builder.store(fn_as_ptr, closure_i8pp)
        env_slot = self.builder.gep(
            closure_i8pp, [ir.Constant(self.i64_ty, 1)], name="env_slot",
        )
        self.builder.store(env_raw, env_slot)
        return closure_raw