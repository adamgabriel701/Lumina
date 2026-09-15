import pytest
from lumina.lexer import Lexer
from lumina.parser import Parser
from lumina.semantic import SemanticAnalyzer
from lumina.errors import LuminaError


def _analyze(src):
    tokens = Lexer(src).tokenize()
    ast = Parser(tokens, "<test>", src).parse()
    SemanticAnalyzer("<test>", src).analyze(ast)


def test_var_decl_type_mismatch():
    src = 'fn main() -> int:\n    let x: int = "texto"\n    return 0\n'
    with pytest.raises(LuminaError, match="Tipo inválido em declaração de 'x'"):
        _analyze(src)


def test_var_decl_ok():
    src = 'fn main() -> int:\n    let x: int = 10\n    return 0\n'
    _analyze(src)


def test_return_type_mismatch():
    src = 'fn f() -> int:\n    return "texto"\n\nfn main() -> int:\n    return 0\n'
    with pytest.raises(LuminaError, match="Tipo inválido em retorno de 'f'"):
        _analyze(src)


def test_int_to_float_promotion():
    src = 'fn main() -> int:\n    let x: float = 10\n    return 0\n'
    _analyze(src)


def test_if_condition_must_be_bool():
    src = 'fn main() -> int:\n    if 5:\n        return 1\n    return 0\n'
    with pytest.raises(LuminaError, match="Condição de 'if'"):
        _analyze(src)


def test_assign_type_mismatch():
    src = (
        'fn main() -> int:\n'
        '    x := 10\n'              # := é mutável
        '    x = "texto"\n'
        '    return 0\n'
    )
    with pytest.raises(LuminaError, match="Tipo inválido em atribuição"):
        _analyze(src)


def test_while_condition_must_be_bool():
    src = (
        'fn main() -> int:\n'
        '    let i = 0\n'
        '    while 5:\n'
        '        i = i + 1\n'
        '    return 0\n'
    )
    with pytest.raises(LuminaError, match="Condição de 'while'"):
        _analyze(src)


def test_assert_must_be_bool():
    src = 'fn main() -> int:\n    assert(5)\n    return 0\n'
    with pytest.raises(LuminaError, match="Condição de 'assert'"):
        _analyze(src)