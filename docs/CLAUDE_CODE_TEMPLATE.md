# Claude Code：Windows 配置指南

适用版本：`cn-stock-mcp==0.2.3`。官方资料核对日期：2026-09-07。本页提供配置方法，本轮未进行 Host 连接或行情实测。

先完成 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，取得实际程序和配置路径。将示例中的 `YOUR_NAME` 及路径替换为本机值；按共同准备说明备份、合并配置。MCP 使用独立的普通 CPython 3.13 环境。



## 1. 配置入口与作用范围

- 用户级：使用 `claude mcp add --scope user`；Claude Code 把此配置保存到用户配置中（默认 `%USERPROFILE%\.claude.json`）。
- 项目级：项目根目录的 `.mcp.json`。
- `local` 是默认的当前项目个人作用域，与 `user` 的所有项目作用域不同。

项目共享方式可把下面的 JSON 合并到 `.mcp.json`；首次在该项目运行 Claude Code 时按提示确认项目和 MCP 服务器。用户级添加见后面的 PowerShell 命令。

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
      "type": "stdio"
    }
  }
}
```

个人跨项目使用时，可改用用户级 CLI 添加：

```powershell
$mcpExe = Join-Path $env:LOCALAPPDATA 'cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe'
$configPath = Join-Path $env:LOCALAPPDATA 'cn-stock-mcp\config.json'
claude mcp add --transport stdio --scope user cn_stock_mcp --env "CN_STOCK_MCP_CONFIG=$configPath" --env TOOL_PROFILE=retail_v1_preview --env PYTHONUTF8=1 -- $mcpExe --stdio
```

两种作用域任选其一；命令中的 `--` 之后是 MCP 程序及其参数。

## 3. 使配置生效与查看工具

重新启动 Claude Code 会话。运行 `claude mcp list` 或 `claude mcp get cn_stock_mcp`，在交互会话中用 `/mcp` 查看状态。项目级服务器显示 Pending approval 时，在受信任项目中完成确认。

查看本服务器的工具列表，默认应包含 [共同准备中列出的 10 个工具](WINDOWS_AGENT_SETUP.md#4-查看工具与客户自查)。连接、发现工具与取得真实行情分别记录；本页没有预先认定任何客户端已实测通过。

## 4. 常见问题

- 配置只在某个项目出现：核对 `--scope`，个人跨项目使用应选 `user`。
- 项目配置不生效：检查 `.mcp.json`、工作区信任及该服务器的审批状态。
- Windows 启动失败：此服务直接启动 `.exe`，命令字段与 `--stdio` 参数分别填写。
- 同名服务器被覆盖：检查用户、项目和 local 配置层，保留一个预期定义。

通用的路径、JSON 转义、Token 文件和多环境问题见 [Windows 共同准备](WINDOWS_AGENT_SETUP.md#5-常见问题)。

## 5. 停用与恢复

在 `/mcp` 中可暂时禁用该服务器。用户级定义用下面的命令移除；项目级定义只从 `.mcp.json` 删除对应条目并重开会话。

```powershell
claude mcp remove cn_stock_mcp --scope user
```

## 官方依据

- [Claude Code：Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)
