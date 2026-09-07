# OpenClaw：Windows 配置指南

适用版本：`cn-stock-mcp==0.2.3`。官方资料核对日期：2026-09-07。本页提供配置方法，本轮未进行 Host 连接或行情实测。

先完成 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，取得实际程序和配置路径。将示例中的 `YOUR_NAME` 及路径替换为本机值；按共同准备说明备份、合并配置。MCP 使用独立的普通 CPython 3.13 环境。



## 1. 配置入口与作用范围

- 默认配置文件：`%USERPROFILE%\.openclaw\openclaw.json`，支持 JSON5。
- Control UI：`Settings → MCP → Configured servers → Add server`，选择 Stdio。
- 设置了 `OPENCLAW_CONFIG_PATH` 或 Profile 时，使用实际 Gateway 的活动配置文件。

本页适用于在 Windows 原生进程中运行的 OpenClaw Gateway。可以在 Control UI 添加基本字段，再用配置编辑器合并下方条目。

## 2. 可复制配置

```json
{
  "mcp": {
    "servers": {
      "cn_stock_mcp": {
        "command": "C:\\Users\\YOUR_NAME\\AppData\\Local\\cn-stock-mcp\\runtime\\venv\\Scripts\\cn-stock-mcp.exe",
        "args": [
          "--stdio"
        ],
        "env": {
          "CN_STOCK_MCP_CONFIG": "C:\\Users\\YOUR_NAME\\AppData\\Local\\cn-stock-mcp\\config.json",
          "TOOL_PROFILE": "retail_v1_preview",
          "PYTHONUTF8": "1"
        },
        "transport": "stdio",
        "cwd": "C:\\Users\\YOUR_NAME\\AppData\\Local\\cn-stock-mcp\\runtime",
        "enabled": true,
        "connectionTimeoutMs": 30000,
        "requestTimeoutMs": 60000,
        "toolFilter": {
          "include": [
            "stock_search",
            "market_brief",
            "stock_snapshot",
            "stock_quote",
            "stock_history",
            "stock_review",
            "watchlist_review",
            "trading_calendar",
            "sector_review",
            "hot_theme_tracker"
          ]
        }
      }
    }
  }
}
```

可选 CLI 添加基础定义，`--no-probe` 使这一步只保存配置；后续通过上方配置补充超时与工具过滤：

```powershell
$mcpExe = Join-Path $env:LOCALAPPDATA 'cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe'
$configPath = Join-Path $env:LOCALAPPDATA 'cn-stock-mcp\config.json'
$runtimeRoot = Join-Path $env:LOCALAPPDATA 'cn-stock-mcp\runtime'
openclaw mcp add cn_stock_mcp --command $mcpExe --arg=--stdio --cwd $runtimeRoot --env "CN_STOCK_MCP_CONFIG=$configPath" --env TOOL_PROFILE=retail_v1_preview --env PYTHONUTF8=1 --no-probe
```

可选 Skill 的用途与 Windows 路径见 [OpenClaw 适配说明](OPENCLAW_INTEGRATION.md)。

## 3. 使配置生效与查看工具

保存后 Gateway 的配置热重载会更新定义，下一轮发现工具使用新配置。可先执行 `openclaw mcp status --verbose` 和 `openclaw mcp doctor cn_stock_mcp` 做配置检查。客户需要检查真实连接时再运行 `openclaw mcp doctor cn_stock_mcp --probe`；它会启动 MCP 并枚举工具。

查看本服务器的工具列表，默认应包含 [共同准备中列出的 10 个工具](WINDOWS_AGENT_SETUP.md#4-查看工具与客户自查)。连接、发现工具与取得真实行情分别记录；本页没有预先认定任何客户端已实测通过。

## 4. 常见问题

- Windows Hub 窗口位于本机，不代表 Gateway 位于本机：官方 Hub 默认安装路径可能创建 WSL Gateway；本页的 Windows `.exe` 路径要求 Windows 原生 Gateway。
- 工具不可见：检查 `toolFilter`、会话工具策略；官方说明 `minimal` 工具档或 `bundle-mcp` deny 会隐藏 MCP 工具。
- CLI reload 未影响现有 Gateway：`openclaw mcp reload` 只刷新当前 CLI 进程拥有的运行时，正在别处运行的 Gateway 需要自己的重载或重启。
- 使用 `mcp.servers` 保存第三方服务器；`openclaw mcp serve` 是相反方向的 OpenClaw 服务端功能。

通用的路径、JSON 转义、Token 文件和多环境问题见 [Windows 共同准备](WINDOWS_AGENT_SETUP.md#5-常见问题)。

## 5. 停用与恢复

将本服务器 `enabled` 设为 `false` 暂停；移除使用 `openclaw mcp unset cn_stock_mcp`，或只删除 `mcp.servers.cn_stock_mcp`。必要时恢复本次配置备份并让 Gateway 重载。

## 官方依据

- [OpenClaw：Connect MCP servers](https://docs.openclaw.ai/tools/mcp)
- [OpenClaw：MCP CLI](https://docs.openclaw.ai/cli/mcp)
- [OpenClaw：Windows](https://docs.openclaw.ai/platforms/windows)
- [OpenClaw：Configuration](https://docs.openclaw.ai/gateway/configuration)
