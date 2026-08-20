# Post-release Windows Acceptance - v0.2.0

Date: 2026-08-20

This record supplements the pre-release acceptance record with evidence from
the public PyPI package and a real subprocess MCP client. No existing `.env`,
Zhitu token file, or token value was read.

## Public PyPI installation

On Windows CPython 3.13.2, a new virtual environment was created at:

`F:\agents\code\temp\pypi-install-v0.2.0-20260818`

The package was installed from the public PyPI index with the fixed version:

```powershell
python -m pip install --no-cache-dir --index-url https://pypi.org/simple cn-stock-mcp==0.2.0
```

Evidence:

- `pip show cn-stock-mcp` reported version `0.2.0`.
- `pip check` reported `No broken requirements found`.
- The `cn-stock-mcp.exe` console script returned `0.2.0`.
- `--init-config` created a blank-token JSON template in the temporary test path.
- `--doctor --json` exited `0`; the expected warnings were missing token and skipped network check.

## Default tool profile

With the blank-token configuration, `--list-tools --json` returned exactly these
10 names:

```text
hot_theme_tracker
market_brief
sector_review
stock_history
stock_quote
stock_review
stock_search
stock_snapshot
trading_calendar
watchlist_review
```

## Real MCP stdio subprocess

The MCP SDK client shipped in the installed environment launched the published
`cn-stock-mcp.exe --stdio` subprocess and completed `initialize` successfully.

- Server: `cn-stock-mcp 0.2.0`
- Negotiated protocol: `2025-11-25`
- `tools/list`: 10 tools, matching the default profile above
- `tools/call stock_quote` with no token: process remained healthy and returned
  a safe partial-failure envelope with `PROVIDER_AUTH_FAILED`
- The response included `meta.disclaimer`, `meta.freshness`, and
  `meta.data_quality`; no credential or credential-bearing URL was present

The no-token call is intentionally not treated as a market-data success. The
Windows deployment contract pauses after creating the file so the user can
enter their Zhitu token manually. A first successful provider query and the
graphical Host reload must be completed by the user/agent in that user's own
environment; this audit did not request, read, or echo a real token.

## Release-gate relationship

The tag-triggered GitHub Release workflow also passed its clean
`windows-latest` wheel smoke before publishing PyPI and GitHub Release assets.
The public release links are:

- <https://pypi.org/project/cn-stock-mcp/0.2.0/>
- <https://github.com/CodeGlimpse/cn-stock-mcp/releases/tag/v0.2.0>
