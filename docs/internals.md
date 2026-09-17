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
   ↓ clang
binário nativo / .wasm
```

## Módulos

### `lumina/lexer/`

- `tokens.py` — `TokenType`, `Token`, `KEYWORDS`
- `lexer.py` — tokeniza com INDENT/DEDENT, COMMENT preservado

### `lumina/parser/`

- `base.py` — primitivas de consumo + comentários pendentes
- `expressions.py` — precedência (logical → bitwise → comparison → shift → range → additive → term → factor → postfix)
- `statements.py` — statements e controle de fluxo
- `patterns.py` — match / switch + multi-pattern
- `declarations.py` — fn, struct, enum, trait, impl, import, extern
- `parser.py` — orquestrador + `@attrs`

### `lumina/ast/`

- `expressions.py` — `NumberExpr`, `StringExpr`, `BinaryExpr`, `NilExpr`, `NoneExpr`, `ComptimeExpr`, ...
- `statements.py` — `Function`, `StructDecl`, `VarDecl`, `ReturnStmt`, `MatchStmt`, ...
- `visitor.py` — `NodeVisitor` (despacha para `visit_<ClassName>`)

### `lumina/semantic/`

- `types.py` — `is_assignable`, `parse_generic`, `substitute_generic`, `unify_type`
- `expressions.py` — type checking de expressões
- `statements.py` — type checking de statements + MatchStmt
- `analyzer.py` — orquestrador, `@derive`, traits

### `lumina/codegen/`

- `codegen.py` — `LLVMCodegen` (orquestrador). Contém:
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
  - `calls.py` — CallExpr + builtins + enums + generics + macros
  - `aggregates.py` — Array, StructLiteral, Lambda
  - `match.py` — MatchExpr
  - `macros.py` — expansão de `@macro`
- `statements/`
  - `var_decl.py`, `control.py`, `flow.py`, `match.py`

### `lumina_cli/`

- `main.py` — dispatch de comandos
- `commands.py` — implementação de cada comando
- `compiler.py` — `compile_lumina`, `run_jit`, `format_node`
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

## Como estender

### Adicionar um tipo

1. `semantic/types.py::is_assignable` — regras
2. `semantic/expressions.py` — visitor (se for expressão)
3. `codegen/types.py::get_llvm_type` — mapeamento LLVM
4. `codegen/expressions/` — visitor de codegen

### Adicionar um builtin

1. `lumina/builtins.py` — adicionar nome em `BUILTIN_FUNCTIONS`
2. `codegen/expressions/calls.py::codegen_user_call` — branch `if func_name == "..."`

### Adicionar uma sintaxe

1. `lexer/tokens.py` — novo `TokenType` (se palavra-chave, adicionar em `KEYWORDS`)
2. `lexer/lexer.py` — reconhecer
3. `ast/expressions.py` ou `ast/statements.py` — nó
4. `parser/expressions.py` ou `parser/statements.py` — regra de parsing
5. `semantic/expressions.py` ou `semantic/statements.py` — type checking
6. `codegen/expressions/` ou `codegen/statements/` — geração LLVM
7. `lumina_cli/compiler.py::format_node` — imprimir

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
