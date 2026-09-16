"""LSP Server para a linguagem Lumina.

Implementa o subconjunto de LSP necessário para o VS Code:
  - textDocument/completion
  - textDocument/hover
  - textDocument/definition
  - textDocument/references
  - textDocument/prepareRename + textDocument/rename
  - textDocument/documentSymbol
  - textDocument/semanticTokens/full
  - textDocument/publishDiagnostics

Protocolo: JSON-RPC 2.0 sobre stdio.

NOTA: usa I/O em modo binário (`sys.stdin.buffer`). O `Content-Length`
é sempre em BYTES (spec LSP), e o Python em modo texto lê CARACTERES,
o que quebra com UTF-8 multi-byte (acentos, emojis).
"""
import bisect
import sys
import json
import re

from lumina.ast import (
    Function, VarDecl, StructDecl, EnumDecl, TraitDecl, ImplBlock,
    IfStmt, WhileStmt, ForStmt, MatchStmt, DeferStmt, BenchStmt,
)
from lumina.lexer import Lexer
from lumina.lexer.tokens import TokenType
from lumina.parser import Parser
from lumina.semantic import SemanticAnalyzer
from lumina.errors import LuminaError


# ============================================================
# LSP SymbolKind
# ============================================================
SK_FILE = 1
SK_NAMESPACE = 3
SK_CLASS = 5
SK_METHOD = 6
SK_FIELD = 8
SK_ENUM = 10
SK_INTERFACE = 11
SK_FUNCTION = 12
SK_VARIABLE = 13
SK_CONSTANT = 14


# ============================================================
# Semantic token types (índices no legend)
# https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#semanticTokenTypes
# ============================================================
TT_NAMESPACE = 0
TT_TYPE = 1
TT_CLASS = 2
TT_ENUM = 3
TT_INTERFACE = 4
TT_STRUCT = 5
TT_TYPE_PARAMETER = 6
TT_PARAMETER = 7
TT_VARIABLE = 8
TT_PROPERTY = 9
TT_ENUM_MEMBER = 10
TT_EVENT = 11
TT_FUNCTION = 12
TT_METHOD = 13
TT_MACRO = 14
TT_KEYWORD = 15
TT_MODIFIER = 16
TT_COMMENT = 17
TT_STRING = 18
TT_NUMBER = 19
TT_REGEXP = 20
TT_OPERATOR = 21

SEMANTIC_TOKEN_TYPES = [
    "namespace", "type", "class", "enum", "interface",
    "struct", "typeParameter", "parameter", "variable", "property",
    "enumMember", "event", "function", "method", "macro",
    "keyword", "modifier", "comment", "string", "number",
    "regexp", "operator",
]

# Modifiers (bitmask)
TM_DECLARATION = 1  # 1 << 0
TM_DEFINITION = 2   # 1 << 1
TM_READONLY = 4     # 1 << 2

SEMANTIC_TOKEN_MODIFIERS = [
    "declaration", "definition", "readonly", "static",
    "deprecated", "abstract", "async", "modification",
    "documentation", "defaultLibrary",
]


# ============================================================
# Protocolo JSON-RPC (binário!)
# ============================================================
def read_message():
    """Lê uma mensagem LSP do stdin em modo binário."""
    headers = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            break
        try:
            key, value = line.decode('ascii').split(': ', 1)
        except ValueError:
            continue
        headers[key] = value
    content_length = int(headers.get('Content-Length', 0))
    body_bytes = sys.stdin.buffer.read(content_length)
    return json.loads(body_bytes.decode('utf-8'))


def write_message(msg):
    """Escreve uma mensagem LSP no stdout em modo binário."""
    body_bytes = json.dumps(msg, ensure_ascii=False).encode('utf-8')
    header = f"Content-Length: {len(body_bytes)}\r\n\r\n".encode('ascii')
    sys.stdout.buffer.write(header)
    sys.stdout.buffer.write(body_bytes)
    sys.stdout.buffer.flush()


# ============================================================
# Helpers de posição
# ============================================================
def get_word_at_position(text, line, char):
    lines = text.split('\n')
    if line >= len(lines):
        return ""
    line_str = lines[line]
    if char > len(line_str):
        return ""
    start = char
    while start > 0 and (line_str[start - 1].isalnum() or line_str[start - 1] == '_'):
        start -= 1
    end = char
    while end < len(line_str) and (line_str[end].isalnum() or line_str[end] == '_'):
        end += 1
    return line_str[start:end]


def find_word_range(text, line, char):
    lines = text.split('\n')
    if line >= len(lines):
        return None
    line_str = lines[line]
    if char > len(line_str):
        return None
    if char == len(line_str) or not (line_str[char].isalnum() or line_str[char] == '_'):
        if char == 0:
            return None
        if not (line_str[char - 1].isalnum() or line_str[char - 1] == '_'):
            return None
        char = char - 1
    start = char
    while start > 0 and (line_str[start - 1].isalnum() or line_str[start - 1] == '_'):
        start -= 1
    end = char
    while end < len(line_str) and (line_str[end].isalnum() or line_str[end] == '_'):
        end += 1
    return (start, end)


def _build_line_starts(source):
    """Retorna uma lista com o offset (byte) do início de cada linha."""
    starts = [0]
    for i, c in enumerate(source):
        if c == '\n':
            starts.append(i + 1)
    return starts


def _offset_to_linecol(starts, offset):
    """Converte um offset absoluto em (line, col), 0-based."""
    line = bisect.bisect_right(starts, offset) - 1
    col = offset - starts[line]
    return line, col


# ============================================================
# AST helpers
# ============================================================
def _fmt_params(params):
    out = []
    for p in params:
        if hasattr(p, 'name'):
            out.append(f"{p.name}: {p.type_ann}")
        elif isinstance(p, tuple) and len(p) >= 2:
            out.append(f"{p[0]}: {p[1]}")
    return ", ".join(out)


def _range_around(line, col, length):
    """Constrói um Range LSP. Assume line/col 1-based."""
    l0 = max(0, (line or 1) - 1)
    c0 = max(0, (col or 1) - 1)
    return {
        "start": {"line": l0, "character": c0},
        "end": {"line": l0, "character": c0 + max(1, length)},
    }


def _walk_stmts(stmts, callback):
    """Percorre statements recursivamente chamando callback(stmt)."""
    if not stmts:
        return
    for stmt in stmts:
        if stmt is None:
            continue
        callback(stmt)
        if isinstance(stmt, IfStmt):
            _walk_stmts(stmt.then_body, callback)
            if stmt.else_body:
                _walk_stmts(stmt.else_body, callback)
        elif isinstance(stmt, WhileStmt):
            _walk_stmts(stmt.body, callback)
        elif isinstance(stmt, ForStmt):
            _walk_stmts(stmt.body, callback)
        elif isinstance(stmt, MatchStmt):
            for case in stmt.cases:
                if len(case) >= 4:
                    _walk_stmts(case[3], callback)
            if stmt.default:
                _walk_stmts(stmt.default, callback)
        elif isinstance(stmt, DeferStmt):
            _walk_stmts(stmt.body, callback)
        elif isinstance(stmt, BenchStmt):
            _walk_stmts(stmt.body, callback)


def _find_all_references(code, names):
    """Varredura léxica de todas as ocorrências de cada nome."""
    result = {n: [] for n in names}
    lines = code.split('\n')
    for i, line_str in enumerate(lines):
        if line_str.strip().startswith('#'):
            continue
        for name in names:
            for match in re.finditer(r'\b' + re.escape(name) + r'\b', line_str):
                result[name].append({
                    "line": i,
                    "col": match.start(),
                    "end_col": match.end(),
                })
    return result


# ============================================================
# Análise do documento
# ============================================================
def validate_and_extract_symbols(code):
    diagnostics = []
    symbols = {"functions": [], "vars": []}
    definitions = {}
    symbol_details = {}
    document_symbols = []

    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens, "lsp.lm", code)
        ast = parser.parse()

        # ----- Passada 1: top-level -----
        for decl in ast:
            if isinstance(decl, Function):
                params_str = _fmt_params(decl.params)
                ret = f" -> {decl.return_type}" if decl.return_type != "void" else ""
                detail = f"fn {decl.name}({params_str}){ret}"
                symbols["functions"].append({"name": decl.name, "detail": detail, "line": decl.line})
                definitions[decl.name] = {"line": decl.line - 1, "col": decl.col - 1}
                symbol_details[decl.name] = {
                    "kind": SK_FUNCTION, "detail": detail,
                    "line": decl.line, "col": decl.col,
                }
                document_symbols.append({
                    "name": decl.name, "detail": detail, "kind": SK_FUNCTION,
                    "range": _range_around(decl.line, decl.col, len(decl.name)),
                    "selectionRange": _range_around(decl.line, decl.col, len(decl.name)),
                })

            elif isinstance(decl, StructDecl):
                fields_str = ", ".join(f"{k}: {v}" for k, v in decl.fields.items())
                detail = f"struct {decl.name} {{ {fields_str} }}"
                symbol_details[decl.name] = {
                    "kind": SK_CLASS, "detail": detail,
                    "line": getattr(decl, 'line', 0) or 0,
                    "col": getattr(decl, 'col', 0) or 0,
                }
                definitions[decl.name] = {
                    "line": getattr(decl, 'line', 1) - 1,
                    "col": getattr(decl, 'col', 1) - 1,
                }
                document_symbols.append({
                    "name": decl.name, "detail": detail, "kind": SK_CLASS,
                    "range": _range_around(getattr(decl, 'line', 1), getattr(decl, 'col', 1), len(decl.name)),
                    "selectionRange": _range_around(getattr(decl, 'line', 1), getattr(decl, 'col', 1), len(decl.name)),
                })

            elif isinstance(decl, EnumDecl):
                variants_str = ", ".join(v[0] for v in decl.variants)
                detail = f"enum {decl.name} {{ {variants_str} }}"
                symbol_details[decl.name] = {
                    "kind": SK_ENUM, "detail": detail,
                    "line": getattr(decl, 'line', 0) or 0,
                    "col": getattr(decl, 'col', 0) or 0,
                }
                document_symbols.append({
                    "name": decl.name, "detail": detail, "kind": SK_ENUM,
                    "range": _range_around(getattr(decl, 'line', 1), getattr(decl, 'col', 1), len(decl.name)),
                    "selectionRange": _range_around(getattr(decl, 'line', 1), getattr(decl, 'col', 1), len(decl.name)),
                })

            elif isinstance(decl, TraitDecl):
                methods_str = ", ".join(m.name for m in decl.methods)
                detail = f"trait {decl.name} {{ {methods_str} }}"
                symbol_details[decl.name] = {
                    "kind": SK_INTERFACE, "detail": detail,
                    "line": getattr(decl, 'line', 0) or 0,
                    "col": getattr(decl, 'col', 0) or 0,
                }
                document_symbols.append({
                    "name": decl.name, "detail": detail, "kind": SK_INTERFACE,
                    "range": _range_around(getattr(decl, 'line', 1), getattr(decl, 'col', 1), len(decl.name)),
                    "selectionRange": _range_around(getattr(decl, 'line', 1), getattr(decl, 'col', 1), len(decl.name)),
                })

            elif isinstance(decl, ImplBlock):
                methods = []
                for m in decl.methods:
                    params_str = _fmt_params(m.params)
                    ret = f" -> {m.return_type}" if m.return_type != "void" else ""
                    mdetail = f"fn {m.name}({params_str}){ret}"
                    methods.append({
                        "name": m.name, "detail": mdetail, "kind": SK_METHOD,
                        "range": _range_around(getattr(m, 'line', 1), getattr(m, 'col', 1), len(m.name)),
                        "selectionRange": _range_around(getattr(m, 'line', 1), getattr(m, 'col', 1), len(m.name)),
                    })
                    symbol_details[m.name] = {
                        "kind": SK_METHOD, "detail": mdetail,
                        "line": getattr(m, 'line', 0) or 0,
                        "col": getattr(m, 'col', 0) or 0,
                    }
                    definitions[m.name] = {
                        "line": getattr(m, 'line', 1) - 1,
                        "col": getattr(m, 'col', 1) - 1,
                    }
                document_symbols.append({
                    "name": decl.struct_name,
                    "detail": f"impl {decl.struct_name}",
                    "kind": SK_NAMESPACE,
                    "range": _range_around(getattr(decl, 'line', 1), getattr(decl, 'col', 1), len(decl.struct_name)),
                    "selectionRange": _range_around(getattr(decl, 'line', 1), getattr(decl, 'col', 1), len(decl.struct_name)),
                    "children": methods,
                })

            elif isinstance(decl, VarDecl):
                var_type = decl.var_type or "inferred"
                symbols["vars"].append({
                    "name": decl.name, "detail": f"{decl.name}: {var_type}",
                    "line": getattr(decl, 'line', 0),
                })
                definitions[decl.name] = {
                    "line": getattr(decl, 'line', 1) - 1,
                    "col": getattr(decl, 'col', 1) - 1,
                }
                symbol_details[decl.name] = {
                    "kind": SK_VARIABLE, "detail": f"{decl.name}: {var_type}",
                    "line": getattr(decl, 'line', 0) or 0,
                    "col": getattr(decl, 'col', 0) or 0,
                }
                document_symbols.append({
                    "name": decl.name,
                    "detail": f"{decl.name}: {var_type}",
                    "kind": SK_VARIABLE,
                    "range": _range_around(getattr(decl, 'line', 1), getattr(decl, 'col', 1), len(decl.name)),
                    "selectionRange": _range_around(getattr(decl, 'line', 1), getattr(decl, 'col', 1), len(decl.name)),
                })

        # ----- Passada 2: semantic (infere tipos, registra locations) -----
        analyzer = SemanticAnalyzer("lsp.lm", code)
        analyzer.analyze(ast)

        for name, info in symbol_details.items():
            if info["kind"] == SK_VARIABLE:
                var_info = analyzer.get_var_info(name) if hasattr(analyzer, 'get_var_info') else None
                if var_info:
                    inferred = var_info.get('type') or 'inferred'
                    info["detail"] = f"{name}: {inferred}"

        # ----- Passada 3: varre corpos de funções por VarDecls locais -----
        def _register_local(stmt):
            if isinstance(stmt, VarDecl):
                var_type = stmt.var_type or "inferred"
                name = stmt.name
                line = getattr(stmt, 'line', 0) or 0
                col = getattr(stmt, 'col', 0) or 0
                if name not in symbol_details:
                    symbol_details[name] = {
                        "kind": SK_VARIABLE,
                        "detail": f"{name}: {var_type}",
                        "line": line, "col": col,
                    }
                if name not in definitions:
                    definitions[name] = {
                        "line": max(0, line - 1),
                        "col": max(0, col - 1),
                    }

        for decl in ast:
            if isinstance(decl, Function):
                _walk_stmts(decl.body, _register_local)
            elif isinstance(decl, ImplBlock):
                for m in decl.methods:
                    _walk_stmts(m.body, _register_local)

        for name, info in symbol_details.items():
            if info["kind"] == SK_VARIABLE and ": inferred" in info["detail"]:
                var_info = analyzer.get_var_info(name) if hasattr(analyzer, 'get_var_info') else None
                if var_info and var_info.get('type'):
                    info["detail"] = f"{name}: {var_info['type']}"

    except LuminaError as e:
        diagnostics.append({
            "range": {
                "start": {"line": max(0, e.line - 1), "character": max(0, e.col - 1)},
                "end": {"line": max(0, e.line - 1), "character": max(1, e.col)},
            },
            "severity": 1,
            "source": "lumina",
            "message": e.message,
        })
    except Exception:
        pass

    references = _find_all_references(code, list(symbol_details.keys()))

    return diagnostics, symbols, definitions, symbol_details, document_symbols, references


# ============================================================
# Semantic tokens
# ============================================================
def _build_name_to_type(ast, symbol_details):
    """Constrói o mapa `nome → token type LSP`.

    Top-level symbols vêm de `symbol_details`. Params e vars locais
    são extraídos da AST (params têm precedência sobre globais).
    """
    mapping = {}

    # Top-level symbols
    for name, info in symbol_details.items():
        kind = info.get('kind')
        if kind == SK_FUNCTION:
            mapping[name] = TT_FUNCTION
        elif kind == SK_METHOD:
            mapping[name] = TT_METHOD
        elif kind == SK_CLASS:
            mapping[name] = TT_CLASS
        elif kind == SK_ENUM:
            mapping[name] = TT_ENUM
        elif kind == SK_INTERFACE:
            mapping[name] = TT_INTERFACE
        elif kind == SK_VARIABLE:
            mapping[name] = TT_VARIABLE

    # Variants de enum
    for decl in ast:
        if isinstance(decl, EnumDecl):
            for vname, _payloads in decl.variants:
                mapping[vname] = TT_ENUM_MEMBER

    # Params (precedência sobre o resto)
    def _collect_params(methods):
        for m in methods:
            for p in m.params:
                pname = p.name if hasattr(p, 'name') else p[0]
                mapping[pname] = TT_PARAMETER

    for decl in ast:
        if isinstance(decl, Function):
            for p in decl.params:
                pname = p.name if hasattr(p, 'name') else p[0]
                mapping[pname] = TT_PARAMETER
        elif isinstance(decl, ImplBlock):
            _collect_params(decl.methods)

    return mapping


def _collect_semantic_tokens(code, tokens, ast, symbol_details):
    """Retorna a lista de inteiros no formato LSP de semantic tokens.

    Cada token é uma tupla de 5 inteiros:
      [deltaLine, deltaStartChar, length, tokenType, tokenModifiers]
    """
    name_to_type = _build_name_to_type(ast, symbol_details)

    starts = _build_line_starts(code)

    result = []
    prev_line = 0
    prev_col = 0

    for tok in tokens:
        if tok.type != TokenType.IDENT:
            continue

        tt = name_to_type.get(tok.value)
        if tt is None:
            continue

        # Deriva a posição inicial do token a partir do offset bruto.
        # O lexer salva `offset = self.pos` (após consumir o token),
        # então a posição inicial é `offset - len(value)`.
        start_offset = tok.offset - len(tok.value)
        if start_offset < 0:
            continue

        try:
            line, col = _offset_to_linecol(starts, start_offset)
        except Exception:
            continue

        delta_line = line - prev_line
        delta_col = col - prev_col if delta_line == 0 else col

        result.extend([delta_line, delta_col, len(tok.value), tt, 0])
        prev_line = line
        prev_col = col

    return result


# ============================================================
# Servidor LSP
# ============================================================
class LuminaLSP:
    def __init__(self):
        self.latest_text = ""
        self.latest_definitions = {}
        self.symbols = {"functions": [], "vars": []}
        self.symbol_details = {}
        self.document_symbols = []
        self.references = {}
        self.latest_uri = ""
        self.semantic_tokens_data = []

    def run(self):
        while True:
            try:
                msg = read_message()
            except Exception as e:
                sys.stderr.write(f"[lumina-lsp] read_message error: {e}\n")
                continue

            if not msg:
                break

            method = msg.get("method")
            params = msg.get("params", {})
            msg_id = msg.get("id")

            try:
                if method == "initialize":
                    write_message({
                        "jsonrpc": "2.0", "id": msg_id,
                        "result": {
                            "capabilities": {
                                "textDocumentSync": 1,
                                "completionProvider": {
                                    "resolveProvider": False,
                                    "triggerCharacters": ["", "."],
                                },
                                "hoverProvider": True,
                                "definitionProvider": True,
                                "referencesProvider": True,
                                "renameProvider": {"prepareProvider": True},
                                "documentSymbolProvider": True,
                                "semanticTokensProvider": {
                                    "legend": {
                                        "tokenTypes": SEMANTIC_TOKEN_TYPES,
                                        "tokenModifiers": SEMANTIC_TOKEN_MODIFIERS,
                                    },
                                    "full": True,
                                },
                            }
                        }
                    })

                elif method in ("textDocument/didOpen", "textDocument/didChange"):
                    text = params.get("textDocument", {}).get("text", "")
                    if not text:
                        changes = params.get("contentChanges", [])
                        if changes:
                            text = changes[0].get("text", "")

                    self.latest_text = text
                    self.latest_uri = params.get("textDocument", {}).get("uri", "")

                    (diagnostics, symbols, defs,
                     details, doc_syms, refs) = validate_and_extract_symbols(text)

                    self.latest_definitions = defs
                    self.symbols = symbols
                    self.symbol_details = details
                    self.document_symbols = doc_syms
                    self.references = refs

                    # Recalcula semantic tokens uma vez por mudança
                    self.semantic_tokens_data = self._recompute_semantic_tokens()

                    write_message({
                        "jsonrpc": "2.0",
                        "method": "textDocument/publishDiagnostics",
                        "params": {
                            "uri": self.latest_uri,
                            "diagnostics": diagnostics,
                        }
                    })

                elif method == "textDocument/completion":
                    write_message({
                        "jsonrpc": "2.0", "id": msg_id,
                        "result": {"isIncomplete": False, "items": self.get_completions()}
                    })

                elif method == "textDocument/hover":
                    write_message({
                        "jsonrpc": "2.0", "id": msg_id,
                        "result": self.get_hover(params),
                    })

                elif method == "textDocument/definition":
                    write_message({
                        "jsonrpc": "2.0", "id": msg_id,
                        "result": self.get_definition(params),
                    })

                elif method == "textDocument/references":
                    write_message({
                        "jsonrpc": "2.0", "id": msg_id,
                        "result": self.get_references(params),
                    })

                elif method == "textDocument/prepareRename":
                    write_message({
                        "jsonrpc": "2.0", "id": msg_id,
                        "result": self.prepare_rename(params),
                    })

                elif method == "textDocument/rename":
                    write_message({
                        "jsonrpc": "2.0", "id": msg_id,
                        "result": self.rename(params),
                    })

                elif method == "textDocument/documentSymbol":
                    write_message({
                        "jsonrpc": "2.0", "id": msg_id,
                        "result": self.document_symbols,
                    })

                elif method == "textDocument/semanticTokens/full":
                    write_message({
                        "jsonrpc": "2.0", "id": msg_id,
                        "result": {"data": self.semantic_tokens_data},
                    })

                elif method == "shutdown":
                    write_message({"jsonrpc": "2.0", "id": msg_id, "result": None})

                elif method == "exit":
                    break

            except Exception as e:
                sys.stderr.write(f"[lumina-lsp] handler error ({method}): {e}\n")
                if msg_id is not None:
                    write_message({
                        "jsonrpc": "2.0", "id": msg_id,
                        "error": {"code": -32603, "message": str(e)},
                    })

    # ------------------------------------------------------------------
    # Recalcula semantic tokens sob demanda
    # ------------------------------------------------------------------
    def _recompute_semantic_tokens(self):
        if not self.latest_text:
            return []
        try:
            lexer = Lexer(self.latest_text)
            tokens = lexer.tokenize()
            parser = Parser(tokens, "lsp.lm", self.latest_text)
            ast = parser.parse()
            return _collect_semantic_tokens(
                self.latest_text, tokens, ast, self.symbol_details
            )
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------
    def get_completions(self):
        items = []
        keywords = [
            'fn', 'let', 'mut', 'if', 'elif', 'else', 'while', 'for', 'in',
            'return', 'print', 'true', 'false', 'match', 'case', 'default',
            'and', 'or', 'not', 'struct', 'enum', 'extern', 'import', 'defer',
            'break', 'continue', 'assert', 'bench', 'trait', 'comptime', 'as',
            'impl', 'switch', 'export', 'none',
        ]
        for kw in keywords:
            items.append({"label": kw, "kind": 14, "detail": "Lumina Keyword"})

        for func in self.symbols.get("functions", []):
            items.append({"label": func["name"], "kind": 3, "detail": func["detail"]})

        for var in self.symbols.get("vars", []):
            items.append({"label": var["name"], "kind": 6, "detail": var["detail"]})

        for name, info in self.symbol_details.items():
            if info["kind"] == SK_CLASS:
                items.append({"label": name, "kind": 7, "detail": info["detail"]})
            elif info["kind"] == SK_ENUM:
                items.append({"label": name, "kind": 13, "detail": info["detail"]})
            elif info["kind"] == SK_INTERFACE:
                items.append({"label": name, "kind": 8, "detail": info["detail"]})

        return items

    def get_hover(self, params):
        pos = params.get("position", {})
        word = get_word_at_position(
            self.latest_text, pos.get("line", 0), pos.get("character", 0)
        )
        if not word:
            return None

        info = self.symbol_details.get(word)
        if info:
            value = f"```lumina\n{info['detail']}\n```"
            return {"contents": {"kind": "markdown", "value": value}}
        return None

    def get_definition(self, params):
        pos = params.get("position", {})
        word = get_word_at_position(
            self.latest_text, pos.get("line", 0), pos.get("character", 0)
        )
        def_loc = self.latest_definitions.get(word)
        if not def_loc:
            return None
        return {
            "uri": self.latest_uri,
            "range": {
                "start": {"line": def_loc["line"], "character": def_loc["col"]},
                "end": {"line": def_loc["line"], "character": def_loc["col"] + len(word)},
            },
        }

    def get_references(self, params):
        pos = params.get("position", {})
        word = get_word_at_position(
            self.latest_text, pos.get("line", 0), pos.get("character", 0)
        )
        if not word:
            return []
        refs = self.references.get(word, [])
        return [
            {
                "uri": self.latest_uri,
                "range": {
                    "start": {"line": r["line"], "character": r["col"]},
                    "end": {"line": r["line"], "character": r["end_col"]},
                },
            }
            for r in refs
        ]

    def prepare_rename(self, params):
        pos = params.get("position", {})
        line = pos.get("line", 0)
        char = pos.get("character", 0)
        word_range = find_word_range(self.latest_text, line, char)
        if not word_range:
            return None
        start, end = word_range
        return {
            "range": {
                "start": {"line": line, "character": start},
                "end": {"line": line, "character": end},
            },
            "placeholder": self.latest_text.split('\n')[line][start:end],
        }

    def rename(self, params):
        pos = params.get("position", {})
        new_name = params.get("newName", "")
        if not new_name:
            return None

        word = get_word_at_position(
            self.latest_text, pos.get("line", 0), pos.get("character", 0)
        )
        if not word:
            return None

        refs = self.references.get(word, [])
        if not refs:
            return None

        edits = []
        for r in refs:
            edits.append({
                "range": {
                    "start": {"line": r["line"], "character": r["col"]},
                    "end": {"line": r["line"], "character": r["end_col"]},
                },
                "newText": new_name,
            })

        return {"changes": {self.latest_uri: edits}}


if __name__ == "__main__":
    LuminaLSP().run()