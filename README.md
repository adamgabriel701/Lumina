# 🌟 Lumina Language

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LLVM Version](https://img.shields.io/badge/LLVM-14%2B-blue.svg)](https://llvm.org/)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Alpha%20%2F%20Active-green.svg)](#)
[![Language](https://img.shields.io/badge/Language-Lumina-6A0DAD.svg)](#)
[![Features](https://img.shields.io/badge/features-28%2F28-success.svg)](#-status-de-implementação)
[![Tests](https://img.shields.io/badge/tests-162%20passed%20%2B%201%20skip-brightgreen.svg)](#-testes-automatizados)
[![Examples](https://img.shields.io/badge/examples-69%2F69%20%2B%201%20skip-success.svg)](#)
[![Cross-compile](https://img.shields.io/badge/cross--compile-aarch64%20%7C%20armv7%20%7C%20riscv64%20%7C%20wasm-blueviolet.svg)](#-cross-compilação)

**Lumina** é uma linguagem de programação de sistemas de propósito geral, focada em alta performance, ergonomia moderna, concorrência e segurança de memória. Ela combina a sintaxe limpa e expressiva baseada em indentação (estilo Python/Nim) com o poder de baixo nível e otimização industrial do backend **LLVM**.

A linguagem oferece tipagem estática com inferência, Garbage Collector nativo (Boehm GC), Tipos Algébricos (Enums com multi-payload), Generics com **Monomorphization** (`<T>`), Traits com Métodos Padrão, Standard Library Bootstrapped, Pattern Matching (incluindo destructuring de structs), Canais de Concorrência (CSP), operadores modernos (`|>`, `defer`, `?.`, `?`, `as`, `:=`), interoperabilidade nativa com C/C++ (FFI), suporte a I/O Assíncrono (`epoll`/`O_NONBLOCK`), um REPL interativo, um Web Playground, um LSP completo (com autocomplete, hover, go-to-definition, rename, find-references e **semantic tokens**), compilação incremental, testes nativos com relatório de cobertura, cross-compile para múltiplas arquiteturas, e é **Cross-Platform** (compila para binários nativos x86_64/ARM/RISC-V, WebAssembly e Bare-Metal).

---

## ✨ Funcionalidades Principais

* **Sintaxe Limpa & Ergonômica:** Escopo definido por indentação significativa. Sem chaves `{}` ou pontos e vírgula `;`.
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
* **Tipagem Estática com Inferência:** O compilador deduz os tipos automaticamente, incluindo retornos de métodos, generics, lambdas, operações binárias, `Option<T>` e `comptime`.
* **Generics com Monomorphization:** Tipos genéricos `<T>` geram cópias especializadas em compile-time, garantindo zero overhead em runtime.
* **Tipos Algébricos (ADTs) & Pattern Matching:** `enum`s com multi-payload e extração via `match`/`switch`. Exaustividade validada pelo compilador.
* **`Option<T>` e `NoneExpr`:** `none` é literal dedicado que constrói `Option::None` e é compatível com `ptr` (null pointer).
* **`comptime` real (constant folding):** `comptime(2 + 3 * 4)` vira literal no IR. Suporta `+ - * / %`, comparações e unário `-`.
* **Globais mutáveis:** Top-level `mut X = 0` é emitido como `GlobalVariable` LLVM (suporta reatribuição em runtime).
* **Closures (Lambdas):** `fn(x: int) -> int: x * 2` com function pointers.
* **Ergonomia Moderna:**
  * Sintaxe curta (`x := 10`), escopo de bloco lexical, F-strings (`$"olá {nome}"`), operador pipe (`5 |> dobrar |> imprimir`).
  * Navegação segura (`?.`), propagação de erros (`?`), cast explícito (`as`).
  * Slicing nativo: `s[1..4]`, `arr[..3]`, `arr[2..]`, `arr[..]`.
  * Bitwise (`&`, `|`, `^`, `~`, `<<`, `>>`).
  * `switch`/`case`/`default` com jump table nativa.
  * `defer` e `assert`.
  * **Auto-formatter** (`lumina fmt`) que **preserva comentários** e suporta `--check`.
* **Mensagens Inteligentes:** Sugestões "Did you mean?" + destaque colorido da linha + `--error-format=json`.
* **Concorrência e I/O Assíncrono:** Canais (CSP), green threads (ucontext), epoll + `O_NONBLOCK`.
* **Gerenciamento de Memória:** Boehm GC, structs no heap, Arena Allocator em `--no-gc`.
* **Otimizações:** TCO, constant folding, `-O0/-O2/-O3`, forward declarations, build incremental, DWARF debug info.
* **Configuração de Link (`[link]`):** libs C/C++, extra_objects, targets específicos.
* **Cross-Compile (`--target`):** aarch64, armv7, riscv64, i386, WASM.
* **Ecossistema:** CLI (`pip install`), REPL, Playground, Package Manager (`lumina.toml`), bind C, test runner, `lumina check`, `lumina doc --format=html|md|json`.
* **Extensão VS Code:** Syntax highlight + LSP completo (autocomplete, hover, definition, references, rename, outline, **semantic tokens**).
* **Cross-Platform:** binários nativos, WebAssembly e Bare-Metal.

---

## 📊 Status de Implementação

Todas as features estão funcionando e validadas por CI local:

| # | Feature | Status |
|---|---|---|
| 1 | String Slicing (`s[1..4]`) | ✅ |
| 2 | Array Indexing (`arr[i]`) | ✅ |
| 2b | Array Slicing real (`arr[a..b]`, `arr[..b]`, `arr[a..]`, `arr[..]`) | ✅ |
| 3 | Operador Pipe (`\|>`) | ✅ |
| 4 | Pipe encadeado | ✅ |
| 5 | Safe Navigation (`?.`) | ✅ |
| 6 | Propagação (`?`) | ✅ |
| 7 | `switch` em inteiros | ✅ |
| 8 | `switch` em enums | ✅ |
| 9 | Sintaxe curta (`:=`) | ✅ |
| 10 | Escopo de bloco lexical | ✅ |
| 11 | `defer` | ✅ |
| 12 | `assert` (aborta em runtime) | ✅ |
| 13 | F-strings com múltiplas variáveis | ✅ |
| 14 | Generics + monomorphization | ✅ |
| 15 | Nested structs + member chain | ✅ |
| 16 | Match guard (`case n if n > 10:`) | ✅ |
| 17 | Match em enum com binding | ✅ |
| 18 | Enum multi-payload (`Dois(int, int)`) | ✅ |
| 19 | Cast explícito (`as`) | ✅ |
| 20 | Ponteiros (`&x`, `*p`) | ✅ |
| 21 | Lambda inline | ✅ |
| 22 | Lambda com bloco | ✅ |
| 23 | Trait com método default | ✅ |
| 24 | Match em string | ✅ |
| 25 | `Option<T>` + `NoneExpr` | ✅ |
| 26 | `comptime` (constant folding) | ✅ |
| 27 | `SliceExpr` dedicado | ✅ |
| 28 | Auto-formatter preserva comentários e `@attrs` | ✅ |
| 29 | Operator Overloading (`__add__`, `__eq__`) | ✅ |
| 30 | `@derive(Eq, PartialEq, Debug, Display, Clone, Default)` | ✅ |
| 31 | `std/vector`, `std/map`, `std/set`, `std/deque` (com crescimento) | ✅ |
| 32 | `std/iter` (adaptadores funcionais) | ✅ |
| 33 | `std/test` (framework de testes) | ✅ |
| 34 | `std/log` (níveis + filtro) | ✅ |
| 35 | Globais mutáveis (`mut X = 0` no topo) | ✅ |
| 36 | LSP completo (hover, rename, references, outline) | ✅ |
| 37 | Semantic tokens no LSP | ✅ |
| 38 | Cross-compile (`--target`) | ✅ |
| 39 | `break` / `continue` reais em loops | ✅ |
| 40 | Short-circuit em `and` / `or` | ✅ |

---

## 🐛 Bugs corrigidos

Os bugs abaixo eram **silenciosos** — passavam pelo CI porque os testes originais só exercitavam o parser/semantic, não o runtime. Foram corrigidos e cobertos por `tests/test_runtime_bugs.py`.

| Bug | Sintoma original | Correção |
|---|---|---|
| `break` / `continue` no-op | `for i in 0..100: if i == 5: break` continuava até 100 | Codegen emite `branch` para `end_bb` / `inc_bb` com `loop_stack` |
| `assert` sem efeito | `assert(1 == 2)` imprimia a linha seguinte e saía com código 0 | Codegen emite `fflush(NULL)` + `abort()` + `unreachable` |
| `defer` inline | `defer print("b")` rodava imediatamente, não no fim | Codegen mantém `defer_stack` por função e emite antes de cada `ret` |
| `and` / `or` sem short-circuit | `x != 0 and 10/x > 1` causava SIGFPE | Codegen emite basic blocks `*_rhs` / `*_end` + `phi i1` |
| Formatter apagava `@derive` | `@derive(Eq, Debug)` era removido silenciosamente | `_format_attrs()` emite os atributos anexados pelo parser |

---

## 🧪 Testes Automatizados

### 1. Pytest (unitários + integração)

```bash
pytest tests/ -v
```

| Arquivo | Testes | Cobre |
|---|---|---|
| `test_lexer.py` | 30 | Tokens, strings, indentação, comentários |
| `test_parser.py` | 35 | Declarações, expressões, slices, fluxo |
| `test_semantic.py` | 19 (1 skip) | Escopo, exaustividade, traits |
| `test_types.py` | 24 | Validação de tipo |
| `test_codegen_bugs.py` | 19 | Regressão no codegen (IR + runtime) |
| `test_semantic_bugs.py` | 13 | Regressão no semantic |
| `test_runtime_bugs.py` | 9 | **Runtime end-to-end** (break, assert, defer, short-circuit, fmt) |
| `test_fmt_comments.py` | 8 | Formatter com comentários |
| `cli/` | 3 | Integração da CLI |
| `features/` | 2 | Smoke + uncertain_features |

**Total:** `162 passed, 1 skipped`.

### 2. Script standalone (~5s)

```bash
python3 run_tests.py
```

Valida 28 linhas do `tests/features/uncertain_features.lm`:

```
==============================================================
📊 Resultado: 28/28 verificações OK
==============================================================
```

### 3. Check de exemplos

```bash
./scripts/check_examples.sh              # só compila
./scripts/check_examples.sh --run        # compila + executa
```

Compila todos os 69 exemplos e, no modo `--run`, executa cada binário. Compara com `examples/*.expected` quando existir:

```
📊 PASS: 54    ⏭️  SKIP: 17    ❌ FAIL: 0  (modo: run)
```

### 4. `lumina check` (rápido, sem codegen)

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

Verificar o binário:

```bash
file app            # → ELF 64-bit LSB pie executable, ARM aarch64
qemu-aarch64 -L /usr/aarch64-linux-gnu ./app
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
lumina fmt arquivo.lm           # Formata (preserva comentários)
lumina fmt arquivo.lm --check   # Verifica formatação (pre-commit)
lumina clean                    # Limpa cache e binários
lumina run arquivo.lm           # Compila e executa
lumina check arquivo.lm         # Lexer+parser+semantic (rápido)
lumina test arquivo.lm          # Suíte de testes nativa
lumina repl                     # REPL JIT interativo
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

### Saída JSON

```bash
lumina check app.lm --error-format=json | jq .
# {
#   "type": "error",
#   "message": "Tipo inválido em declaração de 'x': esperado 'int', obteve 'str'.",
#   "filename": "app.lm",
#   "line": 2,
#   "col": 9,
#   "end_col": null,
#   "notes": []
# }
```

Progresso vai para `stderr`, JSON vai para `stdout` — pipe-safe.

---

## 🔗 Configuração de Link (`[link]`)

```toml
[link]
libs = ["m", "raylib"]              # -lm -lraylib
extra_objects = ["helper.cpp"]      # C/C++ compilados e linkados
target = "wasm"                     # força WASM
extra_flags = ["-DFOO=1"]           # flags extras
```

O `cmd_build` procura por `[link]` em:
1. **Sidecar** (ao lado do `.lm`): `examples/engine.lm` → `examples/engine.toml`
2. **Raiz**: `./lumina.toml`

Campos:

| Campo | Tipo | Descrição |
|---|---|---|
| `libs` | `List[str]` | Bibliotecas (`-l<nome>`) |
| `extra_objects` | `List[str]` | `.c`/`.cpp` compilados e linkados |
| `target` | `str` | `"wasm"` |
| `extra_flags` | `List[str]` | Flags diretas para o `clang` |

**FFI com C++:**
```toml
[link]
extra_objects = ["examples/ffi_helper.cpp"]
```
O `cmd_build` usa `clang++` e adiciona `-lstdc++` automaticamente.

**Raylib:**
```toml
[link]
libs = ["raylib"]
```
Requer `libraylib.so` (instruções em `examples/engine.toml`).

**WASM:**
```toml
[link]
target = "wasm"
```
Requer `wasi-sdk` em `/opt/wasi-sdk`.

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

fn main() -> int:
    x := 10
    y := 20
    if x + y == 30:
        let temp = 100
        print("temp =", temp)   # temp morre aqui fora
    print("Hoje é:", avaliar_dia(2))
    return 0
```

### 2. Enum Multi-Payload + Match
```lumina
enum Par:
    Dois(int, int)
    Zero

fn main() -> int:
    let p = Dois(10, 20)
    match p:
        case Dois(a, b): print("Par:", a, b)
        case Zero:       print("Zero")
    return 0
```

### 3. `Option<T>` e `none`
```lumina
fn buscar(id: int) -> Option:
    if id == 42:
        return Some(100)
    return none

fn main() -> int:
    let x: Option = none
    match x:
        case Some(v): print("Some:", v)
        case None:    print("None")
    return 0
```

### 4. `comptime`
```lumina
fn main() -> int:
    let x = comptime(2 + 3 * 4)     # literal 14 no IR
    let y = comptime(10 % 3)         # literal 1
    print(x, y)
    return 0
```

### 5. Slicing
```lumina
fn main() -> int:
    let s = "abcdef"
    print(s[1..4])   # bcd
    print(s[..3])    # abc
    print(s[2..])    # cdef
    return 0
```

### 6. Vector + Map + Set + Deque
```lumina
import "std/vector"
import "std/map"
import "std/set"
import "std/deque"

fn main() -> int:
    mut v = new_vector()
    v.push(10); v.push(20); v.push(30)
    print("sum:", v.sum())

    mut m = new_map()
    mut i = 0
    while i < 100:
        m.insert(i, i * 10)   # rehash automático
        i += 1
    print("get(42):", m.get(42))

    mut s = new_set()
    s.add(1); s.add(2); s.add(1)
    print("size:", s.size)

    mut d = new_deque()
    d.push_back(1); d.push_front(0)
    print("pop_front:", d.pop_front())
    return 0
```

### 7. `std/iter` com lambdas
```lumina
import "std/iter"

fn main() -> int:
    let n = 5
    mut arr = alloc(n)
    arr[0] = 1; arr[1] = 2; arr[2] = 3; arr[3] = 4; arr[4] = 5

    print("Soma:", sum(arr, n))
    let dobrados = map(arr, n, fn(x: int) -> int: x * 2)
    print("Dobrados somam:", sum(dobrados, n))
    print("Pares:", count_if(arr, n, fn(x: int) -> int: (x % 2) == 0))
    return 0
```

### 8. `std/test` — framework de testes
```lumina
import "std/test"

test "soma":
    return check_eq(1 + 1, 2, "1+1 == 2")

test "strings":
    return check_str_eq("a" + "b", "ab", "concat")

fn main() -> int:
    return 0
```

```bash
lumina test examples/test_framework.lm
```

### 9. `std/log` — logging com níveis
```lumina
import "std/log"

fn main() -> int:
    set_level(LOG_LEVEL_INFO)
    log_debug("não aparece")
    log_info("iniciando")
    log_warn("cuidado")
    log_error("falhou")
    return 0
```

### 10. `@derive(Eq, Debug, Default, Clone)`
```lumina
@derive(Eq, Debug, Default, Clone)
struct Ponto:
    x: int
    y: int

fn main() -> int:
    let p1 = new_Ponto()             # Default
    mut p2: Ponto
    p2.x = 10
    p2.y = 20
    let copia = p2.clone()           # Clone
    print("p1 == p2?", p1 == p2)     # Eq
    print(copia.__debug__())         # Debug
    return 0
```

### 11. Traits + Operator Overloading
```lumina
trait Greeter:
    fn name() -> str
    fn greet():
        print("Hello from", name())

struct English:
    dummy: int

impl Greeter for English:
    fn name() -> str:
        return "Lumina"

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
    mut e: English
    e.dummy = 0
    e.greet()

    mut a: Vector2
    a.x = 1; a.y = 2
    mut b: Vector2
    b.x = 10; b.y = 20
    let c = a + b
    print(c.x, c.y)
    return 0
```

### 12. Generics
```lumina
fn identidade<T>(x: T) -> T:
    return x

fn main() -> int:
    print(identidade(10))
    print(identidade(3.14))
    return 0
```

### 13. Safe nav + Propagação
```lumina
fn dividir(a: int, b: int) -> Result:
    if b == 0:
        return Err(1)
    return Ok(a / b)

fn calcular() -> Result:
    let x = dividir(10, 2)?
    let y = dividir(20, 4)?
    return Ok(x + y)

fn main() -> int:
    match calcular():
        case Ok(v):  print("Resultado:", v)
        case Err(e): print("Erro:", e)
    return 0
```

### 14. Canais CSP
```lumina
import "std/channel"

fn main() -> int:
    let c = new(10)
    send(c, 42)
    print("Recebido:", recv(c))
    return 0
```

### 15. Bitwise
```lumina
fn main() -> int:
    print(12 & 10)   # 8
    print(12 | 10)   # 14
    print(12 ^ 10)   # 6
    print(1 << 4)    # 16
    print(256 >> 2)  # 64
    return 0
```

---

## 📦 Standard Library (`std/`)

### Fundamentos
* `std/prelude` — `Option` e `Result`
* `std/math` — funções matemáticas
* `std/str` — `to_upper`, `to_lower`, `trim`, `split`, `join`, `find`, `substr`
* `std/time`, `std/fs`, `std/alloc`

### Coleções
* `std/vector` — array dinâmico com `reserve` automático
* `std/map` — hash map com **rehash** quando load ≥ 0.75
* `std/set` — conjunto com **rehash**
* `std/deque` — fila dupla com **`grow()`** automático
* `std/list` — linked list
* `std/iter` — adaptadores funcionais

### Testes e Logging
* `std/test` — `check_eq`, `check_ne`, `check_true`, `check_false`, `check_str_eq`
* `std/log` — `log_debug`, `log_info`, `log_warn`, `log_error` + `set_level`/`get_level`

### Concorrência e I/O
* `std/channel` — canais CSP
* `std/async` — green threads (ucontext)
* `std/async_fs` — I/O não-bloqueante
* `std/epoll` — event loop
* `std/net`, `std/http`

### Integração
* `std/json`, `std/sqlite`, `std/raylib`

---

## 📂 Estrutura do Projeto

```text
Lumina/
├── lumina/                     # Núcleo do Compilador
│   ├── ast/                    #   Árvore Sintática
│   ├── lexer/                  #   Tokenizer (INDENT/DEDENT, COMMENT)
│   ├── parser/                 #   Parser (@attrs, slices, patterns)
│   ├── semantic/               #   Análise semântica + @derive + traits
│   ├── codegen/                #   LLVM IR (globais mutáveis, cross-target)
│   ├── common/                 #   Cores ANSI
│   ├── builtins.py
│   └── errors.py
├── lumina_core/                # Bootstrapping (lexer.lm, parser.lm)
├── lumina_cli/                 # CLI + Build + REPL + Test Runner
│   ├── main.py, commands.py, compiler.py
│   ├── playground.py           # Web Playground (JIT)
│   └── utils.py
├── lumina-vscode/              # Extensão VS Code (Syntax + LSP + Semantic Tokens)
├── std/                        # Standard Library (.lm)
├── benchmarks/                 # Benchmark suite
├── examples/                   # 69 exemplos + sidecars [link] + .expected
├── scripts/
│   ├── check_examples.sh       # --run compara com .expected
│   └── run_benchmarks.sh
├── tests/
│   ├── test_lexer.py, test_parser.py, test_semantic.py
│   ├── test_types.py, test_codegen_bugs.py, test_semantic_bugs.py
│   ├── test_runtime_bugs.py    # End-to-end em runtime
│   ├── test_fmt_comments.py
│   ├── cli/, features/, fixtures/
├── run_tests.py                # Suite standalone (28 validações)
├── pyproject.toml
└── playground.html
```

---

## 🎨 Extensão VS Code

A extensão `adam-lumina.lumina` oferece:

- **Syntax highlighting** (TextMate)
- **Autocomplete** (keywords, funções, variáveis, structs, enums)
- **Hover** (tipo/assinatura)
- **Go to Definition** (F12 / Ctrl+Click)
- **Find References** (Shift+F12)
- **Rename Symbol** (F2)
- **Document Symbols** (Ctrl+Shift+O) — outline
- **Semantic Tokens** — cores específicas para funções, parâmetros, variáveis, structs, variantes de enum
- **Diagnostics em tempo real**

### Instalação

```bash
cd lumina-vscode
npx vsce package
code --install-extension lumina-0.2.0.vsix --force
```

Recarregue a janela: `Ctrl+Shift+P` > **Developer: Reload Window**.

Para ativar cores semânticas em temas que não suportam por padrão, adicione em `settings.json`:

```json
"editor.semanticHighlighting.enabled": true
```

### Sublime Text

1. Copie `syntaxes/lumina.tmLanguage.json` para `Packages/Lumina/`
2. Instale o pacote `LSP`
3. Configure o LSP para usar `lumina-vscode/lumina_lsp.py`

---

## 📝 Notas e Limitações

* **Escape analysis:** coleta dados, mas o codegen ainda aloca todas as structs no heap (Boehm GC cuida).
* **`as` só entre primitivos/ponteiros:** cast entre structs requer método explícito.
* **Pattern matching em structs:** suportado em `MatchExpr`, ainda não em `MatchStmt`.
* **Validação de tipo por campo:** `P { x: "texto", y: 2 }` com `x: int` só detecta campos ausentes.
* **`arr[a..]` sem `end`:** em arrays, assume length 0.
* **`comptime`:** literais + aritmética/comparações. Sem chamadas de função.
* **`defer`:** roda no fim da **função**, não do bloco. `defer` dentro de um `if` não tomado ainda executa.
* **LSP `references`/`rename`:** varredura léxica (não distingue escopos).
* **LSP `documentSymbol`:** só símbolos de topo + métodos de `impl`.
* **Cross-compile:** `libgc` precisa ser cross-compilada ou usar `--no-gc`.
* **`std/iter` callbacks:** assinatura `i64 -> i64` (limitado pelo codegen de chamada indireta).
* **Genéricos aninhados (`Box<T>` como parâmetro):** o semantic
  aceita `identidade<T>(x: T)` e `Box<int>` como variável local, mas
  **não** `fn put<T>(b: Box<T>, val: T)`. A monomorphization só cobre
  type params diretos. Genéricos aninhados virão em release futura.
* **Null real para structs:** `?.` (safe navigation) funciona em
  ponteiros de struct válidos, mas não há como construir um `Usuario`
  que seja nullptr. `none` constrói `Option::None` (struct alocada),
  não null pointer. Use `?.` para campos opcionais — em breve teremos
  sintaxe para null real.
* **TCO:** ainda **não implementado**. `sum_rec(1000000, 0)` estoura
  stack. Use `N <= 10000` (default 8MB) ou converta para loop. O
  exemplo `tco_test.lm` reflete essa limitação.
  
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
- [x] LSP (hover, references, rename, outline, semantic tokens)
- [x] Cross-compile (`--target`)
- [x] `break` / `continue` funcionais
- [x] `assert` com abort em runtime
- [x] `defer` no fim do escopo de função
- [x] Short-circuit em `and` / `or`
- [ ] `defer` com escopo de bloco (não de função)
- [ ] Self-hosting (bootstrapping)
- [ ] Macros (quasiquote)
- [ ] Package registry
- [ ] Inlay hints no LSP
- [ ] Code actions (quick fixes)

---

## 📜 Licença
MIT. Veja [LICENSE](LICENSE).
