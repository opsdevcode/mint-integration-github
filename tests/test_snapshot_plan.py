from __future__ import annotations

import json
from pathlib import Path

from implementation.reference_server import handle

ROOT = Path(__file__).resolve().parents[1]


def _phase(phase: str, payload: dict) -> dict:
    return handle(
        {
            "id": phase,
            "jsonrpc": "2.0",
            "method": "phase",
            "params": {
                "integration": {"identity": "repo.github.plan", "version": "0.1.0"},
                "payload": payload,
                "phase": phase,
                "protocol": "mint.protocol/v0",
                "schema": "mint.protocol.request/v0",
            },
        }
    )


def test_observe_and_plan_read_expanded_snapshot_fields() -> None:
    observe_payload = json.loads((ROOT / "fixtures" / "observe.json").read_text(encoding="utf-8"))
    plan_payload = json.loads((ROOT / "fixtures" / "plan.json").read_text(encoding="utf-8"))
    observed = _phase("observe", observe_payload)
    assert "error" not in observed
    snapshot = observed["result"]["payload"]["snapshot"]
    assert snapshot["owner"] == "example"
    assert snapshot["name"] == "demo"
    assert snapshot["visibility"] == "public"
    assert snapshot["description"] == "demo"
    assert snapshot["requiredReviews"] == 0
    assert snapshot["secretScanning"] is False
    planned = _phase("plan", plan_payload)
    assert "error" not in planned
    actions = [item["action"] for item in planned["result"]["payload"]["operations"]]
    assert actions == ["settings.update", "branch_protection.update", "security.update"]
    settings = planned["result"]["payload"]["operations"][0]["desired"]
    assert settings["visibility"] == "private"
    assert settings["defaultBranch"] == "main"


def test_describe_executable_is_github() -> None:
    described = _phase("describe", {})
    assert described["result"]["payload"]["implementation"]["executable"] == (
        "mint-integration-github"
    )
