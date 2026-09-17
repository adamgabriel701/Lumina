# 🌟 Lumina Language

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LLVM Version](https://img.shields.io/badge/LLVM-14%2B-blue.svg)](https://llvm.org/)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Alpha%20%2F%20Active-green.svg)](#)
[![Language](https://img.shields.io/badge/Language-Lumina-6A0DAD.svg)](#)
[![Tests](https://img.shields.io/badge/tests-344%20passed%20%7C%201%20xfailed-brightgreen.svg)](#-testes-automatizados)
[![Examples](https://img.shields.io/badge/examples-54%20ran%20%7C%2017%20skip%20%7C%200%20fail-success.svg)](#)
[![Cross-compile](https://img.shields.io/badge/cross--compile-aarch64%20%7C%20armv7%20%7C%20riscv64%20%7C%20wasm-blueviolet.svg)](#-cross-compilação)

**Lumina** é uma linguagem de programação de sistemas de propósito geral, focada em alta performance, ergonomia moderna, concorrência e segurança de memória. Combina a sintaxe limpa e expressiva baseada em indentação (estilo Python/Nim) com o poder de baixo nível e otimização industrial do backend **LLVM**.

A linguagem oferece tipagem estática com inferência, Garbage Collector nativo (Boehm GC), Tipos Algébricos (Enums com multi-payload e variantes bare), Generics com **Monomorphization** incluindo **genéricos aninhados** (`Box<T>` como parâmetro) e **`impl Box<T>`** (métodos em structs genéricas), **Closures** (lambdas que capturam variáveis externas), Traits com Métodos Padrão, Standard Library Bootstrapped, **Tuplas** com destructuring heterogêneo, Pattern Matching (multi-pattern `|`, wildcard `_`, guard, destructuring de structs), **`for x in arr`** e **`for i, x in arr`** sobre iteráveis, **Tail Call Optimization** para self- e mutual-recursion com propagação de `defer`, operador `nil` para null pointer real, **`defer` com escopo de bloco** (Go/Zig-style), **`@safe` opt-in** para null check automático, **`@macro`** para expansão de AST em compile-time, **escape analysis** (arrays locais no stack), Canais de Concorrência (CSP), operadores modernos (`|>`, `?.`, `?`, `as`, `:=`), interoperabilidade nativa com C/C++ (FFI), I/O Assíncrono (`epoll`/`O_NONBLOCK`), um **REPL persistente**, um Web Playground, um LSP completo (hover qualificado por escopo, references e rename cientes de escopo, semantic tokens), um **linter estático** (`lumina lint`), compilação incremental, testes nativos com relatório de cobertura, cross-compile para múltiplas arquiteturas, e é **Cross-Platform** (nativos x86_64/ARM/RISC-V, WebAssembly e Bare-Metal).

📖 **Documentação navegável em [`docs/`](docs/README.md).**

---

## ✨ Funcionalidades Principais

* **Sintaxe Limpa & Ergonômica:** Escopo definido por indentação significativa. Sem chaves `{}` ou `;`.
* **Standard Library Bootstrapped:** Módulos como `std/math`, `std/str`, `std/string`, `std/result`, `std/sort`, `std/vector`, `std/map`, `std/set`, `std/deque`, `std/iter`, `std/test` e `std/log` são escritos 100% na própria Lumina.
* **Coleções Nativas:** `Vector`, `Map`, `Set` e `Deque` — todos com **crescimento automático**.
* **Adaptadores Funcionais (`std/iter`):** `map`, `filter`, `count_if`, `sum`, `sum_by`, `product`, `min`, `max`, `all`, `any`, `find_index`, `copy`, `fill`, `for_each`, `reverse`.
* **`std/sort` — Ordenação:** `sort(arr, n)` e `sort_by(arr, n, cmp)` com insertion sort (n ≤ 16) + quicksort.
* **`std/test` — Framework de Testes:** `check_eq`, `check_ne`, `check_true`, `check_false`, `check_str_eq`.
* **`std/result` — Helpers:** `unwrap`, `unwrap_or`, `is_ok`, `is_err`, `is_ok_and`, `expect`, `map`, `and_then`.
* **`std/string` — StringBuilder:** `push_char`, `push_str`, `finish`, `clear`, com crescimento geométrico.
* **`std/log` — Logging com Níveis:** `DEBUG`, `INFO`, `WARN`, `ERROR` com filtro em runtime.
* **`@derive` Attributes:** `@derive(Eq, PartialEq, Debug, Display, Clone, Default)`.
* **Tipagem Estática com Inferência:** Deduz tipos em retornos, generics aninhados, lambdas, binárias, `Option<T>`, `nil`, **tuplas** e `comptime`.
* **Generics com Monomorphization:** `<T>` gera cópias especializadas. **Aninhados** (`fn put<T>(b: Box<T>, val: T)`) suportados via `unify_type` + `substitute_generic`. **`impl Box<T>:`** permite métodos em structs genéricas, chamados de `Box<int>`, `Box<str>`, etc.
* **Closures:** `fn(x: int) -> int: x + offset` captura `offset` do escopo externo. Captura por valor. Lambda sem captura continua sendo fn pointer cru (compatível com FFI).
* **Tuplas:** `let (a, b, c) = (1, 2, 3)` — tuplas literais com tipos heterogêneos e destructuring sobre tuplas, structs e arrays.
* **`for x in arr` e `for i, x in arr`:** itera sobre arrays literais (via variável ou inline), strings e `alloc(N)` com N constante.
* **Tipos Algébricos (ADTs) & Pattern Matching:** `enum`s com multi-payload. `match`/`switch` com binding, guard, **multi-pattern** (`case A | B:`) e **wildcard** (`case _:`). **Variantes bare** (`let x = Stop`).
* **`Option<T>`, `none` e `nil`:** `none` = `Option::None`. **`nil`** = null pointer real (C-style), compatível com `ptr`/`str`/`fn`/struct. `u?.campo` faz null check.
* **`@safe`:** null check automático em `u.id` e `arr[i]` para funções anotadas.
* **`@macro`:** funções expandidas em compile-time via substituição de AST. Corpo `return <expr>`.
* **`comptime` real (constant folding):** `comptime(2 + 3 * 4)` vira literal.
* **Globais mutáveis:** Top-level `mut X = 0` vira `GlobalVariable` LLVM.
* **Tail Call Optimization:** Self-recursion **e mutual recursion** (`f → g → f`) rodam em stack constante. **`defer` é emitido a cada iteração.**
* **Escape Analysis:** arrays `alloc(N)` com `N` **constante** e sem `return`/`free` viram `alloca` no stack, reduzindo pressão no Boehm GC.
* **Ergonomia Moderna:** sintaxe curta, F-strings, pipe, `?.`, `?`, `as`, slicing, bitwise, `switch`, `defer` (escopo de bloco), `assert` real, **auto-formatter** preservando comentários e `@attrs`, **short-circuit** em `and`/`or`.
* **Mensagens Inteligentes:** "Did you mean?" + `--error-format=json`.
* **Linter (`lumina lint`):** W001 (unused), W002 (shadowing), W003 (unreachable), W004 (unused param), W005 (empty body). Exit code = nº de warnings.
* **Concorrência e I/O Assíncrono:** Canais, green threads, epoll.
* **Gerenciamento de Memória:** Boehm GC ativo (`GC_init` + `GC_malloc`), `--no-gc` para bare-metal.
* **Otimizações:** TCO, constant folding, escape analysis, `-O0/-O2/-O3`, `opt -O2` em `--release`, build incremental, DWARF.
* **Cross-Compile (`--target`):** aarch64, armv7, riscv64, i386, WASM.
* **CLI ergonômica:** `--help`, exit codes propagados, `--error-format=json` pipe-safe.
* **REPL persistente:** `mut` e declarações sobrevivem entre células. Comandos `:history`, `:decls`, `:clear`.
* **LSP completo com escopo:** hover, go-to-definition, find references e rename distinguem variáveis locais homônimas.
* **Cross-Platform:** nativos, WebAssembly e Bare-Metal.

---

## 📊 Status de Implementação

### Linguagem

| # | Feature | Status |
|---|---|---|
| 1 | String Slicing (`s[1..4]`) | ✅ |
| 2 | Array Indexing / Slicing | ✅ |
| 3 | Operador Pipe (`\|>`) / Pipe encadeado | ✅ |
| 4 | Safe Navigation (`?.`) | ✅ |
| 5 | Propagação (`?`) | ✅ |
| 6 | `switch` (int / enum) | ✅ |
| 7 | Sintaxe curta (`:=`) | ✅ |
| 8 | Escopo de bloco lexical | ✅ |
| 9 | **`defer` com escopo de bloco** | ✅ |
| 10 | `assert` (aborta em runtime) | ✅ |
| 11 | F-strings | ✅ |
| 12 | Generics + monomorphization | ✅ |
| 13 | **Genéricos aninhados (`Box<T>` como parâmetro)** | ✅ |
| 14 | **`impl Box<T>:`** (métodos em structs genéricas) | ✅ |
| 15 | Nested structs + member chain | ✅ |
| 16 | **Tuplas literais + destructuring** | ✅ |
| 17 | **`for x in arr`** (arrays e strings) | ✅ |
| 18 | **`for i, x in arr`** (índice + valor) | ✅ |
| 19 | **Closures** (lambda com captura) | ✅ |
| 20 | Match guard (int, enum, str) | ✅ |
| 21 | Enum multi-payload | ✅ |
| 22 | **Multi-pattern (`case A \| B:`)** | ✅ |
| 23 | **Wildcard (`case _:`)** | ✅ |
| 24 | **Variantes bare (`let x = Stop`)** | ✅ |
| 25 | Cast explícito (`as`) | ✅ |
| 26 | Ponteiros (`&x`, `*p`) | ✅ |
| 27 | Lambdas (inline e bloco) | ✅ |
| 28 | Trait com método default | ✅ |
| 29 | Match em string | ✅ |
| 30 | `Option<T>` + `NoneExpr` + **`nil` (null real)** | ✅ |
| 31 | `comptime` (constant folding) | ✅ |
| 32 | `SliceExpr` dedicado | ✅ |
| 33 | Auto-formatter (comentários + `@attrs` + multi-pattern) | ✅ |
| 34 | Operator Overloading | ✅ |
| 35 | `@derive(...)` | ✅ |
| 36 | `std/{vector,map,set,deque}` | ✅ |
| 37 | `std/iter`, `std/test`, `std/log` | ✅ |
| 38 | **`std/result`** (unwrap, map, and_then) | ✅ |
| 39 | **`std/string`** (StringBuilder) | ✅ |
| 40 | **`std/sort`** (sort, sort_by) | ✅ |
| 41 | Globais mutáveis | ✅ |
| 42 | LSP (hover/rename/references/outline/semantic tokens) | ✅ |
| 43 | **LSP com escopo qualificado** | ✅ |
| 44 | Cross-compile (`--target`) | ✅ |
| 45 | `break` / `continue` | ✅ |
| 46 | Short-circuit em `and` / `or` | ✅ |
| 47 | Type check em campos de struct literal | ✅ |
| 48 | TCO para self-recursion | ✅ |
| 49 | **TCO para mutual recursion (SCC dispatcher)** | ✅ |
| 50 | Boehm GC ativa | ✅ |
| 51 | REPL persistente | ✅ |
| 52 | **`@safe` (null check opt-in)** | ✅ |
| 53 | **`@macro` (expansão de AST)** | ✅ |
| 54 | **Defers emitidos em tail calls** | ✅ |
| 55 | **Escape analysis** (alloca para alloc const sem escape) | ✅ |

### CLI

| # | Feature | Status |
|---|---|---|
| 1 | `lumina new`, `build`, `run`, `check`, `test`, `clean`, `doc`, `install`, `bind`, `fmt` | ✅ |
| 2 | `lumina repl` (persistente), `jit`, `playground` | ✅ |
| 3 | **`lumina lint`** (W001..W005) | ✅ |
| 4 | `--help` / `-h` / `help` | ✅ |
| 5 | Exit codes propagados | ✅ |
| 6 | `--error-format=json` (pipe-safe) | ✅ |
| 7 | `[link]` com `libs`, `extra_objects`, `target`, `extra_flags` | ✅ |
| 8 | **`opt -O2` em `--release`** | ✅ |

---

## 🐛 Bugs corrigidos

Os bugs abaixo eram **silenciosos** — passavam pelo CI porque os testes originais só exercitavam parser/semantic, não runtime. Cada um tem teste de regressão.

| Bug | Sintoma original | Correção | Teste |
|---|---|---|---|
| `break` / `continue` no-op | `for i in 0..100: if i == 5: break` continuava até 100 | `loop_stack` com branch para `end_bb`/`inc_bb` | `test_runtime_bugs.py` |
| `assert` sem efeito | `assert(1 == 2)` imprimia a linha seguinte e saía com 0 | `fflush(NULL)` + `abort()` + `unreachable` | `test_runtime_bugs.py` |
| `defer` inline | `defer print("b")` rodava imediatamente | `defer_stack` por função | `test_runtime_bugs.py` |
| `defer` em `if` não tomado rodava | `if false: defer print("x")` imprimia `x` | Escopo de bloco | `test_defer_scope.py` |
| `defer` em TCO era ignorado | `return self(...)` pulava defers | `_emit_all_defers()` antes do branch de TCO | `test_tco.py` |
| `and` / `or` sem short-circuit | `x != 0 and 10/x > 1` causava SIGFPE | Basic blocks + `phi i1` | `test_runtime_bugs.py` |
| Formatter apagava `@derive` | `@derive(Eq, Debug)` removido no `lumina fmt` | `_format_attrs()` | `test_runtime_bugs.py` |
| CLI engolia exit code | `lumina run` sempre saía com 0 | `cmd_run` propaga exit | `cli/test_exit_codes.py` |
| `test` com falhas saía com 0 | `lumina test` retornava 0 | `cmd_test` retorna nº de falhas | `cli/test_exit_codes.py` |
| `--help` caía em "comando desconhecido" | — | `main()` trata `-h`/`--help`/`help`/sem args | `cli/test_exit_codes.py` |
| `_compile_extra_objects` ignorava `extra_flags` | `.cpp` sem `-DFOO=42` | Passa `linker_extra_flags` para clang/clang++ | `cli/test_build.py` |
| Boehm GC nunca ativava | `-lgc` era decorativo | `GC_malloc` + `call GC_init()` | `test_gc.py` |
| Match guard em enum nunca casava | `case Circle(r) if r > 10:` sempre pulava | 4 blocos por case; bind ANTES do guard | `test_match_guard_enum.py` |
| Match guard em str ignorado | `_codegen_match_with_guard` não testava voidptr | Branch de `strcmp` para voidptr | `test_match_guard_str.py` |
| Self-binding declarava `int` fixo | `case s if s.contains("x")` falhava | `variant_name is None` antes de `isinstance(binding, list)` | `test_match_guard_str.py` |
| String literal virava self-binding | `case "build":` casava qualquer string | Parser envolve literal em `StringExpr` | `test_match_guard_str.py` |
| `covered_variants` explodia com multi-pattern | `unhashable type: list` | Achata listas, ignora `None`, honra wildcard | `test_multi_pattern.py` |
| `struct` recompilado no REPL | `P is already defined` | Cada `LLVMCodegen` cria seu próprio `ir.Context()` | `cli/test_repl.py` |
| `let` em campo `int` aceitava `str` | `Ponto { x: "texto", y: 2 }` imprimia endereço | `is_assignable(field_decl_type, value_type)` por campo | `test_struct_field_types.py` |
| `Box<T>` como parâmetro não compilava | `fn put<T>(b: Box<T>, val: T)` → erro | `unify_type` + `substitute_generic` | `test_nested_generics.py` |
| LSP rename misturava escopos | Renomear `i` em `main` mexia no `i` de `helper` | `_filter_refs_for_scope` via `scope_map` | `lsp/tests/test_lsp_keys.py` |
| SCC dispatcher sem `defer_stack` | `AttributeError` em mutual TCO | Init `defer_stack` no entry + reset por membro | `test_tco_mutual.py` |
| `@attrs` sobrescritos como tuples | `@safe`/`@macro` nunca ativavam | Removido override em `parser/parser.py::parse` | `test_safe_mode.py` / `test_macros.py` |
| `read_file()` sem null check | segfault quando arquivo não existe | `phi` retorna string vazia se `fopen == NULL` | `examples/database.lm` |
| `free()` rejeitava `i64*` | `TypeError: i8* != i64*` | `bitcast` antes do call | `test_escape_analysis.py` |
| `chr`/`atoi` sem branch no codegen | retornavam `0` sempre | Branches dedicados em `calls.py` | `test_std_result.py` |
| `SliceExpr` virava `ptr` | `s[..3] == "abc"` comparava endereços | Infere tipo da fonte (`str` → `str`) | `examples/string_methods_test.lm` |
| `bool` → `int` com `sext` | `true` virava `-1` | `zext` quando origem é `i1` | `test_codegen_bugs.py` |
| `for x in arr` perdia o `N` | loop vazio (N=0) | `array_lengths` no codegen, consultado por `_visit_for_iterable` | `test_forin.py` |
| `impl Box<T>` chamado em `Box<int>` | `%"Box"* != %"Box_int_"*` | `bitcast` para o tipo base quando cai no fallback | `test_generic_impl.py` |
| `std/result::unwrap_or` usava `default` | keyword reservada | Renomeado para `fallback` | `test_std_result.py` |
| `and_then` retornava `int` para function pointers | `_require_assignable` rejeitava `Result` | Retorna `None` (tipo desconhecido) | `test_std_result.py` |
| `lumina lint` estourava `RecursionError` | recursão mútua `_collect_vars`/`_collect_exprs` | Reescrito como `_collect` única | `test_lint.py` |
| Variante de enum com payload usada bare | `let x = Some` compilava silenciosamente | Semantic rejeita se variante tem payload | `test_enum_bare_variant.py` |
| `fn_name` usado como valor | `sort(arr, n, _cmp_asc)` → "Variável não declarada" | Semantic retorna `"fn"`, codegen bitcast p/ voidptr | `test_sort.py` |
| Indirect call com N args | `cmp(a, b)` só passava `a` | `fn_ty = i64 (i64) * n_args` | `test_sort.py` |
| `impl Box<T>:` chamando método base | `%"Box"* != %"Box_int_"*` | Bitcast no `codegen_method_call` fallback | `test_generic_impl.py` |

---

## 🧪 Testes Automatizados

### 1. Pytest (unitários + integração)

```bash
pytest tests/ -v
# 344 passed, 1 xfailed
```

O `1 xfailed` é `test_sort_closure_captures` — closures com captura passadas como callback para outra função ainda não funcionam (o tipo `fn` é `voidptr` e não distingue raw fn ptr de bloco `{fn, env}`). Marcado como esperado-falha.

| Arquivo | Testes | Cobre |
|---|---|---|
| `test_lexer.py` | 30 | Tokens, strings, indentação, comentários |
| `test_parser.py` | 36 | Declarações, expressões, slices, fluxo |
| `test_semantic.py` | 19 | Escopo, exaustividade, traits |
| `test_types.py` | 24 | Validação de tipo |
| `test_codegen_bugs.py` | 19 | Regressão no codegen (IR + runtime) |
| `test_semantic_bugs.py` | 13 | Regressão no semantic |
| `test_runtime_bugs.py` | 9 | Runtime end-to-end |
| `test_closures.py` | **10** | **Closures (captura, escopo, nested)** |
| `test_defer_scope.py` | 7 | Escopo de defer (bloco + TCO) |
| `test_enum_bare_variant.py` | 4 | Variantes bare |
| `test_escape_analysis.py` | 4 | Escape analysis (alloca vs GC) |
| `test_forin.py` | 9 | `for x in arr` |
| `test_gc.py` | 6 | Boehm GC ativa |
| `test_generic_impl.py` | 6 | `impl Box<T>:` |
| `test_lint.py` | 14 | `lumina lint` (W001..W005) |
| `test_tco.py` | 7 | TCO self-recursion |
| `test_tco_mutual.py` | 6 | TCO mutual recursion |
| `test_match_guard_enum.py` | 4 | Guard em enum |
| `test_match_guard_str.py` | 4 | Guard em str |
| `test_match_no_guard.py` | 6 | Regressão pós-refactor |
| `test_multi_pattern.py` | 8 | `case A \| B:`, wildcard |
| `test_nested_generics.py` | 6 | `Box<T>` como parâmetro |
| `test_nil.py` | 10 | `nil`, `== nil`, `?.` em nil |
| `test_struct_field_types.py` | 6 | Type check em campos |
| `test_safe_mode.py` | 6 | `@safe` |
| `test_macros.py` | 6 | `@macro` |
| `test_sort.py` | **10 (1 xfail)** | **`std/sort` + `for i, x in arr`** |
| `test_std_result.py` | 9 | `std/result` helpers |
| `test_tuples.py` | 7 | Tuplas literais + destructuring |
| `test_fmt_comments.py` | 8 | Formatter com comentários |
| `cli/test_build.py` | 2 | `new` → `build` → `run` |
| `cli/test_errors.py` | 1 | Comando desconhecido |
| `cli/test_exit_codes.py` | 7 | Exit codes + `--help` |
| `cli/test_fmt.py` | 1 | Formatter em arquivo válido |
| `cli/test_repl.py` | 10 | REPL persistente |
| `features/test_examples_smoke.py` | 1 | Compila exemplos não-skipados |
| `features/test_language_features.py` | 1 | Output exato de `uncertain_features.lm` |

**Total:** `344 passed, 1 xfailed`.

### 2. LSP (isolado)

```bash
cd lumina-vscode
python3 -m pytest tests/test_lsp_keys.py -v   # 8 passed
```

### 3. Script standalone (~5s)

```bash
python3 run_tests.py
# 📊 Resultado: 28/28 verificações OK
```

### 4. Check de exemplos

```bash
./scripts/check_examples.sh --run
# 📊 PASS: 54    ⏭️  SKIP: 17    ❌ FAIL: 0
```

Os 17 skipados são servidores/sockets/threads que não terminariam sozinhos.

---

## 🌍 Cross-Compilação

```bash
lumina build app.lm --target=aarch64-linux-gnu      # ARM64
lumina build app.lm --target=arm-linux-gnueabihf    # ARMv7
lumina build app.lm --target=riscv64-linux-gnu      # RISC-V 64
lumina build app.lm --target=i386-linux-gnu         # x86 32-bit
lumina build app.lm --target=wasm32-wasi --wasm     # WebAssembly
```

Requer toolchain do target no PATH. Em Ubuntu:

```bash
sudo apt install -y gcc-aarch64-linux-gnu gcc-arm-linux-gnueabihf \
                    gcc-riscv64-linux-gnu qemu-user
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

**Web Server (`wrk -t4 -c100`):** ~5.868 Requests/sec (epoll).

---

## 🚀 Como Usar (CLI)

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
lumina lint arquivo.lm          # Análise estática (W001..W005)
lumina clean                    # Limpa cache e binários
lumina run arquivo.lm           # Compila e executa (propaga exit code)
lumina check arquivo.lm         # Lexer+parser+semantic (rápido)
lumina test arquivo.lm          # Suíte de testes nativa
lumina repl                     # REPL persistente
lumina jit arquivo.lm           # Executa JIT
lumina build app.lm --release   # -O3 + opt -O2 no IR
lumina build app.lm --debug     # -O0 + DWARF
lumina build app.lm --wasm      # WebAssembly
lumina build app.lm --no-gc     # Bare-Metal
lumina build app.lm --target=aarch64-linux-gnu
lumina doc --format=html|md|json
lumina playground               # Playground web (8080)
```

### Lint

```bash
lumina lint app.lm                  # texto colorido
lumina lint app.lm --format=json    # JSON
lumina lint app.lm --quiet          # só exit code
```

Exit code = nº de warnings (0 = limpo).

---

## 🔗 Configuração de Link (`[link]`)

```toml
[link]
libs = ["m", "raylib"]              # -lm -lraylib
extra_objects = ["helper.cpp"]      # C/C++ compilados e linkados
target = "wasm"                     # força WASM
extra_flags = ["-DFOO=1", "-Iinclude"]
```

O `cmd_build` procura por `[link]` em **sidecar** (`examples/engine.lm` → `examples/engine.toml`) ou em **`./lumina.toml`**.

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

### 1. Closures

```lumina
fn main() -> int:
    let offset = 10
    let add = fn(x: int) -> int: x + offset
    print(add(5))         # 15
    return 0
```

Captura por valor: mutação posterior da variável externa não é vista.

### 2. `std/sort` + `for i, x in arr`

```lumina
import "std/sort"

fn main() -> int:
    mut arr = alloc(5)
    arr[0] = 5
    arr[1] = 2
    arr[2] = 8
    arr[3] = 1
    arr[4] = 9

    sort(arr, 5)
    for i, x in arr:
        print(i, x)
    # 0 1
    # 1 2
    # 2 5
    # 3 8
    # 4 9
    return 0
```

### 3. `for x in arr` + tuplas

```lumina
fn main() -> int:
    let nums = [10, 20, 30]
    for n in nums:
        print(n)

    let (a, b, c) = (1, 2, 3)
    print(a + b + c)      # 6
    return 0
```

### 4. `impl Box<T>:` — métodos em structs genéricas

```lumina
struct Box<T>:
    data: T

impl Box<T>:
    fn get() -> int:
        return self.data
    fn set(v: int):
        self.data = v

fn main() -> int:
    mut b: Box<int>
    b.set(42)
    print(b.get())       # 42
    return 0
```

### 5. `std/result` + `map`

```lumina
import "std/result"

fn divide(a: int, b: int) -> Result:
    if b == 0:
        return Err(1)
    return Ok(a / b)

fn main() -> int:
    let r = divide(10, 2)
    print("is_ok:", is_ok(r))               # 1
    print("unwrap:", unwrap(r))             # 5

    let e = divide(10, 0)
    print("is_err:", is_err(e))             # 1
    print("unwrap_or:", unwrap_or(e, -1))   # -1

    let doubled = map(r, fn(x: int) -> int: x * 2)
    print("map:", unwrap(doubled))          # 10
    return 0
```

### 6. `@safe` — null check automático

```lumina
struct Usuario:
    id: int

@safe
fn get_id(u: Usuario) -> int:
    return u.id     # 0 se u == nil, senão u.id

fn main() -> int:
    let u: Usuario = nil
    print(get_id(u))    # 0
    return 0
```

### 7. `@macro` — expansão de AST

```lumina
@macro
fn dobro(x: int) -> int:
    return x * 2

fn main() -> int:
    let a = 5
    print(dobro(a + 1))    # (a + 1) * 2 = 12
    return 0
```

### 8. TCO mutual recursion — 1M chamadas

```lumina
fn is_even(n: int) -> int:
    if n == 0:
        return 1
    return is_odd(n - 1)

fn is_odd(n: int) -> int:
    if n == 0:
        return 0
    return is_even(n - 1)

fn main() -> int:
    print(is_even(1000000))    # 1, sem estourar stack
    return 0
```

### 9. Escape analysis — array local no stack

```lumina
fn main() -> int:
    let buf = alloc(10)        # vira alloca, não GC_malloc
    buf[0] = 42
    print(buf[0])              # 42
    return 0
```

### 10. `nil` (null real) vs `none` (Option)

```lumina
struct Usuario:
    id: int

fn main() -> int:
    let u: Usuario = nil
    if u == nil:
        print("u é nil")
    let v = u?.id       # null check → 0

    let x: Option = none
    match x:
        case Some(v): print("Some:", v)
        case None:    print("None")
    return 0
```

### 11. Genéricos aninhados

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
    print(get(bi))    # 42
    print(get(bs))    # hello
    return 0
```

### 12. `defer` com escopo de bloco

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
# dentro do if / fim do if
# i = 0 / fim da iteração
# i = 1 / fim da iteração
# depois do loop / fim da função
```

### 13. Match — multi-pattern + wildcard + variantes bare

```lumina
enum Color:
    Red
    Green
    Blue

fn classify(n: int) -> str:
    match n:
        case 1 | 2 | 3: return "pequeno"
        case 4 | 5:     return "médio"
        case _:         return "grande"
    return "?"

fn main() -> int:
    let c = Red                 # variante bare
    print(classify(2))          # pequeno
    print(classify(99))         # grande
    return 0
```

### 14. `@derive` + Collections

```lumina
import "std/map"

@derive(Eq, Debug, Clone)
struct Ponto:
    x: int
    y: int

fn main() -> int:
    let p1 = Ponto { x: 1, y: 2 }
    let p2 = p1.clone()
    print(p1 == p2)             # true
    print(p1.__debug__())       # Ponto { x: 1, y: 2 }

    mut m = new_map()
    mut i = 0
    while i < 100:
        m.insert(i, i * 10)     # rehash automático
        i += 1
    print(m.get(42))            # 420
    return 0
```

### 15. Traits + Operator Overloading

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
    print(c.x, c.y)    # 11 22
    return 0
```

---

## 📦 Standard Library (`std/`)

### Fundamentos
`prelude` (Option, Result), `math`, `str`, `string` (StringBuilder), `result`, `sort`, `time`, `fs`, `alloc`.

### Coleções
`vector`, `map`, `set`, `deque`, `list`, `iter`.

### Testes e Logging
`test`, `log`.

### Concorrência e I/O
`channel`, `async`, `async_fs`, `epoll`, `net`, `http`.

### Integração
`json`, `sqlite`, `raylib`.

---

## 📂 Estrutura do Projeto

```text
Lumina/
├── lumina/                     # Compilador
│   ├── ast/                    #   Árvore Sintática
│   ├── lexer/                  #   Tokenizer (INDENT/DEDENT, COMMENT)
│   ├── parser/                 #   Parser (@attrs, slices, tuples, generics, for-in)
│   ├── semantic/               #   Análise semântica + unify_type + closures
│   ├── codegen/                #   LLVM IR (GC, TCO, defer, SCC, macros, @safe, escape, closures)
│   └── errors.py
├── lumina_cli/                 # CLI + Build + REPL + Test Runner + Lint
├── lumina-vscode/              # Extensão VS Code + LSP
├── lumina_core/                # Self-hosting (experimental)
├── std/                        # Standard Library (.lm)
├── benchmarks/                 # Benchmark suite
├── examples/                   # 69 exemplos + sidecars [link]
├── scripts/                    # check_examples.sh, run_benchmarks.sh
├── tests/                      # 344 testes em 35 arquivos
├── docs/                       # Documentação navegável
├── run_tests.py                # Suite standalone (28 validações)
├── CHANGELOG.md
├── pyproject.toml
└── playground.html
```

---

## 🎨 Extensão VS Code

- Syntax highlighting (TextMate)
- Autocomplete
- **Hover** com escopo qualificado (`main::i` vs `helper::i`)
- **Go to Definition** — ciente de escopo
- **Find References** — **filtra por escopo** em locais
- **Rename Symbol** — **ciente de escopo**
- **Document Symbols** — outline com children por função
- **Semantic Tokens**
- **Diagnostics em tempo real**

### Instalação

```bash
cd lumina-vscode
npx vsce package
code --install-extension lumina-0.2.0.vsix --force
```

Ativar cores semânticas em `settings.json`:

```json
"editor.semanticHighlighting.enabled": true
```

---

## 📝 Notas e Limitações

* **Escape analysis:** só `alloc(N)` com `N` **constante** e sem `return`/`free`. Casos dinâmicos vão para GC.
* **`as` só entre primitivos/ponteiros:** cast entre structs requer método explícito.
* **Pattern matching em structs:** suportado em `MatchExpr`, ainda não em `MatchStmt` exaustivo.
* **`arr[a..]` sem `end`:** em arrays, assume length 0.
* **`comptime`:** literais + aritmética/comparações. Sem chamadas de função.
* **TCO:** self-recursion **e** mutual recursion diretas. Tail calls indiretas (via function pointer) não otimizadas.
* **TCO + assinaturas incompatíveis:** SCCs com assinaturas diferentes caem no caminho normal (sem TCO).
* **`@safe`:** opt-in. Sem anotação, `u.id` continua C-style (SIGSEGV rápido). Null check só em `MemberExpr`/`IndexExpr`; não cobre FFI.
* **`@macro`:** corpo deve ser um único `return <expr>`. Multi-statement → erro claro.
* **`impl Box<T>`:** o `<T>` é descartado para registro (`Box_get`); chamadas em `Box<int>` fazem bitcast. Funciona porque `Box<int>` e `Box<str>` têm layout idêntico (8 bytes) no LLVM.
* **Closures:** captura por valor (mutação posterior da variável externa não é vista). **Closure passada como callback para outra função** ainda não funciona — o tipo `fn` é `voidptr` e não distingue `{fn, env}` de raw fn pointer. `sort_by` com lambda inline sem captura funciona; com captura, `xfail`.
* **`std/async`:** FFI não suporta `makecontext` com ponteiro de função. `examples/coroutines.lm` é esqueleto.
* **`std/iter` callbacks:** assinatura `i64 -> i64`.
* **`std/result`:** `int`-only por enquanto (o prelude não é genérico).
* **`std/sort`:** insertion sort para n ≤ 16, quicksort acima. Assume array `i64*` (retorno de `alloc`). Para arrays de bytes, converter antes.
* **`opt -O2`:** só em `--release`. Builds normais mantêm o IR cru para inspeção.
* **REPL:** `mut x = 0` persiste; `let x = 10` é local à célula. O(N²) em sessões longas; use `:clear`.
* **Boehm GC em WASM:** desabilitada (`--target=wasm` força `--no-gc`).

---

## 🗺️ Roadmap

- [x] Sintaxe, AST, lexer/parser
- [x] Codegen LLVM, JIT, REPL
- [x] Generics (incl. aninhados), traits, pattern matching
- [x] Type checking em campos de struct
- [x] Cross-compile (`--target`)
- [x] `break` / `continue` reais
- [x] `assert` com abort
- [x] **`defer` com escopo de bloco**
- [x] Short-circuit em `and` / `or`
- [x] Match guard em enum, string e int
- [x] Multi-pattern, wildcard, variantes bare
- [x] TCO para self-recursion
- [x] **TCO para mutual recursion (SCC)**
- [x] **Defers emitidos em tail calls**
- [x] Boehm GC ativa
- [x] CLI com `--help` e exit codes propagados
- [x] REPL persistente
- [x] LSP hover/references/rename cientes de escopo
- [x] **`nil` — null pointer real**
- [x] **`@safe` (opt-in null check)**
- [x] **`@macro` (expansão de AST)**
- [x] **Escape analysis** (stack allocation)
- [x] **`lumina lint`** (W001..W005)
- [x] **`for x in arr`** + **Tuplas**
- [x] **`impl Box<T>:`** e **`std/result`**
- [x] **`std/string`** (StringBuilder)
- [x] **`opt -O2`** em `--release`
- [x] **Closures** (captura por valor)
- [x] **`for i, x in arr`**
- [x] **`std/sort`**
- [ ] Closures como callback (tipo `Fn` distinto)
- [ ] Safe-by-default global (sem `@safe` explícito)
- [ ] Macros multi-statement / quasiquote
- [ ] Self-hosting (bootstrapping)
- [ ] Package registry
- [ ] Code actions (quick fixes) no LSP
- [ ] Inlay hints no LSP

---

## 📜 Licença

MIT. Veja [LICENSE](LICENSE).

## 📚 Documentação

- [`docs/README.md`](docs/README.md) — índice navegável
- [`CHANGELOG.md`](CHANGELOG.md) — histórico detalhado