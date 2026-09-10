# 🌟 Lumina Examples

Esta pasta contém exemplos práticos e avançados demonstrando o poder da linguagem Lumina.

## 🚀 Como rodar
Para compilar e rodar qualquer exemplo, use a CLI da Lumina a partir da raiz do projeto:
```bash
lumina build examples/nome_do_arquivo.lm
./examples/nome_do_arquivo
```

## 📂 Categorias

### 🌐 Redes e Concorrência
- `server.lm`: Web Server básico usando POSIX Sockets puros (sem abstrações).
- `async_server.lm` / `serve.lm`: Servidores Async I/O usando `epoll` nativo do Linux (Alta performance e non-blocking).
- `proxy.lm`: Proxy Reverso completo. Recebe HTTP, conecta ao backend, encaminha e fecha sockets.
- `threads.lm`: Uso de multithreading nativo via `pthread_create` e compartilhamento de memória.
- `coroutines.lm`: Green Threads (Corrotinas) usando troca de contexto de CPU (`ucontext`).

### 🗄️ Bancos de Dados e Sistemas
- `lumina_db.lm`: Mini banco de dados em memória com persistência em disco (Write-Ahead Log).
- `sql_engine.lm`: Motor de SQL (Columnar Database) com suporte a SELECT, WHERE e SUM.
- `json_parser.lm`: Parser de JSON construído do zero (sem bibliotecas externas).

### ⚙️ Sistemas e Baixo Nível
- `chip8.lm`: Emulador completo da arquitetura CHIP-8 com renderização no terminal.
- `vm.lm`: Máquina Virtual (VM) simples com Fetch, Decode e Execute de Bytecodes.
- `bits.lm`: Demonstração de operações Bitwise (AND, OR, Deslocamentos).
- `escape_test.lm`: Demonstra o Escape Analysis da Lumina (Heap vs Stack automaticamente).

### 🎨 Ergonomia da Linguagem
- `trait_test.lm`: Uso de Traits (Interfaces) e polimorfismo estático.
- `struct_lit_test.lm`: Inicialização de Structs inline (ex: `Point { x: 1, y: 2 }`).
- `match_expr_test.lm`: Pattern Matching que retorna valores diretamente.
- `error_handling.lm`: Tratamento de erros com `Result`, `Option` e o operador `?`.
- `safe_nav.lm`: Navegação segura para evitar Segfaults com `?.`.
- `ergonomia.lm`: F-strings nativas, Operador Pipe (`|>`) e Testes nativos (`test "nome":`).
- `destructure_test.lm`: Destructuring de arrays em variáveis (ex: `let (x, y) = coords`).

### 🧮 Compiladores e Metaprogramação
- `bootstrap_lexer.lm`: Um Lexer escrito na própria linguagem Lumina (Bootstrapping).
- `comptime_test.lm`: Avaliação de expressões em tempo de compilação (Zero runtime cost).

## 🧪 Exemplos da Standard Library
- `vector_test.lm`: Uso do Array Dinâmico (auto-expansível) da `std/vector`.
- `map_test.lm`: Uso do Hash Map com tratamento de colisões da `std/map`.
