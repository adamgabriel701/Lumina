# 🌟 Documentação Lumina

Índice navegável da documentação oficial da linguagem **Lumina**.

---

## 🚀 Começando

| Documento | Para quem | Conteúdo |
|---|---|---|
| [**Guia Rápido**](guia-rapido.md) | Todos | Instalação, primeiro programa, CLI essencial |
| [**Linguagem**](linguagem.md) | Quem programa em Lumina | Sintaxe, tipos, generics, traits, pattern matching, closures, macros |
| [**Standard Library**](stdlib.md) | Quem usa `std/*` | Referência de cada módulo: `math`, `sort`, `io`, `result`, `map`... |
| [**Ferramental**](ferramental.md) | Quem usa CLI/LSP/formatter | `lumina build`, `run`, `lint`, `fmt`, `repl`, LSP, VS Code |
| [**Internals**](internals.md) | Quem mexe no compilador | Pipeline, AST, codegen LLVM, TCO, escape analysis, GC |
| [**Contribuindo**](contributing.md) | Quem manda PR | Setup de dev, testes, estilo, checklist de PR |

---

## 🗺️ Mapa mental do projeto

```
┌─────────────────────────────────────────────────────────────────┐
│  Usuário escreve .lm                                            │
└──────────────────────────────┬──────────────────────────────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │  1. Lexer      (INDENT/DEDENT, escapes)     │
        │  2. Parser     (@attrs, generics, macro!)   │
        │  3. Semantic   (escopo, unify_type, traits) │
        │  4. Codegen    (LLVM IR + GC + TCO + defer) │
        │  5. clang      (link com libc + libgc)      │
        └──────────────────────┬──────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Binário nativo     │
                    │   .wasm / JIT        │
                    └──────────────────────┘
```

Detalhes de cada estágio em [**Internals**](internals.md).

---

## 📌 Atalhos por tema

### Tipos e dados
- [Primitivos e inferência](linguagem.md#tipos-e-inferência)
- [Enums e pattern matching](linguagem.md#tipos-algébricos-adts)
- [Tuplas](linguagem.md#tuplas)
- [`nil` vs `none`](linguagem.md#nil-vs-none)

### Generics e traits
- [Generics com monomorphization](linguagem.md#generics)
- [Genéricos aninhados (`Box<T>`)](linguagem.md#genéricos-aninhados)
- [`impl Box<T>` vs `impl Trait for Box<int>`](linguagem.md#impls-e-traits)
- [Type aliases](linguagem.md#type-aliases)

### Funções
- [Closures com captura](linguagem.md#closures)
- [Tipos de função com assinatura](linguagem.md#tipos-de-função)
- [`@macro` e `nome!(args)`](linguagem.md#macros)

### Metaprogramação e attributes
- [`@derive(...)`](linguagem.md#derive)
- [`@safe`](linguagem.md#safe)
- [`@inline` / `@cold` / `@hot`](linguagem.md#llvm-attrs)

### Otimizações
- [Tail Call Optimization (self + mutual)](internals.md#tco)
- [Escape analysis](internals.md#escape-analysis)
- [Defers em TCO](internals.md#defers-e-tco)

### Memória
- [Boehm GC (`GC_malloc` + `GC_init`)](internals.md#gc)
- [`--no-gc` para bare-metal](ferramental.md#flags-de-build)

---

## 🔗 Links externos

- [README principal](../README.md) — visão geral, benchmarks, badges
- [CHANGELOG](../CHANGELOG.md) — histórico detalhado de mudanças
- [Repositório](https://github.com/adamgabriel701/Lumina)