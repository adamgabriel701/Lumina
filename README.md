# 🌟 Lumina

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LLVM](https://img.shields.io/badge/LLVM-14%2B-blue.svg)](https://llvm.org/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?logo=python\&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](#-status)
[![Tests](https://img.shields.io/badge/tests-440%20passed-brightgreen.svg)](docs/engineering/tests.md)
[![Examples](https://img.shields.io/badge/examples-54%20pass%20%2F%2017%20skip-success.svg)](examples/)
[![Benchmarks](https://img.shields.io/badge/benchmarks-5%20suites-blue.svg)](benchmarks/results/)
[![Cross-compile](https://img.shields.io/badge/cross--compile-arm64%20%7C%20armv7%20%7C%20risc--v%20%7C%20wasm-blueviolet.svg)](#-cross-compilation)
[![Linker](https://img.shields.io/badge/linker-lumina--ld-orange.svg)](docs/internals/linking.md)

**Lumina** é uma linguagem de programação de sistemas com sintaxe limpa baseada em indentação, backend **LLVM** e foco em ergonomia moderna, controle de memória, performance e tooling.

É uma linguagem **estaticamente tipada e compilada**, sem `;` e sem `{}` como delimitadores estruturais.

A linguagem possui:

* sintaxe baseada em indentação significativa;
* inferência de tipos;
* generics e monomorphization;
* traits com métodos default;
* enums algébricos com múltiplos payloads;
* pattern matching;
* closures;
* macros e `comptime`;
* TCO;
* Boehm GC + `--no-gc`;
* escape analysis;
* FFI;
* concorrência e I/O assíncrono;
* backend LLVM;
* JIT e REPL;
* LSP;
* formatter e linter;
* compilação incremental;
* cross-compilation;
* WebAssembly;
* linker ELF próprio para **x86_64 Linux**.

📖 **Documentação completa em [`docs/`](docs/README.md).**

---

## ✨ Por que Lumina?

### Sintaxe que você lê em voz alta

Lumina usa indentação significativa e combina recursos modernos sem depender de blocos delimitados por `{}`.

```lumina
fn main() -> int:
    let usuario = buscar_usuario(42)?

    defer log("fim")

    usuario?.nome |> imprimir

    return 0
```

O objetivo é manter o código compacto sem sacrificar recursos normalmente encontrados em linguagens de sistemas.

### Performance próxima de C

O backend LLVM permite que Lumina gere código nativo competitivo em workloads computacionais.

Nos benchmarks atuais, Lumina fica próxima de C em vários testes compute-bound:

* `fib`: 0.97× de C;
* `loop`: 1.01×;
* `matrix`: 0.97×.

O benchmark de alocação mostra explicitamente o custo do Boehm GC, enquanto `--no-gc` reduz significativamente esse overhead.

A metodologia completa está em [`docs/engineering/benchmarks.md`](docs/engineering/benchmarks.md).

### Memória com GC ou controle manual

O runtime usa **Boehm GC** por padrão, mas Lumina também oferece:

* escape analysis;
* stack allocation para determinados `alloc(N)`;
* `--no-gc`;
* `malloc`/`free` sem GC;
* `nil` como null pointer real;
* `@safe` para null checks automáticos;
* `?.` para navegação segura explícita.

### Metaprogramação em compile-time

Lumina possui:

* `@macro`;
* macros de expressão e statement;
* `@derive`;
* `comptime`;
* constant folding;
* atributos LLVM como `@inline`, `@noinline`, `@cold` e `@hot`.

### Tooling completo

O ecossistema inclui:

* compilador LLVM;
* JIT;
* REPL persistente;
* LSP;
* formatter;
* linter;
* documentação automática;
* FFI binding generator;
* build incremental;
* cross-compilation;
* Web Playground;
* linker próprio.

---

# 🚀 Quickstart

## 1. Pré-requisitos

### Ubuntu/Debian

```bash
sudo apt install -y llvm-14 clang libgc-dev python3.11 python3-pip
```

### Fedora

```bash
sudo dnf install -y llvm-devel clang gc-devel python3.11
```

Para desenvolvimento completo, incluindo testes de cross-compilation:

```bash
sudo apt install -y qemu-user
```

---

## 2. Clone o projeto

```bash
git clone https://github.com/adamgabriel701/Lumina.git
cd Lumina
```

---

## 3. Instale

Para uso:

```bash
pip install -e .
```

Para desenvolvimento:

```bash
pip install -e ".[dev]"
```

---

## 4. Crie seu primeiro projeto

```bash
lumina new ola

cd ola

lumina run main.lm
```

Saída:

```text
Hello from ola!
```

---

# 👀 A linguagem em 60 segundos

Um programa combinando enums, pattern matching, guards, `for`, F-strings e I/O:

```lumina
import "std/io"

enum Resposta:
    Texto(str)
    Numero(int)
    Vazia

fn interpretar(r: Resposta) -> str:
    match r:
        case Texto(s) if s.starts_with("olá"):
            return "saudação"

        case Texto(s):
            return s

        case Numero(n):
            return $"número: {n}"

        case Vazia:
            return "—"

    return "?"

fn main() -> int:
    let respostas = [
        Texto("olá, mundo"),
        Numero(42),
        Vazia
    ]

    for i, r in respostas:
        let categoria = interpretar(r)
        write_line($"{i}: {categoria}")

    return 0
```

Saída:

```text
0: saudação
1: número: 42
2: —
```

Mais exemplos estão disponíveis em [`examples/`](examples/).

---

# 🧠 Modelo de memória

Lumina possui diferentes estratégias de gerenciamento dependendo do contexto:

| Situação                      | Comportamento                                           |
| ----------------------------- | ------------------------------------------------------- |
| `alloc(N)` com `N` variável   | Boehm GC (`GC_malloc`)                                  |
| `alloc(N)` literal sem escape | Stack (`alloca`), quando permitido pela escape analysis |
| `free(x)` explícito           | `GC_free` quando o objeto usa GC                        |
| `--no-gc`                     | `malloc` / `free` da libc                               |
| `--target=wasm`               | `--no-gc`                                               |
| `ptr`                         | ponteiro bruto                                          |
| `str`                         | `i8*` null-terminated                                   |
| `nil`                         | null pointer C-style                                    |
| `none`                        | `Option::None`                                          |
| `u.id` sem `@safe`            | acesso direto                                           |
| `u.id` com `@safe`            | null check automático                                   |
| `u?.id`                       | navegação segura explícita                              |

O Boehm GC é inicializado antes das alocações que dependem dele.

Com `--no-gc`, Lumina pode ser utilizada em ambientes nos quais o runtime de GC não está disponível ou não é desejado.

Mais detalhes em [`docs/internals.md`](docs/internals.md).

---

# 🔥 Features por tema

## Sistema de tipos

* **Inferência estática** em retornos, lambdas, expressões binárias, generics, `Option<T>`, tuplas e `comptime`.
* **Enums multi-payload** com variantes bare.
* **Pattern matching** com:

  * guards;
  * multi-pattern;
  * wildcard;
  * destructuring;
  * self-binding.
* **Generics com monomorphization**.
* Generics aninhados.
* **Traits com métodos default**.
* Especialização para tipos concretos.
* **Type aliases**, inclusive genéricos.
* **Tipos de função** como `fn(int) -> int`.
* **Tuplas** com destructuring heterogêneo.
* Distinção entre `nil` e `none`.

Exemplo:

```lumina
type Pair<T>:
    first: T
    second: T

fn swap<T>(p: Pair<T>) -> Pair<T>:
    return Pair(
        first = p.second,
        second = p.first
    )
```

---

## Memória e segurança

* Boehm GC por padrão.
* Escape analysis.
* Stack allocation para determinadas alocações.
* `--no-gc`.
* `@safe`.
* `nil` como ponteiro nulo real.
* `free`.
* Compatibilidade com FFI.

---

## Concorrência

Lumina possui suporte para:

* canais CSP;
* `pthread_mutex`;
* `pthread_cond`;
* green threads;
* corrotinas via `ucontext`;
* I/O assíncrono;
* `epoll`;
* `O_NONBLOCK`.

Alguns desses componentes continuam sendo **experimentais** e possuem exemplos marcados como `SKIP` na suíte de exemplos.

---

## Metaprogramação

### Macros

```lumina
@macro
fn hello():
    println("Hello!")
```

Lumina suporta macros de expressão e macros multi-statement utilizando a sintaxe:

```text
nome!(args)
```

### Derive

```lumina
@derive(Eq, PartialEq, Debug, Display, Clone, Default)
struct User:
    id: int
    name: str
```

### Compile-time

```lumina
comptime:
    ...
```

Constant folding é realizado durante a compilação quando aplicável.

---

# 🛠️ Tooling

## Linker próprio

Lumina possui um linker ELF estático próprio:

```bash
lumina build app.lm --linker=self
```

O `lumina-ld` substitui a etapa de link convencional para o alvo **Linux x86_64**, utilizando uma runtime freestanding própria.

O resultado pode ser um executável:

```text
ELF 64-bit LSB executable, statically linked
```

sem depender do dynamic linker do sistema.

> **Importante:** o linker próprio atualmente é destinado ao **x86_64 Linux**. Cross-compilation e WebAssembly utilizam o linker LLVM/Clang.

Documentação:

[`docs/internals/linking.md`](docs/internals/linking.md)

---

## LSP

O LSP oferece recursos como:

* hover;
* go-to-definition;
* references;
* rename;
* outline;
* semantic tokens;
* resolução de nomes considerando escopo.

---

## Linter

```bash
lumina lint arquivo.lm
```

Warnings disponíveis atualmente:

```text
W001
W002
W003
W004
W005
```

Para integração com ferramentas:

```bash
lumina lint arquivo.lm --format=json
```

O exit code corresponde ao número de warnings encontrados.

---

## Formatter

```bash
lumina fmt arquivo.lm
```

O formatter preserva elementos importantes do código, incluindo comentários, atributos e construções específicas da linguagem.

---

## REPL

```bash
lumina repl
```

Com comandos como:

```text
:history
:decls
:clear
```

---

## Documentação automática

```bash
lumina doc
```

Formatos disponíveis:

```bash
lumina doc --format=html
lumina doc --format=md
lumina doc --format=json
```

---

## FFI

O comando:

```bash
lumina bind header.h nome
```

gera bindings para headers C.

A integração com C/C++ continua tendo áreas que dependem do ambiente e de componentes externos.

---

# 🔗 Linker próprio

O linker é composto por:

```text
linker/
├── Makefile
├── rt.c
├── start.S
├── lumina-ld
├── test.sh
└── triagem.sh
```

A runtime freestanding implementa as operações necessárias diretamente sobre syscalls Linux.

Exemplo:

```bash
cd linker
make
```

Depois:

```bash
lumina build examples/main.lm --linker=self
```

O pipeline pode ser visualizado como:

```text
Lumina source
     │
     ▼
  Lexer
     │
     ▼
  Parser
     │
     ▼
 Semantic analysis
     │
     ▼
  LLVM IR
     │
     ▼
   clang -c
     │
     ▼
  ELF objects
     │
     ▼
 lumina-ld
     │
     ▼
Static ELF x86_64
```

A triagem atual do linker apresenta:

```text
PASS=53
FAIL-COMPILE=0
FAIL-LINK=0
FAIL-RUN=0
SKIP=18
```

Os skips correspondem principalmente a exemplos que dependem de subsistemas fora do escopo atual do linker, como pthread, raylib, FFI C++, WASM ou servidores que não terminam automaticamente.

Veja [`docs/internals/linking.md`](docs/internals/linking.md) para detalhes de arquitetura, runtime, símbolos, debugging e extensão.

---

# 📚 Exemplos

O diretório [`examples/`](examples/) contém **71 arquivos** cobrindo diferentes partes da linguagem.

| Categoria             | Exemplos                                                            |
| --------------------- | ------------------------------------------------------------------- |
| **Fundamentos**       | `features.lm`, `features_showcase.lm`, `ergonomia.lm`               |
| **Generics & types**  | `generics_test.lm`, `monomorph_test.lm`, `nested_generics.lm`       |
| **Closures & HOFs**   | `lambda_test.lm`, `iter_test.lm`, `iterator_test.lm`                |
| **Traits & impls**    | `trait_test.lm`, `trait_default_test.lm`, `overload_test.lm`        |
| **Pattern matching**  | `match_expr_test.lm`, `match_struct_test.lm`, `destructure_test.lm` |
| **Macros**            | `comptime_test.lm`, `macro_test.lm`                                 |
| **Concorrência**      | `threads.lm`, `coroutines.lm`, `async_server.lm`                    |
| **I/O e web**         | `http_framework.lm`, `server.lm`, `proxy.lm`                        |
| **FFI & raylib**      | `ffi_test.lm`, `chip8.lm`, `engine.lm`                              |
| **Projetos maiores**  | `json_parser.lm`, `sql_engine.lm`, `vm.lm`, `search_engine.lm`      |
| **Bare-metal & WASM** | `wasm_math.lm`, `wasm_memory.lm`, `wasm_js_interop.lm`              |

A verificação automatizada pode ser executada com:

```bash
./scripts/check_examples.sh --run
```

Resultado atual:

```text
54 PASS
17 SKIP
0 FAIL
```

---

# 📊 Status

**Active / Public Release**

O compilador possui pipeline end-to-end funcional, uma suíte extensa de testes e ferramentas suficientes para desenvolver, testar e experimentar programas reais em Lumina.

## Verificação atual

| Métrica           |                      Resultado |
| ----------------- | -----------------------------: |
| Testes `pytest`   |                 **440 passed** |
| Suite standalone  |                      **28/28** |
| Exemplos          | **54 PASS / 17 SKIP / 0 FAIL** |
| Triagem do linker | **53 PASS / 18 SKIP / 0 FAIL** |

### Pytest

```bash
pytest tests/ -q
```

Resultado:

```text
440 passed in 139.78s (0:02:19)
```

### Suite standalone

```bash
python3 run_tests.py
```

Resultado:

```text
28/28 verifications OK
```

### Exemplos

```bash
./scripts/check_examples.sh --run
```

Resultado:

```text
54 PASS / 17 SKIP / 0 FAIL
```

### Linker

```bash
./linker/triagem.sh examples
```

Resultado:

```text
PASS=53
FAIL-COMPILE=0
FAIL-LINK=0
FAIL-RUN=0
SKIP=18
```

## Exemplos atualmente ignorados

Os exemplos que aparecem como `SKIP` na verificação atual incluem:

```text
api
app
async_server
bootstrap_lexer
chip8
coroutines
database
engine
ffi_test
gc_test
http_framework
json_parser
proxy
serve
server
threads
util
wasm_js_interop
```

Os motivos variam conforme o exemplo e incluem dependências externas, subsistemas experimentais, FFI, WASM ou programas que não possuem comportamento adequado para execução automática na triagem.

Os motivos detalhados devem ser consultados em [`docs/engineering/bugs.md`](docs/engineering/bugs.md).

---

# ⚡ Performance

Os benchmarks utilizam mediana de 20 execuções, com 3 warm-ups e afinidade fixa em uma vCPU.

Host utilizado no benchmark:

| Item   | Valor                    |
| ------ | ------------------------ |
| CPU    | AMD EPYC 7763 @ 3.24 GHz |
| vCPUs  | 2 compartilhadas         |
| RAM    | 7.9 GiB                  |
| SO     | Ubuntu 24.04.4 LTS       |
| Kernel | 6.8.0-1064-azure         |

Toolchain:

| Linguagem | Configuração      |
| --------- | ----------------- |
| C         | clang 18.1.3      |
| Rust      | 1.98.1, `-O3`     |
| Go        | 1.27.0            |
| Node.js   | 24.20.0           |
| Python    | 3.14.2            |
| Lumina    | HEAD, `--release` |

## Resultados

| Teste                      |   C -O3 | Rust -O3 | **Lumina --release** |      Go | **Lumina / C** |
| -------------------------- | ------: | -------: | -------------------: | ------: | -------------: |
| Fibonacci (N=35)           | 32.9 ms |  32.1 ms |          **31.9 ms** | 62.2 ms |      **0.97×** |
| Crivo de Eratóstenes (10M) | 21.8 ms |  21.7 ms |              24.3 ms | 35.9 ms |          1.11× |
| Loop matemático (100M)     | 88.1 ms |  96.8 ms |          **88.9 ms** | 82.6 ms |      **1.01×** |
| Matriz 200×200             |  5.5 ms |   8.0 ms |           **5.4 ms** | 14.3 ms |      **0.97×** |
| Alloc churn (1M)           | 13.3 ms |        — |              50.0 ms |       — |          3.77× |

## GC vs `--no-gc`

| Benchmark   |      GC |   `--no-gc` |
| ----------- | ------: | ----------: |
| primes      | 27.8 ms | **23.5 ms** |
| alloc_churn | 50.0 ms | **12.2 ms** |

O benchmark de `alloc_churn` demonstra diretamente o custo do GC em workloads com muitas pequenas alocações.

Por outro lado, `--no-gc` permite aproximar o comportamento de um runtime baseado em `malloc`/`free`.

### Observações

* Os números foram coletados em uma VM compartilhada.
* A mediana é utilizada para reduzir o impacto de outliers.
* C é compilado com **clang**, não gcc, para manter o backend de comparação alinhado com LLVM.
* `--no-gc` é especialmente relevante para workloads com alta frequência de alocações.
* Os benchmarks devem ser interpretados junto com a metodologia completa.

Metodologia, código e resultados históricos:

[`docs/engineering/benchmarks.md`](docs/engineering/benchmarks.md)

---

# 🛠️ CLI

## Projetos

```bash
lumina new meu_projeto
lumina install
lumina bind header.h nome
```

## Compilar e executar

```bash
lumina run arquivo.lm
lumina build arquivo.lm
lumina check arquivo.lm
lumina jit arquivo.lm
```

## Modos de build

```bash
lumina build app.lm --release
lumina build app.lm --debug
lumina build app.lm --wasm
lumina build app.lm --no-gc
lumina build app.lm --linker=self
```

## Targets

```bash
lumina build app.lm --target=aarch64-linux-gnu
lumina build app.lm --target=arm-linux-gnueabihf
lumina build app.lm --target=riscv64-linux-gnu
lumina build app.lm --target=i386-linux-gnu
```

## Qualidade

```bash
lumina test arquivo.lm
lumina lint arquivo.lm
lumina fmt arquivo.lm
lumina doc
```

## Interativo

```bash
lumina repl
lumina playground
```

## Manutenção

```bash
lumina clean
```

### Exit codes

| Comando | Exit code             |
| ------- | --------------------- |
| `run`   | exit code do programa |
| `test`  | número de falhas      |
| `lint`  | número de warnings    |
| `build` | `0`/`1`               |
| `check` | `0`/`1`               |

Para ferramentas de CI:

```bash
--error-format=json
```

O progresso é enviado para `stderr`, permitindo que a saída estruturada seja consumida por outras ferramentas.

Mais detalhes em [`docs/ferramental.md`](docs/ferramental.md).

---

# 🌍 Cross-compilation

Lumina suporta diferentes targets através do backend LLVM e dos toolchains disponíveis no ambiente.

```bash
lumina build app.lm --target=aarch64-linux-gnu
lumina build app.lm --target=arm-linux-gnueabihf
lumina build app.lm --target=riscv64-linux-gnu
lumina build app.lm --target=i386-linux-gnu
```

## Toolchains

Em Ubuntu/Debian:

```bash
sudo apt install -y \
    gcc-aarch64-linux-gnu \
    gcc-arm-linux-gnueabihf \
    gcc-riscv64-linux-gnu \
    qemu-user
```

Dependendo do modo de runtime utilizado, `libgc` também precisa estar disponível para o target.

Para ambientes sem Boehm GC:

```bash
lumina build app.lm --no-gc
```

### Limitação do linker próprio

O `lumina-ld` atualmente suporta:

```text
x86_64 Linux
```

Para outros targets, utilize o linker LLVM/Clang:

```bash
lumina build app.lm --linker=clang
```

---

# 🕸️ WebAssembly

Lumina também pode gerar WebAssembly.

Exemplo:

```lumina
export fn fib(n: int) -> int:
    if n <= 1:
        return n

    return fib(n - 1) + fib(n - 2)
```

Compile:

```bash
lumina build math.lm --wasm
```

O modo WASM utiliza `--no-gc`.

Exemplo de consumo:

```javascript
WebAssembly.instantiateStreaming(fetch("math.wasm"))
    .then(obj => console.log(obj.instance.exports.fib(35)));
```

---

# 🧪 Testes

Lumina possui testes em múltiplas camadas:

```text
tests/
├── parser
├── semantic
├── codegen
├── runtime
├── compiler
└── integration
```

Execute a suíte principal:

```bash
pytest tests/ -q
```

Resultado atual:

```text
440 passed in 139.78s
```

Suite adicional:

```bash
python3 run_tests.py
```

Resultado:

```text
28/28 verifications OK
```

Exemplos end-to-end:

```bash
./scripts/check_examples.sh --run
```

Resultado:

```text
54 PASS / 17 SKIP / 0 FAIL
```

Triagem do linker:

```bash
./linker/triagem.sh examples
```

Resultado:

```text
PASS=53 FAIL-COMPILE=0 FAIL-LINK=0 FAIL-RUN=0 SKIP=18
```

---

# 🐛 Engenharia e regressões

O projeto mantém documentação específica para bugs e regressões:

[`docs/engineering/bugs.md`](docs/engineering/bugs.md)

Cada correção relevante deve, quando aplicável, possuir:

```text
sintoma
   ↓
causa
   ↓
correção
   ↓
teste de regressão
```

Entre as correções recentes estão problemas envolvendo:

* terminadores ausentes em determinados exemplos;
* stack growth causado por `alloca` dentro de loops;
* monomorphization de tipos genéricos;
* resolução de métodos em `impl`;
* nomes canônicos de tipos;
* traits default;
* closures;
* codegen de `ret void`;
* parâmetros via `argv`;
* proteção contra dead-code elimination em benchmarks.

---

# 📖 Documentação

| Documento                                                          | Conteúdo                           |
| ------------------------------------------------------------------ | ---------------------------------- |
| [`docs/README.md`](docs/README.md)                                 | Índice da documentação             |
| [`docs/guia-rapido.md`](docs/guia-rapido.md)                       | Instalação e primeiros passos      |
| [`docs/linguagem.md`](docs/linguagem.md)                           | Referência da linguagem            |
| [`docs/stdlib.md`](docs/stdlib.md)                                 | Standard Library                   |
| [`docs/ferramental.md`](docs/ferramental.md)                       | CLI, LSP, formatter, linter e REPL |
| [`docs/internals.md`](docs/internals.md)                           | Pipeline e internals               |
| [`docs/internals/linking.md`](docs/internals/linking.md)           | Linker próprio e runtime           |
| [`docs/contributing.md`](docs/contributing.md)                     | Desenvolvimento e contribuição     |
| [`docs/engineering/bugs.md`](docs/engineering/bugs.md)             | Bugs e regressões                  |
| [`docs/engineering/tests.md`](docs/engineering/tests.md)           | Organização dos testes             |
| [`docs/engineering/benchmarks.md`](docs/engineering/benchmarks.md) | Metodologia dos benchmarks         |

---

# 🤝 Contributing

Contribuições são bem-vindas.

Antes de abrir um PR:

```bash
pytest tests/ -q

python3 run_tests.py

./scripts/check_examples.sh --run

./linker/triagem.sh examples

lumina fmt --check <arquivos>

lumina lint <arquivos>
```

Se você modificou o linker:

```bash
cd linker
make clean
make
cd ..

./scripts/check_examples.sh --run --linker=self
```

Consulte [`docs/contributing.md`](docs/contributing.md) para:

* setup de desenvolvimento;
* estilo de código;
* estrutura do projeto;
* processo de contribuição;
* criação de novas features;
* testes;
* checklist de PR.

---

# 🏗️ Estrutura do projeto

```text
Lumina/
├── lumina/                 # Compilador
├── lumina_cli/             # CLI
├── lumina-vscode/          # LSP / extensão VS Code
├── std/                    # Standard Library
├── tests/                  # Testes
├── examples/               # Exemplos
├── docs/                   # Documentação
├── scripts/                # Scripts auxiliares
├── linker/                 # lumina-ld + runtime freestanding
├── benchmarks/             # Benchmarks
├── run_tests.py            # Suite standalone
├── CHANGELOG.md            # Histórico de versões
└── README.md               # Este documento
```

---

# 🗺️ Roadmap

## Concluído

* [x] Lexer/parser/AST com indentação significativa
* [x] Codegen LLVM
* [x] JIT
* [x] REPL persistente
* [x] Generics
* [x] Generics aninhados
* [x] Monomorphization
* [x] Traits
* [x] Métodos default
* [x] Pattern matching
* [x] Multi-pattern
* [x] Guards
* [x] Destructuring
* [x] Enums multi-payload
* [x] Enums genéricos
* [x] Type aliases
* [x] Tuplas
* [x] Closures com captura
* [x] Tipos de função
* [x] `impl Box<T>`
* [x] `impl Trait for Box<int>`
* [x] Boehm GC
* [x] Escape analysis
* [x] `--no-gc`
* [x] `nil`
* [x] `@safe`
* [x] `defer` com escopo de bloco
* [x] `@macro`
* [x] Macros multi-statement
* [x] `comptime`
* [x] `for x in arr`
* [x] `for i, x in arr`
* [x] Tail Call Optimization
* [x] Mutual recursion
* [x] Formatter
* [x] Linter
* [x] `lumina doc`
* [x] LSP
* [x] FFI bindings
* [x] Build incremental
* [x] Cross-compilation
* [x] WebAssembly
* [x] `black_box(x)`
* [x] `argv(i)`
* [x] `atoi`
* [x] Benchmarks comparáveis
* [x] Linker próprio
* [x] Runtime freestanding
* [x] ELF estático x86_64
* [x] Codegen de `ret void`
* [x] Hoisting de `alloca`

## Em aberto

* [ ] Safe-by-default global
* [ ] Macros com quasiquote
* [ ] Self-hosting / bootstrapping
* [ ] Package registry
* [ ] Code actions no LSP
* [ ] Inlay hints no LSP
* [ ] Escape analysis para arrays com tamanho dinâmico mas loop-bounded
* [ ] `std/alloc` com arenas como primitiva de primeira classe
* [ ] Aliasing hints (`restrict` / `noalias`)
* [ ] Suporte a pthreads no linker próprio
* [ ] Linker próprio para AArch64
* [ ] Linker próprio para RISC-V
* [ ] Suporte W^X no linker próprio

O roadmap é evolutivo; itens marcados como concluídos representam funcionalidades presentes no estado atual do projeto, enquanto itens em aberto não fazem parte do contrato de estabilidade atual.

Veja [`CHANGELOG.md`](CHANGELOG.md) para o histórico detalhado.

---

# 📜 Versionamento

Lumina segue [Semantic Versioning](https://semver.org/) como referência para versões públicas.

O histórico completo está em:

[`CHANGELOG.md`](CHANGELOG.md)

Para uma mudança relevante na linguagem, o changelog deve documentar:

* alteração de sintaxe;
* alteração semântica;
* impacto na compatibilidade;
* novos recursos;
* bugs corrigidos;
* testes relevantes.

---

# 📌 Estado atual

O estado atual do projeto pode ser resumido assim:

```text
Compiler             ████████████████████  Functional
LLVM backend         ████████████████████  Functional
Type system          ████████████████████  Functional
Generics             ████████████████████  Functional
Pattern matching     ████████████████████  Functional
Macros/comptime      ████████████████████  Functional
GC / memory          ████████████████████  Functional
CLI                  ████████████████████  Functional
LSP                  ████████████████████  Functional
Formatter/linter     ████████████████████  Functional
JIT/REPL             ████████████████████  Functional
Cross compilation    ████████████████████  Available
WebAssembly          ████████████████████  Available
Own linker            ████████████████████  x86_64 Linux
Self-hosting         ███░░░░░░░░░░░░░░░░░  Planned
Package registry     ███░░░░░░░░░░░░░░░░░  Planned
```

A suíte atual fornece uma base de regressão significativa:

```text
440 pytest tests
28/28 standalone verifications
54 example PASS
0 example FAIL
0 linker compile failures
0 linker link failures
0 linker runtime failures
```

Os `SKIP` existentes são explícitos e documentados, em vez de serem tratados como falhas silenciosas.

---

# 📦 Licença

Lumina é distribuída sob a licença **MIT**.

Veja [`LICENSE`](LICENSE).

---

# 🔗 Links

* **Repositório:** [https://github.com/adamgabriel701/Lumina](https://github.com/adamgabriel701/Lumina)
* **Documentação:** [`docs/`](docs/README.md)
* **Changelog:** [`CHANGELOG.md`](CHANGELOG.md)
* **Exemplos:** [`examples/`](examples/)
* **Benchmarks:** [`benchmarks/`](benchmarks/)
* **Issues:** [https://github.com/adamgabriel701/Lumina/issues](https://github.com/adamgabriel701/Lumina/issues)

---

<p align="center">

**Lumina — uma linguagem de sistemas construída do compilador ao linker.**

</p>