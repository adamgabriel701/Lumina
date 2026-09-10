import sys
import os
import json
import subprocess
import glob
import ctypes
import ctypes.util
import re
import hashlib
try:
    import tomllib # Python 3.11+
except ImportError:
    tomllib = None
from llvmlite import binding as llvm
from lumina.ast import Function, VarDecl, AssignStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt, NumberExpr, StringExpr, VariableExpr, BinaryExpr, CallExpr, MemberExpr, IndexExpr
from lumina.lexer import Lexer
from lumina.parser import Parser
from lumina.semantic import SemanticAnalyzer
from lumina.codegen import LLVMCodegen
from lumina.ast import ImportStmt
from lumina.errors import LuminaError

# --- Helpers de Cache ---
def get_all_dependency_files(filename):
    """Faz um scan rápido para encontrar todos os arquivos .lm envolvidos na compilação."""
    files = set()
    def resolve(f):
        abs_f = os.path.abspath(f)
        if abs_f in files: return
        files.add(abs_f)
        try:
            with open(f, "r") as file:
                code = file.read()
        except: return
            
        # Regex para encontrar imports rapidamente sem fazer parse completo
        for match in re.finditer(r'import\s+"([^"]+)"', code):
            dep = match.group(1)
            if dep.startswith("std/"):
                cli_dir = os.path.dirname(os.path.abspath(__file__))
                dep_path = os.path.join(cli_dir, "std", dep.replace("std/", "") + ".lm")
            elif os.path.exists(dep + ".lm" if not dep.endswith(".lm") else dep):
                dep_path = dep if dep.endswith(".lm") else dep + ".lm"
            else:
                dep_path = os.path.join("lumina_modules", dep)
                if not dep_path.endswith(".lm"): dep_path += ".lm"
            resolve(dep_path)
            
    resolve(filename)
    return list(files)

def get_cache_hash(filename):
    """Calcula um hash MD5 baseado no conteúdo de todos os arquivos do projeto."""
    hasher = hashlib.md5()
    deps = get_all_dependency_files(filename)
    for f in sorted(deps):
        try:
            with open(f, "rb") as file:
                hasher.update(file.read())
        except: pass
    return hasher.hexdigest()

# --- Módulos do Compilador ---
def parse_module(filename, current_stack=None):
    abs_path = os.path.abspath(filename)
    if current_stack is None:
        current_stack = set()
    if abs_path in current_stack:
        raise LuminaError(f"Importação circular detectada envolvendo '{filename}'.", filename, 0, 0, "")
        
    current_stack.add(abs_path)
    
    resolved_ast = []
    
    # NOVO: Injeta o Prelude automaticamente se for o arquivo principal
    if len(current_stack) == 1:
        cli_dir = os.path.dirname(os.path.abspath(__file__))
        prelude_path = os.path.join(cli_dir, "std", "prelude.lm")
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
                cli_dir = os.path.dirname(os.path.abspath(__file__))
                clean_name = node.filename.replace("std/", "")
                if clean_name.endswith(".lm"): clean_name = clean_name[:-3]
                std_path = os.path.join(cli_dir, "std", clean_name + ".lm")
                imported_ast = parse_module(std_path, current_stack)
            elif os.path.exists(node.filename if node.filename.endswith(".lm") else node.filename + ".lm"):
                imported_path = node.filename if node.filename.endswith(".lm") else node.filename + ".lm"
                imported_ast = parse_module(imported_path, current_stack)
            else:
                mod_path = os.path.join("lumina_modules", node.filename)
                if not mod_path.endswith(".lm"): mod_path += ".lm"
                if not os.path.exists(mod_path):
                    raise LuminaError(f"Módulo '{node.filename}' não encontrado.", filename, 0, 0, code)
                imported_ast = parse_module(mod_path, current_stack)
            print(f"--> Importando módulo: {node.filename}")
            resolved_ast.extend(imported_ast)
        else:
            resolved_ast.append(node)
            
    current_stack.remove(abs_path)
    return resolved_ast

def compile_lumina(filename, output_file="output.ll", use_cache=True):
    cache_dir = ".lumina_cache"
    cache_file = os.path.join(cache_dir, get_cache_hash(filename) + ".ll") if use_cache else None
    
    if use_cache and os.path.exists(cache_file):
        print("⚡ Usando cache de compilação (.lumina_cache)...")
        with open(cache_file, "r") as f:
            llvm_ir = f.read()
        with open(output_file, "w") as f: f.write(llvm_ir)
        return llvm_ir

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
    # 1. Cria a instância do Codegen
    codegen = LLVMCodegen()
    
    # 2. Passa a informação de quem foge (escapes) do Semantic para o Codegen
    codegen.escapes = analyzer.escapes
    
    # 3. Gera o módulo LLVM IR
    llvm_ir = codegen.generate_module(ast)
    
    with open(output_file, "w") as f: f.write(llvm_ir)
    
    if use_cache:
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_file, "w") as f: f.write(llvm_ir)
        
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
    
    # NOVO: Gera lumina.toml em vez de lumina.json
    config = f"""[package]
name = "{project_name}"
version = "0.1.0"
entry = "main.lm"

[dependencies]
"""
    with open(os.path.join(project_name, "lumina.toml"), "w") as f:
        f.write(config)
        
    main_code = """fn main() -> int:
    print("Hello from """ + project_name + """!")
    return 0
"""
    with open(os.path.join(project_name, "main.lm"), "w") as f:
        f.write(main_code)
        
    print(f"✅ Projeto '{project_name}' criado com sucesso (lumina.toml)!")

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
    
    for filepath in glob.glob("**/*.lm", recursive=True):
        if "lumina_modules" in filepath or filepath.startswith("std/"): continue
        
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
            elif current_doc and (stripped.startswith("fn ") or stripped.startswith("struct ") or stripped.startswith("enum ")):
                clean_decl = stripped
                if stripped.startswith("fn "):
                    clean_decl = stripped.replace("fn ", "").replace(" -> ", " ⟶ ")
                
                docs_data.append({
                    "file": filepath,
                    "type": "Function" if stripped.startswith("fn ") else ("Struct" if stripped.startswith("struct ") else "Enum"),
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
        
    print("✅ Documentação gerada com sucesso em: docs/index.html")

def cmd_build(entry_file=None, extra_flags=[]):
    if entry_file:
        entry = entry_file
        project_name = entry_file.replace('.lm', '')
        libs = []
    else:
        # NOVO: Procura lumina.toml em vez de lumina.json
        if not os.path.exists("lumina.toml"):
            print("❌ Erro: Nenhum arquivo 'lumina.toml' encontrado no diretório atual.")
            return None
            
        with open("lumina.toml", "rb") as f:
            config = tomllib.load(f)
            
        entry = config.get("package", {}).get("entry", "main.lm")
        project_name = config.get("package", {}).get("name", "programa_final")
        libs = config.get("dependencies", {}).keys()
        
    print(f"🛠️  Compilando projeto: {project_name}")
    llvm_ir = compile_lumina(entry)
    if not llvm_ir: return None
    
    link_flags = " ".join([f"-l{lib}" for lib in libs] + extra_flags)
    ir_file = f"{project_name}.ll"
    with open(ir_file, "w") as f: f.write(llvm_ir)
    
    # NOVO: Verifica a flag --no-gc para compilação Bare-Metal
    is_no_gc = "--no-gc" in extra_flags
    gc_flag = "" if is_no_gc else "-lgc"
    
    if is_no_gc:
        print("⚠️ Modo Bare-Metal (--no-gc): Garbage Collector desativado.")
        cmd = f"clang -O3 -march=native -funroll-loops {ir_file} -o {project_name} {link_flags} -lc -lpthread"
    else:
        cmd = f"clang -O3 -march=native -funroll-loops {ir_file} -o {project_name} {link_flags} -lc -lpthread {gc_flag}"
        
    print("\n--- 4. Linkagem Nativa ---")
    print(f"Executando: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Build concluído: ./{project_name}")
        return project_name
    except subprocess.CalledProcessError:
        print("❌ Erro durante a linkagem com o clang.")
        return None

def cmd_clean():
    """Limpa o cache de compilação e os binários gerados."""
    print("🧹 Limpando cache e binários...")
    
    # Remove a pasta de cache
    if os.path.exists(".lumina_cache"):
        subprocess.run(["rm", "-rf", ".lumina_cache"])
        print("✅ Cache (.lumina_cache) removido.")
        
    # Remove arquivos LLVM IR (.ll) soltos na raiz
    for f in glob.glob("*.ll"):
        os.remove(f)
        print(f"✅ Removido: {f}")
        
    # Remove binários sem extensão (gerados pelo build)
    for f in os.listdir("."):
        if os.path.isfile(f) and "." not in f:
            # Evita deletar arquivos de sistema ocultos ou scripts
            if not f.startswith("."):
                os.remove(f)
                print(f"✅ Removido binário: {f}")
                
    print("Limpeza concluída!")

def cmd_run(entry_file=None, use_jit=False):
    """Compila (usando cache se possível) e executa o programa."""
    if not entry_file:
        if os.path.exists("lumina.json"):
            with open("lumina.json", "r") as f:
                config = json.load(f)
                entry_file = config.get("entry", "main.lm")
        elif os.path.exists("main.lm"):
            entry_file = "main.lm"
        else:
            print("❌ Erro: Nenhum arquivo de entrada especificado.")
            return

    if not os.path.exists(entry_file):
        print(f"❌ Erro: Arquivo '{entry_file}' não encontrado.")
        return

    print(f"🚀 Iniciando processo para: {entry_file}")
    
    # Compila o código (usando o cache incremental se não houver mudanças)
    binary_name = cmd_build(entry_file)
    
    if not binary_name:
        print("❌ Falha na compilação.")
        return
        
    print("\n--- Executando Binário Nativo ---")
    # Executa o binário gerado
    subprocess.run([f"./{binary_name}"])

def cmd_bind(header_file, output_name):
    if not os.path.exists(header_file):
        print(f"❌ Erro: Arquivo '{header_file}' não encontrado.")
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
                    arg_type_clean = arg_type.replace("*", "").strip()
                    lumina_type = c_type_map.get(arg_type, "str")
                    lumina_args.append(f"{arg_name}: {lumina_type}")
                else:
                    lumina_args.append(f"arg: str")
                    
        lumina_decls.append(f"extern fn {name}({', '.join(lumina_args)}) -> {ret_type}")
        
    if not lumina_decls:
        print("Nenhuma função válida encontrada no cabeçalho.")
        return
        
    out_file = f"std/{output_name}.lm"
    os.makedirs("std", exist_ok=True)
    with open(out_file, "w") as f:
        f.write(f"# Auto-gerado de {header_file} pelo Lumina Bind\n\n")
        f.write("\n".join(lumina_decls))
        
    print(f"✅ Bindings gerados com sucesso em {out_file} ({len(lumina_decls)} funções)")

# --- Auto-Formatter (lumina fmt) ---
def format_node(node, indent_level=0):
    indent = "    " * indent_level
    
    if isinstance(node, (Function, )):
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
        
    # NOVO: Expressões sabem se devem adicionar indentação e \n baseado no indent_level
    elif isinstance(node, NumberExpr):
        if indent_level > 0: return f"{indent}{node.value}\n"
        return node.value
        
    elif isinstance(node, StringExpr):
        if indent_level > 0: return f"{indent}\"{node.value}\"\n"
        return f"\"{node.value}\""
        
    elif isinstance(node, VariableExpr):
        if indent_level > 0: return f"{indent}{node.name}\n"
        return node.name
        
    elif isinstance(node, BinaryExpr):
        left = format_node(node.left, 0)
        right = format_node(node.right, 0)
        if indent_level > 0: return f"{indent}{left} {node.op} {right}\n"
        return f"{left} {node.op} {right}"
        
    elif isinstance(node, CallExpr):
        args = ", ".join([format_node(a, 0) for a in node.args])
        if indent_level > 0: return f"{indent}{node.name}({args})\n"
        return f"{node.name}({args})"
        
    elif isinstance(node, MemberExpr):
        obj = format_node(node.obj, 0)
        if indent_level > 0: return f"{indent}{obj}.{node.member}\n"
        return f"{obj}.{node.member}"
        
    elif isinstance(node, IndexExpr):
        arr = format_node(node.array, 0)
        idx = format_node(node.index, 0)
        if indent_level > 0: return f"{indent}{arr}[{idx}]\n"
        return f"{arr}[{idx}]"
        
    return f"{indent}{str(node)}\n"

def cmd_fmt(filename):
    if not os.path.exists(filename):
        print(f"❌ Erro: Arquivo '{filename}' não encontrado.")
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
            
        # Salva o código formatado de volta no arquivo
        with open(filename, "w") as f:
            f.write(formatted_code)
            
        print(f"✅ Arquivo '{filename}' formatado com sucesso!")
        
    except LuminaError as e:
        print("❌ Não foi possível formatar devido a erros de sintaxe:")
        print(e)

def cmd_repl():
    print("Lumina REPL 1.0")
    print("Digite seu código. Pressione ENTER numa linha vazia para executar.")
    print("Digite 'exit' para sair.")
    print("----------------------------------------------------------")
    
    # Inicializa o motor JIT nativo uma única vez
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()
    lib_c_path = ctypes.util.find_library('c')
    if lib_c_path: llvm.load_library_permanently(lib_c_path)
    
    buffer = []
    
    while True:
        try:
            # Se o buffer estiver vazio, mostra "lumina>", senão mostra "..."
            prompt = "lumina> " if not buffer else "... "
            line = input(prompt)
            
            if line.strip().lower() in ("exit", "quit"):
                break
                
            # Se o usuário pressionou Enter numa linha vazia
            if not line.strip():
                if not buffer:
                    continue # Continua esperando código
                
                # Junta todo o buffer digitado em um único código
                code = "fn main() -> int:\n    " + "\n    ".join(buffer) + "\n    return 0"
                
                try:
                    # Lexa, parsea, analisa e gera o IR
                    lexer = Lexer(code)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens, "repl.lm", code)
                    ast = parser.parse()
                    
                    analyzer = SemanticAnalyzer("repl.lm", code)
                    analyzer.analyze(ast)
                    
                    codegen = LLVMCodegen()
                    llvm_ir = codegen.generate_module(ast)
                    
                    # Executa na memória RAM via MCJIT
                    mod = llvm.parse_assembly(llvm_ir)
                    mod.verify()
                    target = llvm.Target.from_default_triple()
                    tm = target.create_target_machine()
                    engine = llvm.create_mcjit_compiler(mod, tm) # CORREÇÃO AQUI
                    engine.finalize_object()
                    engine.run_static_constructors()

                    func_ptr = engine.get_function_address("main")
                    cfunc = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.POINTER(ctypes.c_char_p))(func_ptr)
                    cfunc(0, None)
                    
                except LuminaError as e:
                    # Se der erro de sintaxe ou semântica, imprime e continua
                    print(e)
                except Exception as e:
                    print(f"Erro interno: {e}")
                finally:
                    # Limpa o buffer para a próxima execução
                    buffer = []
                continue
                
            # Adiciona a linha ao buffer
            buffer.append(line)
            
        except KeyboardInterrupt:
            print("\n(Buffer limpo. Digite 'exit' para sair)")
            buffer = []
        except EOFError:
            break
                
def main():
    if len(sys.argv) < 2:
        print("Uso: python3 lumina_cli.py <comando> [argumentos]")
        print("Comandos: new, build, run, jit, doc, install, bind, fmt, repl")
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "new":
        if len(args) < 1:
            print("Uso: python3 lumina_cli.py new <nome_do_projeto>")
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
        
    # NOVO COMANDO: CLEAN
    elif command == "clean":
        cmd_clean()
        
    # NOVO COMANDO: RUN (Compila e já roda o binário nativo)
    elif command == "run":
        entry_file = args[0] if args and not args[0].startswith('-') else None
        cmd_run(entry_file, use_jit=False)
        
    elif command == "jit":
        entry = args[0] if args and not args[0].startswith('-') else None
        extra_flags = [arg for arg in args if arg.startswith('-') and arg != '--run']
        cmd_run(args, use_jit=True, extra_flags=extra_flags)
        
    elif command == "doc":
        cmd_doc()
        
    elif command == "install":
        cmd_install()
        
    elif command == "bind":
        if len(args) < 2:
            print("Uso: python3 lumina_cli.py bind <c_header.h> <nome_modulo>")
            return
        cmd_bind(args[0], args[1])
        
    elif command == "fmt":
        if len(args) < 1:
            print("Uso: python3 lumina_cli.py fmt <arquivo.lm>")
            return
        cmd_fmt(args[0])
        
    # NOVO COMANDO: REPL
    elif command == "repl":
        cmd_repl()
        
    else:
        print(f"Comando desconhecido: {command}")

if __name__ == "__main__":
    main()