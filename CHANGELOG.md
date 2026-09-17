# Changelog

Todas as mudanças notáveis deste projeto são documentadas aqui.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o projeto adere [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [Unreleased]

### Adicionado

#### Linguagem
- **Genéricos aninhados** (`Box<T>` como parâmetro): `fn put<T>(b: Box<T>, val: T)` compila e funciona. Unificação via `unify_type`; substituição recursiva via `substitute_generic`. Suporta `Box<int>`, `Box<float>`, `Box<str>` no mesmo TU.
- **`nil`** — literal novo que produz null pointer C-style, semanticamente distinto de `none`:
  - `none` constrói `Option::None` (struct alocada)
  - `nil` é compatível com `ptr`, `str`, `fn` e struct via `is_assignable`
  - `u?.campo` faz null check e devolve 0 quando `u == nil`
  - Comparação `u == nil` faz bitcast entre ponteiros de tipos diferentes
  - `let x = nil` infere `ptr` quando sem anotação
- **`defer` com escopo de bloco** (breaking change — ver abaixo): `defer` dentro de `if`/`while`/`for`/`match` roda no fim **daquele bloco**, não da função. `return`/`break`/`continue` emitem TODOS os defers pendentes.
- **Defers emitidos em tail calls**: `return self(...)` em TCO emite os defers pendentes antes do branch de volta. Cada iteração da recursão re-executa o corpo, re-empilhando seus defers.
- **Multi-pattern** em `match`: `case 1 | 2 | 3:` cai no mesmo corpo. Suporta int, string, variantes nullary. Guard aplica ao OR inteiro.
- **Wildcard `_`**: `case _:` casa sem bindar (equivalente a `default:`).
- **Variantes bare de enum**: `let x = Stop` constrói implicitamente variantes sem payload (como Rust `None`).
- **TCO (Tail Call Optimization)** para self-recursion direta: 5 milhões de recursões em stack constante.
- **Type check em campos de struct literal**: `Ponto { x: "texto", y: 2 }` com `x: int` é erro de compilação.
- **Match guard em enum e string**: `case Circle(r) if r > 10:` testa tag E usa payload no guard.
- **`break` / `continue`** reais em loops.
- **`assert`** aborta em runtime (`fflush(NULL)` + `abort()`).
- **Short-circuit** em `and` / `or` (basic blocks com `phi i1`).

#### CLI
- **`lumina --help` / `-h` / `help`** com saída 0.
- **Exit codes propagados** em `run` / `build` / `test`.
- **`lumina test` respeita `[link]`**.
- **`[link].extra_flags`** agora são passadas ao compilar os `.cpp` de FFI (`-DFOO=42`, `-Iinclude`).

#### REPL
- **REPL persistente**: `mut x = 0` e declarações (`fn`, `struct`, `enum`, `impl`, `import`) sobrevivem entre células. Comandos `:history`, `:decls`, `:clear`, `:help`.

#### Compilador
- **Boehm GC ativa**: codegen emite `GC_malloc` + `call GC_init()` no topo de `main`. `--no-gc` emite `malloc` libc cru.
- **`LLVMCodegen` com `ir.Context()` próprio**: cada instância tem seu próprio contexto (antes usava `global_context`, causando `P is already defined` em recompilações no REPL).

#### LSP
- **Hover com escopo qualificado**: `symbol_details` usa `main::i` / `helper::i` para locais.
- **References/rename cientes de escopo**: quando o cursor está sobre uma variável local do enclosing function, refs são filtradas ao range dessa função. Símbolos top-level continuam com varredura léxica global.
- **`document_symbols` com `children`** por função/método.
- **`read_message` valida `Content-Length`**.

#### Formatter
- **Preserva `@derive`** e outros `@attrs`.
- **Multi-pattern** impresso como `case A | B:`.
- **Wildcard** impresso como `case _:`.

### Corrigido

Os bugs abaixo eram **silenciosos** — passavam pelo CI porque os testes originais exercitavam parser/semantic, não runtime. Todos têm teste de regressão.

- `break` / `continue` no-op (`for i in 0..100: if i == 5: break` continuava até 100).
- `assert` sem efeito (`assert(1 == 2)` imprimia a linha seguinte e saía com 0).
- `defer` inline (`defer print("b")` rodava imediatamente).
- **`defer` em `if` não tomado rodava** (`if false: defer print("x")` imprimia `x`).
- **`defer` em TCO era ignorado** (`return self(...)` pulava os defers pendentes).
- `and` / `or` sem short-circuit (`x != 0 and 10/x > 1` causava SIGFPE).
- Formatter apagava `@derive`.
- CLI engolia exit code.
- `lumina test` com falhas saía com 0.
- `--help` caía em "comando desconhecido".
- `_compile_extra_objects` ignorava `extra_flags`.
- Boehm GC nunca ativava.
- Match guard em enum nunca casava.
- Match guard em str ignorado.
- Self-binding declarava `int` fixo.
- String literal virava self-binding.
- `covered_variants` explodia com multi-pattern (`unhashable type: list`).
- `struct` recompilado no REPL disparava `P is already defined`.
- `let` em campo `int` aceitava `str`.
- **`Box<T>` como parâmetro não compilava** (`Tipo inválido para parâmetro b`).
- **LSP rename misturava escopos** (renomear `i` em `main` mexia no `i` de `helper`).

### Mudado

- **`defer` com escopo de bloco (breaking change)**:
  - Antes: `defer` sempre no fim da função. `if false: defer print("x")` imprimia `x`.
  - Agora: cada bloco tem seu próprio escopo. Padrão Go/Zig/Swift.
- **`codegen/statements/match.py`** refatorado: `_match_chain` + 3 helpers substituem `_codegen_match_{int,enum,str}` e `_codegen_match_with_guard`. Redução de ~450 → ~250 linhas. Zero duplicação.
- **`lumina/semantic/statements.py`**: bindings de match herdam `cond_type` quando `variant_name is None`.
- **`lumina/parser/patterns.py`**: `_parse_case_pattern` acumula alternativas via `|`; string literal vira `StringExpr`.
- **`tests/features/test_examples_smoke.py`** respeita `skip.txt`.
- **`lumina_cli/commands.py`**: REPL persistente; `is_no_gc = is_wasm or --no-gc`.

### Removido

- `replace("GC_malloc", "malloc")` no `cmd_build` (resolvido no codegen).
- `covered_variants = [c[0] for c in node.cases]` (substituído por achatamento).

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