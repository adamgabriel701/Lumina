# 🌟 Lumina

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LLVM](https://img.shields.io/badge/LLVM-14%2B-blue.svg)](https://llvm.org/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Alpha-green.svg)](#-status)
[![Tests](https://img.shields.io/badge/tests-428%20passed-brightgreen.svg)](docs/engineering/tests.md)
[![Examples](https://img.shields.io/badge/examples-54%20ran-success.svg)](examples/)
[![Benchmarks](https://img.shields.io/badge/benchmarks-5%20suites-blue.svg)](benchmarks/results/)
[![Cross-compile](https://img.shields.io/badge/cross--compile-arm64%20%7C%20wasm-blueviolet.svg)](#-cross-compilation)
[![Linker](https://img.shields.io/badge/linker-self--hosted-orange.svg)](docs/internals/linking.md)

**Lumina** é uma linguagem de programação de sistemas com sintaxe limpa baseada em indentação (estilo Python/Nim), backend **LLVM** e foco em ergonomia moderna, concorrência e segurança de memória.

Estática, compilada, sem `;` e sem `{}`. Roda em Linux (x86_64, ARM, RISC-V), WebAssembly e bare-metal.

📖 **Documentação completa em [`docs/`](docs/README.md).**

---

## ✨ Por que Lumina?

**Sintaxe que você lê em voz alta.** Indentação significativa, `|>` para encadear, `?.` para navegação segura, `defer` com escopo de bloco, F-strings.

```lumina
fn main() -> int:
    let usuario = buscar_usuario(42)?
    defer log("fim")
    usuario?.nome |> imprimir
    return 0
```

**Performance de C, ergonomia de linguagem moderna.** Lumina **empata com C** em `fib`, `loop` e `matrix` (mediana de 20 runs, clang -O3 em ambos). `--no-gc` fecha o gap restante em `primes` e `alloc_churn`. Detalhes em [benchmarks](docs/engineering/benchmarks.md).

**Memória sob controle, com rede de segurança.** Boehm GC por padrão (`GC_malloc`), escape analysis coloca arrays locais no stack, `--no-gc` para bare-metal, `@safe` para null check opt-in, `nil` é null pointer real (não um wrapper).

**Metaprogramação real em compile-time.** `@macro` com duas formas (expressão e statement), `@derive(Eq, Debug, Clone, ...)`, `comptime` com constant folding, atributos LLVM (`@inline`, `@cold`).

**Tooling de linguagem séria.** LSP completo com escopo qualificado (hover, go-to-def, references, rename), linter estático (5 warnings), REPL persistente, auto-formatter que preserva comentários e `@attrs`, build incremental, cross-compile, **linker próprio** (`--linker=self`).

**Tipos que ajudam, não atrapalham.** Inferência em 90% dos casos, `Option<T>`, enums com multi-payload, pattern matching com guard e multi-pattern, generics com monomorphization, traits com métodos default, tipos de função com assinatura (`fn(int) -> int`).

---

## 🚀 Quickstart

### 1. Pré-requisitos

```bash
# Ubuntu/Debian
sudo apt install -y llvm-14 clang libgc-dev python3.11 python3-pip

# Fedora
sudo dnf install -y llvm-devel clang gc-devel python3.11
```

### 2. Instale

```bash
git clone https://github.com/adamgabriel701/Lumina.git
cd Lumina
pip install -e .
```

### 3. Rode seu primeiro programa

```bash
lumina new ola
cd ola
lumina run main.lm
# Hello from ola!
```

---

## 👀 A linguagem em 60 segundos

Um programa que exercita ADTs, pattern matching, closures, `defer` e `?` de uma vez:

```lumina
import "std/result"
import "std/io"

enum Resposta:
    Texto(str)
    Numero(int)
    Vazia

fn interpretar(r: Resposta) -> str:
    match r:
        case Texto(s) if s.starts_with("olá"):
            return "saudação"
        case Texto(s):  return s
        case Numero(n): return $"número: {n}"
        case Vazia:     return "—"
    return "?"

fn main() -> int:
    let respostas = [Texto("olá, mundo"), Numero(42), Vazia]
    for i, r in respostas:
        let categoria = interpretar(r)
        write_line($"{i}: {categoria}")
    return 0
```

Saída:

```
0: saudação
1: número: 42
2: —
```

Mais 20 exemplos canônicos em **[`examples/`](examples/)** — closures como callback, macros multi-statement, TCO mutual, `impl Trait for Box<int>`, enums genéricos.

---

## 🧠 Modelo de memória

Uma pergunta que merece resposta direta em linguagem de sistemas:

| Situação | O que acontece |
|---|---|
| `alloc(N)` com `N` variável | **Boehm GC** (`GC_malloc`) |
| `alloc(N)` com `N` literal e sem escape | **stack** (`alloca`), via escape analysis |
| `free(x)` explícito | **Boehm GC** (`GC_free`), sem stack alloc |
| `--no-gc` | Usa `malloc`/`free` da libc |
| `--target=wasm` | Força `--no-gc` (WASM sem libgc) |
| `ptr` | ponteiro bruto (`i64*`) |
| `str` | `i8*` null-terminated |
| `nil` | null pointer C-style |
| `none` | `Option::None` (enum) |
| `u.id` sem `@safe` | acesso C-style — SIGSEGV se `u == nil` |
| `u.id` com `@safe` | null check automático → retorna `0` |
| `u?.id` (safe nav explícito) | null check mesmo sem `@safe` |

O **Boehm GC** é inicializado uma vez em `main` (`GC_init()`), antes de qualquer alocação. `--no-gc` remove essa chamada e usa `malloc` — útil para kernels, embarcados e WASM.

Detalhes de implementação em **[`docs/internals.md`](docs/internals.md#gc)**.

---

## 🔥 Features por tema

### Sistema de tipos

- **Inferência estática** em retornos, lambdas, binárias, generics, `Option<T>`, tuplas e `comptime`.
- **Enums multi-payload** com variantes bare (`let c = Red`), match exaustivo e destructuring.
- **Pattern matching** com guard (`case Circle(r) if r > 10`), multi-pattern (`case 1 | 2 | 3`), wildcard (`case _`) e self-binding (`case s if s.contains("x")`).
- **Generics com monomorphization**, incluindo **aninhados** (`fn put<T>(b: Box<T>, val: T)`).
- **Traits com métodos default** e **especialização em tipo concreto** (`impl Getter for Box<int>`).
- **Type aliases**, inclusive genéricos (`type IPair<B> = Pair<int, B>`).
- **Tipos de função com assinatura** (`fn(int) -> int`), checados em compile-time.
- **Tuplas** com destructuring heterogêneo (`let (a, b) = (1, "x")`).
- **`nil` (null pointer) e `none` (`Option::None`)** como conceitos distintos.

### Memória e segurança

- **Boehm GC** por padrão; **escape analysis** promove `alloc(N)` constantes ao stack.
- **`--no-gc`** para bare-metal e WASM.
- **`@safe`** opt-in para null check em `MemberExpr`/`IndexExpr`.
- **`nil`** como null real (não wrapper), compatível com FFI.
- **`free(x)`** explícito desativa stack alloc (correção de segurança).

### Concorrência

- **Canais CSP** (`std/channel`) com `pthread_mutex` + `pthread_cond`.
- **Green threads** e corrotinas via `ucontext` (experimental).
- **I/O assíncrono** com `epoll` (`std/epoll`) e `O_NONBLOCK` (`std/async_fs`).
- **Servidor HTTP** de exemplo em `std/http` com ~5.8k req/s (epoll).

### Metaprogramação

- **`@macro` com duas formas**: expressão (`nome(args)`) e statement (`nome!(args)`).
- **`@derive(Eq, PartialEq, Debug, Display, Clone, Default)`**.
- **`comptime` real** com constant folding de literais e aritmética.
- **Atributos LLVM** (`@inline`, `@noinline`, `@cold`, `@hot`).

### Tooling

- **Linker próprio** (`lumina build --linker=self`): substitui `clang`/`ld` por `llc` + `lumina-ld` + runtime freestanding. ELF estático, sem libc, sem dynamic linker. Documentação em [`docs/internals/linking.md`](docs/internals/linking.md).
- **LSP completo** com escopo qualificado: hover (`main::i` vs `helper::i`), go-to-def, references, rename, outline, semantic tokens.
- **Linter** (`lumina lint`): W001..W005, exit code = nº de warnings, `--format=json` para CI.
- **Formatter** que preserva comentários, `@attrs`, multi-pattern e wildcard.
- **REPL persistente** com `:history`, `:decls`, `:clear`.
- **Auto-docs** (`lumina doc`) a partir de comentários `##`.
- **Bind FFI** (`lumina bind header.h`) gera `extern fn` de headers C.
- **Web Playground** (JIT ao vivo).
- **Cross-compile** para ARM64, ARMv7, RISC-V, i386, WASM.
- **Compilação incremental** com cache invalidation por hash (inclui fontes do compilador).

### Otimizações

- **Tail Call Optimization** para self-recursion **e mutual recursion** (SCC dispatcher).
- **Defers emitidos em tail calls** (correção silenciosa).
- **Escape analysis** (`alloc(N)` const sem escape → `alloca`).
- **`opt -O2`** no IR antes do clang, apenas em `--release`.
- **`-O0` / `-O2` / `-O3`** + DWARF debug info.

---

## 🔗 Linker próprio

O Lumina tem um linker estático ELF x86_64 escrito em C, invocado via
`lumina build --linker=self`. Ele substitui o `clang`/`ld` na etapa de link,
produzindo um executável **totalmente estático**, sem libc, sem dynamic
linker, sem Boehm GC — a runtime (`rt.c`) implementa as funções que o
codegen emite direto sobre syscalls Linux.

```bash
# Baseline (clang + glibc)
$ lumina build examples/main.lm
$ file examples/main
examples/main: ELF 64-bit LSB pie executable, dynamically linked, ...

# Linker próprio
$ lumina build examples/main.lm --linker=self
$ file examples/main
examples/main: ELF 64-bit LSB executable, statically linked

$ ./examples/main
```

**Cobertura atual** (`linker/triagem.sh examples`):

```
PASS=56  FAIL-COMPILE=0  FAIL-LINK=0  FAIL-RUN=0  SKIP=15
```

Os 15 skips têm motivo documentado: 2 bugs do codegen em aberto, 1 módulo
auxiliar, e 12 que dependem de subsistemas fora do escopo do linker
(pthread, raylib, FFI C++, WASM, servidores que não terminam, ucontext).

Detalhes de arquitetura, extensão e debug em
**[`docs/internals/linking.md`](docs/internals/linking.md)**.

---

## 📚 Exemplos

**[`examples/`](examples/)** tem 71 arquivos cobrindo:

| Categoria | Exemplos |
|---|---|
| **Fundamentos** | `features.lm`, `features_showcase.lm`, `ergonomia.lm` |
| **Generics & types** | `generics_test.lm`, `monomorph_test.lm`, `nested_generics.lm` |
| **Closures & HOFs** | `lambda_test.lm`, `iter_test.lm`, `iterator_test.lm` |
| **Traits & impls** | `trait_test.lm`, `trait_default_test.lm`, `overload_test.lm` |
| **Pattern matching** | `match_expr_test.lm`, `match_struct_test.lm`, `destructure_test.lm` |
| **Macros** | `comptime_test.lm`, `macro_test.lm` |
| **Concorrência** | `threads.lm`, `coroutines.lm`, `async_server.lm` |
| **I/O e web** | `http_framework.lm`, `server.lm`, `proxy.lm` |
| **FFI & raylib** | `ffi_test.lm`, `chip8.lm`, `engine.lm` |
| **Projetos maiores** | `json_parser.lm`, `sql_engine.lm`, `vm.lm`, `search_engine.lm` |
| **Bare-metal & WASM** | `wasm_math.lm`, `wasm_memory.lm`, `wasm_js_interop.lm` |

Verificação automatizada: **[`scripts/check_examples.sh`](scripts/check_examples.sh)**
compila e roda cada um. Suporta `--linker=self` para usar o linker próprio
na etapa de link. Ver [`docs/internals/linking.md`](docs/internals/linking.md)
para detalhes.

---

## 📊 Status

**Alpha / Active.** A linguagem funciona end-to-end para uso real, com cobertura de testes em cada camada:

| Métrica | Valor | Referência |
|---|---|---|
| Testes pytest | **434 passed** | [`docs/engineering/tests.md`](docs/engineering/tests.md) |
| Exemplos compilando | **54 PASS / 17 SKIP / 0 FAIL** (clang) | [`scripts/check_examples.sh`](scripts/check_examples.sh) |
| Exemplos com linker próprio | **56 PASS / 15 SKIP / 0 FAIL** | [`linker/triagem.sh`](linker/triagem.sh) |
| Suite standalone | **28/28** | [`run_tests.py`](run_tests.py) |
| LSP | **8 passed** | [`lumina-vscode/tests/`](lumina-vscode/tests/) |

Testes cobrem **runtime end-to-end** (não só parser/semantic) — cada bug histórico tem teste de regressão. A lista completa de fixes com sintoma, causa e teste associado está em **[`docs/engineering/bugs.md`](docs/engineering/bugs.md)**.

---

## ⚡ Performance

Mediana de 20 execuções com [`hyperfine`](https://github.com/sharkdp/hyperfine),
afinidade fixa em vCPU 1 (`taskset -c 1`), warmup 3, N passado por `argv`.
Host: AMD EPYC 7763 (2 vCPUs compartilhadas, Codespace). Todos os tempos em ms.
C compilado com **clang 18.1.3** (mesmo backend do Lumina).

| Teste | C -O3 | Rust -O3 | **Lumina --release** | Go | **Lumina / C** |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Fibonacci (N=35) | 32.9 | 32.1 | **31.9** | 62.2 | **0.97×** |
| Crivo de Eratóstenes (10M) | 21.8 | 21.7 | 24.3 | 35.9 | 1.11× |
| Loop matemático (100M) | 88.1 | 96.8 | **88.9** | 82.6 | **1.01×** |
| Matriz 200×200 (int64) | 5.5 | 8.0 | **5.4** | 14.3 | **0.97×** |
| Alloc churn (1M, GC) | 13.3 | — | 50.0 | — | 3.77× |

**Variantes `--no-gc` (item #4 do roadmap):**

| Bench | GC | no-GC | Custo do GC |
| :--- | ---: | ---: | ---: |
| primes (1 alloc de 10 MB) | 27.8 | **23.5** | 15% |
| alloc_churn (1M allocs) | 50.0 | **12.2** | 76% |

**Destaques:**

- **Compute-bound (matrix, loop):** **empata com C** (matrix: 5.4 vs 5.5; loop: 88.9 vs 88.1). Mesmo backend LLVM; codegen comparável.
- **Call-heavy (fib):** **empata com C e Rust** (31.9 vs 32.9 / 32.1). A vantagem histórica de "1.25×" era gcc-vs-clang, não Lumina-vs-C.
- **Memory-bound (primes):** 11% atrás de C. O gap está em **System time** — ~3 ms de CPU do `GC_malloc` na alocação inicial de 10 MB. `--no-gc` fecha o gap (23.5 ms, empata com C).
- **Churn (alloc_churn):** 3.77× com GC. O `--no-gc` empata com C (12.2 vs 13.3) — o Boehm GC tem custo real em churn pequeno, e este benchmark **mede isso**.

**Caveats honestos:**

- VM compartilhada: IQR/mediana de 5–60% em várias linhas. A **mediana** é o número reportável; `mean ± σ` seria enganoso (o σ de `fib_c` foi 3.9 ms sobre uma média de 21.9 ms em uma das rodadas).
- C compilado com **clang**, não gcc. Com gcc, `fib_c` cai para ~21 ms — mas aí mede-se `gcc vs clang`, não `C vs Lumina`. O script permite `CC=gcc ./bench.sh` para quem quiser o comparativo cross-compiler.
- Matrix em `int64` nos três. Vetorização: **nenhum** dos compiladores vetoriza o hot loop do matmul 200×200 — é memory-bound no L2 (~1 MB de working set). Os 7 `vector.body` do Lumina são loops de inicialização, não o matmul.

Metodologia completa (flags exatos, código de cada benchmark, critérios de descarte, `bench.sh` comentado) em **[`docs/engineering/benchmarks.md`](docs/engineering/benchmarks.md)**.

---

## 🛠️ CLI

```bash
# Projeto
lumina new meu_projeto              # cria lumina.toml + main.lm
lumina install                      # baixa deps github:* para lumina_modules/
lumina bind header.h nome           # gera FFI bindings de um header C

# Compilar & executar
lumina run arquivo.lm               # compila e executa (propaga exit code)
lumina build arquivo.lm             # só compila
lumina check arquivo.lm             # lexer + parser + semantic (rápido)
lumina jit arquivo.lm               # executa via JIT
lumina build app.lm --release       # -O3 + opt -O2 no IR
lumina build app.lm --debug         # -O0 + DWARF
lumina build app.lm --wasm          # WebAssembly (força --no-gc)
lumina build app.lm --no-gc         # bare-metal
lumina build app.lm --linker=self   # usa lumina-ld (ELF estático)
lumina build app.lm --target=aarch64-linux-gnu

# Qualidade
lumina test arquivo.lm              # suíte de testes nativa
lumina lint arquivo.lm              # W001..W005
lumina fmt arquivo.lm               # formatter (preserva comentários)
lumina doc --format=html|md|json

# Interativo
lumina repl                         # REPL persistente
lumina playground [porta]           # playground web (padrão 8080)

# Manutenção
lumina clean                        # limpa cache e binários
```

Exit codes: `run` propaga o do binário; `test` = nº de falhas; `lint` = nº de warnings; `build`/`check` = 0/1. `--error-format=json` é pipe-safe (progresso vai para stderr).

Detalhes de cada comando em **[`docs/ferramental.md`](docs/ferramental.md)**.

---

## 🌍 Cross-compilation

```bash
lumina build app.lm --target=aarch64-linux-gnu      # ARM64
lumina build app.lm --target=arm-linux-gnueabihf    # ARMv7
lumina build app.lm --target=riscv64-linux-gnu      # RISC-V 64
lumina build app.lm --target=i386-linux-gnu         # x86 32-bit
lumina build app.lm --target=wasm32-wasi --wasm     # WebAssembly
```

Requer toolchain do target no PATH:

```bash
sudo apt install -y gcc-aarch64-linux-gnu gcc-arm-linux-gnueabihf \
                    gcc-riscv64-linux-gnu qemu-user
```

`libgc` precisa estar cross-compilada para o target, ou use `--no-gc`.

**Nota:** `--linker=self` só suporta x86_64 nativo. Para cross-compile ou
WASM, use `--linker=clang` (o padrão).

### WebAssembly

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

## 📖 Documentação

| Documento | Para quem |
|---|---|
| [**Guia Rápido**](docs/guia-rapido.md) | Instalação, primeiro programa, CLI essencial |
| [**Linguagem**](docs/linguagem.md) | Referência completa da sintaxe |
| [**Standard Library**](docs/stdlib.md) | `math`, `sort`, `io`, `result`, `map`, `json`... |
| [**Ferramental**](docs/ferramental.md) | CLI, LSP, formatter, linter, REPL |
| [**Internals**](docs/internals.md) | Pipeline, codegen LLVM, TCO, escape analysis, GC |
| [**Linker**](docs/internals/linking.md) | `lumina-ld` — arquitetura, runtime, integração, extensão |
| [**Contributing**](docs/contributing.md) | Setup de dev, estilo, checklist de PR |

Material de engenharia (para quem mexe no compilador):

- [`docs/engineering/bugs.md`](docs/engineering/bugs.md) — lista completa de bugs corrigidos + identificados (sintoma, causa, teste)
- [`docs/engineering/tests.md`](docs/engineering/tests.md) — os 428 testes por arquivo
- [`docs/engineering/benchmarks.md`](docs/engineering/benchmarks.md) — metodologia completa dos benchmarks

---

## 🤝 Contributing

Contribuições são bem-vindas. Antes de abrir um PR:

```bash
pytest tests/ -q                                  # 434 passed
python3 run_tests.py                              # 28/28
./scripts/check_examples.sh --run                 # 54 PASS / 17 SKIP / 0 FAIL
./linker/triagem.sh examples                      # 56 PASS / 15 SKIP / 0 FAIL
lumina fmt --check <arquivos>                     # se mexeu em .lm
lumina lint <arquivos>                            # sem novos warnings
```

Se você mexeu no linker, rode também:

```bash
( cd linker && make clean && make )
./scripts/check_examples.sh --run --linker=self
```

Checklist completo, estilo de código, como adicionar features e onde pedir ajuda em **[`docs/contributing.md`](docs/contributing.md)**.

---

## 📜 Licença

MIT. Veja [LICENSE](LICENSE).

---

## 🗺️ Roadmap

**Concluído:**

- [x] Lexer/parser/AST com indentação significativa
- [x] Codegen LLVM + JIT + REPL persistente
- [x] Generics (aninhados), traits, pattern matching
- [x] Cross-compile (`--target`)
- [x] TCO self-recursion **e** mutual recursion
- [x] Boehm GC, escape analysis, `--no-gc`
- [x] `nil`, `@safe`, `@macro`, `defer` com escopo de bloco
- [x] `for x in arr`, `for i, x in arr`, tuplas
- [x] Closures com captura (fat pointer unificado)
- [x] `fn(int) -> int` como tipo checado
- [x] `impl Box<T>` **e** `impl Trait for Box<int>`
- [x] Enums genéricos, type aliases (incl. genéricos)
- [x] Macros multi-statement (`nome!(args)`)
- [x] Linter, formatter, `lumina doc`, LSP completo
- [x] **`black_box(x)`** — primitiva nativa anti-DCE
- [x] **`argv(i)` / `atoi`** — parametrização por linha de comando
- [x] **Benchmarks comparáveis** em todas as 5 suites (`bench.sh` com clang, `-fwrapv`, `--no-gc`)
- [x] **Linker próprio** (`lumina-ld`) — ELF estático x86_64, runtime freestanding, paridade com clang no `check_examples.sh`

**Em aberto:**

- [ ] Safe-by-default global (sem `@safe` explícito)
- [ ] Macros com quasiquote
- [ ] Self-hosting (bootstrapping)
- [ ] Package registry
- [ ] Code actions (quick fixes) no LSP
- [ ] Inlay hints no LSP
- [ ] **Escape analysis** para arrays com N dinâmico mas loop-bounded
- [ ] **`std/alloc` arena** como primitiva de 1ª classe para churn controlado
- [ ] **Aliasing hints** (`restrict`/`noalias`) expostos em Lumina
- [ ] **Linker: pthreads** (`pthread_create` via `clone()` + TLS)
- [ ] **Linker: cross-compile** (linkers separados para aarch64, riscv64)
- [ ] **Linker: W^X** (dois segmentos `PT_LOAD` em vez de um RWX)

Detalhes do que já foi feito em **[CHANGELOG.md](CHANGELOG.md)**.