# Codex 接入模板

首发只验收 **Codex + Windows 11 x64 + 普通 CPython 3.13 + 本地 stdio**。需要记录实际使用的 Codex 客户端类型和版本；这份模板本身不代表客户端已经验收。其他 Host 的模板继续保留，首发不作兼容承诺。

依据：[Codex 官方 MCP 文档](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)，核对日期 2026-09-06。Codex 支持用户级 `~/.codex/config.toml` 和受信任项目中的 `.codex/config.toml`；同一 Host 的本地客户端共用 MCP 配置。配置以实际 Codex 版本支持的字段为准。

## 1. 先完成本地安装

按 [AI_DEPLOY_WINDOWS.md](AI_DEPLOY_WINDOWS.md) 核对固定版本、wheel 与依赖约束文件的 SHA256。由最终用户执行 `--init-config`，手动填写 `%LOCALAPPDATA%\cn-stock-mcp\config.json`。Token 不进入 Codex 配置、环境变量、命令行或聊天。

记录实际路径，避免依赖系统 PATH：

```powershell
$runtime = Join-Path $env:LOCALAPPDATA "cn-stock-mcp\runtime\venv"
$mcpExe = Join-Path $runtime "Scripts\cn-stock-mcp.exe"
& $mcpExe --version
& $mcpExe --doctor --json
& $mcpExe --list-tools --json
```

## 2. 添加 Codex 配置

先确认要修改的配置文件，备份原文件，并保留其他 MCP server 与原有字段。以下两种方式任选一种，使用相同 server 名 `cn_stock_mcp`，避免重复注册。

CLI 方式（在已有 Codex CLI 的终端中运行）：

```powershell
codex mcp add cn_stock_mcp -- $mcpExe --stdio
```

需要工作目录、超时和工具白名单时，在已确认的配置中合并下面的 TOML。将两个路径替换为本机实际绝对路径；TOML 不会展开环境变量。

```toml
[mcp_servers.cn_stock_mcp]
command = 'C:\Users\YOUR_NAME\AppData\Local\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe'
args = ["--stdio"]
cwd = 'C:\Users\YOUR_NAME\AppData\Local\cn-stock-mcp\runtime'
startup_timeout_sec = 30
tool_timeout_sec = 60
enabled_tools = ["stock_search", "market_brief", "stock_snapshot", "stock_quote", "stock_history", "stock_review", "watchlist_review", "trading_calendar", "sector_review", "hot_theme_tracker"]
```

工作目录应是部署创建的运行目录，避免从含有其他项目 .env 的目录启动。服务器配置应使用 retail_v1_preview；Codex 白名单是额外限制，不能代替服务器端工具档。若改用项目级配置，必须是客户明确授权的受信任项目。

## 3. 在真实 Codex 客户端验收

重载连接；CLI 可用 `codex mcp list`，TUI 可用 `/mcp` 检查连接。仅显示“已配置”不足以证明工具调用成功。

在客户实际使用的 Codex 客户端发送：

> 先查询中国市场最近交易日和当前交易时段，再查询 000001.SZ 的最新行情。说明实际调用的工具、数据来源、数据时间、fallback、partial failure 和 data_quality；数据未知时明确写 unknown，不提供投资建议。

核对工具调用记录与最终回答。若上游失败，保留脱敏错误类别和未完成项，不记录为通过。随后按 [RETAIL_ACCEPTANCE.md](RETAIL_ACCEPTANCE.md) 保存客户端类型、版本、连接结果、实际调用和人工核对记录。

脚本执行的 MCP stdio 验收不代替这一步；CLI、桌面和 IDE 扩展也不能相互代替具体客户端的验收记录。

## 4. 常见问题

- 找不到程序：核对 command 的绝对路径及运行账号。
- 出现 JSON-RPC 解析错误：必须带 --stdio；直接运行可执行文件会输出普通就绪文字。
- 工具数量错误：先核对服务端 retail_v1_preview，再检查重复注册、白名单和客户端重载状态。
- 启动超时：检查本地 --doctor；不要以无限增大超时掩盖安装或网络问题。
- 配置读取失败：按备份恢复本次修改的条目，再定位 TOML 语法、权限和受信任项目设置。

排障时不发送 Token 文件、完整 Codex 配置或未脱敏日志。更多说明见 [CUSTOMER_DEPLOYMENT.md](CUSTOMER_DEPLOYMENT.md)。
