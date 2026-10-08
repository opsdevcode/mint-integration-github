"""Drive mint.protocol/v0 conformance without a hosted registry."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "implementation" / "reference_server.py"
FIXTURES = ROOT / "fixtures"
PROTOCOL = "mint.protocol/v0"


def _env() -> dict[str, str]:
    env = {key: os.environ[key] for key in ("PATH", "LANG", "LC_ALL") if os.environ.get(key)}
    env["LANG"] = env.get("LANG") or "C.UTF-8"
    env["LC_ALL"] = "C.UTF-8"
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _invoke(request: dict[str, object]) -> dict[str, object]:
    payload = (json.dumps(request, sort_keys=True, separators=(",", ":")) + "\n").encode()
    completed = subprocess.run(
        [sys.executable, str(SERVER)],
        input=payload,
        capture_output=True,
        timeout=2,
        check=False,
        env=_env(),
        shell=False,
    )
    if completed.returncode != 0:
        raise SystemExit(f"integration exited {completed.returncode}")
    return json.loads(completed.stdout.decode("utf-8"))


def _phase(phase: str, payload: dict[str, object], identity: str, version: str) -> dict[str, object]:
    return _invoke(
        {
            "id": phase,
            "jsonrpc": "2.0",
            "method": "phase",
            "params": {
                "identity": identity,
                "payload": payload,
                "phase": phase,
                "protocol": PROTOCOL,
                "version": version,
            },
        }
    )


def main() -> int:
    described = _phase("describe", {}, "pending", "0.0.0")
    manifest = described["result"]["payload"]  # type: ignore[index]
    identity = str(manifest["identity"])
    version = str(manifest["version"])
    artifact = "sha256:" + hashlib.sha256(SERVER.read_bytes()).hexdigest()
    if manifest["artifact"]["digest"] != artifact:
        raise SystemExit("artifact digest mismatch")
    negotiated = _invoke(
        {
            "id": "negotiate",
            "jsonrpc": "2.0",
            "method": "negotiate",
            "params": {"protocolVersions": [PROTOCOL], "schema": "mint.protocol.negotiate/v0"},
        }
    )
    if "error" in negotiated:
        raise SystemExit("negotiate failed")
    described = _phase("describe", {}, identity, version)
    if "error" in described:
        raise SystemExit("describe failed")
    phases = ["negotiate", "describe"]
    for phase in ("observe", "plan", "verify", "evidence"):
        payload = json.loads((FIXTURES / f"{phase}.json").read_text(encoding="utf-8"))
        result = _phase(phase, payload, identity, version)
        if "error" in result:
            raise SystemExit(f"{phase} failed")
        phases.append(phase)
    refused = _phase("execute", {}, identity, version)
    error = refused.get("error")
    if not isinstance(error, dict) or error.get("code") != "MINT_PHASE":
        raise SystemExit("execute must fail closed")
    report = {
        "artifactDigest": artifact,
        "executeRefused": True,
        "identity": identity,
        "ok": True,
        "phases": phases,
        "protocol": PROTOCOL,
        "version": version,
    }
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
