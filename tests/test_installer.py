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


def run_install(home: Path, expected: int = 0) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, KIROCREW_HOME=str(home))
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


def managed_hooks(data: dict) -> list[dict]:
    return [
        hook
        for hook in data["hooks"]
        if isinstance(hook, dict)
        and (
            hook.get("id") == SKILL_NAME
            or hook.get("name") == SKILL_NAME
            or SKILL_NAME in hook.get("skills", [])
        )
    ]


def test_install_and_idempotence() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        home = Path(temporary)
        hooks_file = home / "hooks.json"
        original_other = {
            "id": "other-hook",
            "name": "other-hook",
            "event": "Stop",
            "command": "true",
            "skills": [],
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
        assert found[0]["command"] == ""
        assert found[0]["skills"] == [SKILL_NAME]
        assert found[0]["enabled"] is True
        installed_skill = home / "skills" / SKILL_NAME / "SKILL.md"
        assert installed_skill.read_text(encoding="utf-8") == (ROOT / "SKILL.md").read_text(
            encoding="utf-8"
        )

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


def main() -> None:
    test_install_and_idempotence()
    test_malformed_store_is_not_overwritten()
    print("installer-tests: PASS")


if __name__ == "__main__":
    main()
