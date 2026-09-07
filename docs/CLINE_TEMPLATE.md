# Cline：Windows 配置指南

适用版本：`cn-stock-mcp==0.2.3`。官方资料核对日期：2026-09-07。本页提供配置方法，本轮未进行 Host 连接或行情实测。

先完成 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，取得实际程序和配置路径。将示例中的 `YOUR_NAME` 及路径替换为本机值；按共同准备说明备份、合并配置。MCP 使用独立的普通 CPython 3.13 环境。



## 1. 配置入口与作用范围

- IDE 扩展：Cline 面板顶部 `MCP Servers → Configure → Configure MCP Servers`，打开扩展实际使用的 JSON。
- Cline CLI：`%USERPROFILE%\.cline\mcp.json`；也可以运行 `cline mcp` 向导。
- IDE 与 CLI 分别配置；不要根据另一种客户端的目录推定当前文件。

在实际使用的客户端中打开配置，合并以下 `mcpServers` 对象。`autoApprove: []` 保留工具调用确认。

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
      "disabled": false,
      "autoApprove": []
    }
  }
}
```



## 3. 使配置生效与查看工具

保存后在 MCP Servers 面板启用并重启服务器，查看工具列表。CLI 用户可用 `cline mcp` 向导查看状态、管理和启停服务器，再重新进入会话。

查看本服务器的工具列表，默认应包含 [共同准备中列出的 10 个工具](WINDOWS_AGENT_SETUP.md#4-查看工具与客户自查)。连接、发现工具与取得真实行情分别记录；本页没有预先认定任何客户端已实测通过。

## 4. 常见问题

- IDE 没变化：确认编辑的是扩展入口打开的文件，而非 CLI 的 `.cline\mcp.json`。
- 显示已禁用：检查 `disabled` 与面板开关。
- stdio 无法启动：检查 command、args 和 Windows 账号对运行目录的访问权限。
- 工具调用等待：检查是否有待处理的调用确认。

通用的路径、JSON 转义、Token 文件和多环境问题见 [Windows 共同准备](WINDOWS_AGENT_SETUP.md#5-常见问题)。

## 5. 停用与恢复

在管理界面禁用或设 `disabled: true`。需要删除时仅移除 `mcpServers.cn_stock_mcp`；CLI 向导也提供 Delete server。之后重载，必要时恢复备份。

## 官方依据

- [Cline：MCP](https://docs.cline.bot/mcp/mcp-overview)
- [Cline：Config](https://docs.cline.bot/getting-started/config)
