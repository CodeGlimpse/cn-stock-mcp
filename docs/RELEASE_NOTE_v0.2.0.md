# Release Note - v0.2.0

`cn-stock-mcp` v0.2.0 is the first public distribution-preparation release for AI-assisted Windows deployment.

## Highlights

- Single runtime version source from package metadata.
- Fixed per-user token configuration under `%LOCALAPPDATA%\\cn-stock-mcp\\config.json`.
- `cn-stock-mcp --init-config` creates a token-free template and applies user-only permissions where supported.
- Token identifiers and error/diagnostic paths are redacted.
- All response envelopes include a non-advisory disclaimer.
- `retail_v1_preview` provides a bounded 10-tool profile while `full` remains backward compatible.
- Officially documented first Host set: Codex, Claude Code, OpenClaw and Hermes Agent.
- Release workflow includes non-live tests, dependency audit, SBOM, SHA256 and build provenance.
- PyPI publication is gated by a clean Windows runner wheel install and MCP smoke.

## Important limits

- Data depends on AKShare, Zhitu and downstream public interfaces; no upstream SLA is provided.
- Live verification remains a manually triggered quality gate.
- This release does not provide a Windows installer, broker connection, trading account storage or automated trading.
- Data-source redistribution and financial-information compliance require separate review; see `docs/DATA_SOURCES.md`.
