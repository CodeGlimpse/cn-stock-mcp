# Windows Agent 配置总表

目标版本：`cn-stock-mcp==0.2.3`（发布准备）。更新日期：2026-09-07。

这套指南覆盖以下 13 款软件的 Windows 本地 stdio 配置。先完成 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，再打开所用软件的专页。每页提供配置入口、作用范围、可复制配置、重载、自查、停用与恢复方法。

本轮按用户决定只核对官方资料并做离线检查，不执行真实 Host 连接或行情测试。官方来源与地址变化见 [来源记录](HOST_CONFIGURATION_SOURCES.md)。配置文档覆盖范围不等于客户端实测结果；原有首发售后条款仍以 [交付约定](COMMERCIAL_DELIVERY_TEMPLATE.md) 为准。

## 按软件选择

| 软件 | 配置形式 | 入口 / 默认位置 |
| --- | --- | --- |
| [Codex](CODEX_TEMPLATE.md) | TOML | 用户 `.codex\config.toml`；受信任项目 `.codex\config.toml` |
| [Claude Code](CLAUDE_CODE_TEMPLATE.md) | JSON / CLI | `claude mcp add --scope user`；项目 `.mcp.json` |
| [Claude Desktop](CLAUDE_DESKTOP_TEMPLATE.md) | JSON | `%APPDATA%\Claude\claude_desktop_config.json` |
| [Cursor](CURSOR_TEMPLATE.md) | JSON | 用户 `.cursor\mcp.json` 或项目 `.cursor\mcp.json` |
| [VS Code / GitHub Copilot](VSCODE_TEMPLATE.md) | JSON / JSONC | `MCP: Open User Configuration`；项目 `.vscode\mcp.json` |
| [Cline](CLINE_TEMPLATE.md) | JSON / UI | IDE 的 Configure MCP Servers；CLI 的 `.cline\mcp.json` |
| [Windsurf / Cascade](WINDSURF_TEMPLATE.md) | JSON | `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| [Continue](CONTINUE_TEMPLATE.md) | YAML / JSON | 项目 `.continue\mcpServers\cn-stock-mcp.yaml` |
| [OpenClaw](OPENCLAW_HOST_TEMPLATE.md) | JSON5 / CLI / UI | Windows 原生 Gateway 的 `.openclaw\openclaw.json` |
| [Hermes Agent](HERMES_TEMPLATE.md) | YAML | 用户 `.hermes\config.yaml` 或活动 Profile |
| [OpenCode](OPENCODE_TEMPLATE.md) | JSON / JSONC | 用户 `.config\opencode\opencode.json` 或项目 `opencode.json` |
| [Gemini CLI](GEMINI_CLI_TEMPLATE.md) | JSON / CLI | 用户或项目 `.gemini\settings.json` |
| [Cherry Studio](CHERRY_STUDIO_TEMPLATE.md) | UI 字段 | `设置 → MCP → MCP 服务器`，再绑定目标 Agent |

表中的用户目录以 `%USERPROFILE%` 为起点；自定义 Profile 或配置目录以实际生效文件为准。文件路径、命令和参数应替换成客户本机值。

## 推荐使用顺序

1. [固定版本 Windows 安装](AI_DEPLOY_WINDOWS.md)：核验 wheel、运行时约束和 SHA256。
2. [共同准备](WINDOWS_AGENT_SETUP.md)：客户保管 Token，取得实际路径，备份配置。
3. 从上表选择专页，使用该软件自己的配置结构进行合并。
4. 按专页使配置生效；客户需要连接检查时查看本服务器的工具目录。
5. 客户需要真实数据验证时再采用 [retail 样本计划](RETAIL_ACCEPTANCE.md)；本轮未执行。

## 几个关键差异

- Codex 使用 TOML 的 `mcp_servers` 表。
- VS Code 自身的 `mcp.json` 使用 `servers`。
- OpenClaw 使用 `mcp.servers`；配置所属 Gateway 必须能启动该 Windows 程序。
- Hermes 使用 YAML 的 `mcp_servers`。
- OpenCode 使用 `mcp`，其 `command` 是包含参数的数组，环境字段名是 `environment`。
- Continue 的独立 YAML 需要 `name`、`version`、`schema`；也支持放在指定目录中的 JSON。
- Cherry Studio 添加服务器后还需要给目标 Agent 绑定。
- 其余 JSON 格式也应按专页填写，不能仅凭相似字段推定其他客户端兼容。

仓库还包含可选 [OpenClaw Skill 适配说明](OPENCLAW_INTEGRATION.md)。安装 MCP 与加载 Skill 是两项独立配置。
