# 📚 Documentação Lumina

Índice navegável. Todos os arquivos estão em `docs/`.

---

## 🚀 Começando

- [**Guia Rápido**](guia-rapido.md) — instalação, primeiro programa, CLI.
- [**Linguagem**](linguagem.md) — referência completa da sintaxe e semântica.
- [**Standard Library**](stdlib.md) — módulos `std/*`.
- [**Ferramental**](ferramental.md) — REPL, LSP, linter, formatter, testes.

## 🔧 Para contribuidores

- [**Internals**](internals.md) — arquitetura do compilador.
- [**Contributing**](contributing.md) — como rodar, testar e estender.

---

## Links externos

- [README principal](../README.md)
- [CHANGELOG](../CHANGELOG.md)
- [Repositório](https://github.com/adamgabriel701/Lumina)

---

## O que é a Lumina?

Linguagem de sistemas com:

- Sintaxe indentada (Python/Nim-style)
- Backend LLVM
- Boehm GC
- Generics, traits, pattern matching, tuplas
- TCO (self e mutual recursion)
- `defer`, `nil`, `@safe`, `@macro`
- Escape analysis (stack allocation)
- `impl Box<T>:` para métodos em structs genéricas
- `for x in arr` sobre iteráveis
- REPL persistente, LSP completo, linter, formatter

Status: **Alpha / Active**. 325 testes passando, 0 skips.
