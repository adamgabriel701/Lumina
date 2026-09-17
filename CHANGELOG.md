# Changelog

Todas as mudanças notáveis deste projeto são documentadas aqui.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o projeto adere [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [Unreleased]

### Adicionado

#### Linguagem
- **TCO para mutual recursion (SCC dispatcher)**: SCCs (strongly connected components) do grafo de tail calls viram um dispatcher único. Cada membro vira um bloco dentro do dispatcher; tail calls a outros membros viram store de args + set de `current_id` + branch de volta. `is_even` / `is_odd` com 1M iterações rodam em stack constante.
- **Defers emitidos em tail calls**: `return self(...)` em TCO emite os defers pendentes antes do branch de volta. Cada iteração da recursão re-executa o corpo, re-empilhando seus defers.
- **`@safe`** — null check opt-in em `MemberExpr` e `IndexExpr`: funções anotadas com `@safe` ganham null check silencioso em `u.id` e `arr[i]`. Sem anotação, comportamento C-style (SIGSEGV rápido). `?.` continua funcionando em ambos os modos.
- **`@macro`** — expansão de AST em compile-time: funções anotadas com `@macro` não são registradas como funções normais. No call site, o corpo (`return <expr>`) é substituído por um deep-copy com `VariableExpr(param) → arg`. Macros podem chamar outras macros.

#### Bugs corrigidos (parser/codegen)
- **`@attrs` sobrescritos como tuples**: `parser/parser.py::parse` sobrescrevia `decl.attrs` **depois** de cada `parse_*` ter setado. `parse_function` passava `['safe']` (strings); `parse()` sobrescrevia com `[('safe', [])]`. Resultado: `'safe' in attrs` e `'macro' in attrs` retornavam False. **Fix**: removido o override.
- **Macros malformadas não falhavam**: `_validate_macro(fn)` chamada em `generate_module` na coleta — fonte inválida falha em compile-time mesmo se nunca chamada.
- **SCC dispatcher sem `defer_stack`**: `_materialize_scc_dispatcher` não inicializava `self.defer_stack`. **Fix**: init no entry + reset por membro + restore no final.

### Mudado

- **`codegen/codegen.py`**: novos métodos `_compute_tail_call_sccs`, `_can_dispatcher`, `_materialize_scc_dispatcher`, `_validate_macro`, `_infer_arg_type_lumina`, `_infer_type_map_lumina`. Novo módulo `codegen/expressions/macros.py` com `MacrosMixin`.
- **`codegen/expressions/members.py`**: `visit_MemberExpr` e `visit_IndexExpr` ganharam branch `_safe_mode`. `_load_index` extraído para reuso.
- **`parser/parser.py`**: removido o override `decl.attrs = attrs` em `parse()`.

---

## [Unreleased — Sprints 7a a 8a]

### Adicionado

#### Linguagem
- **Genéricos aninhados** (`Box<T>` como parâmetro): `fn put<T>(b: Box<T>, val: T)` compila e funciona.
- **`nil`** — literal novo que produz null pointer C-style, semanticamente distinto de `none`.
- **`defer` com escopo de bloco** (breaking change): cada bloco `if`/`while`/`for`/`match` tem seu próprio escopo. `return`/`break`/`continue` emitem TODOS os defers pendentes.
- **Multi-pattern** em `match`: `case 1 | 2 | 3:` cai no mesmo corpo.
- **Wildcard `_`**: `case _:` casa sem bindar.
- **Variantes bare de enum**: `let x = Stop`.
- **TCO (Tail Call Optimization)** para self-recursion direta.
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