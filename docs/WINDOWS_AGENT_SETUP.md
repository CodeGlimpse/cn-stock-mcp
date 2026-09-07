# Windows Agent 接入：共同准备

适用范围：Windows 11 x64、普通 CPython 3.13、本机 stdio、retail 10 工具。目标版本为 `0.2.3`，目前是发布准备版；安装公开版本前先确认同版本 Release 和校验文件已存在。

本轮交付为 13 款软件的配置指南及离线检查，按用户决定不执行真实 Host 连接或行情测试。下文的客户端操作和自查步骤供客户在自己的环境中使用。各客户端官方来源见 [来源记录](HOST_CONFIGURATION_SOURCES.md)，软件入口见 [配置总表](HOST_CONFIG_TEMPLATES.md)。

## 1. 安装一次，记录两个路径

先按 [Windows 部署说明](AI_DEPLOY_WINDOWS.md) 完成固定 wheel 与约束文件的 SHA256 核验、独立 venv 安装和客户本人填写 Token。已经完成安装时复用经过确认的运行目录。

安装后在 Windows PowerShell 中取得路径：

```powershell
$runtimeRoot = Join-Path $env:LOCALAPPDATA 'cn-stock-mcp\runtime'
$mcpExe = Join-Path $runtimeRoot 'venv\Scripts\cn-stock-mcp.exe'
$configPath = Join-Path $env:LOCALAPPDATA 'cn-stock-mcp\config.json'
$mcpExe
$configPath
```

- `mcpExe`：要让 Agent 启动的 `cn-stock-mcp.exe` 绝对路径。
- `configPath`：客户自己保管的 MCP 配置文件路径；Token 只在这个文件中手动填写。
- 若实际安装目录不同，用实际路径替换所有模板。`YOUR_NAME` 是占位符，不能原样保留。
- Agent 自身的 Python/Node 环境与 MCP 的独立 venv 可以不同；配置指向 MCP 的可执行文件。

## 2. 配置值怎样填写

| 字段 | 填写方法 |
| --- | --- |
| 启动命令 | `cn-stock-mcp.exe` 的完整路径；路径中的空格属于同一值 |
| 参数 | 单独的 `--stdio`；直接运行不带参数的程序会输出普通就绪文字 |
| `CN_STOCK_MCP_CONFIG` | 只填配置文件路径 |
| `TOOL_PROFILE` | `retail_v1_preview` |
| `PYTHONUTF8` | 字符串 `1` |
| 工作目录 | Host 支持该字段时，填已经存在的 `cn-stock-mcp\runtime` 目录 |

这些环境变量保存路径和运行选项。Token 值不放进 Host 配置、环境变量、命令行、提示词或聊天。

JSON 内的 Windows 反斜杠写成 `\\`；TOML/YAML 示例采用单引号路径。模板使用完整路径，避免依赖不同软件对 `%LOCALAPPDATA%`、`~` 或变量插值的不同处理。

本机 stdio 程序由 Agent 的实际运行进程启动。SSH、容器、WSL 或远程 Gateway 的文件系统与运行账号可能不同；本套指南只描述 Windows 原生本地运行方式。网页上的远程 URL 连接器不能直接接收本机 `.exe` 路径。

## 3. 备份、合并与恢复

文件配置先在本机创建带时间戳备份。下面以 Cursor 用户配置为例；其他软件用其页面列出的实际文件：

```powershell
$hostConfigPath = Join-Path $env:USERPROFILE '.cursor\mcp.json'
$hostBackupPath = $hostConfigPath + '.backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
if (Test-Path -LiteralPath $hostConfigPath) {
    Copy-Item -LiteralPath $hostConfigPath -Destination $hostBackupPath
}
```

已有顶层对象时合并本服务器子项，保留模型设置、其他服务器及未知字段；JSON/TOML/YAML 都不要重复声明同名键。已有 `cn_stock_mcp` 时更新原定义。若配置不存在，按对应页面创建父目录和文件。

配置备份可能包含其他服务的秘密，仅在本机保管。恢复时关闭对应连接，仅回退本次修改；若之后还有其他改动，手动恢复本服务器条目，避免整文件覆盖后续内容。

## 4. 查看工具与客户自查

本地检查命令如下；仅在客户自己已准备好配置时执行：

```powershell
$mcpExe = Join-Path $env:LOCALAPPDATA 'cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe'
$runtimeRoot = Join-Path $env:LOCALAPPDATA 'cn-stock-mcp\runtime'
Set-Location -LiteralPath $runtimeRoot
& $mcpExe --version
& $mcpExe --doctor --json
& $mcpExe --list-tools --json
```

这些命令不主动查询行情。`--doctor` 对“未运行网络检查”的说明可以是提示项；它与上游数据可用性是不同的证据。

默认服务器公开以下 10 个工具：

```text
stock_search
market_brief
stock_snapshot
stock_quote
stock_history
stock_review
watchlist_review
trading_calendar
sector_review
hot_theme_tracker
```

客户端可能给工具名添加服务器前缀。只检查本服务器的目录，不把 Host 的全部工具总数当成 10。Host 保存配置、成功启动服务、发现工具和完成行情查询是不同阶段。

客户需要实际查询时，再依 [retail 验收说明](RETAIL_ACCEPTANCE.md) 查看计划并决定是否执行；本轮没有执行。可使用以下首次查询提示词：

> 先查询最近交易日与交易时段，再查询 000001.SZ 最新行情。说明数据来源、数据时间、fallback、partial failure 和 data_quality；无法核实时明确说明，不提供投资建议。

## 5. 常见问题

| 现象 | 先检查 |
| --- | --- |
| 找不到命令 / ENOENT | 实际 exe 路径、安装账号、文件访问权限和引号 |
| JSON-RPC 解析失败 | 参数里是否有 `--stdio`，stdout 是否被其他程序输出污染 |
| 读到错误配置或 Token 不可用 | `CN_STOCK_MCP_CONFIG` 是否指向客户自己的文件；由客户本人检查文件，不把内容交给 Agent |
| 工具不出现 | Host 是否加载了正确作用域、连接是否启用、当前模型/模式是否支持工具 |
| 工具少于预期 | Host 工具过滤、Agent 绑定和服务端工具档 |
| 修改后仍是旧状态 | 按软件对应的重载、重启或新会话步骤处理 |
| 配置正确但调用失败 | 区分网络、Token、额度、上游与软件错误；保存脱敏错误类别 |
| 图形界面在 Windows，exe 却无法启动 | 确认实际后端/Gateway 是否运行于 Windows 本机 |

发生故障时先按上述类别定位，再决定修正范围；保留客户端原有的工具确认与系统权限设置。
