"""Fixtures e constantes compartilhadas pelos testes."""
import os
import subprocess
import sys

import pytest


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="session")
def repo_root():
    return REPO_ROOT


@pytest.fixture
def run_cli():
    """Executa a CLI como subprocess.

    Passa PYTHONPATH=REPO_ROOT pra que lumina_cli seja encontrado
    mesmo quando cwd é um diretório temporário.
    """
    def _run(*args, cwd=None):
        cmd = [sys.executable, "-m", "lumina_cli.main", *args]
        env = {**os.environ, "PYTHONPATH": REPO_ROOT}
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or REPO_ROOT,
            env=env,
        )
    return _run


@pytest.fixture(scope="session")
def expected_feature_lines():
    """Linhas que DEVEM aparecer no output de uncertain_features.lm."""
    return [
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