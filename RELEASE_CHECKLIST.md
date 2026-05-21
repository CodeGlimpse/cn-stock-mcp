# Release Checklist (`cn-stock-mcp`)

Use this checklist before cutting a release.

## 1. Code and tests
- [ ] Working tree is clean
- [ ] `pytest -q -m "not live"` passes
- [ ] `python -m build` succeeds
- [ ] wheel smoke succeeds (`pip install dist/*.whl` + `cn-stock-mcp --version`)
- [ ] `cn-stock-mcp --doctor` behaves as expected

## 2. Docs and packaging
- [ ] `README.md` points to current docs
- [ ] `docs/START_HERE.md` is current
- [ ] `docs/HANDOFF_MINIMAL.md` is current
- [ ] `docs/IMPLEMENTATION_STATUS.md` is current
- [ ] `CHANGELOG.md` has release notes for the version
- [ ] `LICENSE` is present

## 3. Optional live verification
- [ ] `scripts/smoke_live.sh` passes with valid `ZHITU_TOKEN`
- [ ] manual `Live Smoke` workflow passes if upstream validation is desired

## 4. Versioning and release
- [ ] `pyproject.toml` version is correct
- [ ] release note file is prepared
- [ ] git tag is created
- [ ] branch and tag are pushed
