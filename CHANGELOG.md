# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-08-13

### Changed
- Documented the verified Windows development runtime: regular CPython 3.13.2 with the project virtual environment; Python 3.13t is not supported for the Windows/MCP path because `pywin32` has no available `cp313t` wheel.
- Added the P2 delivery record covering live data, date compatibility, MCP stdio, provider health, and dependency validation.

## [0.1.0] - 2026-05-21

### Added
- Human-friendly documentation entrypoints: `docs/START_HERE.md`
- Agent / host / skill mapping: `docs/AGENT_AND_SKILL_MAP.md`
- AI integration guide: `docs/AI_ONBOARDING.md`
- Host-specific MCP templates for OpenClaw, Claude Desktop, Claude Code, Continue, VS Code, Cursor, Cline, Windsurf, Hermes, and Codex
- `MANIFEST.in` to slim published artifacts
- CLI entry point `cn-stock-mcp`
- `--version`, `--doctor`, `--doctor-network`, `--list-tools`, `--tool ... --payload ...`
- `docs/HANDOFF_MINIMAL.md` as the one-page user handoff
- `docs/FAQ.md` and host template index
- `tests/test_doctor_service.py`
- `LICENSE`
- `RELEASE_CHECKLIST.md`
- `docs/RELEASE_NOTE_v0.1.0.md`

### Changed
- Split doctor behavior into local base checks and explicit network checks
- Refactored doctor logic into `src/cn_stock_mcp/app/services/doctor.py`
- Reduced CLI test coupling by replacing real network CLI checks with dispatch-level tests
- README reorganized into a human-friendly landing page with clearer navigation
- `Live Smoke` workflow repositioned to manual diagnostic use only
- sdist / wheel no longer include `tests/` and `.github/`
- `build` added to `dev` dependencies so CI can run `python -m build` in clean environments
- `docs/IMPLEMENTATION_STATUS.md` refreshed into a current factual status page

### Fixed
- CI failure caused by missing `build` module in the `.[dev]` environment
- `doctor` no longer misreports local source/dev PATH situations as hard failure
- `sector_lookup(children|members)` guidance now consistently requires explicit `sector_type`
