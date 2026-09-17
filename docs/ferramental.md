# 🛠️ Ferramental

## CLI (`lumina`)

### Comandos

| Comando | Descrição |
|---|---|
| `lumina new <nome>` | Cria projeto com `lumina.toml` |
| `lumina build [arquivo] [flags]` | Compila para binário nativo |
| `lumina run [arquivo]` | Compila e executa (exit code propagado) |
| `lumina check [arquivo]` | Lexer + parser + semantic (~100ms) |
| `lumina test [arquivo]` | Suíte nativa (exit = nº falhas) |
| `lumina jit [arquivo]` | Executa via JIT |
| `lumina repl` | REPL persistente |
| `lumina clean` | Limpa cache e binários |
| `lumina doc [--format=...]` | Gera docs (html / md / json) |
| `lumina install` | Baixa dependências do `lumina.toml` |
| `lumina bind <header.h> <nome>` | Bindings FFI a partir de header C |
| `lumina fmt <arquivo> [--check]` | Formata / verifica formatação |
| `lumina playground [porta]` | Playground web (8080) |

### Flags de build

| Flag | Efeito |
|---|---|
| `--release` | `-O3` |
| `--debug` | `-O0` + DWARF + sem cache |
| `--wasm` | Compila para WebAssembly (WASI SDK) |
| `--no-gc` | Sem Boehm GC (bare-metal) |
| `--target=<triple>` | Cross-compile (aarch64, armv7, riscv64, i386) |

### Exit codes

- `lumina run` → exit do binário
- `lumina test` → nº de falhas (0 = tudo passou)
- `lumina build` → 0 sucesso, 1 falha
- `lumina check` → 0 sem erros, 1 com erros

### Saída JSON

```bash
lumina check app.lm --error-format=json | jq .
# { "type": "error", "message": "...", "line": 2, "col": 9, ... }
```

Progresso vai para `stderr`; JSON vai para `stdout` — pipe-safe.

---

## REPL

REPL persistente. `mut` e declarações sobrevivem entre células.

```bash
$ lumina repl
🌟 Lumina REPL 2.0 — estado persistente
Dica: use mut x = 0 no topo para estado que persiste. `let` é local à célula.
lumina> mut counter = 0

lumina> counter = counter + 1

lumina> fn add(a: int, b: int) -> int:
...     return a + b

lumina> print(counter, add(2, 3))
1 5
lumina> exit
```

### Comandos

| Comando | Descrição |
|---|---|
| `:history` | Mostra todas as entradas |
| `:decls` | Só as declarações top-level |
| `:clear` | Limpa todo o estado |
| `:help` | Ajuda |
| `exit` / `quit` | Sai |

### Comportamento

- Células que parseiam como top-level (`fn`/`struct`/`enum`/`trait`/`impl`/`import`/`extern`/`mut`) → declaradas no topo.
- Caso contrário → viram `fn __cell_N() -> int:` recompilado a cada entrada.

### Limitações

- `let x = 10` é local à célula. Use `mut x = 10` para persistir.
- Recompila tudo a cada célula — O(N²) em sessões longas. Use `:clear` periodicamente.
- `mut x = 0\nx = x + 1` na mesma célula vira local. Digite em células separadas.

---

## Formatter (`lumina fmt`)

Auto-formatter que **preserva comentários leading** e **`@attrs`**.

```bash
lumina fmt arquivo.lm           # Formata in-place
lumina fmt arquivo.lm --check   # Verifica (exit 1 se desformatado)
```

### Preserva

- Comentários leading (`#` acima de fn/struct)
- Comentários de bloco (`/* ... */`)
- `@derive`, `@safe`, `@macro`
- Multi-pattern (`case A | B:`)
- Wildcard (`case _:`)

### Não preserva (ainda)

- Comentários inline (`x = 1  # foo`)

### Pre-commit hook

```bash
lumina fmt arquivo.lm --check || exit 1
```

---

## LSP (extensão VS Code)

### Recursos

- **Syntax highlighting** (TextMate)
- **Autocomplete** (keywords, funções, variáveis, structs, enums)
- **Hover** com escopo qualificado (`main::i` vs `helper::i`)
- **Go to Definition** (F12 / Ctrl+Click)
- **Find References** (Shift+F12) — filtra por escopo em locais
- **Rename Symbol** (F2) — ciente de escopo
- **Document Symbols** (Ctrl+Shift+O) — outline com children por função
- **Semantic Tokens** — cores específicas por categoria
- **Diagnostics em tempo real**

### Instalação

```bash
cd lumina-vscode
npx vsce package
code --install-extension lumina-0.2.0.vsix --force
```

Recarregue: `Ctrl+Shift+P` → **Developer: Reload Window**.

Para cores semânticas em temas que não suportam por padrão:

```json
"editor.semanticHighlighting.enabled": true
```

### Sublime Text

1. Copie `syntaxes/lumina.tmLanguage.json` para `Packages/Lumina/`
2. Instale o pacote `LSP`
3. Configure o LSP para `lumina-vscode/lumina_lsp.py`

---

## Testes

### `lumina test`

Testes nativos com framework `std/test`:

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
lumina test exemplo.lm
# exit 0 se todos passaram, N = nº de falhas
```

### Pytest (compilador)

```bash
pytest tests/ -v                # 267 testes
pytest tests/test_tco.py -v     # só TCO
```

### Standalone

```bash
python3 run_tests.py            # 28 validações (~5s)
```

### Check de exemplos

```bash
./scripts/check_examples.sh           # só compila
./scripts/check_examples.sh --run     # compila + executa
# 📊 PASS: 54  ⏭️  SKIP: 17  ❌ FAIL: 0
```

---

## Package Manager (`lumina.toml`)

```toml
[package]
name = "meu_projeto"
version = "0.1.0"
entry = "main.lm"

[dependencies]
# meu_pacote = "github:usuario/repo"

[link]
libs = ["m", "raylib"]
extra_objects = ["helper.cpp"]
extra_flags = ["-DFOO=1", "-Iinclude"]
target = "wasm"
```

`lumina install` baixa dependências `github:*` para `lumina_modules/`.

---

## Playground

```bash
lumina playground [porta]
# http://localhost:8080
```

Servidor HTTP que compila Lumina via JIT e retorna output. Útil para testar sem instalar.

---

## Cross-Compile

```bash
lumina build app.lm --target=aarch64-linux-gnu
lumina build app.lm --target=arm-linux-gnueabihf
lumina build app.lm --target=riscv64-linux-gnu
lumina build app.lm --target=i386-linux-gnu
lumina build app.lm --target=wasm32-wasi --wasm
```

Requer toolchain do target. Em Ubuntu:

```bash
sudo apt install -y gcc-aarch64-linux-gnu gcc-arm-linux-gnueabihf \
                    gcc-riscv64-linux-gnu qemu-user
```

Verificar:

```bash
file app                # → ELF 64-bit LSB pie executable, ARM aarch64
qemu-aarch64 -L /usr/aarch64-linux-gnu ./app
```
