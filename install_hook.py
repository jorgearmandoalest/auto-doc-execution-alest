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
HOOK_ID = "auto-doc-execution-alest"
TELEMETRY_FIELDS = ("last_run", "last_status", "last_error", "run_count")


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


def _load_and_validate_source(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise InstallError(f"fonte de hook inválida: {path}")
    hook = _read_json_object(path)

    expected = {
        "id": HOOK_ID,
        "name": SKILL_NAME,
        "event": "UserPromptSubmit",
        "matcher": "",
        "matcher_mode": "glob",
        "command": "",
        "skills": [SKILL_NAME],
        "timeout": 30,
        "enabled": True,
    }
    for key, value in expected.items():
        if hook.get(key) != value:
            raise InstallError(
                f"hook.json inválido: {key!r} deve ser {value!r}, "
                f"mas é {hook.get(key)!r}"
            )
    return hook


def _is_managed_hook(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    if value.get("id") == HOOK_ID or value.get("name") == SKILL_NAME:
        return True
    skills = value.get("skills")
    return (
        value.get("event") == "UserPromptSubmit"
        and not value.get("command")
        and isinstance(skills, list)
        and SKILL_NAME in skills
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


def _verify_install(path: Path, canonical: dict[str, Any]) -> None:
    data = _read_json_object(path)
    hooks = data.get("hooks")
    if not isinstance(hooks, list):
        raise InstallError("verificação falhou: hooks não é uma lista")
    managed = [item for item in hooks if _is_managed_hook(item)]
    if len(managed) != 1:
        raise InstallError(
            f"verificação falhou: esperava um hook gerenciado, encontrei {len(managed)}"
        )
    for key, value in canonical.items():
        if key in TELEMETRY_FIELDS:
            continue
        if managed[0].get(key) != value:
            raise InstallError(f"verificação falhou no campo {key!r}")


def install(source: Path, destination: Path) -> tuple[str, Path | None]:
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

        match_indexes = [i for i, item in enumerate(raw_hooks) if _is_managed_hook(item)]
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
            if _is_managed_hook(item):
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
            _verify_install(destination, canonical)
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
            _verify_install(destination, canonical)
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
