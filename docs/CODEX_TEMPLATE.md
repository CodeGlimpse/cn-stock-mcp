# Codex：Windows 配置指南

目标版本：`cn-stock-mcp==0.2.3`（发布准备）。官方资料核对日期：2026-09-07。本页提供配置方法，本轮未进行 Host 连接或行情实测。

先完成 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，取得实际程序和配置路径。将示例中的 `YOUR_NAME` 及路径替换为本机值；按共同准备说明备份、合并配置。MCP 使用独立的普通 CPython 3.13 环境。



## 1. 配置入口与作用范围

- 用户级：`%USERPROFILE%\.codex\config.toml`。
- 项目级：项目目录下的 `.codex\config.toml`，只对受信任的项目生效。
- 桌面客户端可在 `Settings → MCP servers` 添加；IDE 扩展可从 MCP 设置入口编辑。官方文档说明同一 Codex Host 的本地客户端共用配置。
- 使用自定义配置目录时，编辑该 Host 实际采用的文件。

本页推荐用户级配置。将下面的两个 TOML 表合并进现有文件；如果已有同名表，更新它，避免重复声明。

## 2. 可复制配置

```toml
[mcp_servers.cn_stock_mcp]
command = 'C:\Users\YOUR_NAME\AppData\Local\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe'
args = ["--stdio"]
cwd = 'C:\Users\YOUR_NAME\AppData\Local\cn-stock-mcp\runtime'
startup_timeout_sec = 30
tool_timeout_sec = 60
enabled_tools = ["stock_search", "market_brief", "stock_snapshot", "stock_quote", "stock_history", "stock_review", "watchlist_review", "trading_calendar", "sector_review", "hot_theme_tracker"]

[mcp_servers.cn_stock_mcp.env]
CN_STOCK_MCP_CONFIG = 'C:\Users\YOUR_NAME\AppData\Local\cn-stock-mcp\config.json'
TOOL_PROFILE = "retail_v1_preview"
PYTHONUTF8 = "1"
```

也可用 CLI 添加基础配置，随后按上面的 TOML 设置工作目录、超时和白名单：

```powershell
$mcpExe = Join-Path $env:LOCALAPPDATA 'cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe'
$configPath = Join-Path $env:LOCALAPPDATA 'cn-stock-mcp\config.json'
codex mcp add cn_stock_mcp --env "CN_STOCK_MCP_CONFIG=$configPath" --env TOOL_PROFILE=retail_v1_preview --env PYTHONUTF8=1 -- $mcpExe --stdio
```

CLI 和手动配置任选一种作为初次添加方式。

## 3. 使配置生效与查看工具

保存后在桌面 MCP 设置中选择 `Restart`；IDE 扩展使用其重启入口；CLI 重新启动会话。CLI 可用 `codex mcp list` 查看配置，在交互界面用 `/mcp` 查看连接和工具。

查看本服务器的工具列表，默认应包含 [共同准备中列出的 10 个工具](WINDOWS_AGENT_SETUP.md#4-查看工具与客户自查)。连接、发现工具与取得真实行情分别记录；本页没有预先认定任何客户端已实测通过。

## 4. 常见问题

- 找不到程序：核对绝对路径以及运行 Codex 的 Windows 账号。
- 项目级配置未加载：核对项目是否受信任、同名配置是否在其他层覆盖。
- 工具不全：检查 `enabled_tools` / `disabled_tools` 和服务器工具档；本模板的白名单是额外限制。
- 启动失败：先做共同准备中的本地自检，再查看该服务器的脱敏错误。

通用的路径、JSON 转义、Token 文件和多环境问题见 [Windows 共同准备](WINDOWS_AGENT_SETUP.md#5-常见问题)。

## 5. 停用与恢复

可在 MCP 设置中禁用服务器，或在 `[mcp_servers.cn_stock_mcp]` 中设 `enabled = false`。移除时只删除本服务器及其 env 表，保存后重载；需要回退时恢复本次备份。

## 官方依据

- [OpenAI：Model Context Protocol](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
