from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
CI = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
MANIFEST = (ROOT / "mint-integration.json").read_text(encoding="utf-8")

WHEEL = "sha256:3c864b4f5e7298a0a2f52d0680cb5c3eb8ea57a8195e7d9ba628fe3b7b6e60da"
JSON = "sha256:1b805a915d950c614c99089942252abbe6d846658afa741b28824330feba41f9"


def test_readme_is_github_first() -> None:
    assert "GitHub Releases are canonical" in README
    assert WHEEL in README
    assert JSON in README
    assert "SHA256SUMS" in README
    assert "pip install ./" in README
    assert "not on PyPI" in README
    assert "pypi.org/project/mint-integration-github" not in README
    assert "mint apply" in README
    assert "branchProtection" in README


def test_ci_verifies_recorded_github_release() -> None:
    assert "GitHub Release assets" in CI
    assert WHEEL.replace("sha256:", "") in CI
    assert "v0.2.0-alpha.1" in CI
    assert "gh release create" not in CI
    assert "git tag" not in CI


def test_manifest_executable_is_github() -> None:
    assert '"executable": "mint-integration-github"' in MANIFEST
    assert "mint-integration-local" not in MANIFEST
