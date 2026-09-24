#!/usr/bin/env bash
# linker/triagem.sh — roda todos os .lm de um diretório pelo pipeline
# do linker e acumula os símbolos que faltam na runtime.
#
# Uso: ./linker/triagem.sh [dir]   (padrão: examples)
#
# A skip list fica em `linker/skip.txt`. Edite lá, não aqui.
# Rode `./linker/test_skipped.sh` periodicamente para podar a lista.

set -u
cd "$(dirname "$0")/.."

DIR="${1:-examples}"
TMP="/tmp/triagem"
mkdir -p "$TMP"

SKIP_FILE="linker/skip.txt"

# Lê a skip list para um array associativo.
declare -A SKIP_MAP
if [ -f "$SKIP_FILE" ]; then
    while IFS= read -r line; do
        [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
        name=$(echo "$line" | awk '{print $1}')
        SKIP_MAP["$name"]=1
    done < "$SKIP_FILE"
else
    echo "aviso: $SKIP_FILE não encontrado — rodando sem skip list" >&2
fi

PASS=()
FAIL_COMPILE=()
FAIL_LINK=()
FAIL_RUN=()
SKIP=()
MISSING_SYMS=()

for f in "$DIR"/*.lm; do
    [ -f "$f" ] || continue
    base=$(basename "$f" .lm)

    if [ -n "${SKIP_MAP[$base]:-}" ]; then
        echo "==> $base                            SKIP"
        SKIP+=("$base")
        continue
    fi

    ll="$TMP/$base.ll"
    o="$TMP/$base.o"
    exe="$TMP/$base"

    rm -f "$ll" "$o" "$exe"
    printf "==> %-30s " "$base"

    # 1) .lm → .ll
    python3 - <<PY >"$TMP/$base.ll.out" 2>"$TMP/$base.ll.err"
from lumina_cli.compiler.pipeline import compile_lumina
try:
    compile_lumina("$f", output_file="$ll", is_no_gc=True)
except SystemExit as e:
    raise SystemExit(e.code if e.code is not None else 1)
PY

    if [ ! -s "$ll" ]; then
        msg=$(tail -1 "$TMP/$base.ll.err" 2>/dev/null || echo "?")
        echo "FAIL-COMPILE  ($msg)"
        FAIL_COMPILE+=("$base")
        continue
    fi

    # 2) .ll → .o
    if ! clang -c -O2 -Wno-override-module -fno-pic -fno-pie \
              -fno-stack-protector "$ll" -o "$o" 2>"$TMP/$base.o.err"; then
        echo "FAIL-ASM     ($(tail -1 $TMP/$base.o.err))"
        FAIL_COMPILE+=("$base")
        continue
    fi

    # 3) link
    if ! ./linker/lumina-ld linker/runtime/start.o "$o" linker/runtime/rt.o \
         -o "$exe" 2>"$TMP/$base.link.err"; then
        syms=$(grep -o "undefined reference to '[^']*'" "$TMP/$base.link.err" \
               | sed "s/.*'\(.*\)'/\1/" | sort -u | tr '\n' ' ')
        if [ -n "$syms" ]; then
            echo "FAIL-LINK    (UND: $syms)"
            MISSING_SYMS+=($syms)
        else
            echo "FAIL-LINK    ($(tail -1 "$TMP/$base.link.err"))"
        fi
        FAIL_LINK+=("$base")
        continue
    fi

    # 4) run
    timeout 5 "$exe" >"$TMP/$base.run.out" 2>&1
    rc=$?
    if [ $rc -eq 124 ]; then
        echo "FAIL-RUN     (timeout)"
        FAIL_RUN+=("$base")
    elif [ $rc -ne 0 ]; then
        echo "FAIL-RUN     (exit=$rc)"
        FAIL_RUN+=("$base")
    else
        echo "OK"
        PASS+=("$base")
    fi
done

echo
echo "============================================="
printf "PASS=%d  FAIL-COMPILE=%d  FAIL-LINK=%d  FAIL-RUN=%d  SKIP=%d\n" \
    "${#PASS[@]}" "${#FAIL_COMPILE[@]}" "${#FAIL_LINK[@]}" "${#FAIL_RUN[@]}" "${#SKIP[@]}"
echo "============================================="

if [ ${#MISSING_SYMS[@]} -gt 0 ]; then
    echo
    echo "Símbolos únicos que faltam na runtime:"
    printf '%s\n' "${MISSING_SYMS[@]}" | sort -u
fi

if [ ${#FAIL_COMPILE[@]} -gt 0 ]; then
    echo; echo "Falhas de compilação (bug do compilador, não do linker):"
    printf '  · %s\n' "${FAIL_COMPILE[@]}"
fi
if [ ${#FAIL_LINK[@]} -gt 0 ]; then
    echo; echo "Falhas de link (símbolo faltando ou bug do linker):"
    printf '  · %s\n' "${FAIL_LINK[@]}"
fi
if [ ${#FAIL_RUN[@]} -gt 0 ]; then
    echo; echo "Falhas de execução (bug do programa, codegen ou runtime):"
    printf '  · %s\n' "${FAIL_RUN[@]}"
fi
if [ ${#SKIP[@]} -gt 0 ]; then
    echo; echo "Pulados:"
    printf '  · %s\n' "${SKIP[@]}"
fi