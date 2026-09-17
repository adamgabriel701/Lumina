# 🌟 Lumina Language

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LLVM Version](https://img.shields.io/badge/LLVM-14%2B-blue.svg)](https://llvm.org/)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Alpha%20%2F%20Active-green.svg)](#)
[![Language](https://img.shields.io/badge/Language-Lumina-6A0DAD.svg)](#)
[![Tests](https://img.shields.io/badge/tests-249%20passed-brightgreen.svg)](#-testes-automatizados)
[![Examples](https://img.shields.io/badge/examples-54%20ran%20%7C%2017%20skip%20%7C%200%20fail-success.svg)](#)
[![Cross-compile](https://img.shields.io/badge/cross--compile-aarch64%20%7C%20armv7%20%7C%20riscv64%20%7C%20wasm-blueviolet.svg)](#-cross-compilação)

**Lumina** é uma linguagem de programação de sistemas de propósito geral, focada em alta performance, ergonomia moderna, concorrência e segurança de memória. Combina a sintaxe limpa e expressiva baseada em indentação (estilo Python/Nim) com o poder de baixo nível e otimização industrial do backend **LLVM**.

A linguagem oferece tipagem estática com inferência, Garbage Collector nativo (Boehm GC), Tipos Algébricos (Enums com multi-payload e variantes bare), Generics com **Monomorphization** incluindo **genéricos aninhados** (`Box<T>` como parâmetro), Traits com Métodos Padrão, Standard Library Bootstrapped, Pattern Matching (multi-pattern `|`, wildcard `_`, guard, destructuring de structs), **Tail Call Optimization** com propagação de `defer`, operador `nil` para null pointer real, **`defer` com escopo de bloco** (Go/Zig-style), Canais de Concorrência (CSP), operadores modernos (`|>`, `?.`, `?`, `as`, `:=`), interoperabilidade nativa com C/C++ (FFI), I/O Assíncrono (`epoll`/`O_NONBLOCK`), um **REPL persistente**, um Web Playground, um LSP completo (com hover qualificado por escopo, references e rename cientes de escopo, semantic tokens), compilação incremental, testes nativos com relatório de cobertura, cross-compile para múltiplas arquiteturas, e é **Cross-Platform** (nativos x86_64/ARM/RISC-V, WebAssembly e Bare-Metal).

---

## ✨ Funcionalidades Principais

* **Sintaxe Limpa & Ergonômica:** Escopo definido por indentação significativa. Sem chaves `{}` ou `;`.
* **Standard Library Bootstrapped:** Módulos como `std/math`, `std/str`, `std/vector`, `std/map`, `std/set`, `std/deque`, `std/iter`, `std/test` e `std/log` são escritos 100% na própria Lumina.
* **Coleções Nativas:** `Vector`, `Map`, `Set` e `Deque` — todos com **crescimento automático** (rehash em Map/Set quando load factor ≥ 0.75, `grow()` em Deque/Vector).
* **Adaptadores Funcionais (`std/iter`):** `map`, `filter`, `count_if`, `sum`, `sum_by`, `product`, `min`, `max`, `all`, `any`, `find_index`, `copy`, `fill`, `for_each`, `reverse`.
* **`std/test` — Framework de Testes:** `check_eq`, `check_ne`, `check_true`, `check_false`, `check_str_eq`. O `lumina test` agrega o resultado e retorna exit code = total de falhas.
* **`std/log` — Logging com Níveis:** `DEBUG`, `INFO`, `WARN`, `ERROR` com filtro em runtime via `set_level()` / `get_level()`.
* **`@derive` Attributes:** `@derive(Eq, PartialEq, Debug, Display, Clone, Default)` gera automaticamente:
  * `Eq`        → `fn __eq__(a, b) -> bool`
  * `PartialEq` → `__eq__` **e** `__ne__` (habilita `==` e `!=`)
  * `Debug`     → `fn __debug__(p) -> str` (`Nome { f1: v1, f2: v2 }`)
  * `Display`   → alias de `Debug`
  * `Clone`     → `fn clone(self) -> Struct` (copia campos)
  * `Default`   → `fn new_Struct() -> Struct` (campos zerados)
* **Tipagem Estática com Inferência:** Deduz tipos automaticamente, incluindo retornos de métodos, generics aninhados, lambdas, operações binárias, `Option<T>`, `nil` e `comptime`.
* **Generics com Monomorphization:** Tipos genéricos `<T>` geram cópias especializadas em compile-time. **Genéricos aninhados** (`fn put<T>(b: Box<T>, val: T)`) suportados — unificação de tipos via `unify_type` e substituição recursiva via `substitute_generic`.
* **Tipos Algébricos (ADTs) & Pattern Matching:** `enum`s com multi-payload. `match`/`switch` com binding, guard (`if`), **multi-pattern** (`case A | B:`), **wildcard** (`case _:`) e exaustividade validada. **Variantes bare** (`let x = Stop`) constroem implicitamente variantes sem payload (como Rust `None`, Haskell `Nothing`).
* **`Option<T>`, `none` e `nil`:** `none` constrói `Option::None` (struct alocada). **`nil`** constrói null pointer real (C-style), compatível com `ptr`/`str`/`fn`/struct. `u?.campo` faz null check automático.
* **`comptime` real (constant folding):** `comptime(2 + 3 * 4)` vira literal no IR.
* **Globais mutáveis:** Top-level `mut X = 0` é emitido como `GlobalVariable` LLVM.
* **Tail Call Optimization:** Self-recursion (`return f(args)`) vira loop. `sum_rec(5_000_000, 0)` roda em stack constante. **`defer` é emitido a cada iteração** (Sprint 8d).
* **Closures (Lambdas):** `fn(x: int) -> int: x * 2` com function pointers.
* **Ergonomia Moderna:**
  * Sintaxe curta (`x := 10`), escopo de bloco lexical, F-strings (`$"olá {nome}"`), operador pipe (`5 |> dobrar |> imprimir`).
  * Navegação segura (`?.`), propagação de erros (`?`), cast explícito (`as`).
  * Slicing nativo: `s[1..4]`, `arr[..3]`, `arr[2..]`, `arr[..]`.
  * Bitwise (`&`, `|`, `^`, `~`, `<<`, `>>`).
  * `switch`/`case`/`default`.
  * **`defer` com escopo de bloco** (Sprint 8b — Go/Zig/Swift-style). Blocos `if`/`while`/`for`/`match` têm seu próprio escopo. `return`/`break`/`continue` emitem TODOS os defers pendentes.
  * **`assert`** aborta em runtime com `fflush(NULL)` + `abort()`.
  * **Auto-formatter** (`lumina fmt`) preserva comentários leading, `@attrs` e `case A | B:` — suporta `--check`.
  * **Short-circuit real** em `and` / `or` (basic blocks com `phi i1`).
* **Mensagens Inteligentes:** Sugestões "Did you mean?" + destaque colorido da linha + `--error-format=json`.
* **Concorrência e I/O Assíncrono:** Canais (CSP), green threads (ucontext), epoll + `O_NONBLOCK`.
* **Gerenciamento de Memória:** Boehm GC ativo (`GC_init` + `GC_malloc`), Arena Allocator em `--no-gc`.
* **Otimizações:** TCO, constant folding, `-O0/-O2/-O3`, forward declarations, build incremental, DWARF debug info.
* **Configuração de Link (`[link]`):** libs C/C++, extra_objects com `extra_flags`, targets específicos.
* **Cross-Compile (`--target`):** aarch64, armv7, riscv64, i386, WASM.
* **CLI ergonômica:** `--help`, exit codes propagados (`run`/`build`/`test`), `--error-format=json` pipe-safe.
* **REPL persistente:** `mut` e declarações (`fn`, `struct`, `enum`, `impl`, `import`) persistem entre células. Comandos `:history`, `:decls`, `:clear`.
* **LSP completo com escopo:** hover, go-to-definition, **find references** e **rename** distinguem variáveis locais homônimas em funções diferentes via chaves qualificadas (`main::i` vs `helper::i`). Semantic tokens e outline também.
* **Cross-Platform:** binários nativos, WebAssembly e Bare-Metal.

---

## 📊 Status de Implementação

### Linguagem

| # | Feature | Status |
|---|---|---|
| 1 | String Slicing (`s[1..4]`) | ✅ |
| 2 | Array Indexing (`arr[i]`) | ✅ |
| 2b | Array Slicing (`arr[a..b]`, `arr[..b]`, `arr[a..]`, `arr[..]`) | ✅ |
| 3 | Operador Pipe (`\|>`) | ✅ |
| 4 | Pipe encadeado | ✅ |
| 5 | Safe Navigation (`?.`) | ✅ |
| 6 | Propagação (`?`) | ✅ |
| 7 | `switch` em inteiros | ✅ |
| 8 | `switch` em enums | ✅ |
| 9 | Sintaxe curta (`:=`) | ✅ |
| 10 | Escopo de bloco lexical | ✅ |
| 11 | **`defer` com escopo de bloco (Go/Zig-style)** | ✅ |
| 12 | `assert` (aborta em runtime) | ✅ |
| 13 | F-strings com múltiplas variáveis | ✅ |
| 14 | Generics + monomorphization | ✅ |
| 15 | Nested structs + member chain | ✅ |
| 16 | Match guard (`case n if n > 10:`) em int, enum e str | ✅ |
| 17 | Match em enum com binding | ✅ |
| 18 | Enum multi-payload (`Dois(int, int)`) | ✅ |
| 18b | **Multi-pattern (`case 1 \| 2:`, `case "a" \| "b":`)** | ✅ |
| 18c | **Wildcard (`case _:`)** | ✅ |
| 18d | **Variantes bare (`let x = Stop`)** | ✅ |
| 19 | Cast explícito (`as`) | ✅ |
| 20 | Ponteiros (`&x`, `*p`) | ✅ |
| 21 | Lambda inline | ✅ |
| 22 | Lambda com bloco | ✅ |
| 23 | Trait com método default | ✅ |
| 24 | Match em string | ✅ |
| 25 | `Option<T>` + `NoneExpr` | ✅ |
| 26 | `comptime` (constant folding) | ✅ |
| 27 | `SliceExpr` dedicado | ✅ |
| 28 | Auto-formatter (comentários + `@attrs` + multi-pattern) | ✅ |
| 29 | Operator Overloading (`__add__`, `__eq__`) | ✅ |
| 30 | `@derive(Eq, PartialEq, Debug, Display, Clone, Default)` | ✅ |
| 31 | `std/vector`, `std/map`, `std/set`, `std/deque` | ✅ |
| 32 | `std/iter` (adaptadores funcionais) | ✅ |
| 33 | `std/test` (framework de testes) | ✅ |
| 34 | `std/log` (níveis + filtro) | ✅ |
| 35 | Globais mutáveis | ✅ |
| 36 | LSP (hover, rename, references, outline, semantic tokens) | ✅ |
| 37 | **LSP hover com escopo qualificado** | ✅ |
| 38 | **LSP references/rename cientes de escopo (Sprint 8a)** | ✅ |
| 39 | Cross-compile (`--target`) | ✅ |
| 40 | `break` / `continue` reais em loops | ✅ |
| 41 | Short-circuit em `and` / `or` | ✅ |
| 42 | Type check em campos de struct literal | ✅ |
| 43 | TCO para self-recursion (5M chamadas) | ✅ |
| 44 | Boehm GC ativa (`GC_init` + `GC_malloc`) | ✅ |
| 45 | REPL persistente (`mut` e `fn` entre células) | ✅ |
| 46 | **Genéricos aninhados (`Box<T>` como parâmetro)** | ✅ |
| 47 | **`nil` — null pointer real para structs** | ✅ |
| 48 | **Defers emitidos em tail calls** | ✅ |

### CLI

| # | Feature | Status |
|---|---|---|
| 1 | `lumina new`, `build`, `run`, `check`, `test`, `clean`, `doc`, `install`, `bind`, `fmt` | ✅ |
| 2 | `lumina repl` (persistente), `jit`, `playground` | ✅ |
| 3 | `--help` / `-h` / `help` | ✅ |
| 4 | Exit codes propagados | ✅ |
| 5 | `--error-format=json` (pipe-safe) | ✅ |
| 6 | `[link]` com `libs`, `extra_objects`, `target`, `extra_flags` | ✅ |

---

## 🐛 Bugs corrigidos

Os bugs abaixo eram **silenciosos** — passavam pelo CI porque os testes originais só exercitavam parser/semantic, não runtime. Cada um tem teste de regressão.

| Bug | Sintoma original | Correção | Teste |
|---|---|---|---|
| `break` / `continue` no-op | `for i in 0..100: if i == 5: break` continuava até 100 | `loop_stack` com branch para `end_bb` / `inc_bb` | `test_runtime_bugs.py` |
| `assert` sem efeito | `assert(1 == 2)` imprimia a linha seguinte e saía com 0 | `fflush(NULL)` + `abort()` + `unreachable` | `test_runtime_bugs.py` |
| `defer` inline | `defer print("b")` rodava imediatamente | `defer_stack` por função, emitido antes de cada `ret` | `test_runtime_bugs.py` |
| `and` / `or` sem short-circuit | `x != 0 and 10/x > 1` causava SIGFPE | Basic blocks `*_rhs` / `*_end` + `phi i1` | `test_runtime_bugs.py` |
| Formatter apagava `@derive` | `@derive(Eq, Debug)` removido no `lumina fmt` | `_format_attrs()` reemite atributos do parser | `test_runtime_bugs.py` |
| CLI engolia exit code | `lumina run` sempre saía com 0 | `cmd_run` propaga exit; `main()` retorna int | `cli/test_exit_codes.py` |
| `test` com falhas saía com 0 | `lumina test` retornava 0 mesmo com falhas | `cmd_test` retorna nº de falhas | `cli/test_exit_codes.py` |
| `--help` caía em "comando desconhecido" | — | `main()` trata `-h`/`--help`/`help`/sem args | `cli/test_exit_codes.py` |
| `_compile_extra_objects` ignorava `extra_flags` | `.cpp` sem `-DFOO=42` → FFI quebrada | Passa `linker_extra_flags` para clang/clang++ | `cli/test_build.py` |
| Boehm GC nunca ativava | `-lgc` no link era decorativo; codegen usava `malloc` cru | `LLVMCodegen` emite `GC_malloc` + `call GC_init()` | `test_gc.py` |
| Match guard em enum nunca casava | `case Circle(r) if r > 10:` sempre pulava | 4 blocos por case; bind ANTES do guard | `test_match_guard_enum.py` |
| Match guard em str ignorado | `_codegen_match_with_guard` não testava voidptr | Adicionado branch de `strcmp` para voidptr | `test_match_guard_str.py` |
| Self-binding declarava `int` fixo | `case s if s.contains("x")` → "método não implementado para struct int" | `variant_name is None` ANTES de `isinstance(binding, list)` | `test_match_guard_str.py` |
| String literal virava self-binding | `case "build":` casava qualquer string quando havia guard | Parser envolve literal em `StringExpr` | `test_match_guard_str.py` |
| `covered_variants` explodia com multi-pattern | `unhashable type: list` | Achata listas, ignora `None`, honra wildcard | `test_multi_pattern.py` |
| `struct` recompilado no REPL | `P is already defined` (`global_context`) | Cada `LLVMCodegen` cria seu próprio `ir.Context()` | `cli/test_repl.py` |
| `let` em campo `int` aceitava `str` | `Ponto { x: "texto", y: 2 }` imprimia endereço da string | `is_assignable(field_decl_type, value_type)` por campo | `test_struct_field_types.py` |
| **`defer` em `if` não tomado rodava** | `if false: defer print("x")` imprimia `x` no fim da função | Escopo de bloco (Sprint 8b) | `test_defer_scope.py` |
| **`defer` em TCO era ignorado** | `return self(...)` pulava os defers pendentes | `_emit_all_defers()` antes do branch de TCO | `test_tco.py` |
| **`Box<T>` como param não compilava** | `fn put<T>(b: Box<T>, val: T)` → erro de tipo | `unify_type` + `substitute_generic` | `test_nested_generics.py` |
| **LSP rename misturava escopos** | Renomear `i` em `main` mexia no `i` de `helper` | `_filter_refs_for_scope` via `scope_map` | `lsp/tests/test_lsp_keys.py` |

---

## 🧪 Testes Automatizados

### 1. Pytest (unitários + integração)

```bash
pytest tests/ -v
```

| Arquivo | Testes | Cobre |
|---|---|---|
| `test_lexer.py` | 30 | Tokens, strings, indentação, comentários |
| `test_parser.py` | 36 | Declarações, expressões, slices, fluxo |
| `test_semantic.py` | 19 | Escopo, exaustividade, traits |
| `test_types.py` | 24 | Validação de tipo |
| `test_codegen_bugs.py` | 19 | Regressão no codegen (IR + runtime) |
| `test_semantic_bugs.py` | 13 | Regressão no semantic |
| `test_runtime_bugs.py` | 9 | Runtime end-to-end (break, assert, defer, short-circuit, fmt) |
| `test_defer_scope.py` | 7 | Escopo de defer (bloco + TCO) |
| `test_enum_bare_variant.py` | 4 | Variantes bare (`let x = Stop`) |
| `test_gc.py` | 6 | Boehm GC ativa (`GC_init` + `GC_malloc`) |
| `test_tco.py` | 7 | TCO: 5M recursões, defers por iteração, sem call recursivo |
| `test_match_guard_enum.py` | 4 | Guard em enum testa tag + bindings |
| `test_match_guard_str.py` | 4 | Guard em str (self-binding, literais, fallthrough) |
| `test_match_no_guard.py` | 6 | Regressão pós-refactor (int, enum, str, switch) |
| `test_multi_pattern.py` | 8 | `case A \| B:`, wildcard `_`, binding rejeitado |
| `test_nested_generics.py` | 6 | `Box<T>` como parâmetro em `put`/`get` |
| `test_nil.py` | 10 | `nil`, `== nil`, `?.` em nil, `nil` como arg |
| `test_struct_field_types.py` | 6 | Type check em campos de struct literal |
| `test_fmt_comments.py` | 8 | Formatter com comentários |
| `cli/test_build.py` | 2 | `new` → `build` → `run` + `extra_flags` |
| `cli/test_errors.py` | 1 | Comando desconhecido → exit ≠ 0 |
| `cli/test_exit_codes.py` | 7 | Exit codes + `--help` |
| `cli/test_fmt.py` | 1 | Formatter em arquivo válido |
| `cli/test_repl.py` | 10 | REPL persistente |
| `features/test_examples_smoke.py` | 1 | Compila todos os exemplos não-skipados |
| `features/test_language_features.py` | 1 | Output exato de `uncertain_features.lm` |

**Total:** `249 passed, 0 skipped`.

### 2. LSP (isolado)

```bash
cd lumina-vscode
python3 -m pytest tests/test_lsp_keys.py -v   # 8 passed
```

### 3. Script standalone (~5s)

```bash
python3 run_tests.py
```

Valida 28 linhas do `tests/features/uncertain_features.lm`:

```
==============================================================
📊 Resultado: 28/28 verificações OK
==============================================================
```

### 4. Check de exemplos

```bash
./scripts/check_examples.sh              # só compila
./scripts/check_examples.sh --run        # compila + executa
```

```
📊 PASS: 54    ⏭️  SKIP: 17    ❌ FAIL: 0  (modo: run)
```

Os 17 skipados são servidores/sockets/threads que não terminariam sozinhos ou requerem hardware específico.

### 5. `lumina check` (rápido, sem codegen)

```bash
lumina check examples/main.lm
lumina check examples/main.lm --error-format=json | jq .
```

Roda só lexer + parser + semantic (~100ms). Ideal para pre-commit.

---

## 🌍 Cross-Compilação

Compile para qualquer arquitetura suportada pelo `clang`:

```bash
lumina build app.lm --target=aarch64-linux-gnu      # ARM64
lumina build app.lm --target=arm-linux-gnueabihf    # ARMv7
lumina build app.lm --target=riscv64-linux-gnu      # RISC-V 64
lumina build app.lm --target=i386-linux-gnu         # x86 32-bit
lumina build app.lm --target=wasm32-wasi --wasm     # WebAssembly
```

Requer toolchain do target no PATH. Em Ubuntu:

```bash
sudo apt install -y gcc-aarch64-linux-gnu     # ARM64
sudo apt install -y gcc-arm-linux-gnueabihf   # ARMv7
sudo apt install -y gcc-riscv64-linux-gnu     # RISC-V 64
sudo apt install -y qemu-user                 # para emular depois
```

**Nota:** `libgc` precisa ser cross-compilada para o target, ou use `--no-gc`.

---

## 🏎️ Benchmarks de Performance

### CPU (Média de 5 execuções, host: Intel i7, Ubuntu 24.04, `-O3`)

| Teste | C -O2 | Rust -O | **Lumina -O3** | Go | Node.js | Python |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Fibonacci** (N=35) | 0.108s | 0.155s | **0.195s** 🥈 | 0.288s | 1.139s | 5.325s |
| **Loop Matemático** (100M) | 0.018s | 0.022s | **0.021s** 🥇 | 0.201s | 0.395s | — |
| **Crivo de Eratóstenes** (10M) | 0.368s | 0.330s | **0.327s** 🥇 | 0.438s | — | — |
| **Matriz 200×200** | 0.024s | 0.050s | **0.030s** 🥈 | 0.091s | 0.251s | — |

**Resumo:**
- 🥇 **Primes:** 1º lugar — empata com C/Rust, 25% mais rápido que Go
- 🥇 **Loop:** 1º lugar — praticamente idêntico a C/Rust, 10x mais rápido que Go
- 🥈 **Fibonacci:** perde para C/Rust por 1.3-1.8x, 1.5x mais rápido que Go
- 🥈 **Matrix:** perde para C por 1.25x, 3x mais rápido que Go

### Web Server (`wrk -t4 -c100`)
* **Lumina-Serve (epoll):** ~5.868 Requests/sec.

### Rodando

```bash
./scripts/run_benchmarks.sh              # -O2
./scripts/run_benchmarks.sh --release    # -O3
```

---

## 🚀 Como Usar (CLI)

### Pré-requisitos
* **Python 3.11+** e `llvmlite`
* **LLVM** e **Clang** no `PATH`
* **Boehm GC** (`sudo apt install libgc-dev`)
* *(Opcional WASM)* **WASI SDK** em `/opt/wasi-sdk`
* *(Opcional Raylib)* **libraylib**
* *(Opcional Cross-compile)* toolchain do target

### Instalação

```bash
pip install -e .
lumina --help
```

### Comandos Principais

```bash
lumina new meu_projeto          # Cria projeto com lumina.toml
lumina install                  # Baixa dependências
lumina bind header.h nome       # Bindings FFI a partir de C
lumina fmt arquivo.lm           # Formata (preserva comentários e @attrs)
lumina fmt arquivo.lm --check   # Verifica formatação (pre-commit)
lumina clean                    # Limpa cache e binários
lumina run arquivo.lm           # Compila e executa (propaga exit code)
lumina check arquivo.lm         # Lexer+parser+semantic (rápido)
lumina test arquivo.lm          # Suíte de testes nativa
lumina repl                     # REPL persistente (mut/fn entre células)
lumina jit arquivo.lm           # Executa JIT
lumina build                    # Compila (-O2)
lumina build app.lm --release   # -O3
lumina build app.lm --debug     # -O0 + DWARF
lumina build app.lm --wasm      # WebAssembly
lumina build app.lm --no-gc     # Bare-Metal
lumina build app.lm --target=aarch64-linux-gnu
lumina doc                      # Docs HTML
lumina doc --format=md|json
lumina playground               # Playground web (porta 8080)
```

### REPL persistente

```bash
$ lumina repl
🌟 Lumina REPL 2.0 — estado persistente
Dica: use mut x = 0 no topo para estado que persiste. `let` é local à célula.
────────────────────────────────────────────────────────────
lumina> mut counter = 0

lumina> counter = counter + 1

lumina> fn add(a: int, b: int) -> int:
...     return a + b

lumina> print(counter, add(2, 3))
1 5
lumina> :history
[D0] mut counter = 0
[D1] fn add(a: int, b: int) -> int:
    return a + b
[C0] counter = counter + 1
[C1] print(counter, add(2, 3))
lumina> exit
```

Comandos: `:history`, `:decls`, `:clear`, `:help`, `exit`.

---

## 🔗 Configuração de Link (`[link]`)

```toml
[link]
libs = ["m", "raylib"]              # -lm -lraylib
extra_objects = ["helper.cpp"]      # C/C++ compilados e linkados
target = "wasm"                     # força WASM
extra_flags = ["-DFOO=1", "-Iinclude"]
```

O `cmd_build` procura por `[link]` em:
1. **Sidecar** (ao lado do `.lm`): `examples/engine.lm` → `examples/engine.toml`
2. **Fallback**: `./lumina.toml`

Campos:

| Campo | Tipo | Descrição |
|---|---|---|
| `libs` | `List[str]` | Bibliotecas (`-l<nome>`) |
| `extra_objects` | `List[str]` | `.c`/`.cpp` compilados e linkados (respeita `extra_flags`) |
| `target` | `str` | `"wasm"` |
| `extra_flags` | `List[str]` | Flags diretas para clang/clang++ |

**FFI com C++:**
```toml
[link]
extra_objects = ["examples/ffi_helper.cpp"]
extra_flags = ["-DFOO=42"]
```
O `cmd_build` usa `clang++`, passa as `extra_flags` e adiciona `-lstdc++`.

---

## 🌐 WebAssembly

```lumina
export fn fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

```bash
lumina build math.lm --wasm
```

```javascript
WebAssembly.instantiateStreaming(fetch("math.wasm"))
  .then(obj => console.log(obj.instance.exports.fib(35)));
```

---

## 🛠️ Exemplos de Código

### 1. Sintaxe + Switch + Escopo
```lumina
fn avaliar_dia(dia: int) -> str:
    switch dia:
        case 1: return "Domingo"
        case 2: return "Segunda"
        default: return "Dia útil"
```

### 2. Enum Multi-Payload + Multi-pattern + Wildcard
```lumina
enum Par:
    Dois(int, int)
    Zero
    Um

fn main() -> int:
    let p = Dois(10, 20)
    match p:
        case Dois(a, b): print("Par:", a, b)
        case Zero | Um:  print("Zero ou Um")
    return 0
```

### 3. `Option<T>`, `none` e `nil`
```lumina
struct Usuario:
    id: int

fn buscar(id: int) -> Option:
    if id == 42:
        return Some(100)
    return none

fn main() -> int:
    # Option
    let x: Option = none
    match x:
        case Some(v): print("Some:", v)
        case None:    print("None")

    # nil (null real)
    let u: Usuario = nil
    if u == nil:
        print("u é nil")
    let v = u?.id     # null check → 0
    print("v =", v)

    return 0
```

### 4. Genéricos aninhados (`Box<T>` como parâmetro)
```lumina
struct Box<T>:
    data: T

fn put<T>(b: Box<T>, val: T):
    b.data = val

fn get<T>(b: Box<T>) -> T:
    return b.data

fn main() -> int:
    mut bi: Box<int>
    mut bs: Box<str>
    put(bi, 42)
    put(bs, "hello")
    print(get(bi))
    print(get(bs))
    return 0
```

### 5. `defer` com escopo de bloco
```lumina
fn main() -> int:
    defer print("fim da função")

    if 1 == 1:
        defer print("fim do if")
        print("dentro do if")

    for i in 0..2:
        defer print("fim da iteração")
        print("i =", i)

    print("depois do loop")
    return 0

# Saída:
# dentro do if
# fim do if
# i = 0
# fim da iteração
# i = 1
# fim da iteração
# depois do loop
# fim da função
```

### 6. TCO com 5 milhões de recursões
```lumina
fn sum_rec(n: int, acc: int) -> int:
    if n == 0:
        return acc
    return sum_rec(n - 1, acc + n)   # tail call → loop

fn main() -> int:
    print(sum_rec(5000000, 0))   # 12500002500000, sem estourar stack
    return 0
```

### 7. Variantes bare
```lumina
enum Color:
    Red
    Green
    Blue

fn name(c: Color) -> str:
    match c:
        case Red:   return "vermelho"
        case Green: return "verde"
        case Blue:  return "azul"
    return "?"

fn main() -> int:
    let a = Red      # variante bare (Rust None, Haskell Nothing)
    print(name(a))
    return 0
```

### 8. `@derive` + Collections
```lumina
import "std/map"

@derive(Eq, Debug, Clone)
struct Ponto:
    x: int
    y: int

fn main() -> int:
    let p1 = Ponto { x: 1, y: 2 }
    let p2 = p1.clone()
    print(p1 == p2)
    print(p1.__debug__())

    mut m = new_map()
    mut i = 0
    while i < 100:
        m.insert(i, i * 10)   # rehash automático
        i += 1
    print(m.get(42))
    return 0
```

### 9. Traits + Operator Overloading
```lumina
struct Vector2:
    x: int
    y: int

impl Vector2:
    fn __add__(a: Vector2, b: Vector2) -> Vector2:
        mut r: Vector2
        r.x = a.x + b.x
        r.y = a.y + b.y
        return r

fn main() -> int:
    mut a: Vector2
    a.x = 1; a.y = 2
    mut b: Vector2
    b.x = 10; b.y = 20
    let c = a + b
    print(c.x, c.y)
    return 0
```

### 10. Bitwise e Slicing
```lumina
fn main() -> int:
    print(12 & 10)      # 8
    print(1 << 4)       # 16
    let s = "abcdef"
    print(s[1..4])      # bcd
    print(s[..3])       # abc
    return 0
```

---

## 📦 Standard Library (`std/`)

### Fundamentos
* `std/prelude` — `Option` e `Result`
* `std/math`, `std/str`, `std/time`, `std/fs`, `std/alloc`

### Coleções
* `std/vector` — array dinâmico com `reserve` automático
* `std/map` — hash map com rehash quando load ≥ 0.75
* `std/set` — conjunto com rehash
* `std/deque` — fila dupla com `grow()` automático
* `std/list` — linked list
* `std/iter` — adaptadores funcionais

### Testes e Logging
* `std/test` — `check_eq`, `check_ne`, `check_true`, `check_false`, `check_str_eq`
* `std/log` — `log_debug`, `log_info`, `log_warn`, `log_error` + `set_level`/`get_level`

### Concorrência e I/O
* `std/channel` — canais CSP
* `std/async` — green threads (ucontext) — esqueleto, ver limitações
* `std/async_fs`, `std/epoll`, `std/net`, `std/http`

### Integração
* `std/json`, `std/sqlite`, `std/raylib`

---

## 📂 Estrutura do Projeto

```text
Lumina/
├── lumina/                     # Núcleo do Compilador
│   ├── ast/                    #   Árvore Sintática
│   ├── lexer/                  #   Tokenizer (INDENT/DEDENT, COMMENT)
│   ├── parser/                 #   Parser (@attrs, slices, patterns, multi-pattern)
│   ├── semantic/               #   Análise semântica + @derive + traits + unify_type
│   ├── codegen/                #   LLVM IR (globais mutáveis, GC, TCO, defer escopo, cross-target)
│   ├── common/
│   ├── builtins.py
│   └── errors.py
├── lumina_core/                # Bootstrapping (lexer.lm, parser.lm)
├── lumina_cli/                 # CLI + Build + REPL + Test Runner
│   ├── main.py, commands.py, compiler.py
│   ├── playground.py
│   └── utils.py
├── lumina-vscode/              # Extensão VS Code (Syntax + LSP + Semantic Tokens)
│   ├── lumina_lsp.py           # LSP server (hover/references/rename com escopo)
│   └── tests/test_lsp_keys.py
├── std/                        # Standard Library (.lm)
├── benchmarks/                 # Benchmark suite
├── examples/                   # 69 exemplos + sidecars [link] + .expected
├── scripts/
│   ├── check_examples.sh
│   └── run_benchmarks.sh
├── tests/                      # 249 testes em 24 arquivos
├── run_tests.py                # Suite standalone (28 validações)
├── CHANGELOG.md
├── pyproject.toml
└── playground.html
```

---

## 🎨 Extensão VS Code

A extensão `adam-lumina.lumina` oferece:

- **Syntax highlighting** (TextMate)
- **Autocomplete** (keywords, funções, variáveis, structs, enums)
- **Hover** com **escopo qualificado** (`main::i` vs `helper::i`)
- **Go to Definition** (F12 / Ctrl+Click) — ciente de escopo
- **Find References** (Shift+F12) — **filtra pelo escopo** quando o símbolo é local
- **Rename Symbol** (F2) — **ciente de escopo**
- **Document Symbols** (Ctrl+Shift+O) — outline com children por função
- **Semantic Tokens** — cores específicas para funções, parâmetros, variáveis, structs, enum members
- **Diagnostics em tempo real**

### Instalação

```bash
cd lumina-vscode
npx vsce package
code --install-extension lumina-0.2.0.vsix --force
```

Recarregue a janela: `Ctrl+Shift+P` > **Developer: Reload Window**.

Para ativar cores semânticas:

```json
"editor.semanticHighlighting.enabled": true
```

---

## 📝 Notas e Limitações

* **Escape analysis:** coleta dados, mas o codegen ainda aloca todas as structs no heap (Boehm GC cuida).
* **`as` só entre primitivos/ponteiros:** cast entre structs requer método explícito.
* **Pattern matching em structs:** suportado em `MatchExpr`, ainda não em `MatchStmt` exaustivo.
* **`arr[a..]` sem `end`:** em arrays, assume length 0.
* **`comptime`:** literais + aritmética/comparações. Sem chamadas de função.
* **TCO:** apenas self-recursion direta (`return f(args)`). Mutual recursion (`f → g → f`) e tail calls indiretas não otimizadas.
* **`std/async` (coroutines):** FFI não suporta `makecontext` com ponteiro de função. `examples/coroutines.lm` é esqueleto.
* **`std/iter` callbacks:** assinatura `i64 -> i64` (limitado pelo codegen de chamada indireta).
* **`nil` em `MemberExpr` não-safe:** `u.id` com `u == nil` causa SIGSEGV (use `u?.id`). Safe-by-default é trabalho futuro.
* **REPL:** `mut x = 0` no topo persiste; `let x = 10` é local à célula. Recompila tudo a cada célula — O(N²) em sessões longas; use `:clear`.
* **Boehm GC em WASM:** desabilitada (`--target=wasm` força `--no-gc`).
* **`defer` em tail calls:** emitido a cada iteração (Sprint 8d). Custo = N × custo do defer.

---

## 🗺️ Roadmap

- [x] Sintaxe, AST, lexer/parser
- [x] Codegen LLVM, JIT, REPL
- [x] Generics, traits, pattern matching, operator overloading
- [x] Validação de tipo, `[link]`, `-O0/-O2/-O3`
- [x] `SliceExpr`, `Option<T>`, `comptime`
- [x] `lumina check`, `--error-format=json`, `fmt --check`, `doc --format`
- [x] Formatter com comentários e `@attrs`
- [x] `std/iter`, `std/vector`, `std/map`, `std/set`, `std/deque`
- [x] `std/test`, `std/log`
- [x] `@derive(Eq, PartialEq, Debug, Display, Clone, Default)`
- [x] Globais mutáveis
- [x] LSP (hover, rename, references, outline, semantic tokens)
- [x] Cross-compile (`--target`)
- [x] `break` / `continue` funcionais
- [x] `assert` com abort em runtime
- [x] **`defer` com escopo de bloco**
- [x] Short-circuit em `and` / `or`
- [x] Match guard em enum, string e int
- [x] Multi-pattern (`case A | B:`)
- [x] Wildcard (`case _:`)
- [x] Variantes bare de enum
- [x] TCO para self-recursion direta
- [x] Boehm GC ativa
- [x] Type check em campos de struct literal
- [x] CLI com `--help` e exit codes propagados
- [x] REPL persistente
- [x] LSP hover com escopo qualificado
- [x] **Genéricos aninhados (`Box<T>` como parâmetro)**
- [x] **`nil` — null pointer real para structs**
- [x] **Defers emitidos em tail calls**
- [x] **LSP references/rename cientes de escopo**
- [ ] TCO para mutual recursion
- [ ] Safe-by-default: null check em `MemberExpr` não-safe
- [ ] Macros (quasiquote / `@macro`)
- [ ] Self-hosting (bootstrapping)
- [ ] Package registry
- [ ] Code actions (quick fixes) no LSP

---

## 📜 Licença

MIT. Veja [LICENSE](LICENSE).

---

## 📚 Histórico

Veja [CHANGELOG.md](CHANGELOG.md) para o histórico detalhado de mudanças.
