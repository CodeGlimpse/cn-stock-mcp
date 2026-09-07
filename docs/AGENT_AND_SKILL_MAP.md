# Agent 与 Skill 对照

13 款 Windows Agent 的接入方法统一从 [配置总表](HOST_CONFIG_TEMPLATES.md) 进入。它们通过 MCP 取得本项目的工具；配置结构和作用域由各客户端决定。

## 客户端入口

| 软件 | 配置指南 | 本仓库是否提供专属 Skill |
| --- | --- | --- |
| Codex | [CODEX_TEMPLATE.md](CODEX_TEMPLATE.md) | 无需专属 Skill |
| Claude Code | [CLAUDE_CODE_TEMPLATE.md](CLAUDE_CODE_TEMPLATE.md) | 无需专属 Skill |
| Claude Desktop | [CLAUDE_DESKTOP_TEMPLATE.md](CLAUDE_DESKTOP_TEMPLATE.md) | 无需专属 Skill |
| Cursor | [CURSOR_TEMPLATE.md](CURSOR_TEMPLATE.md) | 无需专属 Skill |
| VS Code / GitHub Copilot | [VSCODE_TEMPLATE.md](VSCODE_TEMPLATE.md) | 无需专属 Skill |
| Cline | [CLINE_TEMPLATE.md](CLINE_TEMPLATE.md) | 无需专属 Skill |
| Windsurf / Cascade | [WINDSURF_TEMPLATE.md](WINDSURF_TEMPLATE.md) | 无需专属 Skill |
| Continue | [CONTINUE_TEMPLATE.md](CONTINUE_TEMPLATE.md) | 无需专属 Skill |
| OpenClaw | [OPENCLAW_HOST_TEMPLATE.md](OPENCLAW_HOST_TEMPLATE.md) | [可选 OpenClaw 适配](OPENCLAW_INTEGRATION.md) |
| Hermes Agent | [HERMES_TEMPLATE.md](HERMES_TEMPLATE.md) | 无需专属 Skill |
| OpenCode | [OPENCODE_TEMPLATE.md](OPENCODE_TEMPLATE.md) | 无需专属 Skill |
| Gemini CLI | [GEMINI_CLI_TEMPLATE.md](GEMINI_CLI_TEMPLATE.md) | 无需专属 Skill |
| Cherry Studio | [CHERRY_STUDIO_TEMPLATE.md](CHERRY_STUDIO_TEMPLATE.md) | 无需专属 Skill |

## OpenClaw 的可选 Skill

仓库的 `skills/newsbot-stock-routing/` 提供新闻/复盘类任务的工具路由提示，wheel 也携带这份 Skill。它不安装 MCP server，也不保存 Token。先完成 MCP 配置，再按 [OpenClaw 适配说明](OPENCLAW_INTEGRATION.md) 决定是否加载。

## 给集成人员

接口与输入契约参见 [工具目录](TOOL_CATALOG.md)、[最小使用规则](AGENT_MINIMAL.md)、[最小示例](EXAMPLES_MINIMAL.md) 和 [接口说明](INTERFACE_SCHEMA.md)。默认 retail 只公开 10 个高层工具；full 档的底层工具不自动进入零售配置。
