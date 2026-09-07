# Gemini CLI：Windows 配置指南

适用版本：`cn-stock-mcp==0.2.3`。官方资料核对日期：2026-09-07。本页提供配置方法，本轮未进行 Host 连接或行情实测。

先完成 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，取得实际程序和配置路径。将示例中的 `YOUR_NAME` 及路径替换为本机值；按共同准备说明备份、合并配置。MCP 使用独立的普通 CPython 3.13 环境。



## 1. 配置入口与作用范围

- 用户级：`%USERPROFILE%\.gemini\settings.json`。
- 项目级：项目根目录的 `.gemini\settings.json`。
- `gemini mcp add` 默认写项目作用域；个人跨项目使用时明确指定 `--scope user`。

先选择一个作用域。文件包含其他 Gemini 设置时，只合并 `mcpServers.cn_stock_mcp`。保留 `trust: false`，让客户端确认工具调用。

## 2. 可复制配置

```json
{
  "mcpServers": {
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
      "cwd": "C:\\Users\\YOUR_NAME\\AppData\\Local\\cn-stock-mcp\\runtime",
      "timeout": 60000,
      "trust": false,
      "includeTools": [
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
```

CLI 也能创建基础用户级配置，随后在 JSON 中补充工作目录、超时和白名单：

```powershell
$mcpExe = Join-Path $env:LOCALAPPDATA 'cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe'
$configPath = Join-Path $env:LOCALAPPDATA 'cn-stock-mcp\config.json'
gemini mcp add --scope user --transport stdio -e "CN_STOCK_MCP_CONFIG=$configPath" -e TOOL_PROFILE=retail_v1_preview -e PYTHONUTF8=1 cn_stock_mcp $mcpExe -- --stdio
```

## 3. 使配置生效与查看工具

重新启动 Gemini CLI，使用 `gemini mcp list` 或交互界面的 `/mcp list` 查看连接及工具。修改后重新进入会话，确认当前项目采用预期的配置层。

查看本服务器的工具列表，默认应包含 [共同准备中列出的 10 个工具](WINDOWS_AGENT_SETUP.md#4-查看工具与客户自查)。连接、发现工具与取得真实行情分别记录；本页没有预先认定任何客户端已实测通过。

## 4. 常见问题

- 配置没有跨项目复用：核对用户/项目作用域。
- 显示 Disabled：检查 `gemini mcp enable / disable` 保存的启用状态。
- 缺少工具：检查 `mcp.allowed` / `mcp.excluded`、`includeTools` / `excludeTools`；排除规则优先。
- 超时：本模板 `timeout: 60000` 单位为毫秒；先按共同说明检查安装、路径和权限。

通用的路径、JSON 转义、Token 文件和多环境问题见 [Windows 共同准备](WINDOWS_AGENT_SETUP.md#5-常见问题)。

## 5. 停用与恢复

可用 `gemini mcp disable cn_stock_mcp` 暂停。用户级定义用下方命令移除；项目级定义需选择 project 作用域或编辑项目文件。

```powershell
gemini mcp remove cn_stock_mcp --scope user
```

## 官方依据

- [Gemini CLI：MCP servers](https://geminicli.com/docs/tools/mcp-server/)
