from __future__ import annotations

import json
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_conformance_refuses_execute_and_uses_no_network(monkeypatch) -> None:
    def blocked(*_args, **_kwargs):
        raise AssertionError("integration conformance must not open a network socket")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_conformance.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["executeRefused"] is True
    assert "execute" not in report["phases"]
    assert "apply" not in completed.stdout


def test_manifest_has_no_network_or_tokens() -> None:
    text = (ROOT / "mint-integration.json").read_text(encoding="utf-8")
    assert "http://" not in text
    assert "https://" not in text
    assert "token" not in text.lower()
    assert "mint apply" not in text
