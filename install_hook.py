#!/usr/bin/env python3
"""Instala idempotentemente o hook nativo do KiroCrew em hooks.json."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import shutil
import stat
import tempfile
import time
from pathlib import Path
from typing import Any

SKILL_NAME = "auto-doc-execution-alest"
TELEMETRY_FIELDS = ("last_run", "last_status", "last_error", "run_count")

# Cada entrada descreve um hook gerenciado por este instalador: seu HOOK_ID
# canônico, o evento esperado, e o nome do script real (validado como sufixo
# de "command", já que o caminho completo varia por HOME/KIRO_HOME).
_HOOK_DEFINITIONS: dict[str, dict[str, str]] = {
    "auto-doc-execution-alest": {
        "hook_id": "auto-doc-execution-alest",
        "event": "UserPromptSubmit",
        "script_name": "auto-doc-execution-alest-hook",
    },
    "auto-doc-execution-alest-stop-fallback": {
        "hook_id": "auto-doc-execution-alest-stop-fallback",
        "event": "Stop",
        "script_name": "auto-doc-execution-alest-stop-fallback",
    },
}


class InstallError(RuntimeError):
    """Erro seguro de validação ou persistência do hook."""


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError(f"não foi possível ler JSON válido de {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise InstallError(f"{path} deve conter um objeto JSON na raiz")
    return value


def _resolve_definition(path: Path) -> dict[str, str]:
    """Escolhe a definição esperada pelo nome do arquivo fonte (hook.json / hook-stop.json)."""
    stem = path.stem  # "hook" ou "hook-stop"
    if stem == "hook":
        return _HOOK_DEFINITIONS["auto-doc-execution-alest"]
    if stem == "hook-stop":
        return _HOOK_DEFINITIONS["auto-doc-execution-alest-stop-fallback"]
    raise InstallError(
        f"fonte de hook não reconhecida: {path.name} (esperado hook.json ou hook-stop.json)"
    )


def _load_and_validate_source(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise InstallError(f"fonte de hook inválida: {path}")
    hook = _read_json_object(path)
    definition = _resolve_definition(path)

    # O runtime do Kiro Crew (kiro_crew/hooks.py, dataclass ScriptHook) só
    # executa hooks via "command" (subprocesso real). Um campo "skills" no
    # hook.json é lido do disco mas nunca chega ao objeto ScriptHook em
    # memória — não existe no dataclass nem é consultado em nenhum ponto do
    # runtime. Por isso um hook dispara (run_count cresce) sem nunca carregar
    # a skill quando "command" está vazio. O contrato correto é "command"
    # apontar para um script real, replicando o padrão do hook nativo
    # "Alest Learning Loop — Preflight".
    expected_static = {
        "id": definition["hook_id"],
        "name": definition["hook_id"],
        "event": definition["event"],
        "matcher": "",
        "enabled": True,
    }
    for key, value in expected_static.items():
        if hook.get(key) != value:
            raise InstallError(
                f"{path.name} inválido: {key!r} deve ser {value!r}, "
                f"mas é {hook.get(key)!r}"
            )
    command = hook.get("command")
    script_name = definition["script_name"]
    if not isinstance(command, str) or not command.endswith(f"/{script_name}"):
        raise InstallError(
            f"{path.name} inválido: 'command' deve apontar para .../{script_name}, "
            f"mas é {command!r}"
        )
    timeout = hook.get("timeout")
    if not isinstance(timeout, int) or not (1 <= timeout <= 300):
        raise InstallError(f"{path.name} inválido: 'timeout' deve ser um inteiro entre 1 e 300")
    return hook


def _is_managed_hook(value: object, definition: dict[str, str]) -> bool:
    if not isinstance(value, dict):
        return False
    if value.get("id") == definition["hook_id"] or value.get("name") == definition["hook_id"]:
        return True
    command = value.get("command")
    return (
        value.get("event") == definition["event"]
        and isinstance(command, str)
        and command.endswith(f"/{definition['script_name']}")
    )


def _atomic_write(path: Path, data: dict[str, Any], mode: int) -> None:
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        temporary.unlink(missing_ok=True)
        raise


def _verify_install(path: Path, canonical: dict[str, Any], definition: dict[str, str]) -> None:
    data = _read_json_object(path)
    hooks = data.get("hooks")
    if not isinstance(hooks, list):
        raise InstallError("verificação falhou: hooks não é uma lista")
    managed = [item for item in hooks if _is_managed_hook(item, definition)]
    if len(managed) != 1:
        raise InstallError(
            f"verificação falhou: esperava um hook gerenciado ({definition['hook_id']}), "
            f"encontrei {len(managed)}"
        )
    for key, value in canonical.items():
        if key in TELEMETRY_FIELDS:
            continue
        if managed[0].get(key) != value:
            raise InstallError(f"verificação falhou no campo {key!r}")


def install(source: Path, destination: Path) -> tuple[str, Path | None]:
    definition = _resolve_definition(source)
    canonical = _load_and_validate_source(source)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.is_symlink():
        raise InstallError(f"destino é link simbólico; instalação recusada: {destination}")
    if destination.exists() and not destination.is_file():
        raise InstallError(f"destino existe, mas não é arquivo regular: {destination}")

    lock_path = destination.parent / f"{destination.name}.lock"
    if lock_path.is_symlink():
        raise InstallError(f"lock é link simbólico; instalação recusada: {lock_path}")

    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    lock_fd = os.open(lock_path, flags, 0o600)
    backup: Path | None = None
    replaced = False
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        current = _read_json_object(destination)
        raw_hooks = current.get("hooks", [])
        if not isinstance(raw_hooks, list):
            raise InstallError(
                f"{destination} contém 'hooks' que não é uma lista; nada foi alterado"
            )

        match_indexes = [
            i for i, item in enumerate(raw_hooks) if _is_managed_hook(item, definition)
        ]
        if match_indexes:
            first = raw_hooks[match_indexes[0]]
            if isinstance(first, dict):
                canonical = dict(canonical)
                for field in TELEMETRY_FIELDS:
                    if field in first:
                        canonical[field] = first[field]

        new_hooks: list[object] = []
        inserted = False
        for item in raw_hooks:
            if _is_managed_hook(item, definition):
                if not inserted:
                    new_hooks.append(canonical)
                    inserted = True
                continue
            new_hooks.append(item)
        if not inserted:
            new_hooks.append(canonical)

        updated = dict(current)
        updated["hooks"] = new_hooks
        if updated == current:
            _verify_install(destination, canonical, definition)
            return "unchanged", None

        mode = 0o600
        if destination.exists():
            mode = stat.S_IMODE(destination.stat().st_mode)
            stamp = time.strftime("%Y%m%d%H%M%S")
            backup = destination.with_name(
                f"{destination.name}.backup-{stamp}-{time.time_ns()}-{os.getpid()}"
            )
            shutil.copy2(destination, backup)

        try:
            _atomic_write(destination, updated, mode)
            replaced = True
            _verify_install(destination, canonical, definition)
        except BaseException:
            if replaced:
                if backup is not None and backup.exists():
                    os.replace(backup, destination)
                    backup = None
                else:
                    destination.unlink(missing_ok=True)
            raise
        return ("updated" if match_indexes else "installed"), backup
    finally:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        _load_and_validate_source(args.source)
        if args.check:
            print("hook.json válido")
            return 0
        if args.destination is None:
            raise InstallError("--destination é obrigatório fora do modo --check")
        status, backup = install(args.source, args.destination)
        print(f"HOOK_STATUS={status}")
        print(f"HOOK_FILE={args.destination}")
        if backup is not None:
            print(f"HOOK_BACKUP={backup}")
        return 0
    except (InstallError, OSError) as exc:
        print(f"Erro: {exc}", file=os.sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
