#!/usr/bin/env bash
# Verifica todos os exemplos em examples/*.lm.
# Conta: PASS (compilou), SKIP (na skip list), FAIL (bug real).

set -u

SKIP_FILE="tests/features/skip.txt"
PASS=0
SKIP=0
FAIL=0
FAILED_FILES=()

# Lê a skip list
declare -A SKIP_MAP
if [ -f "$SKIP_FILE" ]; then
    while IFS= read -r line; do
        # Pula comentários e linhas vazias
        [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
        # Pega só o nome do arquivo (primeira palavra)
        name=$(echo "$line" | awk '{print $1}')
        SKIP_MAP["$name"]=1
    done < "$SKIP_FILE"
fi

for f in examples/*.lm; do
    base=$(basename "$f")
    if [ -n "${SKIP_MAP[$base]:-}" ]; then
        echo "⏭️  SKIP: $base"
        SKIP=$((SKIP + 1))
        continue
    fi

    # Limpa cache para este arquivo
    rm -rf .lumina_cache

    output=$(timeout 20 python3 -u -m lumina_cli build "$f" 2>&1)
    if echo "$output" | grep -q "Build concluído"; then
        echo "✅ PASS: $base"
        PASS=$((PASS + 1))
    else
        echo "❌ FAIL: $base"
        echo "$output" | tail -5 | sed 's/^/     /'
        FAIL=$((FAIL + 1))
        FAILED_FILES+=("$base")
    fi
done

echo
echo "============================================================"
echo "📊 PASS: $PASS    ⏭️  SKIP: $SKIP    ❌ FAIL: $FAIL"
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
