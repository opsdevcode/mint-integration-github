# mint-integration-github

Plan-only `repo.github` Mint integration. Observation and plan consume a
supplied `mint.repository-snapshot/v0`. There is no GitHub SDK, HTTP
client, or token field.

`execute` is refused. Execution stays in the SpecMint lifecycle.

```bash
python scripts/run_conformance.py
```

Do not pass a PAT. `mint apply` is not part of this integration.
