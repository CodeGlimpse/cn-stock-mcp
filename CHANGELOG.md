# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.2.2] - 2026-09-05

### Security
- Added token-source diagnostics that report configuration/environment conflicts without exposing credential values.
- Added future-source-time rejection and semantic data-quality anomaly flags for impossible market values.

### Fixed
- Zhitu request timeouts now continue to configured backup tokens.
- Snapshot timeout responses now explicitly describe best-effort cancellation and possible background requests.

### Changed
- Added a pinned Windows CPython 3.13 runtime constraints file, CI validation, release audit, SHA256 asset, and customer install verification.
- Added a sale-readiness gate documenting support, refund, host-compatibility, data-source, and disclaimer requirements before external one-time sales.
- Added repository-history secret scanning, pull-request dependency review, and Dependabot update schedules.

## [0.2.1] - 2026-09-05

### Security
- Removed submitted input values and error contexts from validation diagnostics, expanded token/Bearer/JSON-key redaction, and made logs/stdio use strict JSON without `NaN` or `Infinity`.
- Hardened token configuration precedence and permission checks while retaining access for the identifiable interactive Windows user.

### Fixed
- Repaired `stock_compare` for the current Zhitu list and AKShare tuple contracts and made layer failures explicit.
- Made `doctor-network` fail when the provider report is degraded, completed cross-provider batch quote fallback, and aligned documented/provider routes.
- Added canonical `1M`, ETF/LOF history, AKShare-derived MA/MACD/BOLL/KDJ fallback, all documented market-pool types, and true range return calculation for index enhancement.
- Corrected market-brief missing-value ranking, unavailable pool semantics, and zero-denominator breadth ratios.
- Made unknown tool profiles fail closed to the bounded retail profile.

### Changed
- Moved synchronous provider calls off the MCP event loop, bounded concurrent calls and high-cost sector/theme expansion, locked shared provider state, and enforced configured per-process Zhitu quotas.
- Added per-section snapshot freshness/coverage and stronger empty-record data-quality detection.
- Packaged customer deployment documentation and the bundled OpenClaw Skill in the wheel and added `--docs-path`.
- Made the release workflow version-independent and added installed-document validation.

## [0.2.0] - 2026-08-17

### Added
- Prepared the first public AI-assisted Windows distribution path.
- Added fixed per-user token configuration, initialization, permissions hardening, and diagnostic redaction.
- Added response disclaimers and the bounded `retail_v1_preview` tool profile.
- Updated Codex, Claude Code, OpenClaw, and Hermes Agent templates to avoid embedding tokens.
- Added security, privacy, support, data-source, Windows deployment, and release documentation.
- Added release workflow controls for dependency audit, SBOM, checksums, Trusted Publishing, and build provenance.

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
