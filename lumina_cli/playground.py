import os
import json
import ctypes
import ctypes.util
import http.server
import socketserver

from llvmlite import binding as llvm

from lumina.lexer import Lexer
from lumina.parser import Parser
from lumina.semantic import SemanticAnalyzer
from lumina.codegen import LLVMCodegen
from lumina.errors import LuminaError

from .utils import Color, paint, info, success, warn, error, step, LUMINA_ROOT


# Inicializa o motor JIT nativo uma única vez
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()
lib_c_path = ctypes.util.find_library('c')
if lib_c_path:
    llvm.load_library_permanently(lib_c_path)


def _find_playground_html():
    """Procura playground.html no diretório atual e no raiz do projeto."""
    candidates = [
        "playground.html",
        os.path.join(LUMINA_ROOT, "playground.html"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


class PlaygroundHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            html_path = _find_playground_html()
            if html_path is None:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"playground.html nao encontrado.")
                return
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(html_path, 'rb') as f:
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

                # Intercepta o stdout do C nativo
                read_fd, write_fd = os.pipe()
                old_stdout = os.dup(1)
                os.dup2(write_fd, 1)

                cfunc(0, None)
                ctypes.CDLL(None).fflush(None)

                os.dup2(old_stdout, 1)
                os.close(write_fd)

                output_bytes = os.read(read_fd, 65536)
                os.close(read_fd)

                output_str = output_bytes.decode('utf-8')
                if not output_str:
                    output_str = "(Código executado, mas não produziu nenhuma saída.)"

                response = {"success": True, "output": output_str}

            except LuminaError as e:
                msg = str(e).replace("\n", "<br>")
                response = {"success": False, "output": msg}
            except Exception as e:
                response = {"success": False, "output": f"Erro interno do Compilador:\n{str(e)}"}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))


def run_server(port=8080):
    step(f"🚀 Lumina Playground rodando em {paint(f'http://localhost:{port}', Color.INFO + Color.UNDERLINE)}")
    info(f"Pressione {paint('Ctrl+C', Color.BOLD)} para parar o servidor.")
    with socketserver.TCPServer(("", port), PlaygroundHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            warn("\nServidor interrompido pelo usuário.")