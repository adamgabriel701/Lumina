#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo .)"

mkdir -p docs/internals docs/referencia

# =====================================================================
# docs/internals/arquitetura.md
# =====================================================================
cat > docs/internals/arquitetura.md << 'LUMINA_DOC_EOF'
---
tags: [lumina, docs-internals]
---

# Arquitetura

Como o compilador Lumina funciona por dentro. Visão de pássaro; cada
estágio tem um arquivo dedicado.

**Código:** `lumina/`

## Pipeline

```
source.lm
   │
   ├─► 1. LEXER          → tokens    (lexer/lexer.py, lexer/tokens.py)
   │
   ├─► 2. PARSER         → AST       (parser/*, ast/*)
   │
   ├─► 3. SEMANTIC       → AST anot. (semantic/analyzer.py + mixins)
   │
   ├─► 4. CODEGEN        → .ll       (codegen/codegen.py + mixins)
   │
   └─► 5. LINK (clang)   → binário
```

## Estágios

- [Lexer](lexer.md) — tokenização, INDENT/DEDENT, escapes
- [Parser](parser.md) — AST, precedência, `impl` normalization
- [Semântica](semantica.md) — type checking, traits, derives, escape
- [Codegen](codegen.md) — LLVM IR, monomorphização, TCO, closures
- [Runtime](runtime.md) — Boehm GC, `std/`, fat pointers

## Estrutura do compilador

```
lumina/
├── ast/                    Nós da AST (dataclasses)
│   ├── expressions.py
│   ├── statements.py
│   └── visitor.py          Dispatch por tipo (NodeVisitor)
├── lexer/
│   ├── lexer.py            Tokenizador
│   └── tokens.py           TokenType + KEYWORDS
├── parser/
│   ├── base.py             ParserBase (consume/expect/check)
│   ├── expressions.py      Precedência + literais + types
│   ├── patterns.py         case/pattern de match
│   ├── statements.py       let/if/while/for/defer/…
│   ├── declarations.py     fn/struct/enum/impl/trait
│   └── parser.py           Orquestrador (Parser)
├── semantic/
│   ├── analyzer.py         SemanticAnalyzer
│   ├── expressions/        Mixins por tipo de expr
│   ├── statements/         Mixins por tipo de stmt
│   ├── derives.py          @derive
│   ├── trait_resolution.py Defaults de trait
│   └── types.py            PRIMITIVES + parse_fn_type
├── codegen/
│   ├── codegen.py          LLVMCodegen (composition root)
│   ├── expressions/        Mixins por tipo de expr
│   ├── statements/         Mixins por tipo de stmt
│   ├── types.py            get_llvm_type + monomorphização
│   ├── generics.py         materialize_generic
│   ├── traits.py           Trait defaults + validate_macro
│   ├── tco.py              SCCs + dispatcher
│   ├── function_body.py    Corpo de função
│   ├── setup.py            libc + GC + globais mutáveis
│   ├── registration.py     struct/enum/function + LLVM attrs
│   └── helpers.py          create_global_string + fn wrappers
├── common/
│   ├── mangle.py           mangle_type, mangle_method
│   └── colors.py           Color + HAS_COLOR
└── errors.py               LuminaError (dataclass)
```

## Mapeamento de tipos LLVM

| Lumina | LLVM |
|---|---|
| `int` | `i64` |
| `float` | `f64` |
| `bool` | `i1` |
| `str` | `i8*` |
| `ptr` | `i64*` |
| `struct P` | `%P = type { ... }` (por ponteiro em params) |
| `enum E` | `%E = type { i32, i64, ... }` (tag + payload slots) |
| `fn` / `fn(T)->R` | fat pointer `{i8* fn, i8* env}` |

## Onde estão as decisões

- [ADR 0001 — Backend LLVM](../engineering/decisoes/0001-backend-llvm.md)
- Ver também: [contributing](../contributing.md) (fluxo de adicionar features).
LUMINA_DOC_EOF

# =====================================================================
# docs/internals/lexer.md
# =====================================================================
cat > docs/internals/lexer.md << 'LUMINA_DOC_EOF'
---
tags: [lumina, docs-internals]
---

# Lexer

Transforma fonte `.lm` em uma sequência de tokens.

**Código:** `lumina/lexer/`

## Componentes

| Arquivo | Responsabilidade |
|---|---|
| `lexer.py` | Classe `Lexer` — máquina de estados, `tokenize()` |
| `tokens.py` | `TokenType` (Enum), `Token`, `KEYWORDS` |

## API

```python
lexer = Lexer(source, filename="<string>")
tokens: list[Token] = lexer.tokenize()
```

`Token` tem `__slots__ = ('type', 'value', 'line', 'col', 'offset')`.

## Categorias de token

Definidas em `TokenType`:

- **Literais** — `NUMBER`, `FLOAT`, `STRING`, `TRUE`, `FALSE`, `NONE`, `NIL`
- **Identificadores** — `IDENT` (keywords resolvidas via `KEYWORDS`)
- **Keywords** — `LET CONST MUT FN RETURN IF ELIF ELSE WHILE FOR IN BREAK CONTINUE DEFER ERRDEFER MATCH CASE DEFAULT SWITCH STRUCT IMPL TRAIT ENUM IMPORT EXTERN ASSERT BENCH TEST COMPTIME EXPORT AS TYPE NOT`
- **Operadores aritméticos** — `PLUS MINUS STAR SLASH PERCENT`
- **Bitwise** — `AMP PIPE CARET TILDE SHL SHR`
- **Atribuição** — `ASSIGN PLUS_ASSIGN MINUS_ASSIGN STAR_ASSIGN SLASH_ASSIGN AMP_ASSIGN PIPE_ASSIGN CARET_ASSIGN`
- **Comparação/lógicos** — `EQ NEQ LT GT LTE GTE AND OR BANG`
- **Delimitadores** — `LPAREN RPAREN LBRACE RBRACE LBRACKET RBRACKET COMMA DOT DOT_DOT COLON COLON_ASSIGN DOUBLE_COLON SEMICOLON ARROW FAT_ARROW QUESTION AT DOLLAR`
- **Estruturais** — `COMMENT NEWLINE INDENT DEDENT EOF`

## Escapes em strings

`_ESCAPE_MAP` em `lexer.py`:

| Escape | Resultado |
|---|---|
| `\n` | newline |
| `\t` | tab |
| `\r` | carriage return |
| `\0` | NUL |
| `\a` | bell |
| `\b` | backspace |
| `\f` | form feed |
| `\v` | vertical tab |
| `\\` | backslash |
| `\"` | quote |
| `\'` | single quote |

Escapes desconhecidos preservam `\X` como dois caracteres literais.

O processamento acontece em **compile-time** (`_read_escape`), não em runtime — `"\n"` vira 1 byte no binário.

## Indentação (INDENT / DEDENT)

`_handle_indent()` mantém uma pilha de colunas. Ao fim de cada
`NEWLINE`:

- Coluna atual > topo → emite `INDENT`, empilha
- Coluna atual < topo → emite `DEDENT` (repetido até bater)
- Coluna igual → nada

Blocos são delimitados implicitamente. Não há `{` `}`.

## Comentários

Dois tipos:

- **Linha**: `# ...` → vira `TokenType.COMMENT`
- **Bloco**: `/* ... */` → `_collect_block_comment()` consome incluindo
  os delimitadores e emite um único `COMMENT`

Comentários são **preservados como tokens** para que o formatter
(`lumina fmt`) possa reemiti-los na posição correta.

## Strings interpoladas

`_string(interpolated=True)` é chamado quando o token começa com
`$"`. Gera os segmentos que o parser depois monta em
`InterpolatedStringExpr`.

## Erros

`Lexer.error(msg)` levanta `LuminaError` com `filename`, `line` e
`col` já preenchidos. Erros léxicos abortam o pipeline (não há
recuperação).

## Testes

- `tests/test_lexer.py` — 30 casos (tokens, escapes, indent/dedent,
  comentários, `_handle_indent` regression)
- `tests/test_fmt_comments.py` — verifica preservação de comentários

## Ver também

- [Parser](parser.md) — consome `list[Token]`
- [Arquitetura](arquitetura.md)
LUMINA_DOC_EOF

# =====================================================================
# docs/internals/parser.md
# =====================================================================
cat > docs/internals/parser.md << 'LUMINA_DOC_EOF'
---
tags: [lumina, docs-internals]
---

# Parser

Constrói a AST a partir dos tokens do lexer.

**Código:** `lumina/parser/`

## Hierarquia de classes

O parser é dividido em camadas por mixin, cada uma estendendo a
anterior:

```
ParserBase                  base.py           consume/expect/check, comentários
    ▲
ExpressionParser            expressions.py    precedência, literais, tipos
    ▲
PatternParser               patterns.py       case/pattern de match
    ▲
StatementParser             statements.py     let/if/while/for/defer/…
    ▲
DeclarationParser           declarations.py   fn/struct/enum/impl/trait
    ▲
Parser                      parser.py         entrypoint (.parse())
```

O orquestrador (`Parser`) despacha por token: vê `@`, lê attrs; vê
`export`, marca; vê `fn`/`struct`/`enum`/`impl`/`trait`/`type`,
delega ao método específico; senão trata como statement.

## Precedência

`parse_expression()` chama a cadeia descendente. Do mais baixo para
o mais alto:

```
logical (and/or)
  bitwise_or
    bitwise_xor
      bitwise_and
        comparison (== != < > <= >=)
          shift (<< >>)
            range (..)
              additive (+ -)
                term (* / %)
                  factor (unário, chamada, index)
                    postfix (., ?., ?, as, [])
```

Notas:

- **Comparações encadeadas** (`a < b < c`) são normalizadas em
  `(a < b) and (b < c)` (semântica Python-like).
- **Range** (`..`) fica **abaixo** de comparação — `0..n` é
  parseado como `BinaryExpr('..', 0, n)`.
- **`parse_postfix`** é chamado depois do factor para lidar com
  `.`, `?.`, `?` (propagate), `as` (cast) e `[i]` / `[a..b]`.

## `_parse_slice_or_index`

Chamado após consumir `[`. Decide entre:

- `arr[i]` → `IndexExpr`
- `arr[a..b]` → `SliceExpr(a, b)`
- `arr[a..]` → `SliceExpr(a, None)`
- `arr[..b]` → `SliceExpr(None, b)`
- `arr[..]` → `SliceExpr(None, None)`

Usa `parse_additive()` para os bounds (não `parse_expression`), para
não consumir o `..` como operador binário.

## `no_struct_literal`

Flag em `ParserBase` que evita ambiguidade entre `match x:` e
`x { y: 1 }` (struct literal). Fica `True` enquanto o parser lê a
condição de `match`; volta a `False` no corpo.

## Comentários

O parser **anexa** comentários ao nó mais próximo via
`leading_comments`:

- `_skip_comments()` / `_skip_newlines_and_comments()` consomem
  `COMMENT` e acumulam em `pending_comments`
- `_take_comments()` devolve e limpa a lista
- `parse_statement()` pega o snapshot antes de criar o nó

Isso preserva a posição original no formatter.

## Normalização de `impl`

Em `parse_impl`:

```
impl Box<T>:              → struct_name = "Box"     (base fallback)
impl Box<int>:            → struct_name = "Box<int>" (especialização)
impl Getter for Box<int>: → trait="Getter", struct="Box<int>"
```

Regra: se **todos** os args do target são type params únicos maiúsculos,
strippa o `<...>`.

Mangling canônico:

- `Box<int>` + método `greet` → `Box_int__greet`
- `Box<T>` (genérico base) + `greet` → `Box_greet`

## Atributos (`@attrs`)

`@nome` e `@nome(args)` são lidos no topo de `parse()` e anexados ao
próximo nó. Atributos reconhecidos:

- `@derive(Eq, Debug, …)`
- `@macro`
- `@safe`
- `@inline`, `@noinline`, `@cold`, `@hot`
- `export` (tratado como atributo)

## AST produzida

Definida em `lumina/ast/`:

| Onde | Nós |
|---|---|
| `ast/expressions.py` | `NumberExpr`, `StringExpr`, `BinaryExpr`, `CallExpr`, `MemberExpr`, `IndexExpr`, `SliceExpr`, `StructLiteralExpr`, `LambdaExpr`, `MatchExpr`, `CastExpr`, `AddressOfExpr`, `DerefExpr`, `PropagateExpr`, `ComptimeExpr`, `InterpolatedStringExpr`, `TupleExpr`, `ArrayExpr`, … |
| `ast/statements.py` | `Function`, `StructDecl`, `EnumDecl`, `TraitDecl`, `ImplBlock`, `VarDecl`, `AssignStmt`, `ReturnStmt`, `IfStmt`, `WhileStmt`, `ForStmt`, `MatchStmt`, `DeferStmt`, `AssertStmt`, `BenchStmt`, `MacroCallStmt`, `TypeAlias`, `ImportStmt`, `ExternDecl`, … |
| `ast/visitor.py` | `NodeVisitor.visit(node)` — dispatch por `type(node).__name__` |

## Erros

`expect(t_type, t_val)` levanta `LuminaError` com a linha e coluna do
token atual. Não há recovery — o primeiro erro aborta.

## Testes

- `tests/test_parser.py` — 36 casos
- `tests/test_fn_types.py`, `test_forin.py`, `test_tuples.py`,
  `test_type_alias.py`, `test_multi_pattern.py`

## Ver também

- [Lexer](lexer.md)
- [Semântica](semantica.md)
- [Arquitetura](arquitetura.md)
LUMINA_DOC_EOF

# =====================================================================
# docs/internals/semantica.md
# =====================================================================
cat > docs/internals/semantica.md << 'LUMINA_DOC_EOF'
---
tags: [lumina, docs-internals]
---

# Semântica

Type checking, resolução de traits, expansão de derives e análise de
escape sobre a AST.

**Código:** `lumina/semantic/`

## Componentes

| Arquivo | Responsabilidade |
|---|---|
| `analyzer.py` | `SemanticAnalyzer` — orquestrador, escopos, `analyze()` |
| `types.py` | `PRIMITIVES`, `parse_fn_type`, `substitute_generic`, `is_assignable`, `unify_type` |
| `derives.py` | `DerivesMixin._expand_derives()` — sintetiza `__eq__`, `__ne__`, `__debug__`, `clone`, `new_X` |
| `trait_resolution.py` | `TraitResolutionMixin._resolve_trait_defaults()` |
| `expressions/` | Mixins por tipo de expressão |
| `statements/` | Mixins por tipo de statement |

## Passadas

`SemanticAnalyzer.analyze(declarations)` executa em ordem:

1. **Coleta type aliases** → `{nome: (params, target)}`
2. **Coleta macros** → `{nome: Function}` (necessário para validar `nome!(args)`)
3. **Expande `@derive`** → `DerivesMixin._expand_derives()` gera `ImplBlock`s e `Function`s sintetizadas
4. **Resolve trait defaults** → `TraitResolutionMixin._resolve_trait_defaults()` copia métodos default para cada `ImplBlock` que não os definiu
5. **Expande type aliases** → `_expand_type_aliases()` reescreve **todos** os tipos no AST (params, returns, campos, variantes, VarDecls locais)
6. **Registra símbolos** → popula `functions`, `struct_defs`, `enum_defs`, `impls`
7. **Analisa VarDecls top-level** (globais)
8. **Analisa corpos** de funções e métodos de impl

## Escopo

```python
analyzer.push_scope()                 # início de bloco
analyzer.declare_var(name, tipo, mut)
analyzer.get_var_info(name)           # {'type': ..., 'mutable': ...}
analyzer.pop_scope()
```

`self.scopes` é uma pilha de dicts. `scopes[0]` é o global, que
persiste durante `analyze_function`.

## Sistema de tipos

`PRIMITIVES = {"int", "float", "bool", "str", "ptr", "fn", "void"}`.

`parse_fn_type("fn(int, str) -> bool")` devolve
`(params, return_type)` — usado em `CallExpr` e `VarDecl` para
checar chamadas indiretas.

### `is_assignable(target, source)`

Regras principais:

- Mesmo tipo → OK
- Type param (`T`, `U`) → aceita qualquer coisa
- `int` → `float` (promoção)
- `int ↔ ptr` (cast implícito)
- `fn ↔ str ↔ ptr` (todos `i8*` no codegen)
- `nil` → `ptr`, `str`, `fn`, struct
- `Option ↔ Option<X>` (união de args)
- Struct genérica: `<T> → <T>` com mesmos args

### `unify_type` / `substitute_generic`

```python
unify_type("Box<T>", "Box<int>", {})       # True, {"T": "int"}
substitute_generic("Box<T>", {"T": "int"}) # "Box<int>"
substitute_generic("T", {"T": "int"})      # "int"
```

Usados em generics para inferir `type_map` no call site
(`semantic/expressions/calls.py`).

## Type checking por nó

Cada tipo de expressão/statement tem um `visit_*`. Exemplos:

- `visit_BinaryExpr` — infere tipo, tenta operador de struct
  (`__add__`, etc.), faz concat de strings
- `visit_StructLiteralExpr` — valida que todos os campos obrigatórios
  foram passados e que os tipos batem
- `visit_MatchStmt` — exaustividade (todos os variants cobertos ou
  wildcard)
- `visit_CallExpr` — resolve `fn_def`, named args, defaults,
  indiretas via fat pointer, generics
- `visit_VarDecl` — infere `var_type` se ausente
  (`_infer_var_decl_type`)

## Derives

`DerivesMixin._expand_derives()` transforma:

```lumina
@derive(Eq, Debug)
struct Ponto:
    x: int
    y: int
```

em `ImplBlock`s + `Function`s sintetizadas:

- `Eq` → `Ponto___eq__`, `Ponto___ne__`
- `Debug` / `Display` → `Ponto___debug__` (retorna `str`)
- `Clone` → `Ponto_clone()`
- `Default` → `new_Ponto()` (função livre)

## Trait resolution

`_resolve_trait_defaults()`:

1. Coleta `traits_by_name` de todos os `TraitDecl`
2. Para cada `ImplBlock` com `trait_name`:
   - Compara métodos explícitos com os do trait
   - Para cada default não implementado, clona a `Function` com
     `mangle_method(struct_name, method.name)`

## Escape analysis

`check_escape(node)` marca:

- `escapes` — variáveis cujo valor pode escapar da função
- `freed_vars` — variáveis passadas para `free()`

Esses conjuntos são consultados pelo codegen em
`_try_stack_alloc` (`codegen/statements/var_decl.py`): se `alloc(N)`
tem `N` constante, N ≤ 4096, e a variável não está em `escapes` nem
`freed_vars`, gera `alloca` em vez de `GC_malloc`.

## Erros

Erros são `LuminaError` com mensagem, local e sugestão ("você quis
dizer X?" via `_collect_var_refs` + Levenshtein em
`expressions/helpers.py`).

## Testes

- `tests/test_semantic.py`, `test_semantic_bugs.py`
- `tests/test_types.py`, `test_struct_field_types.py`
- `tests/test_derive_*.py`, `test_enum_bare_variant.py`,
  `test_escape_analysis.py`

## Ver também

- [Parser](parser.md)
- [Codegen](codegen.md)
- [Arquitetura](arquitetura.md)
LUMINA_DOC_EOF

# =====================================================================
# docs/internals/codegen.md
# =====================================================================
cat > docs/internals/codegen.md << 'LUMINA_DOC_EOF'
---
tags: [lumina, docs-internals]
---

# Codegen (LLVM)

Emissão de LLVM IR via `llvmlite`, com monomorphização, TCO, escape
analysis e closures.

**Código:** `lumina/codegen/`

## Composition root

`LLVMCodegen` (`codegen.py`) herda de uma pilha de mixins:

```
LLVMCodegen(
    ExpressionCodegen,     expressions/__init__.py
    StatementCodegen,      statements/__init__.py
    SetupMixin,            setup.py
    RegistrationMixin,     registration.py
    TypesCodegen,          types.py
    GenericsMixin,         generics.py
    TraitsMixin,           traits.py
    TCOMixin,              tco.py
    FunctionBodyMixin,     function_body.py
    HelpersCodegen,        helpers.py
)
```

Cada mixin tem um conjunto de `visit_<Node>` que emite IR e retorna
o valor SSA.

Entrypoint:

```python
codegen = LLVMCodegen(target_triple=None, use_gc=True)
ir_str = codegen.generate_module(ast)
```

## Setup inicial (`setup.py`)

`setup_libc_functions()` declara no módulo LLVM:

| Função | Uso |
|---|---|
| `printf`, `snprintf` | formatação |
| `malloc`, `free` | alocação (fallback / `--no-gc`) |
| `GC_malloc`, `GC_init` | Boehm GC |
| `strcpy`, `strcat`, `strlen`, `strncpy` | strings |
| `strstr`, `strncmp`, `strcmp` | comparação/busca |
| `atoi` | parsing de inteiro |

`_emit_mutable_global(decl)` cria `GlobalVariable` para `VarDecl`
top-level mutável.

## Registro (`registration.py`)

`register_struct(node)` — cria `ir.IdentifiedStructType` com campos.

`register_enum(node)` — tipo `{ i32 tag, i64 payload0, i64 payload1, … }`
onde o número de slots é `_enum_max_payloads(node)` (maior nº de
payloads entre variantes).

`register_function(node)` — cria a `ir.Function` com assinatura
derivada de `params` e `return_type`. `main` ganha assinatura C
`i32 (i32, i8**)` + globais `__lumina_argc` / `__lumina_argv`.

`_apply_llvm_attrs(func, attrs)` — mapeia `@inline` → `alwaysinline`,
`@noinline` → `noinline`, `@cold` → `cold`, `@hot` → `inlinehint`
(LLVM `hot` é string attribute; `inlinehint` tem mesma intenção).

## Tipos e monomorphização (`types.py`)

`get_llvm_type(name)` — mapeia o tipo Lumina para LLVM.

Structs **por ponteiro** em parâmetros (`get_llvm_param_type`
devolve `ptr`). `get_llvm_type` força monomorphização **antes** de
checar `struct_types`, evitando inconsistência entre 1ª e 2ª
chamadas.

`get_or_create_monomorphized_struct("Box<int>")`:

1. Cria `%Box_int_` via `context.get_identified_type`
2. Registra em `struct_types` sob a chave canônica **e** a mangled
3. Registra em `struct_fields` (ambos)
4. Registra em `struct_defs` (ambos)
5. Retorna o tipo LLVM

O mesmo para enums (`get_or_create_monomorphized_enum`).

Mangling: `Box<int>` → `Box_int_`; `Map<str, int>` → `Map_str_int_`.

## Generics (`generics.py`)

`materialize_generic(gen_def, type_map)`:

1. Calcula o nome mangled a partir dos type args
2. Cria a `ir.Function` (se ainda não existe)
3. Salva/restaura `builder`, `symbol_table`, `var_types`,
   `current_func_name`, `defer_stack`, `closure_vars`, `_safe_mode`
4. Emite o corpo com o `type_map` aplicado
5. Marca como materializado para não repetir

`_infer_arg_type_lumina(arg_node)` — infere tipo Lumina de um arg
para popular o `type_map` (usado quando a inferência semântica não
resolveu tudo).

## TCO (`tco.py`)

**Self-recursion** (`_try_tail_call` em `statements/flow.py`):
`return f(...)` dentro da própria `f` → store dos novos args nos
slots + `br body_bb` (em vez de `call`).

**Mutual recursion** (`_compute_tail_call_sccs` + `_materialize_scc_dispatcher`):

1. Constrói grafo de tail calls entre funções
2. Tarjan para achar SCCs
3. Para cada SCC com ≥ 2 membros, cria dispatcher `__scc_N`:
   - Params: `(i32 id, <params comuns>)`
   - `switch` sobre `id` para o bloco de cada membro
   - Cada membro é envolvido por um wrapper que chama
     `__scc_N(id, args)`
4. Dentro de cada membro do SCC, `return g(...)` vira
   `store args nos slots + store id + br dispatch_bb`

Defers são emitidos **antes** do branch de TCO
(`_emit_all_defers()`).

## Escape analysis

Ver [Semântica](semantica.md#escape-analysis) para a análise.
Aqui, `_try_stack_alloc(node)` em `statements/var_decl.py`
transforma `alloc(N)` (N literal, N ≤ 4096, sem escape/free) em:

```python
arr_ty = ir.ArrayType(elem_ty, n)
arr_ptr = self.builder.alloca(arr_ty, name=node.name + "_stack")
```

`alloc_bytes(N)` usa `i8` como elemento; `alloc(N)` usa `i64`.

## Closures / fat pointers

Todo valor `fn` é `{fn_ptr: i8*, env_ptr: i8*}` no heap:

- `_emit_lambda_closure(node)` em `expressions/aggregates.py`
  1. Aloca env struct com capturas por valor
  2. Emite `__closure_N(i8* env, i64 a1, …, i64 aN) -> i64`
  3. Aloca bloco `{fn_ptr, env_ptr}`
- `_wrap_fn_as_closure(raw_func)` em `helpers.py` — envolve funções
  nomeadas usadas como valor (`env_ptr = NULL`)
- `_call_closure(name, node)` em `expressions/calls.py` desempacota
  e chama
- `&fn_name` (AddressOfExpr) devolve o **fn ptr cru** (FFI-compatível)

## @safe

`_safe_mode` é ligado por `@safe`. Em `visit_MemberExpr` e
`visit_IndexExpr` (em `expressions/members.py`), insere:

```
is_null = icmp eq obj, null
br is_null, null_bb, ok_bb
null_bb: valor = zero; br end_bb
ok_bb:   valor = load/gep; br end_bb
end_bb:  phi [valor, zero]
```

Sem `@safe`, o acesso é direto (C-style) — SIGSEGV se `obj == nil`.
`?.` (safe nav) faz o mesmo check independente de `@safe`.

## GC

`use_gc=True` (padrão): chamadas a `alloc` vão para `GC_malloc`,
`main` começa com `call GC_init()`.

`use_gc=False` (`--no-gc`, `--wasm`): `malloc`/`free` da libc.

## Macros

`@macro` tem duas expansões:

- **Expressão** (`nome(args)`) — `_expand_macro_expr` substitui os
  params pelo arg e inlineia o `return <expr>` no call site
- **Statement** (`nome!(args)`) — `_expand_macro_stmt` inlineia o
  corpo inteiro (`_substitute_in_stmt` percorre VarDecl, AssignStmt,
  IfStmt, WhileStmt, ForStmt, DeferStmt, AssertStmt)

`_validate_macro(fn)` garante que o corpo é válido (no caso de
expressão, exige `return <expr>`; no caso de statement, aceita
múltiplos statements).

## Testes

- `tests/test_codegen_bugs.py`, `test_llvm_attrs.py`
- `tests/test_tco.py`, `test_tco_mutual.py`
- `tests/test_escape_analysis.py`, `test_gc.py`
- `tests/test_closures.py`, `test_macro*.py`
- `tests/test_generic_*.py`, `test_impl_box_generic.py`

## Ver também

- [Semântica](semantica.md)
- [Runtime](runtime.md)
- [ADR 0001 — LLVM](../engineering/decisoes/0001-backend-llvm.md)
LUMINA_DOC_EOF

# =====================================================================
# docs/internals/runtime.md
# =====================================================================
cat > docs/internals/runtime.md << 'LUMINA_DOC_EOF'
---
tags: [lumina, docs-internals]
---

# Runtime

Não há uma runtime monolítica. O suporte em tempo de execução vem de
três fontes:

1. **libc** — `malloc`, `free`, `printf`, `strcmp`, etc.
2. **Boehm GC** — `libgc` (`GC_malloc`, `GC_init`), linkado com `-lgc`
3. **`std/*.lm`** — biblioteca padrão escrita em Lumina

**Código:** `std/` (Lumina) + `lumina_cli/commands/linking.py` +
`lumina/codegen/setup.py`

## GC

Padrão: **Boehm-Demers-Weiser** conservador. Inicializado uma vez em
`main` com `call GC_init()` (emitido por `codegen/setup.py`).
`alloc(N)` chama `GC_malloc(N * 8)`.

`--no-gc`: usa `malloc`/`free` da libc diretamente. `main` não chama
`GC_init`.

`--wasm`: força `--no-gc` (libgc não está disponível no WASI).

O flag é propagado em `lumina_cli/commands/build.py`:

```python
is_no_gc = ("--no-gc" in extra_flags) or is_wasm
codegen = LLVMCodegen(target_triple=target_triple, use_gc=not is_no_gc)
```

E na linkagem: `-lgc` só é passado se `use_gc`.

## Escape analysis em runtime

`alloc(N)` com N constante e sem escape/free vira `alloca` no stack
— nenhuma chamada de alocação. Ver
[Semântica](semantica.md#escape-analysis) e
[Codegen](codegen.md#escape-analysis).

Isso é o que faz `primes` (10M) rodar sem `GC_malloc` quando o
algoritmo permite.

## Closures em runtime

Valores `fn` são **fat pointers** `{fn_ptr, env_ptr}` no heap:

- Capturas ficam no env, copiadas por valor
- `env_ptr = NULL` para funções nomeadas usadas como valor
- `&fn_name` devolve o fn ptr cru (compatível com FFI C)

`_call_closure` desempacota antes de chamar. Ver
[Codegen](codegen.md#closures--fat-pointers).

## Defers

`defer` usa uma pilha por função (`defer_stack`). Escopo:

- Bloco (`_begin_scope` / `_end_scope` em `statements/flow.py`)
- Função (emitido no `ret`, inclusive em TCO via `_emit_all_defers`)

## `std/` — biblioteca padrão

Todos os módulos são escritos em Lumina (bootstrapped), exceto
bindings FFI:

| Categoria | Módulos |
|---|---|
| **Fundamentos** | `prelude` (auto-importado), `math`, `str`, `string` (StringBuilder), `result` |
| **Coleções** | `vector`, `map`, `set`, `deque`, `list`, `sort`, `iter` |
| **Testes / log** | `test`, `log` |
| **I/O e SO** | `io`, `fs`, `os`, `path`, `time`, `alloc` |
| **Concorrência** | `channel`, `async`, `async_fs`, `epoll`, `net`, `http` |
| **Integração** | `json`, `sqlite`, `raylib` |

`std/prelude.lm` é auto-importado por `parse_module`
(`lumina_cli/compiler/parse.py`) antes de resolver os `import` do
usuário.

### `std/alloc` (arena)

Primitiva para churn controlado: `init(cap)`, `alloc(arena, n)`,
`reset(arena)`, `destroy(arena)`. Evita `GC_malloc` em loops com
muitas alocações pequenas.

## `main` — assinatura C

`register_function` (em `codegen/registration.py`) reescreve `main`
para a assinatura C:

```
i32 main(i32 argc, i8** argv)
```

Emite globais `__lumina_argc` e `__lumina_argv` para que o código
Lumina acesse via `argv(i)` builtin. Isso é o que destrava
benchmarks parametrizados por linha de comando.

## FFI

`extern fn` gera declaração LLVM sem corpo — resolvido na linkagem
(clang, `-l` ou `extra_objects`). Tipos são mapeados diretamente:

| C | Lumina |
|---|---|
| `int`, `long`, `size_t` | `int` (i64) |
| `float`, `double` | `float` (f64) |
| `char*`, `const char*` | `str` (i8*) |
| `void*` | `str` (i8*) — ponteiro bruto |
| `char` | `int` |

## Testes

- `tests/test_gc.py`, `test_runtime_bugs.py`
- `tests/test_std_*.py` (io, math, os, path, result)
- `benchmarks/alloc_churn.lm`, `bench_runtime.lm`

## Ver também

- [Codegen](codegen.md)
- [Stdlib](../guia/stdlib.md)
- [Ferramental](../guia/ferramental.md)
- [Benchmarks](../engineering/benchmarks.md) (impacto do GC)
LUMINA_DOC_EOF

# =====================================================================
# docs/referencia/cli.md
# =====================================================================
cat > docs/referencia/cli.md << 'LUMINA_DOC_EOF'
---
tags: [lumina, docs-referencia]
---

# Referência da CLI — `lumina`

Implementação em `lumina_cli/`. Entrypoint em `lumina_cli/main.py`
(`main()` retorna exit code inteiro 0..255).

## Sinopse

```
lumina <comando> [opções] [argumentos]
```

## Comandos

| Comando | Descrição | Módulo |
|---|---|---|
| `new <nome>` | Cria projeto (`lumina.toml` + `main.lm`) | `commands/new.py` |
| `build [arq] [flags]` | Compila `.lm` → binário | `commands/build.py` |
| `run [arq] [flags]` | Compila e executa (propaga exit) | `commands/build.py` |
| `check [arq]` | lexer + parser + semantic (sem IR) | `commands/build.py` |
| `jit [arq]` | Executa via JIT (MCJIT, sem clang) | `compiler/pipeline.py` |
| `test [arq]` | Roda funções `test_*` | `commands/test_suite.py` |
| `fmt <arq>` | Formata (in-place ou `--check`) | `commands/fmt.py` |
| `fmt --stdin` | Lê de stdin, escreve em stdout | `commands/fmt.py` |
| `fmt --check-all <dir>` | Verifica todos os `.lm` do dir | `commands/fmt.py` |
| `lint <arq>` | Análise estática (W001..W005) | `lint.py` |
| `doc [--format=X]` | Gera docs (`html`/`md`/`json`) | `commands/doc.py` |
| `repl` | REPL persistente (JIT) | `commands/repl.py` |
| `playground [porta]` | Servidor HTTP com playground JIT | `playground.py` |
| `bind <header.h> <nome>` | Gera bindings FFI | `commands/bind.py` |
| `install` | Baixa deps do `lumina.toml` | `commands/install.py` |
| `clean` | Remove artefatos de build | `commands/clean.py` |
| `--help` / `-h` / `help` | Uso | `main.py` |

## Flags globais

| Flag | Efeito |
|---|---|
| `--error-format=text\|json` | Formato dos erros (JSON é pipe-safe) |
| `--help`, `-h` | Uso + exit 0 |

## `lumina build` / `run`

`cmd_build(entry_file=None, extra_flags=[])` resolve o entrypoint
nesta ordem:

1. `entry_file` passado na linha de comando
2. `[package] entry` do `lumina.toml` (se existir)
3. `main.lm`

Flags (filtradas de `extra_flags` antes de ir pro linker):

| Flag | Efeito |
|---|---|
| `--release` | `-O3` no clang + `opt -O2` no IR |
| `--debug` | `-O0` + `-g` (DWARF) |
| `--wasm` | Compila para WebAssembly (força `--no-gc`) |
| `--no-gc` | Sem Boehm GC (usa `malloc`/`free`) |
| `--target=<triple>` | Cross-compile (`aarch64-linux-gnu`, etc.) |

Comportamento:

- `cmd_check` só roda `check_lumina` (sem gerar IR nem linkar).
- `cmd_run` chama `cmd_build` e executa o binário, **propagando o
  exit code**.
- `jit` invoca `run_jit(llvm_ir, cli_args)` — MCJIT, sem clang.
  O `main` recebe `argv`/`argc` injetados.

### Saída

- `lumina build foo.lm` → binário `./foo` (nome derivado do `.lm`)
- `lumina build` (sem arg, com `lumina.toml`) → usa `entry` e
  `package.name` como nome do binário
- WASM → `<project_name>.wasm` com `export fn` marcadas
- IR intermediário → `<project_name>.ll` no diretório atual

### Cache

`lumina build` usa cache incremental em `.lumina_cache/`:

- Chave = hash MD5 de: conteúdo dos `.lm` + fontes Python do
  compilador + flags de build (`get_cache_hash` em `utils.py`)
- Cache hit requer **três** condições:
  1. Arquivo de hash existe
  2. Hash bate (IR + `opt_flag` marker)
  3. **Binário de saída existe em disco**

Sem (3), refaz a linkagem (bug histórico: `mv` do binário depois
do build quebrava o cache).

`--wasm` e `--debug` **desabilitam** o cache.

## `lumina test`

`cmd_test(entry_file=None)`:

1. Resolve entry (mesma ordem do build)
2. `parse_module(entry)` → AST
3. Coleta funções com nome começando em `test_`
4. Gera um `main` sintético que chama cada uma e soma falhas
5. Compila com `-fprofile-instr-generate -fcoverage-mapping`
6. Executa; exit code = nº de falhas

## `lumina fmt`

Preserva:

- Comentários de linha (`#`) e bloco (`/* */`)
- `@attrs` (`@derive`, `@safe`, `@inline`, …) via `_format_attrs`
- Multi-pattern (`case A | B:`)
- Wildcard (`case _:`)

Idempotente: `fmt(fmt(x)) == fmt(x)`.

Modos:

```
lumina fmt <arquivo>              # formata in-place
lumina fmt <arquivo> --check      # só verifica (exit 1 se precisa)
lumina fmt --stdin                # stdin → stdout
lumina fmt --stdin --check        # verifica stdin
lumina fmt --check-all <dir>      # todos os .lm recursivamente
```

## `lumina lint`

`lint_file(filename, format="text", quiet=False)`. Exit code = nº de
warnings.

| Código | Descrição |
|---|---|
| **W001** | Variável declarada mas nunca usada |
| **W002** | Variável sombreia outra do mesmo escopo |
| **W003** | Código inalcançável após `return`/`break`/`continue` |
| **W004** | Parâmetro nunca usado |
| **W005** | Função com corpo vazio |

Suprime com prefixo `_`:

```lumina
fn f(_unused: int):
    let _tmp = 10
```

Flags:

```
lumina lint <arq>                 # texto colorido
lumina lint <arq> --format=json   # JSON (pipe-safe)
lumina lint <arq> --quiet         # só exit code
```

## `lumina doc`

`cmd_doc(output_format="html", output_path=None)`.

Formatos:

- `html` → `docs/index.html`
- `md` → `docs/index.md`
- `json` → `docs/index.json`

Coleta comentários `##` acima de declarações (`_collect_docs`) e
classifica por tipo (`Function`, `Struct`, `Enum`, `Trait`).

```
lumina doc
lumina doc --format=md
lumina doc --format=json
lumina doc --format=html --output=out/api.html
```

## `lumina repl`

`cmd_repl()` — JIT persistente via MCJIT.

- `mut x = 0` persiste entre células (vira global)
- `let x = 10` é local à célula
- `fn`, `struct`, `enum`, `trait`, `impl` persistem
- Cada célula é compilada como `__cell_N` e chamada
- Recompila **tudo** a cada célula (O(N²) em sessões longas)

Comandos:

| Comando | Efeito |
|---|---|
| `:help` | Lista comandos |
| `:history` | Tudo que foi digitado |
| `:decls` | Só declarações top-level |
| `:clear` | Limpa estado |
| `exit` / `quit` | Sai |

Detecta GC via `ctypes.util.find_library('gc')`; se não achar,
usa `malloc`.

## `lumina playground`

`run_server(port=8080)` — servidor HTTP em `http.server`. Procura
`playground.html` no diretório atual, raiz do projeto ou diretório
do pacote.

POST `/` com `{"code": "..."}` → compila + executa JIT e devolve
`{"success": bool, "output": str}`. Captura `stdout` via `os.dup`
do fd 1.

## `lumina bind`

`cmd_bind(header_file, output_name)` — regex em C header para
extrair assinaturas de função:

```python
pattern = r'(\w[\w\s\*]*?)\s+(\w+)\s*\(([^)]*)\)\s*;'
```

Mapeamento C → Lumina (`c_type_map`):

| C | Lumina |
|---|---|
| `int`, `long`, `size_t`, `int64_t` | `int` |
| `float`, `double` | `float` |
| `char*`, `const char*` | `str` |
| `void*` | `str` (ponteiro bruto) |
| `char` | `int` |

Gera `std/<output_name>.lm` com `extern fn` para cada função.

```
lumina bind sqlite3.h sqlite3
# → std/sqlite3.lm
```

## `lumina install`

`cmd_install()` lê `[dependencies]` de `lumina.toml`:

```toml
[dependencies]
meu_pacote = "github:usuario/repo"
```

Clona para `lumina_modules/<nome>/`:

```
https://github.com/usuario/repo.git
```

## `lumina clean`

`cmd_clean()` remove:

- `.lumina_cache/`
- Binários conhecidos: `programa_final`, `lumina_test_bin`,
  `output`, `lumina_jit_temp`
- `.ll` e `.o` gerados

## `lumina new`

`cmd_new(project_name)` cria:

```
<nome>/
├── lumina.toml
└── main.lm
```

Conteúdo de `lumina.toml`:

```toml
[package]
name = "<nome>"
version = "0.1.0"
entry = "main.lm"

[dependencies]
```

`main.lm` é um `Hello from <nome>!`.

## `lumina.toml`

Formato completo:

```toml
[package]
name = "MeuBanco"
version = "0.1.0"
entry = "main.lm"

[dependencies]
meu_pacote = "github:adamgabriel701/Lumina"

[link]
libs = ["m", "pthread", "raylib"]
extra_objects = ["examples/ffi_helper.cpp"]
extra_flags = ["-DFOO=1", "-Iinclude"]
target = "wasm32-wasi"
```

### `[link]`

Lido por `load_link_config(entry_file)`. Procura:

1. **Sidecar**: `foo.lm` → `foo.toml`
2. **Raiz**: `./lumina.toml`

Chaves:

| Chave | Efeito |
|---|---|
| `libs` | Adiciona `-l<lib>` no clang |
| `extra_objects` | Compila `.c`/`.cpp` com clang/clang++ e linka |
| `extra_flags` | Passa direto ao clang (+ `-DFOO=1`, `-Iinclude`) |
| `target` | Sobrescreve o target (mesmo efeito de `--target`) |

`compile_extra_objects()` detecta C++ pela extensão (`.cpp`, `.cc`,
`.cxx`, `.C`) e usa `clang++`. Passa `linker_extra_flags` para o
compilador do objeto (bug fix: `.cpp` com `-DFOO=42` era ignorado).

## Exit codes

| Comando | Exit code |
|---|---|
| `run` | Propaga o do binário |
| `build` | 0 se OK, ≠ 0 se falha |
| `check` | 0 se OK, ≠ 0 se erros |
| `test` | Nº de testes falhando |
| `lint` | Nº de warnings |
| `fmt` | 0 se já formatado, 1 se precisa |
| `--help` | 0 |

## Variáveis de ambiente

- **`LUMINA_ROOT`** — derivado do path do pacote (`utils.py`).
  Aponta para a raiz do repo; usado para achar `std/`.
- **`NO_COLOR`** — desabilita cores ANSI (via `_supports_color`
  em `common/colors.py`; honra `TERM=dumb` e `sys.stdout.isatty()`).

## Erros

`--error-format=json` faz erros irem para stdout como JSON
(`LuminaError.to_dict()`); progresso continua em stderr.

Formato do JSON:

```json
{
  "type": "error",
  "message": "Variável 'x' não declarada.",
  "filename": "foo.lm",
  "line": 3,
  "col": 5,
  "end_col": 6,
  "notes": ["você quis dizer 'y'?"]
}
```

## Ver também

- [Guia rápido](../getting-started/guia-rapido.md)
- [Ferramental](../guia/ferramental.md)
- [Internals › Arquitetura](../internals/arquitetura.md)
LUMINA_DOC_EOF

# =====================================================================
# Relatório
# =====================================================================
echo ""
echo "✓ Docs internals escritos:"
ls -la docs/internals/
echo ""
echo "✓ Referência da CLI:"
ls -la docs/referencia/
echo ""
echo "Próximo passo sugerido:"
echo "  ./scripts/context.sh docs   # mede o novo tamanho"
echo "  git add -A && git commit -m 'docs: preenche internals + referência CLI com conteúdo real'"
