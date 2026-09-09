# 🌟 Lumina Language

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LLVM Version](https://img.shields.io/badge/LLVM-14%2B-blue.svg)](https://llvm.org/)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Alpha%20%2F%20Active-green.svg)](#)
[![Language](https://img.shields.io/badge/Language-Lumina-6A0DAD.svg)](#)

**Lumina** é uma linguagem de programação de sistemas de propósito geral, focada em alta performance, ergonomia moderna, concorrência e segurança de memória. Ela combina a sintaxe limpa e expressiva baseada em indentação (estilo Python/Nim) com o poder de baixo nível e otimização industrial do backend **LLVM**.

A linguagem oferece tipagem estática com inferência, Garbage Collector nativo (Boehm GC), Tipos Algébricos (Enums), operadores modernos (`|>`, `defer`, `?.`, `?`), Generics (`<T>`), interoperabilidade nativa com C/C++ (FFI), suporte a Green Threads e I/O Assíncrono (`epoll`), um REPL interativo, um Web Playground, compilação incremental, e é **Cross-Platform** (compila para binários nativos x86_64/ARM e para WebAssembly).

---

## ✨ Funcionalidades Principais

* **Sintaxe Limpa & Ergonômica:** Escopo definido por indentação significativa. Sem chaves `{}` ou pontos e vírgulas `;`.
* **Tipagem Estática com Inferência:** O compilador deduz os tipos automaticamente.
* **Tipos Algébricos (ADTs) & Pattern Matching:** `enum`s com payloads (ex: `Some(int)`, `None`) e extração via `match`.
* **Generics (Polimorfismo):** Suporte a tipos genéricos `<T>` em Structs e Funções.
* **Ergonomia Moderna:**
  * **F-strings Nativas:** `print("Usuário {id} logou.")`.
  * **Operador Pipe (`|>`):** `5 |> dobrar |> imprimir`.
  * **Navegação Segura (`?.`):** Evita Segmentation Faults ao acessar structs nulas: `usuario?.perfil?.nome`.
  * **Propagação de Erros (`?`):** Retorna erros automaticamente sem `try/catch`: `let val = abrir_arquivo()?`.
  * **Defer & Assert:** Garantia de limpeza de escopo e testes nativos.
  * **Auto-Formatter:** `lumina fmt` formata o código automaticamente.
* **Gerenciamento de Memória Automático:** Integração nativa com o **Boehm GC** (`libgc`).
* **Otimizações de Compilador:** Escape Analysis (aloca na Stack em vez do Heap se a variável não fugir), Tail Call Optimization (TCO) e DWARF Debug Info (depurável no GDB/LLDB).
* **Concorrência e Redes:**
  * **Multithreading:** Threads nativas do SO via `pthread_create`.
  * **Green Threads:** Suporte a Corrotinas via troca de contexto de CPU (`ucontext`).
  * **Async I/O:** Event Loop não-bloqueante de baixa latência usando `epoll` do Linux.
  * **Web Framework & Proxy:** Servidores TCP/HTTP e Proxy Reverso.
* **Pipeline LLVM Avançado & Cache:** Otimizações `clang -O3 -march=native` e hashing MD5 para compilação instantânea.
* **Ecossistema Integrado:** CLI, REPL, Web Playground (JIT), Gerenciador de Pacotes Git, Auto-documentador HTML, Auto-Gerador de Bindings C, Native Benchmarking (`bench`) e Extensão VS Code com **LSP (Autocomplete)**.
* **Cross-Platform (Wasm):** Compila para `.wasm`, rodando em navegadores e Node.js.

---

## 🏎️ Benchmarks de Performance (Média de 10 Execuções)

Para isolar a qualidade do código gerado, tanto a Lumina quanto o C foram compilados com o mesmo backend LLVM (`clang -O3 -march=native -funroll-loops`).

| Teste | C | Rust | **Lumina** | Go | Node.js | Python |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Loop Matemático** (100M) | 0.0029s | 0.0040s | **0.0028s** 🥇 | 0.1007s | 0.1476s | - |
| **Crivo de Eratóstenes** (10M) | 0.0308s | 0.0326s | **0.0257s** 🥇 | 0.0416s | - | - |
| **Matrizes** (200x200) | **0.0066s** | 0.0102s | **0.0073s** | 0.0168s | 0.0551s | - |
| **Fibonacci** (N=35) | 0.0400s | 0.0362s | **0.0400s** 🥇 | 0.0713s | 0.2364s | 1.4574s |

*Resultado: A Lumina supera o C em loops matemáticos e acesso a memória, e destrói o Rust em 3 dos 4 testes.*

---

## 🚀 Como Usar (CLI)

### Pré-requisitos
* **Python 3.10+** e `llvmlite` (`pip install llvmlite`)
* **LLVM** e **Clang** no `PATH`
* **Boehm GC** (`sudo apt install libgc-dev`)
* **Git**

### Comandos Principais
```bash
lumina new meu_projeto      # Cria a estrutura inicial
lumina install              # Baixa dependências do GitHub
lumina bind header.h nome   # Gera bindings FFI a partir de um arquivo C
lumina fmt arquivo.lm       # Formata o código automaticamente
lumina clean                # Limpa o cache e binários antigos
lumina run arquivo.lm       # Compila e executa o binário nativo em um único passo
lumina repl                 # Inicia o console interativo (REPL JIT)
lumina jit                  # Executa instantaneamente na memória RAM
lumina build                # Compila para binário nativo otimizado (-O3)
lumina build app.lm --wasm  # Compila para WebAssembly (.wasm)
lumina doc                  # Gera portal de documentação HTML
```

### 🌐 Web Playground (JIT)
Inicie um servidor web local que compila e executa código Lumina instantaneamente na memória RAM via motor MCJIT, capturando o `printf` nativo e exibindo no navegador:
```bash
python3 playground.py
# Acesse http://localhost:8080 no navegador
```

---

## 🛠️ Exemplos de Código

### 1. Ergonomia Moderna (Pipe, F-strings, Defer, Safe Nav)
```lumina
fn dobrar(x: int) -> int:
    return x * 2

fn processar_dados(id: int):
    defer print("Liberando recursos do ID:", id)
    print("Processando dados para o usuario {id}...")

fn main() -> int:
    processar_dados(1)
    
    mut u: Usuario
    let safe_id = u?.id  # Navegação segura (não crasha se 'u' for nulo)
    
    let resultado = 5 |> dobrar |> dobrar
    print("Resultado do Pipe: {resultado}")
    return 0
```

### 2. Tratamento de Erros com `?` (Zero-cost)
```lumina
enum Result:
    Ok(int)
    Err(int)

fn dividir(a: int, b: int) -> Result:
    if b == 0: return Err(1)
    return Ok(a / b)

fn processar() -> Result:
    # Se dividir retornar Err, a função 'processar' para e retorna o Err imediatamente
    let val = dividir(10, 0)?
    print("Deu certo! Valor:", val)
    return Ok(100)
```

### 3. Generics e Native Benchmarking
```lumina
struct Box<T>:
    data: T

fn somar(n: int) -> int:
    mut total = 0
    mut i = 0
    while i < n:
        total += i
        i += 1
    return total

fn main() -> int:
    bench "somar 1 milhao":
        let res = somar(1000000)
        print("Resultado:", res)
    return 0
```

### 4. WebAssembly (Node.js)
Compile com `--wasm` e carregue no Node.js:
```javascript
const fs = require('fs');
async function run() {
    const wasmBuffer = fs.readFileSync('wasm_math.wasm');
    const { instance } = await WebAssembly.instantiate(wasmBuffer, {});
    const fib = instance.exports.fib;
    const result = fib(10n); // Usa BigInt pois a Lumina usa inteiros de 64 bits
    console.log("🚀 Fibonacci(10):", result);
}
run();
```

---

## 📦 Standard Library (`std/`)

A Lumina conta com uma biblioteca padrão modularizada escrita na própria linguagem, encapsulando chamadas de sistema e bibliotecas C nativas de forma segura:

* `std/math`: Funções matemáticas.
* `std/fs`: Manipulação de arquivos.
* `std/http`: Web Framework HTTP nativo.
* `std/net`: Sockets TCP e Proxy Reverso.
* `std/async`: Green Threads e troca de contexto (ucontext).
* `std/epoll`: Event Loop Assíncrono (I/O não-bloqueante).
* `std/vector`: Array Dinâmico que cresce automaticamente na memória (Heap).
* `std/sqlite`: Bindings para banco de dados SQLite.
* `std/raylib`: Bindings para engine gráfica Raylib.

---

## 📂 Estrutura do Projeto

```text
Lumina/
├── lumina_cli.py            # CLI, Build System, REPL, Cache e Package Manager
├── lumina_lsp.py            # Language Server Protocol (Autocomplete e Diagnóstico)
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

## 🎨 Extensão para o VS Code

A Lumina oferece suporte a realce de sintaxe, regras de indentação, **Autocomplete** e **Diagnóstico de Erros em tempo real** para o VS Code:

1. Gere o pacote `.vsix` executando `npx vsce package` na pasta `lumina-vscode`.
2. No VS Code, abra o painel de Extensões (`Ctrl+Shift+X`).
3. Clique no menu de três pontos (`...`) no canto superior direito > **Instalar de VSIX...**.
4. Selecione o arquivo `.vsix` gerado e reinicie a janela.

---

## 📜 Licença
Este projeto é distribuído sob a Licença **MIT**. Para mais detalhes, consulte o arquivo [LICENSE](LICENSE).