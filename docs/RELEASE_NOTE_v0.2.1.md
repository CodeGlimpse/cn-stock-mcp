# Release Note - v0.2.1

`cn-stock-mcp` v0.2.1 is a security, correctness, and distribution hardening release for the AI-assisted Windows deployment path.

## Highlights

- Validation errors, logs, and stdio output now use stronger secret redaction and strict JSON.
- `stock_compare`, `doctor-network`, provider routing, batch quote fallback, monthly intervals, market pools, fund history, and range calculations were repaired and covered by regression tests.
- AKShare can now derive MA, MACD, BOLL, and KDJ from historical bars when that fallback is applicable.
- Shared provider state and AKShare output redirection are concurrency-protected; MCP synchronous work and high-cost sector/theme expansion are bounded.
- Snapshot responses expose section-level freshness/coverage, and data quality detects records whose key market values are all missing.
- The wheel now includes customer deployment documents and the bundled OpenClaw Skill; use `cn-stock-mcp --docs-path` to locate them.
- The Windows release gate derives its expected version from the tag and validates the installed customer documentation.

## Upgrade

Install the immutable patch version in the dedicated user environment:

```powershell
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\python.exe" -m pip install --upgrade cn-stock-mcp==0.2.1
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe" --version
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe" --doctor --json
```

Restart or reload the MCP Host after upgrading. Keep the user-owned Zhitu token only in `%LOCALAPPDATA%\cn-stock-mcp\config.json`; do not paste it into chat or Host configuration.

## Important boundaries

- This release does not connect to a broker, retain a brokerage account, place orders, or automate trading.
- It does not provide investment reference, investment advice, risk advice, buy/sell instructions, return promises, or personalized suitability decisions.
- Scores and labels describe heuristic data/market structure only; they are not recommendations or confidence estimates.
- The release does not include built-in watchlist persistence or scheduling.
- Third-party data may be delayed, incomplete, wrong, rate-limited, or unavailable. Users remain responsible for upstream tokens, terms, permissions, and independent verification.
- Current real-upstream coverage remains a manually triggered diagnostic gate; public artifact and clean-machine verification are recorded separately from live-provider claims.
