# Hermes Agent：Windows 配置指南

适用版本：`cn-stock-mcp==0.2.3`。官方资料核对日期：2026-09-07。本页提供配置方法，本轮未进行 Host 连接或行情实测。

先完成 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，取得实际程序和配置路径。将示例中的 `YOUR_NAME` 及路径替换为本机值；按共同准备说明备份、合并配置。MCP 使用独立的普通 CPython 3.13 环境。



## 1. 配置入口与作用范围

默认用户配置：`%USERPROFILE%\.hermes\config.yaml`，顶层为 `mcp_servers`。使用 `HERMES_HOME` 或 Profile 时，打开活动环境实际使用的配置。

官方目前提供 Windows 原生安装。确认 Hermes 运行于 Windows 本机后，把下面的服务器条目合并进 YAML；已存在 `mcp_servers` 时在其下新增子项，不重复顶层键。

## 2. 可复制配置

```yaml
mcp_servers:
  cn_stock_mcp:
    command: 'C:\Users\YOUR_NAME\AppData\Local\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe'
    args: ['--stdio']
    env:
      CN_STOCK_MCP_CONFIG: 'C:\Users\YOUR_NAME\AppData\Local\cn-stock-mcp\config.json'
      TOOL_PROFILE: retail_v1_preview
      PYTHONUTF8: '1'
    tools:
      include: ["stock_search", "market_brief", "stock_snapshot", "stock_quote", "stock_history", "stock_review", "watchlist_review", "trading_calendar", "sector_review", "hot_theme_tracker"]
```



## 3. 使配置生效与查看工具

启动 `hermes chat`；正在运行的会话中使用 `/reload-mcp` 重载配置和工具目录。桌面版应在对应 Agent 的 MCP/工具管理入口查看状态，必要时重新打开会话。

查看本服务器的工具列表，默认应包含 [共同准备中列出的 10 个工具](WINDOWS_AGENT_SETUP.md#4-查看工具与客户自查)。连接、发现工具与取得真实行情分别记录；本页没有预先认定任何客户端已实测通过。

## 4. 常见问题

- 同时装有 WSL 与原生版：确认编辑的配置和实际运行的 Hermes 属于同一环境。
- YAML 解析失败：检查缩进、重复的 `mcp_servers` 键；Windows 路径使用单引号。
- 工具不全：检查 `tools.include` / `tools.exclude` 以及服务器是否被设为 `enabled: false`。
- 配置更新未生效：执行 `/reload-mcp` 或重开会话；无需把 MCP 依赖安装到 Hermes 自身环境。

通用的路径、JSON 转义、Token 文件和多环境问题见 [Windows 共同准备](WINDOWS_AGENT_SETUP.md#5-常见问题)。

## 5. 停用与恢复

在 `mcp_servers.cn_stock_mcp` 下添加 `enabled: false` 停用，或删除该子项。重载后生效；恢复时合并本次备份，保留其他服务器。

## 官方依据

- [Hermes：MCP integration](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp/)
- [Hermes：Installation（含原生 Windows）](https://hermes-agent.nousresearch.com/docs/getting-started/installation)
