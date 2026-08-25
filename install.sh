#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="auto-doc-execution-alest"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
SOURCE_SKILL="${SCRIPT_DIR}/SKILL.md"
SOURCE_HOOK="${SCRIPT_DIR}/hook.json"
HOOK_INSTALLER="${SCRIPT_DIR}/install_hook.py"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ -n "${KIROCREW_HOME:-}" ]]; then
  CREW_HOME="${KIROCREW_HOME}"
elif [[ -n "${HOME:-}" ]]; then
  CREW_HOME="${HOME}/.kiro/crew"
else
  printf 'Erro: defina HOME ou KIROCREW_HOME antes de executar o instalador.\n' >&2
  exit 1
fi

SKILL_DIR="${CREW_HOME}/skills/${SKILL_NAME}"
SKILL_FILE="${SKILL_DIR}/SKILL.md"
HOOKS_FILE="${CREW_HOME}/hooks.json"

for required in "${SOURCE_SKILL}" "${SOURCE_HOOK}" "${HOOK_INSTALLER}"; do
  if [[ ! -f "${required}" ]]; then
    printf 'Erro: arquivo obrigatório ausente: %s\n' "${required}" >&2
    exit 1
  fi
done

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  printf 'Erro: Python 3 é necessário somente para instalar/atualizar hooks.json.\n' >&2
  exit 1
fi

if ! grep -qx 'name: auto-doc-execution-alest' "${SOURCE_SKILL}"; then
  printf 'Erro: SKILL.md não declara o nome esperado: %s.\n' "${SKILL_NAME}" >&2
  exit 1
fi
if ! grep -qx 'always: false' "${SOURCE_SKILL}"; then
  printf 'Erro: SKILL.md deve declarar always: false; o gatilho agora é o hook.\n' >&2
  exit 1
fi
if grep -qx 'always: true' "${SOURCE_SKILL}"; then
  printf 'Erro: always: true reintroduziria ativação duplicada.\n' >&2
  exit 1
fi
"${PYTHON_BIN}" "${HOOK_INSTALLER}" --source "${SOURCE_HOOK}" --check >/dev/null

if [[ -L "${SKILL_DIR}" ]]; then
  printf 'Erro: diretório da skill é link simbólico; instalação recusada: %s\n' "${SKILL_DIR}" >&2
  exit 1
fi
if [[ -e "${SKILL_DIR}" && ! -d "${SKILL_DIR}" ]]; then
  printf 'Erro: destino da skill existe, mas não é diretório: %s\n' "${SKILL_DIR}" >&2
  exit 1
fi
mkdir -p "${SKILL_DIR}"

if [[ -L "${SKILL_FILE}" ]]; then
  printf 'Erro: arquivo da skill é link simbólico; instalação recusada: %s\n' "${SKILL_FILE}" >&2
  exit 1
fi
if [[ -e "${SKILL_FILE}" && ! -f "${SKILL_FILE}" ]]; then
  printf 'Erro: destino da skill existe, mas não é arquivo regular: %s\n' "${SKILL_FILE}" >&2
  exit 1
fi

SKILL_CHANGED=0
SKILL_WAS_NEW=0
SKILL_BACKUP=""
TEMP_FILE=""
cleanup() {
  if [[ -n "${TEMP_FILE}" ]]; then
    rm -f "${TEMP_FILE}"
  fi
}
trap cleanup EXIT

if [[ ! -f "${SKILL_FILE}" ]] || ! cmp -s "${SOURCE_SKILL}" "${SKILL_FILE}"; then
  SKILL_CHANGED=1
  if [[ -f "${SKILL_FILE}" ]]; then
    SKILL_BACKUP="${SKILL_FILE}.backup-$(date +%Y%m%d%H%M%S)-$$"
    cp -p "${SKILL_FILE}" "${SKILL_BACKUP}"
  else
    SKILL_WAS_NEW=1
  fi

  umask 022
  TEMP_FILE="$(mktemp "${SKILL_DIR}/.SKILL.md.tmp.XXXXXX")"
  cp "${SOURCE_SKILL}" "${TEMP_FILE}"
  chmod 0644 "${TEMP_FILE}"
  mv -f "${TEMP_FILE}" "${SKILL_FILE}"
  TEMP_FILE=""

  if ! cmp -s "${SOURCE_SKILL}" "${SKILL_FILE}"; then
    if [[ -n "${SKILL_BACKUP}" ]]; then
      cp -p "${SKILL_BACKUP}" "${SKILL_FILE}"
    else
      rm -f "${SKILL_FILE}"
    fi
    printf 'Erro: verificação da skill falhou; estado anterior restaurado.\n' >&2
    exit 1
  fi
fi

set +e
HOOK_OUTPUT="$("${PYTHON_BIN}" "${HOOK_INSTALLER}" \
  --source "${SOURCE_HOOK}" \
  --destination "${HOOKS_FILE}" 2>&1)"
HOOK_RC=$?
set -e

if [[ ${HOOK_RC} -ne 0 ]]; then
  if [[ ${SKILL_CHANGED} -eq 1 ]]; then
    if [[ -n "${SKILL_BACKUP}" ]]; then
      cp -p "${SKILL_BACKUP}" "${SKILL_FILE}"
    elif [[ ${SKILL_WAS_NEW} -eq 1 ]]; then
      rm -f "${SKILL_FILE}"
    fi
  fi
  printf '%s\n' "${HOOK_OUTPUT}" >&2
  printf 'Erro: hook não foi instalado; alteração da skill foi revertida.\n' >&2
  exit 1
fi

printf '%s\n' "${HOOK_OUTPUT}"
printf 'Skill instalada em:\n%s\n' "${SKILL_FILE}"
if [[ -n "${SKILL_BACKUP}" ]]; then
  printf 'Backup da skill anterior:\n%s\n' "${SKILL_BACKUP}"
fi
printf 'Hook nativo UserPromptSubmit habilitado para carregar $%s em todo prompt.\n' "${SKILL_NAME}"
printf 'Execute `kirocrew restart` para o gateway recarregar o hook.\n'
