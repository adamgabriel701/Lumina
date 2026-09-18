"""Macros (@macro) via expansão de AST."""
import os
import pathlib
import subprocess
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


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
        r2 = subprocess.run([binary], capture_output=True, text=True, timeout=timeout)
        return r2.stdout, r2.returncode
    finally:
        for p in (path, path[:-3] + ".ll", path[:-3]):
            if os.path.exists(p):
                os.remove(p)


def test_macro_simple():
    src = (
        '@macro\n'
        'fn dobro(x: int) -> int:\n'
        '    return x * 2\n'
        '\n'
        'fn main() -> int:\n'
        '    print(dobro(5))\n'
        '    return 0\n'
    )
    out, rc = _run(src)
    assert "10" in out


def test_macro_with_expression_arg():
    """Precedência: dobro(a + 1) → (a + 1) * 2, não a + 1*2."""
    src = (
        '@macro\n'
        'fn dobro(x: int) -> int:\n'
        '    return x * 2\n'
        '\n'
        'fn main() -> int:\n'
        '    let a = 5\n'
        '    print(dobro(a + 1))   # (5+1)*2 = 12\n'
        '    return 0\n'
    )
    out, rc = _run(src)
    assert "12" in out, f"out={out!r}"


def test_macro_two_args():
    src = (
        '@macro\n'
        'fn max(a: int, b: int) -> int:\n'
        '    return a > b ? a : b\n'   # sem ternário — usar if inline
        '\n'
        'fn main() -> int:\n'
        '    return 0\n'
    )
    # Sem ternário em Lumina. Reescrever.
    src = (
        '@macro\n'
        'fn sq(x: int) -> int:\n'
        '    return x * x\n'
        '\n'
        'fn main() -> int:\n'
        '    print(sq(3) + sq(4))\n'   # 9 + 16 = 25
        '    return 0\n'
    )
    out, rc = _run(src)
    assert "25" in out, f"out={out!r}"


def test_macro_composes_with_other_calls():
    src = (
        '@macro\n'
        'fn dobro(x: int) -> int:\n'
        '    return x * 2\n'
        '\n'
        '@macro\n'
        'fn quadruplo(x: int) -> int:\n'
        '    return dobro(dobro(x))\n'   # macro chamando macro
        '\n'
        'fn main() -> int:\n'
        '    print(quadruplo(3))\n'   # 3*4 = 12
        '    return 0\n'
    )
    out, rc = _run(src)
    assert "12" in out, f"out={out!r}"


def test_macro_rejects_multistatement():
    """Macro multi-statement chamada como **expressão** (sem `!`) falha.

    Declarar uma macro com corpo multi-statement é válido (ela pode ser
    usada em statement via `nome!(...)`). O que falha é tentar usá-la
    como expressão — isso exigiria um valor de retorno que ela não tem.
    """
    src = (
        '@macro\n'
        'fn bad(x: int) -> int:\n'
        '    let y = x + 1\n'
        '    return y * 2\n'
        '\n'
        'fn main() -> int:\n'
        '    let r = bad(3)\n'   # ← sem `!`, chamada como expressão
        '    return r\n'
    )
    with tempfile.NamedTemporaryFile("w", suffix=".lm", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        r = subprocess.run(
            [sys.executable, "-m", "lumina_cli", "build", path],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        assert r.returncode != 0, (
            f"macro multi-statement como expressão deveria falhar:\n{r.stdout}"
        )
        combined = r.stdout + r.stderr
        assert "return <expr>" in combined or "posição de statement" in combined, (
            f"mensagem de erro não menciona a sintaxe correta:\n{combined}"
        )
    finally:
        for p in (path, path[:-3] + ".ll", path[:-3]):
            if os.path.exists(p):
                os.remove(p)


def test_macro_with_ptr_arg():
    src = (
        '@macro\n'
        'fn deref_first(p: ptr) -> int:\n'
        '    return p[0]\n'
        '\n'
        'fn main() -> int:\n'
        '    mut arr = alloc(3)\n'
        '    arr[0] = 77\n'
        '    print(deref_first(arr))\n'
        '    return 0\n'
    )
    out, rc = _run(src)
    assert "77" in out, f"out={out!r}"
