# 🌟 Lumina Examples

Catálogo completo dos exemplos. Cada arquivo `.lm` também tem um binário compilado (`.ll` + executável) quando aplicável.

## 🚀 Como rodar

```bash
lumina build examples/nome.lm
./examples/nome
```

Ou direto: `lumina run examples/nome.lm`

---

## 🌐 Rede e Concorrência

| Arquivo | O que mostra |
|---|---|
| `server.lm` | Web server básico com POSIX sockets puros |
| `serve.lm` | Variante do server com abstrações maiores |
| `async_server.lm` | Servidor assíncrono com `epoll` + `O_NONBLOCK` |
| `async_file_test.lm` | I/O de arquivos não-bloqueante |
| `proxy.lm` | Proxy reverso HTTP (recebe, encaminha, fecha) |
| `proxy.ll` | IR do proxy |
| `threads.lm` | Multithreading nativo com `pthread_create` |
| `coroutines.lm` | Green threads via `ucontext` (troca de contexto) |

## 🗄️ Bancos de Dados e Sistemas

| Arquivo | O que mostra |
|---|---|
| `lumina_db.lm` | Mini banco em memória com write-ahead log |
| `native_db.lm` | Variante mais baixo nível do banco |
| `sql_engine.lm` | Motor de SQL colunar (SELECT, WHERE, SUM) |
| `database.lm` | Exemplo de camada de dados |
| `search_engine.lm` | Indexação e busca de texto |
| `json_parser.lm` | Parser de JSON do zero |
| `json_test.lm` | Testes do parser de JSON |
| `quicksort.lm` | QuickSort recursivo |

## ⚙️ Sistemas e Baixo Nível

| Arquivo | O que mostra |
|---|---|
| `chip8.lm` | Emulador CHIP-8 completo (renderiza no terminal) |
| `vm.lm` | Máquina virtual com fetch/decode/execute |
| `bits.lm` | Operações bitwise (AND, OR, shifts) |
| `escape_test.lm` | Escape analysis: stack vs heap automáticos |
| `gc_test.lm` | Interação com o Boehm GC |
| `tco_test.lm` | Tail Call Optimization em recursão |
| `iterator_test.lm` | Iteradores customizados |
| `linked_list_demo.lm` | Lista ligada com ponteiros |
| `lexer.lm` | Lexer escrito em Lumina (bootstrapping) |
| `parser.lm` | Parser escrito em Lumina |
| `bootstrap_lexer.lm` | Variante do lexer para bootstrapping |
| `engine.lm` | Motor genérico (config + dispatch) |

## 🎨 Ergonomia da Linguagem

| Arquivo | O que mostra |
|---|---|
| `trait_test.lm` | Traits (interfaces) e polimorfismo estático |
| `trait_default_test.lm` | Traits com métodos default (usa `#23`) |
| `struct_lit_test.lm` | Inicialização inline: `Point { x: 1, y: 2 }` |
| `match_expr_test.lm` | Pattern matching que retorna valor |
| `match_struct_test.lm` | Destructuring de struct no `match` |
| `error_handling.lm` | `Result`, `Option`, operador `?` |
| `safe_nav.lm` | Navegação segura `?.` |
| `ergonomia.lm` | F-strings, pipe `|>`, `test "nome":` |
| `destructure_test.lm` | Destructuring: `let (x, y) = coords` |
| `break_test.lm` | `break` em loops |
| `cast_test.lm` | Casts `as` entre tipos |
| `defaults_test.lm` | Parâmetros com default |
| `generics_test.lm` | Funções genéricas `<T>` |
| `monomorph_test.lm` | Monomorphization de structs `Box<int>` |
| `lambda_test.lm` | Closures / funções anônimas |
| `overload_test.lm` | Overload via traits |
| `struct_lit_test.lm` | Struct literals |
| `string_methods_test.lm` | Métodos de string (`upper`, `contains`) |
| `features.lm` | Showcase geral de features |
| `features_showcase.lm` | Showcase estendido |

## 🧮 Metaprogramação e Compilação

| Arquivo | O que mostra |
|---|---|
| `comptime_test.lm` | Avaliação em tempo de compilação |
| `prelude_test.lm` | Uso do prelude automático |

## 🕸️ WebAssembly

| Arquivo | O que mostra |
|---|---|
| `wasm_math.lm` | Exporta `fib` pra JavaScript |
| `wasm_memory.lm` | Manipulação de memória no WASM |
| `wasm_js_interop.lm` | Chama JS do WASM (`extern "wasm"`) |

## 📚 Standard Library

| Arquivo | Módulo |
|---|---|
| `vector_test.lm` | `std/vector` — array dinâmico |
| `map_test.lm` | `std/map` — hash map |
| `string_methods_test.lm` | `std/str` |
| `ffi_test.lm` | FFI: chama libc |
| `api.lm` | Demo de API HTTP |
| `app.lm` | App de exemplo integrando módulos |
| `bench_test.lm` | Harness de benchmark |
| `http_framework.lm` | Framework HTTP |
| `test_runner.lm` | Test runner nativo |
| `util.lm` | Utilidades gerais |
| `main.lm` | Entrypoint do projeto exemplo |
| `program.lm` | Programa genérico de exemplo |

## 🔧 Exemplos arquivados / suporte

- `api.ll`, `app.ll`, `async_server.ll` etc — IR gerado (não editar)
- `MeuBanco/` — projeto de exemplo com `lumina.toml` próprio
- `program` — binário de suporte
- `util.ll` — IR de util

## 📖 Adicionando um novo exemplo

1. Crie `examples/meu_exemplo.lm`
2. Adicione uma entrada neste README na categoria adequada
3. Rode `lumina build examples/meu_exemplo.lm` e confirme que compila
4. Comite `.lm` (não precisa comitar `.ll` nem o binário)