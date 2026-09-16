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
    import tomllib
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
    set_progress_stream,
)
from .compiler import compile_lumina, run_jit, format_node


# ============================================================
#  Error format global (text ou json)
# ============================================================
ERROR_FORMAT = "text"


def set_error_format(fmt: str):
    """Define o formato de erro global.

    Valores: 'text' (padrão) ou 'json'.
    Em modo JSON, todo progresso vai para stderr; stdout fica exclusivo
    para a linha JSON — assim `... | jq .` funciona direto.
    """
    global ERROR_FORMAT
    if fmt not in ("text", "json"):
        fmt = "text"
    ERROR_FORMAT = fmt

    if fmt == "json":
        set_progress_stream(sys.stderr)
    else:
        set_progress_stream(sys.stdout)


def _report_error(e):
    """Reporta um erro respeitando ERROR_FORMAT.

    Em modo 'json', emite uma linha JSON no stdout. Em modo 'text',
    usa o formatador colorido padrão (via `error`).
    Aceita tanto LuminaError quanto strings simples.
    """
    if ERROR_FORMAT == "json":
        try:
            payload = e.to_dict()
        except AttributeError:
            payload = {"type": "error", "message": str(e)}
        print(json.dumps(payload, ensure_ascii=False), flush=True)
    else:
        error(e)


# ============================================================
#  Helpers de [link]
# ============================================================
def _load_link_config(entry_file=None):
    """Carrega config de [link] do lumina.toml apropriado.

    Prioridade:
      1. Se entry_file dado: procura <entry_file sem .lm>.toml (sidecar).
      2. Fallback: procura ./lumina.toml.

    Retorna dict com chaves: libs, extra_objects, target, extra_flags.
    Retorna {} (vazio) se não encontrar nada.
    """
    config_path = None
    if entry_file:
        sidecar = re.sub(r'\.lm$', '.toml', entry_file)
        if os.path.exists(sidecar):
            config_path = sidecar
        elif os.path.exists("lumina.toml"):
            config_path = "lumina.toml"
    elif os.path.exists("lumina.toml"):
        config_path = "lumina.toml"

    if not config_path:
        return {}

    if tomllib is None:
        return {}

    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
    except Exception:
        return {}

    link = config.get("link", {})
    return {
        "libs": list(link.get("libs", [])),
        "extra_objects": list(link.get("extra_objects", [])),
        "target": link.get("target"),
        "extra_flags": list(link.get("extra_flags", [])),
    }


def _compile_extra_objects(extra_objects):
    """Compila cada extra_object (.c/.cpp/.cc) para .o e retorna a lista.

    Retorna (obj_paths, has_cpp) onde has_cpp indica se algum veio de C++.
    """
    obj_paths = []
    has_cpp = False

    for src in extra_objects:
        if not os.path.exists(src):
            warn(f"⚠️  extra_object não encontrado: {paint(src, Color.MUTED)}")
            continue

        is_cpp = src.endswith(('.cpp', '.cc', '.cxx', '.C'))
        compiler = "clang++" if is_cpp else "clang"
        obj_out = os.path.splitext(src)[0] + ".o"

        try:
            subprocess.run(
                [compiler, "-O2", "-c", src, "-o", obj_out],
                check=True, capture_output=True,
            )
            obj_paths.append(obj_out)
            if is_cpp:
                has_cpp = True
        except subprocess.CalledProcessError as e:
            err = (e.stderr or b"").decode("utf-8", errors="replace")[:200]
            _report_error(f"Falha ao compilar {src}: {err}")

    return obj_paths, has_cpp


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

# Configuração de link (opcional)
# [link]
# libs = ["m", "raylib"]              # passado como -lm -lraylib
# extra_objects = ["helper.cpp"]      # arquivos C/C++ compilados e linkados
# target = "wasm"                     # força compilação WASM
# extra_flags = ["-DFOO"]             # flags extras para o clang
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

    success(f"✅ Projeto '{paint(project_name, Color.BOLD + Color.BRIGHT_CYAN)}' criado com sucesso!")


# ============================================================
#  install
# ============================================================
def cmd_install():
    if not os.path.exists("lumina.toml"):
        _report_error("Nenhum arquivo 'lumina.toml' encontrado no diretório atual.")
        return

    if tomllib is None:
        _report_error("tomllib não disponível. Use Python 3.11+.")
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
                _report_error(f"Falha ao atualizar {pkg_name}.")
        else:
            info(f"⬇️  Baixando pacote '{paint(pkg_name, Color.BOLD)}' de {url}...")
            try:
                subprocess.run(["git", "clone", url, dest], check=True)
                success(f"✅ Pacote '{pkg_name}' instalado em lumina_modules/{pkg_name}")
            except subprocess.CalledProcessError:
                _report_error(f"Falha ao baixar o repositório {url}")


# ============================================================
#  doc
# ============================================================
def cmd_doc(output_format="html", output_path=None):
    """Gera documentação a partir de comentários `##`.

    Formatos:
      - html (padrão): docs/index.html
      - md:            docs/index.md
      - json:          docs/index.json

    `output_path` sobrescreve o caminho padrão.
    """
    info(f"📚 Gerando documentação ({output_format})...")
    docs_data = _collect_docs()

    if output_format == "json":
        content = _render_doc_json(docs_data)
        default_path = os.path.join("docs", "index.json")
    elif output_format == "md":
        content = _render_doc_md(docs_data)
        default_path = os.path.join("docs", "index.md")
    else:
        content = _render_doc_html(docs_data)
        default_path = os.path.join("docs", "index.html")

    dest = output_path or default_path
    parent = os.path.dirname(dest)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(dest, "w") as f:
        f.write(content)

    success(f"✅ Documentação gerada em: {paint(dest, Color.BOLD + Color.BRIGHT_CYAN)}")


def _collect_docs():
    """Coleta os itens documentados (## acima de fn/struct/enum/trait)."""
    docs_data = []
    for filepath in glob.glob("**/*.lm", recursive=True):
        if "lumina_modules" in filepath or filepath.startswith("std/"):
            continue
        try:
            with open(filepath, "r") as f:
                lines = f.readlines()
        except Exception:
            continue

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
                stripped.startswith("enum ") or
                stripped.startswith("trait ")
            ):
                if stripped.startswith("fn "):
                    decl = stripped.replace("fn ", "").replace(" -> ", " ⟶ ")
                    dtype = "Function"
                elif stripped.startswith("struct "):
                    decl = stripped
                    dtype = "Struct"
                elif stripped.startswith("enum "):
                    decl = stripped
                    dtype = "Enum"
                else:
                    decl = stripped
                    dtype = "Trait"

                docs_data.append({
                    "file": filepath,
                    "type": dtype,
                    "decl": decl,
                    "doc": "\n".join(current_doc),
                })
                current_doc = []
    return docs_data


def _render_doc_html(docs_data):
    html = """<!DOCTYPE html>
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
        html += "<p>Nenhuma documentação encontrada. Use '##' acima de funções, structs ou enums.</p>"
    else:
        for item in docs_data:
            html += f"""
    <div class="item">
        <div class="decl">{item['decl']} <span class="type">{item['type']}</span></div>
        <div class="doc">{item['doc']}</div>
        <div class="file">Definido em: {item['file']}</div>
    </div>
"""
    html += """
</body>
</html>"""
    return html


def _render_doc_md(docs_data):
    lines = ["# 🌟 Lumina Standard Library", ""]
    if not docs_data:
        lines.append("_Nenhuma documentação encontrada. Use `##` acima de funções, structs ou enums._")
        return "\n".join(lines)

    by_type = {}
    for item in docs_data:
        by_type.setdefault(item["type"], []).append(item)

    for dtype in ("Function", "Struct", "Enum", "Trait"):
        if dtype not in by_type:
            continue
        heading = {"Function": "Funções", "Struct": "Structs",
                   "Enum": "Enums", "Trait": "Traits"}[dtype]
        lines.append(f"## {heading}")
        lines.append("")
        for item in by_type[dtype]:
            lines.append(f"### `{item['decl']}`")
            lines.append("")
            if item["doc"]:
                for doc_line in item["doc"].split("\n"):
                    lines.append(doc_line)
                lines.append("")
            lines.append(f"_Definido em: `{item['file']}`_")
            lines.append("")
    return "\n".join(lines)


def _render_doc_json(docs_data):
    payload = {
        "title": "Lumina Standard Library",
        "count": len(docs_data),
        "items": docs_data,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


# ============================================================
#  build
# ============================================================
def cmd_build(entry_file=None, extra_flags=[]):
    link_cfg = _load_link_config(entry_file)
    libs = link_cfg.get("libs", [])
    extra_objs_src = link_cfg.get("extra_objects", [])
    link_target = link_cfg.get("target")
    link_extra_flags = link_cfg.get("extra_flags", [])

    if entry_file:
        entry = entry_file
        if entry_file.endswith(".lm"):
            project_name = entry_file[:-3]
        else:
            project_name = entry_file
    else:
        if not os.path.exists("lumina.toml"):
            _report_error("Nenhum arquivo 'lumina.toml' encontrado no diretório atual.")
            return None
        if tomllib is None:
            _report_error("tomllib não disponível. Use Python 3.11+.")
            return None
        with open("lumina.toml", "rb") as f:
            config = tomllib.load(f)
        entry = config.get("package", {}).get("entry", "main.lm")
        project_name = config.get("package", {}).get("name", "programa_final")

    extra_flags = list(extra_flags)
    if link_target == "wasm" and "--wasm" not in extra_flags:
        extra_flags.append("--wasm")
        info(f"🎯 Target '{link_target}' detectado em [link] — forçando --wasm")

    # NOVO: extrai --target=<triple> antes de qualquer coisa.
    # `--target=aarch64-linux-gnu` etc.
    target_triple = None
    filtered_flags = []
    for f in extra_flags:
        if f.startswith("--target="):
            target_triple = f.split("=", 1)[1]
        else:
            filtered_flags.append(f)
    extra_flags = filtered_flags

    is_no_gc = "--no-gc" in extra_flags
    is_wasm = "--wasm" in extra_flags
    is_debug = "--debug" in extra_flags
    is_release = "--release" in extra_flags

    if is_debug:
        opt_flag = "-O0"
    elif is_release:
        opt_flag = "-O3"
    else:
        opt_flag = "-O2"

    step(f"🛠️  Compilando projeto: {paint(project_name, Color.BOLD + Color.BRIGHT_CYAN)}")
    info(f"⚙️  Otimização: {paint(opt_flag, Color.BOLD)}")

    cache_use = not (is_wasm or is_debug)

    llvm_ir = compile_lumina(entry, use_cache=cache_use, is_wasm=is_wasm,
                             is_debug=is_debug, on_error=_report_error,
                             target_triple=target_triple)
    if not llvm_ir:
        return None

    cli_flags = {"--wasm", "--debug", "--no-gc", "--release"}
    linker_extra_flags = [f for f in extra_flags if f not in cli_flags]
    linker_extra_flags.extend(link_extra_flags)

    extra_obj_paths, has_cpp = _compile_extra_objects(extra_objs_src)

    ir_file = f"{project_name}.ll"
    with open(ir_file, "w") as f:
        f.write(llvm_ir)

    debug_flag = "-g" if is_debug else ""

    if is_wasm:
        warn("⚠️ Compilando para WebAssembly: Garbage Collector nativo desativado.")
        with open(ir_file, "r") as f:
            ir_code = f.read()
        ir_code = ir_code.replace("GC_malloc", "malloc")
        with open(ir_file, "w") as f:
            f.write(ir_code)

        export_names = []
        with open(entry, "r") as f:
            source_code = f.read()
        for match in re.finditer(r'export\s+fn\s+(\w+)', source_code):
            export_names.append(match.group(1))

        clang_bin = "/opt/wasi-sdk/bin/clang" if os.path.exists("/opt/wasi-sdk/bin/clang") else "clang"

        cmd_args = [clang_bin, "-O3", "-nostartfiles", debug_flag,
                    "--target=wasm32-unknown-wasi",
                    "--sysroot=/opt/wasi-sdk/share/wasi-sysroot", ir_file]
        cmd_args.extend(extra_obj_paths)

        if export_names:
            success(f"📦 Exportando funções para JS: {', '.join(export_names)}")
            cmd_args.append(f"-Wl,--entry={export_names[0]}")
            for name in export_names:
                cmd_args.append(f"-Wl,--export={name}")
            cmd_args.extend(["-lc", "-Wl,--allow-undefined", "-o", f"{project_name}.wasm"])
        else:
            cmd_args.extend(["-lc", "-Wl,--export=main", "-Wl,--allow-undefined", "-o", f"{project_name}.wasm"])

        for lib in libs:
            cmd_args.append(f"-l{lib}")
        cmd_args.extend(linker_extra_flags)
    else:
        gc_flag = "-lgc" if not is_no_gc else ""
        if is_no_gc:
            warn("⚠️ Modo Bare-Metal (--no-gc): Garbage Collector desativado.")

        if target_triple:
            info(f"🎯 Cross-compilando para: {paint(target_triple, Color.BOLD)}")
            warn("⚠️ Cross-compile requer sysroot/toolchain do target no PATH "
                 "(ex: gcc-aarch64-linux-gnu). libgc precisa estar linkável "
                 "para o target, ou use --no-gc.")

        cmd_args = ["clang"]
        if target_triple:
            cmd_args.append(f"--target={target_triple}")
        cmd_args.extend([opt_flag, "-Wno-override-module", debug_flag,
                         ir_file, "-o", project_name, "-lc", "-lm", "-lpthread"])

        if gc_flag:
            cmd_args.append(gc_flag)

        cmd_args.extend(extra_obj_paths)

        if has_cpp:
            cmd_args.append("-lstdc++")

        for lib in libs:
            cmd_args.append(f"-l{lib}")

        cmd_args.extend(linker_extra_flags)

    hash_obj_file = f".lumina_cache/{project_name}.bin_hash"
    opt_marker = opt_flag

    if os.path.exists(hash_obj_file) and not is_wasm and not is_debug:
        with open(hash_obj_file, "r") as f:
            old_hash = f.read()
        combined = llvm_ir + "|" + opt_marker
        new_hash = hashlib.md5(combined.encode()).hexdigest()
        if old_hash == new_hash:
            success(f"✅ Build incremental: Nenhum código mudou. Pulando linkagem.")
            return project_name

    header("4. Linkagem Nativa")
    cmd_str = " ".join(cmd_args)
    info(f"Executando: {paint(cmd_str, Color.MUTED)}")

    try:
        subprocess.run(cmd_args, check=True)
        output_path = f"{project_name}.wasm" if is_wasm else project_name
        display_path = output_path if os.path.isabs(output_path) else f"./{output_path}"
        success(f"✅ Build concluído: {paint(display_path, Color.BOLD + Color.SUCCESS)}")

        os.makedirs(".lumina_cache", exist_ok=True)
        cache_subdir = os.path.dirname(hash_obj_file)
        if cache_subdir:
            os.makedirs(cache_subdir, exist_ok=True)

        combined = llvm_ir + "|" + opt_marker
        with open(hash_obj_file, "w") as f:
            f.write(hashlib.md5(combined.encode()).hexdigest())

        return output_path
    except subprocess.CalledProcessError:
        _report_error(LuminaError(
            "Erro durante a linkagem com o clang. Veja a saída acima para detalhes.",
            entry, 0, 0, "",
        ))
        return None


# ============================================================
#  check
# ============================================================
def cmd_check(entry_file=None):
    if not entry_file:
        if os.path.exists("lumina.toml") and tomllib:
            with open("lumina.toml", "rb") as f:
                config = tomllib.load(f)
                entry_file = config.get("package", {}).get("entry", "main.lm")
        elif os.path.exists("main.lm"):
            entry_file = "main.lm"
        else:
            _report_error("Nenhum arquivo de entrada especificado.")
            return False

    if not os.path.exists(entry_file):
        _report_error(f"Arquivo '{entry_file}' não encontrado.")
        return False

    step(f"🔍 Verificando: {paint(entry_file, Color.BOLD + Color.BRIGHT_CYAN)}")

    from .compiler import check_lumina
    ok = check_lumina(entry_file, on_error=_report_error)

    if ok:
        success(f"✅ {paint(entry_file, Color.BOLD)} — sem erros")
    return ok


# ============================================================
#  test
# ============================================================
def cmd_test(entry_file=None):
    """Executa a suíte de testes. Retorna o número de falhas (exit code).

    Exit codes:
      - 0                → todos os testes passaram
      - N > 0            → N falhas
      - 1                → erro de compilação/build
    """
    if not entry_file:
        if os.path.exists("lumina.toml") and tomllib:
            with open("lumina.toml", "rb") as f:
                config = tomllib.load(f)
                entry_file = config.get("package", {}).get("entry", "main.lm")
        elif os.path.exists("main.lm"):
            entry_file = "main.lm"
        else:
            _report_error("Nenhum arquivo de entrada especificado.")
            return 1

    if not os.path.exists(entry_file):
        _report_error(f"Arquivo '{entry_file}' não encontrado.")
        return 1

    step(f"🧪 Iniciando suíte de testes para: {paint(entry_file, Color.BOLD + Color.BRIGHT_CYAN)}")

    from .compiler import parse_module
    from lumina.ast import Function, CallExpr, NumberExpr, ReturnStmt, VariableExpr

    try:
        ast = parse_module(entry_file)
    except LuminaError as e:
        _report_error(e)
        return 1

    test_funcs = [decl for decl in ast if isinstance(decl, Function) and decl.name.startswith("test_")]
    if not test_funcs:
        warn("⚠️ Nenhuma função de teste (ex: `test \"nome\":`) encontrada no código.")
        return 0

    from lumina.ast import VarDecl, AssignStmt, BinaryExpr

    new_ast = [decl for decl in ast if not (isinstance(decl, Function) and decl.name == "main")]

    # Synthetic main que soma os retornos de cada teste.
    # Exit code = total de falhas.
    total_var = "_total_failures"
    body = [VarDecl(total_var, "int", NumberExpr("0"), True)]
    for func in test_funcs:
        call = CallExpr(VariableExpr(func.name, 0, 0), [])
        add = BinaryExpr("+", VariableExpr(total_var, 0, 0), call)
        body.append(AssignStmt(VariableExpr(total_var, 0, 0), add))
    body.append(ReturnStmt([VariableExpr(total_var, 0, 0)]))
    new_main = Function("main", [], "int", body)
    new_ast.append(new_main)

    try:
        with open(entry_file, "r") as f:
            source_code = f.read()
        analyzer = SemanticAnalyzer(entry_file, source_code)
        analyzer.analyze(new_ast)
    except LuminaError as e:
        _report_error(e)
        return 1

    codegen = LLVMCodegen()
    codegen.escapes = analyzer.escapes
    llvm_ir = codegen.generate_module(new_ast)

    ir_file = "lumina_test_runner.ll"
    binary_name = "lumina_test_bin"

    with open(ir_file, "w") as f:
        f.write(llvm_ir)

    # NOVO: respeita [link] do lumina.toml (sidecar ou raiz)
    link_cfg = _load_link_config(entry_file)
    libs = link_cfg.get("libs", [])
    extra_objs_src = link_cfg.get("extra_objects", [])
    link_extra_flags = link_cfg.get("extra_flags", [])
    extra_obj_paths, has_cpp = _compile_extra_objects(extra_objs_src)

    cmd_args = ["clang", "-O0", "-fprofile-instr-generate", "-fcoverage-mapping",
                ir_file, "-o", binary_name, "-lc", "-lm", "-lpthread", "-lgc"]
    cmd_args.extend(extra_obj_paths)
    if has_cpp:
        cmd_args.append("-lstdc++")
    for lib in libs:
        cmd_args.append(f"-l{lib}")
    cmd_args.extend(link_extra_flags)

    try:
        subprocess.run(cmd_args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        header("Executando Testes")
        result = subprocess.run(
            [f"./{binary_name}"],
            capture_output=True, text=True,
            env={**os.environ, "LLVM_PROFILE_FILE": "lumina_test.profraw"},
        )
        print(result.stdout)

        if result.returncode == 0:
            success(f"✅ Todos os {len(test_funcs)} testes passaram!")
            try:
                subprocess.run(["llvm-profdata", "merge", "-sparse",
                                "lumina_test.profraw", "-o", "lumina_test.profdata"],
                               check=True, capture_output=True)
                header("📊 Relatório de Cobertura de Código")
                subprocess.run(["llvm-cov", "report", binary_name,
                                "-instr-profile=lumina_test.profdata"], check=True)
            except Exception:
                warn("⚠️ Ferramentas de cobertura (llvm-cov) não encontradas. Relatório ignorado.")
            return 0
        else:
            _report_error(f"{result.returncode} teste(s) falharam.")
            return result.returncode if result.returncode > 0 else 1

    except subprocess.CalledProcessError:
        _report_error("Erro durante a compilação da suíte de testes.")
        return 1
    finally:
        for f in (ir_file, binary_name, "lumina_test.profraw", "lumina_test.profdata"):
            if os.path.exists(f):
                os.remove(f)


# ============================================================
#  clean
# ============================================================
def cmd_clean():
    step("🧹 Limpando cache e binários...")

    if os.path.exists(".lumina_cache"):
        subprocess.run(["rm", "-rf", ".lumina_cache"])
        success("✅ Cache (.lumina_cache) removido.")

    for ext in ["*.ll", "*.wasm"]:
        for f in glob.glob(ext):
            os.remove(f)
            success(f"✅ Removido: {paint(f, Color.MUTED)}")

    known_outputs = {"programa_final", "lumina_test_bin", "output", "lumina_jit_temp"}
    for f in os.listdir("."):
        if f in known_outputs and os.path.isfile(f):
            os.remove(f)
            success(f"✅ Removido binário: {paint(f, Color.MUTED)}")

    success("Limpeza concluída!")


# ============================================================
#  run / jit
# ============================================================
def cmd_run(entry_file=None, use_jit=False, extra_flags=[], cli_args=None):
    """Compila e executa. Retorna o exit code do programa.

    Exit codes:
      - exit code do binário compilado (0..255)
      - 1 se a compilação falhar
    """
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
            _report_error("Nenhum arquivo de entrada especificado.")
            return 1

    if not os.path.exists(entry_file):
        _report_error(f"Arquivo '{entry_file}' não encontrado.")
        return 1

    step(f"🚀 Iniciando processo para: {paint(entry_file, Color.BOLD + Color.BRIGHT_CYAN)}")

    if use_jit:
        ir_file = "lumina_jit_temp.ll"
        try:
            llvm_ir = compile_lumina(entry_file, output_file=ir_file, on_error=_report_error)
            if not llvm_ir:
                return 1
            return run_jit(llvm_ir, cli_args or [])
        finally:
            if os.path.exists(ir_file):
                os.remove(ir_file)

    binary_name = cmd_build(entry_file, extra_flags=extra_flags)
    if not binary_name:
        # cmd_build já reportou o erro
        return 1

    header("Executando Binário Nativo")

    if os.path.isabs(binary_name):
        exe_path = binary_name
    else:
        exe_path = f"./{binary_name}"

    result = subprocess.run([exe_path])
    return result.returncode


# ============================================================
#  bind
# ============================================================
def cmd_bind(header_file, output_name):
    if not os.path.exists(header_file):
        _report_error(f"Arquivo '{header_file}' não encontrado.")
        return

    with open(header_file, "r") as f:
        content = f.read()

    pattern = r'(\w[\w\s\*]*?)\s+(\w+)\s*\(([^)]*)\)\s*;'
    matches = re.finditer(pattern, content)

    c_type_map = {
        "int": "int", "long": "int", "long long": "int", "short": "int", "size_t": "int",
        "float": "float", "double": "float",
        "char*": "str", "const char*": "str", "void*": "str", "const void*": "str",
        "char": "int", "unsigned char": "int", "unsigned int": "int", "unsigned long": "int",
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

    success(f"✅ Bindings gerados em {paint(out_file, Color.BOLD + Color.BRIGHT_CYAN)} ({len(lumina_decls)} funções)")


# ============================================================
#  fmt
# ============================================================
def cmd_fmt(filename, check_only=False):
    """Formata um arquivo Lumina.

    Se `check_only=True`, não escreve — apenas verifica se o código
    já está formatado. Retorna True se OK (ou já formatado), False se
    precisa formatar ou se houve erro.

    Nota: o auto-formatter preserva comentários leading e `@attrs`.
    Comentários trailing (inline) ainda são descartados.
    """
    if not os.path.exists(filename):
        _report_error(f"Arquivo '{filename}' não encontrado.")
        return False

    with open(filename, "r") as f:
        original_code = f.read()

    try:
        lexer = Lexer(original_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens, filename, original_code)
        ast = parser.parse()

        formatted_code = ""
        for node in ast:
            formatted_code += format_node(node)
    except LuminaError as e:
        _report_error(e)
        return False

    if check_only:
        if formatted_code == original_code:
            success(f"✅ {paint(filename, Color.BOLD)} — já formatado")
            return True
        else:
            info(f"⚠️  {paint(filename, Color.BOLD)} precisa ser formatado")
            return False

    with open(filename, "w") as f:
        f.write(formatted_code)

    success(f"✅ Arquivo '{paint(filename, Color.BOLD + Color.BRIGHT_CYAN)}' formatado com sucesso!")
    return True


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
                        ctypes.c_int, ctypes.c_int32, ctypes.POINTER(ctypes.c_char_p)
                    )(func_ptr)
                    ret = cfunc(0, None)
                    ctypes.CDLL(None).fflush(None)
                    if ret != 0:
                        print(f"=> {ret}")

                except LuminaError as e:
                    print(e)
                except Exception as e:
                    _report_error(f"Erro interno: {e}")
                finally:
                    buffer = []
                continue

            buffer.append(line)

        except KeyboardInterrupt:
            warn("\n(Buffer limpo. Digite 'exit' para sair)")
            buffer = []
        except EOFError:
            break