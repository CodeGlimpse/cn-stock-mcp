# Tool routing

## 1. 意图 → tool

- 系统异常 / 上游挂了 → `provider_health`
- 是否交易日 / 上下个交易日 → `trading_calendar`
- 市场简报 / 收盘复盘 → `market_brief`
- 实时价格 / 涨跌 / 快照 → `stock_quote`
- 历史走势 / K线 / 分时 → `stock_history`
- 单只标的多周期共振 / 周期冲突 → `multi_timeframe_review`
- 单股复盘 → `stock_review`
- 股票池批量对比 → `stock_review_batch`
- 候选扫描 / 找优先级 → `stock_candidate_scan`
- 固定观察池 / 自选池复盘 → `watchlist_review`
- 单板块复盘 / 行业强弱 / 龙头跟风拖累 → `sector_review`
- 多板块横向比较 / 板块轮动 → `sector_rotation_review`
- MACD / MA / BOLL / KDJ → `technical_indicator`
- 涨停 / 跌停 / 强势股池 → `market_pool`
- 指数概况 / 大盘概览 → `market_overview`
- 板块列表 / 某板块有哪些股票 → `sector_lookup`
- 代码不确定 / 名称歧义 → `stock_search`

规则：**代码不确定时先 search，再 quote/history/review。**

## 2. 参数硬规则

### 2.1 `sec_type` 必须和 symbol 一致

常见组合：
- `stock`: `600519.SH` / `000001.SZ` / `688001.SH`
- `index`: `000001.SH` / `399001.SZ` / `399006.SZ` / `899050.BJ`
- `fund`: `159001.SZ`

禁止错配；错配会直接返回 `INVALID_ARGUMENT`。

### 2.2 周期参数

只用：`5/15/30/60/d/w/m/y`

补充：
- **不要传 `1m`**
- `m` 表示 **月线 `1M`**，不是 1 分钟

### 2.3 指标参数

只用：`macd / ma / boll / kdj`

### 2.4 股池类型

优先标准值：`limit_up / limit_down / strong`

### 2.5 `sector_lookup`

- `list + concept`：概念板块列表
- `list + primary`：一级板块列表
- `children` / `members`：**股票成员列表**，不是子板块

### 2.6 非交易日回退

这些工具会自动回退到最近有效交易日：
- `stock_review`
- `stock_review_batch`
- `market_brief`
- `market_pool`（当 `trade_date` 为空时）

## 3. 默认 provider 路由

- `stock_quote(stock-main)`：`zhitu` 主，`akshare` 备
- `stock_quote(index/fund)`：`zhitu` 主，`akshare` 备
- `stock_quote(stock-bj/star)`：`zhitu` 主
- `stock_search`：`akshare` 主，`zhitu` 备
- `stock_history(stock)`：`akshare`
- `stock_history(index)`：`zhitu` 主，`akshare` 备
- `stock_review` / `stock_review_batch` / `trading_calendar`：`akshare`
- `watchlist_review`：显式 symbols 池，成员复盘当前复用 `akshare`
- `stock_candidate_scan`：universe 扩展走 `zhitu`，成员复盘当前复用 `akshare`
- `sector_review`：成员股获取走 `zhitu`，成员复盘当前复用 `akshare`
- `sector_rotation_review`：对多个 `sector_review` 结果做横向聚合；当前建议 `primary` 板块、较小 `limit` 起步
- `market_overview` / `market_pool` / `stock_orderbook` / `sector_lookup`：`zhitu`

如用户明确要求优先顺序，再传：
- `provider_preference: ["akshare", "zhitu"]`
- `provider_preference: ["zhitu", "akshare"]`

## 4. 最小 payload 模板

### 实时行情
```json
{"tool":"stock_quote","payload":{"symbols":["600519.SH"],"sec_type":"stock"}}
```

### 指数历史
```json
{"tool":"stock_history","payload":{"symbol":"000001.SH","sec_type":"index","interval":"d","limit":30}}
```

### 单股复盘
```json
{"tool":"stock_review","payload":{"symbol":"600519.SH","trade_date":"2026-05-01"}}
```

### 市场简报
```json
{"tool":"market_brief","payload":{"brief_type":"close","trade_date":"2026-05-01","top_n":3}}
```

### 股池
```json
{"tool":"market_pool","payload":{"pool_type":"limit_up","limit":20}}
```

### 板块成员股
```json
{"tool":"sector_lookup","payload":{"mode":"children","sector_name":"TFG板块趋势","limit":20}}
```

### 板块复盘
```json
{"tool":"sector_review","payload":{"sector_name":"TFG板块趋势","trade_date":"2026-04-30","top_n":3,"limit":20}}
```

### 板块区间轮动复盘
```json
{"tool":"sector_review","payload":{"sector_name":"TFG板块趋势","start_date":"2026-04-01","end_date":"2026-04-30","top_n":3,"limit":20}}
```

### 板块轮动复盘（多板块）
```json
{"tool":"sector_rotation_review","payload":{"sector_names":["1000信息","1000工业"],"sector_type":"primary","trade_date":"2026-05-06","top_n":2,"member_top_n":2,"limit":5}}
```

### 候选扫描
```json
{"tool":"stock_candidate_scan","payload":{"pool_type":"strong","trade_date":"2026-05-06","limit":5,"top_n":3}}
```

### 观察池复盘
```json
{"tool":"watchlist_review","payload":{"symbols":["600519.SH","300750.SZ","000001.SZ"],"watchlist_name":"核心池","trade_date":"2026-05-06","top_n":2}}
```

### 多周期复盘
```json
{"tool":"multi_timeframe_review","payload":{"symbol":"000001.SH","sec_type":"index","intervals":["15","d","w"],"indicators":["macd","ma","kdj"],"limit":60}}
```
