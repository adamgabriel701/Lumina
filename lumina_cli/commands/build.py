"""`lumina build`, `lumina check`, `lumina run` — compilação, checagem e execução."""
import hashlib
import json
import os
import re
import subprocess

try:
    import tomllib
except ImportError:
    tomllib = None

from lumina.errors import LuminaError

from ..compiler import compile_lumina, check_lumina, run_jit
from ..utils import Color, paint, info, success, warn, step, header
from .errors import report_error
from .linking import load_link_config, compile_extra_objects


def cmd_build(entry_file=None, extra_flags=[]):
    link_cfg = load_link_config(entry_file)
    libs = link_cfg.get("libs", [])
    extra_objs_src = link_cfg.get("extra_objects", [])
    link_target = link_cfg.get("target")
    link_extra_flags = link_cfg.get("extra_flags", [])

    if entry_file:
        entry = entry_file
        project_name = entry_file[:-3] if entry_file.endswith(".lm") else entry_file
    else:
        if not os.path.exists("lumina.toml"):
            report_error("Nenhum arquivo 'lumina.toml' encontrado no diretório atual.")
            return None
        if tomllib is None:
            report_error("tomllib não disponível. Use Python 3.11+.")
            return None
        with open("lumina.toml", "rb") as f:
            config = tomllib.load(f)
        entry = config.get("package", {}).get("entry", "main.lm")
        project_name = config.get("package", {}).get("name", "programa_final")

    extra_flags = list(extra_flags)
    if link_target == "wasm" and "--wasm" not in extra_flags:
        extra_flags.append("--wasm")
        info(f"🎯 Target '{link_target}' detectado em [link] — forçando --wasm")

    target_triple = None
    filtered_flags = []
    for f in extra_flags:
        if f.startswith("--target="):
            target_triple = f.split("=", 1)[1]
        else:
            filtered_flags.append(f)
    extra_flags = filtered_flags

    is_wasm = "--wasm" in extra_flags
    is_debug = "--debug" in extra_flags
    is_release = "--release" in extra_flags
    is_no_gc = ("--no-gc" in extra_flags) or is_wasm

    opt_flag = "-O0" if is_debug else ("-O3" if is_release else "-O2")

    step(f"🛠️  Compilando projeto: {paint(project_name, Color.BOLD + Color.BRIGHT_CYAN)}")
    info(f"⚙️  Otimização: {paint(opt_flag, Color.BOLD)}")

    cache_use = not (is_wasm or is_debug)

    llvm_ir = compile_lumina(entry, use_cache=cache_use, is_wasm=is_wasm,
                             is_debug=is_debug, is_no_gc=is_no_gc,
                             on_error=report_error,
                             target_triple=target_triple)
    if not llvm_ir:
        return None

    cli_flags = {"--wasm", "--debug", "--no-gc", "--release"}
    linker_extra_flags = [f for f in extra_flags if f not in cli_flags]
    linker_extra_flags.extend(link_extra_flags)

    extra_obj_paths, has_cpp = compile_extra_objects(extra_objs_src, linker_extra_flags)

    ir_file = f"{project_name}.ll"
    with open(ir_file, "w") as f:
        f.write(llvm_ir)

    if is_release and not is_wasm:
        try:
            opt_result = subprocess.run(
                ["opt", "-O2", "-S", ir_file, "-o", ir_file],
                capture_output=True, text=True, timeout=30,
            )
            if opt_result.returncode != 0:
                warn("⚠️  opt -O2 falhou; seguindo com IR não-otimizado.")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            warn("⚠️  'opt' não encontrado no PATH; pulando otimização extra.")

    debug_flag = "-g" if is_debug else ""

    if is_wasm:
        warn("⚠️ Compilando para WebAssembly: Garbage Collector nativo desativado.")
        with open(entry, "r") as f:
            source_code = f.read()
        export_names = [m.group(1) for m in re.finditer(r'export\s+fn\s+(\w+)', source_code)]

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
            cmd_args.extend(["-lc", "-Wl,--export=main", "-Wl,--allow-undefined",
                             "-o", f"{project_name}.wasm"])

        for lib in libs:
            cmd_args.append(f"-l{lib}")
        cmd_args.extend(linker_extra_flags)

        output_path = f"{project_name}.wasm"
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

        output_path = project_name

    # ------------------------------------------------------------------
    # Cache incremental de LINKAGEM
    #
    # A cache só é confiável se TODAS as condições baterem:
    #   1. O arquivo de hash existe (build anterior rodou)
    #   2. O hash do IR + opt_flag bate (código não mudou)
    #   3. O BINÁRIO DE SAÍDA existe em disco (não foi deletado/movido)
    #
    # Sem (3), temos o bug: cache diz "nada mudou, pulando linkagem",
    # o comando reporta sucesso, mas o binário não existe. Sintoma típico:
    #   $ lumina build foo.lm --release && mv foo foo_lumina
    #   mv: cannot stat 'foo': No such file or directory
    # ------------------------------------------------------------------
    hash_obj_file = f".lumina_cache/{project_name}.bin_hash"
    opt_marker = opt_flag

    cache_hit = False
    if (not is_wasm) and (not is_debug) and os.path.exists(hash_obj_file):
        # Só confiamos no cache se o BINÁRIO existe. Sem isso, um
        # `rm foo` (ou `mv foo foo_lumina`) seguido de `lumina build`
        # cairia em cache hit e nunca regeneraria o binário.
        if os.path.exists(output_path):
            with open(hash_obj_file, "r") as f:
                old_hash = f.read()
            combined = llvm_ir + "|" + opt_marker
            new_hash = hashlib.md5(combined.encode()).hexdigest()
            if old_hash == new_hash:
                cache_hit = True

    if cache_hit:
        success("✅ Build incremental: Nenhum código mudou. Pulando linkagem.")
        return output_path

    header("4. Linkagem Nativa")
    info(f"Executando: {paint(' '.join(cmd_args), Color.MUTED)}")

    try:
        subprocess.run(cmd_args, check=True)
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
        report_error(LuminaError(
            "Erro durante a linkagem com o clang. Veja a saída acima para detalhes.",
            entry, 0, 0, "",
        ))
        return None


def cmd_check(entry_file=None):
    if not entry_file:
        if os.path.exists("lumina.toml") and tomllib:
            with open("lumina.toml", "rb") as f:
                config = tomllib.load(f)
                entry_file = config.get("package", {}).get("entry", "main.lm")
        elif os.path.exists("main.lm"):
            entry_file = "main.lm"
        else:
            report_error("Nenhum arquivo de entrada especificado.")
            return False

    if not os.path.exists(entry_file):
        report_error(f"Arquivo '{entry_file}' não encontrado.")
        return False

    step(f"🔍 Verificando: {paint(entry_file, Color.BOLD + Color.BRIGHT_CYAN)}")
    ok = check_lumina(entry_file, on_error=report_error)
    if ok:
        success(f"✅ {paint(entry_file, Color.BOLD)} — sem erros")
    return ok


def cmd_run(entry_file=None, use_jit=False, extra_flags=[], cli_args=None):
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
            report_error("Nenhum arquivo de entrada especificado.")
            return 1

    if not os.path.exists(entry_file):
        report_error(f"Arquivo '{entry_file}' não encontrado.")
        return 1

    step(f"🚀 Iniciando processo para: {paint(entry_file, Color.BOLD + Color.BRIGHT_CYAN)}")

    if use_jit:
        ir_file = "lumina_jit_temp.ll"
        try:
            llvm_ir = compile_lumina(entry_file, output_file=ir_file, on_error=report_error)
            if not llvm_ir:
                return 1
            return run_jit(llvm_ir, cli_args or [])
        finally:
            if os.path.exists(ir_file):
                os.remove(ir_file)

    binary_name = cmd_build(entry_file, extra_flags=extra_flags)
    if not binary_name:
        return 1

    header("Executando Binário Nativo")
    exe_path = binary_name if os.path.isabs(binary_name) else f"./{binary_name}"
    result = subprocess.run([exe_path])
    return result.returncode