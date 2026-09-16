#!/usr/bin/env bash
# =========================================================
# Compila todos os exemplos em examples/*.lm.
#
# Uso:
#   ./scripts/check_examples.sh              # só compila
#   ./scripts/check_examples.sh --run        # compila + executa
#   ./scripts/check_examples.sh --run-only   # só executa (assume já compilados)
#
# Comportamento do --run:
#   - Se existe examples/<nome>.expected, compara output linha a linha
#   - Senão, verifica apenas exit code 0
#   - Timeout de 10s por binário
# =========================================================

set -u

RUN_MODE=0
RUN_ONLY=0
for arg in "$@"; do
    case "$arg" in
        --run)      RUN_MODE=1 ;;
        --run-only) RUN_MODE=1; RUN_ONLY=1 ;;
    esac
done

SKIP_FILE="tests/features/skip.txt"
# Adiciona os skips específicos de --run
RUN_SKIP_MAP=""
if [ -f "tests/features/run_skip.txt" ] && [ "$RUN_MODE" = "1" ]; then
    declare -A RUN_SKIP_MAP
    while IFS= read -r line; do
        [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
        name=$(echo "$line" | awk '{print $1}')
        RUN_SKIP_MAP["$name"]=1
    done < "tests/features/run_skip.txt"
fi
PASS=0
SKIP=0
FAIL=0
FAILED_FILES=()

# Lê a skip list
declare -A SKIP_MAP
if [ -f "$SKIP_FILE" ]; then
    while IFS= read -r line; do
        [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
        name=$(echo "$line" | awk '{print $1}')
        SKIP_MAP["$name"]=1
    done < "$SKIP_FILE"
fi

# ---------- Modo compile + run ----------
compile_one() {
    local f="$1"
    rm -rf .lumina_cache
    local output
    output=$(timeout 20 python3 -u -m lumina_cli build "$f" 2>&1)
    if echo "$output" | grep -q "Build concluído"; then
        return 0
    fi
    echo "$output" | tail -5 | sed 's/^/     /'
    return 1
}

run_one() {
    local base="$1"
    local exe="examples/${base%.lm}"
    if [ ! -x "$exe" ]; then
        echo "     (binário não encontrado: $exe)"
        return 1
    fi

    local expected_file="examples/${base%.lm}.expected"
    if [ -f "$expected_file" ]; then
        local actual
        actual=$(timeout 10 "$exe" 2>&1)
        local rc=$?
        local expected
        expected=$(cat "$expected_file")
        if [ "$actual" = "$expected" ]; then
            return 0
        else
            echo "     (output mismatch — esperado vs. obtido):"
            diff <(echo "$expected") <(echo "$actual") | head -10 | sed 's/^/     /'
            return 1
        fi
    else
        if timeout 10 "$exe" > /dev/null 2>&1; then
            return 0
        else
            local rc=$?
            echo "     (exit code: $rc)"
            return 1
        fi
    fi
}

# ---------- Loop principal ----------
for f in examples/*.lm; do
    [ -f "$f" ] || continue
    base=$(basename "$f")

    if [ -n "${SKIP_MAP[$base]:-}" ]; then
        echo "⏭️  SKIP: $base"
        SKIP=$((SKIP + 1))
        continue
    fi
    
    if [ "$RUN_MODE" = "1" ] && [ -n "${RUN_SKIP_MAP[$base]:-}" ]; then
        echo "⏭️  SKIP (run): $base"
        SKIP=$((SKIP + 1))
        continue
    fi

    # Compila (a menos que --run-only)
    if [ "$RUN_ONLY" = "0" ]; then
        if ! compile_one "$f"; then
            echo "❌ FAIL (compile): $base"
            FAIL=$((FAIL + 1))
            FAILED_FILES+=("$base")
            continue
        fi
    fi

    # Executa (se --run ou --run-only)
    if [ "$RUN_MODE" = "1" ]; then
        if run_one "$base"; then
            echo "✅ PASS (ran): $base"
            PASS=$((PASS + 1))
        else
            echo "❌ FAIL (run): $base"
            FAIL=$((FAIL + 1))
            FAILED_FILES+=("$base")
        fi
    else
        echo "✅ PASS: $base"
        PASS=$((PASS + 1))
    fi
done

echo
echo "============================================================"
if [ "$RUN_MODE" = "1" ]; then
    echo "📊 PASS: $PASS    ⏭️  SKIP: $SKIP    ❌ FAIL: $FAIL  (modo: run)"
else
    echo "📊 PASS: $PASS    ⏭️  SKIP: $SKIP    ❌ FAIL: $FAIL  (modo: compile)"
fi
echo "============================================================"

if [ ${#FAILED_FILES[@]} -gt 0 ]; then
    echo
    echo "Falharam:"
    for f in "${FAILED_FILES[@]}"; do
        echo "  · $f"
    done
    exit 1
fi
exit 0