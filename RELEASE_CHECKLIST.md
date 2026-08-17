# Release Checklist (`cn-stock-mcp`)

Use this checklist before cutting a release.

## 1. Code and tests
- [ ] Working tree is clean
- [ ] `pytest -q -m "not live"` passes
- [ ] `python -m build` succeeds
- [ ] wheel smoke succeeds (`pip install dist/*.whl` + `cn-stock-mcp --version`)
- [ ] `cn-stock-mcp --doctor` behaves as expected
- [ ] token config init creates a user-only configuration and no command output contains token content
- [ ] `retail_v1_preview` exposes exactly 10 tools; `full` preserves all tools
- [ ] `--json` envelopes include the non-advisory disclaimer and source/freshness metadata

## 2. Docs and packaging
- [ ] `README.md` points to current docs
- [ ] `docs/START_HERE.md` is current
- [ ] `docs/HANDOFF_MINIMAL.md` is current
- [ ] `docs/IMPLEMENTATION_STATUS.md` is current
- [ ] `CHANGELOG.md` has release notes for the version
- [ ] `LICENSE` is present
- [ ] `SECURITY.md`, `PRIVACY.md`, `DATA_SOURCES.md`, and `SUPPORT.md` are current

## 3. Optional live verification
- [ ] `scripts/smoke_live.sh` passes with valid `ZHITU_TOKEN`
- [ ] manual `Live Smoke` workflow passes if upstream validation is desired
- [ ] four Host acceptance records are complete on clean Windows user profiles

## 4. Versioning and release
- [ ] `pyproject.toml` version is correct
- [ ] release note file is prepared
- [ ] git tag is created
- [ ] branch and tag are pushed
- [ ] SHA256, SBOM, and build provenance are attached or verifiable
- [ ] PyPI Trusted Publishing succeeded and public metadata shows the released version
