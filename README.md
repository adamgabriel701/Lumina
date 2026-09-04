# 🌟 Lumina Language

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LLVM Version](https://img.shields.io/badge/LLVM-14%2B-blue.svg)](https://llvm.org/)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Alpha%20%2F%20Active-green.svg)](#)
[![Language](https://img.shields.io/badge/Language-Lumina-6A0DAD.svg)](#)

**Lumina** é uma linguagem de programação de sistemas de propósito geral, focada em alta performance, ergonomia e segurança de memória. Ela combina a sintaxe limpa e expressiva baseada em indentação (estilo Python/Nim) com o poder de baixo nível e otimização industrial do backend **LLVM**.

A linguagem oferece tipagem estática com inferência, controle de memória híbrido (manual + RAII), Tipos Algébricos (Enums), interoperabilidade nativa com C (FFI), compilação incremental com cache inteligente e um ecossistema completo de ferramentas no CLI.

---

## ✨ Funcionalidades Principais

* **Sintaxe Limpa & Indentada:** Escopo definido por indentação significativa (sem chaves `{}` ou pontos e vírgulas `;`).
* **Tipagem Estática com Inferência:** O compilador deduz os tipos automaticamente sem perder a segurança e performance de tempo de compilação.
* **Mutabilidade Rigorosa:** `let` declara variáveis imutáveis por padrão. Use `mut` para indicar mutabilidade explícita.
* **Tipos Algébricos (ADTs) & Pattern Matching:** Defina `enum`s contendo dados/payloads (ex: `Some(int)`, `None`) e extraia valores com `match`.
* **Gerenciamento de Memória Híbrido (RAII & Auto-Free):**
  * Suporte a ponteiros explícitos (`&` e `*`), aritmética e alocação dinâmica (`alloc` / `free`).
  * **RAII:** Recursos e buffers alocados no Heap são automaticamente destruídos no término do escopo, prevenindo vazamentos de memória sem a sobrecarga de um Garbage Collector.

* **Pipeline LLVM Avançado & Cache Incremental:**
  * **Otimizações LLVM em Memória:** Aplica `PassManager` (nível `-O2`) diretamente na AST intermediária.
  * **Compilação Incremental:** Sistema de hashing MD5 (`.lumina_cache`) que pula a recompilação se nenhum arquivo dependente for modificado.
  * **Proteção Contra Imports Circulares:** O resolvedor de módulos rastreia e bloqueia grafos de dependência cíclicos em tempo de compilação.

* **Ecossistema Integrado:** CLI unificada (`lumina_cli.py`), gerenciador de dependências Git (`lumina install`), gerador de documentação HTML (`lumina doc`), execução JIT instantânea e extensão oficial do VS Code.

---

## 🏎️ Benchmarks de Performance

A Lumina foi testada contra as principais linguagens compiladas e interpretadas do mercado em ambiente de estresse (otimização `-O2` para C, C++ e Lumina, `-O` para Rust, nativo para Go).

### Teste 1: Fibonacci Recursivo (N=35) — Chamadas de Função e CPU

| Linguagem | Tempo (s) |
| --- | --- |
| C++ | 0.0239 |
| C | 0.0264 |
| Rust | 0.0318 |
| **Lumina** | **0.0393** |
| Go | 0.0683 |
| Node.js | 0.4414 |
| Python | 1.5887 |

### Teste 2: Loop Matemático (100 Milhões) — Estresse de Memória e Loops

| Linguagem | Tempo (s) |
| --- | --- |
| **Lumina** | **0.0026** |
| C | 0.0027 |
| Rust | 0.0028 |
| C++ | 0.0035 |
| Go | 0.0974 |
| Node.js | 0.1691 |

---

## 🚀 Como Usar (CLI)

### Pré-requisitos

* **Python 3.10+**
* Biblioteca `llvmlite` (`pip install llvmlite`)
* **LLVM** e **Clang** instalados e acessíveis no `PATH`
* **Git** (para o gerenciador de pacotes)

---

### Instalação Global Recomendada (Alias / Symlink)

Para executar o comando `lumina` de qualquer diretório sem precisar apontar para a pasta do script, adicione um alias no seu terminal:

```bash
# Linux / macOS (~/.bashrc ou ~/.zshrc)
alias lumina="python3 /caminho/para/Lumina/lumina_cli.py"

# Windows (PowerShell - $PROFILE)
function lumina { python C:\caminho\para\Lumina\lumina_cli.py $args }
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
  "name": "meu_projeto",
  "entry": "main.lm",
  "libs": [],
  "dependencies": {
    "utils": "github:usuario/repo"
  }
}
```

Baixe ou atualize todos os pacotes dentro do diretório `lumina_modules/`:

```bash
lumina install
```

#### 3. Execução Instantânea via JIT

Compila e executa diretamente na memória RAM sem gerar arquivos intermediários no disco.

```bash
lumina jit
```

#### 4. Compilar para Binário Nativo Otimizado

Aplica as otimizações em memória, utiliza o cache incremental (`.lumina_cache`) e invoca o `clang` para gerar o executável final:

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

### 1. Tipos Algébricos, Pattern Matching e FFI Nativa

```lumina
# Enum com Payload
enum Option:
    Some(int)
    None

fn dividir(a: int, b: int) -> Option:
    if b == 0:
        return None
    return Some(a / b)

fn main() -> int:
    let res = dividir(10, 2)
    
    # Extração de dados via Pattern Matching
    match res:
        case Some(val):
            print("Sucesso! Resultado:", val)
        case None:
            print("Falha: divisao por zero")
            
    # Chamando funções C diretamente via FFI
    extern fn sqrt(x: float) -> float
    print("Raiz quadrada de 16.0:", sqrt(16.0))
    
    return 0
```

### 2. Gerenciamento Automático de Memória (RAII / Auto-Free)

O compilador insere as instruções de limpeza no término do escopo da variável, evitando *memory leaks* sem necessitar de Garbage Collector:

```lumina
fn processar_dados():
    # Alocação dinâmica manual no Heap (retorna um ponteiro *int)
    mut arr = alloc(1024)
    
    arr[0] = 42
    print("Primeiro elemento do array no Heap:", arr[0])
    
    # O compilador Lumina injeta automaticamente o 'free(arr)' 
    # ao atingir o fim da função (RAII), prevenindo vazamento de memória!

fn main() -> int:
    processar_dados()
    return 0
```

---

## 📦 Standard Library (`std/`)

A Lumina conta com uma biblioteca padrão modularizada em `std/` escrita na própria linguagem, encapsulando chamadas de sistema e bibliotecas C nativas de forma segura:

```lumina
import "std/math"
import "std/fs"

fn main() -> int:
    let angulo = 3.14159 / 2.0
    print("Seno de 90 graus:", std_math.sin(angulo))
    return 0
```

---

## 📂 Estrutura do Projeto

```text
Lumina/
├── lumina_cli.py            # CLI, Build System, Cache e Package Manager
├── std/                     # Standard Library (math.lm, fs.lm, etc)
├── benchmarks/              # Suíte de benchmarks (Lumina vs C, Rust, Go)
├── program.lm               # Arquivo principal de testes locais
├── lumina/                  # Núcleo do Compilador
│   ├── errors.py            # Erros amigáveis com indicação de linha e coluna (Rust-style)
│   ├── lexer/               # Análise Léxica (Tokens, INDENT/DEDENT)
│   ├── parser/              # Análise Sintática e Construção da AST
│   ├── semantic/            # Analisador Semântico (Escopos, Mutabilidade, Tipos)
│   ├── codegen/             # Geração de código LLVM IR (RAII, Enums, FFI)
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
