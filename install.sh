#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="auto-doc-execution-alest"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
SOURCE_SKILL="${SCRIPT_DIR}/SKILL.md"
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

# Scripts de hook ficam em ~/.kiro/bin (não em KIROCREW_HOME), no mesmo local
# usado pelos demais scripts de hook nativos (ex: alest-kiro-preflight), e é
# esse caminho literal que hook.json/hook-stop.json referenciam em "command".
if [[ -n "${KIRO_HOME:-}" ]]; then
  KIRO_BIN_DIR="${KIRO_HOME}/bin"
elif [[ -n "${HOME:-}" ]]; then
  KIRO_BIN_DIR="${HOME}/.kiro/bin"
else
  printf 'Erro: defina HOME ou KIRO_HOME antes de executar o instalador.\n' >&2
  exit 1
fi

SKILL_DIR="${CREW_HOME}/skills/${SKILL_NAME}"
SKILL_FILE="${SKILL_DIR}/SKILL.md"
HOOKS_FILE="${CREW_HOME}/hooks.json"

# Pares (arquivo JSON fonte : nome do script em bin/) geridos por este
# instalador. auto-doc-execution-alest injeta a diretiva de carregamento no
# início do turno (UserPromptSubmit); auto-doc-execution-alest-stop-fallback
# roda no fim do turno (Stop) e grava localmente qualquer turno em que a
# skill não tenha emitido sua saída esperada -- rede de segurança que nunca
# escreve no Notion (a skill mantém busca semântica de hub, decisão
# deliberada, então o script Stop não pode ter um ID fixo de página).
HOOK_PAIRS=(
  "hook.json:auto-doc-execution-alest-hook"
  "hook-stop.json:auto-doc-execution-alest-stop-fallback"
)

for required in "${SOURCE_SKILL}" "${HOOK_INSTALLER}"; do
  if [[ ! -f "${required}" ]]; then
    printf 'Erro: arquivo obrigatório ausente: %s\n' "${required}" >&2
    exit 1
  fi
done
for pair in "${HOOK_PAIRS[@]}"; do
  json_name="${pair%%:*}"
  script_name="${pair##*:}"
  for required in "${SCRIPT_DIR}/${json_name}" "${SCRIPT_DIR}/bin/${script_name}"; do
    if [[ ! -f "${required}" ]]; then
      printf 'Erro: arquivo obrigatório ausente: %s\n' "${required}" >&2
      exit 1
    fi
  done
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
for pair in "${HOOK_PAIRS[@]}"; do
  json_name="${pair%%:*}"
  "${PYTHON_BIN}" "${HOOK_INSTALLER}" --source "${SCRIPT_DIR}/${json_name}" --check >/dev/null
done

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

if [[ -L "${KIRO_BIN_DIR}" ]]; then
  printf 'Erro: diretório de scripts de hook é link simbólico; instalação recusada: %s\n' "${KIRO_BIN_DIR}" >&2
  exit 1
fi
if [[ -e "${KIRO_BIN_DIR}" && ! -d "${KIRO_BIN_DIR}" ]]; then
  printf 'Erro: destino de scripts de hook existe, mas não é diretório: %s\n' "${KIRO_BIN_DIR}" >&2
  exit 1
fi
mkdir -p "${KIRO_BIN_DIR}"

# ── Estado de rollback (skill + N scripts) ──────────────────────────────────
SKILL_CHANGED=0
SKILL_WAS_NEW=0
SKILL_BACKUP=""
TEMP_FILE=""

# Índices paralelos a HOOK_PAIRS: script_changed/script_was_new/script_backup.
SCRIPT_CHANGED=()
SCRIPT_WAS_NEW=()
SCRIPT_BACKUP=()
SCRIPT_FILE_PATH=()

CLEANUP_TEMP_FILES=()
cleanup() {
  local tmp
  if [[ -n "${TEMP_FILE}" ]]; then
    rm -f "${TEMP_FILE}"
  fi
  for tmp in "${CLEANUP_TEMP_FILES[@]:-}"; do
    [[ -n "${tmp}" ]] && rm -f "${tmp}"
  done
  return 0
}
trap cleanup EXIT

rollback_all() {
  local i
  if [[ ${SKILL_CHANGED} -eq 1 ]]; then
    if [[ -n "${SKILL_BACKUP}" ]]; then
      cp -p "${SKILL_BACKUP}" "${SKILL_FILE}"
    elif [[ ${SKILL_WAS_NEW} -eq 1 ]]; then
      rm -f "${SKILL_FILE}"
    fi
  fi
  for i in "${!HOOK_PAIRS[@]}"; do
    if [[ "${SCRIPT_CHANGED[$i]:-0}" -eq 1 ]]; then
      if [[ -n "${SCRIPT_BACKUP[$i]:-}" ]]; then
        cp -p "${SCRIPT_BACKUP[$i]}" "${SCRIPT_FILE_PATH[$i]}"
      elif [[ "${SCRIPT_WAS_NEW[$i]:-0}" -eq 1 ]]; then
        rm -f "${SCRIPT_FILE_PATH[$i]}"
      fi
    fi
  done
}

# ── Instala cada script de hook (verificado, com backup) ───────────────────
for i in "${!HOOK_PAIRS[@]}"; do
  pair="${HOOK_PAIRS[$i]}"
  script_name="${pair##*:}"
  source_script="${SCRIPT_DIR}/bin/${script_name}"
  dest_script="${KIRO_BIN_DIR}/${script_name}"
  SCRIPT_FILE_PATH[$i]="${dest_script}"
  SCRIPT_CHANGED[$i]=0
  SCRIPT_WAS_NEW[$i]=0
  SCRIPT_BACKUP[$i]=""

  if [[ -L "${dest_script}" ]]; then
    printf 'Erro: script do hook é link simbólico; instalação recusada: %s\n' "${dest_script}" >&2
    exit 1
  fi
  if [[ -e "${dest_script}" && ! -f "${dest_script}" ]]; then
    printf 'Erro: destino do script do hook existe, mas não é arquivo regular: %s\n' "${dest_script}" >&2
    exit 1
  fi

  if [[ ! -f "${dest_script}" ]] || ! cmp -s "${source_script}" "${dest_script}"; then
    SCRIPT_CHANGED[$i]=1
    if [[ -f "${dest_script}" ]]; then
      SCRIPT_BACKUP[$i]="${dest_script}.backup-$(date +%Y%m%d%H%M%S)-$$"
      cp -p "${dest_script}" "${SCRIPT_BACKUP[$i]}"
    else
      SCRIPT_WAS_NEW[$i]=1
    fi

    umask 022
    temp_script="$(mktemp "${KIRO_BIN_DIR}/.${script_name}.tmp.XXXXXX")"
    CLEANUP_TEMP_FILES+=("${temp_script}")
    cp "${source_script}" "${temp_script}"
    chmod 0755 "${temp_script}"
    mv -f "${temp_script}" "${dest_script}"
    CLEANUP_TEMP_FILES=("${CLEANUP_TEMP_FILES[@]/${temp_script}/}")

    if ! cmp -s "${source_script}" "${dest_script}"; then
      if [[ -n "${SCRIPT_BACKUP[$i]}" ]]; then
        cp -p "${SCRIPT_BACKUP[$i]}" "${dest_script}"
      else
        rm -f "${dest_script}"
      fi
      printf 'Erro: verificação do script %s falhou; estado anterior restaurado.\n' "${script_name}" >&2
      exit 1
    fi
  fi
done

# ── Instala a skill (verificada, com backup) ────────────────────────────────
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

# ── Instala cada hook em hooks.json (verificado, com backup/rollback) ──────
HOOK_OUTPUTS=()
for pair in "${HOOK_PAIRS[@]}"; do
  json_name="${pair%%:*}"
  set +e
  hook_output="$("${PYTHON_BIN}" "${HOOK_INSTALLER}" \
    --source "${SCRIPT_DIR}/${json_name}" \
    --destination "${HOOKS_FILE}" 2>&1)"
  hook_rc=$?
  set -e
  if [[ ${hook_rc} -ne 0 ]]; then
    rollback_all
    printf '%s\n' "${hook_output}" >&2
    printf 'Erro: hook %s não foi instalado; alterações da skill e dos scripts foram revertidas.\n' "${json_name}" >&2
    exit 1
  fi
  HOOK_OUTPUTS+=("${hook_output}")
done

for output in "${HOOK_OUTPUTS[@]}"; do
  printf '%s\n' "${output}"
done
printf 'Skill instalada em:\n%s\n' "${SKILL_FILE}"
if [[ -n "${SKILL_BACKUP}" ]]; then
  printf 'Backup da skill anterior:\n%s\n' "${SKILL_BACKUP}"
fi
for i in "${!HOOK_PAIRS[@]}"; do
  printf 'Script do hook instalado em:\n%s\n' "${SCRIPT_FILE_PATH[$i]}"
  if [[ -n "${SCRIPT_BACKUP[$i]:-}" ]]; then
    printf 'Backup do script anterior:\n%s\n' "${SCRIPT_BACKUP[$i]}"
  fi
done
printf 'Hooks nativos habilitados: UserPromptSubmit injeta $%s em todo prompt; Stop grava fallback local se a skill não emitir a saída esperada.\n' "${SKILL_NAME}"
printf 'Execute `kirocrew restart` para o gateway recarregar os hooks.\n'
