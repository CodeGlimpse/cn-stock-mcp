# Windows AI 部署与首次问答验收

本文件是给客户 Agent 的部署合同。Agent 必须按固定版本执行，遇到系统安装、网络、Host 配置覆盖或权限问题时先说明并请求用户确认；不得读取、打印、上传或写入 Zhitu token。

## 目标版本与安全边界

- 当前固定版本：`cn-stock-mcp==0.2.2`
- 运行方式：本机 stdio MCP server
- 默认配置文件：`%LOCALAPPDATA%\cn-stock-mcp\config.json`
- 首选工具档：`retail_v1_preview`
- 首批文档化 Host：Codex、Claude Code、OpenClaw、Hermes Agent；本版本验证的是共同的 stdio MCP 合同，Host 图形界面仍需按客户环境单独验收。
- 该项目只查询公开市场数据，不连接券商、不保存交易账户、不下单。

不要把 token 写入 MCP Host 配置、Git 仓库、命令行参数、聊天记录或诊断包。

## Agent 执行流程

### 1. 预检

确认 Windows x64、Python 3.13（普通 CPython，不是 free-threaded 版本）和网络可用。项目代码兼容 Python 3.11–3.13，但本首发 Windows 自动部署合同固定验收 3.13；若没有受支持的 Python，先向用户说明将进行用户级安装，再执行官方 Python 安装流程；不要修改系统 PATH 或全局执行策略。

### 2. 固定版本安装

```powershell
$root = Join-Path $env:LOCALAPPDATA "cn-stock-mcp"
$venv = Join-Path $root "runtime\venv"
$download = Join-Path $root "downloads\0.2.2"
New-Item -ItemType Directory -Force -Path $download | Out-Null

py -3.13 -m venv $venv
$python = Join-Path $venv "Scripts\python.exe"
& $python -m pip install --upgrade pip
& $python -m pip download --only-binary=:all: --no-deps --dest $download cn-stock-mcp==0.2.2

$wheel = Get-ChildItem -LiteralPath $download -Filter "cn_stock_mcp-0.2.2-*.whl" | Select-Object -First 1
if (-not $wheel) { throw "v0.2.2 wheel was not found" }
$checksums = Join-Path $download "sha256sums.txt"
Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/CodeGlimpse/cn-stock-mcp/releases/download/v0.2.2/sha256sums.txt" -OutFile $checksums
$constraints = Join-Path $download "constraints-windows-py313.txt"
Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/CodeGlimpse/cn-stock-mcp/releases/download/v0.2.2/constraints-windows-py313.txt" -OutFile $constraints
$line = Get-Content -LiteralPath $checksums | Where-Object { $_ -match [regex]::Escape($wheel.Name) } | Select-Object -First 1
if (-not $line) { throw "v0.2.2 checksum entry was not found" }
$expected = ($line -split '\s+')[0].ToLowerInvariant()
$actual = (Get-FileHash -LiteralPath $wheel.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw "cn-stock-mcp wheel SHA256 mismatch" }
$constraintLine = Get-Content -LiteralPath $checksums | Where-Object { $_ -match [regex]::Escape($constraints | Split-Path -Leaf) } | Select-Object -First 1
if (-not $constraintLine) { throw "runtime dependency constraints checksum entry was not found" }
$constraintExpected = ($constraintLine -split '\s+')[0].ToLowerInvariant()
$constraintActual = (Get-FileHash -LiteralPath $constraints -Algorithm SHA256).Hash.ToLowerInvariant()
if ($constraintActual -ne $constraintExpected) { throw "runtime dependency constraints SHA256 mismatch" }

# The constraints file pins the tested Windows CPython 3.13 runtime closure;
# it prevents a future PyPI dependency release from silently changing the
# customer's installation.
& $python -m pip install -c $constraints $wheel.FullName
```

记录安装版本、解释器路径、wheel 文件名、依赖约束文件名和校验结果，但不要记录 token。不要使用未固定版本的 `pip install cn-stock-mcp` 作为验收证据。如果 PyPI 包、GitHub Release、wheel、依赖约束文件或校验项任一不存在，或 SHA256 不匹配，停止部署，不要改装 GitHub `main` 分支。

解析并记录 Host 必须使用的绝对命令路径：

```powershell
$mcpExe = Join-Path $env:LOCALAPPDATA "cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe"
(Resolve-Path -LiteralPath $mcpExe).Path
```

不要假设该用户专用虚拟环境已加入 `PATH`。

安装后的客户文档可通过以下命令定位；wheel 已携带部署文档和 Skill：

```powershell
& $mcpExe --docs-path
```

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

`--doctor` 可因跳过网络检查显示 `WARN`，但退出码必须为 0；`--doctor-network` 必须退出 0。`--list-tools --json` 会返回 retail 工具目录及其 schema，必须只包含 `retail_v1_preview` 的 10 个工具。输出中允许出现工具名称、schema、版本、脱敏配置路径和状态，但不得出现 token 原文、尾号或带凭据 URL 查询参数。

`--doctor-network` 会执行多项真实上游检查，可能消耗智兔请求额度；额度紧张时可先完成本地 `--doctor`、MCP 握手和工具列表验收，再由用户决定是否运行网络检查。

### 5. 配置 Host

使用对应 Host 模板，把其中的 `cn-stock-mcp` 命令替换为步骤 2 解析出的 `cn-stock-mcp.exe` 绝对路径；只写 `command`、`args`、必要的工作目录和工具白名单，不要加入 `ZHITU_TOKEN`。修改前备份原配置，保留原有字段和其他 MCP server。

- Codex：`docs/CODEX_TEMPLATE.md`
- Claude Code：`docs/CLAUDE_CODE_TEMPLATE.md`
- OpenClaw：`docs/OPENCLAW_HOST_TEMPLATE.md`
- Hermes Agent：`docs/HERMES_TEMPLATE.md`

### 6. 重载并首次问答

重载对应 Host，确认 server 已连接并看到 `retail_v1_preview` 的 10 个工具。Host 没有原生工具白名单时，以 server 端工具档的 10 个结果为准。使用以下固定问题：

> 查询平安银行最新行情，给出数据来源、数据时间、交易时段和数据质量；不要提供投资建议。

验收必须看到 symbol、数据来源（若上游未提供则明确标记 unknown）、freshness/as_of、session_context 或等价信息，并确认回答没有 token、下单指令、收益承诺或荐股结论。`data_quality` 只是数据可用性提示，不是投资置信度。

## 回滚

如果 Host 连接失败，先恢复刚才的配置备份，再运行 `--doctor --json`。不要删除用户配置文件；卸载只允许移除本项目虚拟环境，token 文件由用户自行保留或删除。

## Agent 禁止事项

- 禁止读取或回显 `%LOCALAPPDATA%\cn-stock-mcp\config.json` 的 token 字段。
- 禁止把 token 放入 Host JSON/TOML/YAML、PowerShell 历史、日志或截图。
- 禁止执行买卖、账户登录、券商连接或自动交易。
- 禁止以 `data_quality`、candidate score、risk tag 或技术指标作为投资建议。
