"""Fluxo `lumina new` → `build` → `run`."""
import os
import subprocess


def test_new_and_build(tmp_path, run_cli):
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
