import os
import ctypes
import ctypes.util

from llvmlite import binding as llvm

from lumina.ast import (
    Function, VarDecl, AssignStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt,
    NumberExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr,
    MemberExpr, IndexExpr, ImportStmt
)
from lumina.lexer import Lexer
from lumina.parser import Parser
from lumina.semantic import SemanticAnalyzer
from lumina.codegen import LLVMCodegen
from lumina.errors import LuminaError

from .utils import (
    Color, paint, cprint, info, success, warn, error, step, header, arrow,
    STD_DIR, get_cache_hash
)


def parse_module(filename, current_stack=None):
    abs_path = os.path.abspath(filename)
    if current_stack is None:
        current_stack = set()
    if abs_path in current_stack:
        raise LuminaError(
            f"Importação circular detectada envolvendo '{filename}'.",
            filename, 0, 0, ""
        )

    current_stack.add(abs_path)
    resolved_ast = []

    # Injeta o Prelude automaticamente se for o arquivo principal
    if len(current_stack) == 1:
        prelude_path = os.path.join(STD_DIR, "prelude.lm")
        if os.path.exists(prelude_path):
            with open(prelude_path, "r") as f:
                prelude_code = f.read()
            lexer = Lexer(prelude_code)
            tokens = lexer.tokenize()
            parser = Parser(tokens, prelude_path, prelude_code)
            prelude_ast = parser.parse()
            resolved_ast.extend(prelude_ast)

    with open(filename, "r") as f:
        code = f.read()

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, filename, code)
    ast = parser.parse()

    for node in ast:
        if isinstance(node, ImportStmt):
            if node.filename.startswith("std/"):
                clean_name = node.filename.replace("std/", "")
                if clean_name.endswith(".lm"):
                    clean_name = clean_name[:-3]
                std_path = os.path.join(STD_DIR, clean_name + ".lm")
                imported_ast = parse_module(std_path, current_stack)
            elif os.path.exists(node.filename if node.filename.endswith(".lm") else node.filename + ".lm"):
                imported_path = node.filename if node.filename.endswith(".lm") else node.filename + ".lm"
                imported_ast = parse_module(imported_path, current_stack)
            else:
                mod_path = os.path.join("lumina_modules", node.filename)
                if not mod_path.endswith(".lm"):
                    mod_path += ".lm"
                if not os.path.exists(mod_path):
                    raise LuminaError(
                        f"Módulo '{node.filename}' não encontrado.",
                        filename, 0, 0, code
                    )
                imported_ast = parse_module(mod_path, current_stack)
            arrow(f"--> Importando módulo: {paint(node.filename, Color.BOLD)}")
            resolved_ast.extend(imported_ast)
        else:
            resolved_ast.append(node)

    current_stack.remove(abs_path)
    return resolved_ast


def compile_lumina(filename, output_file="output.ll", use_cache=True, is_wasm=False):
    cache_dir = ".lumina_cache"
    cache_file = os.path.join(cache_dir, get_cache_hash(filename) + ".ll") if use_cache else None

    if use_cache and os.path.exists(cache_file):
        info("⚡ Usando cache de compilação (.lumina_cache)...")
        with open(cache_file, "r") as f:
            llvm_ir = f.read()
        with open(output_file, "w") as f:
            f.write(llvm_ir)
        return llvm_ir

    header("1. Análise Léxica e Sintática")
    try:
        ast = parse_module(filename)
    except LuminaError as e:
        error(e)
        return None

    header("2. Análise Semântica")
    with open(filename, "r") as f:
        source_code = f.read()
    analyzer = SemanticAnalyzer(filename, source_code)
    try:
        analyzer.analyze(ast)
    except LuminaError as e:
        error(e)
        return None

    header("3. Geração de Código LLVM IR")
    codegen = LLVMCodegen()
    codegen.escapes = analyzer.escapes
    codegen.is_wasm = is_wasm  # NOVO: Passa a flag para o codegen alterar o tipo do main()
    llvm_ir = codegen.generate_module(ast)

    with open(output_file, "w") as f:
        f.write(llvm_ir)

    if use_cache:
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_file, "w") as f:
            f.write(llvm_ir)

    return llvm_ir


def run_jit(llvm_ir, cli_args):
    header("Execução JIT (Just-In-Time)")
    try:
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
    except Exception:
        pass

    lib_c_path = ctypes.util.find_library('c')
    if lib_c_path:
        llvm.load_library_permanently(lib_c_path)

    mod = llvm.parse_assembly(llvm_ir)
    mod.verify()
    target = llvm.Target.from_default_triple()
    tm = target.create_target_machine()
    engine = llvm.create_mcjit_compiler(mod, tm)
    engine.finalize_object()
    engine.run_static_constructors()

    func_ptr = engine.get_function_address("main")
    cfunc = ctypes.CFUNCTYPE(
        ctypes.c_int64, ctypes.c_int32, ctypes.POINTER(ctypes.c_char_p)
    )(func_ptr)

    full_args = ["lumina_program"] + cli_args
    argc = len(full_args)
    argv = [arg.encode('utf-8') for arg in full_args]

    info("Executando...\n")
    ret = cfunc(argc, (ctypes.c_char_p * len(argv))(*argv))
    ctypes.CDLL(None).fflush(None)
    print()
    info(f"[JIT] Programa finalizado com exit code: {paint(str(ret), Color.BOLD + Color.SUCCESS)}")


# --- Auto-Formatter (AST printer usado por `lumina fmt`) ---
def format_node(node, indent_level=0):
    indent = "    " * indent_level

    if isinstance(node, Function):
        params = ", ".join([f"{p[0]}: {p[1]}" for p in node.params])
        ret = f" -> {node.return_type}" if node.return_type != "void" else ""
        s = f"{indent}fn {node.name}({params}){ret}:\n"
        for stmt in node.body:
            s += format_node(stmt, indent_level + 1)
        return s

    elif isinstance(node, VarDecl):
        mut = "mut " if node.is_mutable else "let "
        typ = f": {node.var_type}" if node.var_type else ""
        val = f" = {format_node(node.value, 0)}" if node.value else ""
        return f"{indent}{mut}{node.name}{typ}{val}\n"

    elif isinstance(node, AssignStmt):
        target = format_node(node.target, 0)
        val = format_node(node.value, 0)
        return f"{indent}{target} = {val}\n"

    elif isinstance(node, ReturnStmt):
        vals = ", ".join([format_node(v, 0) for v in node.values])
        return f"{indent}return {vals}\n"

    elif isinstance(node, IfStmt):
        cond = format_node(node.condition, 0)
        s = f"{indent}if {cond}:\n"
        for stmt in node.then_body:
            s += format_node(stmt, indent_level + 1)
        if node.else_body:
            s += f"{indent}else:\n"
            for stmt in node.else_body:
                s += format_node(stmt, indent_level + 1)
        return s

    elif isinstance(node, WhileStmt):
        cond = format_node(node.condition, 0)
        s = f"{indent}while {cond}:\n"
        for stmt in node.body:
            s += format_node(stmt, indent_level + 1)
        return s

    elif isinstance(node, ForStmt):
        start = format_node(node.start, 0)
        end = format_node(node.end, 0)
        s = f"{indent}for {node.var_name} in {start}..{end}:\n"
        for stmt in node.body:
            s += format_node(stmt, indent_level + 1)
        return s

    elif isinstance(node, NumberExpr):
        if indent_level > 0:
            return f"{indent}{node.value}\n"
        return node.value

    elif isinstance(node, StringExpr):
        if indent_level > 0:
            return f"{indent}\"{node.value}\"\n"
        return f"\"{node.value}\""

    elif isinstance(node, VariableExpr):
        if indent_level > 0:
            return f"{indent}{node.name}\n"
        return node.name

    elif isinstance(node, BinaryExpr):
        left = format_node(node.left, 0)
        right = format_node(node.right, 0)
        if indent_level > 0:
            return f"{indent}{left} {node.op} {right}\n"
        return f"{left} {node.op} {right}"

    elif isinstance(node, CallExpr):
        args = ", ".join([format_node(a, 0) for a in node.args])
        if indent_level > 0:
            return f"{indent}{node.name}({args})\n"
        return f"{node.name}({args})"

    elif isinstance(node, MemberExpr):
        obj = format_node(node.obj, 0)
        if indent_level > 0:
            return f"{indent}{obj}.{node.member}\n"
        return f"{obj}.{node.member}"

    elif isinstance(node, IndexExpr):
        arr = format_node(node.array, 0)
        idx = format_node(node.index, 0)
        if indent_level > 0:
            return f"{indent}{arr}[{idx}]\n"
        return f"{arr}[{idx}]"

    return f"{indent}{str(node)}\n"