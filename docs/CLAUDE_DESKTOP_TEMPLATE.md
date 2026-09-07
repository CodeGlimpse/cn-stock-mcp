# Claude Desktop：Windows 配置指南

目标版本：`cn-stock-mcp==0.2.3`（发布准备）。官方资料核对日期：2026-09-07。本页提供配置方法，本轮未进行 Host 连接或行情实测。

先完成 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，取得实际程序和配置路径。将示例中的 `YOUR_NAME` 及路径替换为本机值；按共同准备说明备份、合并配置。MCP 使用独立的普通 CPython 3.13 环境。



## 1. 配置入口与作用范围

用户级文件：`%APPDATA%\Claude\claude_desktop_config.json`。这是 Windows 桌面客户端的本地 MCP 配置。

打开 Claude Desktop 的 `Settings → Developer → Edit Config`。入口名称可能随版本显示为本地语言；由该入口打开实际配置文件，然后合并以下对象。

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
      }
    }
  }
}
```



## 3. 使配置生效与查看工具

保存文件后完全退出 Claude Desktop，包括系统托盘中的进程，再重新打开。在输入框的连接器/工具入口找到 `cn_stock_mcp`，查看可用工具；官方文档当前使用 `Connectors → Manage connectors`。

查看本服务器的工具列表，默认应包含 [共同准备中列出的 10 个工具](WINDOWS_AGENT_SETUP.md#4-查看工具与客户自查)。连接、发现工具与取得真实行情分别记录；本页没有预先认定任何客户端已实测通过。

## 4. 常见问题

- 修改后仍是旧配置：确认已完全退出并重开应用。
- ENOENT：确认 command 是实际 `cn-stock-mcp.exe` 的绝对路径，JSON 内反斜杠已转义。
- 服务器启动错误：在 `%APPDATA%\Claude\logs` 查看对应 MCP 日志的错误类别，分享前脱敏。
- 打开的是远程连接器 URL 设置：本服务使用本地 Developer 配置中的 stdio。

通用的路径、JSON 转义、Token 文件和多环境问题见 [Windows 共同准备](WINDOWS_AGENT_SETUP.md#5-常见问题)。

## 5. 停用与恢复

从 `mcpServers` 中移除 `cn_stock_mcp`，保留其他服务器，完全退出并重开应用。需要回退时恢复该配置文件的本次备份。

## 官方依据

- [MCP 官方：Connect to local MCP servers（Claude Desktop 示例）](https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers)
