# 📦 Standard Library

Todos os módulos são escritos 100% na Lumina e vivem em `std/`.

Import: `import "std/nome"`.

---

## Fundamentos

### `std/prelude` (auto-importado)

```lumina
enum Option:
    Some(int)
    None

enum Result:
    Ok(int)
    Err(int)
```

### `std/math`

```lumina
extern fn pow(base: float, exp: float) -> float
extern fn sqrt(val: float) -> float
extern fn abs(val: int) -> int

fn potencia(base: float, exp: float) -> float
fn raiz_quadrada(val: float) -> float
fn valor_absoluto(val: int) -> int
```

### `std/str`

```lumina
fn to_upper(s: str) -> str
fn to_lower(s: str) -> str
fn trim(s: str) -> str
fn ends_with(s: str, suffix: str) -> int
fn split(s: str, delimiter: str) -> ptr
fn join(arr: ptr, delimiter: str) -> str
fn substr(s: str, start: int, length: int) -> str
fn find(texto: str, alvo: str) -> int
```

### `std/time`

```lumina
fn agora() -> int      # clock() em ticks
```

### `std/fs`

```lumina
fn deletar_arquivo(path: str) -> int
```

### `std/alloc`

Arena allocator para `--no-gc`:

```lumina
struct Arena:
    buffer: ptr
    offset: int
    capacity: int

fn init(cap: int) -> Arena
fn alloc(a: Arena, size: int) -> ptr
fn reset(a: Arena)
fn destroy(a: Arena)
```

---

## Coleções

### `std/vector`

Array dinâmico com crescimento automático (dobra a capacidade).

```lumina
import "std/vector"

mut v = new_vector()
v.push(10)
v.push(20)
print(v.get(0))     # 10
print(v.sum())      # 30
print(v.is_empty()) # 0

# Métodos: push, pop, get, set, clear, is_empty, sum
# Campos: data (ptr), len (int), cap (int)
```

### `std/map`

Hash map `int → int` com rehash em load factor ≥ 0.75.

```lumina
import "std/map"

mut m = new_map()
m.insert(42, 100)
print(m.get(42))       # 100
print(m.contains(42))  # 1
m.remove(42)
```

### `std/set`

Conjunto de `int` com rehash.

```lumina
import "std/set"

mut s = new_set()
s.add(1); s.add(2); s.add(1)
print(s.size)          # 2
print(s.contains(1))   # 1
```

### `std/deque`

Fila dupla com buffer circular e crescimento.

```lumina
import "std/deque"

mut d = new_deque()
d.push_back(1)
d.push_front(0)
print(d.pop_front())   # 0
print(d.pop_back())    # 1
```

### `std/list`

Linked list simples.

```lumina
import "std/list"

mut l = new()
push(l, 10)
push(l, 20)
print(get(l, 0))       # 10
print(l.size)          # 2
```

### `std/iter`

Adaptadores funcionais para arrays. Callbacks: `fn(x: int) -> int`.

```lumina
import "std/iter"

let n = 5
mut arr = alloc(n)
arr[0] = 1; arr[1] = 2; arr[2] = 3; arr[3] = 4; arr[4] = 5

sum(arr, n)                                # 15
product(arr, n)                            # 120
min(arr, n); max(arr, n)
count_if(arr, n, fn(x: int) -> int: (x % 2) == 0)
map(arr, n, fn(x: int) -> int: x * 2)
filter(arr, n, fn(x: int) -> int: x > 2)
all(arr, n, fn(x: int) -> int: x > 0)
any(arr, n, fn(x: int) -> int: x > 3)
find_index(arr, n, fn(x: int) -> int: x == 4)
copy(arr, n); fill(arr, n, 0)
for_each(arr, n, fn(x: int) -> int: x + 10)
reverse(arr, n)
```

---

## Testes e Logging

### `std/test`

```lumina
import "std/test"

test "soma":
    return check_eq(1 + 1, 2, "1+1 == 2")

test "strings":
    return check_str_eq("a" + "b", "ab", "concat")

fn main() -> int:
    return 0
```

`lumina test arquivo.lm` roda todos os blocos `test "..."` e retorna exit = total de falhas.

Funções: `check_eq`, `check_ne`, `check_true`, `check_false`, `check_str_eq`.

### `std/log`

Níveis `DEBUG=0`, `INFO=1`, `WARN=2`, `ERROR=3`.

```lumina
import "std/log"

set_level(LOG_LEVEL_INFO)
log_debug("não aparece")
log_info("iniciando")
log_warn("cuidado")
log_error("falhou")
```

---

## Concorrência e I/O

### `std/channel`

Canais estilo Go (CSP).

```lumina
import "std/channel"

let c = new(10)   # buffer de 10
send(c, 42)
print(recv(c))    # 42
```

### `std/async`

Green threads (ucontext). **Esqueleto** — ver limitações.

### `std/async_fs`

I/O não-bloqueante (`O_NONBLOCK`).

```lumina
import "std/async_fs"

let dados = read_file_async("arquivo.txt")
```

### `std/epoll`

Event loop (Linux).

```lumina
import "std/epoll"

let epfd = criar()
adicionar(epfd, server_fd)
let events = esperar(epfd, 100)
```

### `std/net` / `std/http`

Servidor TCP/HTTP.

```lumina
import "std/http"

let server_fd = iniciar(8080)
```

---

## Integração

### `std/json`

Parser simples.

```lumina
import "std/json"

let payload = "{\"name\":\"Adam\",\"age\":25}"
let name = get_str(payload, "name")    # Adam
let age = get_int(payload, "age")      # 25
```

### `std/sqlite`

FFI para SQLite3.

```lumina
import "std/sqlite"

let db = abrir("dados.db")
executar(db, "CREATE TABLE ...")
fechar(db)
```

### `std/raylib`

Engine 2D/3D.

```lumina
import "std/raylib"

InitWindow(800, 600, "Lumina")
while WindowShouldClose() == 0:
    BeginDrawing()
    ClearBackground(RAYWHITE)
    DrawText("Hello", 300, 250, 20, BLACK)
    EndDrawing()
CloseWindow()
```

Requer `libraylib.so`. Configurar em `[link]`.
