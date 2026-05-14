# Interface Schema (`openclaw-stock-mcp`)

Last Updated: 2026-05-09

> 本文是当前对外契约（输入/输出与关键约束）。
> 若与历史文档冲突，以本文与代码实现为准。

---

## 1. Tool 列表（当前）

- stock_search
- stock_quote
- stock_history
- stock_review
- stock_review_batch
- watchlist_review
- trading_calendar
- market_overview
- market_brief
- technical_indicator
- multi_timeframe_review
- market_pool
- stock_orderbook
- stock_candidate_scan
- stock_profile
- sector_quote
- sector_lookup
- sector_review
- sector_rotation_review
- sector_leaders
- hot_theme_tracker
- provider_health
- event_calendar
- capital_flow
- stock_financial
- limit_stat
- northbound
- valuation_rank
- index_compose
- industry_valuation_rank
- earnings_quality
- macro_indicator
- dragon_tiger
- etf_snapshot
- convertible_bond
- derivatives_data
- margin_trading

---

## 2. 通用约束

### market
- 默认/当前：`CN`

### sec_type
- `stock | index | fund | sector`

### interval（对外）
- `5m | 15m | 30m | 60m | 1d | 1w | 1M | 1y`
- 输入别名兼容：`5/15/30/60/d/w/m/y`
- `1m` 当前不支持（避免与 `1M` 混淆）

### adjust
- `none | qfq | hfq`

### indicator
- `macd | ma | boll | kdj`

### pool_type
- `limit_up | limit_down | strong | sub_new | broken_limit`
- 输入别名兼容：
  - `ztgc | up | 涨停 -> limit_up`
  - `dtgc | down | 跌停 -> limit_down`
  - `qsgc | 强势 -> strong`
  - `cxgc | 次新 -> sub_new`
  - `zbgc | 炸板 -> broken_limit`

### symbol
- 推荐 canonical：`000001.SZ`、`600519.SH`、`899050.BJ` 等。
- 输出中的 `symbol` 应为标准化结果。

---

## 3. 响应 envelope（统一）

成功：
```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": {
    "schema_version": "v1",
    "request_id": "req_xxx",
    "tool": "stock_quote"
  }
}
```

失败：
```json
{
  "success": false,
  "data": null,
  "error": {
    "error_code": "INVALID_ARGUMENT",
    "message": "Invalid request payload",
    "retryable": false,
    "provider": null
  },
  "meta": {
    "schema_version": "v1",
    "request_id": "req_xxx",
    "tool": "stock_quote"
  }
}
```

错误码详见 `ERROR_MODEL.md`。

---

## 4. Provider 路由（当前策略）

- trading_calendar / stock_review：`akshare`
- stock_search：`akshare` 主，`zhitu` 备
- market_overview：`mixed`
- sector_lookup：`zhitu`
- stock_history：
  - stock：`zhitu` 主，`akshare` 备
  - index：`zhitu` 主，`akshare` 备
- technical_indicator：
  - stock：`zhitu` 主，`akshare` 备
  - index：`zhitu` 主，`akshare` 备
  - fund：`zhitu`
- market_pool / stock_orderbook / stock_profile：`zhitu`
- capital_flow / stock_financial / limit_stat / northbound / index_compose：`akshare`
- earnings_quality：`akshare`（复用 `stock_financial` 快照）
- macro_indicator：`akshare`
- dragon_tiger：`akshare`
- etf_snapshot：`akshare`
- convertible_bond：`akshare`
- derivatives_data：`akshare`
- margin_trading：`akshare`
- valuation_rank：市场估值快照使用 `akshare`；个股估值字段复用 `stock_quote`（`zhitu` 主，`akshare` 备）
- industry_valuation_rank：行业成员股来自 `sector_lookup(children, primary)`（`zhitu`），成员估值字段复用 `stock_quote`（`zhitu` 主，`akshare` 备）
- stock_quote：
  - stock-main：`zhitu` 主，`akshare` 备（批量请求使用 `/hs/public/ssjymore`，最多 20 支）
  - stock-bj：`zhitu` 主，`akshare` 备（AKShare 走 `stock_bj_a_spot_em()`，10s TTL 缓存）
  - index/fund：`zhitu` 主，`akshare` 备
  - stock-star：`zhitu`
- hot_theme_tracker：当前通过上层聚合复用 `sector_rotation_review + market_pool`

> `stock_orderbook` 当前已支持：
> - 沪深主板：`/hs/real/five/{code}`
> - 科创板：`/tech/real/mmwp/{code}`
> - 北交所：`/bj/stock/real/mmwp/{code}`

> 实际回退行为由实现与实时可用性决定。

---

## 5. 复盘类工具的关键输出约定（摘要）

- `stock_review`：单股复盘摘要（latest_bar/stats/benchmark/windows/summary）
- `stock_review_batch`：批量排序与分组（items/rankings/groups/summary）
- `sector_quote`：板块指数实时行情（支持 `sector_type=primary` 和 `sector_type=concept`）
- `sector_review`：板块成员聚合（breadth/stats/sentiment/rotation/structure/rankings/buckets）；支持 `sector_type=primary`（一级行业）和 `sector_type=concept`（概念题材）
- `stock_profile`：公司基本面（profile/dividends/unlocks/quarter_profits/valuation/dividend_summary/unlock_risk）
- `sector_rotation_review`：跨板块比较（rankings/buckets/rotation）
- `capital_flow`：资金流向（market/individual/industry/concept）
- `stock_financial`：财务数据三层视图（snapshot/history/details）
- `limit_stat`：短线情绪统计（封板率/连板分布/炸板/昨涨停今继续率；返回 `partial_failure` + `errors` 标记跌停数据获取失败）
- `northbound`：北向资金（当日流向/历史/持股排行）
- `valuation_rank`：估值排名（市场估值温度 + 个股 PE/PB 排名）
- `index_compose`：指数成分与权重（支持集中度统计；返回 `used_fallback_endpoint` + `endpoint_note` 标记权重接口降级）
- `industry_valuation_rank`：一级行业估值分位（成员股 PE/PB 聚合后横向排序）
- `earnings_quality`：盈利质量评估（扣非占比/增速一致性/现金转化/ROE/杠杆综合评分）
- `macro_indicator`：宏观经济指标（CPI/PPI/PMI/GDP/LPR/M2等，支持cn/usa/euro/global，latest/history/calendar/overview四种模式）
- `dragon_tiger`：龙虎榜明细（日榜明细/机构买卖/活跃营业部/营业部胜率排行/个股上榜统计）
- `etf_snapshot`：ETF行情快照（全市场实时行情+IOPV折溢价+资金流+份额+净值）
- `convertible_bond`：可转债数据（集思录快照/双低/溢价率/YTM/强赎监控/等权指数）
- `derivatives_data`：期货/期权数据（期货实时+历史/期权合约列表/QVIX隐含波动率）
- `margin_trading`：融资融券数据（两市汇总+个股明细，支持融资买入/融券卖出排序；返回 `partial_failure` + `errors` 标记部分交易所获取失败）

补充（可观测性字段，已在关键工具 meta 中统一输出）：
- `provider_used`：本次实际使用的 provider（或集合）
- `fallback_chain`：本次可用的主备链路
- `latency_ms`：本次调用耗时（毫秒）
- `stock_candidate_scan`：候选评分（candidate_score/candidate_label/reason_tags/risk_flags）
- `watchlist_review`：观察池评分（watchlist_score/status_label/reason_tags/risk_flags）
- `multi_timeframe_review`：多周期一致性（trend_score/trend_label/signal_tags/conflict_notes；指标获取失败时记录 `partial_failure` + errors 含 interval/indicator）
- `hot_theme_tracker`：热点主线跟踪（themes/theme_score/theme_label/pool_snapshot）

详细字段以实现返回为准，新增字段遵循向后兼容（尽量只增不删）。

---

## 7. 统一响应契约

所有 MCP tool 返回值遵循以下共享字段约定：

### 通用字段（跨 tool）

| 字段 | 类型 | 语义 | 产出 tool |
|---|---|---|---|
| `partial_failure` | bool | 本次调用存在部分数据获取失败 | margin_trading, limit_stat, multi_timeframe_review, stock_quote, stock_candidate_scan, watchlist_review 等 |
| `errors` | list[dict] | 失败条目列表；每条含 `error_code`, `message`, `retryable`, 上下文字段（如 `exchange`, `section`, `interval`, `indicator`, `symbol`） | 同上 |
| `provider_used` | str 或 list[str] | 实际使用的 provider | 所有 tool |
| `fallback_chain` | list[str] | 主备 provider 链路 | 所有 tool |
| `latency_ms` | int | 调用耗时（毫秒） | 所有 tool |

### 降级字段（tool-specific）

| 字段 | 类型 | 语义 | 产出 tool |
|---|---|---|---|
| `used_fallback_endpoint` | bool | 降级到了备用接口 | index_compose |
| `endpoint_note` | str | 降级原因说明 | index_compose |

### errors 条目通用结构

```json
{
  "error_code": "PROVIDER_UNAVAILABLE",
  "message": "...",
  "retryable": true,
  "provider": "zhitu"
}
```

tool-specific 上下文字段按需附加（如 `exchange`, `section`, `interval`, `indicator`, `symbol`）。

---

## 8. tool ↔ usecase 文件命名映射

| MCP tool 名 | usecase 文件 | 备注 |
|---|---|---|
| stock_search | stock_search.py | 1:1 |
| stock_quote | stock_quote.py | 1:1 |
| stock_history | stock_history.py | 1:1 |
| stock_review | stock_review.py | 1:1 |
| stock_review_batch | stock_review_batch.py | 1:1 |
| stock_orderbook | orderbook.py | 文件名不一致 |
| stock_profile | stock_profile.py | 1:1 |
| stock_financial | stock_financial.py | 1:1 |
| stock_candidate_scan | stock_candidate_scan.py | 1:1 |
| technical_indicator | technical_indicator.py | 1:1 |
| trading_calendar | trading_calendar.py | 1:1 |
| market_overview | market_overview.py | 1:1 |
| market_brief | market_brief.py | 1:1 |
| market_pool | market_pool.py | 1:1 |
| sector_review | sector_review.py | 1:1 |
| sector_rotation_review | sector_rotation_review.py | 1:1 |
| sector_lookup | sector_lookup.py | 1:1 |
| sector_quote | sector_quote.py | 1:1 |
| sector_leaders | sector_leaders.py | 1:1 |
| watchlist_review | watchlist_review.py | 1:1 |
| multi_timeframe_review | multi_timeframe_review.py | 1:1 |
| hot_theme_tracker | hot_theme_tracker.py | 1:1 |
| event_calendar | event_calendar.py | 1:1 |
| capital_flow | capital_flow.py | 1:1 |
| limit_stat | limit_stat.py | 1:1 |
| northbound | northbound.py | 1:1 |
| valuation_rank | valuation_rank.py | 1:1 |
| index_compose | index_compose.py | 1:1 |
| industry_valuation_rank | industry_valuation_rank.py | 1:1 |
| earnings_quality | earnings_quality.py | 1:1 |
| macro_indicator | macro_indicator.py | 1:1 |
| dragon_tiger | dragon_tiger.py | 1:1 |
| etf_snapshot | etf_snapshot.py | 1:1 |
| convertible_bond | convertible_bond.py | 1:1 |
| derivatives_data | derivatives_data.py | 1:1 |
| margin_trading | margin_trading.py | 1:1 |
| provider_health | provider_health.py | 1:1 |
| block_trade | block_trade.py | 1:1 |
| institute_hold | institute_hold.py | 1:1 |
| money_rate | money_rate.py | 1:1 |
| stock_screen | stock_screen.py | 1:1 |
| insider_trade | insider_trade.py | 1:1 |
| dividend_rank | dividend_rank.py | 1:1 |
| shareholder_change | shareholder_change.py | 1:1 |
| disclosure_calendar | disclosure_calendar.py | 1:1 |
| stock_repurchase | stock_repurchase.py | 1:1 |

---

## 6. 上游数据源文档入口

### AKShare
- https://akshare.akfamily.xyz/

### Zhitu API
- A 股：https://www.zhituapi.com/hsstockapi.html
- 沪深指数：https://www.zhituapi.com/hsindexapi.html
- 北交所：https://www.zhituapi.com/bjdataapi.html
- 科创板：https://www.zhituapi.com/kcdataapi.html
- 基金：https://www.zhituapi.com/fundmarketapi.html


## 榜单语义统一（v1）
适用工具：`sector_quote`、`stock_candidate_scan`、`watchlist_review`、`sector_leaders`
- 输入：`sort_by/descending/top_n/return_mode`
- 输出 meta：`filtered_from/filtered_count/ranked_count`
