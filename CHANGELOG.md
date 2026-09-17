# Changelog

Todas as mudanças notáveis deste projeto são documentadas aqui.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o projeto adere [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [Unreleased]

### Adicionado

#### Linguagem
- **Multi-pattern** em `match`: `case 1 | 2 | 3:` cai no mesmo corpo. Suporta int literals, string literals e variantes nullary de enum. Bindings + multi-pattern é rejeitado no parser.
- **Wildcard `_`**: `case _:` casa sem bindar (equivalente a `default:`), em qualquer posição.
- **Variantes bare de enum**: `let x = Stop` constrói implicitamente variantes sem payload (como `None` em Rust, `Nothing` em Haskell). Variantes com payload continuam exigindo `Some(42)`.
- **TCO (Tail Call Optimization)** para self-recursion direta: `return sum_rec(n - 1, acc + n)` vira loop. Testado com 5 milhões de recursões em stack constante. Mutual recursion não otimizada.
- **Type check em campos de struct literal**: `Ponto { x: "texto", y: 2 }` com `x: int` agora é erro de compilação (antes compilava e imprimia o endereço da string).
- **Match guard em enum**: `case Circle(r) if r > 10:` agora testa a tag da variante E usa o payload no guard.
- **Match guard em string**: `case s if s.contains("x"):` — binding disponível no guard.
- **`break` / `continue`** reais em loops (antes eram no-op silencioso).
- **`assert`** aborta em runtime com `fflush(NULL)` + `abort()` (antes era no-op).
- **`defer`** executa no fim da função (antes era inline).
- **Short-circuit** em `and` / `or` (basic blocks com `phi i1` — antes avaliava ambos os lados).

#### CLI
- **`lumina --help` / `-h` / `help`** com saída 0.
- **Exit codes propagados**: `lumina run` retorna o exit code do binário; `lumina test` retorna o número de falhas; `lumina build` retorna 1 em falha.
- **`lumina test` respeita `[link]`** do `lumina.toml` (libs, extra_objects, extra_flags).
- **`[link].extra_flags`** agora são passadas ao compilar os `.cpp` de FFI (`-DFOO=42`, `-Iinclude`, `-std=c++17`).
- **`_load_link_config`** cai para `./lumina.toml` quando o sidecar do `.lm` não existe.

#### REPL
- **REPL persistente**: `mut x = 0` e declarações (`fn`, `struct`, `enum`, `impl`, `import`) sobrevivem entre células. Comandos `:history`, `:decls`, `:clear`, `:help`.
- Aviso no startup: "`let` é local à célula; use `mut` para persistir".

#### Compilador
- **Boehm GC ativa**: codegen emite `GC_malloc` + `call GC_init()` no topo de `main`. O `-lgc` no linker finalmente faz algo.
- **`--no-gc`** emite `malloc` (libc) cru para bare-metal.
- **`LLVMCodegen` com `ir.Context()` próprio**: cada instância tem seu próprio contexto (antes usava `global_context`, causando "P is already defined" em recompilações no REPL).
- **Variantes bare** no `visit_VariableExpr` do semantic e codegen.

#### LSP
- **Hover com escopo qualificado**: `symbol_details` agora usa `main::i` / `helper::i` para locais. Hover correto para variáveis homônimas em funções diferentes.
- **`document_symbols` com `children`**: outline do VS Code mostra locais como filhos de cada função/método.
- **`read_message` valida `Content-Length`**: defesa contra cliente JSON-RPC corrompido.

#### Formatter
- **Preserva `@derive`** e outros `@attrs`: `_format_attrs()` reemite os atributos anexados pelo parser.
- **Multi-pattern** impresso corretamente: `case A | B:`.
- **Wildcard** impresso como `case _:`.

#### Documentação
- `README.md` expandido com **44 features** catalogadas e tabela de **17 bugs silenciosos**.
- `CHANGELOG.md` criado.

### Corrigido

Os bugs abaixo eram **silenciosos** — passavam pelo CI porque os testes originais exercitavam parser/semantic, não runtime. Todos têm teste de regressão.

- **`break` / `continue` no-op** (`for i in 0..100: if i == 5: break` continuava até 100).
- **`assert` sem efeito** (`assert(1 == 2)` imprimia a linha seguinte e saía com 0).
- **`defer` inline** (`defer print("b")` rodava imediatamente).
- **`and` / `or` sem short-circuit** (`x != 0 and 10/x > 1` causava SIGFPE).
- **Formatter apagava `@derive`**.
- **CLI engolia exit code** (`lumina run` sempre saía com 0).
- **`lumina test` com falhas saía com 0**.
- **`--help` caía em "comando desconhecido"**.
- **`_compile_extra_objects` ignorava `extra_flags`** (`-DFOO=42` não chegava ao `.cpp`).
- **Boehm GC nunca ativava** (`-lgc` era decorativo, codegen usava `malloc` cru).
- **Match guard em enum nunca casava** (`case Circle(r) if r > 10:` sempre pulava).
- **Match guard em str ignorado** (`_codegen_match_with_guard` não testava voidptr).
- **Self-binding declarava `int` fixo** (`case s if s.contains("x")` → "método não implementado para struct int").
- **String literal virava self-binding** (`case "build":` casava qualquer string quando havia guard em outro case).
- **`covered_variants = [c[0] ...]` explodia** com `unhashable type: list` em multi-pattern.
- **`struct` recompilado no REPL** disparava `P is already defined` (types vazavam pelo `global_context`).
- **`let` em campo `int` aceitava `str`** (`Ponto { x: "texto", y: 2 }` imprimia endereço da string).

### Mudado

- **`codegen/statements/match.py`** refatorado: `_codegen_match_{int,enum,str}` e `_codegen_match_with_guard` foram unificados em `_match_chain` + 3 helpers (`_classify_match_kind`, `_compute_pattern_match`, `_emit_bindings`). Redução de ~450 → ~250 linhas. Zero duplicação.
- **`lumina/semantic/statements.py`**: bindings de match herdam `cond_type` quando `variant_name is None` (self-binding).
- **`lumina/parser/patterns.py`**: `_parse_case_pattern` acumula múltiplas alternativas via `|`; string literal vira `StringExpr`.
- **`tests/features/test_examples_smoke.py`** respeita `skip.txt` (mesmo arquivo usado por `scripts/check_examples.sh`).

### Removido

- `replace("GC_malloc", "malloc")` no `cmd_build` (resolvido no codegen com `--no-gc`).
- `covered_variants = [c[0] for c in node.cases]` (substituído por achatamento de listas).

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
- `std/prelude` (`Option`, `Result`)
- `std/math`, `std/str`, `std/time`, `std/fs`, `std/alloc`
- `std/vector`, `std/map`, `std/set`, `std/deque` (com crescimento automático)
- `std/list` (linked list)
- `std/iter` (adaptadores funcionais)
- `std/test`, `std/log`
- `std/channel` (CSP), `std/async`, `std/epoll`, `std/net`, `std/http`
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