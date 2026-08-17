# Implementation Status (`cn-stock-mcp`)

Last Updated: 2026-08-17

这页是当前项目状态的**事实源**。如果 README、handoff、历史讨论与本页不一致，以本页为准。

当前目标公开版本：`0.2.0`。PyPI 与 GitHub Release 尚需完成远端发布；Windows AI 自部署流程见 `AI_DEPLOY_WINDOWS.md`。

---

## 1) 项目定位

`cn-stock-mcp` 的核心交付物是：
- **一个通用 MCP server**

仓库内另外附带：
- 面向多种 AI agent / MCP host 的接入文档与配置模板
- 一个 OpenClaw skill adapter（不是跨平台通用 skill 标准）

---

## 2) 当前已经具备的交付能力

### 安装与命令入口
项目现在已经具备真正的 console script，可直接运行：

```bash
cn-stock-mcp --stdio
cn-stock-mcp --version
cn-stock-mcp --doctor
cn-stock-mcp --doctor --json
cn-stock-mcp --doctor-network
cn-stock-mcp --doctor-network --json
cn-stock-mcp --list-tools
cn-stock-mcp --list-tools --json
cn-stock-mcp --describe-tool stock_quote
cn-stock-mcp --tool provider_health --payload '{}'
cn-stock-mcp --init-config
```

### 自检能力
当前 doctor 分为两层：

- `--doctor`
  - 本地基础检查
  - 不默认联网
  - 对本地源码环境缺 PATH 命令等情况返回 `WARN` 而不是误报 `FAIL`

- `--doctor-network`
  - 在本地基础检查之外
  - 额外验证 token / provider / 上游连通性

两种 doctor 都支持 `--json`，输出包含 `result`、`exit_code` 和逐项 `checks`，适合脚本或宿主集成读取；token 配置文件缺失、格式错误或不可读时只报告脱敏 WARN，不输出 token 内容。

### 打包与发布物
当前已经完成：
- wheel / sdist 构建
- console script 写入 `entry_points.txt`
- `MANIFEST.in` 控制发布内容
- sdist / wheel 不再携带 `tests/` 与 `.github/`
- 默认 token 配置路径为每用户 `%LOCALAPPDATA%\\cn-stock-mcp\\config.json`
- `retail_v1_preview` 工具档包含 10 个高层工具；`full` 保持全量兼容

### 文档与交付层
当前已具备：
- 人类入口：`docs/START_HERE.md`
- 一页接入：`docs/HANDOFF_MINIMAL.md`
- FAQ：`docs/FAQ.md`
- host 模板总入口：`docs/HOST_CONFIG_TEMPLATES.md`
- host-specific 模板：OpenClaw / Claude Desktop / Claude Code / Continue / VS Code / Cursor / Cline / Windsurf / Hermes / Codex
- Windows AI 部署与首次问答验收合同：`docs/AI_DEPLOY_WINDOWS.md`
- 对外边界：`docs/SECURITY.md` / `docs/PRIVACY.md` / `docs/DATA_SOURCES.md` / `docs/SUPPORT.md`
- AI 集成说明：`docs/AI_ONBOARDING.md`
- AI 最小规则：`docs/AGENT_MINIMAL.md`
- agent / skill 对照：`docs/AGENT_AND_SKILL_MAP.md`
- 接口契约与错误模型同步维护成功响应的 `meta.freshness` 数据新鲜度信息及 provider/cache 可观测字段

---

## 3) 当前测试与 CI 状态

### 已验证（截至上一轮，历史基线）
- 非 live 回归：`511 passed, 22 deselected`
- CLI 相关轻量测试已降耦，不再依赖真实网络 `doctor-network` 子进程
- `market_pool` 显式日期缓存命中不再先访问交易日历上游
- fallback 不再吞掉未预期的编程异常或结果策略异常
- `python -m build` 的 CI 失败根因已修复：`build` 已加入 `dev` 依赖
- Windows 本地使用 `python -m build --no-isolation` 可正常生成 wheel/sdist

### CI
当前保留：
- `.github/workflows/ci.yml`
- `.github/workflows/live-smoke.yml`

说明：
- `CI` 用于构建、非 live 测试、wheel 安装 smoke、CLI smoke，并覆盖 Python 3.11/3.12/3.13
- `windows-smoke` 使用普通 CPython 3.13 验证缓存、fallback、transport、doctor、构建和 CLI
- `Live Smoke` 当前已经收缩为 **manual only** 的诊断 workflow

### Live Smoke 当前定位
当前将 `Live Smoke` 视作：
- **手动诊断 / 上游连通性验证 workflow**

而不是基础质量门禁或定时巡检任务。

### P2 实时数据与兼容性验证（历史记录，仍未覆盖本轮新配置和免责声明）

2026-08-13 在 Windows 普通 CPython 3.13.2 项目虚拟环境中完成：

- 实时 smoke：13/13 通过
- extended live：3/3 通过
- Zhitu 市场池日期格式兼容：3/3 通过，支持 `YYYY-MM-DD` 与 `YYYYMMDD`
- MCP stdio 进程级验证：initialize 成功、当时 52 个工具、无效参数返回 `INVALID_ARGUMENT`
- `--doctor-network`：`provider_health` 通过
- `pip check`：通过
- 完整非 live 回归：472 通过，16 个 live 用例排除
- Provider 复用后首次 `create_server()` 约 0.33 秒，后续约 0.06 秒

详细命令、环境和限制见 `docs/P2_DELIVERY_RECORD_2026-08-13.md`。

### P2 接口文档与数据新鲜度

2026-08-14 已完成：

- `docs/INTERFACE_SCHEMA.md` 与当时实际 52 个注册 tool 对齐
- `docs/ERROR_MODEL.md` 增加 `meta.freshness` 成功响应契约
- MCP 成功响应统一提供 `observed_at/as_of/basis/status/age_seconds`
- 无法从业务 payload 识别源时间时返回 `status=unknown`，不伪造数据产生时间

交付记录见 `docs/P2_DELIVERY_RECORD_2026-08-14.md`。

### P1 稳定性与使用体验

2026-08-15 已完成：

- 统一响应层将 provider、fallback、耗时等稳定可观测字段提升到顶层 `meta`，同时保留 `data.meta` 兼容旧调用方
- freshness 支持 `source_as_of`、`source_timestamp`、`source_date` 显式 hint，优先于通用字段扫描
- doctor 支持机器可读的 `--doctor --json` / `--doctor-network --json`，并区分 token 配置缺失、格式错误、结构错误和不可读状态
- AKShare 资金流 endpoint 增加进程内熔断、统一 proxy/环境代理配置、空结果失败处理和板块 endpoint fallback
- `capital_flow` 增加新鲜缓存、显式 `allow_stale` stale-if-error；默认不返回旧缓存，stale 结果带 `stale` 与 `stale_age_seconds`

### P2 功能添加

2026-08-15 已完成（本轮不包含本地持久化观察列表）：

- `trading_calendar` 点查询增加 `session_context`，区分交易日、开盘前、上午交易、午休、下午交易、收盘后和历史日期，并提供最近有效行情日期及收盘数据提示
- 新增受控 `stock_snapshot`，最多 5 个标的、历史最多 60 根、总超时预算最多 60 秒（默认 30 秒），组合行情/历史/财务/估值/事件/风险，不涉及交易执行
- 所有成功工具响应增加 `meta.data_quality`（`data_quality_v1`），解释 fallback、partial failure、年龄、缺失字段、异常值和空结果
- 新增 registry 驱动的 `docs/TOOL_CATALOG.md`，并提供 `--list-tools --json` 与 `--describe-tool`

---

## 4) 当前可用工具（MCP tools）

当前工具注册总数：**53**

工具包括：
- `stock_search`
- `stock_quote`
- `stock_snapshot`
- `stock_history`
- `stock_review`
- `stock_review_batch`
- `trading_calendar`
- `market_overview`
- `technical_indicator`
- `market_pool`
- `stock_orderbook`
- `sector_lookup`
- `provider_health`
- `sector_rotation_review`
- `stock_candidate_scan`
- `watchlist_review`
- `multi_timeframe_review`
- `hot_theme_tracker`
- `stock_profile`
- `sector_review`
- `sector_leaders`
- `market_brief`
- `event_calendar`
- `capital_flow`
- `stock_financial`
- `limit_stat`
- `northbound`
- `valuation_rank`
- `index_compose`
- `index_enhance`
- `industry_valuation_rank`
- `earnings_quality`
- `macro_indicator`
- `dragon_tiger`
- `etf_snapshot`
- `convertible_bond`
- `derivatives_data`
- `margin_trading`
- `block_trade`
- `institute_hold`
- `money_rate`
- `stock_screen`
- `insider_trade`
- `dividend_rank`
- `shareholder_change`
- `disclosure_calendar`
- `stock_repurchase`
- `stock_compare`
- `industry_chain`
- `stock_warrant`
- `fund_flow`
- `limit_up_pool`
- `sec_reveal`

> 具体参数、输入/输出契约、字段说明，请看：`docs/INTERFACE_SCHEMA.md`

---

## 5) 当前 AI / Host / Skill 分层

### 大多数 AI agent / host
使用方式是：
- 直接把 `cn-stock-mcp` 当作 **MCP server** 接入
- 不需要仓库内专属 skill 文件

已提供模板的宿主包括：
- OpenClaw
- Claude Desktop
- Claude Code
- Continue
- VS Code
- Cursor
- Cline
- Windsurf
- Hermes
- Codex

### 当前仓库内真正附带的 skill
主要是：
- `skills/newsbot-stock-routing/SKILL.md`

它是：
- OpenClaw / news agent 的 skill adapter
- 不是所有平台通用的 skill 标准

---

## 6) 当前已知设计约束

### `sector_lookup`
这是当前最容易踩坑的接口之一：
- `mode=children|members` 表示**成员股列表**，不是子板块
- `mode=children|members` 时，**必须显式传 `sector_type=primary|concept`**

### `provider_health`
不建议在正常业务回答前默认调用：
- 会增加延迟
- 会消耗上游请求
- 更适合诊断场景

### 资金流缓存与 endpoint 熔断

- `capital_flow.allow_stale` 默认是 `false`；只有调用方显式允许时才可能返回标记清晰的旧缓存
- `PROVIDER_CIRCUIT_OPEN` 表示单个不稳定 endpoint 被进程内熔断，不是 token 鉴权错误；等待恢复窗口后会自动尝试半开恢复
- 熔断状态是进程内状态，重启 MCP server 后会清空，不提供跨进程共享或持久化
- `provider_proxy_url` 可为 provider 请求指定代理；`provider_trust_env=true` 时允许读取环境代理，默认关闭以避免隐式代理差异

### Windows Python 运行时

- 已验证：普通 CPython 3.13.2，`cp313-win_amd64`。
- 当前不把 Python 3.13t/free-threaded 作为 Windows/MCP 开发环境；`pywin32` 尚无可用的 `cp313t` wheel。
- Windows 同时安装两个构建时，应使用 `py -3.13` 或项目 `.venv`，不要使用默认 `py` / `py -3`。

### Provider 初始化性能

- `ProviderRouter` 在进程内共享 AKShare/Zhitu Provider，避免每个 UseCase 重复创建 Zhitu HTTP client。
- 该优化只改变实例生命周期，不改变 Provider 路由、token 轮换或 fallback 契约。
- 共享 Provider 已通过完整非 live、MCP transport 和实时 smoke 回归。

### 大 payload / 大 universe
当前所有 AI 使用建议都默认：
- 先用轻工具
- 先用小参数
- 只有用户明确要求更大覆盖时再放大

---

## 7) 当前仍可继续优化，但不阻塞交付

以下事项仍值得继续做，但它们不是“当前不能交付”的阻塞项：

1. 决定 `Live Smoke` 是否长期保留为 schedule，或进一步收缩为 manual only
2. 对重点宿主做一轮真机 smoke（例如 Claude Desktop / Cursor / Cline / OpenClaw）
3. 继续保持 `AI_ONBOARDING.md`、`AGENT_MINIMAL.md`、`.agent-hints.json` 的一致性

---

## 8) 当前状态结论

截至 2026-08-13，本项目已经不再只是“开发中代码仓库”，而是已经具备：
- 安装
- 自检
- 打包
- host 接入
- 人类友好文档
- AI 集成说明
- 多宿主配置模板
- 基础 CI 验证

当前最适合的定位是：

> **一个可交付给最终用户 / AI 集成人员试装、试接、试用的中国证券市场 MCP server 项目。**
