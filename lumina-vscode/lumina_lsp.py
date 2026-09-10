import sys
import json
from lumina.lexer import Lexer
from lumina.parser import Parser
from lumina.semantic import SemanticAnalyzer
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

def get_word_at_position(text, line, char):
    lines = text.split('\n')
    if line >= len(lines): return ""
    line_str = lines[line]
    if char >= len(line_str): return ""
    
    start = char
    while start > 0 and (line_str[start-1].isalnum() or line_str[start-1] == '_'):
        start -= 1
    end = char
    while end < len(line_str) and (line_str[end].isalnum() or line_str[end] == '_'):
        end += 1
    return line_str[start:end]

def validate_and_extract_symbols(code):
    diagnostics = []
    symbols = {"functions": [], "vars": []}
    definitions = {}
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens, "lsp.lm", code)
        ast = parser.parse()
        
        for decl in ast:
            if isinstance(decl, Function):
                params_str = ", ".join([f"{p[0]}: {p[1]}" for p in decl.params])
                symbols["functions"].append({
                    "name": decl.name,
                    "detail": f"fn {decl.name}({params_str}) -> {decl.return_type}",
                    "line": decl.line
                })
                definitions[decl.name] = {"line": decl.line - 1, "col": decl.col - 1}
            elif isinstance(decl, VarDecl):
                symbols["vars"].append({"name": decl.name, "detail": f"{decl.name}: {decl.var_type or 'inferred'}", "line": decl.line})
                definitions[decl.name] = {"line": decl.line - 1, "col": decl.col - 1}
                
        analyzer = SemanticAnalyzer("lsp.lm", code)
        analyzer.analyze(ast)
        definitions.update({k: {"line": v[1] - 1, "col": v[2] - 1} for k, v in analyzer.definition_locations.items()})
        
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
        pass
    return diagnostics, symbols, definitions

class LuminaLSP:
    def __init__(self):
        self.latest_text = ""
        self.latest_definitions = {}

    def run(self):
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
                            "hoverProvider": True,
                            "definitionProvider": True
                        }
                    }
                })
            elif method in ("textDocument/didOpen", "textDocument/didChange"):
                text = params.get("textDocument", {}).get("text", "")
                if not text:
                    changes = params.get("contentChanges", [])
                    if changes: text = changes[0].get("text", "")
                
                self.latest_text = text
                diagnostics, symbols, defs = validate_and_extract_symbols(text)
                self.latest_definitions = defs
                
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
                    "result": {"isIncomplete": False, "items": self.get_completions()}
                })
            elif method == "textDocument/hover":
                write_message({"jsonrpc": "2.0", "id": msg_id, "result": {"contents": "Lumina Language Server"}})
            elif method == "textDocument/definition":
                pos = params.get("position", {})
                line = pos.get("line", 0)
                char = pos.get("character", 0)
                word = get_word_at_position(self.latest_text, line, char)
                
                def_loc = self.latest_definitions.get(word)
                if def_loc:
                    result = {
                        "uri": params.get("textDocument", {}).get("uri", ""),
                        "range": {
                            "start": {"line": def_loc["line"], "character": def_loc["col"]},
                            "end": {"line": def_loc["line"], "character": def_loc["col"] + len(word)}
                        }
                    }
                    write_message({"jsonrpc": "2.0", "id": msg_id, "result": result})
                else:
                    write_message({"jsonrpc": "2.0", "id": msg_id, "result": None})
            elif method == "shutdown":
                write_message({"jsonrpc": "2.0", "id": msg_id, "result": None})
            elif method == "exit":
                break

    def get_completions(self):
        items = []
        keywords = ['fn', 'let', 'mut', 'if', 'elif', 'else', 'while', 'for', 'in', 'return', 'print', 'true', 'false', 'match', 'case', 'default', 'and', 'or', 'not', 'struct', 'enum', 'extern', 'import', 'defer', 'break', 'continue', 'assert', 'bench', 'trait', 'comptime', 'as']
        for kw in keywords:
            items.append({"label": kw, "kind": 14, "detail": "Lumina Keyword"})
        return items

if __name__ == "__main__":
    lsp = LuminaLSP()
    lsp.run()