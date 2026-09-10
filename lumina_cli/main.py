import sys
import os

# --- Bootstrap de imports ---
# Permite executar de 3 formas:
#   1) python3 -m lumina_cli.main <cmd>      (a partir de /workspaces/Lumina)
#   2) python3 lumina_cli/main.py <cmd>      (a partir de /workspaces/Lumina)
#   3) python3 main.py <cmd>                 (a partir de dentro de lumina_cli/)
if __package__ in (None, ""):
    parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent not in sys.path:
        sys.path.insert(0, parent)
    __package__ = "lumina_cli"

from .utils import Color, paint, cprint, info, success, warn, error, step, header
from .commands import (
    cmd_new, cmd_build, cmd_clean, cmd_run, cmd_doc, cmd_install,
    cmd_bind, cmd_fmt, cmd_repl, cmd_test, # NOVO
)
from .playground import run_server as run_playground


def usage():
    header("🌟 Lumina CLI")
    info("Uso: python3 -m lumina_cli.main <comando> [argumentos]")
    print()
    step("Comandos disponíveis:")
    commands = [
        ("new <nome>",                    "Cria um novo projeto Lumina"),
        ("build [arquivo] [--no-gc]",     "Compila o projeto para um binário nativo"),
        ("run [arquivo]",                  "Compila e executa o binário nativo"),
        ("test [arquivo]",                 "Compila e executa a suíte de testes nativa"), # NOVO
        ("jit [arquivo]",                  "Compila e executa via JIT (Just-In-Time)"),
        ("clean",                          "Limpa o cache e os binários gerados"),
        ("doc",                            "Gera documentação HTML do projeto"),
        ("install",                        "Baixa/instala dependências do lumina.json"),
        ("bind <header.h> <nome>",         "Gera bindings Lumina a partir de um header C"),
        ("fmt <arquivo.lm>",               "Formata o código-fonte Lumina"),
        ("repl",                           "Inicia o REPL interativo"),
        ("playground [porta]",             "Inicia o playground web (padrão: 8080)"),
    ]
    for cmd, desc in commands:
        print(f"  {paint(cmd, Color.BOLD + Color.BRIGHT_CYAN)}  {paint(desc, Color.MUTED)}")
    print()
    info(f"Exemplo: {paint('python3 -m lumina_cli.main new meu_projeto', Color.MUTED)}")


def main():
    if len(sys.argv) < 2:
        usage()
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "new":
        if len(args) < 1:
            error("Uso: python3 -m lumina_cli.main new <nome_do_projeto>")
            return
        cmd_new(args[0])

    elif command == "build":
        if not args:
            entry_file = None
            extra_flags = []
        else:
            entry_file = None
            for arg in args:
                if not arg.startswith('-'):
                    entry_file = arg
                    break
            extra_flags = [arg for arg in args if arg.startswith('-')]
        cmd_build(entry_file, extra_flags)

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
            error("Uso: python3 -m lumina_cli.main bind <c_header.h> <nome_modulo>")
            return
        cmd_bind(args[0], args[1])

    elif command == "fmt":
        if len(args) < 1:
            error("Uso: python3 -m lumina_cli.main fmt <arquivo.lm>")
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


if __name__ == "__main__":
    main()