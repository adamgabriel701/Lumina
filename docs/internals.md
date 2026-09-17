# 🔧 Internals do Compilador

Arquitetura e fluxo de compilação.

## Pipeline

```
source.lm
   ↓ Lexer (lumina/lexer/)
tokens
   ↓ Parser (lumina/parser/)
AST (lumina/ast/)
   ↓ SemanticAnalyzer (lumina/semantic/)
AST + tipos + symbol tables
   ↓ LLVMCodegen (lumina/codegen/)
LLVM IR
   ↓ opt -O2 (só em --release)
LLVM IR otimizado
   ↓ clang
binário nativo / .wasm
```

## Módulos

### `lumina/lexer/`

- `tokens.py` — `TokenType`, `Token`, `KEYWORDS`
- `lexer.py` — tokeniza com INDENT/DEDENT, COMMENT preservado

### `lumina/parser/`

- `base.py` — primitivas de consumo + comentários pendentes
- `expressions.py` — precedência + tuple literals
- `statements.py` — statements e controle de fluxo
- `patterns.py` — match / switch + multi-pattern
- `declarations.py` — fn, struct, enum, trait, `impl Box<T>`, import, extern
- `parser.py` — orquestrador + `@attrs`

### `lumina/ast/`

- `expressions.py` — `NumberExpr`, `StringExpr`, `BinaryExpr`, `NilExpr`, `NoneExpr`, `ComptimeExpr`, `TupleExpr`, ...
- `statements.py` — `Function`, `StructDecl`, `VarDecl`, `ReturnStmt`, `MatchStmt`, ...
- `visitor.py` — `NodeVisitor` (despacha para `visit_<ClassName>`)

### `lumina/semantic/`

- `types.py` — `is_assignable`, `parse_generic`, `substitute_generic`, `unify_type`
- `expressions.py` — type checking de expressões + `visit_TupleExpr`
- `statements.py` — type checking de statements, `BUILTIN_RET`, MatchStmt
- `analyzer.py` — orquestrador, `@derive`, traits

### `lumina/codegen/`

- `codegen.py` — `LLVMCodegen` (orquestrador):
  - `setup_libc_functions` — GC_malloc ou malloc
  - `generate_module` — pipeline principal
  - `register_struct` / `register_enum` / `register_function`
  - `generate_function_body` — entry_bb + body_bb (para TCO)
  - `materialize_generic` — monomorphization
  - `_compute_tail_call_sccs` / `_materialize_scc_dispatcher` — mutual recursion
  - `_validate_macro` / `_infer_arg_type_lumina` / `_infer_type_map_lumina`
- `helpers.py` — `create_global_string`, `to_float_if_needed`
- `types.py` — `get_llvm_type` + monomorphized structs
- `expressions/`
  - `literals.py` — Number, Bool, String, Interp, Nil, None
  - `operators.py` — Binary, Unary, Cast, Deref, Address, Propagate
  - `members.py` — Variable, Member (`?.` + `@safe`), Index, Slice
  - `calls.py` — CallExpr + builtins (`chr`, `atoi`, `int`, `float`, `str`) + enums + generics + macros
  - `aggregates.py` — Array, StructLiteral, Lambda, **Tuple**
  - `match.py` — MatchExpr
  - `macros.py` — expansão de `@macro`
- `statements/`
  - `var_decl.py` — **escape analysis** (`_try_stack_alloc`) + `array_lengths`
  - `control.py` — if/while/for + **`_visit_for_iterable`** (`for x in arr`)
  - `flow.py` — assign/return/defer + **destructuring** (struct/array/tuple)
  - `match.py` — MatchStmt com `_match_chain`

### `lumina_cli/`

- `main.py` — dispatch de comandos
- `commands.py` — implementação de cada comando
- `compiler.py` — `compile_lumina`, `run_jit`, `format_node`
- `lint.py` — análise estática (W001..W005)
- `playground.py` — servidor web
- `utils.py` — cores, hashes, paths

## Componentes importantes

### Comentários no parser

O lexer emite `COMMENT` tokens. O parser acumula em `pending_comments` e anexa em `decl.leading_comments`. O formatter reemite.

### `@derive`

`SemanticAnalyzer._expand_derives` insere `ImplBlock` sintéticos e funções livres (`new_Struct`) diretamente no AST antes da análise. Codegen trata igual.

### TCO self-recursion

`visit_ReturnStmt` detecta `return self(args)`. Em vez de emitir `call` + `ret`, avalia args em temporários, sobrescreve os slots dos params, emite `branch` para `body_bb`. Nunca emite `ret`.

### TCO mutual recursion (SCC)

`generate_module` roda Kosaraju no grafo de tail calls. Para cada SCC de tamanho ≥ 2 com assinaturas compatíveis, gera `__scc_N(i32 entry_id, params...)` com `switch` sobre `entry_id`. Membros viram blocos; wrappers `f`, `g` chamam o dispatcher com `entry_id` correto.

`_try_tail_call` detecta `_current_scc_slots` e emite store de args + set de `current_id` + branch para `dispatch_bb`.

### `defer` com escopo de bloco

`defer_stack` é uma lista de corpos de defer. `_begin_scope()` marca o índice atual; `_end_scope(start)` emite e deleta; `_emit_scope_defers(start)` emite sem deletar (usado em `break`/`continue`). `_emit_all_defers()` emite tudo (usado em `return`).

Cada bloco (`if`/`while`/`for`/`match`) faz `_begin_scope` no início e `_end_scope` no fallthrough. `break`/`continue` fazem `_emit_scope_defers` antes do branch.

### `@safe`

`generate_function_body` seta `self._safe_mode = 'safe' in attrs`. `visit_MemberExpr` / `visit_IndexExpr` checam `node.is_safe or self._safe_mode`. Se safe, geram bloco de null check com phi.

### `@macro`

`generate_module` coleta funções com `attr macro` em `self.macros`. Essas não são registradas como funções normais. `codegen_user_call` verifica `func_name in self.macros` antes de tudo e expande via `_expand_macro_expr` (deep-copy + substituição de `VariableExpr(param) → arg`).

### Escape analysis

`var_decl.py::_try_stack_alloc` decide se `alloc(N)` vai para stack ou heap:

- `N` **constante** (NumberExpr) e `N > 0` e `N <= 4096`.
- o nome **não** está em `self.escapes` (retornado, atribuído a campo, etc.).
- o nome **não** está em `self.freed_vars` (tem `free(x)` explícito).

Se as 3 condições valem, gera `alloca` de `ArrayType(i64, N)` (ou `i8` para `alloc_bytes`) e aponta `symbol_table[nome]` para o primeiro elemento.

`self.escapes` é populado em `semantic/analyzer.py::check_escape`. `self.freed_vars` é populado em `semantic/expressions.py::visit_CallExpr` quando detecta `free(x)`.

### `array_lengths` (para `for x in arr`)

`visit_VarDecl` registra `self.array_lengths[name] = len(value.elements)` quando `value` é `ArrayExpr`. Isso é necessário porque `visit_VariableExpr` faz `load` do slot (um `i64*`) e o `pointee` LLVM do slot é `i64`, não `ArrayType` — o tamanho seria perdido. `_visit_for_iterable` consulta `array_lengths` antes de tentar `arr_val.type.pointee.count`.

`_visit_for_iterable` cobre 4 casos:

1. Variável com array literal registrado → `N` conhecido, GEP simples.
2. Array inline → `ArrayType*`, GEP duplo `[0, idx]`.
3. String → `strlen` em runtime, elemento `i8`.
4. Outros → loop vazio (não crasha).

### `impl Box<T>:` — resolução de método genérico

`parse_impl` descarta o `<T>` para registro: `struct_name = "Box"`. Todos os métodos ficam como `Box_get`, `Box_set`.

`codegen_method_call` tenta `f"{struct_name}_{method_name}"` (ex: `Box_int__get`), e se não achar, cai para `f"{base}_{method_name}"` (ex: `Box_get`). Se `used_base == True` e o tipo do `self` esperado pelo método (i.e., `func_type.args[0]`) for diferente do tipo do `obj_val` (`Box_int_*` vs `Box*`), emite `bitcast`.

Isso funciona porque `Box<T>` no LLVM tem o mesmo layout para qualquer `T` do mesmo tamanho (i64/ptr/f64).

### Tuplas — `LiteralStructType`

`visit_TupleExpr` cria `ir.LiteralStructType([t1, t2, ...])` onde cada `ti` é o tipo LLVM do elemento. Diferente de `ArrayExpr`, que força tudo para `i64`.

`visit_DestructureStmt` em `flow.py` trata 4 casos:

1. `PointerType[IdentifiedStructType]` — struct nomeada.
2. `PointerType[LiteralStructType]` — tupla literal.
3. `PointerType[ArrayType]` — alloca de array literal.
4. `PointerType[T]` (raw) — array `alloc`'d.

### `lumina lint`

`lumina_cli/lint.py` roda 4 checks (`_check_unused`, `_check_shadowing`, `_check_unreachable`, `_check_empty_functions`) sobre o AST sem rodar o semantic. Ponto de entrada único `_collect(node, into)` para evitar recursão mútua entre statements e expressões.

### `opt -O2` em `--release`

`cmd_build` roda `opt -O2 -S ir -o ir` antes do clang **apenas** quando `--release`. Em builds normais o IR fica cru, permitindo inspeção e mantendo testes que checam nomes de blocos (`sum_rec_body`, `and_rhs`).

Se `opt` não está no PATH, emite warning e segue sem otimizar.

## Como estender

### Adicionar um tipo

1. `semantic/types.py::is_assignable` — regras
2. `semantic/expressions.py` — visitor (se for expressão)
3. `codegen/types.py::get_llvm_type` — mapeamento LLVM
4. `codegen/expressions/` — visitor de codegen

### Adicionar um builtin

1. `lumina/builtins.py` — adicionar nome em `BUILTIN_FUNCTIONS`
2. `semantic/statements.py::BUILTIN_RET` — tipo de retorno (se retorna valor)
3. `codegen/expressions/calls.py::codegen_user_call` — branch `if func_name == "..."`

### Adicionar uma sintaxe

1. `lexer/tokens.py` — novo `TokenType` (se palavra-chave, adicionar em `KEYWORDS`)
2. `lexer/lexer.py` — reconhecer
3. `ast/expressions.py` ou `ast/statements.py` — nó
4. `parser/expressions.py` ou `parser/statements.py` — regra de parsing
5. `semantic/expressions.py` ou `semantic/statements.py` — type checking
6. `codegen/expressions/` ou `codegen/statements/` — geração LLVM
7. `lumina_cli/compiler.py::format_node` — imprimir
8. `lumina_cli/lint.py::_collect` — coletar (se for um nó que pode conter `VariableExpr`)

## Debug

Inspecionar IR:

```bash
lumina build app.lm --debug
cat app.ll
```

Debug de semantic:

```python
from lumina.lexer import Lexer
from lumina.parser import Parser
from lumina.semantic import SemanticAnalyzer

code = open("app.lm").read()
tokens = Lexer(code).tokenize()
ast = Parser(tokens, "app.lm", code).parse()
SemanticAnalyzer("app.lm", code).analyze(ast)
```

Inspecionar IR otimizado:

```bash
lumina build app.lm --release
cat app.ll   # já passou por opt -O2
```
