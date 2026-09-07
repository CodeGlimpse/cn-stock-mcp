# Cursor：Windows 配置指南

目标版本：`cn-stock-mcp==0.2.3`（发布准备）。官方资料核对日期：2026-09-07。本页提供配置方法，本轮未进行 Host 连接或行情实测。

先完成 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，取得实际程序和配置路径。将示例中的 `YOUR_NAME` 及路径替换为本机值；按共同准备说明备份、合并配置。MCP 使用独立的普通 CPython 3.13 环境。



## 1. 配置入口与作用范围

- 用户级：`%USERPROFILE%\.cursor\mcp.json`。
- 项目级：项目根目录的 `.cursor\mcp.json`。
- 新版可从 `Customize` 页面管理 MCP；若界面不同，按上述文件方式配置。

个人使用推荐用户级文件；团队项目使用项目级文件。选定一个作用域，创建父目录并合并以下 JSON。

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

保存后从 Cursor 的 MCP 管理入口刷新或重载服务器；若版本没有独立重载按钮，重新打开 Cursor。进入可使用工具的 Agent 对话，并在工具列表启用本服务器。

查看本服务器的工具列表，默认应包含 [共同准备中列出的 10 个工具](WINDOWS_AGENT_SETUP.md#4-查看工具与客户自查)。连接、发现工具与取得真实行情分别记录；本页没有预先认定任何客户端已实测通过。

## 4. 常见问题

- 当前项目没有工具：检查配置所在作用域和该会话的工具开关。
- command 不能执行：核对绝对路径；配置文件中的文字 `%LOCALAPPDATA%` 不等于 PowerShell 已展开的路径。
- 模型没有调用工具：确认当前模式和模型支持工具调用，并已启用该服务器。
- 同名项重复：检查用户级与项目级配置。

通用的路径、JSON 转义、Token 文件和多环境问题见 [Windows 共同准备](WINDOWS_AGENT_SETUP.md#5-常见问题)。

## 5. 停用与恢复

先在 MCP 管理入口停用。永久移除时从所选 `mcp.json` 删除本服务器条目，再重载；恢复时使用本次备份。

## 官方依据

- [Cursor：Model Context Protocol](https://cursor.com/docs/mcp)
