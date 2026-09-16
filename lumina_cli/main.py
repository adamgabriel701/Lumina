import sys
import os

if __package__ in (None, ""):
    parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent not in sys.path:
        sys.path.insert(0, parent)
    __package__ = "lumina_cli"

from .utils import Color, paint, cprint, info, success, warn, error, step, header
from .commands import (
    cmd_new, cmd_build, cmd_clean, cmd_run, cmd_doc, cmd_install,
    cmd_bind, cmd_fmt, cmd_repl, cmd_test, cmd_check,
    set_error_format,
)
from .playground import run_server as run_playground


def usage():
    header("🌟 Lumina CLI")
    info("Uso: lumina <comando> [argumentos] [--error-format=text|json]")
    print()
    step("Comandos disponíveis:")
    commands = [
        ("new <nome>",                    "Cria um novo projeto Lumina"),
        ("build [arquivo] [flags]",       "Compila para binário nativo (-O2 padrão)"),
        ("run [arquivo]",                 "Compila e executa o binário nativo"),
        ("check [arquivo]",               "Só lexer+parser+semantic (rápido, sem codegen)"),
        ("test [arquivo]",                "Compila e executa a suíte de testes nativa"),
        ("jit [arquivo]",                 "Compila e executa via JIT (Just-In-Time)"),
        ("clean",                         "Limpa o cache e os binários gerados"),
        ("doc",                           "Gera documentação HTML do projeto"),
        ("install",                       "Baixa/instala dependências do lumina.toml"),
        ("bind <header.h> <nome>",        "Gera bindings Lumina a partir de um header C"),
        ("fmt <arquivo.lm>",              "Formata o código-fonte Lumina"),
        ("repl",                          "Inicia o REPL interativo"),
        ("playground [porta]",            "Inicia o playground web (padrão: 8080)"),
    ]
    for cmd, desc in commands:
        print(f"  {paint(cmd, Color.BOLD + Color.BRIGHT_CYAN)}  {paint(desc, Color.MUTED)}")
    print()
    info(f"Flags de build: {paint('--release (-O3)', Color.MUTED)}, "
         f"{paint('--debug (-O0 + DWARF)', Color.MUTED)}, "
         f"{paint('--wasm', Color.MUTED)}, "
         f"{paint('--no-gc', Color.MUTED)}")
    info(f"Exemplo: {paint('lumina new meu_projeto', Color.MUTED)}")


def main():
    args = sys.argv[1:]

    # ---- Extrai flags globais (--error-format) ----
    error_format = "text"
    filtered = []
    for arg in args:
        if arg.startswith("--error-format="):
            error_format = arg.split("=", 1)[1]
        else:
            filtered.append(arg)
    set_error_format(error_format)
    args = filtered

    if len(args) < 1:
        usage()
        return

    command = args[0]
    args = args[1:]

    if command == "new":
        if len(args) < 1:
            error("Uso: lumina new <nome_do_projeto>")
            return
        cmd_new(args[0])

    elif command == "build":
        entry_file = None
        extra_flags = []
        for arg in args:
            if not arg.startswith('-') and not entry_file:
                entry_file = arg
            elif arg.startswith('-'):
                extra_flags.append(arg)
        cmd_build(entry_file, extra_flags)

    elif command == "check":
        entry_file = args[0] if args and not args[0].startswith('-') else None
        ok = cmd_check(entry_file)
        if not ok:
            sys.exit(1)

    elif command == "test":
        entry_file = args[0] if args and not args[0].startswith('-') else None
        cmd_test(entry_file)

    elif command == "clean":
        cmd_clean()

    elif command == "run":
        entry_file = args[0] if args and not args[0].startswith('-') else None
        extra_flags = [arg for arg in args if arg.startswith('-')]
        cmd_run(entry_file, use_jit=False, extra_flags=extra_flags)

    elif command == "jit":
        entry_file = args[0] if args and not args[0].startswith('-') else None
        cmd_run(entry_file, use_jit=True)

    elif command == "doc":
        cmd_doc()

    elif command == "install":
        cmd_install()

    elif command == "bind":
        if len(args) < 2:
            error("Uso: lumina bind <c_header.h> <nome_modulo>")
            return
        cmd_bind(args[0], args[1])

    elif command == "fmt":
        if len(args) < 1:
            error("Uso: lumina fmt <arquivo.lm>")
            return
        cmd_fmt(args[0])

    elif command == "repl":
        cmd_repl()

    elif command == "playground":
        port = 8080
        if args and args[0].isdigit():
            port = int(args[0])
        run_playground(port=port)

    else:
        error(f"Comando desconhecido: {paint(command, Color.BOLD)}")
        print()
        usage()
        sys.exit(1)


if __name__ == "__main__":
    main()