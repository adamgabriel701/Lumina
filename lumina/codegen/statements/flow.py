from llvmlite import ir


class FlowMixin:

    def visit_AssignStmt(self, node):
        val = self.visit(node.value)

        # Assign a variável
        if hasattr(node.target, 'name'):
            ptr = self.symbol_table.get(node.target.name)
            if ptr:
                if val.type == self.f64_ty and ptr.type.pointee == self.i64_ty:
                    val = self.builder.fptosi(val, self.i64_ty, name="assign_cast")
                self.builder.store(val, ptr)

        # Assign a campo (obj.member = val)
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

        # Assign a índice (arr[i] = val)
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
        for stmt in node.body:
            self.visit(stmt)

    def visit_AssertStmt(self, node):
        self.visit(node.condition)

    def visit_BenchStmt(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_BreakStmt(self, node):
        pass

    def visit_ContinueStmt(self, node):
        pass
