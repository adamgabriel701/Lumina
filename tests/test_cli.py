# tests/test_cli.py
import subprocess
import sys
import os
import shutil

def run_cli(*args, cwd=None):
    """Executa o comando `lumina` e retorna o resultado."""
    # Usa o executável do Python atual para invocar o módulo
    cmd = [sys.executable, "-m", "lumina_cli.main", *args]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

def test_new_and_build(tmp_path):
    """Testa o fluxo: new -> build -> run"""
    
    # 1. Cria um novo projeto na pasta temporária
    proj_name = "meu_teste_proj"
    result = run_cli("new", proj_name, cwd=tmp_path)
    assert result.returncode == 0, f"Erro em 'lumina new': {result.stderr}"
    
    proj_dir = os.path.join(tmp_path, proj_name)
    assert os.path.exists(os.path.join(proj_dir, "main.lm"))
    assert os.path.exists(os.path.join(proj_dir, "lumina.toml"))
    
    # 2. Compila o projeto
    result = run_cli("build", cwd=proj_dir)
    assert result.returncode == 0, f"Erro em 'lumina build': {result.stderr}"
    assert "Build concluído" in result.stdout
    
    # Verifica se o binário nativo foi gerado
    binary_path = os.path.join(proj_dir, proj_name)
    assert os.path.exists(binary_path), "Binário nativo não encontrado"
    
    # 3. Executa o binário para ver se funciona
    # Usamos subprocess direto pois a CLI envelopa a execução
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
    
    # O código formatado deve continuar válido
    assert "fn main() -> int:" in file_path.read_text()

def test_unknown_command():
    """Testa se a CLI rejeita comandos inválidos graciosamente"""
    result = run_cli("comando_inexistente")
    assert result.returncode == 0 # Retorna 0 mas imprime a ajuda
    assert "Comando desconhecido" in result.stdout
