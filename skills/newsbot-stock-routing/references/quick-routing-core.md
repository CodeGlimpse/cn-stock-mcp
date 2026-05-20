# Quick routing core

只保留高频 CN 市场请求的最短路由。

## 高频意图 → tool

- 市场整体 / 收盘简报 / 情绪温度 → `market_brief`
- 热点主线 / 次主线 / 风险主题 → `hot_theme_tracker`
- 单板块 / 行业 / 概念复盘 → `sector_review`
- 多板块横向比较 / 板块轮动 → `sector_rotation_review`
- 单股复盘 → `stock_review`
- 股票池批量对比 → `stock_review_batch`
- 候选扫描 → `stock_candidate_scan`
- 自选池 / 固定观察池 → `watchlist_review`
- 实时价格 / 涨跌快照 → `stock_quote`
- 历史走势 / K 线 / 分时 → `stock_history`
- 多周期共振 / 冲突 → `multi_timeframe_review`
- 技术指标 → `technical_indicator`
- 涨停/跌停/强势/次新/炸板快照 → `market_pool`
- 深度短线情绪 / 连板结构 → `limit_up_pool`
- 是否交易日 / 上下个交易日 → `trading_calendar`
- 板块列表 / 板块成员 → `sector_lookup`
- 代码不确定 / 名称歧义 → `stock_search`
- 上游健康检查 → `provider_health`

## 高频硬规则

1. 代码或名称不确定时，先 `stock_search`，再 quote/history/review。
2. `sector_lookup(mode=children|members)` 必须显式传 `sector_type=primary|concept`。
3. 单板块优先 `sector_review`；多板块比较才用 `sector_rotation_review`。
4. 只要轻量池子快照，优先 `market_pool`；需要更深短线情绪和历史分析再用 `limit_up_pool`。
5. 常规回答不要先跑 `provider_health`；只在异常诊断时使用。
6. 优先小 payload：`limit/top_n` 先用 3~5，需要更多再放大。

## 何时再读其他 references

- 需要详细参数/路由约束 → `tool-routing.md`
- 需要统一 envelope 字段语义 → `review-envelope-v1.md`
- 需要输出组织与错误处理 → `output-rules.md`
