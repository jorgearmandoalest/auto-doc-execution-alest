#!/usr/bin/env python3
"""Testes de integração do instalador, apenas com a biblioteca padrão."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "install.sh"
SKILL_NAME = "auto-doc-execution-alest"
HOOK_SCRIPT_NAME = "auto-doc-execution-alest-hook"
STOP_SCRIPT_NAME = "auto-doc-execution-alest-stop-fallback"


def run_install(home: Path, expected: int = 0) -> subprocess.CompletedProcess[str]:
    # HOME/KIRO_HOME também apontam para `home` neste teste: o instalador grava
    # os scripts de hook em ``$KIRO_HOME/bin`` (ou ``$HOME/.kiro/bin``), separado
    # de KIROCREW_HOME (onde vivem hooks.json e a skill). Usar o mesmo diretório
    # para os três mantém o teste hermético com uma única árvore temporária.
    env = dict(os.environ, KIROCREW_HOME=str(home), HOME=str(home), KIRO_HOME=str(home))
    result = subprocess.run(
        ["bash", str(INSTALL)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == expected, result.stdout + result.stderr
    return result


def _managed_hooks_for(data: dict, script_name: str) -> list[dict]:
    return [
        hook
        for hook in data["hooks"]
        if isinstance(hook, dict) and str(hook.get("command", "")).endswith(f"/{script_name}")
    ]


def managed_hooks(data: dict) -> list[dict]:
    """Hook UserPromptSubmit (compat com testes existentes)."""
    return _managed_hooks_for(data, HOOK_SCRIPT_NAME)


def test_install_and_idempotence() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        home = Path(temporary)
        hooks_file = home / "hooks.json"
        original_other = {
            "id": "other-hook",
            "name": "other-hook",
            "event": "Stop",
            "command": "true",
        }
        context = {"context_summary": "preserve-me"}
        hooks_file.write_text(
            json.dumps({"hooks": [original_other], "resume-context": context}),
            encoding="utf-8",
        )

        first = run_install(home)
        assert "UserPromptSubmit" in first.stdout
        data = json.loads(hooks_file.read_text(encoding="utf-8"))
        assert data["resume-context"] == context
        assert original_other in data["hooks"]

        found = managed_hooks(data)
        assert len(found) == 1
        assert found[0]["event"] == "UserPromptSubmit"
        assert found[0]["matcher"] == ""
        assert found[0]["command"].endswith(f"/{HOOK_SCRIPT_NAME}")
        assert found[0]["enabled"] is True

        found_stop = _managed_hooks_for(data, STOP_SCRIPT_NAME)
        assert len(found_stop) == 1
        assert found_stop[0]["event"] == "Stop"
        assert found_stop[0]["matcher"] == ""
        assert found_stop[0]["command"].endswith(f"/{STOP_SCRIPT_NAME}")
        assert found_stop[0]["enabled"] is True

        installed_skill = home / "skills" / SKILL_NAME / "SKILL.md"
        assert installed_skill.read_text(encoding="utf-8") == (ROOT / "SKILL.md").read_text(
            encoding="utf-8"
        )
        for script_name in (HOOK_SCRIPT_NAME, STOP_SCRIPT_NAME):
            installed_script = home / "bin" / script_name
            assert installed_script.is_file()
            assert os.access(installed_script, os.X_OK)
            assert installed_script.read_text(encoding="utf-8") == (
                ROOT / "bin" / script_name
            ).read_text(encoding="utf-8")

        backups_before = sorted(home.glob("hooks.json.backup-*"))
        content_before = hooks_file.read_bytes()
        second = run_install(home)
        assert "HOOK_STATUS=unchanged" in second.stdout
        assert hooks_file.read_bytes() == content_before
        assert sorted(home.glob("hooks.json.backup-*")) == backups_before

        data = json.loads(hooks_file.read_text(encoding="utf-8"))
        managed = managed_hooks(data)[0]
        managed.update(
            {
                "event": "AgentSpawn",
                "run_count": 17,
                "last_status": "ok",
            }
        )
        data["hooks"].append(
            {
                "id": "duplicate-old-id",
                "name": SKILL_NAME,
                "event": "UserPromptSubmit",
                "command": "",
                "skills": [SKILL_NAME],
            }
        )
        hooks_file.write_text(json.dumps(data), encoding="utf-8")
        run_install(home)
        repaired = json.loads(hooks_file.read_text(encoding="utf-8"))
        found = managed_hooks(repaired)
        assert len(found) == 1
        assert found[0]["event"] == "UserPromptSubmit"
        assert found[0]["run_count"] == 17
        assert found[0]["last_status"] == "ok"


def test_malformed_store_is_not_overwritten() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        home = Path(temporary)
        hooks_file = home / "hooks.json"
        hooks_file.write_text("{broken", encoding="utf-8")
        original = hooks_file.read_bytes()
        result = run_install(home, expected=1)
        assert "não foi possível ler JSON válido" in result.stderr
        assert hooks_file.read_bytes() == original
        assert not (home / "skills" / SKILL_NAME / "SKILL.md").exists()


def _run_stop_fallback(home: Path, payload: dict) -> subprocess.CompletedProcess[str]:
    script = ROOT / "bin" / STOP_SCRIPT_NAME
    env = dict(os.environ, HOME=str(home))
    result = subprocess.run(
        ["python3", str(script)],
        input=json.dumps(payload),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


def test_stop_fallback_skips_when_marker_present() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        home = Path(temporary)
        _run_stop_fallback(
            home,
            {"assistant_text": "Trabalho concluído.\n\n✅ Documentado em Atividade X com sucesso"},
        )
        log_file = home / ".kiro" / "crew" / SKILL_NAME / "missed-turns.jsonl"
        assert not log_file.exists()


def test_stop_fallback_records_when_marker_missing() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        home = Path(temporary)
        _run_stop_fallback(
            home,
            {
                "assistant_text": "Atualizei os arquivos e finalizei sem chamar a skill.",
                "parent_session_key": "sess_teste",
            },
        )
        log_file = home / ".kiro" / "crew" / SKILL_NAME / "missed-turns.jsonl"
        assert log_file.is_file()
        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["session_key"] == "sess_teste"
        assert "não emitiu a saída esperada" in record["reason"]


def test_stop_fallback_ignores_empty_text() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        home = Path(temporary)
        _run_stop_fallback(home, {"assistant_text": ""})
        log_file = home / ".kiro" / "crew" / SKILL_NAME / "missed-turns.jsonl"
        assert not log_file.exists()


def main() -> None:
    test_install_and_idempotence()
    test_malformed_store_is_not_overwritten()
    test_stop_fallback_skips_when_marker_present()
    test_stop_fallback_records_when_marker_missing()
    test_stop_fallback_ignores_empty_text()
    print("installer-tests: PASS")


if __name__ == "__main__":
    main()
