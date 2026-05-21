# Release Note - v0.1.0

`cn-stock-mcp` v0.1.0 is the first release cut after the project was reshaped from a developer-oriented repository into a more user-friendly MCP delivery.

## Highlights

### 1. Real CLI entry point
The package now provides a real command entry:

```bash
cn-stock-mcp --stdio
cn-stock-mcp --version
cn-stock-mcp --doctor
cn-stock-mcp --doctor-network
cn-stock-mcp --list-tools
```

This removes the need for end users to understand Python module paths.

### 2. Better self-check flow
Doctor is now split into:
- local base checks via `--doctor`
- explicit upstream/network checks via `--doctor-network`

This makes first-run experience much less confusing for offline users and source/dev environments.

### 3. Cleaner release artifacts
Build outputs now:
- keep the MCP package and docs that matter
- avoid shipping `tests/` and `.github/` in release artifacts

### 4. Better human-facing docs
The repository now includes:
- `docs/START_HERE.md`
- `docs/HANDOFF_MINIMAL.md`
- `docs/FAQ.md`
- `docs/AI_ONBOARDING.md`
- `docs/AGENT_AND_SKILL_MAP.md`

These make the project easier to adopt for both human users and AI integrators.

### 5. Host-specific MCP templates
The project now ships templates for:
- OpenClaw
- Claude Desktop
- Claude Code
- Continue
- VS Code
- Cursor
- Cline
- Windsurf
- Hermes
- Codex

### 6. CI and packaging hygiene
- `build` was added to `dev` dependencies so CI can execute `python -m build`
- `Live Smoke` was repositioned as a manual diagnostic workflow
- implementation status and changelog were refreshed

## Intended use
This release is suitable for:
- MCP host integration
- AI agent integration
- end-user trial installation
- OpenClaw adapter usage

## Notes
- The main product is the MCP server itself.
- The repository also contains an OpenClaw-specific skill adapter at `skills/newsbot-stock-routing/SKILL.md`.
