# Full Examples (`cn-stock-mcp`)

给需要完整调用样例的人类开发者使用。AI agent 默认先读：

- `docs/AGENT_MINIMAL.md`
- `docs/EXAMPLES_MINIMAL.md`

只有在需要更完整调用模板时，再读本页。

## 高频与常规能力样例

### stock_quote(stock-main) 双源路由样例

```bash
# 默认路由（stock-main）：zhitu 主，akshare 备
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_quote --payload '{"symbols":["600519.SH"],"sec_type":"stock"}'

# 批量行情（沪深主板自动走 /hs/public/ssjymore 批量接口，最多 20 支）
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_quote --payload '{"symbols":["600519.SH","000001.SZ","601318.SH"],"sec_type":"stock"}'

# 显式指定 provider_preference（先 akshare，再 zhitu）
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_quote --payload '{"symbols":["600519.SH"],"sec_type":"stock","provider_preference":["akshare","zhitu"]}'
```

### trading_calendar 复盘日期辅助样例

```bash
# 单日判断：是否交易日、前后交易日、最近交易日
PYTHONPATH=src python -m cn_stock_mcp.main --tool trading_calendar --payload '{"date":"2026-05-01"}'

# 区间交易日列表
PYTHONPATH=src python -m cn_stock_mcp.main --tool trading_calendar --payload '{"start_date":"2026-04-27","end_date":"2026-05-08"}'
```

### stock_history(index) 多周期调用样例（5/15/30/60/d/w/m/y）

```bash
# 5分钟
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_history --payload '{"symbol":"000001.SH","sec_type":"index","interval":"5","limit":20}'

# 日线
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_history --payload '{"symbol":"000001.SH","sec_type":"index","interval":"d","limit":30}'

# 周线
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_history --payload '{"symbol":"000001.SH","sec_type":"index","interval":"w","limit":30}'

# 月线
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_history --payload '{"symbol":"000001.SH","sec_type":"index","interval":"m","limit":24}'
```

### stock_history(stock) 分钟级 / 复权样例

```bash
# 股票 5 分钟（分钟级自动按不复权请求）
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_history --payload '{"symbol":"600519.SH","sec_type":"stock","interval":"5","start_date":"2026-05-07","end_date":"2026-05-07","limit":20,"adjust":"qfq"}'

# 股票日线前复权
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_history --payload '{"symbol":"600519.SH","sec_type":"stock","interval":"d","start_date":"2026-04-01","end_date":"2026-05-07","limit":30,"adjust":"qfq"}'

# 股票周线后复权
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_history --payload '{"symbol":"600519.SH","sec_type":"stock","interval":"w","start_date":"2026-01-01","end_date":"2026-05-07","limit":20,"adjust":"hfq"}'
```

说明：
- `stock_history(stock)` 当前默认优先走 **Zhitu**，`akshare` 作为 fallback。
- 分钟级（`5/15/30/60`）在 Zhitu 上**仅支持不复权**；即使传入 `qfq/hfq`，底层也会自动按 `n` 请求。
- 日线及以上支持：`none / qfq / hfq`，并映射到 Zhitu 的 `n / f / b`。

### technical_indicator 多指标 / 多周期调用样例

```bash
# MACD + 日线（d）
PYTHONPATH=src python -m cn_stock_mcp.main --tool technical_indicator --payload '{"symbol":"000001.SH","sec_type":"index","indicator":"macd","interval":"d","limit":30}'

# MA + 15分钟（15）
PYTHONPATH=src python -m cn_stock_mcp.main --tool technical_indicator --payload '{"symbol":"000001.SH","sec_type":"index","indicator":"ma","interval":"15","limit":50}'

# BOLL + 周线（w）
PYTHONPATH=src python -m cn_stock_mcp.main --tool technical_indicator --payload '{"symbol":"000001.SH","sec_type":"index","indicator":"boll","interval":"w","limit":40}'

# KDJ + 月线（m）
PYTHONPATH=src python -m cn_stock_mcp.main --tool technical_indicator --payload '{"symbol":"000001.SH","sec_type":"index","indicator":"kdj","interval":"m","limit":24}'
```

### technical_indicator(stock) 股票指标样例

```bash
# 股票日线 MACD
PYTHONPATH=src python -m cn_stock_mcp.main --tool technical_indicator --payload '{"symbol":"600519.SH","sec_type":"stock","indicator":"macd","interval":"d","start_date":"2026-04-01","end_date":"2026-05-07","limit":30}'

# 股票 5 分钟 MA（分钟级仅请求不复权数据）
PYTHONPATH=src python -m cn_stock_mcp.main --tool technical_indicator --payload '{"symbol":"600519.SH","sec_type":"stock","indicator":"ma","interval":"15","start_date":"2026-05-07","end_date":"2026-05-07","limit":20}'
```

说明：
- `technical_indicator(stock)` 当前优先走 **Zhitu**，`akshare` 作为 fallback。
- 股票指标当前支持 `macd / ma / boll / kdj`。
- 分钟级指标当前仅请求 **不复权** 数据。

### market_pool 类型扩充调用样例

```bash
# 标准类型：不传 trade_date 时，自动回退到最近有效交易日
PYTHONPATH=src python -m cn_stock_mcp.main --tool market_pool --payload '{"pool_type":"limit_up","limit":50}'

# 显式指定 trade_date
PYTHONPATH=src python -m cn_stock_mcp.main --tool market_pool --payload '{"pool_type":"limit_up","trade_date":"2026-05-01","limit":50}'
```

### hot_theme_tracker 热点主线跟踪样例

```bash
# 显式指定主线候选板块
PYTHONPATH=src python -m cn_stock_mcp.main --tool hot_theme_tracker --payload '{"sector_names":["1000信息","1000工业","1000医药"],"sector_type":"primary","trade_date":"2026-05-06","top_n":3,"member_limit":5}'

# 不指定 sector_names：自动从 primary 板块列表中截取前 N 个做热度跟踪
PYTHONPATH=src python -m cn_stock_mcp.main --tool hot_theme_tracker --payload '{"sector_type":"primary","trade_date":"2026-05-06","sector_limit":8,"top_n":3}'
```

### stock_review 个股复盘摘要样例

```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_review --payload '{"symbol":"600519.SH","trade_date":"2026-05-01"}'
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_review --payload '{"symbol":"600519.SH","start_date":"2026-04-01","end_date":"2026-05-01"}'
```

### stock_review_batch 批量复盘样例

```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_review_batch --payload '{"symbols":["600519.SH","000001.SZ","300750.SZ"],"trade_date":"2026-05-01","sort_by":"relative_strength","top_n":3}'
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_review_batch --payload '{"symbols":["600519.SH","000001.SZ","300750.SZ"],"start_date":"2026-04-01","end_date":"2026-05-01","sort_by":"return","top_n":3}'
```

### market_brief 一键市场简报样例

```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool market_brief --payload '{}'
PYTHONPATH=src python -m cn_stock_mcp.main --tool market_brief --payload '{"brief_type":"close","trade_date":"2026-05-01","top_n":3}'
PYTHONPATH=src python -m cn_stock_mcp.main --tool market_brief --payload '{"include_pools":false}'
```

### sector_review 板块复盘样例

```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool sector_review --payload '{"sector_name":"1000信息","sector_type":"primary","trade_date":"2026-04-30","top_n":3,"limit":20}'
PYTHONPATH=src python -m cn_stock_mcp.main --tool sector_review --payload '{"sector_name":"人工智能","sector_type":"concept","trade_date":"2026-04-30","top_n":3,"limit":20}'
PYTHONPATH=src python -m cn_stock_mcp.main --tool sector_review --payload '{"sector_name":"1000信息","sector_type":"primary","start_date":"2026-04-01","end_date":"2026-04-30","top_n":3,"limit":20}'
```

### stock_profile 公司基本面样例

```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_profile --payload '{"symbol":"000001.SZ"}'
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_profile --payload '{"symbol":"600519.SH","include":["profile","dividends","valuation"]}'
```

### sector_rotation_review 板块轮动复盘样例

```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool sector_rotation_review --payload '{"sector_names":["1000信息","1000工业"],"sector_type":"primary","trade_date":"2026-05-06","top_n":1,"member_top_n":1,"limit":1}'
PYTHONPATH=src python -m cn_stock_mcp.main --tool sector_rotation_review --payload '{"sector_names":["1000信息","1000工业","1000医药"],"sector_type":"primary","start_date":"2026-04-01","end_date":"2026-04-30","top_n":2,"member_top_n":2,"limit":3}'
```

### stock_candidate_scan 候选扫描样例

```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_candidate_scan --payload '{"pool_type":"strong","trade_date":"2026-05-06","limit":3,"top_n":2}'
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_candidate_scan --payload '{"symbols":["600519.SH"],"sector_names":["1000信息","1000工业"],"sector_type":"primary","trade_date":"2026-05-06","limit":5,"top_n":3}'
```

### watchlist_review 观察池复盘样例

```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool watchlist_review --payload '{"symbols":["600519.SH","300750.SZ","000001.SZ"],"watchlist_name":"核心池","trade_date":"2026-05-06","top_n":2}'
PYTHONPATH=src python -m cn_stock_mcp.main --tool watchlist_review --payload '{"symbols":["600519.SH","300750.SZ","000001.SZ"],"watchlist_name":"核心池","start_date":"2026-04-01","end_date":"2026-05-06","top_n":3}'
```

### multi_timeframe_review 多周期复盘样例

```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool multi_timeframe_review --payload '{"symbol":"000001.SH","sec_type":"index","intervals":["15","d","w"],"indicators":["macd","ma","kdj"],"limit":60}'
PYTHONPATH=src python -m cn_stock_mcp.main --tool multi_timeframe_review --payload '{"symbol":"600519.SH","sec_type":"stock","intervals":["30","d","w"],"indicators":["macd","ma","kdj"],"limit":60}'
```

## 补充样例

### event_calendar 事件时间轴样例

```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool event_calendar --payload '{"symbols":["600519.SH"],"event_types":["dividend","unlock","profit"],"start_date":"2026-01-01","end_date":"2026-12-31"}'
PYTHONPATH=src python -m cn_stock_mcp.main --tool event_calendar --payload '{"symbols":["600519.SH"],"next_event_only":true}'
```

### sector_leaders 板块龙头快照样例

```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool sector_leaders --payload '{"sector_name":"1000信息","sector_type":"primary","trade_date":"2026-05-08","top_n":3}'
```
