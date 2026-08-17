# Windows Acceptance Record - v0.2.0

Date: 2026-08-17

## Local controlled acceptance

The final wheel was installed into a new Windows CPython 3.13 virtual environment outside the source tree. No existing project environment, editable install, `.env`, or token file was used.

Verified results:

- `cn-stock-mcp==0.2.0` installed from `cn_stock_mcp-0.2.0-py3-none-any.whl` with public dependencies.
- `--init-config` created a blank-token user configuration.
- Windows ACL retained only the executing account and `SYSTEM` with full control.
- `--version` returned `0.2.0`; local doctor exited `0`.
- The generated `retail_v1_preview` configuration exposed exactly 10 tools; a missing configuration retained the 53-tool `full` profile.
- A real MCP SDK stdio client initialized the server, listed the 10-tool profile, and successfully called `stock_quote` for `000001` through the no-token AKShare path.
- The successful response included `freshness`, `data_quality`, and the non-advisory disclaimer.
- Wheel/sdist contents contained no test suite, GitHub workflow, `.env`, or token configuration file.

## Clean runner release gate

The tag-triggered Release workflow runs a separate `windows-latest` job before publication. It builds the wheel, installs it in a new runner venv, creates and checks a blank-token config, verifies version/doctor/the 10-tool profile, and exercises the MCP `tools/list` handler. The PyPI and GitHub Release job depends on this Windows job, so publication cannot start if the clean-runner gate fails.

## Scope boundary

No Zhitu token was entered or read during this acceptance. The first live query used AKShare. Codex, Claude Code, OpenClaw, and Hermes Agent have versioned configuration templates, but their graphical or interactive shells were not all installed on this workstation; their shared stdio contract is covered by the real MCP client test and the clean Windows release gate.
