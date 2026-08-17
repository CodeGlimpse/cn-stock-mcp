# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-08-17

### Added
- Prepared the first public AI-assisted Windows distribution path.
- Added fixed per-user token configuration, initialization, permissions hardening, and diagnostic redaction.
- Added response disclaimers and the bounded `retail_v1_preview` tool profile.
- Updated Codex, Claude Code, OpenClaw, and Hermes Agent templates to avoid embedding tokens.
- Added security, privacy, support, data-source, Windows deployment, and release documentation.
- Added release workflow controls for dependency audit, SBOM, checksums, Trusted Publishing, and build provenance.

## [Unreleased] - 2026-08-15

### Changed
- Documented the verified Windows development runtime: regular CPython 3.13.2 with the project virtual environment; Python 3.13t is not supported for the Windows/MCP path because `pywin32` has no available `cp313t` wheel.
- Added the P2 delivery record covering live data, date compatibility, MCP stdio, provider health, and dependency validation.
- Reused Provider instances across routers to avoid repeated Windows SSL initialization during MCP registry construction; focused construction time dropped from about 17.9 seconds to 0.33 seconds.
- Synchronized the interface and error-model documentation with the current 52-tool registry.
- Added `meta.freshness` to successful tool responses with server observation time and recognizable source as-of information.
- Promoted provider/fallback/latency observability from business payloads to the response envelope while preserving the nested fields for compatibility.
- Added machine-readable `--doctor --json` and `--doctor-network --json` output, including sanitized token configuration diagnostics.
- Added explicit provider proxy and environment-proxy controls for upstream requests.
- Added capital-flow fresh caching, opt-in stale-if-error behavior, endpoint circuit breaking, empty-result handling, and sector endpoint fallback metadata.
- Added trading-session context to `trading_calendar`, a bounded `stock_snapshot` composite tool, and `data_quality_v1` metadata for successful responses.
- Generated the registry-driven `docs/TOOL_CATALOG.md` and added `--list-tools --json` / `--describe-tool` CLI discovery commands.
- Added `.gitattributes` to keep repository text files on stable line endings across Windows and Unix.
- Extended CI coverage to Python 3.13 and added a Windows CPython 3.13 smoke job.

### Fixed
- Avoided the `market_pool` trading-calendar upstream call when an explicit-date pool result is already cached; cached responses now preserve the requested item count semantics.
- Stopped fallback from swallowing unexpected provider adapter and fallback-policy exceptions.
- Fixed capital-flow summary formatting when upstream rows omit optional large-order fields.
- Added `PROVIDER_CIRCUIT_OPEN` as a retryable error for temporarily blocked unstable endpoints.
- Exposed the valuation section from `stock_profile` so composite snapshots do not silently omit requested valuation data.

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
