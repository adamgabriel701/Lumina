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
| `Enum` | Enum definido pelo usuário |
| `Tuple` | Tupla de tipos heterogêneos |

### Inferência

```lumina
let x = 10            # int
let y = 3.14          # float
let s = "oi"          # str
let b = true          # bool
let p = nil           # ptr (default)
let t = (1, "dois")   # Tuple
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

### `impl Box<T>:` — métodos em structs genéricas

```lumina
struct Box<T>:
    data: T

impl Box<T>:
    fn get() -> int:
        return self.data
    fn set(v: int):
        self.data = v

fn main() -> int:
    mut b: Box<int>
    b.set(42)
    print(b.get())     # 42
    return 0
```

O `<T>` é descartado para registro (`Box_get`, `Box_set`). Chamadas em `Box<int>`, `Box<str>`, etc. resolvem pelo nome base. Funciona porque `Box<int>` e `Box<str>` têm layout idêntico (8 bytes) no LLVM.

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

## `for x in arr` — iteráveis

Itera sobre arrays literais e strings, sem precisar de `0..len`.

```lumina
fn main() -> int:
    let nums = [10, 20, 30]
    for n in nums:
        print(n)

    for n in [100, 200]:    # inline
        print(n)

    let s = "abc"
    for c in s:
        print(c)            # byte (int)
    return 0
```

Casos suportados:

- **Array literal via variável:** loop com N conhecido, GEP simples.
- **Array inline:** `for x in [1, 2, 3]`.
- **String:** `strlen` em runtime, elemento `i8`.
- **`break` / `continue`:** funcionam normalmente.
- **Nested:** `for a in outer: for b in inner: ...`.

## Tuplas

Tuplas literais com tipos heterogêneos:

```lumina
fn main() -> int:
    let (a, b, c) = (1, 2, 3)
    print(a + b + c)          # 6

    let (nome, idade) = ("Adam", 30)
    print(nome, idade)        # Adam 30

    let (n, s) = (42, "hello")  # tipos diferentes
    print(n)                  # 42
    print(s)                  # hello
    return 0
```

`LiteralStructType` no LLVM: cada elemento mantém seu tipo. O destructuring funciona sobre tuplas, structs nomeadas e arrays `alloc`'d.

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

## Escape analysis

`alloc(N)` com `N` constante e sem `return`/`free` viram `alloca` no stack:

```lumina
fn main() -> int:
    let buf = alloc(10)     # vira alloca, não GC_malloc
    buf[0] = 42
    print(buf[0])           # 42
    return 0
```

## FFI (extern)

```lumina
extern fn printf(fmt: str, ...) -> int
extern fn malloc(size: int) -> ptr
```

Configurar libs em `[link]` no `lumina.toml`.

## Símbolos reservados

`fn`, `let`, `mut`, `const`, `if`, `elif`, `else`, `while`, `for`, `in`,
`return`, `break`, `continue`, `defer`, `errdefer`, `match`, `case`,
`default`, `switch`, `struct`, `enum`, `impl`, `trait`, `import`,
`extern`, `assert`, `bench`, `test`, `comptime`, `export`, `as`,
`true`, `false`, `none`, `nil`, `and`, `or`, `not`.
