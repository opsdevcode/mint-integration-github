# mint-integration-github

Plan-only `repo.github` Mint integration. Observation and plan consume a
supplied `mint.repository-snapshot/v0` with identity, settings,
branchProtection, and security fields. There is no GitHub SDK, HTTP
client, or token field.

`execute` is refused. Execution stays in the SpecMint lifecycle.

```bash
python scripts/run_conformance.py
mint integrations test --local .
```

GitHub Releases are canonical. This version is not on PyPI. There is no
`latest` tag and no PyPI token. Download the immutable prerelease, check
`SHA256SUMS`, then install the local wheel:

```bash
curl -fsSL -O https://github.com/opsdevcode/mint-integration-github/releases/download/v0.2.0-alpha.1/SHA256SUMS
curl -fsSL -O https://github.com/opsdevcode/mint-integration-github/releases/download/v0.2.0-alpha.1/mint_integration_github-0.2.0a1-py3-none-any.whl
shasum -a 256 -c SHA256SUMS
pip install ./mint_integration_github-0.2.0a1-py3-none-any.whl
```

Recorded wheel digest
`sha256:3c864b4f5e7298a0a2f52d0680cb5c3eb8ea57a8195e7d9ba628fe3b7b6e60da`.
Tagged `mint-integration.json` digest
`sha256:1b805a915d950c614c99089942252abbe6d846658afa741b28824330feba41f9`.

Do not pass a PAT. `mint apply` is not part of this integration.
Release Please owns prerelease tags. Public preview, not 1.0.
