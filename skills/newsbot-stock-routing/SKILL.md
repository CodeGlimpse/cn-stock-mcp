---
name: newsbot-stock-routing
description: Route news agent CN market requests to cn-stock-mcp tools. Use for China market briefings, hot-theme tracking, sector rotation, stock review, market pool, technical indicator, trading-day, and symbol lookup tasks. Do not use for general non-market news research.
user-invocable: false
metadata: {"openclaw":{"skillKey":"newsbot-stock-routing","requires":{"config":["mcp.servers.cn-stock-mcp"]}}}
---

# newsbot-stock-routing

Use this skill when the **news** agent receives CN market data / 复盘类请求：A 股、指数、基金、市场简报、热点主线、板块强弱、板块轮动、龙头跟风拖累、交易日判断、技术指标、涨停跌停股池、代码检索。

Do **not** use this skill for 一般宏观新闻、国际政治新闻、公司新闻核验等**不需要** `cn-stock-mcp` 数据工具的任务。

## Token-saving default

先用最轻 tool，先用最小 payload，够回答就停：

- 默认 `limit/top_n` 先用 `3~5`
- 名称/代码不确定先 `stock_search`
- 常规回答不要先跑 `provider_health`
- 单板块优先 `sector_review`；多板块比较才用 `sector_rotation_review`
- 轻量池子快照优先 `market_pool`；更深短线情绪/历史结构再用 `limit_up_pool`

## High-frequency routing

先读：`{baseDir}/references/quick-routing-core.md`

它只覆盖高频场景，足够回答大部分市场简报 / 复盘问题。

## Hard rules

- The default `retail_v1_preview` profile exposes only `stock_search`, `market_brief`, `stock_snapshot`, `stock_quote`, `stock_history`, `stock_review`, `watchlist_review`, `trading_calendar`, `sector_review`, and `hot_theme_tracker`. Before routing to another tool, confirm that the user enabled `tool_profile=full`; never loop on `TOOL_NOT_FOUND`.
- `sector_lookup(mode=children|members)` **必须显式传** `sector_type=primary|concept`
- `sector_lookup(children)` 表示**成员股**，不是子板块
- 若 `requested_trade_date != trade_date`，必须说明已回退到有效交易日
- `rotation.score` 是轮动/结构信号分，**不是** 情绪温度分
- 遇到 `null` / `[]` / `applicable=false`，不要脑补结论
- 输出必须标注数据来源、时间/新鲜度，以及 fallback、partial failure 或 unknown；`data_quality` 不是投资置信度。
- 固定边界：只提供数据参考，不提供投资建议、荐股、买卖指令、收益承诺或个性化风险建议。

## Read references only when needed

- 高频最短路由：`{baseDir}/references/quick-routing-core.md`
- 高频/常规工具的详细参数与 provider 路由：`{baseDir}/references/tool-routing.md`
- 长尾工具（宏观、龙虎榜、ETF、可转债、期货/期权等）：`{baseDir}/references/tool-routing-extended.md`
- 需要 payload 示例时：`{baseDir}/references/tool-examples.md`
- 统一 envelope 字段与评分语义：`{baseDir}/references/review-envelope-v1.md`
- 输出组织、失败处理、表达优先级：`{baseDir}/references/output-rules.md`
