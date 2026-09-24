from llvmlite import ir
from ...ast import (
    NumberExpr, BoolExpr, StringExpr, InterpolatedStringExpr, ComptimeExpr,
    NoneExpr, NilExpr, 
)


class LiteralsMixin:

    def visit_NumberExpr(self, node):
        if node.value.startswith('0x') or node.value.startswith('0X'):
            return ir.Constant(self.f64_ty, float(int(node.value, 16))) if node.is_float else ir.Constant(self.i64_ty, int(node.value, 16))
        return ir.Constant(self.f64_ty, float(node.value)) if node.is_float else ir.Constant(self.i64_ty, int(node.value))

    def visit_BoolExpr(self, node):
        return ir.Constant(ir.IntType(1), 1 if node.value else 0)

    def visit_StringExpr(self, node):
        return self.create_global_string(node.value)

    def visit_NoneExpr(self, node):
        """NOVO (A): Constrói Option::None (tag=1, sem payload).

        O prelude declara `enum Option: Some(int); None`, então Option
        está em struct_types. Se não estiver, retorna 0.
        """
        if "Option" in self.struct_types:
            return self._construct_enum("Option", 1, [])
        return ir.Constant(self.i64_ty, 0)

    def visit_NilExpr(self, node):
        """`nil` produz um null pointer (i8* null).

        O VarDecl/AssignStmt/coerção faz o bitcast para o tipo
        do alvo (ex: Usuario*). Se ficar i8*, print mostra "(null)".
        """
        return ir.Constant(self.voidptr_ty, None)

    def visit_InterpolatedStringExpr(self, node):
        return self.codegen_fstring(node.parts)

    def codegen_fstring(self, elements):
        """
        Compila `$"..."` como concatenação dinâmica, sem buffer fixo.

        Estratégia:
          1. Cada elemento vira uma string temporária:
             - StringExpr → global string literal
             - valor `i8*` (str) → usa direto
             - valor `f64` → snprintf("%f")
             - valor `i64` → snprintf("%ld")
          2. Soma comprimentos com strlen.
          3. Aloca buffer final (GC_malloc ou malloc).
          4. strcpy do primeiro + strcat dos demais.

        Bug histórico: valores `i8*` (str) caíam no ramo `%ld` e eram
        formatados como inteiro, imprimindo o ponteiro em decimal
        (`Nome: 101940821279152` em vez de `Nome: João`).

        PATCH: usa `_fn_emit_alloca` para o buffer numérico em vez de
        `self.builder.alloca`. Sem isso, cada `$"..."` com interpolação
        numérica dentro de um loop empilhava `alloca` a cada iteração,
        crescendo o RSP. Em `gc_test` (1M iterações com `"Lixo " + i`),
        o stack estourava em 8 MB. Com `_fn_emit_alloca`, o buffer é
        reservado UMA vez no entry block da função.
        """
        i8_ptr = self.i8_ty.as_pointer()

        parts = []  # lista de (str_llvm_val, label)
        for i, el in enumerate(elements):
            if isinstance(el, StringExpr):
                sv = self.create_global_string(el.value)
                parts.append((sv, f"str_{i}"))
                continue

            v = self.visit(el)

            # Se já é string (ponteiro), usa direto — NÃO formata.
            if isinstance(v.type, ir.PointerType):
                sv = self.builder.bitcast(v, i8_ptr, name=f"fstr_str_cast_{i}")
                parts.append((sv, f"var_{i}"))
                continue

            # Números: snprintf em buffer local.
            #
            # PATCH: _fn_emit_alloca hoista para o entry block da função,
            # evitando crescimento de stack quando este f-string aparece
            # dentro de um loop.
            num_buf = self._fn_emit_alloca(
                f"fstr_num_buf_{i}",
                ir.ArrayType(self.i8_ty, 32),
            )
            num_buf_i8 = self.builder.bitcast(
                num_buf, i8_ptr, name=f"fstr_num_i8_{i}"
            )
            if isinstance(v.type, ir.DoubleType):
                fmt = self.create_global_string("%f")
            else:
                fmt = self.create_global_string("%ld")
            self.builder.call(
                self.snprintf,
                [num_buf_i8, ir.Constant(self.i64_ty, 32), fmt, v],
                name=f"fstr_snprintf_{i}",
            )
            parts.append((num_buf_i8, f"num_{i}"))

        # Soma tamanhos (+1 para NUL)
        total = ir.Constant(self.i64_ty, 1)
        for sv, label in parts:
            ln = self.builder.call(self.strlen, [sv], name=f"fstr_len_{label}")
            total = self.builder.add(total, ln, name=f"fstr_total_{label}")

        # Aloca buffer
        buf_raw = self.builder.call(self.malloc, [total], name="fstr_buf")
        buf = self.builder.bitcast(buf_raw, i8_ptr, name="fstr_buf_i8")

        # Concatena
        if not parts:
            self.builder.store(ir.Constant(self.i8_ty, 0), buf)
        else:
            self.builder.call(self.strcpy, [buf, parts[0][0]], name="fstr_first")
            for sv, label in parts[1:]:
                self.builder.call(self.strcat, [buf, sv], name=f"fstr_cat_{label}")

        return buf

    def visit_ComptimeExpr(self, node):
        # NOVO (B): se o semantic fez constant folding, usa o valor dobrado
        if getattr(node, 'folded', None) is not None:
            return self.visit(node.folded)
        return self.visit(node.expr)