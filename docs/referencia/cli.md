---
tags: [lumina, docs-referencia]
---

# Referência da CLI — `lumina`

Implementação em `lumina_cli/commands/`.

## Comandos

| Comando | Descrição | Módulo |
|---|---|---|
| `lumina new <nome>` | Cria projeto novo | `commands/new.py` |
| `lumina build` | Compila `.lm` → executável | `commands/build.py` |
| `lumina run` | Compila e executa | `commands/build.py` |
| `lumina fmt` | Formata código | `commands/fmt.py` |
| `lumina test` | Roda suíte de testes | `commands/test_suite.py` |
| `lumina doc` | Gera documentação | `commands/doc.py` |
| `lumina repl` | REPL interativo | `commands/repl.py` |
| `lumina bind` | Gera bindings FFI | `commands/bind.py` |
| `lumina install` | Instala toolchain | `commands/install.py` |
| `lumina clean` | Limpa artefatos | `commands/clean.py` |

## `lumina.toml`

Exemplo mínimo:

```toml
[package]
name = "MeuBanco"
version = "0.1.0"

[build]
opt-level = 3
target = "native"
```

Exemplos reais no repo: `lumina.toml`, `examples/*/lumina.toml`.

## `LUMINA_*` (variáveis de ambiente)

> Preencher conforme `lumina_cli/` for evoluindo.