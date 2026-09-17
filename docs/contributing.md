# 🤝 Contributing

## Setup

```bash
git clone https://github.com/adamgabriel701/Lumina.git
cd Lumina
pip install -e .
pip install -r requirements-dev.txt
```

Dependências de sistema:

```bash
sudo apt install -y libgc-dev clang llvm python3.11
```

## Rodar testes

```bash
# Todos os testes (325)
pytest tests/ -v

# Só um arquivo
pytest tests/test_tco.py -v
pytest tests/test_forin.py -v
pytest tests/test_tuples.py -v
pytest tests/test_lint.py -v

# Standalone (~5s)
python3 run_tests.py

# Compilar todos os exemplos
./scripts/check_examples.sh --run
```

## LSP

```bash
cd lumina-vscode
python3 -m pytest tests/test_lsp_keys.py -v
```

## Estrutura de branches

- `main` — stable
- `feature/<nome>` — nova feature
- `fix/<nome>` — correção de bug

## Fluxo de PR

1. Fork + clone
2. Branch: `git checkout -b feature/minha-feature`
3. Adicione testes (ver `tests/test_*.py`)
4. Rode `pytest tests/ -v` e `./scripts/check_examples.sh --run`
5. Commit seguindo [Conventional Commits](https://www.conventionalcommits.org/)
6. Push e abra PR

## Conventional Commits

```
feat(codegen): TCO para mutual recursion via SCC dispatcher
feat(parser): tuplas literais + destructuring
feat(cli): lumina lint
fix(parser): @attrs como strings em Function
fix(codegen): bitcast para impl Box<T> em Box<int>
docs: atualiza README + CHANGELOG
test(forin): adiciona testes para `for x in arr`
refactor(match): unifica em _match_chain
chore: atualiza dependências
```

Escopos comuns: `lexer`, `parser`, `semantic`, `codegen`, `cli`, `lint`, `lsp`, `repl`, `docs`.

## Adicionar testes

Coloque em `tests/test_<área>.py`. Use `subprocess` para rodar `lumina_cli`:

```python
def _run(src, timeout=30):
    with tempfile.NamedTemporaryFile("w", suffix=".lm", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        r1 = subprocess.run(
            [sys.executable, "-m", "lumina_cli", "build", path],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=timeout,
        )
        assert r1.returncode == 0, f"Build falhou:\n{r1.stdout}\n{r1.stderr}"
        binary = path[:-3]
        r2 = subprocess.run([binary], capture_output=True, text=True)
        return r2.stdout, r2.returncode
    finally:
        for p in (path, path[:-3] + ".ll", path[:-3]):
            if os.path.exists(p):
                os.remove(p)


def test_minha_feature():
    out, rc = _run("fn main() -> int:\n    print(42)\n    return 0\n")
    assert "42" in out
```

## Adicionar exemplos

`examples/<nome>.lm`. Se não terminar sozinho (servidor, socket), adicione em `tests/features/skip.txt`.

Se tiver output esperado, crie `examples/<nome>.expected`:

```
linha 1
linha 2
```

## Adicionar builtins

Em `lumina/builtins.py::BUILTIN_FUNCTIONS`:

```python
BUILTIN_FUNCTIONS = frozenset({
    "print", "input", ..., "meu_novo_builtin",
})
```

E o branch no codegen em `codegen/expressions/calls.py::codegen_user_call`:

```python
if func_name == "meu_novo_builtin":
    # geração LLVM
    ...
```

Se o builtin retorna valor, adicione também em `semantic/statements.py::BUILTIN_RET` para o `VarDecl` inferir o tipo corretamente.

## Adicionar módulos da stdlib

Crie `std/<nome>.lm` em Lumina. Consumido via `import "std/<nome>"`.

## Estilo

- **Python**: PEP 8. Nomes em snake_case.
- **Lumina**: 4 espaços de indentação. Nomes em snake_case.
- **Testes**: 1 assert por teste quando possível.

## Reportar bugs

Abra uma [issue](https://github.com/adamgabriel701/Lumina/issues) com:

1. Arquivo `.lm` mínimo que reproduz
2. Comando exato (`lumina run foo.lm`)
3. Output esperado vs. obtido
4. Versão: `lumina --help`

## Áreas que precisam de ajuda

Ver [`README.md` → Roadmap](../README.md#-roadmap). Em especial:

- **Safe-by-default global** — generalizar `@safe` para todos os MemberExpr
- **Macros multi-statement** — expandir corpo com múltiplos statements
- **Self-hosting** — compilar o próprio compilador em Lumina
- **Package registry** — `lumina publish` + index JSON
- **Code actions no LSP** — quick fixes (sugestão de `@derive` quando `==` falha)
- **Inlay hints no LSP** — `: int` fantasma em `let x = 10`
- **Genéricos reais** — `Result<T, E>`, `Vector<T>` funcional com tipo params

## Licença

MIT. Ao contribuir, você concorda com os termos da [LICENSE](../LICENSE).
