---
name: newsbot-stock-routing
description: Route news agent CN market requests to openclaw-stock-mcp tools. Use for China market briefings, hot-theme tracking, sector rotation, stock review, market pool, technical indicator, trading-day, and symbol lookup tasks. Do not use for general non-market news research.
user-invocable: false
metadata: {"openclaw":{"skillKey":"newsbot-stock-routing","requires":{"config":["mcp.servers.openclaw-stock-mcp"]}}}
---

# newsbot-stock-routing

Use this skill when the **news** agent receives CN market data or复盘类请求：A 股/指数/基金行情、市场简报、热点主线、板块强弱、板块轮动、龙头/跟风/拖累、交易日判断、技术指标、涨停跌停股池、代码检索。

Do **not** use this skill for一般宏观新闻、国际政治新闻、公司新闻核验等**不需要** `openclaw-stock-mcp` 数据工具的任务。

## Quick routing

- 市场整体 / 收盘简报 / 情绪温度 → `market_brief`
- 热点主线 / 次主线 / 风险主题 → `hot_theme_tracker`
- 单板块 / 行业 / 概念复盘 → `sector_review`
- 多板块横向比较 / 板块轮动 → `sector_rotation_review`
- 单股复盘 → `stock_review`
- 股票池批量对比 → `stock_review_batch`
- 候选扫描 / 找值得继续跟踪的票 → `stock_candidate_scan`
- 固定观察池 / 自选池持续跟踪 → `watchlist_review`
- 实时价格 / 涨跌快照 → `stock_quote`
- 历史走势 / K 线 / 分时 → `stock_history`
- 单只标的跨周期共振 / 冲突 → `multi_timeframe_review`
- MACD / MA / BOLL / KDJ → `technical_indicator`
- 涨停 / 跌停 / 强势 / 次新 / 炸板股池 → `market_pool`
- 是否交易日 / 上下个交易日 → `trading_calendar`
- 板块列表 / 板块成员 → `sector_lookup`
- 代码不确定 / 名称歧义 → `stock_search`
- 上游健康检查 → `provider_health`
- 宏观经济指标（CPI/PMI/GDP/LPR/M2等）→ `macro_indicator`
- 龙虎榜明细（游资/机构/营业部胜率）→ `dragon_tiger`
- ETF行情快照（IOPV折溢价/资金流/份额/净值）→ `etf_snapshot`
- 可转债（双低/溢价率/YTM/强赎监控）→ `convertible_bond`
- 期货/期权（期货实时+历史/期权合约/QVIX隐含波动率）→ `derivatives_data`

## Operating rules

- 代码或名称不确定时，**先 `stock_search`，再 quote/history/review**。
- 解释 `market_brief`、`sector_review`、`sector_rotation_review` 和 `hot_theme_tracker` 时，**优先使用统一公共字段 `review_envelope_v1`**。
- `sentiment.score` 是统一情绪温度分；`rotation.score` 是轮动信号分，**不能混用**。
- 若 `requested_trade_date != trade_date`，必须明确说明“已回退到有效交易日”。
- `sector_rotation_review` 当前优先用于 `primary` 板块的横向比较；若用户给的是单个板块，优先走 `sector_review`。
- `hot_theme_tracker` 当前适合快速回答“主线是谁 / 是否扩散 / 哪些方向在退潮”，不是单板块深度复盘的替代品。
- `sector_rotation_review` live 路径仍偏重；默认先用较小 `limit`（如 3~5），需要更大覆盖时再逐步放大。
- `market_brief` 里的 `overview / index_ranking / highlights / pools` 是**兼容补充字段**，不要把它们当成主契约。
- 当字段为 `null`、空数组，或 `applicable=false` 时，不要脑补结论。

## Read references when needed

- Envelope 字段与评分语义：`{baseDir}/references/review-envelope-v1.md`
- Tool 路由、参数和 provider 规则：`{baseDir}/references/tool-routing.md`
- 输出组织与失败处理：`{baseDir}/references/output-rules.md`
