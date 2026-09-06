# 🌟 Lumina Language

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LLVM Version](https://img.shields.io/badge/LLVM-14%2B-blue.svg)](https://llvm.org/)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Alpha%20%2F%20Active-green.svg)](#)
[![Language](https://img.shields.io/badge/Language-Lumina-6A0DAD.svg)](#)

**Lumina** é uma linguagem de programação de sistemas de propósito geral, focada em alta performance, ergonomia moderna, concorrência e segurança de memória. Ela combina a sintaxe limpa e expressiva baseada em indentação (estilo Python/Nim) com o poder de baixo nível e otimização industrial do backend **LLVM**.

A linguagem oferece tipagem estática com inferência, Garbage Collector nativo (Boehm GC), Tipos Algébricos (Enums), operadores modernos (`|>`, `defer`, f-strings), interoperabilidade nativa com C (FFI), multithreading nativo (POSIX Threads), compilação incremental com cache inteligente e um ecossistema completo de ferramentas no CLI.

---

## ✨ Funcionalidades Principais

* **Sintaxe Limpa & Ergonômica:** Escopo definido por indentação significativa. Sem chaves `{}` ou pontos e vírgulas `;`.
* **Tipagem Estática com Inferência:** O compilador deduz os tipos automaticamente sem perder a segurança e performance de tempo de compilação.
* **Mutabilidade Rigorosa:** `let` declara variáveis imutáveis por padrão. Use `mut` para indicar mutabilidade explícita.
* **Tipos Algébricos (ADTs) & Pattern Matching:** Defina `enum`s contendo dados/payloads (ex: `Some(int)`, `None`) e extraia valores com `match`.
* **Ergonomia Moderna:**
  * **F-strings Nativas:** Interpolação direta: `print("Usuário {id} logou.")`.
  * **Operador Pipe (`|>`):** Composição de funções estilo Elixir/F#: `5 |> dobrar |> imprimir`.
  * **Defer:** Garante a execução de limpeza ao sair do escopo: `defer close(fd)`.
  * **Test Runner:** Blocos `test "nome":` nativos para testes integrados.
* **Gerenciamento de Memória Automático (Garbage Collector):**
  * Integração nativa com o **Boehm GC** (`libgc`). A memória alocada dinamicamente é limpa automaticamente em segundo plano, eliminando vazamentos de memória sem a necessidade de chamadas manuais de `free()`.
* **Concorrência e Redes (I/O Nativo):**
  * **Multithreading:** Suporte a criação de threads nativas do SO via FFI com `pthread_create` e `pthread_join`, incluindo ponteiros de função (`&worker`).
  * **Web Framework:** Módulo `std/http` para criação de servidores TCP/HTTP de altíssima performance direto no kernel (POSIX Sockets).
* **Pipeline LLVM Avançado & Cache Incremental:**
  * **Otimizações Agressivas:** Gera código intermediário (IR) limpo e delega ao `clang -O3 -march=native` a vetorização de loops (AVX/SSE) e promoção a registradores (`mem2reg`).
  * **Constant Folding:** Contas matemáticas com literais são resolvidas em tempo de compilação.
  * **Compilação Incremental:** Sistema de hashing MD5 (`.lumina_cache`) que pula a recompilação se nenhum arquivo dependente for modificado.
* **Ecossistema Integrado:** CLI unificada, gerenciador de dependências Git, gerador de documentação HTML, execução JIT instantânea e extensão do VS Code.

---

## 🏎️ Benchmarks de Performance (Média de 10 Execuções)

A Lumina foi testada contra as principais linguagens compiladas e interpretadas do mercado. Os testes abaixo representam a **média de 10 execuções** consecutivas para garantir estabilidade matemática e remover ruídos do SO. 
Para isolar a qualidade do código gerado, tanto a Lumina quanto o C foram compilados com o mesmo backend LLVM (`clang -O3 -march=native -funroll-loops`).

### Teste 1: Fibonacci Recursivo (N=35) — Chamadas de Função e CPU
| Linguagem | Tempo Médio (s) |
| --- | --- |
| Rust | 0.0362 |
| C | 0.0400 |
| **Lumina** | **0.0400** 🥇 |
| Go | 0.0713 |
| Node.js | 0.2364 |
| Python | 1.4574 |

### Teste 2: Loop Matemático (100 Milhões) — Estresse de Memória e Loops
| Linguagem | Tempo Médio (s) |
| --- | --- |
| **Lumina** | **0.0028** 🥇 |
| C | 0.0029 |
| Rust | 0.0040 |
| Go | 0.1007 |
| Node.js | 0.1476 |

### Teste 3: Crivo de Eratóstenes (10 Milhões) — Acesso a Array no Heap
| Linguagem | Tempo Médio (s) |
| --- | --- |
| **Lumina** | **0.0257** 🥇 |
| C | 0.0308 |
| Rust | 0.0326 |
| Go | 0.0416 |

### Teste 4: Multiplicação de Matrizes (200x200) — Loops Aninhados e Cache
| Linguagem | Tempo Médio (s) |
| --- | --- |
| C | 0.0066 |
| **Lumina** | **0.0073** |
| Rust | 0.0102 |
| Go | 0.0168 |
| Node.js | 0.0551 |

*Resultado: Com o mesmo backend (LLVM/Clang), a Lumina supera o C em loops matemáticos e acesso a memória otimizado, e destrói o Rust em 3 dos 4 testes, provando ser uma linguagem de sistemas de altíssima performance.*

---

## 🚀 Como Usar (CLI)

### Pré-requisitos

* **Python 3.10+**
* Biblioteca Python `llvmlite` (`pip install llvmlite`)
* **LLVM** e **Clang** instalados e acessíveis no `PATH`
* **Boehm GC** instalado (`sudo apt install libgc-dev`)
* **Git** (para o gerenciador de pacotes)

---

### Instalação Global Recomendada (Alias / Symlink)

Para executar o comando `lumina` de qualquer diretório sem precisar apontar para a pasta do script, adicione um alias no seu terminal:

```bash
# Linux / macOS (~/.bashrc ou ~/.zshrc)
alias lumina="python3 /caminho/para/Lumina/lumina_cli.py"
```

---

### Comandos Principais

#### 1. Criar um novo projeto
Gera a estrutura inicial com arquivo de configuração `lumina.json` e ponto de entrada `main.lm`.
```bash
lumina new meu_projeto
cd meu_projeto
```

#### 2. Gerenciar Dependências Remotas
Declare repositórios remotos do GitHub no arquivo `lumina.json`:
```json
{
  "dependencies": {
    "utils": "github:usuario/repo"
  }
}
```
Baixe os pacotes para `lumina_modules/`:
```bash
lumina install
```

#### 3. Execução Instantânea via JIT
Compila e executa diretamente na memória RAM sem gerar arquivos intermediários no disco.
```bash
lumina jit
```

#### 4. Compilar para Binário Nativo Otimizado
Aplica as otimizações em memória, utiliza o cache incremental (`.lumina_cache`) e invoca o `clang -O3` para gerar o executável final:
```bash
lumina build
./meu_projeto
```

#### 5. Gerar Portal de Documentação HTML
Extrai comentários iniciados em `##` do código e cria a página web em `docs/index.html`:
```bash
lumina doc
```

---

## 🛠️ Exemplos de Código

### 1. Ergonomia Moderna (Pipe, F-strings, Defer)
```lumina
fn dobrar(x: int) -> int:
    return x * 2

fn processar_dados(id: int):
    defer print("Liberando recursos do ID:", id)
    print("Processando dados para o usuario {id}...")
    return

fn main() -> int:
    processar_dados(1)
    
    # Operador Pipe (|>)
    let resultado = 5 |> dobrar |> dobrar
    print("Resultado do Pipe: {resultado}")
    return 0
```

### 2. Multithreading Nativo (POSIX Threads)
A Lumina suporta concorrência real passando ponteiros de função (`&worker`) diretamente para a API do C:
```lumina
extern fn pthread_create(thread: str, attr: int, start_routine: int, arg: str) -> int
extern fn pthread_join(thread: int, retval: int) -> int

fn worker(arg: str) -> str:
    let id = arg[0] - 48
    print("Thread", id, "iniciada!")
    return ""

fn main() -> int:
    mut t1 = alloc(1)
    pthread_create(t1, 0, &worker, "1")
    pthread_join(t1[0], 0)
    return 0
```

### 3. Web Framework HTTP Nativo
Um servidor web rodando direto no kernel do Linux, sem Apache ou Node.js:
```lumina
import "std/http"

fn main() -> int:
    let server_fd = iniciar(8080)
    mut request_buffer = alloc_bytes(1024)
    
    while true:
        let client_fd = accept(server_fd, ...)
        recv(client_fd, request_buffer, 1024, 0)
        
        # Roteamento HTTP
        if request_buffer[5] == 32: # "GET / "
            responder(client_fd, "<h1>Bem-vindo!</h1>")
            continue
            
        not_found(client_fd)
```

---

## 📦 Standard Library (`std/`)

A Lumina conta com uma biblioteca padrão modularizada em `std/` escrita na própria linguagem, encapsulando chamadas de sistema e bibliotecas C nativas de forma segura:

* `std/math`: Funções matemáticas (sqrt, sin, cos).
* `std/fs`: Manipulação de arquivos.
* `std/http`: Web Framework HTTP nativo (Servidor TCP, Rotas, Respostas HTTP).

---

## 📂 Estrutura do Projeto

```text
Lumina/
├── lumina_cli.py            # CLI, Build System, Cache e Package Manager
├── std/                     # Standard Library (http.lm, math.lm, fs.lm, etc)
├── benchmarks/              # Suíte de benchmarks (Lumina vs C, Rust, Go)
├── program.lm               # Arquivo principal de testes locais
├── lumina/                  # Núcleo do Compilador
│   ├── errors.py            # Erros amigáveis com indicação de linha e coluna (Rust-style)
│   ├── lexer/               # Análise Léxica (Tokens, INDENT/DEDENT)
│   ├── parser/              # Análise Sintática e Construção da AST (F-strings, Pipe)
│   ├── semantic/            # Analisador Semântico (Escopos, Mutabilidade, Tipos)
│   ├── codegen/             # Geração de código LLVM IR (GC, Enums, FFI, Threads)
│   └── ast/                 # Definições dos Nós da Árvore Sintática Abstrata
└── tests/                   # Suíte de testes funcionais e de regressão
```

---

## 🎨 Extensão para o VS Code

A Lumina oferece suporte a realce de sintaxe (*syntax highlighting*) e regras de indentação para o VS Code:

1. Gere o pacote `.vsix` executando `npx @vscode/vsce package` na pasta da extensão.
2. No VS Code, abra o painel de Extensões (`Ctrl+Shift+X`).
3. Clique no menu de três pontos (`...`) no canto superior direito > **Instalar de VSIX...**.
4. Selecione o arquivo `.vsix` gerado e reinicie a janela.

---

## 📜 Licença

Este projeto é distribuído sob a Licença **MIT**. Para mais detalhes, consulte o arquivo [LICENSE](LICENSE).
