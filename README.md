# 🌟 Lumina Language

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LLVM Version](https://img.shields.io/badge/LLVM-14%2B-blue.svg)](https://llvm.org/)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Alpha%20%2F%20Active-green.svg)](#)
[![Language](https://img.shields.io/badge/Language-Lumina-6A0DAD.svg)](#)

**Lumina** é uma linguagem de programação de sistemas de propósito geral, focada em alta performance, ergonomia moderna, concorrência e segurança de memória. Ela combina a sintaxe limpa e expressiva baseada em indentação (estilo Python/Nim) com o poder de baixo nível e otimização industrial do backend **LLVM**.

A linguagem oferece tipagem estática com inferência, Garbage Collector nativo (Boehm GC), Tipos Algébricos (Enums), Generics com **Monomorphization** (`<T>`), Traits, Standard Prelude (Auto-import), Match Expressions, Closures (Lambdas), operadores modernos (`|>`, `defer`, `?.`, `?`, `as`), interoperabilidade nativa com C/C++ (FFI), suporte a I/O Assíncrono (`epoll`), um REPL interativo, um Web Playground, um LSP com "Go to Definition", compilação incremental, e é **Cross-Platform** (compila para binários nativos x86_64/ARM, WebAssembly e Bare-Metal).

---

## ✨ Funcionalidades Principais

* **Sintaxe Limpa & Ergonômica:** Escopo definido por indentação significativa. Sem chaves `{}` ou pontos e vírgulas `;`.
* **Standard Prelude:** Tipos básicos (`Option`, `Result`) e funções nativas são auto-importados em todos os arquivos.
* **Tipagem Estática com Inferência:** O compilador deduz os tipos automaticamente, incluindo retornos de métodos e Lambdas.
* **Generics com Monomorphization:** Suporte a tipos genéricos `<T>` que geram cópias especializadas em tempo de compilação (`Box<int>` vira `Box_int` no LLVM IR), garantindo zero overhead de runtime.
* **Traits (Interfaces):** Suporte a polimorfismo estático com verificação de assinaturas em tempo de compilação (`impl Trait for Struct`).
* **Tipos Algébricos (ADTs) & Pattern Matching:** `enum`s com payloads e extração via `match`. `match` também funciona como expressão que retorna valores. O compilador checa a exaustividade dos casos.
* **Closures (Lambdas):** Funções anônimas inline (`fn(x: int) -> int: x * 2`) que podem ser passadas como argumentos.
* **Ergonomia Moderna:**
  * **F-strings Nativas:** `$"Usuário {id} logou."`.
  * **Operador Pipe (`|>`):** `5 |> dobrar |> imprimir`.
  * **Navegação Segura (`?.`):** Evita Segmentation Faults ao acessar structs nulas: `usuario?.perfil?.nome`.
  * **Propagação de Erros (`?`):** Retorna erros automaticamente: `let val = abrir_arquivo()?`.
  * **Casting Explícito (`as`):** `10 as float`, `ptr as int`.
  * **Struct Literals:** Inicialização inline: `Point { x: 10, y: 20 }`.
  * **Defer & Assert:** Garantia de limpeza de escopo e testes nativos.
  * **Auto-Formatter:** `lumina fmt` formata o código automaticamente.
* **Gerenciamento de Memória Avançado:**
  * **Garbage Collector:** Integração nativa com o **Boehm GC** (`libgc`).
  * **Escape Analysis:** Se uma variável alocada não fugir do escopo, o compilador a aloca na Stack (Pilha) automaticamente.
  * **Arena Allocator:** Modo Bare-Metal (`--no-gc`) com alocador determinístico na `std/alloc`.
* **Otimizações de Compilador:** Tail Call Optimization (TCO), Constant Folding, Comptime Evaluation e DWARF Debug Info (depurável no GDB/LLDB).
* **Concorrência e Redes:**
  * **Multithreading:** Threads nativas do SO via `pthread_create`.
  * **Green Threads:** Suporte a Corrotinas via troca de contexto de CPU (`ucontext`).
  * **Async I/O:** Event Loop não-bloqueante de baixa latência usando `epoll` do Linux (Validado a **5.8k requisições/segundo**).
* **Ecossistema Integrado:** CLI (`lumina.toml`), REPL, Web Playground (JIT), Package Manager, Auto-Gerador de Bindings C, Native Benchmarking (`bench`) e Extensão VS Code/Sublime Text com **LSP (Autocomplete, Diagnósticos e Go to Definition)**.
* **Cross-Platform:** Compila para binários nativos, WebAssembly (`.wasm`) e Bare-Metal (`--no-gc`).

---

## 🏎️ Benchmarks de Performance

### CPU (Média de 10 Execuções - `clang -O3 -march=native`)
| Teste | C | Rust | **Lumina** | Go | Node.js | Python |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Loop Matemático** (100M) | 0.0029s | 0.0040s | **0.0028s** 🥇 | 0.1007s | 0.1476s | - |
| **Crivo de Eratóstenes** (10M) | 0.0308s | 0.0326s | **0.0257s** 🥇 | 0.0416s | - | - |
| **Matrizes** (200x200) | **0.0066s** | 0.0102s | **0.0073s** | 0.0168s | 0.0551s | - |
| **Fibonacci** (N=35) | 0.0400s | 0.0362s | **0.0400s** 🥇 | 0.0713s | 0.2364s | 1.4574s |

### Web Server (`wrk -t4 -c100`)
* **Lumina-Serve (epoll):** ~5.868 Requests/sec.

---

## 🚀 Como Usar (CLI)

### Pré-requisitos
* **Python 3.10+** e `llvmlite` (`pip install llvmlite`)
* **LLVM** e **Clang** no `PATH`
* **Boehm GC** (`sudo apt install libgc-dev`)

### Comandos Principais
```bash
lumina new meu_projeto      # Cria a estrutura inicial (com lumina.toml)
lumina install              # Baixa dependências do GitHub
lumina bind header.h nome   # Gera bindings FFI a partir de um arquivo C
lumina fmt arquivo.lm       # Formata o código automaticamente
lumina clean                # Limpa o cache e binários antigos
lumina run arquivo.lm       # Compila e executa o binário nativo
lumina repl                 # Inicia o console interativo (REPL JIT)
lumina jit                  # Executa instantaneamente na memória RAM
lumina build                # Compila para binário nativo otimizado (-O3)
lumina build app.lm --wasm  # Compila para WebAssembly (.wasm)
lumina build app.lm --no-gc # Compila para Bare-Metal (sem Garbage Collector)
```

### 🌐 Web Playground (JIT)
Inicie um servidor web local que compila e executa código Lumina instantaneamente na memória RAM, exibindo no navegador:
```bash
python3 playground.py
# Acesse http://localhost:8080 no navegador
```

---

## 🛠️ Exemplos de Código

### 1. Traits, Struct Literals e Pattern Matching
```lumina
trait Drawable:
    fn draw()
    fn get_area() -> int

struct Square:
    size: int

impl Drawable for Square:
    fn draw():
        print("Desenhando Square...")
    fn get_area() -> int:
        return 10 * 10

fn main() -> int:
    let sq = Square { size: 10 }
    sq.draw()
    print("Área:", sq.get_area())
    return 0
```

### 2. Match Expressions, Closures e Standard Prelude
```lumina
fn avaliar(n: int) -> int:
    # Match retorna um valor diretamente
    return match n {
        1 => 100,
        2 => 200,
        else => 999
    }

fn main() -> int:
    # Closure passada como argumento
    let res = avaliar(2) |> (x) -> x + 1
    print("Resultado:", res)
    
    # Option e Result já estão disponíveis via Prelude
    let opt = Some(42)
    match opt:
        case Some(v): print("Option contém:", v)
        case None: print("Vazio")
    return 0
```

---

## 📦 Standard Library (`std/`)

* `std/math`: Funções matemáticas.
* `std/fs`: Manipulação de arquivos.
* `std/http`: Web Framework HTTP nativo.
* `std/net`: Sockets TCP e Proxy Reverso.
* `std/async`: Green Threads e troca de contexto (ucontext).
* `std/epoll`: Event Loop Assíncrono (I/O não-bloqueante).
* `std/vector`: Array Dinâmico que cresce automaticamente na memória (Heap).
* `std/map`: Hash Map (Dicionário) com tratamento de colisões via Linked List.
* `std/alloc`: Arena Allocator para sistemas Bare-Metal.
* `std/str`: Funções utilitárias de string (find, substr).
* `std/json`: Parser de JSON nativo escrito em Lumina.
* `std/sqlite`: Bindings para banco de dados SQLite.
* `std/raylib`: Bindings para engine gráfica Raylib.

---

## 📂 Estrutura do Projeto

```text
Lumina/
├── lumina_cli.py            # CLI, Build System, REPL, Cache e Package Manager
├── lumina_lsp.py            # Language Server Protocol (Autocomplete e Go to Definition)
├── playground.py            # Web Playground (JIT HTTP Server)
├── lumina/                  # Núcleo do Compilador (Lexer, Parser, Semantic, Codegen)
├── std/                     # Standard Library (.lm)
├── benchmarks/              # Suíte de benchmarks (Lumina vs C, Rust, Go)
├── examples/                # Exemplos de código (Proxy, JSON Parser, Wasm, etc)
├── tests/                   # Suíte de testes funcionais
├── scripts/                 # Scripts de automação
└── lumina-vscode/           # Extensão VS Code (Syntax + LSP Client)
```

---

## 🎨 Extensão para o VS Code e Sublime Text

A Lumina oferece suporte a realce de sintaxe, regras de indentação, **Autocomplete**, **Diagnóstico de Erros em tempo real** e **Go to Definition**:

1. Gere o pacote `.vsix` executando `npx vsce package` na pasta `lumina-vscode`.
2. No VS Code, abra o painel de Extensões (`Ctrl+Shift+X`).
3. Clique no menu de três pontos (`...`) no canto superior direito > **Instalar de VSIX...**.
4. Selecione o arquivo `.vsix` gerado e reinicie a janela.
5. Para Sublime Text, copie o arquivo `syntaxes/lumina.tmLanguage.json` para a pasta `Packages/Lumina/` e instale o pacote `LSP` da Package Control.

---

## 📜 Licença
Este projeto é distribuído sob a Licença **MIT**. Para mais detalhes, consulte o arquivo [LICENSE](LICENSE).