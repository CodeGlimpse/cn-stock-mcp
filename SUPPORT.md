# Support Policy

The first supported public release is `0.2.0`. Its release gate targets Windows 11 x64 with regular CPython 3.13 and the shared local stdio MCP contract. Codex, Claude Code, OpenClaw, and Hermes Agent have versioned configuration templates; graphical Host behavior must be verified in the user's own environment.

Support covers installation, self-checks, MCP connectivity, tool schemas, source/freshness metadata, and redacted diagnostics. It does not guarantee third-party upstream availability, field stability, data timeliness, licensing rights, investment outcomes, or suitability for a particular decision.

When reporting a problem, include the version, operating system, Host name, reproduction steps, and redacted `--doctor --json` output. Do not attach token configuration files or unredacted URLs. See [docs/SUPPORT.md](docs/SUPPORT.md) for details.
