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
# Todos os testes (267)
pytest tests/ -v

# Só um arquivo
pytest tests/test_tco.py -v

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
fix(parser): @attrs como strings em Function
docs: atualiza README + CHANGELOG
test(tco): adiciona testes para is_even/is_odd 1M
refactor(match): unifica em _match_chain
chore: atualiza dependências
```

Escopos comuns: `lexer`, `parser`, `semantic`, `codegen`, `cli`, `lsp`, `repl`, `docs`.

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

## Licença

MIT. Ao contribuir, você concorda com os termos da [LICENSE](../LICENSE).
```

---

## 🔨 Commit

```bash
git add README.md CHANGELOG.md docs/

git commit -m "docs: atualiza README/CHANGELOG + cria docs/ navegável

README.md:
  - Badge: 249 → 267 testes
  - Tabela de features: +SCC TCO, @safe, @macro, defers em TCO
  - Tabela de bugs: +SCC sem defer_stack, @attrs como tuples
  - Tabela de testes: +test_tco_mutual (6), test_safe_mode (6),
    test_macros (6)
  - Exemplos: @safe, @macro, mutual TCO, nil, Box<T>, defer escopo
  - Roadmap: 48 concluídos
  - Link para docs/

CHANGELOG.md:
  - [Unreleased]: nova seção com Sprints 8c, 8d, 9a, 9b + fixes
  - [Unreleased-Sprints 7a-8a]: seção anterior consolidada

docs/ (novo):
  - README.md — índice navegável
  - guia-rapido.md — instalação, primeiros programas, CLI
  - linguagem.md — sintaxe, tipos, controle, patterns, @attrs
  - stdlib.md — módulos std/* completos
  - ferramental.md — CLI, REPL, formatter, LSP, testes, playground
  - internals.md — arquitetura do compilador, pipeline, como estender
  - contributing.md — setup, fluxo de PR, adicionar testes"

git push origin main
