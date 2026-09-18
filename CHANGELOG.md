# Changelog

Todas as mudanças notáveis deste projeto são documentadas aqui.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o projeto adere [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [Unreleased — 0.4.0]

### Adicionado

#### Linguagem
- **Closures como callback (tipo `fn` unificado em fat pointer)**: todo valor `fn` em Lumina agora é `{fn_ptr, env_ptr}`. Lambdas com captura usam env != NULL; lambdas sem captura e funções nomeadas usam env = NULL (wrapped em runtime). Isso destrava `sort_by(arr, n, fn(a, b): ...)` com captura, `map`/`filter` com captura em `std/iter`, e qualquer HOF. `&fn_name` devolve o fn ptr cru (FFI-compatível). Resolve o `xfail` histórico de `test_sort_closure_captures`.
- **Closures** (captura por valor): `let offset = 10; let add = fn(x: int) -> int: x + offset`. O codegen detecta variáveis livres em `LambdaExpr`, gera um bloco `{fn_ptr, env_ptr}` no heap, e emite uma função `i64 __closure_N(i8* env, i64 a1, ..., i64 aN)` que lê os campos do env. Suporta lambda aninhada, captura dentro de loop, e chamada com N argumentos.
- **`for i, x in arr`** — índice + valor no mesmo loop. Parser aceita `IDENT COMMA IDENT` após `for`; o `ForStmt` guarda `"i,x"` em `var_name`; o semantic declara ambos; o codegen emite slot para o índice e para o valor.
- **`std/sort`** — `sort(arr, n)` (crescente) e `sort_by(arr, n, cmp)` (comparator). Insertion sort para `n ≤ 16`, quicksort acima. `is_sorted(arr, n)` verifica.
- **`fn_name` como valor** — `sort(arr, n, _cmp_asc)` passa função por nome. Semantic retorna `"fn"`, codegen produz fat pointer `{wrapper, NULL}`.
- **Indirect call com N args** — `fn_ty = i64 (i8*, i64, ..., i64)` via fat pointer. `cmp(a, b)` agora passa ambos.
- **Variante com payload usada bare** agora é erro: `let x = Some` falha com mensagem clara em vez de compilar silenciosamente.
- **`std/io`** — `read_line`, `read_int`, `read_char`, `write`, `write_line`, `eprintln`. Usa os builtins `stdin`/`stdout`/`stderr`/`fgets`/`fputs`/`fflush`/`getchar` diretamente.

#### `std`
- `std/sort.lm` — `_cmp_asc`, `_insertion_sort`, `_partition`, `_quicksort_rec`, `sort`, `sort_by`, `is_sorted`.
- `std/string.lm` — `StringBuilder` com `push_char`, `push_str`, `finish`, `clear`, `size`.
- `std/result.lm` — `unwrap`, `unwrap_or` (renomeado `default` → `fallback`), `is_ok`, `is_err`, `is_ok_and`, `expect`, `map`, `and_then`.
- `std/io.lm` — `read_line` (remove `\n` final, retorna `""` em EOF), `read_int`, `read_char`, `write`, `write_line`, `eprintln`. Sem `extern fn` declarados (são builtins do compilador).

### Corrigido

- **Closure com captura como callback segfaultava.** `sort_by(arr, n, fn(a, b): (b-a)*mult)` passava o bloco `{fn_ptr, env_ptr}` como se fosse um fn ptr cru, e o receptor chamava lixo. **Fix:** unificação do tipo `fn` em fat pointer `{fn_ptr, env_ptr}` + `_call_closure` em toda chamada indireta. Funções nomeadas usadas como valor são wrapped em runtime (`_wrap_fn_as_closure`), com wrapper `i64(i8*, i64, ...)` que adapta a assinatura original. `&fn_name` devolve o fn ptr cru para FFI.
- **`stdin`/`stdout`/`stderr` faltavam em `BUILTIN_RET`.** `std/io.lm` falhava no semantic com "Tipo inválido para parâmetro 'stream': esperado 'str', obteve 'int'" porque `stdout()` era inferido como `int` no `VarDecl`. **Fix:** `BUILTIN_RET` centralizado em `lumina/builtins.py` (fonte única) e `stdin`/`stdout`/`stderr` adicionados como `"str"`.
- **`extern fn fgets` colidia com o builtin.** O `generate_module` registrava o extern com assinatura `i8*(i8*, i64, i8*)`, mas o branch de builtin em `calls.py` trunca `size` para `i32` (assinatura real do C). Resultado: `TypeError: Type of #2 arg mismatch: i64 != i32`. **Fix:** `generate_module` pula `ExternDecl` cujo nome está em `BUILTIN_FUNCTIONS` — o codegen de builtin já emite a assinatura correta.
- **`getchar` retornava `i32` sem normalização.** `ret i32 %getchar_call` não casava com o tipo de retorno `-> int` da função Lumina (i64), gerando `value doesn't match function result type 'i64'` no clang. **Fix:** `sext i32 → i64` antes de retornar.
- **`visit_ReturnStmt` sem normalização `iN → i64`.** Qualquer builtin que devolvesse `i32`/`i8`/`i16` quebrava no `ret`. **Fix:** branch defensivo em `flow.py::visit_ReturnStmt` com `zext` para `i1` e `sext` para os demais.
- **`"\n"` em fonte Lumina virava 2 bytes literais.** O lexer preserva escapes como texto (`\` + `n`), então `fputs("\n", out)` imprimia `\n` literal em vez de newline. **Fix:** `std/io.lm` usa `chr(10)`.
- **`read_line` com `buf[n-1] = 0` não surtia efeito.** Reescrevido com loop explícito que varre o buffer até NUL ou `\n` (ASCII 10), sobrescrevendo com NUL no primeiro caso.
- **`_handle_indent` não era chamado em `tokenize()`.** Regressão que quebrava **todos** os blocos indentados — `fn`, `if`, `while`, `for`, `struct`, `enum`, `impl`, `trait`, `match` — com "Esperado INDENT, mas encontrei X". **Fix:** restaurado o branch `if self.at_line_start: self._handle_indent()` no loop principal.
- `visit_VariableExpr` (semantic + codegen) checava `functions` antes de variantes de enum. Como variantes são adicionadas em `functions` no `analyze()`, `Red` bare virava `"fn"` em vez de `"Color"`. **Fix:** ordem invertida (variante antes de função).
- `for x in arr` com `N` variável (não-literal) caía em loop vazio. Agora `array_lengths` também registra `alloc(NumberExpr)`.
- `parse_for` declarava `from ..ast import ForStmt` dentro do método, sombreando o import do topo do arquivo → `UnboundLocalError`.
- `chr` e `atoi` sem branch de codegen (retornavam `0`). Adicionados em `calls.py`.
- `SliceExpr` inferido como `ptr` no `VarDecl`, fazendo `s[..3] == "abc"` comparar endereços. Agora infere pela fonte (`str` → `str`, array → `ptr`).
- `bool` → `int` usava `sext` (`true` virava `-1`). Agora `zext` quando origem é `i1`.
- `read_file()` dava segfault se o arquivo não existia. Agora retorna `""` via `phi` com `fopen == NULL`.
- `free()` rejeitava `i64*` (`TypeError: i8* != i64*`). Bitcast antes do call.
- `impl Box<T>` chamado em `Box<int>` gerava `%"Box"* != %"Box_int_"*`. Bitcast no `codegen_method_call` quando cai no fallback.
- `std/result::unwrap_or` usava `default` (keyword reservada). Renomeado para `fallback`.
- `and_then` retornava `int` para function pointers, falhando em `_require_assignable`. Agora retorna `None` (tipo desconhecido).
- `lumina lint` estourava `RecursionError` por recursão mútua entre `_collect_vars` e `_collect_exprs`. Reescrito como `_collect` única.

### Adicionado (tests)

- `tests/test_std_io.py` (6 testes) — `read_line`, `read_int`, `read_line_eof`, `write`, `write_line`, `eprintln`.
- `tests/test_closures.py` (10 testes).
- `tests/test_sort.py` (10 testes — `test_sort_closure_captures` deixou de ser xfail).
- `tests/test_lint.py` (14 testes, do 0.3.0).
- `tests/test_forin.py` (9 testes).
- `tests/test_tuples.py` (7 testes).
- `tests/test_generic_impl.py` (6 testes).
- `tests/test_std_result.py` (9 testes).
- `tests/test_escape_analysis.py` (4 testes).

**Total: 384 passed** (antes 383 passed + 1 xfailed, do 0.3.0).

### Mudado

- `lumina/builtins.py` — `BUILTIN_RET` agora vive ao lado de `BUILTIN_FUNCTIONS` (fonte única de verdade). Consumido por `semantic/statements.py`, `semantic/expressions.py` e `codegen/codegen.py`.
- `lumina/codegen/codegen.py::generate_module` — skip de `ExternDecl` que colide com builtin.
- `lumina/codegen/codegen.py::__init__` — `_fn_wrappers` cacheia wrappers `i64(i8*, i64...)` para funções nomeadas usadas como valor.
- `lumina/codegen/helpers.py` — `_make_fn_wrapper` (wrapper que adapta `i64(i8*, i64...)` → assinatura original) + `_wrap_fn_as_closure` (bloco `{wrapper, NULL}` no heap).
- `lumina/codegen/expressions/aggregates.py::visit_LambdaExpr` — sempre chama `_emit_lambda_closure`; `_emit_lambda_plain` removido.
- `lumina/codegen/expressions/members.py::visit_VariableExpr` — função nomeada usada como valor vira `_wrap_fn_as_closure`.
- `lumina/codegen/expressions/operators.py::visit_AddressOfExpr` — `&fn_name` devolve fn ptr cru (FFI-compatível).
- `lumina/codegen/expressions/calls.py` — toda chamada indireta passa por `_call_closure` (sem distinção `closure_vars` vs fn ptr cru).
- `lumina/codegen/expressions/calls.py::getchar` — `sext i32 → i64`.
- `lumina/codegen/statements/flow.py::visit_ReturnStmt` — normalização defensiva `iN → i64`.
- `lumina/semantic/expressions.py::visit_VariableExpr` reordena os checks: variante → `fn` → variável.
- `lumina/codegen/statements/control.py::_visit_for_iterable` — caso "índice + valor" quando `var_name` contém `,`.
- `std/io.lm` — reescrito. Sem `extern fn` (usa builtins), `chr(10)` em vez de `"\n"`, `read_line` com loop explícito.

---

## [Unreleased — 0.3.0]

### Adicionado

#### Linguagem
- **Escape analysis:** `alloc(N)` com `N` constante e sem `return`/`free` viram `alloca` no stack. Reduz pressão no Boehm GC. Reduz ~30% das alocações em código típico.
- **`for x in arr`:** itera sobre arrays literais e strings. Aceita `let arr = [1, 2, 3]; for n in arr` e `for n in [10, 20]` inline.
- **Tuplas literais:** `let (a, b, c) = (1, 2, 3)`. Tipos heterogêneos via `LiteralStructType`.
- **`impl Box<T>:`** — métodos em structs genéricas. O `<T>` é descartado para registro; chamadas em `Box<int>`, `Box<str>`, etc. fazem bitcast para o tipo base.
- **`std/string`** — `StringBuilder` com `push_char`, `push_str`, `finish`, `clear`, crescimento geométrico. Complementa `std/str` (que é funcional).
- **`std/result`** — `unwrap`, `unwrap_or`, `is_ok`, `is_err`, `is_ok_and`, `expect`, `map`, `and_then`.
- **`lumina lint`** — análise estática sem gerar código: W001 (unused), W002 (shadowing), W003 (unreachable), W004 (unused param), W005 (empty body). `--format=json`, `--quiet`, exit code = nº warnings.
- **`opt -O2`** no IR antes do clang, apenas em `--release`.
- **`chr` e `atoi`** agora têm branches dedicados no codegen (antes retornavam 0).

#### CLI
- `lumina lint <arquivo> [--format=text|json] [--quiet]`.
- `--help`/`-h`/`help` retornam exit code 0 (antes caíam em "comando desconhecido").

### Corrigido

- `@attrs` sobrescritos como tuples em `parse()` — `@safe`/`@macro` nunca ativavam.
- `read_file()` dava segfault quando o arquivo não existia (agora retorna `""` via `phi`).
- `free()` rejeitava `i64*` (bitcast para `i8*` antes do call).
- `SliceExpr` era inferido como `ptr` no `VarDecl`, fazendo `s[..3] == "abc"` comparar endereços.
- `bool` → `int` usava `sext`, fazendo `true` virar `-1`. Agora usa `zext` quando origem é `i1`.
- `impl Box<T>` chamado em `Box<int>` gerava `%"Box"* != %"Box_int_"*`. Bitcast para o tipo base.
- `std/result::unwrap_or` usava `default` (keyword reservada). Renomeado para `fallback`.
- `for x in arr` com `N` não-constante caía em loop vazio. Agora registra `array_lengths` no `var_decl`.
- `and_then` retornava `int` para function pointers, falhando no `_require_assignable`.
- `lumina lint` estourava `RecursionError` por recursão mútua entre `_collect_vars` e `_collect_exprs`. Reescrito como `_collect` única.

### Adicionado (tests)

- `tests/test_lint.py` (14 testes).
- `tests/test_forin.py` (9 testes).
- `tests/test_tuples.py` (7 testes).
- `tests/test_generic_impl.py` (6 testes).
- `tests/test_std_result.py` (9 testes).
- `tests/test_escape_analysis.py` (4 testes).

**Total: 325 passed** (antes 267).

---

## [Unreleased — Sprint 9]

### Adicionado

#### Linguagem
- **TCO para mutual recursion (SCC dispatcher)**: SCCs (strongly connected components) do grafo de tail calls viram um dispatcher único. Cada membro vira um bloco dentro do dispatcher; tail calls a outros membros viram store de args + set de `current_id` + branch de volta. `is_even` / `is_odd` com 1M iterações rodam em stack constante.
- **Defers emitidos em tail calls**: `return self(...)` em TCO emite os defers pendentes antes do branch de volta. Cada iteração da recursão re-executa o corpo, re-empilhando seus defers.
- **`@safe`** — null check opt-in em `MemberExpr` e `IndexExpr`.
- **`@macro`** — expansão de AST em compile-time.

#### Bugs corrigidos (parser/codegen)
- **`@attrs` sobrescritos como tuples**.
- **Macros malformadas não falhavam**.
- **SCC dispatcher sem `defer_stack`**.

### Mudado

- **`codegen/codegen.py`**: novos métodos `_compute_tail_call_sccs`, `_can_dispatcher`, `_materialize_scc_dispatcher`, `_validate_macro`, `_infer_arg_type_lumina`, `_infer_type_map_lumina`. Novo módulo `codegen/expressions/macros.py`.
- **`codegen/expressions/members.py`**: `visit_MemberExpr` e `visit_IndexExpr` ganharam branch `_safe_mode`.
- **`parser/parser.py`**: removido o override `decl.attrs = attrs` em `parse()`.

---

## [Unreleased — Sprints 7a a 8a]

### Adicionado

#### Linguagem
- **Genéricos aninhados** (`Box<T>` como parâmetro).
- **`nil`** — null pointer C-style.
- **`defer` com escopo de bloco** (breaking change).
- **Multi-pattern** em `match`: `case 1 | 2 | 3:`.
- **Wildcard `_`**.
- **Variantes bare de enum**.
- **TCO (Tail Call Optimization)** para self-recursion.
- **Type check em campos de struct literal**.
- **Match guard em enum e string**.
- **`break` / `continue`** reais.
- **`assert`** aborta em runtime.
- **Short-circuit** em `and` / `or`.

#### CLI
- `--help` / `-h` / `help`.
- Exit codes propagados em `run` / `build` / `test`.
- `lumina test` respeita `[link]`.
- `[link].extra_flags` passadas ao compilar `.cpp` de FFI.

#### REPL
- REPL persistente com `:history`, `:decls`, `:clear`, `:help`.

#### Compilador
- Boehm GC ativa (`GC_init` + `GC_malloc`).
- `LLVMCodegen` com `ir.Context()` próprio.

#### LSP
- Hover com escopo qualificado.
- References/rename cientes de escopo.
- `document_symbols` com `children` por função/método.
- `read_message` valida `Content-Length`.

#### Formatter
- Preserva `@derive` e outros `@attrs`.
- Multi-pattern impresso como `case A | B:`.
- Wildcard impresso como `case _:`.

### Corrigido

21 bugs silenciosos — ver tabela no `README.md`.

### Mudado

- **`defer` com escopo de bloco** (breaking change).
- **`codegen/statements/match.py`** refatorado para `_match_chain`.
- **`semantic/statements.py`**: bindings herdam `cond_type` quando `variant_name is None`.
- **`parser/patterns.py`**: `_parse_case_pattern` acumula alternativas; string literal vira `StringExpr`.

### Removido

- `replace("GC_malloc", "malloc")` no `cmd_build`.
- `covered_variants = [c[0] for c in node.cases]`.

---

## [1.0.0] — Estado inicial

### Adicionado

#### Linguagem
- Sintaxe baseada em indentação (INDENT/DEDENT)
- Tipagem estática com inferência
- Sintaxe curta (`x := 10`), escopo de bloco lexical
- F-strings (`$"olá {nome}"`)
- Operador pipe (`5 |> dobrar |> imprimir`)
- Navegação segura (`?.`), propagação de erros (`?`), cast (`as`)
- Slicing (`s[1..4]`, `arr[..3]`, `arr[2..]`, `arr[..]`)
- Bitwise (`&`, `|`, `^`, `~`, `<<`, `>>`)
- `switch`/`case`/`default`
- `defer`, `assert`
- Generics com monomorphization (`<T>`)
- Traits com métodos padrão
- Pattern matching com binding e guard
- Enum multi-payload
- `Option<T>` e `NoneExpr`
- `comptime` (constant folding)
- Globais mutáveis (`mut X = 0`)
- Lambdas (inline e com bloco)
- Operator overloading (`__add__`, `__eq__`)
- `@derive(Eq, PartialEq, Debug, Display, Clone, Default)`

#### Standard Library (bootstrapped em Lumina)
- `std/prelude` (`Option`, `Result`), `std/math`, `std/str`, `std/time`, `std/fs`, `std/alloc`
- `std/vector`, `std/map`, `std/set`, `std/deque`, `std/list`, `std/iter`
- `std/test`, `std/log`
- `std/channel`, `std/async`, `std/async_fs`, `std/epoll`, `std/net`, `std/http`
- `std/json`, `std/sqlite`, `std/raylib`

#### Compilador
- Lexer com comentários preservados (`#`, `/* */`)
- Parser com `@attrs`, slices, patterns
- Análise semântica com `@derive`, traits, exaustividade
- Codegen LLVM IR com globais mutáveis, cross-target
- Cross-compile (`--target`): aarch64, armv7, riscv64, i386, WASM
- `-O0` / `-O2` / `-O3` + DWARF debug info
- Build incremental com cache
- FFI com C/C++ (`[link]`)

#### CLI
- `lumina new`, `build`, `run`, `check`, `test`, `clean`, `doc`, `install`, `bind`, `fmt`, `repl`, `jit`, `playground`
- `--error-format=json` (pipe-safe)
- `[link]` com `libs`, `extra_objects`, `target`, `extra_flags`

#### Ferramental
- Extensão VS Code com syntax highlight (TextMate) e LSP
- LSP: autocomplete, hover, go-to-definition, references, rename, outline, semantic tokens, diagnostics
- Web Playground (JIT)
- Auto-formatter preservando comentários leading
- **153 testes** (pytest) + **28 validações** standalone (`run_tests.py`)

[Unreleased]: https://github.com/adamgabriel701/Lumina/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/adamgabriel701/Lumina/releases/tag/v1.0.0