# 🌟 Lumina Language

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LLVM Version](https://img.shields.io/badge/LLVM-14%2B-blue.svg)](https://llvm.org/)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Alpha%20%2F%20Active-green.svg)](#)
[![Language](https://img.shields.io/badge/Language-Lumina-6A0DAD.svg)](#)

**Lumina** é uma linguagem de programação de sistemas de propósito geral, focada em alta performance, ergonomia moderna, concorrência e segurança de memória. Ela combina a sintaxe limpa e expressiva baseada em indentação (estilo Python/Nim) com o poder de baixo nível e otimização industrial do backend **LLVM**.

A linguagem oferece tipagem estática com inferência, Garbage Collector nativo (Boehm GC), Tipos Algébricos (Enums), Generics com **Monomorphization** (`<T>`), Traits com Métodos Padrão, Standard Library Bootstrapped, Pattern Matching em Structs (Destructuring), Canais de Concorrência (CSP), operadores modernos (`|>`, `defer`, `?.`, `?`, `as`, `:=`), interoperabilidade nativa com C/C++ (FFI), suporte a I/O Assíncrono (`epoll`/`O_NONBLOCK`), um REPL interativo, um Web Playground, um LSP com Autocomplete e "Go to Definition", compilação incremental, testes nativos com relatório de cobertura, e é **Cross-Platform** (compila para binários nativos x86_64/ARM, WebAssembly e Bare-Metal).

---

## ✨ Funcionalidades Principais

* **Sintaxe Limpa & Ergonômica:** Escopo definido por indentação significativa. Sem chaves `{}` ou pontos e vírgula `;`.
* **Standard Library Bootstrapped:** Módulos como `std/math`, `std/str`, `std/time`, `std/list`, `std/channel` e `std/async_fs` são escritos 100% na própria Lumina.
* **Tipagem Estática com Inferência:** O compilador deduz os tipos automaticamente, incluindo retornos de métodos e Lambdas.
* **Generics com Monomorphization:** Suporte a tipos genéricos `<T>` que geram cópias especializadas em tempo de compilação, garantindo zero overhead de runtime.
* **Tipos Algébricos (ADTs) & Pattern Matching:** `enum`s com payloads e extração via `match` ou `switch`. O compilador checa a exaustividade dos casos.
* **Pattern Matching em Structs:** Destructuring direto no `match` para extrair campos de structs literais de forma elegente.
* **Closures (Lambdas):** Funções anônimas inline (`fn(x: int) -> int: x * 2`).
* **Ergonomia Moderna:**
  * **Sintaxe Curta (`:=`):** Declare variáveis mutáveis rapidamente: `x := 10`.
  * **Escopo de Bloco Lexical:** Variáveis declaradas dentro de `if`/`for`/`while` "morrem" ao sair do bloco, garantindo segurança de memória.
  * **F-strings Nativas:** `$"Usuário {id} logou."`.
  * **Operador Pipe (`|>`):** `5 |> dobrar |> imprimir`.
  * **Navegação Segura (`?.`):** Evita Segmentation Faults ao acessar structs nulas.
  * **Propagação de Erros (`?`):** Retorna erros automaticamente.
  * **Casting Explícito (`as`):** `10 as float`, `ptr as int`.
  * **String Slicing:** Fatiamento nativo de strings e arrays: `texto[1..5]`.
  * **Switch Statements:** Sintaxe limpa de salto (jump table nativa do LLVM) para inteiros e enums.
  * **Defer & Assert:** Garantia de limpeza de escopo e testes nativos.
  * **Auto-Formatter:** `lumina fmt` formata o código automaticamente (100% da AST).
  * **Error Recovery:** O Parser se recupera de erros de sintaxe e continua analisando o resto do arquivo, permitindo que o LSP destaque múltiplos erros de uma vez.
* **Mensagens Inteligentes:** Erros léxicos e semânticos sugerem correções ("Did you mean?").
* **Concorrência e I/O Assíncrono:**
  * **Canais (CSP):** Comunicação segura entre threads estilo Go usando `pthread_mutex` e `pthread_cond`.
  * **Green Threads:** Suporte a Corrotinas via troca de contexto de CPU (`ucontext`).
  * **Async I/O:** Event Loop não-bloqueante de baixa latência usando `epoll` e `O_NONBLOCK`.
* **Gerenciamento de Memória Avançado:**
  * **Garbage Collector:** Integração nativa com o **Boehm GC** (`libgc`).
  * **Escape Analysis:** Variáveis alocadas são colocadas na Stack automaticamente se não fugirem do escopo; se fugirem, vão para o Heap.
  * **Arena Allocator:** Modo Bare-Metal (`--no-gc`) com alocador determinístico.
* **Otimizações de Compilador:** 
  * Tail Call Optimization (TCO), Constant Folding, Comptime Evaluation.
  * **Forward Declarations:** Funções podem ser chamadas antes de serem definidas no arquivo.
  * **Build Incremental:** A CLI detecta se o LLVM IR não mudou e pula a linkagem instantaneamente.
  * **Debug Info (DWARF):** Gera metadados de depuração (`--debug`) permitindo inspectar código `.lm` no GDB/LLDB.
* **Ecossistema Integrado:** CLI via `pip install`, REPL, Web Playground (JIT), Package Manager (`lumina.toml`), Auto-Gerador de Bindings C, Test Runner nativo (`lumina test`) com relatório de cobertura via `llvm-cov`.
* **Cross-Platform:** Compila para binários nativos, WebAssembly (`.wasm` com exports diretos para JS) e Bare-Metal.

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

### 2. Pattern Matching em Structs e Traits com Métodos Padrão
```lumina
struct Point:
    x: int
    y: int

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
    mut p: Point
    p.x = 10
    p.y = 20
    
    # Destructuring Match!
    let msg = match p {
        Point { x: 0, y: 0 } => "Origem",
        Point { x: val_x, y: val_y } => "Outro ponto",
        else => "Desconhecido"
    }
    print(msg)
    
    # Trait com método padrão
    mut e: English
    e.greet()
    return 0
```

### 3. Canais de Concorrência (CSP)
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

## 📜 Licença
Este projeto é distribuído sob a Licença **MIT**. Para mais detalhes, consulte o arquivo [LICENSE](LICENSE).