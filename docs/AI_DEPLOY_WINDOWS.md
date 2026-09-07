# Windows AI 部署与首次问答验收

> 适用版本：cn-stock-mcp 0.2.3。安装前核对同版本 PyPI、GitHub Release 与校验文件；缺失时停止，不改装 main。实际公开状态以发布平台为准。

本文件是给客户 Agent 的部署合同。Agent 必须按固定版本执行，遇到系统安装、网络、Host 配置覆盖或权限问题时先说明并请求用户确认；不得读取、打印、上传或写入 Zhitu token。

## 目标版本与安全边界

- 当前固定版本：`cn-stock-mcp==0.2.3`
- 运行方式：本机 stdio MCP server
- 默认配置文件：`%LOCALAPPDATA%\cn-stock-mcp\config.json`
- 首选工具档：`retail_v1_preview`
- Windows 配置指南覆盖 [13 款软件](HOST_CONFIG_TEMPLATES.md)；按实际客户端选择专页，首发合同的 Host 范围仍以交付约定为准。
- 该项目只查询公开市场数据，不连接券商、不保存交易账户、不下单。

不要把 token 写入 MCP Host 配置、Git 仓库、命令行参数、聊天记录或诊断包。

## Agent 执行流程

### 1. 预检

确认 Windows x64、Python 3.13（普通 CPython，不是 free-threaded 版本）和网络可用。项目代码兼容 Python 3.11–3.13，但本首发 Windows 自动部署合同固定验收 3.13；若没有受支持的 Python，先向用户说明将进行用户级安装，再执行官方 Python 安装流程；不要修改系统 PATH 或全局执行策略。

### 2. 固定版本安装

```powershell
$ErrorActionPreference = "Stop"
$root = Join-Path $env:LOCALAPPDATA "cn-stock-mcp"
$venv = Join-Path $root "runtime\venv"
$download = Join-Path $root "downloads\0.2.3"
New-Item -ItemType Directory -Force -Path $download | Out-Null

py -3.13 -m venv $venv
if ($LASTEXITCODE -ne 0) { throw "venv creation failed" }
$python = Join-Path $venv "Scripts\python.exe"
& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip setup failed" }
& $python -m pip download --only-binary=:all: --no-deps --dest $download cn-stock-mcp==0.2.3
if ($LASTEXITCODE -ne 0) { throw "fixed wheel download failed" }

$wheel = Get-ChildItem -LiteralPath $download -Filter "cn_stock_mcp-0.2.3-*.whl" | Select-Object -First 1
if (-not $wheel) { throw "v0.2.3 wheel was not found" }
$checksums = Join-Path $download "sha256sums.txt"
Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/CodeGlimpse/cn-stock-mcp/releases/download/v0.2.3/sha256sums.txt" -OutFile $checksums
$constraints = Join-Path $download "constraints-windows-py313.txt"
Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/CodeGlimpse/cn-stock-mcp/releases/download/v0.2.3/constraints-windows-py313.txt" -OutFile $constraints
$line = Get-Content -LiteralPath $checksums | Where-Object { $_ -match [regex]::Escape($wheel.Name) } | Select-Object -First 1
if (-not $line) { throw "v0.2.3 checksum entry was not found" }
$expected = ($line -split '\s+')[0].ToLowerInvariant()
$actual = (Get-FileHash -LiteralPath $wheel.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw "cn-stock-mcp wheel SHA256 mismatch" }
$constraintLine = Get-Content -LiteralPath $checksums | Where-Object { $_ -match [regex]::Escape([IO.Path]::GetFileName($constraints)) } | Select-Object -First 1
if (-not $constraintLine) { throw "runtime dependency constraints checksum entry was not found" }
$constraintExpected = ($constraintLine -split '\s+')[0].ToLowerInvariant()
$constraintActual = (Get-FileHash -LiteralPath $constraints -Algorithm SHA256).Hash.ToLowerInvariant()
if ($constraintActual -ne $constraintExpected) { throw "runtime dependency constraints SHA256 mismatch" }

# The constraints file pins the tested Windows CPython 3.13 runtime closure;
# it prevents a future PyPI dependency release from silently changing the
# customer's installation.
& $python -m pip install -c $constraints $wheel.FullName
if ($LASTEXITCODE -ne 0) { throw "constrained wheel installation failed" }
& $python -m pip check
if ($LASTEXITCODE -ne 0) { throw "runtime dependency check failed" }
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

### 4. 本地检查与经授权的真实验收

```powershell
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe" --version
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe" --doctor --json
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe" --list-tools --json
```

`--doctor` 可因跳过网络检查显示 `WARN`，但退出码必须为 0。`--list-tools --json` 会返回 retail 工具目录及其 schema，必须只包含 `retail_v1_preview` 的 10 个工具。输出中允许出现工具名称、schema、版本、脱敏配置路径和状态，但不得出现 token 原文、尾号或带凭据 URL 查询参数。

真实数据验收按 [RETAIL_ACCEPTANCE.md](RETAIL_ACCEPTANCE.md) 先输出计划，获得 Token 使用与网络请求授权后运行限定的 10 工具样本。该脚本和可选的 --doctor-network 都会消耗上游请求；不要默认同时执行。遇到非 PASS 结果停止，保存脱敏报告并处理未完成项。

### 5. 配置 Host

先看 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，再从 [13 款配置总表](HOST_CONFIG_TEMPLATES.md) 选择实际软件。按该客户端专页的格式填写程序绝对路径与 `--stdio`；OpenCode 的命令数组、VS Code 的 `servers` 等结构不能与其他模板混用。

修改前备份并合并配置，保留其他字段。环境变量只放配置路径、工具档及编码选项；Token 仍由客户本人保管在 MCP 配置文件中。

### 6. 客户按需重载与首次问答

本轮配置指南整理按用户要求不执行真实测试。以下是客户需要实际验证时使用的步骤。

按所选软件专页重载，记录实际客户端类型与版本，查看本服务器的 `retail_v1_preview` 10 工具。需要行情查询时再使用以下问题，并分别记录连接与查询结果：

> 查询平安银行最新行情，给出数据来源、数据时间、交易时段和数据质量；不要提供投资建议。

验收必须看到 symbol、数据来源（若上游未提供则明确标记 unknown）、freshness/as_of、session_context 或等价信息，并确认回答没有 token、下单指令、收益承诺或荐股结论。`data_quality` 只是数据可用性提示，不是投资置信度。

## 回滚

如果 Host 连接失败，先恢复刚才的配置备份，再运行 `--doctor --json`。不要删除用户配置文件；卸载只允许移除本项目虚拟环境，token 文件由用户自行保留或删除。

## Agent 禁止事项

- 禁止读取或回显 `%LOCALAPPDATA%\cn-stock-mcp\config.json` 的 token 字段。
- 禁止把 token 放入 Host JSON/TOML/YAML、PowerShell 历史、日志或截图。
- 禁止执行买卖、账户登录、券商连接或自动交易。
- 禁止以 `data_quality`、candidate score、risk tag 或技术指标作为投资建议。
