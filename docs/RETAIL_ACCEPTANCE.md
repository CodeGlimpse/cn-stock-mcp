# 首发 retail 与 Codex 验收

版本 `0.2.3` 已正式发布，本页用于客户逐单验收。首发验收 Windows 11 x64、普通 CPython 3.13、Codex、retail 10 工具。研发本轮未执行真实行情查询或实际 Host 测试；客户验收结果另行记录。离线测试、MCP 客户端脚本与真实 Codex 客户端分别记录，不能互相代替。

## 1. 安装与协议检查

先按 [AI_DEPLOY_WINDOWS.md](AI_DEPLOY_WINDOWS.md) 验证 wheel 与依赖约束 SHA256，完成安装、`pip check`、`--version` 和本地 `--doctor`。安装包自带验收工具：

```powershell
$venv = Join-Path $env:LOCALAPPDATA "cn-stock-mcp\runtime\venv"
$python = Join-Path $venv "Scripts\python.exe"
$mcpExe = Join-Path $venv "Scripts\cn-stock-mcp.exe"
$docs = (& $mcpExe --docs-path).Trim()
$tools = Join-Path (Split-Path $docs -Parent) "tools"
$constraints = Join-Path (Split-Path $docs -Parent) "constraints-windows-py313.txt"
& $python (Join-Path $tools "verify_runtime_constraints.py") $constraints --installed
```

`verify_mcp_stdio.py` 检查 initialize、工具数量与 INVALID_ARGUMENT 错误响应，不访问行情，不能证明有效数据可用。单元测试中的成功响应使用固定样本，也不能充当真实数据证据。

## 2. 先展示真实查询计划

```powershell
$configPath = Join-Path $env:LOCALAPPDATA "cn-stock-mcp\config.json"
$acceptance = Join-Path $tools "verify_retail_acceptance.py"
& $python $acceptance --command $mcpExe --config $configPath --expected-version 0.2.3
```

不加 `--run-live` 时只输出计划，不启动服务、不读取配置、不访问上游。确认客户自己的 Token 已手动配置，并获得本次真实请求授权后才能执行下一节。

| 顺序 | 工具 | 样本与限制 |
| --- | --- | --- |
| 1 | trading_calendar | 最近 5 个交易日，取得真实查询日期与交易时段 |
| 2 | stock_search | 平安银行，最多 5 项 |
| 3 | stock_quote | 000001.SZ，一只股票 |
| 4 | stock_history | 000001.SZ，日线 5 条，AKShare |
| 5 | stock_snapshot | 一只股票，仅行情和 5 条日线，30 秒等待预算 |
| 6 | stock_review | 一只股票，使用步骤 1 的最近交易日 |
| 7 | watchlist_review | 一只股票，top_n=1 |
| 8 | market_brief | close 简报，top_n=3，不包含股池 |
| 9 | hot_theme_tracker | 自动取 2 个一级行业，每行业最多 2 个成员，不包含股池 |
| 10 | sector_review | 使用步骤 9 的一个真实行业名，最多 2 个成员 |

总共最多 10 次顺序 MCP 工具调用；任何非 PASS 结果停止后续调用，不自动重试。不暴露 full 档工具，也不预设行业名。单次 MCP 等待默认 60 秒；超时关闭本次子进程。第三方同步调用在取消前可能仍消耗请求。

## 3. 执行与保存报告

选择新的报告文件，不覆盖以往证据：

```powershell
$reports = Join-Path $env:LOCALAPPDATA "cn-stock-mcp\acceptance"
New-Item -ItemType Directory -Path $reports -Force | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$report = Join-Path $reports "retail-0.2.3-$stamp.json"
& $python $acceptance --command $mcpExe --config $configPath --expected-version 0.2.3 --report $report --zhitu-budget 60 --run-live
```

脚本只让 MCP 子进程读取指定 Token 配置，并在空临时目录启动以避开其他项目的 `.env`。报告只保存允许的来源名、时间、状态、记录数量、耗时和错误类别，不保存 Token、错误原文、URL、原始行情或评分。

`--zhitu-budget 60` 仅限制本次进程中每个 Token 的智兔配额计数；有多个 Token 时上限分别计算。它不是整个账户、AKShare 或所有 HTTP 请求的硬上限，也不等于实际计费数。MCP 复合工具、fallback 和底层重试可能发出多个请求；实际消耗以供应商后台为准。报告明确写 `upstream_request_count: not_measured`。

| 状态 | 退出码 | 含义与处理 |
| --- | --- | --- |
| PASS | 0 | 本轮限定样本和元数据完整；不证明全部市场、全部参数或 Codex 客户端已通过 |
| PARTIAL | 2 | 部分缺失、空数据、旧数据、来源或时间无法核验；保留报告，人工复核后决定补测 |
| FAIL | 1 | 协议、版本、工具集或数据契约不符；停止并定位 |
| BLOCKED | 3 | 配置/程序缺失、连接、Token、额度、上游或超时阻塞；记录未执行项，处理后另开一份报告 |

计划模式本身退出 0 只表示计划生成成功，其报告状态仍是 BLOCKED。周末、节假日的 `aged_data` 也会保守标成 PARTIAL；结合最近交易日、数据时间和交易时段人工核验，不把服务端观察时间当作行情时间。部分成功不是自动通过，不循环重试以凑够成功次数。

## 4. 真实 Codex 客户端记录

按 [CODEX_TEMPLATE.md](CODEX_TEMPLATE.md) 完成配置和问答，保存下表。脚本的 `host_acceptance` 永远是 `NOT_RUN`，需要单独完成本项。

| 字段 | 实际验收记录 |
| --- | --- |
| 日期、验收人员、交付编号 | `[填写；不录入账户秘密]` |
| Windows / Python 版本、是否标准用户 | `[填写]` |
| 软件版本、wheel SHA256 | `[填写]` |
| Codex 客户端 | `[桌面 / CLI / IDE 扩展，填写实际版本]` |
| 配置备份与恢复验证 | `[本机记录，不上传完整配置]` |
| server 连接、10 工具列表 | `[PASS / FAIL / BLOCKED，附脱敏依据]` |
| 实际调用 | `[trading_calendar、stock_quote 的调用与结果]` |
| 回答核对 | `[symbol、来源、as_of、时段、fallback、partial_failure、data_quality、免责声明]` |
| retail 报告 | `[报告文件名、状态及未完成项]` |
| 升级/回滚 | `[约定版本安装与配置恢复结果]` |
| 最终结论 | `[通过 / 待补测 / 未通过，确认人员与时间]` |

只写“Codex 已配置”或粘贴模型自称成功不足以验收；必须看到实际工具调用和数据。不得把本机 CLI 版本推断成桌面或 IDE 扩展版本。
