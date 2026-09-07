# Continue：Windows 配置指南

目标版本：`cn-stock-mcp==0.2.3`（发布准备）。官方资料核对日期：2026-09-07。本页提供配置方法，本轮未进行 Host 连接或行情实测。

先完成 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，取得实际程序和配置路径。将示例中的 `YOUR_NAME` 及路径替换为本机值；按共同准备说明备份、合并配置。MCP 使用独立的普通 CPython 3.13 环境。



## 1. 配置入口与作用范围

工作区独立文件：`<项目目录>\.continue\mcpServers\cn-stock-mcp.yaml`。目录名 `mcpServers` 是复数。

在需要使用股票工具的项目创建上述文件。独立 YAML 块需包含 `name`、`version` 和 `schema`；采用两个空格缩进，不使用制表符。

## 2. 可复制配置

```yaml
name: cn-stock-mcp
version: 0.2.3
schema: v1
mcpServers:
  - name: cn_stock_mcp
    type: stdio
    command: 'C:\Users\YOUR_NAME\AppData\Local\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe'
    args:
      - --stdio
    env:
      CN_STOCK_MCP_CONFIG: 'C:\Users\YOUR_NAME\AppData\Local\cn-stock-mcp\config.json'
      TOOL_PROFILE: retail_v1_preview
      PYTHONUTF8: '1'
```

如已有标准 JSON 配置，也可保存为 `.continue\mcpServers\cn-stock-mcp.json`，任选一种格式：

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

保存后重载 Continue 配置或重新加载编辑器窗口。在 Continue 中选择 `Agent` 模式并启用对应工具；官方说明 MCP 仅在 Agent 模式使用。

查看本服务器的工具列表，默认应包含 [共同准备中列出的 10 个工具](WINDOWS_AGENT_SETUP.md#4-查看工具与客户自查)。连接、发现工具与取得真实行情分别记录；本页没有预先认定任何客户端已实测通过。

## 4. 常见问题

- 工具不出现：检查当前是否为 Agent 模式、项目目录是否正确。
- YAML 加载失败：检查缩进和独立块的三个元数据字段。
- 重复服务器：同一目录中不要同时保留内容相同的 YAML 与 JSON。
- 当前窗口是远程工作区：本模板只适用于能启动 Windows 本地程序的运行环境。

通用的路径、JSON 转义、Token 文件和多环境问题见 [Windows 共同准备](WINDOWS_AGENT_SETUP.md#5-常见问题)。

## 5. 停用与恢复

将此独立配置文件备份到 `.continue\mcpServers` 目录之外后移除原配置，避免备份仍被自动发现；或者只移除该条目。重载 Continue 后生效。

## 官方依据

- [Continue：How to Set Up Model Context Protocol](https://docs.continue.dev/customize/deep-dives/mcp)
- [Continue：config.yaml Reference](https://docs.continue.dev/reference)
