# Security Policy

`cn-stock-mcp` is a local stdio MCP server. It does not connect to brokers, store brokerage accounts, place orders, or provide remote administration.

## Supported version

Security fixes are provided for the latest published minor release. The first supported public line is `0.2.x`.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting or a private Security Advisory for this repository. If private reporting is unavailable, open an Issue containing only a request for a private contact channel. Never include tokens, configuration files, full URLs, logs with query parameters, or personal data in a public Issue.

Zhitu tokens are stored by default in `%LOCALAPPDATA%\cn-stock-mcp\config.json` on Windows. Host configuration examples intentionally contain no token values. See [docs/SECURITY.md](docs/SECURITY.md) for the complete handling and release-control policy.
