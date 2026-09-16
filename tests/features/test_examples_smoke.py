"""Compila todos os arquivos de examples/ que não estão no skip.txt.

O skip.txt (compartilhado com scripts/check_examples.sh) lista exemplos
que não são compiláveis como executáveis (bibliotecas sem main(),
exemplos que dependem de headers externos, etc.).

Antes, este teste passava por acidente: `lumina build` engolia o exit
code, então qualquer falha do linker era silenciosa. Agora que exit
codes propagam (ver tests/cli/test_exit_codes.py), precisamos respeitar
o skip.txt.
"""
import glob
import os
import pathlib


def _load_skip_list(repo_root):
    """Lê `tests/features/skip.txt` (formato: <nome>.lm [motivo])."""
    skip_file = pathlib.Path(repo_root) / "tests" / "features" / "skip.txt"
    skip = set()
    if not skip_file.exists():
        return skip

    for raw in skip_file.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # primeira palavra é o nome do arquivo
        name = line.split()[0]
        skip.add(name)
    return skip


def test_smoke_tests_examples(run_cli, repo_root):
    examples = glob.glob(os.path.join(repo_root, "examples/*.lm"))
    assert len(examples) > 0, "Nenhum exemplo encontrado"

    skip_list = _load_skip_list(repo_root)

    failures = []
    for file in examples:
        basename = os.path.basename(file)
        if basename in skip_list:
            continue

        result = run_cli("build", file)
        if result.returncode != 0:
            failures.append((basename, result.stderr))

    assert not failures, (
        f"{len(failures)} exemplo(s) falharam ao compilar:\n"
        + "\n".join(f"  · {name}: {err[:200]}" for name, err in failures)
    )