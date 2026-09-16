"""Compila todos os arquivos de examples/."""
import glob
import os


def test_smoke_tests_examples(run_cli, repo_root):
    examples = glob.glob(os.path.join(repo_root, "examples/*.lm"))
    assert len(examples) > 0, "Nenhum exemplo encontrado"

    for file in examples:
        result = run_cli("build", file)
        assert result.returncode == 0, f"Erro ao compilar {file}:\n{result.stderr}"