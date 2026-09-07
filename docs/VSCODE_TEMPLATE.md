# VS Code / GitHub Copilot：Windows 配置指南

适用版本：`cn-stock-mcp==0.2.3`。官方资料核对日期：2026-09-07。本页提供配置方法，本轮未进行 Host 连接或行情实测。

先完成 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，取得实际程序和配置路径。将示例中的 `YOUR_NAME` 及路径替换为本机值；按共同准备说明备份、合并配置。MCP 使用独立的普通 CPython 3.13 环境。



## 1. 配置入口与作用范围

- 用户级：`Ctrl+Shift+P → MCP: Open User Configuration`，编辑当前用户配置文件。
- 工作区级：项目根目录的 `.vscode\mcp.json`。
- 可用 `MCP: Add Server` 向导选择 stdio 与作用域。本页覆盖 VS Code 内的 Copilot Chat / Agent。

个人 Windows 本地使用推荐通过命令面板打开用户配置。VS Code 的顶层字段是 `servers`；把下面对象合并进去。

## 2. 可复制配置

```json
{
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
      "type": "stdio",
      "cwd": "C:\\Users\\YOUR_NAME\\AppData\\Local\\cn-stock-mcp\\runtime"
    }
  }
}
```



## 3. 使配置生效与查看工具

用 `MCP: List Servers` 或配置文件内的 Start / Restart 操作启动服务器，按提示确认信任。在 Copilot Chat 的工具选择器中启用本服务器，使用支持工具的 Agent 会话。

查看本服务器的工具列表，默认应包含 [共同准备中列出的 10 个工具](WINDOWS_AGENT_SETUP.md#4-查看工具与客户自查)。连接、发现工具与取得真实行情分别记录；本页没有预先认定任何客户端已实测通过。

## 4. 常见问题

- 文件被忽略：VS Code 自身的 `mcp.json` 使用 `servers` 顶层键。
- 使用多个 VS Code Profile：各 Profile 的用户 MCP 配置可能不同。
- SSH、容器或远程工作区：确认服务实际运行在 Windows 本机；该页路径属于本机用户环境。
- Agent Host 会话：官方说明 VS Code 会转发其 MCP 配置；本模板没有交互式 input 依赖。独立 Copilot CLI 的配置文件另有格式。

通用的路径、JSON 转义、Token 文件和多环境问题见 [Windows 共同准备](WINDOWS_AGENT_SETUP.md#5-常见问题)。

## 5. 停用与恢复

用服务器管理入口停止；持久移除时删除所选用户/工作区文件中的 `servers.cn_stock_mcp` 条目。保留其他服务器，重载并按需恢复备份。

## 官方依据

- [VS Code：Add and manage MCP servers](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
- [VS Code：MCP configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)
