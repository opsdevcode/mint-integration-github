from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PUBLISH = (REPO / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
TRAIN = (REPO / ".github" / "workflows" / "release-train.yml").read_text(encoding="utf-8")
CONFIG = json.loads((REPO / "release-please-config.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((REPO / ".release-please-manifest.json").read_text(encoding="utf-8"))


def _assert_actions_are_pinned(workflow: str) -> None:
    for line in workflow.splitlines():
        stripped = line.strip()
        if not stripped.startswith("uses:"):
            continue
        spec = stripped.split("uses:", 1)[1].strip()
        if spec.startswith("./"):
            continue
        name, _, ref = spec.partition("@")
        sha = ref.split()[0]
        assert name and len(sha) == 40, spec
        assert all(ch in "0123456789abcdef" for ch in sha), spec


def test_release_train_uses_conventional_semver_release_prs() -> None:
    package = CONFIG["packages"]["."]
    assert "branches:" in TRAIN and "- main" in TRAIN
    assert "googleapis/release-please-action@" in TRAIN
    assert "actions/create-github-app-token@" in TRAIN
    assert "repositories: mint-integration-github" in TRAIN
    assert "permission-contents: write" in TRAIN
    assert "permission-pull-requests: write" in TRAIN
    assert "permission-issues:" not in TRAIN
    assert package["release-type"] == "python"
    assert package["package-name"] == "mint-integration-github"
    assert package["versioning-strategy"] == "prerelease"
    assert package["prerelease"] is True
    assert package["prerelease-type"] == "alpha"
    assert package["include-v-in-tag"] is True
    assert package["include-component-in-tag"] is False
    assert package["skip-labeling"] is True
    assert set(MANIFEST) == {"."}
    assert re.fullmatch(r"0\.\d+\.\d+-alpha\.\d+", MANIFEST["."])


def test_publish_is_release_event_driven_and_once_built() -> None:
    assert "release:" in PUBLISH
    assert "- published" in PUBLISH
    assert "tags:" not in PUBLISH
    assert "workflow_dispatch:" not in PUBLISH
    assert "python -m build --sdist --wheel" in PUBLISH
    assert "Test exact artifacts in isolated Python 3.12 venvs" in PUBLISH
    assert "sha256sum" in PUBLISH
    assert "anchore/sbom-action@66cbf4bc1f1c0d2edc94016e65bc221b6bb0ad6c" in PUBLISH
    assert "actions/attest-build-provenance@db473fddc028af60658334401dc6fa3ffd8669fd" in PUBLISH
    assert "pypa/gh-action-pypi-publish@ed0c53931b1dc9bd32cbe73a98c7f6766f8a527e" in PUBLISH


def test_publish_refuses_manual_aliases_and_tokens() -> None:
    assert "refuse non-alpha or 1.x release tag" in PUBLISH
    assert "release tag ${TAG} must match pyproject.toml" in PUBLISH
    assert "PYPI_TOKEN" not in PUBLISH
    assert "password:" not in PUBLISH
    assert "skip-existing: false" in PUBLISH
    assert "packages-dir: pypi-dist" in PUBLISH
    assert "GH_REPO: ${{ github.repository }}" in PUBLISH
    assert "gh release create" not in PUBLISH
    assert "git tag" not in PUBLISH
    assert ":latest" not in PUBLISH
    assert "refs/tags/latest" not in PUBLISH
    assert "vscode-marketplace:" not in PUBLISH
    assert "open-vsx:" not in PUBLISH
    assert "VSCE_PAT" not in PUBLISH
    assert "OVSX_PAT" not in PUBLISH
    assert "mint apply" not in PUBLISH


def test_release_actions_are_commit_pinned() -> None:
    _assert_actions_are_pinned(TRAIN)
    _assert_actions_are_pinned(PUBLISH)
