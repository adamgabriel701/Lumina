# ⚙️ Internals

Como o compilador Lumina funciona por dentro. Para quem quer contribuir ou entender decisões de design.

---

## Pipeline

```
┌────────────────────────────────────────────────────────────────────┐
│  source.lm                                                         │
└──────────────────────────┬─────────────────────────────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │  1. LEXER                           │
        │     - Tokeniza (INDENT/DEDENT)      │
        │     - Processa escapes em strings   │
        │     - Preserva comentários          │
        └──────────────────┬──────────────────┘
                           │ tokens
        ┌──────────────────▼──────────────────┐
        │  2. PARSER                          │
        │     - Produz AST                    │
        │     - Resolve imports               │
        │     - Lê @attrs                     │
        │     - Normaliza `impl Box<T>:`      │
        └──────────────────┬──────────────────┘
                           │ AST
        ┌──────────────────▼──────────────────┐
        │  3. SEMANTIC                        │
        │     - Expande @derive e aliases     │
        │     - Resolve trait defaults        │
        │     - Type checking + unify_type    │
        │     - Marca escapes e freed_vars    │
        └──────────────────┬──────────────────┘
                           │ AST anotado
        ┌──────────────────▼──────────────────┐
        │  4. CODEGEN (LLVM IR)               │
        │     - Registra structs/enums/fns    │
        │     - Monomorphização on-demand     │
        │     - TCO + SCC dispatchers         │
        │     - Escape analysis               │
        │     - Defer + macros + @safe        │
        └──────────────────┬──────────────────┘
                           │ .ll
        ┌──────────────────▼──────────────────┐
        │  5. LINK (clang)                    │
        │     - -lc -lm -lpthread -lgc        │
        │     - extra_objects do [link]       │
        └──────────────────┬──────────────────┘
                           │
                    Binário nativo
```

---

## Estrutura do compilador

```
lumina/
├── ast/                    # Nós da AST (dataclasses)
│   ├── expressions.py
│   ├── statements.py
│   └── visitor.py          # dispatch por tipo
├── lexer/
│   ├── lexer.py            # tokenizador
│   └── tokens.py           # TokenType + KEYWORDS
├── parser/
│   ├── base.py             # ParserBase (consume/expect/check)
│   ├── expressions.py      # precedência
│   ├── statements.py       # controle de fluxo
│   ├── declarations.py     # fn, struct, enum, impl, ...
│   ├── patterns.py         # match, case, multi-pattern
│   └── parser.py           # orquestrador
├── semantic/
│   ├── analyzer.py         # orquestrador (SemanticAnalyzer)
│   ├── expressions/
│   ├── statements/
│   ├── derives.py          # @derive
│   ├── trait_resolution.py # trait defaults
│   └── types.py            # is_assignable, unify_type, substitute_generic
├── codegen/
│   ├── codegen.py          # composition root (LLVMCodegen)
│   ├── expressions/        # literals, operators, calls, methods, ...
│   ├── statements/         # var_decl, control, flow, match, macro_stmt
│   ├── types.py            # get_llvm_type + monomorphização
│   ├── generics.py         # materialize_generic
│   ├── traits.py           # trait defaults + validate_macro
│   ├── tco.py              # SCCs + dispatcher
│   ├── function_body.py    # corpo de função
│   ├── setup.py            # libc + GC + globais mutáveis
│   ├── registration.py     # register_struct/enum/function
│   └── helpers.py          # create_global_string + fn wrappers
├── common/
│   ├── mangle.py           # mangle_type, mangle_method
│   └── colors.py           # ANSI colors
├── builtins.py             # BUILTIN_FUNCTIONS + BUILTIN_RET
└── errors.py               # LuminaError
```

---

## Lexer

### INDENT / DEDENT

```python
# PILHA de indentação (colunas)
# 0  → topo, sem INDENT/DEDENT
# 4  → INDENT
# 8  → INDENT
# 4  → DEDENT
# 0  → DEDENT
```

### Escape sequences

Processadas em **compile-time** (`_read_escape`):

```python
_ESCAPE_MAP = {
    'n': '\n', 't': '\t', 'r': '\r', '0': '\0',
    'a': '\x07', 'b': '\b', 'f': '\f', 'v': '\v',
    '\\': '\\', '"': '"', "'": "'",
}
```

Escapes desconhecidos preservam `\X` (backslash + letra).

### Comentários

Preservados como `TokenType.COMMENT` (para o formatter reemitir).

---

## Parser

### Precedência

```
expression
  ↓
logical (and/or)
  ↓
bitwise_or
  ↓
bitwise_xor
  ↓
bitwise_and
  ↓
comparison
  ↓
shift (<< >>)
  ↓
range (..)
  ↓
additive (+ -)
  ↓
term (* / %)
  ↓
factor (unário, chamada, index)
```

### `no_struct_literal`

Flag que evita ambiguidade entre `match x:` (statement) e `x { y: 1 }` (struct literal). É `True` enquanto parseia a condição de `match`.

### Normalização de `impl`

```python
# impl Box<T>:        → struct_name = "Box"   (mangle → Box_get)
# impl Getter for Box<int>: → struct_name = "Box<int>" (mangle → Box_int__get)
# impl Box<int>:      → struct_name = "Box<int>"
```

Regra: se **todos** os args do target são type params únicos maiúsculos, strippa o `<...>`.

---

## Semantic

### Passadas

```
1. _expand_derives       → @derive(Eq, Debug) vira ImplBlocks + Functions
2. _resolve_trait_defaults → copia métodos default para ImplBlocks
3. Coleta type_aliases   → {nome: (params, target)}
4. _expand_type_aliases  → reescreve todos os tipos no AST
5. Coleta macros         → {nome: Function} (para validar nome!(args))
6. Registra símbolos     → functions, structs, enum variants
7. Analisa top-level VarDecls
8. Analisa corpos de funções e métodos de impl
```

### `unify_type` / `substitute_generic`

```python
unify_type("Box<T>", "Box<int>", type_map)
# → True, type_map = {"T": "int"}

substitute_generic("Box<T>", {"T": "int"})
# → "Box<int>"

substitute_generic("T", {"T": "int"})
# → "int"
```

### `is_assignable`

Regras (em `types.py`):

- Mesmo tipo → OK
- Type param (`T`, `U`) → aceita qualquer coisa
- `int → float` (promoção)
- `int ↔ ptr` (cast implícito)
- `fn ↔ str ↔ ptr` (todos `i8*`)
- `nil` → `ptr`, `str`, `fn`, struct
- `Option ↔ Option<X>`
- `<T> → <T>` com mesmos args

---

## Codegen

### Estrutura LLVM

| Lumina | LLVM |
|---|---|
| `int` | `i64` |
| `float` | `f64` |
| `bool` | `i1` |
| `str` | `i8*` |
| `ptr` | `i64*` |
| `struct P` | `%P = type { ... }` (passada por ponteiro) |
| `enum E` | `%E = type { i32, i64, ... }` (tag + payloads) |
| `fn` | fat pointer `{i8*, i8*}` (fn_ptr + env_ptr) |

### Monomorphização

Cada instanciação gera uma cópia:

```
identidade<T>(x: T) -> T
├── identidade__int
├── identidade__float
└── identidade__str
```

Nome mangled: `identidade__int` (`__` separa base de args).

Structs/enums: `Box<int>` → `Box_int_`.

### TCO (Tail Call Optimization)

**Self-recursion:**

```lumina
fn sum(n: int, acc: int) -> int:
    if n == 0: return acc
    return sum(n - 1, acc + n)
```

Gera IR com `sum_body:` (loop) em vez de `call sum`:

```
entry: alloca + store args → branch body
body:  ; corpo do usuário
       ; se for tail call: store novos args + branch body
```

**Mutual recursion (SCC):**

```lumina
fn is_even(n): if n == 0: return 1; return is_odd(n - 1)
fn is_odd(n):  if n == 0: return 0; return is_even(n - 1)
```

→ dispatcher `__scc_0` com `switch` sobre `current_id`. Cada wrapper chama `__scc_0(id, args)`.

### Escape analysis

`alloc(N)` com `N` **constante** e sem `return`/`free` vira `alloca` no stack:

```lumina
fn main() -> int:
    let buf = alloc(10)     # → alloca [10 x i64], não GC_malloc
    buf[0] = 42
    print(buf[0])
    return 0
```

Critérios:
- `N` é `NumberExpr` literal
- `N > 0` e `N <= 4096`
- Variável não está em `escapes` nem `freed_vars`

### Defers e TCO

`defer` é emitido **antes** do branch de TCO. Cada iteração re-executa o corpo, re-empilhando seus defers.

```lumina
fn loop(n: int) -> int:
    defer print("cleanup")
    if n == 0: return 0
    return loop(n - 1)
```

Emite `print("cleanup")` a cada iteração.

### Macros

**Expressão** (`nome(args)`): expansão inline, corpo deve ser `return <expr>`.

**Statement** (`nome!(args)`): inlineia o corpo inteiro (`_substitute_in_stmt` percorre VarDecl, AssignStmt, IfStmt, etc.).

### Fat pointers (`fn`)

Todo valor `fn` é `{fn_ptr, env_ptr}` no heap:

```python
def _emit_lambda_closure(self, node):
    # 1. Env struct no heap com capturas
    # 2. Função __closure_N(i8* env, i64 a1, ..., i64 aN)
    # 3. Bloco {fn_ptr, env_ptr} no heap
    return closure_raw
```

Chamadas indiretas passam por `_call_closure` (desempacota).

Funções nomeadas usadas como valor são **wrapped** em runtime (`_wrap_fn_as_closure`). `&fn_name` devolve o fn ptr **cru** (FFI-compatível).

### `@safe`

Se a função tem `@safe`, `MemberExpr` e `IndexExpr` fazem null check:

```
if obj == nil: return 0
else:          return obj.campo
```

Implementado com basic blocks + `phi`.

### GC

- `use_gc=True` → `GC_malloc` + `call GC_init()` em `main`
- `use_gc=False` (`--no-gc`) → `malloc` da libc
- WASM força `--no-gc`

### Registro de tipos

`get_or_create_monomorphized_struct("Box<int>")`:
1. Cria `%Box_int_` via `context.get_identified_type`
2. Registra em `struct_types["Box<int>"]`, `struct_types["Box_int_"]`
3. Registra em `struct_fields` (ambos)
4. **Registra em `struct_defs` (ambos)** ← chave canônica e mangled
5. Retorna o tipo LLVM

O mesmo para enums (`get_or_create_monomorphized_enum`).

---

## Testes

### Estrutura

```
tests/
├── cli/                 # subprocess `lumina <cmd>`
├── features/            # compila e roda exemplos
├── fixtures/            # .lm prontos para teste
├── test_*.py            # unitários e integração
└── conftest.py          # fixtures (lex, parse, analyze, run_cli)
```

### Fixtures principais

```python
@pytest.fixture
def lex():        # lex(src) → List[Token]

@pytest.fixture
def parse():      # parse(src) → List[Stmt]

@pytest.fixture
def analyze():    # analyze(src) → List[Stmt] (com semantic rodado)

@pytest.fixture
def run_cli():    # run_cli("build", file) → CompletedProcess
```

### Categorias de teste

| Categoria | Arquivo | O que cobre |
|---|---|---|
| Lexer | `test_lexer.py` | tokens, escapes, indent |
| Parser | `test_parser.py` | precedência, AST, slices |
| Semantic | `test_semantic.py` | escopo, exaustividade, traits |
| Types | `test_types.py` | is_assignable, promoções |
| Codegen (IR) | `test_codegen_bugs.py`, `test_gc.py`, `test_tco.py` | IR gerado |
| Codegen (runtime) | `test_runtime_bugs.py`, `test_closures.py` | executa o binário |
| Features | `test_generic_*.py`, `test_fn_*.py`, `test_macro*.py` | features específicas |
| CLI | `cli/test_*.py` | subprocess |
| Smoke | `features/test_*.py` | compila examples/ |

### Rodando

```bash
pytest tests/ -v                       # tudo (428 testes)
pytest tests/ -k "generic"             # filtro por nome
pytest tests/test_generic_enums.py -v  # arquivo único
python3 run_tests.py                   # suite standalone (28 validações)
./scripts/check_examples.sh --run      # compila + roda examples/
```

---

## Debugging

### Inspecionar IR

```bash
lumina build app.lm           # gera app.ll (IR cru)
lumina build app.lm --release # -O3 + opt -O2 no IR
```

### Inspecionar cache

```bash
ls .lumina_cache/             # IR compilado por hash
lumina clean                  # limpa tudo
```

### Forçar recompilação

O cache é invalidado quando:
- O `.lm` muda
- Qualquer `.py` do compilador muda
- As flags de build mudam

Se quiser forçar, `lumina clean` antes.

### LSP debug

```bash
cd lumina-vscode
python3 lumina_lsp.py         # roda o servidor
# Ou: F5 no VS Code com extension dev host
```