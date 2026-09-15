# 🌟 Lumina Language

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LLVM Version](https://img.shields.io/badge/LLVM-14%2B-blue.svg)](https://llvm.org/)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Alpha%20%2F%20Active-green.svg)](#)
[![Language](https://img.shields.io/badge/Language-Lumina-6A0DAD.svg)](#)
[![Features](https://img.shields.io/badge/features-24%2F24-success.svg)](#-status-de-implementação)
[![Tests](https://img.shields.io/badge/tests-5%20passed%20%2B%2028%2F28-brightgreen.svg)](#-testes-automatizados)
[![Examples](https://img.shields.io/badge/examples-70%2F70-success.svg)](#)

**Lumina** é uma linguagem de programação de sistemas de propósito geral, focada em alta performance, ergonomia moderna, concorrência e segurança de memória. Ela combina a sintaxe limpa e expressiva baseada em indentação (estilo Python/Nim) com o poder de baixo nível e otimização industrial do backend **LLVM**.

A linguagem oferece tipagem estática com inferência, Garbage Collector nativo (Boehm GC), Tipos Algébricos (Enums com multi-payload), Generics com **Monomorphization** (`<T>`), Traits com Métodos Padrão, Standard Library Bootstrapped, Pattern Matching (incluindo destructuring de structs), Canais de Concorrência (CSP), operadores modernos (`|>`, `defer`, `?.`, `?`, `as`, `:=`), interoperabilidade nativa com C/C++ (FFI), suporte a I/O Assíncrono (`epoll`/`O_NONBLOCK`), um REPL interativo, um Web Playground, um LSP com Autocomplete e "Go to Definition", compilação incremental, testes nativos com relatório de cobertura, e é **Cross-Platform** (compila para binários nativos x86_64/ARM, WebAssembly e Bare-Metal).

---

## ✨ Funcionalidades Principais

* **Sintaxe Limpa & Ergonômica:** Escopo definido por indentação significativa. Sem chaves `{}` ou pontos e vírgula `;`.
* **Standard Library Bootstrapped:** Módulos como `std/math`, `std/str`, `std/time`, `std/list`, `std/channel` e `std/async_fs` são escritos 100% na própria Lumina.
* **Tipagem Estática com Inferência:** O compilador deduz os tipos automaticamente, incluindo retornos de métodos, generics e Lambdas.
* **Generics com Monomorphization:** Suporte a tipos genéricos `<T>` que geram cópias especializadas em tempo de compilação, garantindo zero overhead de runtime. Cobre funções e structs (`Box<int>`, `Box<float>`, ...).
* **Tipos Algébricos (ADTs) & Pattern Matching:** `enum`s com **múltiplos payloads** (`Dois(int, int)`) e extração via `match` ou `switch`. O compilador checa a exaustividade dos casos.
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
  * **String / Array Slicing:** Fatiamento nativo: `texto[1..5]`, `arr[1..4]`.
  * **Switch Statements:** Sintaxe limpa de salto (jump table nativa do LLVM) para inteiros e enums.
  * **Defer & Assert:** Garantia de limpeza de escopo e testes nativos.
  * **Auto-Formatter:** `lumina fmt` formata o código automaticamente (AST-based).
* **Mensagens Inteligentes:** Erros léxicos e semânticos sugerem correções ("Did you mean?") com destaque colorido da linha.
* **Concorrência e I/O Assíncrono:**
  * **Canais (CSP):** Comunicação segura entre threads estilo Go usando `pthread_mutex` e `pthread_cond`.
  * **Green Threads:** Suporte a Corrotinas via troca de contexto de CPU (`ucontext`).
  * **Async I/O:** Event Loop não-bloqueante de baixa latência usando `epoll` e `O_NONBLOCK`.
* **Gerenciamento de Memória Avançado:**
  * **Garbage Collector:** Integração nativa com o **Boehm GC** (`libgc`).
  * **Arena Allocator:** Modo Bare-Metal (`--no-gc`) com alocador determinístico.
* **Otimizações de Compilador:**
  * Tail Call Optimization (TCO), Constant Folding, Comptime Evaluation.
  * **Forward Declarations:** Funções podem ser chamadas antes de serem definidas no arquivo.
  * **Build Incremental:** A CLI detecta se o LLVM IR não mudou e pula a linkagem. O hash inclui os fontes do compilador — mudanças em `.py` também invalidam o cache.
  * **Debug Info (DWARF):** Gera metadados de depuração (`--debug`) permitindo inspectar código `.lm` no GDB/LLDB.
* **Ecossistema Integrado:** CLI via `pip install`, REPL, Web Playground (JIT), Package Manager (`lumina.toml`), Auto-Gerador de Bindings C, Test Runner nativo (`lumina test`) com relatório de cobertura via `llvm-cov`.
* **Cross-Platform:** Compila para binários nativos, WebAssembly (`.wasm` com exports diretos para JS) e Bare-Metal.

---

## 📊 Status de Implementação

Todas as 24 features testadas em `tests/uncertain_features.lm` estão funcionando e validadas por CI local:

| # | Feature | Status |
|---|---|---|
| 1 | String Slicing (`s[1..4]`) | ✅ |
| 2 | Array Indexing (`arr[i]`) | ✅ |
| 2b | Array Slicing real (`arr[a..b]`) | ✅ |
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

---

## 🧪 Testes Automatizados

A suíte é dividida em duas partes:

### 1. Pytest (integração ponta-a-ponta)

```bash
pytest tests/ -v
```

Cobre:
- `test_new_and_build` — fluxo `lumina new` → `build` → `run`
- `test_fmt` — auto-formatter em código válido
- `test_unknown_command` — CLI rejeita comandos inválidos
- `test_smoke_tests_examples` — compila **todos** os arquivos de `examples/`
- `test_uncertain_features` — valida 28 linhas de output do teste de features

### 2. Script standalone (5 segundos)

```bash
python3 run_tests.py
```

Compila, executa, e valida cada linha esperada do `tests/uncertain_features.lm`. Retorna exit code 0/1 — ideal para pre-commit hooks ou CI rápido.

```
==============================================================
📊 Resultado: 28/28 verificações OK
==============================================================

✅ Todos os testes passaram!
```

---

## 🏎️ Benchmarks de Performance

### CPU (Média de 10 Execuções - `clang -O3 -march=native`)
| Teste | C | Rust | **Lumina** | Go | Node.js | Python |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Loop Matemático** (10M) | 0.000038s | - | **0.000049s** 🥈 | - | - | - |
| **Crivo de Eratóstenes** (10M) | 0.0308s | 0.0326s | **0.0257s** 🥇 | 0.0416s | - | - |
| **Fibonacci** (N=35) | 0.0400s | 0.0362s | **0.0400s** 🥇 | 0.0713s | 0.2364s | 1.4574s |

### Web Server (`wrk -t4 -c100`)
* **Lumina-Serve (epoll):** ~5.868 Requests/sec.

---

## 🚀 Como Usar (CLI)

### Pré-requisitos
* **Python 3.11+** e `llvmlite` (`pip install llvmlite`)
* **LLVM** e **Clang** no `PATH`
* **Boehm GC** (`sudo apt install libgc-dev`)
* *(Opcional para WASM)* **WASI SDK** instalado em `/opt/wasi-sdk`

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
lumina fmt arquivo.lm           # Formata o código automaticamente
lumina clean                    # Limpa o cache e binários antigos
lumina run arquivo.lm           # Compila e executa o binário nativo
lumina test arquivo.lm          # Compila e executa a suíte de testes nativa
lumina repl                     # Inicia o console interativo (REPL JIT)
lumina jit arquivo.lm           # Executa instantaneamente na memória RAM
lumina build                    # Compila para binário nativo otimizado (-O3)
lumina build app.lm --debug     # Compila com símbolos DWARF (GDB/LLDB)
lumina build app.lm --wasm      # Compila para WebAssembly (.wasm)
lumina build app.lm --no-gc     # Compila para Bare-Metal (sem Garbage Collector)
lumina playground               # Inicia o Web Playground JIT (porta 8080)
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
| `target` | `str` | Força um target. Valores aceitos: `"wasm"`. Outros targets podem ser adicionados no futuro. |
| `extra_flags` | `List[str]` | Flags extras que são passadas **diretamente** para o `clang` na fase de linkagem. Útil para `-L`, `-Wl,...`, defines, etc. |

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

Requer `wasi-sdk` em `/opt/wasi-sdk`. O `cmd_build` usa
`/opt/wasi-sdk/bin/clang` automaticamente quando disponível.

**Biblioteca matemática + flags extras:**

```toml
[link]
libs = ["m", "pthread"]
extra_flags = ["-L/opt/custom/lib", "-Wl,-rpath,/opt/custom/lib"]
```

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

### Notas

- **`GC_malloc` → `malloc`:** no target WASM, o `cmd_build` substitui
  automaticamente `GC_malloc` por `malloc`, já que o Boehm GC não está
  disponível em WASM.
- **`export fn`:** funções marcadas com `export fn nome` são detectadas
  via regex no fonte e exportadas para o JS (`-Wl,--export=nome`).
- **Cache incremental:** o hash de link inclui a flag de otimização. Trocar
  `--release` ↔ padrão ↔ `--debug` força relinkagem.

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

### 3. Traits com Métodos Padrão
```lumina
trait Greeter:
    fn greet():
        print("Hello from Lumina")

struct English:
    dummy: int

impl Greeter for English:
    # usa o default do trait

fn main() -> int:
    mut e: English
    e.greet()
    return 0
```

### 4. Generics com Monomorphization
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

### 5. Navegação Segura e Propagação de Erros
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

### 6. Canais de Concorrência (CSP)
```lumina
import "std/channel"

fn main() -> int:
    let c = new(10)
    send(c, 42)
    let val = recv(c)
    print("Recebido do canal:", val)
    return 0
```

---

## 📦 Standard Library (`std/`)

* `std/math`: Funções matemáticas via FFI (`potencia`, `raiz_quadrada`, `valor_absoluto`).
* `std/str`: Manipulação de strings nativa (`to_upper`, `to_lower`, `trim`, `split`, `join`).
* `std/list`: Lista Ligada (Linked List) dinâmica usando Structs e Ponteiros.
* `std/channel`: Canais de concorrência seguros entre threads (CSP).
* `std/async_fs`: I/O de arquivos não-bloqueante usando `O_NONBLOCK`.
* `std/time`: Medição de tempo de alta precisão.
* `std/fs`: Manipulação de arquivos.
* `std/http`: Web Framework HTTP nativo.
* `std/net`: Sockets TCP e Proxy Reverso.
* `std/async`: Green Threads e troca de contexto (ucontext).
* `std/epoll`: Event Loop Assíncrono (I/O não-bloqueante).
* `std/vector`: Array Dinâmico que cresce automaticamente na memória.
* `std/map`: Hash Map (Dicionário) com tratamento de colisões.
* `std/alloc`: Arena Allocator para sistemas Bare-Metal.
* `std/json`: Parser de JSON nativo escrito em Lumina.
* `std/sqlite`: Bindings para banco de dados SQLite.
* `std/raylib`: Bindings para engine gráfica Raylib.

---

## 📂 Estrutura do Projeto

```text
Lumina/
├── lumina/                     # Núcleo do Compilador (Lexer, Parser, Semantic, Codegen)
├── lumina_core/                # Início do Bootstrapping (Lexer e Parser nativos em .lm)
├── lumina_cli/                 # CLI modular, Build System, REPL, Test Runner e Package Manager
│   ├── main.py                 # Ponto de entrada da CLI
│   ├── commands.py             # Lógica dos comandos (build, run, fmt, new, test, etc)
│   ├── compiler.py             # Lógica de compilação, JIT e geração de IR
│   ├── playground.py           # Web Playground (JIT HTTP Server)
│   └── utils.py                # Cores ANSI, Helpers de Caminho e Cache Hash
├── lumina-vscode/              # Extensão VS Code (Syntax + LSP Client + LSP Server)
├── std/                        # Standard Library (.lm)
├── benchmarks/                 # Suíte de benchmarks (Lumina vs C, Rust, Go)
├── examples/                   # Exemplos de código (Proxy, JSON Parser, WASM, etc)
├── tests/                      # Suíte de testes funcionais (pytest) e Smoke Tests
│   ├── test_cli.py             # Pytest: integração ponta-a-ponta
│   └── uncertain_features.lm   # Teste das 24 features verificadas
├── run_tests.py                # Suíte standalone (28 validações, ~5s)
├── pyproject.toml              # Configuração de build e distribuição PyPI
└── playground.html             # Interface web do playground
```

---

## 🎨 Extensão para o VS Code e Sublime Text

A Lumina oferece suporte a realce de sintaxe, regras de indentação, **Autocomplete de funções do usuário**, **Diagnóstico de Erros em tempo real** e **Go to Definition**:

1. Gere o pacote `.vsix` executando `npx vsce package` na pasta `lumina-vscode`.
2. No VS Code, abra o painel de Extensões (`Ctrl+Shift+X`).
3. Clique no menu de três pontos (`...`) no canto superior direito > **Instalar de VSIX...**.
4. Selecione o arquivo `.vsix` gerado e reinicie a janela.
5. Para Sublime Text, copie o arquivo `syntaxes/lumina.tmLanguage.json` para a pasta `Packages/Lumina/` e instale o pacote `LSP` da Package Control.

---

## 📝 Notas e Limitações Conhecidas

* **Auto-formatter:** funciona sobre a AST, então **comentários são descartados** ao reformatar. Planejado para uma versão futura.
* **Escape analysis:** os dados de escape são coletados no semantic (`analyzer.escapes`), mas a alocação automática Stack↔Heap ainda não foi conectada ao codegen — hoje tudo passa pelo Boehm GC quando o GC está ativo.
* **`dois as int`:** o operador `as` só faz cast entre tipos primitivos e ponteiros; cast entre structs requer método explícito.
* **Pattern matching em structs via `match`:** suportado em `MatchExpr` (expressões), ainda não em `MatchStmt` (statements com bloco).

---

## 📜 Licença
Este projeto é distribuído sob a Licença **MIT**. Para mais detalhes, consulte o arquivo [LICENSE](LICENSE).
