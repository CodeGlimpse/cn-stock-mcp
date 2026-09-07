# OpenCode：Windows 配置指南

目标版本：`cn-stock-mcp==0.2.3`（发布准备）。官方资料核对日期：2026-09-07。本页提供配置方法，本轮未进行 Host 连接或行情实测。

先完成 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，取得实际程序和配置路径。将示例中的 `YOUR_NAME` 及路径替换为本机值；按共同准备说明备份、合并配置。MCP 使用独立的普通 CPython 3.13 环境。



## 1. 配置入口与作用范围

- 用户级：默认 `%USERPROFILE%\.config\opencode\opencode.json`。
- 项目级：项目根目录的 `opencode.json`。
- 自定义 `OPENCODE_CONFIG` 或配置目录时，使用实际生效的位置；项目配置可覆盖用户配置。

本页用于 Windows 原生 OpenCode CLI 或本地后端。OpenCode 官方推荐 WSL 以获得更好的整体体验；WSL/远程后端不使用本页的 Windows 路径。合并下面的 `mcp` 对象。

## 2. 可复制配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "cn_stock_mcp": {
      "type": "local",
      "command": [
        "C:\\Users\\YOUR_NAME\\AppData\\Local\\cn-stock-mcp\\runtime\\venv\\Scripts\\cn-stock-mcp.exe",
        "--stdio"
      ],
      "environment": {
        "CN_STOCK_MCP_CONFIG": "C:\\Users\\YOUR_NAME\\AppData\\Local\\cn-stock-mcp\\config.json",
        "TOOL_PROFILE": "retail_v1_preview",
        "PYTHONUTF8": "1"
      },
      "enabled": true,
      "timeout": 30000
    }
  }
}
```



## 3. 使配置生效与查看工具

重新启动本地 OpenCode 会话，运行 `opencode mcp list` 查看服务器状态。在会话工具选择中启用 `cn_stock_mcp` 提供的工具。

查看本服务器的工具列表，默认应包含 [共同准备中列出的 10 个工具](WINDOWS_AGENT_SETUP.md#4-查看工具与客户自查)。连接、发现工具与取得真实行情分别记录；本页没有预先认定任何客户端已实测通过。

## 4. 常见问题

- 复制其他 Host 模板后无效：OpenCode 使用 `mcp`、`type: local`、命令与参数组成的 `command` 数组，以及 `environment`。
- 启动工具发现超时：本模板 `timeout: 30000` 的单位是毫秒，官方将其用于获取工具；它不是所有行情调用的总时限。
- 桌面客户端连接了 WSL/远程后端：切换到预期 Windows 本地运行环境。
- 工具被过滤：检查 OpenCode 的工具权限/启用配置和当前 Agent。

通用的路径、JSON 转义、Token 文件和多环境问题见 [Windows 共同准备](WINDOWS_AGENT_SETUP.md#5-常见问题)。

## 5. 停用与恢复

将 `mcp.cn_stock_mcp.enabled` 改为 `false`，重开会话；删除时只移除该对象。按需恢复配置备份。

## 官方依据

- [OpenCode：MCP servers](https://opencode.ai/docs/mcp-servers/)
- [OpenCode：Config](https://opencode.ai/docs/config/)
- [OpenCode：Windows support](https://opencode.ai/docs/windows-wsl/)
