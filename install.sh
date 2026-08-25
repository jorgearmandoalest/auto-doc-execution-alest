#!/usr/bin/env bash
set -euo pipefail

SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${1:-}" == "--check" ]]; then
  node "$SOURCE_ROOT/scripts/validate-chain.mjs"
  exit 0
fi

TARGET_INPUT="${1:-$PWD}"
if [[ ! -d "$TARGET_INPUT" ]]; then
  echo "Destino inexistente: $TARGET_INPUT" >&2
  exit 1
fi

TARGET_ROOT="$(cd "$TARGET_INPUT" && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"

node "$SOURCE_ROOT/scripts/validate-chain.mjs"

copy_with_backup() {
  local source_file="$1"
  local destination_file="$2"

  mkdir -p "$(dirname "$destination_file")"

  if [[ -L "$destination_file" ]]; then
    echo "Recusado: destino é symlink: $destination_file" >&2
    exit 1
  fi

  if [[ -f "$destination_file" ]]; then
    if cmp -s "$source_file" "$destination_file"; then
      echo "Sem alteração: $destination_file"
      return
    fi
    cp -p "$destination_file" "$destination_file.bak.$STAMP"
    echo "Backup: $destination_file.bak.$STAMP"
  fi

  cp "$source_file" "$destination_file"
  echo "Instalado: $destination_file"
}

copy_with_backup \
  "$SOURCE_ROOT/.kiro/hooks/auto-doc-execution-alest.kiro.hook" \
  "$TARGET_ROOT/.kiro/hooks/auto-doc-execution-alest.kiro.hook"
copy_with_backup \
  "$SOURCE_ROOT/.kiro/steering/auto-doc-execution-alest.md" \
  "$TARGET_ROOT/.kiro/steering/auto-doc-execution-alest.md"
copy_with_backup \
  "$SOURCE_ROOT/.kiro/agents/auto-doc-execution-alest.json" \
  "$TARGET_ROOT/.kiro/agents/auto-doc-execution-alest.json"
copy_with_backup \
  "$SOURCE_ROOT/.kiro/agents/auto-doc-execution-alest.prompt.md" \
  "$TARGET_ROOT/.kiro/agents/auto-doc-execution-alest.prompt.md"

echo
printf '%s\n' \
  'CHAIN_INSTALL_PASS' \
  'Próximos passos obrigatórios:' \
  '1. Configure o MCP notion por token sem salvar o segredo no repositório.' \
  '2. Conecte a integração do Notion à página Execuções.' \
  '3. Pré-aprove no Kiro somente as ferramentas notion de busca, leitura, append/update e criação de página.' \
  '4. Reinicie o Kiro.'
