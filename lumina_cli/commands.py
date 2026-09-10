import os
import re
import sys
import json
import glob
import hashlib
import subprocess
import ctypes
import ctypes.util

from lumina.ast.statements import ImportStmt

try:
    import tomllib  # Python 3.11+
except ImportError:
    tomllib = None

from llvmlite import binding as llvm

from lumina.lexer import Lexer
from lumina.parser import Parser
from lumina.semantic import SemanticAnalyzer
from lumina.codegen import LLVMCodegen
from lumina.errors import LuminaError

from .utils import (
    Color, paint, cprint, info, success, warn, error, step, header, arrow,
)
from .compiler import compile_lumina, run_jit, format_node


# ============================================================
#  new
# ============================================================
def cmd_new(project_name):
    os.makedirs(project_name, exist_ok=True)

    config = f"""[package]
name = "{project_name}"
version = "0.1.0"
entry = "main.lm"

[dependencies]
"""
    with open(os.path.join(project_name, "lumina.toml"), "w") as f:
        f.write(config)

    main_code = (
        'fn main() -> int:\n'
        f'    print("Hello from {project_name}!")\n'
        '    return 0\n'
    )
    with open(os.path.join(project_name, "main.lm"), "w") as f:
        f.write(main_code)

    success(f"✅ Projeto '{paint(project_name, Color.BOLD + Color.BRIGHT_CYAN)}' criado com sucesso (lumina.toml)!")


# ============================================================
#  install
# ============================================================
def cmd_install():
    if not os.path.exists("lumina.toml"):
        error("❌ Erro: Nenhum arquivo 'lumina.toml' encontrado no diretório atual.")
        return

    if tomllib is None:
        error("❌ Erro: tomllib não disponível. Use Python 3.11+.")
        return

    with open("lumina.toml", "rb") as f:
        config = tomllib.load(f)

    deps = config.get("dependencies", {})
    if not deps:
        info("Nenhuma dependência encontrada no lumina.toml.")
        return

    os.makedirs("lumina_modules", exist_ok=True)

    for pkg_name, source in deps.items():
        if not source.startswith("github:"):
            warn(f"⚠️  Fonte inválida para {paint(pkg_name, Color.BOLD)}. Use o formato 'github:usuario/repo'.")
            continue

        repo_path = source.split(":")[1]
        url = f"https://github.com/{repo_path}.git"
        dest = os.path.join("lumina_modules", pkg_name)

        if os.path.exists(dest):
            info(f"🔄 Atualizando pacote '{paint(pkg_name, Color.BOLD)}'...")
            try:
                subprocess.run(["git", "-C", dest, "pull"], check=True)
                success(f"✅ Pacote '{pkg_name}' atualizado.")
            except subprocess.CalledProcessError:
                error(f"❌ Falha ao atualizar {pkg_name}.")
        else:
            info(f"⬇️  Baixando pacote '{paint(pkg_name, Color.BOLD)}' de {url}...")
            try:
                subprocess.run(["git", "clone", url, dest], check=True)
                success(f"✅ Pacote '{pkg_name}' instalado em lumina_modules/{pkg_name}")
            except subprocess.CalledProcessError:
                error(f"❌ Falha ao baixar o repositório {url}")


# ============================================================
#  doc
# ============================================================
def cmd_doc():
    info("📚 Gerando documentação...")
    docs_data = []

    for filepath in glob.glob("**/*.lm", recursive=True):
        if "lumina_modules" in filepath or filepath.startswith("std/"):
            continue

        with open(filepath, "r") as f:
            lines = f.readlines()

        current_doc = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## "):
                current_doc.append(stripped[3:])
            elif stripped.startswith("##"):
                current_doc.append(stripped[2:])
            elif stripped == "" or stripped.startswith("#"):
                current_doc = []
            elif current_doc and (
                stripped.startswith("fn ") or
                stripped.startswith("struct ") or
                stripped.startswith("enum ")
            ):
                clean_decl = stripped
                if stripped.startswith("fn "):
                    clean_decl = stripped.replace("fn ", "").replace(" -> ", " ⟶ ")
                docs_data.append({
                    "file": filepath,
                    "type": ("Function" if stripped.startswith("fn ")
                             else "Struct" if stripped.startswith("struct ")
                             else "Enum"),
                    "decl": clean_decl,
                    "doc": "\n".join(current_doc)
                })
                current_doc = []

    html_content = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Lumina Documentation</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 2rem; background-color: #f8f9fa; }
        h1 { border-bottom: 2px solid #ddd; padding-bottom: 0.5rem; color: #2c3e50; }
        .item { background: #fff; padding: 1.5rem; margin-bottom: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .decl { font-family: "Fira Code", "Courier New", monospace; font-size: 1.1rem; color: #d6336c; font-weight: bold; }
        .type { display: inline-block; padding: 0.2rem 0.5rem; background: #e9ecef; border-radius: 4px; font-size: 0.8rem; color: #495057; margin-left: 0.5rem; }
        .doc { margin-top: 0.5rem; color: #495057; }
        .file { font-size: 0.8rem; color: #6c757d; font-style: italic; margin-top: 1rem; }
    </style>
</head>
<body>
    <h1>🌟 Lumina Standard Library</h1>
"""
    if not docs_data:
        html_content += "<p>Nenhuma documentação encontrada. Use '##' acima de funções, structs ou enums.</p>"
    else:
        for item in docs_data:
            html_content += f"""
    <div class="item">
        <div class="decl">{item['decl']} <span class="type">{item['type']}</span></div>
        <div class="doc">{item['doc']}</div>
        <div class="file">Definido em: {item['file']}</div>
    </div>
"""
    html_content += """
</body>
</html>"""

    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w") as f:
        f.write(html_content)

    success("✅ Documentação gerada com sucesso em: docs/index.html")


# ============================================================
#  build
# ============================================================
def cmd_build(entry_file=None, extra_flags=[]):
    if entry_file:
        entry = entry_file
        project_name = entry_file.replace('.lm', '')
        libs = []
    else:
        if not os.path.exists("lumina.toml"):
            error("❌ Erro: Nenhum arquivo 'lumina.toml' encontrado no diretório atual.")
            return None
        if tomllib is None:
            error("❌ Erro: tomllib não disponível. Use Python 3.11+.")
            return None
        with open("lumina.toml", "rb") as f:
            config = tomllib.load(f)
        entry = config.get("package", {}).get("entry", "main.lm")
        project_name = config.get("package", {}).get("name", "programa_final")
        libs = config.get("dependencies", {}).keys()

    # Detecta as flags passadas
    is_no_gc = "--no-gc" in extra_flags
    is_wasm = "--wasm" in extra_flags
    is_debug = "--debug" in extra_flags

    step(f"🛠️  Compilando projeto: {paint(project_name, Color.BOLD + Color.BRIGHT_CYAN)}")
    
    # Compila o código. Ignora o cache se for WASM ou Debug, pois o binário final muda
    llvm_ir = compile_lumina(entry, use_cache=not (is_wasm or is_debug), is_wasm=is_wasm, is_debug=is_debug)
    if not llvm_ir:
        return None

    # Filtra as flags internas da CLI para não passá-las para o clang
    cli_flags = {"--wasm", "--debug", "--no-gc"}
    linker_extra_flags = [f for f in extra_flags if f not in cli_flags]
    
    link_flags = " ".join([f"-l{lib}" for lib in libs] + linker_extra_flags)
    ir_file = f"{project_name}.ll"
    
    # Salva o IR original
    with open(ir_file, "w") as f:
        f.write(llvm_ir)

    # Lida com Debug Info (DWARF)
    debug_flag = "-g" if is_debug else ""

    # Lida com WebAssembly
    if is_wasm:
        warn("⚠️ Compilando para WebAssembly: Garbage Collector nativo desativado.")
        
        # HOTFIX WASM: Como não temos libgc no WASM, substituímos GC_malloc por malloc nativo do WASI
        with open(ir_file, "r") as f:
            ir_code = f.read()
        ir_code = ir_code.replace("GC_malloc", "malloc")
        with open(ir_file, "w") as f:
            f.write(ir_code)
        
        # NOVO: Lida com exports de função para WebAssembly
        import re
        export_names = []
        with open(entry, "r") as f:
            source_code = f.read()
            
        for match in re.finditer(r'export\s+fn\s+(\w+)', source_code):
            export_names.append(match.group(1))
            
        clang_bin = "/opt/wasi-sdk/bin/clang" if os.path.exists("/opt/wasi-sdk/bin/clang") else "clang"
        target_flag = "--target=wasm32-unknown-wasi"
        sysroot_flag = "--sysroot=/opt/wasi-sdk/share/wasi-sysroot"
        output_ext = "wasm"
        
        if export_names:
            success(f"📦 Exportando funções para JS: {', '.join(export_names)}")
            # --entry diz ao linker qual é a função principal (em vez de main)
            # --export expõe as funções para o JavaScript chamá-las
            entry_flag = f"-Wl,--entry={export_names[0]}"
            export_flags = [f"-Wl,--export={name}" for name in export_names]
            export_flags.append(entry_flag)
            
            # Como não usamos o main do WASI, não precisamos do crt1 que o procura
            # Removemos o start file para evitar o erro undefined_weak:main
            cmd = (f"{clang_bin} -O3 -nostartfiles {debug_flag} {target_flag} {sysroot_flag} {ir_file} "
                   f"-o {project_name}.{output_ext} {' '.join(export_flags)} -lc -Wl,--allow-undefined")
        else:
            cmd = (f"{clang_bin} -O3 {debug_flag} {target_flag} {sysroot_flag} {ir_file} "
                   f"-o {project_name}.{output_ext} -lc -Wl,--export=main -Wl,--allow-undefined")
    else:
        # Lida com GC em compilação nativa
        gc_flag = "" if is_no_gc else "-lgc"
        if is_no_gc:
            warn("⚠️ Modo Bare-Metal (--no-gc): Garbage Collector desativado.")
            
        target_flag = "-march=native -funroll-loops"
        output_ext = "" # Binário nativo sem extensão
        
        # NOVO: Adicionado -flto (Link-Time Optimization) para Dead Code Elimination na std/
        cmd = (f"clang -O3 -flto {target_flag} {debug_flag} {ir_file} "
               f"-o {project_name} {link_flags} -lc -lm -lpthread {gc_flag}")

    hash_obj_file = f".lumina_cache/{project_name}.bin_hash"
    
    # Verifica se o IR mudou desde a última build
    ir_changed = True
    if os.path.exists(hash_obj_file):
        with open(hash_obj_file, "r") as f:
            old_hash = f.read()
        # Compara o hash do IR atual com o salvo
        new_hash = hashlib.md5(llvm_ir.encode()).hexdigest()
        if old_hash == new_hash and not is_wasm and not is_debug:
            success(f"✅ Build incremental: Nenhum código mudou. Pulando linkagem.")
            return project_name

    header("4. Linkagem Nativa")
    info(f"Executando: {paint(cmd, Color.MUTED)}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        output_path = f"{project_name}.{output_ext}" if is_wasm else project_name
        success(f"✅ Build concluído: {paint('./' + output_path, Color.BOLD + Color.SUCCESS)}")
        
        # Salva o hash do IR para a próxima vez
        os.makedirs(".lumina_cache", exist_ok=True)
        
        # NOVO: Garante que a subpasta do cache exista (ex: .lumina_cache/lumina_core/)
        cache_subdir = os.path.dirname(hash_obj_file)
        if cache_subdir:
            os.makedirs(cache_subdir, exist_ok=True)
            
        with open(hash_obj_file, "w") as f:
            f.write(hashlib.md5(llvm_ir.encode()).hexdigest())
            
        return output_path
    except subprocess.CalledProcessError:
        error("❌ Erro durante a linkagem com o clang.")
        return None
    

# ============================================================
#  test
# ============================================================
def cmd_test(entry_file=None):
    """Compila o projeto executando automaticamente todas as funções de teste, com cobertura."""
    if not entry_file:
        if os.path.exists("lumina.toml") and tomllib:
            with open("lumina.toml", "rb") as f:
                config = tomllib.load(f)
                entry_file = config.get("package", {}).get("entry", "main.lm")
        elif os.path.exists("main.lm"):
            entry_file = "main.lm"
        else:
            error("❌ Erro: Nenhum arquivo de entrada especificado.")
            return

    if not os.path.exists(entry_file):
        error(f"❌ Erro: Arquivo '{paint(entry_file, Color.BOLD)}' não encontrado.")
        return

    step(f"🧪 Iniciando suíte de testes para: {paint(entry_file, Color.BOLD + Color.BRIGHT_CYAN)}")
    
    from .compiler import parse_module
    from lumina.ast import Function, CallExpr, NumberExpr, ReturnStmt
    from lumina.semantic import SemanticAnalyzer
    from lumina.codegen import LLVMCodegen
    from lumina.errors import LuminaError
    
    try:
        ast = parse_module(entry_file)
    except LuminaError as e:
        error(e); return None

    test_funcs = [decl for decl in ast if isinstance(decl, Function) and decl.name.startswith("test_")]
    
    if not test_funcs:
        warn("⚠️ Nenhuma função de teste (ex: `test \"nome\":`) encontrada no código.")
        return

    new_ast = [decl for decl in ast if not (isinstance(decl, Function) and decl.name == "main")]
    
    # NOVO: Chama os testes sequencialmente no main injetado
    test_calls = []
    for func in test_funcs:
        test_calls.append(CallExpr(func.name, []))
        
    new_main = Function("main", [], "int", test_calls + [ReturnStmt([NumberExpr("0")])])
    new_ast.append(new_main)

    try:
        with open(entry_file, "r") as f: source_code = f.read()
        analyzer = SemanticAnalyzer(entry_file, source_code)
        analyzer.analyze(new_ast)
    except LuminaError as e:
        error(e); return

    codegen = LLVMCodegen()
    codegen.escapes = analyzer.escapes
    llvm_ir = codegen.generate_module(new_ast)

    ir_file = "lumina_test_runner.ll"
    binary_name = "lumina_test_bin"
    
    with open(ir_file, "w") as f:
        f.write(llvm_ir)
        
    # NOVO: Adiciona -fprofile-instr-generate para mapear cobertura de código
    cmd = f"clang -O0 -fprofile-instr-generate -fcoverage-mapping {ir_file} -o {binary_name} -lc -lpthread -lgc"
    
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        header("Executando Testes")
        result = subprocess.run([f"./{binary_name}"], capture_output=True, text=True, env={**os.environ, "LLVM_PROFILE_FILE": "lumina_test.profraw"})
        print(result.stdout)
        
        if result.returncode == 0:
            success(f"✅ Todos os {len(test_funcs)} testes passaram!")
            
            # Gera o relatório de cobertura no terminal
            try:
                subprocess.run(["llvm-profdata", "merge", "-sparse", "lumina_test.profraw", "-o", "lumina_test.profdata"], check=True, capture_output=True)
                header("📊 Relatório de Cobertura de Código")
                subprocess.run(["llvm-cov", "show", binary_name, "-instr-profile=lumina_test.profdata"], check=True)
                subprocess.run(["llvm-cov", "report", binary_name, "-instr-profile=lumina_test.profdata"], check=True)
            except Exception:
                warn("⚠️ Ferramentas de cobertura (llvm-cov) não encontradas. Relatório ignorado.")
        else:
            error("❌ Um ou mais testes falharam (Assertion Failed).")
            
    except subprocess.CalledProcessError:
        error("❌ Erro durante a compilação da suíte de testes.")
    finally:
        # Limpa os arquivos temporários
        if os.path.exists(ir_file): os.remove(ir_file)
        if os.path.exists(binary_name): os.remove(binary_name)
        if os.path.exists("lumina_test.profraw"): os.remove("lumina_test.profraw")
        if os.path.exists("lumina_test.profdata"): os.remove("lumina_test.profdata")


# ============================================================
#  clean
# ============================================================
def cmd_clean():
    """Limpa o cache de compilação e os binários gerados."""
    step("🧹 Limpando cache e binários...")

    if os.path.exists(".lumina_cache"):
        subprocess.run(["rm", "-rf", ".lumina_cache"])
        success("✅ Cache (.lumina_cache) removido.")

    # Remove arquivos LLVM IR (.ll) e WebAssembly (.wasm)
    for ext in ["*.ll", "*.wasm"]:
        for f in glob.glob(ext):
            os.remove(f)
            success(f"✅ Removido: {paint(f, Color.MUTED)}")

    # Remove binários sem extensão (gerados pelo build nativo)
    for f in os.listdir("."):
        if os.path.isfile(f) and "." not in f and not f.startswith("."):
            os.remove(f)
            success(f"✅ Removido binário: {paint(f, Color.MUTED)}")

    success("Limpeza concluída!")


# ============================================================
#  run / jit
# ============================================================
def cmd_run(entry_file=None, use_jit=False, extra_flags=[]):
    """Compila (usando cache se possível) e executa o programa."""
    if not entry_file:
        if os.path.exists("lumina.toml") and tomllib:
            with open("lumina.toml", "rb") as f:
                config = tomllib.load(f)
                entry_file = config.get("package", {}).get("entry", "main.lm")
        elif os.path.exists("lumina.json"):
            with open("lumina.json", "r") as f:
                config = json.load(f)
                entry_file = config.get("entry", "main.lm")
        elif os.path.exists("main.lm"):
            entry_file = "main.lm"
        else:
            error("❌ Erro: Nenhum arquivo de entrada especificado.")
            return

    if not os.path.exists(entry_file):
        error(f"❌ Erro: Arquivo '{paint(entry_file, Color.BOLD)}' não encontrado.")
        return

    step(f"🚀 Iniciando processo para: {paint(entry_file, Color.BOLD + Color.BRIGHT_CYAN)}")

    if use_jit:
        ir_file = "lumina_jit_temp.ll"
        llvm_ir = compile_lumina(entry_file, output_file=ir_file)
        if not llvm_ir:
            error("❌ Falha na compilação.")
            return
        # Limpa IR temporário
        if os.path.exists(ir_file):
            os.remove(ir_file)
        run_jit(llvm_ir, [])
        return

    binary_name = cmd_build(entry_file, extra_flags=extra_flags)
    if not binary_name:
        error("❌ Falha na compilação.")
        return

    header("Executando Binário Nativo")
    subprocess.run([f"./{binary_name}"])


# ============================================================
#  bind
# ============================================================
def cmd_bind(header_file, output_name):
    if not os.path.exists(header_file):
        error(f"❌ Erro: Arquivo '{paint(header_file, Color.BOLD)}' não encontrado.")
        return

    with open(header_file, "r") as f:
        content = f.read()

    pattern = r'(\w[\w\s\*]*?)\s+(\w+)\s*\(([^)]*)\)\s*;'
    matches = re.finditer(pattern, content)

    c_type_map = {
        "int": "int", "long": "int", "long long": "int", "short": "int", "size_t": "int",
        "float": "float", "double": "float",
        "char*": "str", "const char*": "str", "void*": "str", "const void*": "str",
        "char": "int", "unsigned char": "int", "unsigned int": "int", "unsigned long": "int"
    }

    lumina_decls = []
    for match in matches:
        c_ret = match.group(1).strip()
        name = match.group(2).strip()
        args_str = match.group(3).strip()

        if name in ("if", "while", "for", "return", "struct", "typedef", "static", "extern", "void"):
            continue

        ret_type = c_type_map.get(c_ret, "str")

        lumina_args = []
        if args_str and args_str != "void":
            for arg in args_str.split(','):
                arg = arg.strip()
                parts = arg.rsplit(' ', 1)
                if len(parts) == 2:
                    arg_type, arg_name = parts[0].strip(), parts[1].strip()
                    lumina_type = c_type_map.get(arg_type, "str")
                    lumina_args.append(f"{arg_name}: {lumina_type}")
                else:
                    lumina_args.append(f"arg: str")

        lumina_decls.append(f"extern fn {name}({', '.join(lumina_args)}) -> {ret_type}")

    if not lumina_decls:
        warn("Nenhuma função válida encontrada no cabeçalho.")
        return

    out_file = f"std/{output_name}.lm"
    os.makedirs("std", exist_ok=True)
    with open(out_file, "w") as f:
        f.write(f"# Auto-gerado de {header_file} pelo Lumina Bind\n\n")
        f.write("\n".join(lumina_decls))

    success(f"✅ Bindings gerados com sucesso em {paint(out_file, Color.BOLD + Color.BRIGHT_CYAN)} "
            f"({len(lumina_decls)} funções)")


# ============================================================
#  fmt
# ============================================================
def cmd_fmt(filename):
    if not os.path.exists(filename):
        error(f"❌ Erro: Arquivo '{paint(filename, Color.BOLD)}' não encontrado.")
        return

    with open(filename, "r") as f:
        code = f.read()

    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens, filename, code)
        ast = parser.parse()

        formatted_code = ""
        for node in ast:
            formatted_code += format_node(node)

        with open(filename, "w") as f:
            f.write(formatted_code)

        success(f"✅ Arquivo '{paint(filename, Color.BOLD + Color.BRIGHT_CYAN)}' formatado com sucesso!")

    except LuminaError as e:
        error("❌ Não foi possível formatar devido a erros de sintaxe:")
        print(e)


# ============================================================
#  repl
# ============================================================
def cmd_repl():
    step("Lumina REPL 1.0")
    info("Digite seu código. Pressione ENTER numa linha vazia para executar.")
    info(f"Digite {paint('exit', Color.BOLD)} para sair.")
    cprint("-" * 58, color=Color.MUTED)

    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()
    lib_c_path = ctypes.util.find_library('c')
    if lib_c_path:
        llvm.load_library_permanently(lib_c_path)

    buffer = []
    while True:
        try:
            prompt_str = "lumina> " if not buffer else "... "
            line = input(paint(prompt_str, Color.PROMPT))

            if line.strip().lower() in ("exit", "quit"):
                break

            if not line.strip():
                if not buffer:
                    continue
                code = "fn main() -> int:\n    " + "\n    ".join(buffer) + "\n    return 0"
                try:
                    lexer = Lexer(code)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens, "repl.lm", code)
                    ast = parser.parse()

                    analyzer = SemanticAnalyzer("repl.lm", code)
                    analyzer.analyze(ast)

                    codegen = LLVMCodegen()
                    llvm_ir = codegen.generate_module(ast)

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
                    cfunc(0, None)
                    ctypes.CDLL(None).fflush(None)

                except LuminaError as e:
                    print(e)
                except Exception as e:
                    error(f"Erro interno: {e}")
                finally:
                    buffer = []
                continue

            buffer.append(line)

        except KeyboardInterrupt:
            warn("\n(Buffer limpo. Digite 'exit' para sair)")
            buffer = []
        except EOFError:
            break