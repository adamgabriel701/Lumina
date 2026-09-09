import http.server
import socketserver
import json
import sys
import os
import ctypes
import ctypes.util
from llvmlite import binding as llvm
from lumina.lexer import Lexer
from lumina.parser import Parser
from lumina.semantic import SemanticAnalyzer
from lumina.codegen import LLVMCodegen
from lumina.errors import LuminaError

# Inicializa o motor JIT nativo uma única vez
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()
lib_c_path = ctypes.util.find_library('c')
if lib_c_path: llvm.load_library_permanently(lib_c_path)

class PlaygroundHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('playground.html', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/compile':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            code = data.get('code', '')
            
            # NOVO: Indenta todas as linhas do código do usuário com 4 espaços
            indented_code = "\n    ".join(code.splitlines())
            full_code = f"fn main() -> int:\n    {indented_code}\n    return 0"
            
            try:
                lexer = Lexer(full_code)
                tokens = lexer.tokenize()
                parser = Parser(tokens, "playground.lm", full_code)
                ast = parser.parse()
                
                analyzer = SemanticAnalyzer("playground.lm", full_code)
                analyzer.analyze(ast)
                
                codegen = LLVMCodegen()
                llvm_ir = codegen.generate_module(ast)
                
                # Configura o JIT
                mod = llvm.parse_assembly(llvm_ir)
                mod.verify()
                target = llvm.Target.from_default_triple()
                tm = target.create_target_machine()
                engine = llvm.create_mcjit_compiler(mod, tm)
                engine.finalize_object()
                engine.run_static_constructors()

                func_ptr = engine.get_function_address("main")
                cfunc = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int32, ctypes.POINTER(ctypes.c_char_p))(func_ptr)
                
                # === NOVO: Intercepta o stdout do C nativo ===
                # Cria um pipe (tubo de comunicação)
                read_fd, write_fd = os.pipe()
                # Salva o stdout original do Python
                old_stdout = os.dup(1)
                # Redireciona o stdout (fd 1) para o nosso pipe
                os.dup2(write_fd, 1)
                
                # Executa o código Lumina na memória RAM
                cfunc(0, None)
                
                # Força o flush do buffer do C (printf)
                ctypes.CDLL(None).fflush(None)
                
                # Restaura o stdout original do Python
                os.dup2(old_stdout, 1)
                os.close(write_fd)
                
                # Lê o que o código Lumina imprimiu no pipe
                output_bytes = os.read(read_fd, 65536)
                os.close(read_fd)
                
                output_str = output_bytes.decode('utf-8')
                if not output_str:
                    output_str = "(Código executado, mas não produziu nenhuma saída.)"
                
                response = {"success": True, "output": output_str}
                
            except LuminaError as e:
                # Se for erro de sintaxe/semântica, formata bonito para o navegador
                msg = str(e).replace("\n", "<br>")
                response = {"success": False, "output": msg}
            except Exception as e:
                response = {"success": False, "output": f"Erro interno do Compilador:\n{str(e)}"}
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

def run_server(port=8080):
    with socketserver.TCPServer(("", port), PlaygroundHandler) as httpd:
        print(f"🚀 Lumina Playground rodando em http://localhost:{port}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()