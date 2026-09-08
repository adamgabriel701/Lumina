import sys
import json
from lumina.lexer import Lexer
from lumina.parser import Parser
from lumina.semantic import SemanticAnalyzer
from lumina.ast import Function, VarDecl, StructDecl, EnumDecl
from lumina.errors import LuminaError

def read_message():
    headers = {}
    while True:
        line = sys.stdin.readline()
        if not line: return None
        line = line.strip()
        if not line: break
        key, value = line.split(': ', 1)
        headers[key] = value
    content_length = int(headers.get('Content-Length', 0))
    body = sys.stdin.read(content_length)
    return json.loads(body)

def write_message(msg):
    body = json.dumps(msg)
    sys.stdout.write(f"Content-Length: {len(body)}\r\n\r\n{body}")
    sys.stdout.flush()

def validate_and_extract_symbols(code):
    diagnostics = []
    symbols = {"functions": [], "vars": []}
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens, "lsp.lm", code)
        ast = parser.parse()
        
        # Extrai símbolos para Autocomplete e Hover
        for decl in ast:
            if isinstance(decl, Function):
                params_str = ", ".join([f"{p[0]}: {p[1]}" for p in decl.params])
                symbols["functions"].append({
                    "name": decl.name,
                    "detail": f"fn {decl.name}({params_str}) -> {decl.return_type}",
                    "line": 0 # Linha simplificada para o LSP
                })
            elif isinstance(decl, VarDecl):
                symbols["vars"].append({"name": decl.name, "detail": f"{decl.name}: {decl.var_type or 'inferred'}"})
                
        analyzer = SemanticAnalyzer("lsp.lm", code)
        analyzer.analyze(ast)
    except LuminaError as e:
        diagnostics.append({
            "range": {
                "start": {"line": max(0, e.line - 1), "character": max(0, e.col - 1)},
                "end": {"line": max(0, e.line - 1), "character": max(1, e.col)}
            },
            "severity": 1,
            "message": e.message
        })
    except Exception as e:
        pass # Ignora erros de parse incompletos durante a digitação
    return diagnostics, symbols

def get_completions(symbols):
    items = []
    # Palavras-chave da linguagem
    keywords = ['fn', 'let', 'mut', 'if', 'elif', 'else', 'while', 'for', 'in', 'return', 'print', 'true', 'false', 'match', 'case', 'default', 'and', 'or', 'not', 'struct', 'enum', 'extern', 'import', 'defer', 'break', 'continue']
    for kw in keywords:
        items.append({"label": kw, "kind": 14, "detail": "Lumina Keyword"})
    
    # Funções do usuário
    for func in symbols.get("functions", []):
        items.append({"label": func["name"], "kind": 3, "detail": func["detail"], "documentation": "Função definida no arquivo"})
        
    # Variáveis do usuário
    for var in symbols.get("vars", []):
        items.append({"label": var["name"], "kind": 6, "detail": var["detail"]})
        
    return items

def main():
    latest_symbols = {"functions": [], "vars": []}
    while True:
        msg = read_message()
        if not msg: break
        
        method = msg.get("method")
        params = msg.get("params", {})
        msg_id = msg.get("id")
        
        if method == "initialize":
            write_message({
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "capabilities": {
                        "textDocumentSync": 1,
                        "completionProvider": {"resolveProvider": False, "triggerCharacters": ["", "."]},
                        "hoverProvider": True
                    }
                }
            })
        elif method in ("textDocument/didOpen", "textDocument/didChange"):
            text = params.get("textDocument", {}).get("text", "")
            if not text:
                changes = params.get("contentChanges", [])
                if changes: text = changes[0].get("text", "")
            
            diagnostics, latest_symbols = validate_and_extract_symbols(text)
            write_message({
                "jsonrpc": "2.0",
                "method": "textDocument/publishDiagnostics",
                "params": {
                    "uri": params.get("textDocument", {}).get("uri", ""),
                    "diagnostics": diagnostics
                }
            })
        elif method == "textDocument/completion":
            write_message({
                "jsonrpc": "2.0", "id": msg_id,
                "result": {"isIncomplete": False, "items": get_completions(latest_symbols)}
            })
        elif method == "textDocument/hover":
            # Hover simples: se passar o mouse em uma função conhecida, mostra a assinatura
            word = params.get("position", {}).get("word", "") # Note: VS Code não envia 'word', mas para simplificar o LSP aqui
            # Como o VS Code não envia a palavra no hover, uma implementação real exigiria mapear a posição.
            # Vamos deixar um placeholder para provar que o capability está ativo.
            write_message({"jsonrpc": "2.0", "id": msg_id, "result": {"contents": "Lumina Language Server"}})
        elif method == "shutdown":
            write_message({"jsonrpc": "2.0", "id": msg_id, "result": None})
        elif method == "exit":
            break

if __name__ == "__main__":
    main()