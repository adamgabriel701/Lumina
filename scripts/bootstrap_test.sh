#!/usr/bin/env bash
# scripts/bootstrap_test.sh — roda o lexer self-hosted em fixtures reais.
#
# Verifica que o binário do parser.lm (compilado do .lm) não trava
# quando alimentado com arquivos .lm reais. Não compara AST ainda —
# isso é o próximo passo (bootstrap_ast_test.sh).
#
# Uso:
#   ./scripts/bootstrap_test.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "==> Compilando lumina_core/parser.lm"
if ! lumina build lumina_core/parser.lm --release >/dev/null 2>&1; then
    echo "  ❌ compilação falhou"
    echo "  Rode: lumina build lumina_core/parser.lm"
    exit 1
fi

# O binário sai em ./parser (nome derivado do .lm)
BIN="./lumina_core/parser"
if [ ! -x "$BIN" ]; then
    # fallback: talvez o binário tenha sido movido
    BIN="./parser"
fi
if [ ! -x "$BIN" ]; then
    echo "  ❌ binário não encontrado"
    exit 1
fi

echo "==> Rodando em fixtures"
FIXTURES=$(find tests/fixtures -name '*.lm' | sort)
PASS=0
FAIL=0
FAILED_FILES=()

for f in $FIXTURES; do
    # 10s de timeout por fixture
    out=$(timeout 10 "$BIN" "$f" 2>&1 || true)
    rc=$?

    if [ $rc -ne 0 ]; then
        echo "  ❌ FAIL (exit=$rc): $f"
        echo "$out" | head -3 | sed 's/^/     /'
        FAIL=$((FAIL + 1))
        FAILED_FILES+=("$f")
        continue
    fi

    # Output deve conter pelo menos alguns tokens
    token_count=$(echo "$out" | grep -cE '^(IDENT|NUMBER|STRING|FN|LET|RETURN|LPAREN|RPAREN)' || true)
    if [ "$token_count" -lt 3 ]; then
        echo "  ❌ FAIL (só $token_count tokens): $f"
        echo "$out" | head -3 | sed 's/^/     /'
        FAIL=$((FAIL + 1))
        FAILED_FILES+=("$f")
        continue
    fi

    echo "  ✅ PASS ($token_count tokens): $(basename "$f")"
    PASS=$((PASS + 1))
done

echo
echo "============================================================"
echo "Bootstrap: $PASS PASS / $FAIL FAIL"
echo "============================================================"

if [ $FAIL -gt 0 ]; then
    echo "Falharam:"
    for f in "${FAILED_FILES[@]}"; do
        echo "  · $f"
    done
    exit 1
fi
