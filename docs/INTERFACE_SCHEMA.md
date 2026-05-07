# Interface Schema (`openclaw-stock-mcp`)

Last Updated: 2026-05-07

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
- sector_lookup
- sector_review
- sector_rotation_review
- hot_theme_tracker
- provider_health

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
- market_pool / stock_orderbook：`zhitu`
- stock_quote：
  - stock-main：`zhitu` 主，`akshare` 备（批量请求使用 `/hs/public/ssjymore`，最多 20 支）
  - index/fund：`zhitu` 主，`akshare` 备
  - stock-bj/star：`zhitu`
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
- `sector_review`：板块成员聚合（breadth/stats/sentiment/rotation/structure/rankings/buckets）
- `sector_rotation_review`：跨板块比较（rankings/buckets/rotation）
- `stock_candidate_scan`：候选评分（candidate_score/candidate_label/reason_tags/risk_flags）
- `watchlist_review`：观察池评分（watchlist_score/status_label/reason_tags/risk_flags）
- `multi_timeframe_review`：多周期一致性（trend_score/trend_label/signal_tags/conflict_notes）
- `hot_theme_tracker`：热点主线跟踪（themes/theme_score/theme_label/pool_snapshot）

详细字段以实现返回为准，新增字段遵循向后兼容（尽量只增不删）。

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
