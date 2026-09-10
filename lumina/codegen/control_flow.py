from llvmlite import ir
from ..ast import IfStmt, WhileStmt, ForStmt, MatchStmt, ArrayExpr, VariableExpr

class ControlFlowCodegen:
    def codegen_if(self, node: IfStmt):
        cond_val = self.codegen_expr(node.condition)
        if cond_val.type != ir.IntType(1): cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(self.i64_ty, 0), name="if_cond")
        then_bb = self.builder.append_basic_block(name="if.then")
        else_bb = self.builder.append_basic_block(name="if.else") if node.else_body else None
        end_bb = self.builder.append_basic_block(name="if.end")
        if else_bb: self.builder.cbranch(cond_val, then_bb, else_bb)
        else: self.builder.cbranch(cond_val, then_bb, end_bb)
        
        self.builder.position_at_end(then_bb)
        self.cleanup_vars.append(set())
        old_symbols = self.symbol_table.copy() # NOVO: Salva escopo
        for stmt in node.then_body: self.codegen_stmt(stmt)
        self.symbol_table = old_symbols       # NOVO: Restaura escopo
        if not self.builder.block.is_terminated: self.cleanup_block(self.cleanup_vars.pop()); self.builder.branch(end_bb)
        else: self.cleanup_vars.pop()
        
        if else_bb:
            self.builder.position_at_end(else_bb)
            self.cleanup_vars.append(set())
            old_symbols = self.symbol_table.copy() # NOVO: Salva escopo
            for stmt in node.else_body: self.codegen_stmt(stmt)
            self.symbol_table = old_symbols       # NOVO: Restaura escopo
            if not self.builder.block.is_terminated: self.cleanup_block(self.cleanup_vars.pop()); self.builder.branch(end_bb)
            else: self.cleanup_vars.pop()
        self.builder.position_at_end(end_bb)

    def codegen_while(self, node: WhileStmt):
        cond_bb, body_bb, end_bb = self.builder.append_basic_block(name="while.cond"), self.builder.append_basic_block(name="while.body"), self.builder.append_basic_block(name="while.end")
        self.builder.branch(cond_bb); self.builder.position_at_end(cond_bb)
        cond_val = self.codegen_expr(node.condition)
        if cond_val.type != ir.IntType(1): cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(self.i64_ty, 0), name="while_cond")
        self.builder.cbranch(cond_val, body_bb, end_bb)
        
        self.builder.position_at_end(body_bb)
        self.cleanup_vars.append(set())
        old_symbols = self.symbol_table.copy() # NOVO: Salva escopo
        old_continue, old_break = self.continue_block, self.break_block; self.continue_block, self.break_block = cond_bb, end_bb
        for stmt in node.body: self.codegen_stmt(stmt)
        self.continue_block, self.break_block = old_continue, old_break
        self.symbol_table = old_symbols       # NOVO: Restaura escopo
        if not self.builder.block.is_terminated: self.cleanup_block(self.cleanup_vars.pop()); self.builder.branch(cond_bb)
        else: self.cleanup_vars.pop()
        self.builder.position_at_end(end_bb)

    def codegen_for(self, node: ForStmt):
        if node.iterable is not None: return self.codegen_for_iter(node)
        old_symbols = self.symbol_table.copy() # NOVO: Salva escopo do for
        ptr = self.builder.alloca(self.i64_ty, name=node.var_name)
        start_val = self.codegen_expr(node.start)
        if start_val.type != self.i64_ty: start_val = self.builder.fptosi(start_val, self.i64_ty, name="for_start_int")
        self.builder.store(start_val, ptr); self.symbol_table[node.var_name] = ptr; self.var_types[node.var_name] = self.i64_ty
        end_val = self.codegen_expr(node.end)
        if end_val.type != self.i64_ty: end_val = self.builder.fptosi(end_val, self.i64_ty, name="for_end_int")
        cond_bb, body_bb, inc_bb, end_bb = self.builder.append_basic_block(name="for.cond"), self.builder.append_basic_block(name="for.body"), self.builder.append_basic_block(name="for.inc"), self.builder.append_basic_block(name="for.end")
        self.builder.branch(cond_bb); self.builder.position_at_end(cond_bb)
        curr_val = self.builder.load(ptr, name=node.var_name + "_val")
        self.builder.cbranch(self.builder.icmp_signed("<", curr_val, end_val, name="for_cond"), body_bb, end_bb)
        self.builder.position_at_end(body_bb); self.cleanup_vars.append(set())
        old_continue, old_break = self.continue_block, self.break_block; self.continue_block, self.break_block = inc_bb, end_bb
        for stmt in node.body: self.codegen_stmt(stmt)
        self.continue_block, self.break_block = old_continue, old_break
        if not self.builder.block.is_terminated: self.cleanup_block(self.cleanup_vars.pop()); self.builder.branch(inc_bb)
        else: self.cleanup_vars.pop()
        self.builder.position_at_end(inc_bb)
        self.builder.store(self.builder.add(curr_val, ir.Constant(self.i64_ty, 1), name="for_next"), ptr)
        self.builder.branch(cond_bb)
        self.symbol_table = old_symbols       # NOVO: Restaura escopo
        self.builder.position_at_end(end_bb)

    def codegen_for_iter(self, node: ForStmt):
        iterable_val = self.codegen_expr(node.iterable)
        length, arr_ptr = ir.Constant(self.i64_ty, 0), iterable_val
        if isinstance(node.iterable, VariableExpr) and node.iterable.name in self.array_sizes:
            arr_ptr = self.symbol_table.get(node.iterable.name); length = ir.Constant(self.i64_ty, self.array_sizes[node.iterable.name])
        elif isinstance(node.iterable, ArrayExpr):
            arr_ty = ir.ArrayType(self.i64_ty, len(node.iterable.elements)); arr_ptr = self.builder.alloca(arr_ty, name="iter_arr_tmp"); length = ir.Constant(self.i64_ty, len(node.iterable.elements))
            for i, el in enumerate(node.iterable.elements):
                el_val = self.codegen_expr(el)
                if el_val.type == self.f64_ty: el_val = self.builder.fptosi(el_val, self.i64_ty, name="to_int")
                self.builder.store(el_val, self.builder.gep(arr_ptr, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, i)]))
        elif isinstance(node.iterable, VariableExpr):
            info = self.var_types.get(node.iterable.name)
            if info and info == self.voidptr_ty: arr_ptr = iterable_val; length = self.builder.call(self.strlen, [iterable_val], name="iter_len")
            else: arr_ptr = iterable_val
        else: arr_ptr = iterable_val
        idx_ptr = self.builder.alloca(self.i64_ty, name="for_idx"); self.builder.store(ir.Constant(self.i64_ty, 0), idx_ptr)
        cond_bb, body_bb, inc_bb, end_bb = self.builder.append_basic_block(name="for.cond"), self.builder.append_basic_block(name="for.body"), self.builder.append_basic_block(name="for.inc"), self.builder.append_basic_block(name="for.end")
        self.builder.branch(cond_bb); self.builder.position_at_end(cond_bb)
        curr_idx = self.builder.load(idx_ptr, name="for_idx_val")
        self.builder.cbranch(self.builder.icmp_signed("<", curr_idx, length, name="for_cond"), body_bb, end_bb)
        self.builder.position_at_end(body_bb)
        idx_i32 = self.builder.trunc(curr_idx, self.i32_ty, name="for_idx_i32")
        if isinstance(arr_ptr.type, ir.PointerType) and isinstance(arr_ptr.type.pointee, ir.ArrayType): elem_ptr = self.builder.gep(arr_ptr, [ir.Constant(self.i32_ty, 0), idx_i32], name="for_elem_ptr")
        elif isinstance(arr_ptr.type, ir.PointerType): elem_ptr = self.builder.gep(arr_ptr, [idx_i32], name="for_elem_ptr")
        else: elem_ptr = self.builder.gep(arr_ptr, [idx_i32], name="for_elem_ptr")
        elem_val = self.builder.load(elem_ptr, name=node.var_name + "_val")
        if elem_val.type == self.i8_ty: elem_val = self.builder.zext(elem_val, self.i64_ty, name="char_to_int")
        var_ptr = self.builder.alloca(self.i64_ty, name=node.var_name); self.builder.store(elem_val, var_ptr)
        self.symbol_table[node.var_name] = var_ptr; self.var_types[node.var_name] = self.i64_ty
        self.cleanup_vars.append(set())
        old_continue, old_break = self.continue_block, self.break_block; self.continue_block, self.break_block = inc_bb, end_bb
        for stmt in node.body: self.codegen_stmt(stmt)
        self.continue_block, self.break_block = old_continue, old_break
        if not self.builder.block.is_terminated: self.cleanup_block(self.cleanup_vars.pop()); self.builder.branch(inc_bb)
        else: self.cleanup_vars.pop()
        self.builder.position_at_end(inc_bb)
        self.builder.store(self.builder.add(curr_idx, ir.Constant(self.i64_ty, 1), name="for_next"), idx_ptr)
        self.builder.branch(cond_bb); self.builder.position_at_end(end_bb)

    def codegen_match(self, node: MatchStmt):
        cond_val = self.codegen_expr(node.condition)
        
        # Se for um Enum (Pointer to IdentifiedStructType)
        if isinstance(cond_val.type, ir.PointerType) and isinstance(cond_val.type.pointee, ir.IdentifiedStructType):
            tag_ptr = self.builder.gep(cond_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 0)]); tag_val = self.builder.load(tag_ptr, name="enum_tag")
            default_bb, end_bb = self.builder.append_basic_block(name="match.default"), self.builder.append_basic_block(name="match.end")
            sw = self.builder.switch(tag_val, default_bb)
            
            for val_node, var_name, body in node.cases:
                from ..ast import VariableExpr
                if isinstance(val_node, VariableExpr):
                    variant_name = val_node.name
                    if variant_name not in self.variant_defs: raise Exception(f"Variante '{variant_name}' não existe.")
                    enum_name, index, _ = self.variant_defs[variant_name]
                    case_bb = self.builder.append_basic_block(name=f"match.case_{variant_name}"); sw.add_case(ir.Constant(self.i32_ty, index), case_bb)
                    
                    self.builder.position_at_end(case_bb)
                    if var_name:
                        payload_ptr = self.builder.gep(cond_val, [ir.Constant(self.i32_ty, 0), ir.Constant(self.i32_ty, 1)])
                        payload_val = self.builder.load(payload_ptr, name=var_name + "_val")
                        var_ptr = self.builder.alloca(self.i64_ty, name=var_name); self.builder.store(payload_val, var_ptr)
                        self.symbol_table[var_name] = var_ptr; self.var_types[var_name] = self.i64_ty
                    self.cleanup_vars.append(set())
                    for stmt in body: self.codegen_stmt(stmt)
                    if not self.builder.block.is_terminated: self.cleanup_block(self.cleanup_vars.pop()); self.builder.branch(end_bb)
                    else: self.cleanup_vars.pop()
                    
            self.builder.position_at_end(default_bb)
            if node.default:
                self.cleanup_vars.append(set())
                for stmt in node.default: self.codegen_stmt(stmt)
                if not self.builder.block.is_terminated: self.cleanup_block(self.cleanup_vars.pop()); self.builder.branch(end_bb)
                else: self.cleanup_vars.pop()
            else: self.builder.branch(end_bb)
            self.builder.position_at_end(end_bb)
            
        else:
            # NOVO: Switch para Inteiros (Gera Jump Table nativa no LLVM)
            default_bb = self.builder.append_basic_block(name="switch.default")
            end_bb = self.builder.append_basic_block(name="switch.end")
            sw = self.builder.switch(cond_val, default_bb)
            
            for val_node, var_name, body in node.cases:
                case_bb = self.builder.append_basic_block(name="switch.case")
                val = self.codegen_expr(val_node)
                if val.type != self.i64_ty:
                    val = self.builder.zext(val, self.i64_ty, name="case_val_ext")
                sw.add_case(val, case_bb)
                
                self.builder.position_at_end(case_bb)
                self.cleanup_vars.append(set())
                for stmt in body: self.codegen_stmt(stmt)
                if not self.builder.block.is_terminated:
                    self.cleanup_block(self.cleanup_vars.pop())
                    self.builder.branch(end_bb)
                else:
                    self.cleanup_vars.pop()
                    
            self.builder.position_at_end(default_bb)
            if node.default:
                self.cleanup_vars.append(set())
                for stmt in node.default: self.codegen_stmt(stmt)
                if not self.builder.block.is_terminated:
                    self.cleanup_block(self.cleanup_vars.pop())
                    self.builder.branch(end_bb)
                else:
                    self.cleanup_vars.pop()
            else:
                self.builder.branch(end_bb)
                
            self.builder.position_at_end(end_bb)