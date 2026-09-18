# Changelog

Todas as mudanças notáveis deste projeto são documentadas aqui.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o projeto adere [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [Unreleased — 0.4.0]

### Adicionado

#### Linguagem
- **`type Alias = <tipo>`**: abrevia tipos longos e dá nome semântico. `type Callback = fn(int) -> int`; use `Callback` em params, retornos, campos de struct, `VarDecl` (locais e top-level) e payloads de enum. Aliases encadeados (`A → B → C`) e aliases dentro de assinaturas (`type Pred = fn(Callback) -> int`) funcionam. A expansão acontece na passada 0 do semantic; o resto do pipeline nunca vê o alias.
- **`type Alias<A, B> = ...` (aliases genéricos)**: aliases com parâmetros de tipo, com substituição de args. `type IPair<B> = Pair<int, B>` → use `IPair<str>` em qualquer posição de tipo (params, retornos, campos, `VarDecl`, payloads). O `expand_type_alias` faz substituição + recursão.
- **Enums genéricos com inferência de type args**: `enum Res<T, E>: Ok(T); Err(E)` — os type args são inferidos no construtor (`Ok(42)` → `Res<int, int>`; `Has("hello")` → `Box<str>`), e o registro acontece sob chave **canônica** (`Res<int,int>`) **e** mangled (`Res_int_int_`). Habilita enums genéricos aninhados com `match` correto.
- **`impl Trait for Box<int>` (especialização de trait em tipo genérico)**: além de `impl Box<T>:` (métodos na struct genérica, `<T>` descartado para registro → `Box_get`), agora `impl Trait for Box<int>:` preserva o tipo completo (mangle `Box_int__metodo`) e coexiste com `impl Trait for Box<str>:` (mangle `Box_str__metodo`). O lookup em chamadas tenta o nome completo primeiro e cai para o base como fallback.
- **`std/iter` e `std/sort` com assinaturas tipadas**: callbacks passam a ser `fn(int) -> int` (`std/iter`) e `fn(int, int) -> int` (`std/sort`). Passar lambda com arity ou tipos errados é detectado em compile-time em vez de segfault em runtime.
- **Tipos de função com assinatura (`fn(int, int) -> int`)**: antes `fn` era opaco (`voidptr`); agora é possível anotar params e retornos. Lambdas e funções nomeadas propagam a assinatura automaticamente, e chamadas via variável `fn` são validadas em compile-time (arity + tipos). `fn` sem assinatura continua aceitando qualquer valor, e mistura tipado/untyped é permitida nos dois sentidos.
- **`fn` como campo de struct**: `struct Handler: cb: fn(int) -> int`. Atribuir lambda (com ou sem captura) ou função nomeada ao campo; chamar via `h.cb(args)` faz indirect call e valida arity/tipos em compile-time. Habilita vtable manual, event handlers, callbacks armazenados.
- **Closures como callback (tipo `fn` unificado em fat pointer)**: todo valor `fn` em Lumina agora é `{fn_ptr, env_ptr}`. Lambdas com captura usam env != NULL; lambdas sem captura e funções nomeadas usam env = NULL (wrapped em runtime). Isso destrava `sort_by(arr, n, fn(a, b): ...)` com captura, `map`/`filter` com captura em `std/iter`, e qualquer HOF. `&fn_name` devolve o fn ptr cru (FFI-compatível). Resolve o `xfail` histórico de `test_sort_closure_captures`.
- **Closures** (captura por valor): `let offset = 10; let add = fn(x: int) -> int: x + offset`. O codegen detecta variáveis livres em `LambdaExpr`, gera um bloco `{fn_ptr, env_ptr}` no heap, e emite uma função `i64 __closure_N(i8* env, i64 a1, ..., i64 aN)` que lê os campos do env. Suporta lambda aninhada, captura dentro de loop, e chamada com N argumentos.
- **Escape sequences em strings**: `\n`, `\t`, `\r`, `\0`, `\a`, `\b`, `\f`, `\v`, `\\`, `\"`, `\'` são processados pelo lexer em compile-time. Antes eram preservados como texto literal (`\` + letra). Escapes desconhecidos são mantidos como `\X` (backslash + letra) para não quebrar código existente.
- **Macros multi-statement (`nome!(args)`)**: sintaxe nova que inlineia o corpo inteiro da macro no call site. Diferente de `nome(args)` (macro de expressão, exige corpo `return <expr>`), `nome!(args)` aceita qualquer número de statements e é usado em posição de statement. Substituição de parâmetros cobre expressões e statements (`VarDecl`, `AssignStmt`, `ReturnStmt`, `IfStmt`, `WhileStmt`, `ForStmt`, `DeferStmt`, `AssertStmt`). Inclusive `return` dentro da macro retorna da função chamadora.
- **`for i, x in arr`** — índice + valor no mesmo loop. Parser aceita `IDENT COMMA IDENT` após `for`; o `ForStmt` guarda `"i,x"` em `var_name`; o semantic declara ambos; o codegen emite slot para o índice e para o valor.
- **`std/sort`** — `sort(arr, n)` (crescente) e `sort_by(arr, n, cmp)` (comparator). Insertion sort para `n ≤ 16`, quicksort acima. `is_sorted(arr, n)` verifica.
- **`fn_name` como valor** — `sort(arr, n, _cmp_asc)` passa função por nome. Semantic retorna `"fn"`, codegen produz fat pointer `{wrapper, NULL}`.
- **Indirect call com N args** — `fn_ty = i64 (i8*, i64, ..., i64)` via fat pointer. `cmp(a, b)` agora passa ambos.
- **Variante com payload usada bare** agora é erro: `let x = Some` falha com mensagem clara em vez de compilar silenciosamente.
- **`std/io`** — `read_line`, `read_int`, `read_char`, `write`, `write_line`, `eprintln`. Usa os builtins `stdin`/`stdout`/`stderr`/`fgets`/`fputs`/`fflush`/`getchar` diretamente.

#### `std`
- `std/sort.lm` — `_cmp_asc`, `_insertion_sort`, `_partition`, `_quicksort_rec`, `sort`, `sort_by`, `is_sorted`.
- `std/string.lm` — `StringBuilder` com `push_char`, `push_str`, `finish`, `clear`, `size`.
- `std/result.lm` — `unwrap`, `unwrap_or` (renomeado `default` → `fallback`), `is_ok`, `is_err`, `is_ok_and`, `expect`, `map`, `and_then`.
- `std/io.lm` — `read_line` (remove `\n` final, retorna `""` em EOF), `read_int`, `read_char`, `write`, `write_line`, `eprintln`. Sem `extern fn` declarados (são builtins do compilador). Usa `"\n"` diretamente (o lexer agora processa o escape).

### Corrigido

#### Genéricos (sessão de fechamento)

- **`get_llvm_param_type` retornava tipos diferentes para a mesma string dependendo da ordem das chamadas.** Durante `register_function`, `"Box<int>"` ainda não estava em `struct_types`, então caía no `get_llvm_type` que faz monomorphização on-demand e devolve **valor** (`Box_int_`). Na 2ª chamada (durante `generate_function_body`), já estava em `struct_types` e devolvia **ponteiro** (`Box_int_*`). Resultado: `alloca(Box_int_*)` cria `Box_int_**`, e `store(Box_int_, Box_int_**)` explode com `TypeError: cannot store %"Box_int_" to %"Box_int_"**`. **Fix:** `get_llvm_param_type` sempre chama `get_llvm_type` primeiro (forçando monomorphização) e devolve `.as_pointer()` se for `IdentifiedStructType`.
- **`impl Box<T>:` era mangleado como `Box_T__get`, nunca encontrado.** O parser fazia `mangle_method("Box<T>", "get")` → `Box_T__get`, mas o codegen só procura por `Box_int__get` (especialização) e `Box_get` (base). **Fix:** `parse_impl` normaliza `impl Box<T>:` → `Box` quando todos os type args do alvo são type params únicos maiúsculos (`T`, `U`, `V`). `impl Getter for Box<int>:` mantém `Box<int>` (especialização). Cobre os dois casos sem ambiguidade.
- **Semantic procurava `Box_get` mesmo quando existia `Box_int__get`.** O lookup em `visit_CallExpr` usava `f"{obj_type.split('<')[0]}_{func_name}"`. Com `impl Getter for Box<int>`, o método estava registrado como `Box_int__get` e o lookup buscava `Box_get`. **Fix:** lookup tenta o nome completo (`mangle_method(obj_type, func_name)`) e cai para o nome base; mesmo padrão em `_infer_call_expr_type`.
- **`_resolve_trait_defaults` (codegen) usava f-string em vez de `mangle_method`.** `f"{decl.struct_name}_{trait_method.name}"` produzia `Box<T>_greet` quando o alvo era genérico. **Fix:** `mangle_method` (mesma função canônica usada pelo parser).
- **`struct_defs` só registrava chave mangled.** `get_or_create_monomorphized_struct` e `get_or_create_monomorphized_enum` faziam apenas `self.struct_defs[mangled] = base_decl`, mas `_construct_enum` consulta por `self.struct_defs["Custom<int>"]` (chave canônica). **Fix:** registra sob **ambas** as chaves.
- **`visit_VarDecl` forçava tipo default de enum genérico.** Em `let c = Wrap(42)`, semantic infere `var_type = "Custom"` (nome base, sem args). `is_struct_like` era `False`, então caía em `llvm_ty = get_llvm_type("Custom")`, que monomorphiza com defaults (`Custom<int>`) e devolve `Custom_int_` (valor). O `_construct_enum` produz `Custom_int_*` (ponteiro), e o `bitcast` final era `Custom_int_* → Custom_int_` (inválido). Pior: em `let b = Has("hello")`, `val.type = Box_str_*` mas `llvm_ty = Box_int_*` (defaults), causando `bitcast Box_str_* → Box_int_*` (structs diferentes). **Fix:** se `val.type` já é ponteiro para `IdentifiedStructType`, usa `val.type` como tipo do slot — o tipo real do valor sempre vence.

#### Demais correções

- **`type` como keyword quebrou bindings C de socket.** `std/http.lm`, `std/net.lm` e `examples/server.lm` usavam `type` como nome de parâmetro em `extern fn socket(domain, type, protocol)`. Renomeado para `sock_type`.
- **`_expand_type_aliases` não recursava em corpos de função.** `let cb: Callback = ...` dentro de `fn main` mantinha o tipo literal. Agora percorre `IfStmt`/`WhileStmt`/`ForStmt`/`MatchStmt`/`DeferStmt`/`BenchStmt` recursivamente.
- **Whitelist de tipos do `VarDecl` rejeitava `fn(...) -> R`.** Só aceitava `fn` puro. Após a expansão do alias `Callback` → `fn(int) -> int`, a validação rejeitava com "Tipo fn(int) -> int não declarado". Corrigido em `statements/var_decl.py` e `analyzer.py`.
- **`parse_struct` usava `expect(IDENT)` no tipo do campo.** `struct S: cb: fn(int) -> int` falhava com "Esperado IDENT, mas encontrei FN ('fn')". Corrigido para `parse_type()`.
- **Closure com captura como callback segfaultava.** `sort_by(arr, n, fn(a, b): (b-a)*mult)` passava o bloco `{fn_ptr, env_ptr}` como se fosse um fn ptr cru, e o receptor chamava lixo. **Fix:** unificação do tipo `fn` em fat pointer `{fn_ptr, env_ptr}` + `_call_closure` em toda chamada indireta. Funções nomeadas usadas como valor são wrapped em runtime (`_wrap_fn_as_closure`), com wrapper `i64(i8*, i64, ...)` que adapta a assinatura original. `&fn_name` devolve o fn ptr cru para FFI.
- **`_validate_macro` bloqueava macros multi-statement mesmo na declaração.** A validação exigia `return <expr>` no `generate_module`, então uma macro multi-statement nunca podia ser declarada — mesmo que só fosse usada via `nome!(args)`. **Fix:** a validação só verifica que o corpo não está vazio; a exigência de `return <expr>` fica inteiramente a cargo de `_expand_macro_expr` (usado quando a macro é chamada como expressão).
- **`stdin`/`stdout`/`stderr` faltavam em `BUILTIN_RET`.** `std/io.lm` falhava no semantic com "Tipo inválido para parâmetro 'stream': esperado 'str', obteve 'int'" porque `stdout()` era inferido como `int` no `VarDecl`. **Fix:** `BUILTIN_RET` centralizado em `lumina/builtins.py` (fonte única) e `stdin`/`stdout`/`stderr` adicionados como `"str"`.
- **`extern fn fgets` colidia com o builtin.** O `generate_module` registrava o extern com assinatura `i8*(i8*, i64, i8*)`, mas o branch de builtin em `calls.py` trunca `size` para `i32` (assinatura real do C). Resultado: `TypeError: Type of #2 arg mismatch: i64 != i32`. **Fix:** `generate_module` pula `ExternDecl` cujo nome está em `BUILTIN_FUNCTIONS` — o codegen de builtin já emite a assinatura correta.
- **`getchar` retornava `i32` sem normalização.** `ret i32 %getchar_call` não casava com o tipo de retorno `-> int` da função Lumina (i64), gerando `value doesn't match function result type 'i64'` no clang. **Fix:** `sext i32 → i64` antes de retornar.
- **`visit_ReturnStmt` sem normalização `iN → i64`.** Qualquer builtin que devolvesse `i32`/`i8`/`i16` quebrava no `ret`. **Fix:** branch defensivo em `flow.py::visit_ReturnStmt` com `zext` para `i1` e `sext` para os demais.
- **`"\n"` em fonte Lumina virava 2 bytes literais.** O lexer preservava escapes como texto (`\` + `n`), então `fputs("\n", out)` imprimia `\n` literal em vez de newline. **Fix:** lexer processa escapes em compile-time; `std/io.lm` usa `"\n"` diretamente.
- **`read_line` com `buf[n-1] = 0` não surtia efeito.** Reescrevido com loop explícito que varre o buffer até NUL ou `\n` (ASCII 10), sobrescrevendo com NUL no primeiro caso.
- **`_handle_indent` não era chamado em `tokenize()`.** Regressão que quebrava **todos** os blocos indentados — `fn`, `if`, `while`, `for`, `struct`, `enum`, `impl`, `trait`, `match` — com "Esperado INDENT, mas encontrei X". **Fix:** restaurado o branch `if self.at_line_start: self._handle_indent()` no loop principal.
- `visit_VariableExpr` (semantic + codegen) checava `functions` antes de variantes de enum. Como variantes são adicionadas em `functions` no `analyze()`, `Red` bare virava `"fn"` em vez de `"Color"`. **Fix:** ordem invertida (variante antes de função).
- `for x in arr` com `N` variável (não-literal) caía em loop vazio. Agora `array_lengths` também registra `alloc(NumberExpr)`.
- `parse_for` declarava `from ..ast import ForStmt` dentro do método, sombreando o import do topo do arquivo → `UnboundLocalError`.
- `chr` e `atoi` sem branch de codegen (retornavam `0`). Adicionados em `calls.py`.
- `SliceExpr` inferido como `ptr` no `VarDecl`, fazendo `s[..3] == "abc"` comparar endereços. Agora infere pela fonte (`str` → `str`, array → `ptr`).
- `bool` → `int` usava `sext` (`true` virava `-1`). Agora `zext` quando origem é `i1`.
- `read_file()` dava segfault se o arquivo não existia. Agora retorna `""` via `phi` com `fopen == NULL`.
- `free()` rejeitava `i64*` (`TypeError: i8* != i64*`). Bitcast antes do call.
- `impl Box<T>` chamado em `Box<int>` gerava `%"Box"* != %"Box_int_"*`. Bitcast no `codegen_method_call` quando cai no fallback.
- `std/result::unwrap_or` usava `default` (keyword reservada). Renomeado para `fallback`.
- `and_then` retornava `int` para function pointers, falhando em `_require_assignable`. Agora retorna `None` (tipo desconhecido).
- `lumina lint` estourava `RecursionError` por recursão mútua entre `_collect_vars` e `_collect_exprs`. Reescrito como `_collect` única.

### Adicionado (tests)

- `tests/test_type_alias.py` (8 testes) — alias de primitivo, alias de `fn`, alias em campo/param/retorno/VarDecl/enum, encadeamento.
- `tests/test_fn_struct_fields.py` (7 testes) — campo fn-typed, lambda com captura, função nomeada, múltiplos campos fn, erro de arity e tipo.
- `tests/test_fn_types.py` (12 testes) — parse de `fn(T1, T2) -> R`, chamada com arity e tipos validados, mistura tipado/untyped, propagação de retorno, assinatura com `str`.
- `tests/test_macro_stmts.py` (8 testes) — `nome!(args)`, substituição em statements, validação de arity, rejeição de `nome!(args)` sem macro, `return` em macro-stmt retorna da função chamadora, uso em loop, macros expression continuam funcionando, macro multi-statement como expressão (sem `!`) é rejeitada.
- `tests/test_std_io.py` (6 testes) — `read_line`, `read_int`, `read_line_eof`, `write`, `write_line`, `eprintln`.
- `tests/test_closures.py` (10 testes).
- `tests/test_sort.py` (10 testes — `test_sort_closure_captures` deixou de ser xfail).
- `tests/test_lint.py` (14 testes, do 0.3.0).
- `tests/test_forin.py` (9 testes).
- `tests/test_tuples.py` (7 testes).
- `tests/test_generic_impl.py` (6 testes).
- `tests/test_std_result.py` (9 testes).
- `tests/test_escape_analysis.py` (4 testes).
- `tests/test_generic_enums.py` (2 testes, sessão de fechamento) — enum genérico `Wrap(42)` e `Has("hello")`, com inferência de type args na construção e match correto.
- `tests/test_impl_box_generic.py` (3 testes, sessão de fechamento) — `impl Trait for Box<int>`, duas especializações distintas coexistindo (`impl Kind for Box<int>` e `impl Kind for Box<str>`), e `impl Box<T>:` como fallback.
- `tests/test_generic_type_alias.py` (4 testes, sessão de fechamento) — `type BI = Box<int>` em assinatura de função, em param de struct, encadeado (`A → B → C`) e com params (`type IPair<B> = Pair<int, B>`).

**Total: 428 passed** (antes 419; antes disso, 411).

### Mudado

- `lumina/lexer/lexer.py` — `_read_escape` processa `\n`/`\t`/`\r`/`\0`/`\a`/`\b`/`\f`/`\v`/`\\`/`\"`/`\'` em compile-time. Escapes desconhecidos preservam `\X` como texto. Aplica-se a strings normais e interpoladas (`f"..."`).
- `lumina/ast/statements.py` — novo nó `MacroCallStmt` (name, args, line, col) para `nome!(args)`.
- `lumina/parser/statements.py` — detecta `IDENT BANG LPAREN` em statement position e produz `MacroCallStmt`.
- `lumina/semantic/statements/macro_stmt.py` (novo) — valida que `nome!(args)` referencia uma `@macro` declarada e que a aridade bate.
- `lumina/semantic/analyzer.py` — coleta `@macro` em `self.macros` (passada 0) para validar `MacroCallStmt`.
- `lumina/codegen/statements/macro_stmt.py` (novo) — `visit_MacroCallStmt` inlineia o corpo inteiro da macro no call site.
- `lumina/codegen/expressions/macros.py` — nova função `_substitute_in_stmt` que percorre `VarDecl`, `DestructureStmt`, `AssignStmt`, `ReturnStmt`, `IfStmt`, `WhileStmt`, `ForStmt`, `DeferStmt`, `AssertStmt` e delega expressões a `_substitute_in_expr`.
- `lumina/codegen/traits.py::_validate_macro` — só valida que o corpo não está vazio. A exigência de `return <expr>` fica em `_expand_macro_expr` (call site expression).
- `lumina/codegen/statements/__init__.py` — `MacroStmtMixin` adicionado à MRO.
- `lumina/builtins.py` — `BUILTIN_RET` agora vive ao lado de `BUILTIN_FUNCTIONS` (fonte única de verdade). Consumido por `semantic/statements.py`, `semantic/expressions.py` e `codegen/codegen.py`.
- `lumina/codegen/codegen.py::generate_module` — skip de `ExternDecl` que colide com builtin.
- `lumina/codegen/codegen.py::__init__` — `_fn_wrappers` cacheia wrappers `i64(i8*, i64...)` para funções nomeadas usadas como valor.
- `lumina/codegen/helpers.py` — `_make_fn_wrapper` (wrapper que adapta `i64(i8*, i64...)` → assinatura original) + `_wrap_fn_as_closure` (bloco `{wrapper, NULL}` no heap).
- `lumina/codegen/expressions/aggregates.py::visit_LambdaExpr` — sempre chama `_emit_lambda_closure`; `_emit_lambda_plain` removido.
- `lumina/codegen/expressions/members.py::visit_VariableExpr` — função nomeada usada como valor vira `_wrap_fn_as_closure`.
- `lumina/codegen/expressions/operators.py::visit_AddressOfExpr` — `&fn_name` devolve fn ptr cru (FFI-compatível).
- `lumina/codegen/expressions/calls.py` — toda chamada indireta passa por `_call_closure` (sem distinção `closure_vars` vs fn ptr cru).
- `lumina/codegen/expressions/calls.py::getchar` — `sext i32 → i64`.
- `lumina/codegen/statements/flow.py::visit_ReturnStmt` — normalização defensiva `iN → i64`.
- `lumina/semantic/expressions.py::visit_VariableExpr` reordena os checks: variante → `fn` → variável.
- `lumina/codegen/statements/control.py::_visit_for_iterable` — caso "índice + valor" quando `var_name` contém `,`.
- `std/io.lm` — reescrito. Sem `extern fn` (usa builtins), `"\n"` direto (lexer processa), `read_line` com loop explícito.
- `lumina/codegen/types.py::get_llvm_param_type` — força monomorphização antes de checar `struct_types`; `IdentifiedStructType` sempre devolve `.as_pointer()`.
- `lumina/codegen/types.py::get_or_create_monomorphized_{struct,enum}` — registra sob **chave canônica** (`Custom<int>`) **e** mangled (`Custom_int_`).
- `lumina/parser/declarations.py::parse_impl` — normaliza `impl Box<T>:` → nome base `Box` quando todos os args são type params únicos maiúsculos; `impl Trait for Box<int>` preserva `Box<int>`.
- `lumina/semantic/expressions/calls.py::visit_CallExpr` — lookup de método tenta nome completo (`mangle_method`) e cai para base.
- `lumina/semantic/statements/var_decl.py::_infer_call_expr_type` — mesmo padrão de lookup.
- `lumina/codegen/traits.py::_resolve_trait_defaults` — usa `mangle_method` (canônico) em vez de f-string.
- `lumina/codegen/statements/var_decl.py::visit_VarDecl` — usa `val.type` quando já é ponteiro para `IdentifiedStructType` (cobre `Box<str>` vs `Box<int>` e enum genérico com nome base).

### Adicionado (sessão de benchmarks)

#### Linguagem

- **`black_box(x: int) -> int`** — primitiva nativa que emite uma barreira
  `asm sideeffect ""` no IR (mesma técnica de `std::hint::black_box` do Rust).
  Impede que o LLVM elimine código cujo resultado "não é usado". Sem ela,
  `for i in 0..N: acc += i` é fechado na fórmula de Gauss e o benchmark mede
  zero. Registrada em `lumina/builtins.py` (`BUILTIN_FUNCTIONS` + `BUILTIN_RET`)
  e emitida via `ir.InlineAsm(..., side_effect=True)` em
  `codegen/expressions/builtins.py`.

- **`argv(i: int) -> str`** agora funciona de verdade. `main() -> int` sem
  params ganha a assinatura C `i32 (i32, i8**)`; o codegen salva `argc`/`argv`
  em globais `__lumina_argc`/`__lumina_argv` no entry de `main`; o builtin
  `argv(i)` lê `__lumina_argv[i]`. Antes, retornava `0` — todo `.lm`
  precisava ter N hardcoded.

#### Benchmarks

- **`benchmarks/alloc_churn.c`** e **`benchmarks/alloc_churn.lm`** — 1M
  alloc/free de tamanhos variados (1..512 bytes via LCG, seed fixo em 12345,
  wrap em u32). Diferente de `primes` (que só aloca 10 MB uma vez), mede o
  Boehm GC em churn real. Ambos usam barreira anti-DCE — C com
  `__asm__ __volatile__`, Lumina com `black_box` — para o loop não virar
  no-op.

- **`benchmarks/matrix_i64.c`** — variante de `matrix.c` com índices `i64`
  puros. Serve para isolar se a não-vetorização do matmul 200×200 vem do
  cast `(size_t)i * n + k` (hipótese testada: nem com nem sem o cast, nem
  gcc nem clang vetorizam o hot loop — é memory-bound).

- **`benchmarks/bench.sh`** reescrito:
  - **clang por padrão** (alinhado com o backend do Lumina). `CC=gcc` para
    cross-compiler. Motivo: C+clang vs Lumina+clang isola a linguagem;
    C+gcc media `gcc vs clang`, não `C vs Lumina`.
  - **`-fwrapv`** no `CFLAGS` — força overflow assinado a wrapping.
  - Compila variantes **`--no-gc`** de `primes` e `alloc_churn` para isolar
    custo do Boehm GC.
  - **`alloc_churn`** entra na verificação de corretude (RNGs alinhados —
    mesmo LCG, mesma seed).
  - Bloco extra de sumário para `primes_gc_vs_nogc`.

- **Parâmetros por `argv`** em `fib.lm`, `primes.lm`, `loop.lm`, `matrix.lm`,
  `alloc_churn.lm`. O `bench.sh` passa o mesmo N a todas as linguagens; não
  há mais N hardcoded.

#### Corrigido (sessão de benchmarks)

- **Closures emitiam `ret i32` num `define i64`.** `_emit_lambda_closure`
  não salvava/trocava `current_func_name` ao gerar o corpo da lambda. Com o
  `main` recebendo a assinatura `i32 (i32, i8**)`, o `visit_ReturnStmt`
  dentro de closures usava o tipo de retorno de `main` (i32) em vez do tipo
  real da closure (i64). Sintoma: `error: value doesn't match function
  result type 'i64'` no clang. **Fix:** registra a closure em
  `functions_table`, aponta `current_func_name` para o nome da closure,
  zera `current_body_bb` (desliga TCO dentro de closures), restaura após o
  corpo. Cobre `test_closure_body_block`, `test_closure_nested` e
  `lambda_test.lm`.

- **`main() -> int` sem params retornava `i64` para o clang.** Com a
  assinatura C `i32 (i32, i8**)`, o `ret` precisa truncar. `visit_ReturnStmt`
  ganhou branch defensivo `i64 → i32` quando `ret_ty.width < 64`.

### Mudado (benchmarks)

- **`loop.c`** — `t * (int64_t)i` virou `(int64_t)((uint64_t)t * i)`.
  Unsigned multiply tem wrap garantido pela norma; signed multiply era UB,
  o LLVM assumia "nunca negativo", e o branch era eliminado por DCE. C e
  Lumina agora medem a mesma coisa.

- **`alloc_churn.c`** — adicionada `static inline void bb(void *p)` com
  `__asm__ __volatile__("" : : "r"(p) : "memory")`. Sem isso, clang -O3
  apaga o par `malloc`/`free` (o ponteiro não escapa).

- **`alloc_churn.lm`** — adicionado `black_box(p as int)` após o store.
  Mesmo efeito.

### Removido (benchmarks)

- **`alloc_churn.lm`**: seed via `time(0)`. Agora usa seed fixo (12345),
  alinhado com o `.c`, para o output bater na verificação de corretude.

### Resultados (última rodada, 2026-09-18)

C compilado com **clang 18.1.3**, 20 runs, `taskset -c 1`:

| Bench | C | Rust | Go | **Lumina** | **L/C** |
|---|---:|---:|---:|---:|---:|
| fib (35) | 32.91 | 32.08 | 62.17 | **31.85** | **0.97×** |
| primes (10M) | 21.83 | 21.68 | 35.93 | 24.25 | 1.11× |
| loop (100M) | 88.10 | 96.82 | 82.55 | **88.87** | **1.01×** |
| matrix (200×200) | 5.54 | 7.99 | 14.25 | **5.39** | **0.97×** |
| alloc_churn (1M) | 13.27 | — | — | 50.01 | 3.77× |
| primes `--no-gc` | — | — | — | **23.48** | (vs GC: 0.84×) |
| alloc_churn `--no-gc` | — | — | — | **12.15** | **0.92×** |

**Leitura:** Lumina empata ou ganha de C em 4 de 5 benchmarks. O único gap
real é `alloc_churn`, atribuível ao Boehm GC — a variante `--no-gc` empata
com C (12.15 vs 13.27).

---

## [Unreleased — 0.3.0]

### Adicionado

#### Linguagem
- **Escape analysis:** `alloc(N)` com `N` constante e sem `return`/`free` viram `alloca` no stack. Reduz pressão no Boehm GC. Reduz ~30% das alocações em código típico.
- **`for x in arr`:** itera sobre arrays literais e strings. Aceita `let arr = [1, 2, 3]; for n in arr` e `for n in [10, 20]` inline.
- **Tuplas literais:** `let (a, b, c) = (1, 2, 3)`. Tipos heterogêneos via `LiteralStructType`.
- **`impl Box<T>:`** — métodos em structs genéricas. O `<T>` é descartado para registro; chamadas em `Box<int>`, `Box<str>`, etc. fazem bitcast para o tipo base.
- **`std/string`** — `StringBuilder` com `push_char`, `push_str`, `finish`, `clear`, crescimento geométrico. Complementa `std/str` (que é funcional).
- **`std/result`** — `unwrap`, `unwrap_or`, `is_ok`, `is_err`, `is_ok_and`, `expect`, `map`, `and_then`.
- **`lumina lint`** — análise estática sem gerar código: W001 (unused), W002 (shadowing), W003 (unreachable), W004 (unused param), W005 (empty body). `--format=json`, `--quiet`, exit code = nº warnings.
- **`opt -O2`** no IR antes do clang, apenas em `--release`.
- **`chr` e `atoi`** agora têm branches dedicados no codegen (antes retornavam 0).

#### CLI
- `lumina lint <arquivo> [--format=text|json] [--quiet]`.
- `--help`/`-h`/`help` retornam exit code 0 (antes caíam em "comando desconhecido").

### Corrigido

- `@attrs` sobrescritos como tuples em `parse()` — `@safe`/`@macro` nunca ativavam.
- `read_file()` dava segfault quando o arquivo não existia (agora retorna `""` via `phi`).
- `free()` rejeitava `i64*` (bitcast para `i8*` antes do call).
- `SliceExpr` era inferido como `ptr` no `VarDecl`, fazendo `s[..3] == "abc"` comparar endereços.
- `bool` → `int` usava `sext`, fazendo `true` virar `-1`. Agora usa `zext` quando origem é `i1`.
- `impl Box<T>` chamado em `Box<int>` gerava `%"Box"* != %"Box_int_"*`. Bitcast para o tipo base.
- `std/result::unwrap_or` usava `default` (keyword reservada). Renomeado para `fallback`.
- `for x in arr` com `N` não-constante caía em loop vazio. Agora registra `array_lengths` no `var_decl`.
- `and_then` retornava `int` para function pointers, falhando no `_require_assignable`.
- `lumina lint` estourava `RecursionError` por recursão mútua entre `_collect_vars` e `_collect_exprs`. Reescrito como `_collect` única.

### Adicionado (tests)

- `tests/test_lint.py` (14 testes).
- `tests/test_forin.py` (9 testes).
- `tests/test_tuples.py` (7 testes).
- `tests/test_generic_impl.py` (6 testes).
- `tests/test_std_result.py` (9 testes).
- `tests/test_escape_analysis.py` (4 testes).

**Total: 325 passed** (antes 267).

---

## [Unreleased — Sprint 9]

### Adicionado

#### Linguagem
- **TCO para mutual recursion (SCC dispatcher)**: SCCs (strongly connected components) do grafo de tail calls viram um dispatcher único. Cada membro vira um bloco dentro do dispatcher; tail calls a outros membros viram store de args + set de `current_id` + branch de volta. `is_even` / `is_odd` com 1M iterações rodam em stack constante.
- **Defers emitidos em tail calls**: `return self(...)` em TCO emite os defers pendentes antes do branch de volta. Cada iteração da recursão re-executa o corpo, re-empilhando seus defers.
- **`@safe`** — null check opt-in em `MemberExpr` e `IndexExpr`.
- **`@macro`** — expansão de AST em compile-time.

#### Bugs corrigidos (parser/codegen)
- **`@attrs` sobrescritos como tuples**.
- **Macros malformadas não falhavam**.
- **SCC dispatcher sem `defer_stack`**.

### Mudado

- **`codegen/codegen.py`**: novos métodos `_compute_tail_call_sccs`, `_can_dispatcher`, `_materialize_scc_dispatcher`, `_validate_macro`, `_infer_arg_type_lumina`, `_infer_type_map_lumina`. Novo módulo `codegen/expressions/macros.py`.
- **`codegen/expressions/members.py`**: `visit_MemberExpr` e `visit_IndexExpr` ganharam branch `_safe_mode`.
- **`parser/parser.py`**: removido o override `decl.attrs = attrs` em `parse()`.

---

## [Unreleased — Sprints 7a a 8a]

### Adicionado

#### Linguagem
- **Genéricos aninhados** (`Box<T>` como parâmetro).
- **`nil`** — null pointer C-style.
- **`defer` com escopo de bloco** (breaking change).
- **Multi-pattern** em `match`: `case 1 | 2 | 3:`.
- **Wildcard `_`**.
- **Variantes bare de enum**.
- **TCO (Tail Call Optimization)** para self-recursion.
- **Type check em campos de struct literal**.
- **Match guard em enum e string**.
- **`break` / `continue`** reais.
- **`assert`** aborta em runtime.
- **Short-circuit** em `and` / `or`.

#### CLI
- `--help` / `-h` / `help`.
- Exit codes propagados em `run` / `build` / `test`.
- `lumina test` respeita `[link]`.
- `[link].extra_flags` passadas ao compilar `.cpp` de FFI.

#### REPL
- REPL persistente com `:history`, `:decls`, `:clear`, `:help`.

#### Compilador
- Boehm GC ativa (`GC_init` + `GC_malloc`).
- `LLVMCodegen` com `ir.Context()` próprio.

#### LSP
- Hover com escopo qualificado.
- References/rename cientes de escopo.
- `document_symbols` com `children` por função/método.
- `read_message` valida `Content-Length`.

#### Formatter
- Preserva `@derive` e outros `@attrs`.
- Multi-pattern impresso como `case A | B:`.
- Wildcard impresso como `case _:`.

### Corrigido

21 bugs silenciosos — ver tabela no `README.md`.

### Mudado

- **`defer` com escopo de bloco** (breaking change).
- **`codegen/statements/match.py`** refatorado para `_match_chain`.
- **`semantic/statements.py`**: bindings herdam `cond_type` quando `variant_name is None`.
- **`parser/patterns.py`**: `_parse_case_pattern` acumula alternativas; string literal vira `StringExpr`.

### Removido

- `replace("GC_malloc", "malloc")` no `cmd_build`.
- `covered_variants = [c[0] for c in node.cases]`.

---

## [1.0.0] — Estado inicial

### Adicionado

#### Linguagem
- Sintaxe baseada em indentação (INDENT/DEDENT)
- Tipagem estática com inferência
- Sintaxe curta (`x := 10`), escopo de bloco lexical
- F-strings (`$"olá {nome}"`)
- Operador pipe (`5 |> dobrar |> imprimir`)
- Navegação segura (`?.`), propagação de erros (`?`), cast (`as`)
- Slicing (`s[1..4]`, `arr[..3]`, `arr[2..]`, `arr[..]`)
- Bitwise (`&`, `|`, `^`, `~`, `<<`, `>>`)
- `switch`/`case`/`default`
- `defer`, `assert`
- Generics com monomorphization (`<T>`)
- Traits com métodos padrão
- Pattern matching com binding e guard
- Enum multi-payload
- `Option<T>` e `NoneExpr`
- `comptime` (constant folding)
- Globais mutáveis (`mut X = 0`)
- Lambdas (inline e com bloco)
- Operator overloading (`__add__`, `__eq__`)
- `@derive(Eq, PartialEq, Debug, Display, Clone, Default)`

#### Standard Library (bootstrapped em Lumina)
- `std/prelude` (`Option`, `Result`), `std/math`, `std/str`, `std/time`, `std/fs`, `std/alloc`
- `std/vector`, `std/map`, `std/set`, `std/deque`, `std/list`, `std/iter`
- `std/test`, `std/log`
- `std/channel`, `std/async`, `std/async_fs`, `std/epoll`, `std/net`, `std/http`
- `std/json`, `std/sqlite`, `std/raylib`

#### Compilador
- Lexer com comentários preservados (`#`, `/* */`)
- Parser com `@attrs`, slices, patterns
- Análise semântica com `@derive`, traits, exaustividade
- Codegen LLVM IR com globais mutáveis, cross-target
- Cross-compile (`--target`): aarch64, armv7, riscv64, i386, WASM
- `-O0` / `-O2` / `-O3` + DWARF debug info
- Build incremental com cache
- FFI com C/C++ (`[link]`)

#### CLI
- `lumina new`, `build`, `run`, `check`, `test`, `clean`, `doc`, `install`, `bind`, `fmt`, `repl`, `jit`, `playground`
- `--error-format=json` (pipe-safe)
- `[link]` com `libs`, `extra_objects`, `target`, `extra_flags`

#### Ferramental
- Extensão VS Code com syntax highlight (TextMate) e LSP
- LSP: autocomplete, hover, go-to-definition, references, rename, outline, semantic tokens, diagnostics
- Web Playground (JIT)
- Auto-formatter preservando comentários leading
- **153 testes** (pytest) + **28 validações** standalone (`run_tests.py`)

[Unreleased]: https://github.com/adamgabriel701/Lumina/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/adamgabriel701/Lumina/releases/tag/v1.0.0