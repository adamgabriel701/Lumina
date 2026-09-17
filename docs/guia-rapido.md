# 🚀 Guia Rápido

## Pré-requisitos

- **Python 3.11+** e `llvmlite`
- **LLVM** e **Clang** no `PATH`
- **Boehm GC** (`sudo apt install libgc-dev`)
- *(Opcional WASM)* **WASI SDK** em `/opt/wasi-sdk`
- *(Opcional Raylib)* **libraylib**
- *(Opcional Cross-compile)* toolchain do target

## Instalação

```bash
git clone https://github.com/adamgabriel701/Lumina.git
cd Lumina
pip install -e .
lumina --help
```

## Primeiro programa

`hello.lm`:

```lumina
fn main() -> int:
    print("Olá, Lumina!")
    return 0
```

```bash
lumina run hello.lm
```

## Estrutura de projeto

```bash
lumina new meu_projeto
cd meu_projeto
```

Gera:

```
meu_projeto/
├── lumina.toml    # package + [link]
└── main.lm        # entry point
```

## Comandos essenciais

| Comando | O que faz |
|---|---|
| `lumina run arquivo.lm` | Compila e executa (propaga exit code) |
| `lumina check arquivo.lm` | Lexer+parser+semantic (~100ms) |
| `lumina test arquivo.lm` | Suíte nativa (exit = nº falhas) |
| `lumina lint arquivo.lm` | Análise estática (unused, shadow, unreachable) |
| `lumina fmt arquivo.lm` | Formata (preserva comentários) |
| `lumina fmt arquivo.lm --check` | Verifica formatação (pre-commit) |
| `lumina build app.lm --release` | Compila com `-O3` + `opt -O2` |
| `lumina build app.lm --debug` | `-O0` + DWARF |
| `lumina build app.lm --wasm` | WebAssembly |
| `lumina build app.lm --no-gc` | Bare-metal (sem GC) |
| `lumina repl` | REPL persistente |
| `lumina playground` | Playground web (8080) |

## Exemplo completo

```lumina
struct Ponto:
    x: int
    y: int

fn soma(a: int, b: int) -> int:
    return a + b

fn main() -> int:
    let p = Ponto { x: 10, y: 20 }
    print("Ponto:", p.x, p.y)
    print("Soma:", soma(p.x, p.y))
    return 0
```

## REPL persistente

```bash
$ lumina repl
lumina> mut counter = 0

lumina> counter = counter + 1

lumina> fn add(a: int, b: int) -> int:
...     return a + b

lumina> print(counter, add(2, 3))
1 5
lumina> :history
lumina> exit
```

Comandos: `:history`, `:decls`, `:clear`, `:help`, `exit`.

## Próximos passos

- [Linguagem](linguagem.md) — sintaxe completa
- [Standard Library](stdlib.md) — módulos disponíveis
- [Ferramental](ferramental.md) — LSP, linter, formatter, testes
