#!/usr/bin/env bash
# linker/triagem.sh — roda todos os .lm de um diretório pelo pipeline
# do linker e acumula os símbolos que faltam na runtime.
#
# Uso: ./linker/triagem.sh [dir]   (padrão: examples)
#
# Skip list: arquivos conhecidos como fora de escopo ou com bugs
# conhecidos do compilador (não do linker). Ajuste conforme for
# resolvendo.

set -u
cd "$(dirname "$0")/.."

DIR="${1:-examples}"
TMP="/tmp/triagem"
mkdir -p "$TMP"

# SKIP_LIST — arquivos pulados e o motivo:
#   util — módulo auxiliar, sem `fn main`
#   threads — usa pthread_create; implementação exige clone()+TLS
#   engine, ffi_test, wasm_js_interop — dependem de FFI/WASM/Raylib externos
#   api, app, async_server, http_framework, serve, server, proxy — servidores de rede (loop infinito)
#   bootstrap_lexer, database, gc_test, json_parser — dependem de .tbss (TLS nativo)
#   chip8, coroutines — alinhamento de pilha da runtime freestanding nativa
SKIP_LIST="util threads engine ffi_test wasm_js_interop api app async_server http_framework serve server proxy bootstrap_lexer database gc_test json_parser chip8 coroutines"

PASS=()
FAIL_COMPILE=()
FAIL_LINK=()
FAIL_RUN=()
SKIP=()
MISSING_SYMS=()

for f in "$DIR"/*.lm; do
    [ -f "$f" ] || continue
    base=$(basename "$f" .lm)

    case " $SKIP_LIST " in
        *" $base "*)
            echo "==> $base                            SKIP"
            SKIP+=("$base")
            continue
            ;;
    esac

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