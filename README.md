# 🌟 Lumina Language

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LLVM Version](https://img.shields.io/badge/LLVM-14%2B-blue.svg)](https://llvm.org/)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Alpha%20%2F%20Active-green.svg)](#)
[![Language](https://img.shields.io/badge/Language-Lumina-6A0DAD.svg)](#)
[![Features](https://img.shields.io/badge/features-28%2F28-success.svg)](#-status-de-implementação)
[![Tests](https://img.shields.io/badge/tests-153%20passed%20%2B%201%20skip-brightgreen.svg)](#-testes-automatizados)
[![Examples](https://img.shields.io/badge/examples-66%2F66%20%2B%201%20skip-success.svg)](#)

**Lumina** é uma linguagem de programação de sistemas de propósito geral, focada em alta performance, ergonomia moderna, concorrência e segurança de memória. Ela combina a sintaxe limpa e expressiva baseada em indentação (estilo Python/Nim) com o poder de baixo nível e otimização industrial do backend **LLVM**.

A linguagem oferece tipagem estática com inferência, Garbage Collector nativo (Boehm GC), Tipos Algébricos (Enums com multi-payload), Generics com **Monomorphization** (`<T>`), Traits com Métodos Padrão, Standard Library Bootstrapped, Pattern Matching (incluindo destructuring de structs), Canais de Concorrência (CSP), operadores modernos (`|>`, `defer`, `?.`, `?`, `as`, `:=`), interoperabilidade nativa com C/C++ (FFI), suporte a I/O Assíncrono (`epoll`/`O_NONBLOCK`), um REPL interativo, um Web Playground, um LSP completo (com autocomplete, hover, go-to-definition, rename e find-references), compilação incremental, testes nativos com relatório de cobertura, e é **Cross-Platform** (compila para binários nativos x86_64/ARM, WebAssembly e Bare-Metal).

---

## ✨ Funcionalidades Principais

* **Sintaxe Limpa & Ergonômica:** Escopo definido por indentação significativa. Sem chaves `{}` ou pontos e vírgula `;`.
* **Standard Library Bootstrapped:** Módulos como `std/math`, `std/str`, `std/time`, `std/vector`, `std/map`, `std/set`, `std/deque`, `std/iter` e `std/async_fs` são escritos 100% na própria Lumina.
* **Coleções Nativas:** `Vector` (array dinâmico), `Map` (hash map com rehash automático), `Set` (conjunto com rehash automático) e `Deque` (fila dupla com `grow()` automático) com API consistente de structs + métodos.
* **Adaptadores Funcionais (`std/iter`):** `map`, `filter`, `count_if`, `sum`, `sum_by`, `product`, `min`, `max`, `all`, `any`, `find_index`, `copy`, `fill`, `for_each`, `reverse` — com suporte a lambdas.
* **`@derive` Attributes:** `@derive(Eq, Debug, Default, Clone, Display)` gera automaticamente:
  * `Eq`      → `fn __eq__(a, b) -> int` comparando campo a campo
  * `Debug`   → `fn __debug__(p) -> str` formatando `Nome { f1: v1, f2: v2 }`
  * `Display` → alias de `Debug`
  * `Clone`   → `fn clone() -> Struct` copiando campos de `self`
  * `Default` → `fn new_Struct() -> Struct` com todos os campos zerados
* **Tipagem Estática com Inferência:** O compilador deduz os tipos automaticamente, incluindo retornos de métodos, generics, lambdas, operações binárias, `Option<T>` e `comptime`.
* **Generics com Monomorphization:** Suporte a tipos genéricos `<T>` que geram cópias especializadas em tempo de compilação, garantindo zero overhead de runtime. Cobre funções e structs (`Box<int>`, `Box<float>`, ...).
* **Tipos Algébricos (ADTs) & Pattern Matching:** `enum`s com **múltiplos payloads** (`Dois(int, int)`) e extração via `match` ou `switch`. O compilador checa a exaustividade dos casos.
* **`Option<T>` e `NoneExpr`:** `none` é um literal dedicado que constrói `Option::None` e é compatível com `ptr` (null pointer).
* **`comptime` real (constant folding):** `comptime(2 + 3 * 4)` é avaliado em compile-time e vira um literal no IR.
* **Pattern Matching em Structs:** Destructuring direto no `match` para extrair campos de structs literais.
* **Closures (Lambdas):** Funções anônimas inline (`fn(x: int) -> int: x * 2`) com suporte a **function pointers**.
* **Ergonomia Moderna:**
  * **Sintaxe Curta (`:=`):** Declare variáveis mutáveis rapidamente: `x := 10`.
  * **Escopo de Bloco Lexical:** Variáveis declaradas dentro de `if`/`for`/`while` "morrem" ao sair do bloco.
  * **F-strings Nativas:** `$"Usuário {id} logou."` com múltiplas variáveis.
  * **Operador Pipe (`|>`):** `5 |> dobrar |> imprimir`.
  * **Navegação Segura (`?.`):** Evita Segmentation Faults ao acessar structs nulas (null check nativo no LLVM IR).
  * **Propagação de Erros (`?`):** Retorna erros automaticamente em funções que retornam `Result`.
  * **Casting Explícito (`as`):** `10 as float`, `ptr as int`.
  * **String / Array Slicing:** Fatiamento nativo: `texto[1..5]`, `arr[1..4]`, `arr[..3]`, `arr[2..]`, `arr[..]`.
  * **Operadores Bitwise:** `&`, `|`, `^`, `~`, `<<`, `>>` funcionam em inteiros.
  * **Switch Statements:** Sintaxe limpa de salto (jump table nativa do LLVM) para inteiros e enums.
  * **Defer & Assert:** Garantia de limpeza de escopo e testes nativos.
  * **Auto-Formatter:** `lumina fmt` formata o código automaticamente (AST-based), **preservando comentários** (linha e bloco). Suporta `--check` para pre-commit.
* **Mensagens Inteligentes:** Erros léxicos e semânticos sugerem correções ("Did you mean?") com destaque colorido da linha. Suporta saída JSON (`--error-format=json`) para integração com ferramentas.
* **Concorrência e I/O Assíncrono:**
  * **Canais (CSP):** Comunicação segura entre threads estilo Go usando `pthread_mutex` e `pthread_cond`.
  * **Green Threads:** Suporte a Corrotinas via troca de contexto de CPU (`ucontext`).
  * **Async I/O:** Event Loop não-bloqueante de baixa latência usando `epoll` e `O_NONBLOCK`.
* **Gerenciamento de Memória Avançado:**
  * **Garbage Collector:** Integração nativa com o **Boehm GC** (`libgc`).
  * **Structs no Heap:** Structs locais que podem escapar (retornadas de funções, armazenadas em campos) são alocadas no heap. O Boehm GC cuida da liberação.
  * **Arena Allocator:** Modo Bare-Metal (`--no-gc`) com alocador determinístico.
* **Otimizações de Compilador:**
  * Tail Call Optimization (TCO), Constant Folding, Comptime Evaluation.
  * **Níveis de otimização:** `-O0` (debug), `-O2` (padrão), `-O3` (`--release`).
  * **Forward Declarations:** Funções podem ser chamadas antes de serem definidas no arquivo.
  * **Top-level constants inlined:** `let X = 42` no topo é inline em cada uso.
  * **Build Incremental:** A CLI detecta se o LLVM IR não mudou e pula a linkagem. O hash inclui os fontes do compilador — mudanças em `.py` também invalidam o cache. O hash de link inclui a flag de otimização.
  * **Debug Info (DWARF):** Gera metadados de depuração (`--debug`) permitindo inspectar código `.lm` no GDB/LLDB.
* **Configuração de Link (`[link]`):** Linka bibliotecas C/C++ (`libs`), compila objetos auxiliares (`extra_objects`), força targets (`target = "wasm"`) e passa flags extras ao linker (`extra_flags`), via `lumina.toml` ou sidecar `.toml` ao lado do `.lm`.
* **Ecossistema Integrado:** CLI via `pip install`, REPL, Web Playground (JIT), Package Manager (`lumina.toml`), Auto-Gerador de Bindings C, Test Runner nativo (`lumina test`) com relatório de cobertura via `llvm-cov`, `lumina check` (só lexer+parser+semantic) e `lumina doc --format=html|md|json`.
* **Cross-Platform:** Compila para binários nativos, WebAssembly (`.wasm` com exports diretos para JS) e Bare-Metal.

---

## 📊 Status de Implementação

Todas as 28 features testadas em `tests/features/uncertain_features.lm` estão funcionando e validadas por CI local:

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
| 12 | `assert` | ✅ |
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
| 28 | Auto-formatter preserva comentários | ✅ |
| 29 | Operator Overloading (`__add__`, `__eq__`) | ✅ |
| 30 | `@derive(Eq, Debug, Default, Clone, Display)` | ✅ |
| 31 | `std/vector`, `std/map`, `std/set`, `std/deque` | ✅ |
| 32 | `std/iter` (adaptadores funcionais) | ✅ |
| 33 | LSP completo (hover, rename, references, outline) | ✅ |

---

## 🧪 Testes Automatizados

A suíte é dividida em quatro partes:

### 1. Pytest (unitários + integração)

```bash
pytest tests/ -v
```

Cobre:

| Arquivo | Testes | Cobre |
|---|---|---|
| `test_lexer.py` | 30 | Tokens, strings, indentação, comentários, block comments |
| `test_parser.py` | 35 | Declarações, expressões, slices, controle de fluxo, match |
| `test_semantic.py` | 19 (1 skip) | Escopo, exaustividade, traits, inferência |
| `test_types.py` | 24 | Validação de tipo em VarDecl/Assign/Return/conditions |
| `test_codegen_bugs.py` | 20 | Regressão de bugs no codegen |
| `test_semantic_bugs.py` | 15 | Regressão de bugs no semantic |
| `test_fmt_comments.py` | 8 | Formatter preservando comentários + idempotência |
| `cli/` | 3 | Integração ponta-a-ponta da CLI |
| `features/` | 2 | Smoke tests dos exemplos + uncertain_features |

**Total:** `153 passed, 1 skipped`.

### 2. Script standalone (5 segundos)

```bash
python3 run_tests.py
```

Compila, executa, e valida cada linha esperada do `tests/features/uncertain_features.lm`.

```
==============================================================
📊 Resultado: 28/28 verificações OK
==============================================================

✅ Todos os testes passaram!
```

### 3. Check de exemplos (end-to-end)

```bash
./scripts/check_examples.sh
```

Compila **todos** os 66 arquivos de `examples/`, respeitando a `tests/features/skip.txt`:

```
📊 PASS: 66    ⏭️  SKIP: 1    ❌ FAIL: 0
```

O único skip é `util.lm` — módulo auxiliar que não tem `fn main()`, importado por outros exemplos.

### 4. `lumina check` (rápido, sem codegen)

```bash
lumina check examples/main.lm         # texto colorido
lumina check examples/main.lm --error-format=json | jq .
```

Roda só lexer + parser + semantic. Ideal para pre-commit manual (~100ms).

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
- 🥇 **Primes:** 1º lugar — empata com C e Rust, 25% mais rápido que Go
- 🥇 **Loop:** 1º lugar — praticamente idêntico a C e Rust, 10x mais rápido que Go
- 🥈 **Fibonacci:** perde para C/Rust por 1.3-1.8x, 1.5x mais rápido que Go
- 🥈 **Matrix:** perde para C por 1.25x, 1.6x mais rápido que Rust, 3x mais rápido que Go

### Web Server (`wrk -t4 -c100`)
* **Lumina-Serve (epoll):** ~5.868 Requests/sec.

### Rodando os benchmarks

```bash
./scripts/run_benchmarks.sh              # Lumina em -O2 (padrão)
./scripts/run_benchmarks.sh --release    # Lumina em -O3
```

---

## 🚀 Como Usar (CLI)

### Pré-requisitos
* **Python 3.11+** e `llvmlite` (`pip install llvmlite`)
* **LLVM** e **Clang** no `PATH`
* **Boehm GC** (`sudo apt install libgc-dev`)
* *(Opcional para WASM)* **WASI SDK** instalado em `/opt/wasi-sdk`
* *(Opcional para Raylib)* **libraylib** (compilada de source ou via gerenciador de pacotes)

### Instalação
Após clonar o repositório, instale a CLI globalmente no seu ambiente Python:
```bash
pip install -e .
```
Agora o comando `lumina` está disponível globalmente no seu terminal!

### Comandos Principais
```bash
lumina new meu_projeto          # Cria a estrutura inicial (com lumina.toml)
lumina install                  # Baixa dependências do GitHub via lumina.toml
lumina bind header.h nome       # Gera bindings FFI a partir de um arquivo C
lumina fmt arquivo.lm           # Formata o código (preserva comentários)
lumina fmt arquivo.lm --check   # Verifica formatação sem escrever (pre-commit)
lumina clean                    # Limpa o cache e binários antigos
lumina run arquivo.lm           # Compila e executa o binário nativo
lumina check arquivo.lm         # Só lexer+parser+semantic (rápido)
lumina test arquivo.lm          # Compila e executa a suíte de testes nativa
lumina repl                     # Inicia o console interativo (REPL JIT)
lumina jit arquivo.lm           # Executa instantaneamente na memória RAM
lumina build                    # Compila (default: -O2)
lumina build app.lm --release   # Compila com -O3 (release)
lumina build app.lm --debug     # Compila com -O0 + DWARF (GDB/LLDB)
lumina build app.lm --wasm      # Compila para WebAssembly (.wasm)
lumina build app.lm --no-gc     # Compila para Bare-Metal (sem Garbage Collector)
lumina doc                      # Gera docs em HTML (docs/index.html)
lumina doc --format=md          # Gera docs em Markdown (docs/index.md)
lumina doc --format=json        # Gera docs em JSON (docs/index.json)
lumina playground               # Inicia o Web Playground JIT (porta 8080)
```

### Saída estruturada (JSON)

Qualquer comando que reporta erro aceita `--error-format=json`. Progresso vai para `stderr`, JSON vai para `stdout` — perfeito para pipes:

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

---

## 🔗 Configuração de Link (`[link]`)

A seção `[link]` do `lumina.toml` controla como o `cmd_build` invoca o linker.
Ela permite linkar bibliotecas C/C++, incluir arquivos `.cpp` auxiliares e
forçar targets específicos (como WASM), sem precisar passar flags pela CLI.

### Sintaxe

```toml
[link]
libs = ["m", "raylib"]              # passado como -lm -lraylib
extra_objects = ["helper.cpp"]      # arquivos C/C++ compilados e linkados
target = "wasm"                     # força compilação WASM
extra_flags = ["-DFOO=1"]           # flags extras para o clang
```

### Onde colocar

O `cmd_build` procura por `[link]` em **dois lugares**, nesta ordem:

1. **Sidecar**: ao lado do `.lm` que está sendo compilado.
   ```
   examples/engine.lm       → examples/engine.toml
   examples/ffi_test.lm     → examples/ffi_test.toml
   ```

2. **Raiz do projeto**: `./lumina.toml` (usado quando `entry_file` não é dado).

Isso permite que cada exemplo tenha sua própria configuração de link.

### Campos

| Campo | Tipo | Descrição |
|---|---|---|
| `libs` | `List[str]` | Bibliotecas para linkar (`-l<nome>`). O linker procura em `/usr/lib`, `/usr/local/lib`, `LD_LIBRARY_PATH`, etc. |
| `extra_objects` | `List[str]` | Arquivos `.c`, `.cpp`, `.cc`, `.cxx` que serão **compilados** (por `clang`/`clang++`) e linkados. Os `.o` resultantes são gerados ao lado do fonte. |
| `target` | `str` | Força um target. Valores aceitos: `"wasm"`. |
| `extra_flags` | `List[str]` | Flags extras passadas **diretamente** para o `clang` na linkagem. Útil para `-L`, `-Wl,...`, defines, etc. |

### Exemplos práticos

**FFI com C++:**

```toml
# examples/ffi_test.toml
[link]
extra_objects = ["examples/ffi_helper.cpp"]
```

```cpp
// examples/ffi_helper.cpp
extern "C" void cpp_print_hello() {
    std::printf("Hello from C++\n");
}
```

O `cmd_build` detecta que é `.cpp`, usa `clang++` em vez de `clang`, e
adiciona `-lstdc++` automaticamente.

**Raylib (biblioteca gráfica):**

```toml
# examples/engine.toml
[link]
libs = ["raylib"]
```

Requer `libraylib.so` instalada. Em Ubuntu:

```bash
sudo apt install -y libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev \
    libxi-dev libgl1-mesa-dev libglu1-mesa-dev mesa-common-dev

git clone --depth 1 https://github.com/raysan5/raylib.git /tmp/raylib
cd /tmp/raylib/src
make PLATFORM=PLATFORM_DESKTOP RAYLIB_LIBTYPE=SHARED
sudo make install RAYLIB_LIBTYPE=SHARED
sudo ldconfig
```

**WASM com WASI SDK:**

```toml
# examples/wasm_js_interop.toml
[link]
target = "wasm"
```

Requer `wasi-sdk` em `/opt/wasi-sdk`:

```bash
wget https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-21/wasi-sdk-21.0-linux.tar.gz -O /tmp/wasi-sdk.tar.gz
sudo mkdir -p /opt/wasi-sdk
sudo tar xzf /tmp/wasi-sdk.tar.gz -C /opt/wasi-sdk --strip-components=1
```

O `cmd_build` usa `/opt/wasi-sdk/bin/clang` automaticamente quando disponível.

### Ordem de montagem do comando

Para builds nativos, o `cmd_build` monta o comando assim:

```
clang <opt_flag> -Wno-override-module [<debug_flag>] <ir_file> -o <output> \
    -lc -lm -lpthread -lgc \
    [<extra_objects .o>] [<-lstdc++ se houver C++>] \
    [<-l<lib> para cada lib do [link].libs>] \
    [<extra_flags>] [<flags da CLI>]
```

Onde `<opt_flag>` é:
- `-O0` se `--debug`
- `-O3` se `--release`
- `-O2` no padrão

---

## 🌐 WebAssembly e Interoperabilidade

Compile módulos Lumina para a Web e chame-os diretamente do JavaScript!

**1. Código Lumina (`math.lm`):**
```lumina
export fn fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

fn main() -> int:
    return 0
```

**2. Compile para WASM:**
```bash
lumina build math.lm --wasm
```

**3. Chame no JavaScript:**
```javascript
WebAssembly.instantiateStreaming(fetch("math.wasm"))
  .then(obj => {
      let result = obj.instance.exports.fib(35);
      console.log("Fib calculado em C/WASM pela Lumina:", result);
  });
```

---

## 🛠️ Exemplos de Código

### 1. Sintaxe Curta, Switch e Escopo de Bloco
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
        print("Dentro do if, temp =", temp)
    # A variável 'temp' não existe aqui fora!

    let dia = avaliar_dia(2)
    print("Hoje é:", dia)
    return 0
```

### 2. Enum Multi-Payload + Pattern Matching
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

    let y = buscar(42)
    match y:
        case Some(v): print("Achou:", v)
        case None:    print("Não achou")
    return 0
```

### 4. `comptime` (constant folding)
```lumina
fn main() -> int:
    let x = comptime(2 + 3 * 4)      # vira literal 14 no IR
    let y = comptime(10 % 3)          # vira literal 1
    let z = comptime(2.5 * 4)         # vira literal 10.0

    print("x =", x)
    print("y =", y)
    print("z =", z)
    return 0
```

### 5. Slicing (novo nó `SliceExpr`)
```lumina
fn main() -> int:
    let s = "abcdef"
    print(s[1..4])    # bcd
    print(s[..3])     # abc
    print(s[2..])     # cdef
    print(s[..])      # abcdef

    let arr = [10, 20, 30, 40, 50]
    let sub = arr[1..3]   # [20, 30]
    print(sub[0], sub[1])
    return 0
```

### 6. Vector (Array Dinâmico)
```lumina
import "std/vector"

fn main() -> int:
    mut v = new_vector()
    v.push(10)
    v.push(20)
    v.push(30)

    print("len:", v.len)
    print("get(0):", v.get(0))
    print("sum:", v.sum())
    print("is_empty:", v.is_empty())
    return 0
```

### 7. Map (Hash Map)
```lumina
import "std/map"

fn main() -> int:
    mut m = new_map()
    # Cresce automaticamente (rehash) quando passa de 75% de carga
    mut i = 0
    while i < 100:
        m.insert(i, i * 10)
        i += 1

    print("size:", m.size)
    print("get(42):", m.get(42))
    print("contains(99):", m.contains(99))
    return 0
```

### 8. Set (Conjunto)
```lumina
import "std/set"

fn main() -> int:
    mut s = new_set()
    s.add(1)
    s.add(2)
    s.add(3)
    s.add(1)          # no-op (já existe)

    print("size:", s.size)
    print("contains(1):", s.contains(1))
    print("contains(99):", s.contains(99))
    return 0
```

### 9. Deque (Fila Dupla, buffer circular)
```lumina
import "std/deque"

fn main() -> int:
    mut d = new_deque()
    # Cresce automaticamente quando atinge a capacidade
    mut i = 0
    while i < 100:
        d.push_back(i)
        i += 1

    print("size:", d.size)
    print("get(0):", d.get(0))
    print("get(99):", d.get(99))
    return 0
```

### 10. Adaptadores Funcionais (`std/iter`)
```lumina
import "std/iter"

fn main() -> int:
    let n = 5
    mut arr = alloc(n)
    arr[0] = 1
    arr[1] = 2
    arr[2] = 3
    arr[3] = 4
    arr[4] = 5

    print("Soma:", sum(arr, n))
    print("Max:", max(arr, n))

    # map com lambda
    let dobrados = map(arr, n, fn(x: int) -> int: x * 2)
    print("Dobrados somam:", sum(dobrados, n))

    # filter com predicado
    let npares = count_if(arr, n, fn(x: int) -> int: (x % 2) == 0)
    print("Quantidade de pares:", npares)
    return 0
```

### 11. Traits com Métodos Padrão
```lumina
trait Greeter:
    fn name() -> str
    fn greet():
        let n = name()
        print("Hello from", n)

struct English:
    dummy: int

impl Greeter for English:
    fn name() -> str:
        return "Lumina"

fn main() -> int:
    mut e: English
    e.dummy = 0
    e.greet()
    return 0
```

### 12. Operator Overloading
```lumina
struct Vector2:
    x: int
    y: int

impl Vector2:
    fn __add__(a: Vector2, b: Vector2) -> Vector2:
        mut result: Vector2
        result.x = a.x + b.x
        result.y = a.y + b.y
        return result

    fn __eq__(a: Vector2, b: Vector2) -> int:
        if a.x == b.x and a.y == b.y:
            return 1
        return 0

fn main() -> int:
    mut v1: Vector2
    v1.x = 10
    v1.y = 20
    mut v2: Vector2
    v2.x = 5
    v2.y = 5

    let v3 = v1 + v2       # chama Vector2___add__
    print("V3 X:", v3.x)
    print("V3 Y:", v3.y)

    let iguais = v1 == v2  # chama Vector2___eq__
    print("iguais?", iguais)
    return 0
```

### 13. `@derive(Eq, Debug, Default, Clone)`
```lumina
@derive(Eq, Debug, Default, Clone)
struct Ponto:
    x: int
    y: int

fn main() -> int:
    # Default → new_Ponto()
    let p1 = new_Ponto()
    print("p1.x =", p1.x)   # 0

    # Clone → p.clone()
    mut original: Ponto
    original.x = 10
    original.y = 20
    let copia = original.clone()
    print("copia.x =", copia.x)   # 10

    # Eq → operador ==
    print("p1 == copia?", p1 == copia)

    # Debug → __debug__()
    print(copia.__debug__())   # "Ponto { x: 10, y: 20 }"

    return 0
```

### 14. Generics com Monomorphization
```lumina
fn identidade<T>(x: T) -> T:
    return x

fn main() -> int:
    let a = identidade(10)
    let b = identidade(3.14)
    print("int:", a)
    print("float:", b)
    return 0
```

### 15. Navegação Segura e Propagação de Erros
```lumina
struct Node:
    value: int

fn dividir(a: int, b: int) -> Result:
    if b == 0:
        return Err(1)
    return Ok(a / b)

fn calcular() -> Result:
    let x = dividir(10, 2)?
    let y = dividir(20, 4)?
    return Ok(x + y)

fn main() -> int:
    let n: Node = none
    let v = n?.value           # retorna 0 (sem segfault)
    print("Safe nav:", v)

    match calcular():
        case Ok(v):  print("Resultado:", v)
        case Err(e): print("Erro:", e)
    return 0
```

### 16. Canais de Concorrência (CSP)
```lumina
import "std/channel"

fn main() -> int:
    let c = new(10)
    send(c, 42)
    let val = recv(c)
    print("Recebido do canal:", val)
    return 0
```

### 17. Bitwise e Shifts
```lumina
fn main() -> int:
    let x = 12 & 10     # and   = 8
    let y = 12 | 10     # or    = 14
    let z = 12 ^ 10     # xor   = 6
    let w = 1 << 4      # shl   = 16
    let v = 256 >> 2    # shr   = 64
    print(x, y, z, w, v)
    return 0
```

---

## 📦 Standard Library (`std/`)

### Fundamentos
* `std/prelude`: Tipos `Option` e `Result` disponíveis em todos os arquivos.
* `std/math`: Funções matemáticas via FFI (`potencia`, `raiz_quadrada`, `valor_absoluto`).
* `std/str`: Manipulação de strings (`to_upper`, `to_lower`, `trim`, `split`, `join`, `find`, `substr`).
* `std/time`: Medição de tempo de alta precisão.
* `std/fs`: Manipulação de arquivos.
* `std/alloc`: Arena Allocator para sistemas Bare-Metal.

### Coleções
* `std/vector`: Array dinâmico que cresce automaticamente (`push`, `pop`, `get`, `set`, `clear`, `is_empty`, `sum`, `reserve`).
* `std/map`: Hash map de `int → int` com **rehash automático** em load factor ≥ 0.75 (`insert`, `get`, `contains`, `remove`).
* `std/set`: Conjunto de `int` com **rehash automático** em load factor ≥ 0.75 (`add`, `contains`, `remove`).
* `std/deque`: Fila dupla com buffer circular e **`grow()` automático** (`push_back`, `push_front`, `pop_front`, `pop_back`, `get`, `is_empty`).
* `std/list`: Lista Ligada (Linked List) dinâmica usando Structs e Ponteiros.
* `std/iter`: Adaptadores funcionais (`map`, `filter`, `count_if`, `sum`, `sum_by`, `product`, `min`, `max`, `all`, `any`, `find_index`, `copy`, `fill`, `for_each`, `reverse`).

### Concorrência e I/O
* `std/channel`: Canais de concorrência seguros entre threads (CSP).
* `std/async`: Green Threads e troca de contexto (ucontext).
* `std/async_fs`: I/O de arquivos não-bloqueante usando `O_NONBLOCK`.
* `std/epoll`: Event Loop Assíncrono (I/O não-bloqueante).
* `std/net`: Sockets TCP e Proxy Reverso.
* `std/http`: Web Framework HTTP nativo.

### Integração e Ferramentas
* `std/json`: Parser de JSON nativo escrito em Lumina.
* `std/sqlite`: Bindings para banco de dados SQLite.
* `std/raylib`: Bindings para engine gráfica Raylib.

---

## 📂 Estrutura do Projeto

```text
Lumina/
├── lumina/                     # Núcleo do Compilador
│   ├── ast/                    #   Árvore Sintática (Expr, Stmt, Visitor)
│   ├── lexer/                  #   Tokenizer (INDENT/DEDENT, f-strings, COMMENT)
│   ├── parser/                 #   Parser recursivo descendente (com @attrs)
│   ├── semantic/               #   Análise semântica + validação + @derive
│   ├── codegen/                #   LLVM IR (exprs, stmts, types, match)
│   ├── common/                 #   Utilitários compartilhados (cores ANSI)
│   ├── builtins.py             #   Fonte única de verdade dos builtins
│   └── errors.py               #   LuminaError com highlight estilo Rust
├── lumina_core/                # Início do Bootstrapping (Lexer/Parser em .lm)
├── lumina_cli/                 # CLI modular, Build System, REPL, Test Runner
│   ├── main.py                 #   Ponto de entrada + dispatch de comandos
│   ├── commands.py             #   Lógica dos comandos + suporte a [link]
│   ├── compiler.py             #   parse_module, compile_lumina, check_lumina, format_node
│   ├── playground.py           #   Web Playground (JIT HTTP Server)
│   ├── utils.py                #   Cores, cache hash, resolução de imports
│   └── __main__.py             #   Permite `python -m lumina_cli`
├── lumina-vscode/              # Extensão VS Code (Syntax + LSP Client + Server)
│   ├── lumina_lsp.py           #   LSP: hover, rename, references, documentSymbol
│   ├── extension.js            #   Client LSP
│   └── syntaxes/               #   TextMate grammar
├── std/                        # Standard Library (.lm)
├── benchmarks/                 # Benchmarks (Lumina vs C, Rust, Go, Node, Python)
├── examples/                   # 66 exemplos + sidecars [link]
├── scripts/
│   ├── check_examples.sh       #   Compila todos os exemplos (PASS/SKIP/FAIL)
│   └── run_benchmarks.sh       #   Roda a suíte de benchmarks
├── tests/
│   ├── test_lexer.py           #   30 testes de lexing
│   ├── test_parser.py          #   35 testes de parsing
│   ├── test_semantic.py        #   19 testes de análise semântica
│   ├── test_types.py           #   24 testes de validação de tipo
│   ├── test_codegen_bugs.py    #   20 testes de regressão (codegen)
│   ├── test_semantic_bugs.py   #   15 testes de regressão (semantic)
│   ├── test_fmt_comments.py    #   8 testes de formatter com comentários
│   ├── cli/                    #   Testes de integração da CLI
│   ├── features/               #   Smoke tests + uncertain_features.lm + skip.txt
│   └── fixtures/               #   Arquivos .lm auxiliares
├── run_tests.py                # Suíte standalone (28 validações, ~5s)
├── pyproject.toml              # Configuração de build e distribuição PyPI
└── playground.html             # Interface web do playground
```

---

## 🎨 Extensão para o VS Code e Sublime Text

A extensão VS Code oferece:

- **Realce de sintaxe** (TextMate grammar em `syntaxes/lumina.tmLanguage.json`)
- **Autocomplete** de keywords, funções, variáveis, structs e enums
- **Diagnóstico de erros em tempo real** (parser + semantic)
- **Go to Definition** (Ctrl+Click / F12)
- **Hover** — mostra tipo/assinatura do símbolo sob o cursor
- **Find References** (Shift+F12)
- **Rename Symbol** (F2) — renomeia em todas as ocorrências do arquivo
- **Document Symbols** (Ctrl+Shift+O) — outline de funções, structs, enums, traits e impl blocks

### Instalação

1. Gere o pacote `.vsix`:
   ```bash
   cd lumina-vscode
   npx vsce package
   ```
2. No VS Code, abra `Ctrl+Shift+P` > **Extensions: Install from VSIX...**
3. Selecione o arquivo `lumina-0.2.0.vsix` gerado
4. Recarregue a janela (`Ctrl+Shift+P` > **Developer: Reload Window**)

### Sublime Text

1. Copie `syntaxes/lumina.tmLanguage.json` para `Packages/Lumina/`
2. Instale o pacote `LSP` da Package Control
3. Configure o `LSP` para apontar para `lumina-vscode/lumina_lsp.py`

---

## 📝 Notas e Limitações Conhecidas

* **Escape analysis:** os dados de escape são coletados no semantic (`analyzer.escapes`), mas a alocação automática Stack↔Heap ainda não foi conectada ao codegen. Por segurança, **toda struct local é alocada no heap** — o Boehm GC cuida da liberação.
* **`dois as int`:** o operador `as` só faz cast entre tipos primitivos e ponteiros; cast entre structs requer método explícito.
* **Pattern matching em structs via `match`:** suportado em `MatchExpr` (expressões), ainda não em `MatchStmt` (statements com bloco).
* **Validação de tipo por campo em struct literals:** `P { x: "texto", y: 2 }` com `x: int` não é detectado (só a existência dos campos é checada).
* **`arr[a..]` sem `end`:** em strings, usa `strlen`; em arrays, assume length 0 (limitação do codegen atual — não há `len()` para `ptr`).
* **`comptime`:** suporta constant folding de literais e operações aritméticas (`+`, `-`, `*`, `/`, `%`, comparações e unário `-`). Chamadas de função em compile-time ainda não são suportadas.
* **`std/map` e `std/set`:** crescem automaticamente via rehash quando o load factor ≥ 0.75. Não libera memória de tombstones em `remove` (retrocompatível com a estratégia atual).
* **`std/iter` callbacks:** como o codegen só suporta chamadas indiretas com assinatura `i64 -> i64`, todas as funções de callback recebem e retornam `int`. Para predicados, use 1 = true / 0 = false.
* **LSP `references`:** usa varredura léxica — não distingue escopos nem filtra por tipo. Suficiente para `rename` e navegação em código simples.
* **LSP `rename`:** afeta só o arquivo atual (não propaga para imports em outros arquivos).
* **LSP `documentSymbol`:** só retorna símbolos de topo (funções, structs, enums, traits) e métodos de `impl`. Variáveis locais não aparecem no outline.

---

## 🗺️ Roadmap

- [x] Sintaxe base, AST, lexer/parser
- [x] Codegen LLVM, JIT, REPL
- [x] Generics com monomorphization
- [x] Pattern matching (int, enum, string, struct)
- [x] Traits com métodos default
- [x] Operator overloading (`__add__`, `__eq__`, ...)
- [x] Validação de tipo em VarDecl/Assign/Return/conditions
- [x] Configuração de link (`[link]`) com suporte a C/C++/WASM
- [x] `-O0`/`-O2`/`-O3` configuráveis
- [x] `SliceExpr` na AST
- [x] `Option<T>` + `NoneExpr` dedicados
- [x] `comptime` real (constant folding)
- [x] `lumina check` (só lexer+parser+semantic)
- [x] `--error-format=json` em todos os comandos
- [x] `lumina fmt --check` (pre-commit)
- [x] `lumina doc --format=html|md|json`
- [x] Formatter preservando comentários
- [x] `std/iter` (adaptadores funcionais)
- [x] `std/vector` (array dinâmico)
- [x] `std/map` (hash map com rehash automático)
- [x] `std/set` (conjunto com rehash automático)
- [x] `std/deque` (fila dupla com grow automático)
- [x] `@derive(Eq, Debug)` para structs
- [x] `@derive(Default, Clone, Display)`
- [x] LSP (autocomplete, go-to-def, hover, references, rename, documentSymbol)
- [ ] Self-hosting (bootstrapping)
- [ ] `--target=aarch64-linux` (cross-compile)
- [ ] Macros (quasiquote / `comptime` com AST)
- [ ] Semantic tokens no LSP

---

## 📜 Licença
Este projeto é distribuído sob a Licença **MIT**. Para mais detalhes, consulte o arquivo [LICENSE](LICENSE).