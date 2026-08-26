#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="auto-doc-execution-alest"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
SOURCE_FILE="${SCRIPT_DIR}/SKILL.md"

if [[ -n "${KIROCREW_HOME:-}" ]]; then
  CREW_HOME="${KIROCREW_HOME}"
elif [[ -n "${HOME:-}" ]]; then
  CREW_HOME="${HOME}/.kiro/crew"
else
  printf 'Erro: defina HOME ou KIROCREW_HOME antes de executar o instalador.\n' >&2
  exit 1
fi

DESTINATION_DIR="${CREW_HOME}/skills/${SKILL_NAME}"
DESTINATION_FILE="${DESTINATION_DIR}/SKILL.md"

if [[ ! -f "${SOURCE_FILE}" ]]; then
  printf 'Erro: não encontrei %s ao lado do instalador.\n' "${SOURCE_FILE}" >&2
  exit 1
fi

if ! grep -qx 'name: auto-doc-execution-alest' "${SOURCE_FILE}"; then
  printf 'Erro: o SKILL.md não declara o nome esperado: %s.\n' "${SKILL_NAME}" >&2
  exit 1
fi

if ! grep -qx 'always: true' "${SOURCE_FILE}"; then
  printf 'Erro: o SKILL.md não está configurado com always: true.\n' >&2
  exit 1
fi

if [[ -L "${DESTINATION_DIR}" ]]; then
  printf 'Erro: o diretório de destino é um link simbólico; instalação recusada por segurança: %s\n' "${DESTINATION_DIR}" >&2
  exit 1
fi

if [[ -e "${DESTINATION_DIR}" && ! -d "${DESTINATION_DIR}" ]]; then
  printf 'Erro: o destino existe, mas não é um diretório: %s\n' "${DESTINATION_DIR}" >&2
  exit 1
fi

mkdir -p "${DESTINATION_DIR}"

if [[ -L "${DESTINATION_FILE}" ]]; then
  printf 'Erro: o arquivo de destino é um link simbólico; instalação recusada por segurança: %s\n' "${DESTINATION_FILE}" >&2
  exit 1
fi

if [[ -e "${DESTINATION_FILE}" && ! -f "${DESTINATION_FILE}" ]]; then
  printf 'Erro: o destino existe, mas não é um arquivo regular: %s\n' "${DESTINATION_FILE}" >&2
  exit 1
fi

if [[ -f "${DESTINATION_FILE}" ]] && cmp -s "${SOURCE_FILE}" "${DESTINATION_FILE}"; then
  printf 'auto-doc-execution-alest já está instalada e atualizada em:\n%s\n' "${DESTINATION_FILE}"
  printf 'Nenhuma alteração foi necessária. Abra uma nova sessão do Kiro Crew para usá-la.\n'
  exit 0
fi

BACKUP_FILE=""
if [[ -f "${DESTINATION_FILE}" ]]; then
  BACKUP_FILE="${DESTINATION_FILE}.backup-$(date +%Y%m%d%H%M%S)-$$"
  cp -p "${DESTINATION_FILE}" "${BACKUP_FILE}"
fi

umask 022
TEMP_FILE="$(mktemp "${DESTINATION_DIR}/.SKILL.md.tmp.XXXXXX")"
cleanup() {
  if [[ -n "${TEMP_FILE:-}" ]]; then
    rm -f "${TEMP_FILE}"
  fi
}
trap cleanup EXIT

cp "${SOURCE_FILE}" "${TEMP_FILE}"
chmod 0644 "${TEMP_FILE}"
mv -f "${TEMP_FILE}" "${DESTINATION_FILE}"
TEMP_FILE=""

if ! cmp -s "${SOURCE_FILE}" "${DESTINATION_FILE}"; then
  if [[ -n "${BACKUP_FILE}" ]]; then
    cp -p "${BACKUP_FILE}" "${DESTINATION_FILE}"
  else
    rm -f "${DESTINATION_FILE}"
  fi
  printf 'Erro: a verificação pós-instalação falhou; o estado anterior foi restaurado.\n' >&2
  exit 1
fi

printf 'auto-doc-execution-alest instalada com sucesso em:\n%s\n' "${DESTINATION_FILE}"
if [[ -n "${BACKUP_FILE}" ]]; then
  printf 'Backup da versão anterior:\n%s\n' "${BACKUP_FILE}"
fi
printf 'Abra uma nova sessão do Kiro Crew para carregar a skill.\n'
