#!/usr/bin/env bash
# scripts/context.sh  — gera bundles enxutos por caso de uso
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
mkdir -p ctx

case "${1:-all}" in
  docs)
    repomix --include "README.md,llms.txt,docs/**,pyproject.toml,lumina.toml" \
            --ignore "CHANGELOG.md" \
            --output ctx/docs.xml ;;
  lang)   # pergunta sobre a linguagem (lexer→codegen)
    repomix --include "lumina/**,lumina_core/**" --output ctx/lang.xml ;;
  cli)    # pergunta sobre CLI
    repomix --include "lumina_cli/**,pyproject.toml" --output ctx/cli.xml ;;
  std)    # pergunta sobre stdlib
    repomix --include "std/**,docs/guia/stdlib.md" --output ctx/std.xml ;;
  all)
    repomix --output ctx/all.xml ;;
  tree)
    tree -L 3 -I '__pycache__|node_modules|*.pyc|.venv|*.ll|*.wasm' \
      > ctx/tree.txt && cat ctx/tree.txt ;;
  changelog)
    repomix --include "CHANGELOG.md,docs/engineering/**" \
            --output ctx/changelog.xml ;;
  *)
    echo "uso: $0 {docs|lang|cli|std|all|tree|changelog}"; exit 1 ;;
esac

# mostra o custo em tokens
for f in ctx/*.xml; do
  [ -f "$f" ] && printf '%-20s %8s  %s\n' "$(basename "$f")" \
    "$(wc -c <"$f" | numfmt --to=iec)" \
    "~$(( $(wc -c <"$f") / 4 )) tokens"
done
