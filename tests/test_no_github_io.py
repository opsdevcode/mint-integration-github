from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_no_github_sdk_http_or_tokens() -> None:
    text = (ROOT / "implementation" / "reference_server.py").read_text(encoding="utf-8")
    banned = ("requests", "httpx", "PyGithub", "urllib.request", "GH_TOKEN", "GITHUB_TOKEN")
    for item in banned:
        assert item not in text
    assert "token" not in text.lower() or "secret-shaped" in text
