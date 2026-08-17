# Windows AI 部署与首次问答验收

本文件是给客户 Agent 的部署合同。Agent 必须按固定版本执行，遇到系统安装、网络、Host 配置覆盖或权限问题时先说明并请求用户确认；不得读取、打印、上传或写入 Zhitu token。

## 目标版本与安全边界

- 首发版本：`cn-stock-mcp==0.2.0`
- 运行方式：本机 stdio MCP server
- 默认配置文件：`%LOCALAPPDATA%\cn-stock-mcp\config.json`
- 首选工具档：`retail_v1_preview`
- Host：Codex、Claude Code、OpenClaw、Hermes Agent
- 该项目只查询公开市场数据，不连接券商、不保存交易账户、不下单。

不要把 token 写入 MCP Host 配置、Git 仓库、命令行参数、聊天记录或诊断包。

## Agent 执行流程

### 1. 预检

确认 Windows x64、Python 3.11–3.13 和网络可用。若没有受支持的 Python，先向用户说明将进行用户级安装，再执行官方 Python 安装流程；不要修改系统 PATH 或全局执行策略。

### 2. 固定版本安装

```powershell
py -3.13 -m venv "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv"
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\python.exe" -m pip install --upgrade pip
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\python.exe" -m pip install cn-stock-mcp==0.2.0
```

记录安装版本和解释器路径。不要使用未固定版本的 `pip install cn-stock-mcp` 作为验收证据。

解析并记录 Host 必须使用的绝对命令路径：

```powershell
$mcpExe = Join-Path $env:LOCALAPPDATA "cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe"
(Resolve-Path -LiteralPath $mcpExe).Path
```

不要假设该用户专用虚拟环境已加入 `PATH`。

### 3. 创建配置并交给用户填 token

```powershell
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe" --init-config
```

向用户展示配置文件路径，然后暂停：由用户手动打开该文件，在 `zhitu.tokens.primary` 中填写 token。Agent 只可继续执行状态检查，不得读取文件内容。

### 4. 本地与网络自检

```powershell
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe" --version
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe" --doctor --json
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe" --doctor-network --json
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe" --list-tools --json
```

`--doctor` 可因跳过网络检查显示 `WARN`，但退出码必须为 0；`--doctor-network` 必须退出 0。`--list-tools --json` 必须只列出 `retail_v1_preview` 的 10 个工具。输出中只允许出现配置路径、状态和数量，不得出现 token 原文、尾号或 URL 查询参数。

### 5. 配置 Host

使用对应 Host 模板，把其中的 `cn-stock-mcp` 命令替换为步骤 2 解析出的 `cn-stock-mcp.exe` 绝对路径；只写 `command`、`args`、必要的工作目录和工具白名单，不要加入 `ZHITU_TOKEN`。修改前备份原配置，保留原有字段和其他 MCP server。

- Codex：`docs/CODEX_TEMPLATE.md`
- Claude Code：`docs/CLAUDE_CODE_TEMPLATE.md`
- OpenClaw：`docs/OPENCLAW_HOST_TEMPLATE.md`
- Hermes Agent：`docs/HERMES_TEMPLATE.md`

### 6. 重载并首次问答

重载对应 Host，确认 server 已连接并看到 `retail_v1_preview` 的 10 个工具。Host 没有原生工具白名单时，以 server 端工具档的 10 个结果为准。使用以下固定问题：

> 查询平安银行最新行情，给出数据来源、数据时间、交易时段和数据质量；不要提供投资建议。

验收必须看到 symbol、source、freshness/as_of、session_context 或等价信息，并确认回答没有 token、下单指令、收益承诺或荐股结论。

## 回滚

如果 Host 连接失败，先恢复刚才的配置备份，再运行 `--doctor --json`。不要删除用户配置文件；卸载只允许移除本项目虚拟环境，token 文件由用户自行保留或删除。

## Agent 禁止事项

- 禁止读取或回显 `%LOCALAPPDATA%\cn-stock-mcp\config.json` 的 token 字段。
- 禁止把 token 放入 Host JSON/TOML/YAML、PowerShell 历史、日志或截图。
- 禁止执行买卖、账户登录、券商连接或自动交易。
- 禁止以 `data_quality`、candidate score、risk tag 或技术指标作为投资建议。
