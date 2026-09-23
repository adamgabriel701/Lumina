# 🐛 Bugs corrigidos

Lista completa de bugs silenciosos corrigidos no compilador. Todos passavam pelo CI original porque os testes só exercitavam parser/semantic — não runtime. Cada um tem teste de regressão.

**Sintoma** = o que o usuário via. **Correção** = o que mudou no código. **Teste** = arquivo de regressão.

---

## Runtime

| Bug | Sintoma | Correção | Teste |
|---|---|---|---|
| `break` / `continue` no-op | `for i in 0..100: if i == 5: break` continuava até 100 | `loop_stack` com branch para `end_bb`/`inc_bb` | `test_runtime_bugs.py` |
| `assert` sem efeito | `assert(1 == 2)` imprimia a linha seguinte e saía com 0 | `fflush(NULL)` + `abort()` + `unreachable` | `test_runtime_bugs.py` |
| `defer` inline | `defer print("b")` rodava imediatamente | `defer_stack` por função | `test_runtime_bugs.py` |
| `defer` em `if` não tomado rodava | `if false: defer print("x")` imprimia `x` | Escopo de bloco | `test_defer_scope.py` |
| `defer` em TCO era ignorado | `return self(...)` pulava defers | `_emit_all_defers()` antes do branch de TCO | `test_tco.py` |
| `and` / `or` sem short-circuit | `x != 0 and 10/x > 1` causava SIGFPE | Basic blocks + `phi i1` | `test_runtime_bugs.py` |

## Codegen

| Bug | Sintoma | Correção | Teste |
|---|---|---|---|
| Formatter apagava `@derive` | `@derive(Eq, Debug)` removido no `lumina fmt` | `_format_attrs()` | `test_runtime_bugs.py` |
| Boehm GC nunca ativava | `-lgc` era decorativo | `GC_malloc` + `call GC_init()` | `test_gc.py` |
| Match guard em enum nunca casava | `case Circle(r) if r > 10:` sempre pulava | 4 blocos por case; bind ANTES do guard | `test_match_guard_enum.py` |
| Match guard em str ignorado | `_codegen_match_with_guard` não testava voidptr | Branch de `strcmp` para voidptr | `test_match_guard_str.py` |
| Self-binding declarava `int` fixo | `case s if s.contains("x")` falhava | `variant_name is None` antes de `isinstance(binding, list)` | `test_match_guard_str.py` |
| String literal virava self-binding | `case "build":` casava qualquer string | Parser envolve literal em `StringExpr` | `test_match_guard_str.py` |
| `covered_variants` explodia com multi-pattern | `unhashable type: list` | Achata listas, ignora `None`, honra wildcard | `test_multi_pattern.py` |
| `struct` recompilado no REPL | `P is already defined` | Cada `LLVMCodegen` cria seu próprio `ir.Context()` | `cli/test_repl.py` |
| `let` em campo `int` aceitava `str` | `Ponto { x: "texto", y: 2 }` imprimia endereço | `is_assignable(field_decl_type, value_type)` por campo | `test_struct_field_types.py` |
| `Box<T>` como parâmetro não compilava | `fn put<T>(b: Box<T>, val: T)` → erro | `unify_type` + `substitute_generic` | `test_nested_generics.py` |
| LSP rename misturava escopos | Renomear `i` em `main` mexia no `i` de `helper` | `_filter_refs_for_scope` via `scope_map` | `lsp/tests/test_lsp_keys.py` |
| SCC dispatcher sem `defer_stack` | `AttributeError` em mutual TCO | Init `defer_stack` no entry + reset por membro | `test_tco_mutual.py` |
| `@attrs` sobrescritos como tuples | `@safe`/`@macro` nunca ativavam | Removido override em `parser/parser.py::parse` | `test_safe_mode.py` / `test_macros.py` |
| `read_file()` sem null check | segfault quando arquivo não existe | `phi` retorna string vazia se `fopen == NULL` | `examples/database.lm` |
| `free()` rejeitava `i64*` | `TypeError: i8* != i64*` | `bitcast` antes do call | `test_escape_analysis.py` |
| `chr`/`atoi` sem branch no codegen | retornavam `0` sempre | Branches dedicados em `calls.py` | `test_std_result.py` |
| `SliceExpr` virava `ptr` | `s[..3] == "abc"` comparava endereços | Infere tipo da fonte (`str` → `str`) | `examples/string_methods_test.lm` |
| `bool` → `int` com `sext` | `true` virava `-1` | `zext` quando origem é `i1` | `test_codegen_bugs.py` |
| `for x in arr` perdia o `N` | loop vazio (N=0) | `array_lengths` no codegen, consultado por `_visit_for_iterable` | `test_forin.py` |
| `impl Box<T>` chamado em `Box<int>` | `%"Box"* != %"Box_int_"*` | `bitcast` para o tipo base quando cai no fallback | `test_generic_impl.py` |
| `std/result::unwrap_or` usava `default` | keyword reservada | Renomeado para `fallback` | `test_std_result.py` |
| `and_then` retornava `int` para function pointers | `_require_assignable` rejeitava `Result` | Retorna `None` (tipo desconhecido) | `test_std_result.py` |

## Semantic

| Bug | Sintoma | Correção | Teste |
|---|---|---|---|
| `lumina lint` estourava `RecursionError` | recursão mútua `_collect_vars`/`_collect_exprs` | Reescrito como `_collect` única | `test_lint.py` |
| Variante de enum com payload usada bare | `let x = Some` compilava silenciosamente | Semantic rejeita se variante tem payload | `test_enum_bare_variant.py` |
| `fn_name` usado como valor | `sort(arr, n, _cmp_asc)` → "Variável não declarada" | Semantic retorna `"fn"`, codegen bitcast p/ voidptr | `test_sort.py` |
| Indirect call com N args | `cmp(a, b)` só passava `a` | `fn_ty = i64 (i64) * n_args` | `test_sort.py` |
| `impl Box<T>:` chamando método base | `%"Box"* != %"Box_int_"*` | Bitcast no `codegen_method_call` fallback | `test_generic_impl.py` |

## Stdlib / Builtins

| Bug | Sintoma | Correção | Teste |
|---|---|---|---|
| `stdin`/`stdout`/`stderr` fora de `BUILTIN_RET` | `std/io.lm` falhava com "Tipo inválido para parâmetro 'stream': esperado 'str', obteve 'int'" | `BUILTIN_RET` centralizado em `lumina/builtins.py` | `test_std_io.py` |
| `extern fn fgets` colidia com builtin | `TypeError: Type of #2 arg mismatch: i64 != i32` | `generate_module` pula `ExternDecl` que colide com builtin | `test_std_io.py` |
| `getchar` retornava `i32` | `ret i32 %getchar_call` não casava com `-> int` | `sext i32 → i64` em `calls.py` | `test_std_io.py` |
| `visit_ReturnStmt` sem `iN → i64` | qualquer builtin que devolvesse i32 quebrava o ret | Normalização defensiva `iN → i64` | `test_std_io.py` |
| `"\n"` em fonte virava 2 bytes literais | `fputs("\n", out)` imprimia `\n` literal | Lexer processa escapes em compile-time | `test_std_io.py` / `test_lexer.py` |
| `read_line` com `buf[n-1] = 0` | newline não era removido da linha lida | Loop explícito em `std/io.lm` | `test_std_io.py` |
| `_handle_indent` não era chamado | todos os blocos indentados falhavam com "Esperado INDENT, mas encontrei X" | Restaurada chamada em `tokenize()` | `test_lexer.py::test_indent_dedent` |

## Closures & Macros

| Bug | Sintoma | Correção | Teste |
|---|---|---|---|
| Closure com captura como callback segfaultava | `sort_by(arr, n, fn(a, b): (b-a)*mult)` passava bloco `{fn_ptr, env_ptr}` como fn ptr cru | Tipo `fn` unificado em fat pointer; `_call_closure` em toda indireta | `test_sort.py::test_sort_closure_captures` |
| `_validate_macro` rejeitava declaração multi-statement | macro multi-statement não podia ser declarada | Validação só verifica corpo não-vazio; exigência de `return <expr>` fica no call site de expressão | `test_macro_stmts.py` |
| `parse_struct` usava `expect(IDENT)` no tipo do campo | `struct S: cb: fn(int) -> int` falhava com "Esperado IDENT, mas encontrei FN ('fn')" | `parse_type()` (mesmo helper de params/enums/traits) | `test_fn_struct_fields.py` |

## Generics (sessão de fechamento)

| Bug | Sintoma | Correção | Teste |
|---|---|---|---|
| `get_llvm_param_type` inconsistente | `TypeError: cannot store %"Box_int_" to %"Box_int_"**` em `fn get(b: BI)` | `get_llvm_type` força monomorphização antes de checar `struct_types`; structs sempre devolvem ponteiro | `test_generic_type_alias.py::test_generic_alias_inside_fn_sig` |
| `impl Box<T>:` registrava `Box_T__get` | `Método 'get' não implementado para 'Box'` | Parser normaliza `impl Box<T>:` → nome base `Box` (se args são todos type params únicos maiúsculos) | `test_impl_box_generic.py::test_generic_impl_still_works_as_fallback` |
| Semantic procurava `Box_get`, existia `Box_int__get` | `Método 'get' não implementado` mesmo com `impl Getter for Box<int>` | Lookup tenta nome completo (`mangle_method`) e cai para base | `test_impl_box_generic.py::test_impl_trait_for_box_int` |
| `struct_defs["Custom<int>"]` não registrado | `KeyError: 'Custom<int>'` em `_construct_enum` | `get_or_create_monomorphized_{struct,enum}` registra sob chave canônica **e** mangled | `test_generic_enums.py` |
| `visit_VarDecl` forçava tipo default de enum | `bitcast Custom_int_* → Custom_int_` inválido em `let c = Wrap(42)` | Se `val.type` já é ponteiro para struct identificada, usa `val.type` como tipo do slot | `test_generic_enums.py::test_generic_enum_str_payload` |

## CLI

| Bug | Sintoma | Correção | Teste |
|---|---|---|---|
| CLI engolia exit code | `lumina run` sempre saía com 0 | `cmd_run` propaga exit | `cli/test_exit_codes.py` |
| `test` com falhas saía com 0 | `lumina test` retornava 0 | `cmd_test` retorna nº de falhas | `cli/test_exit_codes.py` |
| `--help` caía em "comando desconhecido" | — | `main()` trata `-h`/`--help`/`help`/sem args | `cli/test_exit_codes.py` |
| `_compile_extra_objects` ignorava `extra_flags` | `.cpp` sem `-DFOO=42` | Passa `linker_extra_flags` para clang/clang++ | `cli/test_build.py` |

---

## Bugs identificados (não corrigidos)

Bugs encontrados durante o desenvolvimento do linker próprio
(`lumina-ld`). Nenhum é do linker — o linker produziu ELF válido em
todos os casos. São bugs do **codegen** que ficaram invisíveis enquanto
o `clang` + `glibc` faziam o link, porque forneciam um `_start` que
fazia `exit_group` no retorno de `main` e uma stack que crescia até
8 MB.

| Bug | Sintoma | Causa | Onde | Impacto |
|---|---|---|---|---|
| `main` sem `ret` após tail print | `./chip8` segfaulta em `add %al,(%rax)` num endereço de padding | Codegen emite o último `call printf` como tail call, mas não emite `ret` depois. O `call` retorna para o byte seguinte ao último `call`, que não existe no `.text` do `.o` — cai no padding zeros entre `.text` e a próxima seção | `lumina/codegen/function_body.py` ou `statements/flow.py` (`_try_tail_call`, caso "último statement é call") | Todo exemplo que termina com `print()` na posição tail crasharia com `--linker=self`. Com clang+glibc funciona por sorte |
| `alloca` dentro de loop estoura stack | `./gc_test` (1M iterações de `let lixo = "..."`) segfaulta com ~250K iterações; `ulimit -s unlimited` faz funcionar | Codegen emite `alloca` para `lixo` dentro do corpo do loop, não uma única vez no entry block. Cada iteração empilha mais um slot, esgotando os 8 MB de stack padrão | `lumina/codegen/statements/var_decl.py::visit_VarDecl` | Qualquer loop longo com variável local estoura stack. Não afeta programas curtos |

### Correções propostas

**Bug 1 (`main` sem `ret`)**: no `_try_tail_call`, quando o último statement
da função é uma chamada de função, emitir `ret` no bloco `end` após o `call`.
Verificar se o retorno da função não está sendo consumido. Teste de regressão
mínimo:

```lumina
fn f() -> int:
    print("oi")
    return 0
```

com inspeção `objdump -d` para confirmar `ret` presente.

**Bug 2 (`alloca` em loop)**: hoistar todos os `alloca` para o entry block
da função. Alternativa: usar `phi` para reutilizar o slot entre iterações.
A primeira abordagem é mais simples e cobre 100% dos casos.

### Como foram descobertos

Ambos só apareceram quando o `lumina-ld` passou a gerar o executável completo,
sem o `_start` do glibc e sem a stack gerenciada pelo kernel. A lista
completa de bugs do compilador (todos corrigidos) está nas seções anteriores
deste documento — esses dois são os únicos em aberto até a data de hoje.

### Testes de regressão (quando corrigidos)

Adicionar em `tests/test_codegen_bugs.py`:

```python
def test_main_ends_with_ret():
    """Regressão para chip8: main com print em tail position deve ter ret."""
    src = '''
fn main() -> int:
    print("oi")
    return 0
'''
    # compila, desmonta, confirma que .text termina com `c3` (ret)
    ...

def test_loop_locals_no_stack_growth():
    """Regressão para gc_test: 1M iterações não podem estourar a stack."""
    src = '''
fn main() -> int:
    mut i = 0
    while i < 1000000:
        let lixo = "Lixo " + i
        i += 1
    return 0
'''
    # compila e roda com ulimit -s 8192 (default); deve retornar 0
    ...
```