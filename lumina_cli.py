import sys
import os
import json
import subprocess
import glob
import ctypes
import ctypes.util
from llvmlite import binding as llvm
from lumina.lexer import Lexer
from lumina.parser import Parser
from lumina.semantic import SemanticAnalyzer
from lumina.codegen import LLVMCodegen
from lumina.ast import ImportStmt
from lumina.errors import LuminaError

# --- Módulos do Compilador ---
def parse_module(filename):
    with open(filename, "r") as f:
        code = f.read()
        
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, filename, code)
    ast = parser.parse()
    
    resolved_ast = []
    for node in ast:
        if isinstance(node, ImportStmt):
            # 1. Se for da stdlib (std/)
            if node.filename.startswith("std/"):
                cli_dir = os.path.dirname(os.path.abspath(__file__))
                std_path = os.path.join(cli_dir, "std", node.filename.replace("std/", "") + ".lm")
                imported_ast = parse_module(std_path)
                
            # 2. Se for um arquivo local
            elif os.path.exists(node.filename + ".lm" if not node.filename.endswith(".lm") else node.filename):
                imported_path = node.filename if node.filename.endswith(".lm") else node.filename + ".lm"
                imported_ast = parse_module(imported_path)
                
            # 3. NOVO: Se for um pacote baixado (lumina_modules/)
            else:
                mod_path = os.path.join("lumina_modules", node.filename)
                if not mod_path.endswith(".lm"):
                    mod_path += ".lm"
                    
                if not os.path.exists(mod_path):
                    raise LuminaError(f"Módulo '{node.filename}' não encontrado localmente, na stdlib ou em lumina_modules/.", filename, 0, 0, code)
                    
                imported_ast = parse_module(mod_path)
                
            print(f"--> Importando módulo: {node.filename}")
            resolved_ast.extend(imported_ast)
        else:
            resolved_ast.append(node)
    return resolved_ast

def compile_lumina(filename, output_file="output.ll"):
    print("--- 1. Análise Léxica e Sintática ---")
    try:
        ast = parse_module(filename)
    except LuminaError as e:
        print(e); return None
        
    print("\n--- 2. Análise Semântica ---")
    with open(filename, "r") as f: source_code = f.read()
    analyzer = SemanticAnalyzer(filename, source_code)
    try:
        analyzer.analyze(ast)
    except LuminaError as e:
        print(e); return None
    
    print("\n--- 3. Geração de Código LLVM IR ---")
    codegen = LLVMCodegen()
    llvm_ir = codegen.generate_module(ast)
    
    with open(output_file, "w") as f: f.write(llvm_ir)
    return llvm_ir

def run_jit(llvm_ir, cli_args):
    print("\n--- Execução JIT (Just-In-Time) ---")
    try:
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
    except: pass
    
    lib_c_path = ctypes.util.find_library('c')
    if lib_c_path: llvm.load_library_permanently(lib_c_path)

    mod = llvm.parse_assembly(llvm_ir)
    mod.verify()
    target = llvm.Target.from_default_triple()
    tm = target.create_target_machine()
    engine = llvm.create_mcjit_compiler(mod, tm)
    engine.finalize_object()
    engine.run_static_constructors()

    func_ptr = engine.get_function_address("main")
    cfunc = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.POINTER(ctypes.c_char_p))(func_ptr)
    
    full_args = ["lumina_program"] + cli_args
    argc = len(full_args)
    argv = [arg.encode('utf-8') for arg in full_args]
    
    print("Executando...\n")
    ret = cfunc(argc, (ctypes.c_char_p * len(argv))(*argv))
    ctypes.CDLL(None).fflush(None)
    print(f"\n[JIT] Programa finalizado com exit code: {ret}")

# --- Comandos da CLI ---
def cmd_new(project_name):
    os.makedirs(project_name, exist_ok=True)
    
    # NOVO: lumina.json agora tem campo de dependências
    config = {
        "name": project_name,
        "entry": "main.lm",
        "libs": [],
        "dependencies": {}
    }
    with open(os.path.join(project_name, "lumina.json"), "w") as f:
        json.dump(config, f, indent=2)
        
    main_code = """fn main() -> int:
    print("Hello from """ + project_name + """!")
    return 0
"""
    with open(os.path.join(project_name, "main.lm"), "w") as f:
        f.write(main_code)
        
    print(f"✅ Projeto '{project_name}' criado com sucesso!")

# NOVO COMANDO: INSTALL
def cmd_install():
    if not os.path.exists("lumina.json"):
        print("❌ Erro: Nenhum arquivo 'lumina.json' encontrado no diretório atual.")
        return
        
    with open("lumina.json", "r") as f:
        config = json.load(f)
        
    deps = config.get("dependencies", {})
    if not deps:
        print("Nenhuma dependência encontrada no lumina.json.")
        return
        
    os.makedirs("lumina_modules", exist_ok=True)
    
    for pkg_name, source in deps.items():
        # Formato esperado: "github:usuario/repo"
        if not source.startswith("github:"):
            print(f"⚠️  Fonte inválida para {pkg_name}. Use o formato 'github:usuario/repo'.")
            continue
            
        repo_path = source.split(":")[1]
        url = f"https://github.com/{repo_path}.git"
        dest = os.path.join("lumina_modules", pkg_name)
        
        if os.path.exists(dest):
            print(f"🔄 Atualizando pacote '{pkg_name}'...")
            subprocess.run(["git", "-C", dest, "pull"], check=True)
        else:
            print(f"⬇️  Baixando pacote '{pkg_name}' de {url}...")
            try:
                subprocess.run(["git", "clone", url, dest], check=True)
                print(f"✅ Pacote '{pkg_name}' instalado em lumina_modules/{pkg_name}")
            except subprocess.CalledProcessError:
                print(f"❌ Falha ao baixar o repositório {url}")

def cmd_doc():
    print("📚 Gerando documentação...")
    docs_data = []
    
    # Encontra todos os arquivos .lm na pasta atual e subpastas
    for filepath in glob.glob("**/*.lm", recursive=True):
        with open(filepath, "r") as f:
            lines = f.readlines()
            
        current_doc = []
        for line in lines:
            stripped = line.strip()
            
            # Se for um comentário de documentação (##)
            if stripped.startswith("## "):
                current_doc.append(stripped[3:])
            elif stripped.startswith("##"):
                current_doc.append(stripped[2:])
            # Se for uma linha vazia ou comentário normal, limpa o doc atual
            elif stripped == "" or stripped.startswith("#"):
                current_doc = []
            # Se for uma declaração (fn, struct, enum) e tivermos um doc acumulado
            elif current_doc and (stripped.startswith("fn ") or stripped.startswith("struct ") or stripped.startswith("enum ")):
                # Limpa a sintaxe para ficar bonito no HTML (remove indentação extra)
                clean_decl = stripped
                
                # Separa parâmetros de função para formatar melhor
                if stripped.startswith("fn "):
                    clean_decl = stripped.replace("fn ", "").replace(" -> ", " ⟶ ")
                
                docs_data.append({
                    "file": filepath,
                    "type": "Function" if stripped.startswith("fn ") else ("Struct" if stripped.startswith("struct ") else "Enum"),
                    "decl": clean_decl,
                    "doc": "\n".join(current_doc)
                })
                current_doc = [] # Reseta o doc

    # Gera o HTML
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
        
    print("✅ Documentação gerada com sucesso em: docs/index.html")

def cmd_build(entry_file=None):
    # NOVO: Se um arquivo for passado, usa ele. Senão, lê o lumina.json
    if entry_file:
        entry = entry_file
        project_name = entry_file.replace('.lm', '')
        libs = []
    else:
        if not os.path.exists("lumina.json"):
            print("❌ Erro: Nenhum arquivo 'lumina.json' encontrado no diretório atual.")
            return None
            
        with open("lumina.json", "r") as f:
            config = json.load(f)
            
        entry = config.get("entry", "main.lm")
        project_name = config.get("name", "programa_final")
        libs = config.get("libs", [])
        
    print(f"🛠️  Compilando projeto: {project_name}")
    llvm_ir = compile_lumina(entry)
    if not llvm_ir: return None
    
    link_flags = " ".join([f"-l{lib}" for lib in libs])
    # Muda o output.ll para o mesmo nome do projeto para não sobrescrever
    ir_file = f"{project_name}.ll"
    with open(ir_file, "w") as f: f.write(llvm_ir)
    
    cmd = f"clang -O2 {ir_file} -o {project_name} {link_flags}"
    
    print("\n--- 4. Linkagem Nativa ---")
    print(f"Executando: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Build concluído: ./{project_name}")
        return project_name
    except subprocess.CalledProcessError:
        print("❌ Erro durante a linkagem com o clang.")
        return None

def cmd_run(args, use_jit=False):
    # NOVO: Define o arquivo de entrada padrão
    entry = "program.lm"
    
    # Se o usuário passou o nome do arquivo, usa ele
    if args and not args[0].startswith('--'):
        entry = args[0]
        args = args[1:]
    # Senão, se existir um lumina.json, lê a config
    elif os.path.exists("lumina.json"):
        with open("lumina.json", "r") as f:
            config = json.load(f)
            entry = config.get("entry", "main.lm")
    # Senão, se existir um main.lm, usa ele
    elif os.path.exists("main.lm"):
        entry = "main.lm"
        
    if not os.path.exists(entry):
        print(f"❌ Erro: Arquivo de entrada '{entry}' não encontrado.")
        return
        
    print(f"🚀 Executando via JIT: {entry}")
    llvm_ir = compile_lumina(entry)
    if llvm_ir: run_jit(llvm_ir, args)

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 lumina_cli.py <comando> [argumentos]")
        print("Comandos: new, build, run, jit, doc, install")
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "new":
        if len(args) < 1:
            print("Uso: python3 lumina_cli.py new <nome_do_projeto>")
            return
        cmd_new(args[0])
        
    elif command == "build":
        entry_file = args[0] if args else None
        cmd_build(entry_file)
        
    elif command == "run":
        cmd_run(args, use_jit=False)
        
    elif command == "jit":
        cmd_run(args, use_jit=True)
        
    elif command == "doc":
        cmd_doc()
        
    # NOVO COMANDO NA CLI
    elif command == "install":
        cmd_install()
        
    else:
        print(f"Comando desconhecido: {command}")

if __name__ == "__main__":
    main()