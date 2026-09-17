# 📚 Documentação Lumina

Índice navegável. Todos os arquivos estão em `docs/`.

---

## 🚀 Começando

- [**Guia Rápido**](guia-rapido.md) — instalação, primeiro programa, CLI.
- [**Linguagem**](linguagem.md) — referência completa da sintaxe e semântica.
- [**Standard Library**](stdlib.md) — módulos `std/*`.
- [**Ferramental**](ferramental.md) — REPL, LSP, formatter, testes.

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
- Genéricos, traits, pattern matching
- TCO (self e mutual recursion)
- `defer`, `nil`, `@safe`, `@macro`
- REPL persistente, LSP completo, formatter

Status: **Alpha / Active**. 267 testes passando, 0 skips.
```

---

## 📄 `docs/guia-rapido.md`

```markdown
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
| `lumina fmt arquivo.lm` | Formata (preserva comentários) |
| `lumina fmt arquivo.lm --check` | Verifica formatação (pre-commit) |
| `lumina build app.lm --release` | Compila com `-O3` |
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
- [Ferramental](ferramental.md) — LSP, formatter, testes
```

---

## 📄 `docs/linguagem.md`

```markdown
# 📖 Linguagem

## Sintaxe básica

Escopo por indentação (4 espaços). Sem `{}` nem `;`.

```lumina
fn main() -> int:
    x := 10
    if x > 5:
        print("grande")
    return 0
```

## Tipos

| Tipo | Descrição |
|---|---|
| `int` | Inteiro 64-bit (`i64`) |
| `float` | Ponto flutuante 64-bit (`f64`) |
| `bool` | Booleano (`i1`) |
| `str` | Ponteiro para string (`i8*`) |
| `ptr` | Ponteiro genérico |
| `fn` | Function pointer |
| `void` | Sem retorno |
| `Struct` | Struct definida pelo usuário |

### Inferência

```lumina
let x = 10            # int
let y = 3.14          # float
let s = "oi"          # str
let b = true          # bool
let p = nil           # ptr (default)
```

## Variáveis

```lumina
let x = 10            # imutável
mut y = 20            # mutável
z := 30               # mutável (sintaxe curta)
let p: Ponto = nil    # anotação explícita
```

## Funções

```lumina
fn soma(a: int, b: int) -> int:
    return a + b

fn log(msg: str):
    print(msg)
```

### Parâmetros padrão

```lumina
fn greet(name: str = "World") -> int:
    print("Hello,", name)
    return 0
```

### Genéricos

```lumina
fn identidade<T>(x: T) -> T:
    return x

struct Box<T>:
    data: T

fn put<T>(b: Box<T>, val: T):
    b.data = val
```

## Estruturas de controle

```lumina
if x > 0:
    print("positivo")
elif x < 0:
    print("negativo")
else:
    print("zero")

while i < 10:
    i += 1

for i in 0..10:
    print(i)

switch n:
    case 1: return "um"
    case 2: return "dois"
    default: return "?"
```

## Pattern Matching

### Básico

```lumina
match p:
    case Dois(a, b): print(a, b)
    case Zero:       print("zero")
```

### Multi-pattern + Wildcard

```lumina
match n:
    case 1 | 2 | 3: return "pequeno"
    case 4 | 5:     return "médio"
    case _:         return "grande"
```

### Guard

```lumina
match n:
    case x if x > 100: return "grande"
    case x:            return "pequeno"
```

### Variantes bare

```lumina
enum Color:
    Red
    Green
    Blue

let c = Red      # constrói implicitamente
```

## Enums (ADTs)

```lumina
enum Result:
    Ok(int)
    Err(int)

enum Multi:
    Dois(int, int)
    Zero
    Um
```

## Structs e métodos

```lumina
struct Ponto:
    x: int
    y: int

impl Ponto:
    fn soma() -> int:
        return self.x + self.y

fn main() -> int:
    let p = Ponto { x: 1, y: 2 }
    print(p.soma())    # 3
    return 0
```

## Traits

```lumina
trait Greeter:
    fn name() -> str
    fn greet():
        print("Hello from", name())

struct English:
    dummy: int

impl Greeter for English:
    fn name() -> str:
        return "Lumina"
```

## `@derive`

```lumina
@derive(Eq, PartialEq, Debug, Clone, Default)
struct Ponto:
    x: int
    y: int
```

Gera:
- `Eq` / `PartialEq` → `__eq__`, `__ne__`
- `Debug` / `Display` → `__debug__`
- `Clone` → `clone(self)`
- `Default` → `new_Ponto()`

## `@safe` — null check opt-in

```lumina
@safe
fn get_id(u: Usuario) -> int:
    return u.id        # 0 se u == nil

@safe
fn first(arr: ptr) -> int:
    return arr[0]      # 0 se arr == nil
```

Sem `@safe`, `u.id` é C-style (SIGSEGV se nil).

## `@macro` — expansão de AST

```lumina
@macro
fn dobro(x: int) -> int:
    return x * 2

fn main() -> int:
    let a = 5
    print(dobro(a + 1))    # (a + 1) * 2
    return 0
```

Restrição: corpo deve ser um único `return <expr>`.

## Erros: `Option`, `none`, `nil`

```lumina
# Option
fn buscar(id: int) -> Option:
    if id == 42:
        return Some(100)
    return none

# nil (null pointer C-style)
fn get_id(u: Usuario) -> int:
    if u == nil:
        return -1
    return u.id

# Safe navigation
let v = u?.id          # 0 se u == nil
```

## Operadores modernos

| Operador | Descrição |
|---|---|
| `\|>` | Pipe: `5 \|> dobro` == `dobro(5)` |
| `?.` | Safe navigation |
| `?` | Propaga erro (`Result`) |
| `as` | Cast explícito |
| `:=` | Declaração curta |

## Slicing

```lumina
let s = "abcdef"
print(s[1..4])   # bcd
print(s[..3])    # abc
print(s[2..])    # cdef
print(s[..])     # abcdef
```

## `defer` com escopo de bloco

```lumina
fn main() -> int:
    defer print("fim da função")
    if 1 == 1:
        defer print("fim do if")
        print("dentro")
    for i in 0..2:
        defer print("fim da iteração")
        print(i)
    return 0

# dentro / fim do if / 0 / fim da iteração / 1 / fim da iteração / fim da função
```

## `comptime` (constant folding)

```lumina
let x = comptime(2 + 3 * 4)   # vira literal 14 no IR
```

## TCO (Tail Call Optimization)

Self-recursion:

```lumina
fn sum_rec(n: int, acc: int) -> int:
    if n == 0:
        return acc
    return sum_rec(n - 1, acc + n)   # vira loop
```

Mutual recursion:

```lumina
fn is_even(n: int) -> int:
    if n == 0: return 1
    return is_odd(n - 1)

fn is_odd(n: int) -> int:
    if n == 0: return 0
    return is_even(n - 1)
```

## FFI (extern)

```lumina
extern fn printf(fmt: str, ...) -> int
extern fn malloc(size: int) -> ptr

#[link]
# libs = ["m"]
```

## Símbolos reservados

`fn`, `let`, `mut`, `const`, `if`, `elif`, `else`, `while`, `for`, `in`,
`return`, `break`, `continue`, `defer`, `errdefer`, `match`, `case`,
`default`, `switch`, `struct`, `enum`, `impl`, `trait`, `import`,
`extern`, `assert`, `bench`, `test`, `comptime`, `export`, `as`,
`true`, `false`, `none`, `nil`, `and`, `or`, `not`.
