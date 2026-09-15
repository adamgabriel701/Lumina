# tests/test_cli.py
import subprocess
import sys
import os
import glob

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_cli(*args, cwd=None):
    """Executa o comando `lumina` e retorna o resultado.

    Passa PYTHONPATH=REPO_ROOT pra que o módulo lumina_cli seja
    encontrado mesmo quando cwd é um diretório temporário.
    """
    cmd = [sys.executable, "-m", "lumina_cli.main", *args]
    env = {**os.environ, "PYTHONPATH": REPO_ROOT}
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env)


def test_new_and_build(tmp_path):
    """Testa o fluxo: new -> build -> run"""

    proj_name = "meu_teste_proj"
    result = run_cli("new", proj_name, cwd=tmp_path)
    assert result.returncode == 0, f"Erro em 'lumina new': {result.stderr}"

    proj_dir = os.path.join(tmp_path, proj_name)
    assert os.path.exists(os.path.join(proj_dir, "main.lm"))
    assert os.path.exists(os.path.join(proj_dir, "lumina.toml"))

    result = run_cli("build", cwd=proj_dir)
    assert result.returncode == 0, f"Erro em 'lumina build': {result.stderr}"
    assert "Build concluído" in result.stdout

    binary_path = os.path.join(proj_dir, proj_name)
    assert os.path.exists(binary_path), "Binário nativo não encontrado"

    proc = subprocess.run([binary_path], capture_output=True, text=True)
    assert proc.returncode == 0
    assert "Hello from meu_teste_proj!" in proc.stdout


def test_fmt(tmp_path):
    """Testa se o formatter não quebra o código válido"""
    code = """fn main() -> int:
    print("Teste")
    return 0
"""
    file_path = tmp_path / "test_fmt.lm"
    file_path.write_text(code)

    result = run_cli("fmt", str(file_path))
    assert result.returncode == 0, f"Erro em 'lumina fmt': {result.stderr}"
    assert "formatado com sucesso" in result.stdout

    assert "fn main() -> int:" in file_path.read_text()


def test_unknown_command():
    """Testa se a CLI rejeita comandos inválidos e retorna exit code 1"""
    result = run_cli("comando_inexistente")
    assert result.returncode == 1
    assert "Comando desconhecido" in result.stdout


def test_smoke_tests_examples():
    """Compila todos os arquivos da pasta examples/ para garantir que nenhum commit quebre o codegen."""
    examples = glob.glob(os.path.join(REPO_ROOT, "examples/*.lm"))
    assert len(examples) > 0, "Nenhum exemplo encontrado"

    for file in examples:
        result = run_cli("build", file, cwd=REPO_ROOT)
        assert result.returncode == 0, f"Erro ao compilar {file}:\n{result.stderr}"


# ============================================================
# Validar output exato de uncertain_features.lm
# ============================================================
EXPECTED_LINES = [
    "1. Slicing: ell",
    "2. Array indexing:",
    "3. Pipe: 10",
    "4. Pipe encadeado: 20",
    "5. Safe nav: 0",
    "6. Propagate: 10",
    "Segunda",
    "Ok: 5",
    "9. Short decl: 42",
    "10. Dentro do if: 100",
    "11. Início",
    "11. Defer executado",
    "11. Fim",
    "12. Assert OK",
    "13. Nome: João, Idade: 30",
    "14. Generics int: 10",
    "14. Generics float: 3.140000",
    "15. Valor profundo: 99",
    "16. Match guard: Grande",
    "17. Valor: 42",
    "18. Par: 10 20",
    "19. Cast: 10 3",
    "20. Ponteiro: 42",
    "21. Lambda: 20",
    "22. Lambda bloco: 30",
    "23. Trait default OK",
    "24. Comando: run",
    "=== Fim dos testes ===",
]


def test_uncertain_features():
    """Roda tests/uncertain_features.lm e valida cada linha esperada no output."""
    # Caminho RELATIVO — o cmd_build deriva o nome do binário do entry_file,
    # e o cmd_run executa "./<binário>". Caminho absoluto quebra o "./".
    target = "tests/uncertain_features.lm"

    run_cli("clean", cwd=REPO_ROOT)

    result = run_cli("run", target, cwd=REPO_ROOT)
    output = result.stdout + result.stderr

    assert result.returncode == 0, f"Compilação/execução falhou:\n{output}"

    missing = [line for line in EXPECTED_LINES if line not in output]
    assert not missing, (
        f"{len(missing)} linha(s) esperadas não apareceram:\n"
        + "\n".join(f"  · {m}" for m in missing)
        + f"\n\nOutput completo:\n{output}"
    )