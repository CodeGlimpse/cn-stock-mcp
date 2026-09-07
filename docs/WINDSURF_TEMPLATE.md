# Windsurf / Cascade：Windows 配置指南

目标版本：`cn-stock-mcp==0.2.3`（发布准备）。官方资料核对日期：2026-09-07。本页提供配置方法，本轮未进行 Host 连接或行情实测。

先完成 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，取得实际程序和配置路径。将示例中的 `YOUR_NAME` 及路径替换为本机值；按共同准备说明备份、合并配置。MCP 使用独立的普通 CPython 3.13 环境。

官方入口的品牌和地址变更已记录在 [来源与核对说明](HOST_CONFIGURATION_SOURCES.md) 中。

## 1. 配置入口与作用范围

用户级文件：`%USERPROFILE%\.codeium\windsurf\mcp_config.json`。从 Cascade 的 MCP 图标或设置中的 `Cascade → MCP Servers` 打开原始配置。

合并以下 JSON，并在 Cascade 中启用本服务器。实际界面可能显示 Windsurf Settings 或 Devin Settings。

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

保存后回到 Cascade 的 MCP 管理面板刷新或重载；如果当前版本没有该操作，重新打开客户端。检查本服务器及其工具是否启用，再进入 Cascade 对话。

查看本服务器的工具列表，默认应包含 [共同准备中列出的 10 个工具](WINDOWS_AGENT_SETUP.md#4-查看工具与客户自查)。连接、发现工具与取得真实行情分别记录；本页没有预先认定任何客户端已实测通过。

## 4. 常见问题

- 文档品牌与安装版本不同：本次 Windsurf 官方地址重定向到 Devin Desktop 文档，但该页仍明确使用 `.codeium\windsurf\mcp_config.json`；优先由客户端入口打开实际文件。
- 团队环境无法添加：核对管理员 MCP allowlist，服务器 ID 区分大小写。
- 只缺少部分工具：核对客户端工具开关、`disabledTools` 及服务端 retail 档。
- 连接失败：核对 Windows 路径和客户端实际运行账号。

通用的路径、JSON 转义、Token 文件和多环境问题见 [Windows 共同准备](WINDOWS_AGENT_SETUP.md#5-常见问题)。

## 5. 停用与恢复

通过 MCP 管理面板禁用，或从配置中仅删除 `cn_stock_mcp`。保存、重载；需要回退时恢复本次备份。

## 官方依据

- [Windsurf 官方入口（本次重定向）](https://docs.windsurf.com/windsurf/cascade/mcp)
- [当前官方页面：Cascade MCP Integration](https://docs.devin.ai/desktop/cascade/mcp)
