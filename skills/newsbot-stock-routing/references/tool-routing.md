# Tool routing

## 1. 意图 → tool

- 板块指数行情 / 快速榜单（涨跌幅/成交额）→ `sector_quote`（支持 min_turnover/min_change_percent/exclude_null_fields/return_mode）
- 系统异常 / 上游挂了 → `provider_health`
- 是否交易日 / 上下个交易日 → `trading_calendar`
- 市场简报 / 收盘复盘 → `market_brief`
- 实时价格 / 涨跌 / 快照 → `stock_quote`
- 历史走势 / K线 / 分时 → `stock_history`
- 单只标的多周期共振 / 周期冲突 → `multi_timeframe_review`
- 单股复盘 → `stock_review`
- 股票池批量对比 → `stock_review_batch`
- 公司基本面 / 概念标签 / 分红 / 解禁 / 估值快照 → `stock_profile`
- 事件时间轴（分红/解禁/业绩）→ `event_calendar`（可用 `next_event_only=true` 做盘前提醒；同日冲突可传 `event_priority`）
- 候选扫描 / 找优先级 → `stock_candidate_scan`
- 固定观察池 / 自选池复盘 → `watchlist_review`
- 单板块复盘 / 行业强弱 / 龙头跟风拖累 → `sector_review`（支持 `sector_type=primary` 一级行业 / `sector_type=concept` 概念题材）
- 板块龙头/跟风/拖累快照（轻量）→ `sector_leaders`
- 多板块横向比较 / 板块轮动 → `sector_rotation_review`
- 热点主线跟踪 / 主线切换 → `hot_theme_tracker`
- 资金流向（大盘/个股/行业/概念）→ `capital_flow`
- 财报核心面板 / 三表明细 → `stock_financial`
- 短线情绪（封板率/连板/炸板）→ `limit_stat`
- 北向资金流向 / 持股排行 → `northbound`
- 估值排名（PE/PB + 市场估值温度）→ `valuation_rank`
- 指数成分与权重分析 → `index_compose`
- 行业估值分位（一级行业横向估值）→ `industry_valuation_rank`
- 盈利质量评估（财报质量打分）→ `earnings_quality`
- 宏观经济指标（CPI/PPI/PMI/GDP/LPR/M2/信贷/出口/非农/BDI/黄金等）→ `macro_indicator`
- 龙虎榜（日榜明细/机构买卖/活跃营业部/营业部胜率/个股上榜统计）→ `dragon_tiger`
- ETF行情快照（全市场实时+IOPV折溢价+资金流+份额+净值）→ `etf_snapshot`
- 可转债（双低/溢价率/YTM/强赎监控/等权指数）→ `convertible_bond`
- 期货/期权（期货实时+历史/期权合约/QVIX隐含波动率）→ `derivatives_data`
- 融资融券（两市汇总+个股明细/融资买入排序）→ `margin_trading`
- 大宗交易（每日明细+个股汇总/折溢率+行业统计+营业部胜率排行+活跃个股追踪）→ `block_trade`
- 机构持仓（季度汇总+个股明细/增持减持变动）→ `institute_hold`
- 货币市场利率（SHIBOR曲线+银行间拆借+回购定盘利率）→ `money_rate`
- 选股筛选（市场/价格/涨跌幅/成交量/成交额/振幅多条件）→ `stock_screen`
- 高管增减持（十大流通股东变动+增减持历史）→ `insider_trade`
- 股息率/分红排名（历史分红排名+分红方案+单股分红明细）→ `dividend_rank`
- 股东变动（十大股东变动+全市场股东持股汇总）→ `shareholder_change`
- 披露日历（财报披露时间表/预约日/变更/实际披露日）→ `disclosure_calendar`
- MACD / MA / BOLL / KDJ → `technical_indicator`
- 涨停 / 跌停 / 强势 / 次新 / 炸板股池 → `market_pool`
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

优先标准值：`limit_up / limit_down / strong / sub_new / broken_limit`

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

- `stock_quote(stock-main)`：`zhitu` 主，`akshare` 备；**批量请求自动走 `/hs/public/ssjymore`（最多 20 支）**
- `stock_quote(index/fund)`：`zhitu` 主，`akshare` 备
- `stock_quote(stock-bj)`：`zhitu` 主，`akshare` 备（AKShare 走 `stock_bj_a_spot_em()`，10s TTL 缓存）
- `stock_quote(stock-star)`：`zhitu` 主，`akshare` 备（Sina `stock_zh_a_spot()` 源，缺 PE/PB/市值/换手率/振幅）
- `stock_search`：`akshare` 主，`zhitu` 备
- `stock_history(stock)`：`zhitu` 主，`akshare` 备
- `stock_history(index)`：`zhitu` 主，`akshare` 备
- `technical_indicator(stock/index)`：`zhitu` 主，`akshare` 备
- `stock_review` / `stock_review_batch` / `trading_calendar`：`akshare`
- `watchlist_review`：显式 symbols 池，成员复盘当前复用 `akshare`
- `capital_flow`：`akshare`
- `stock_financial`：`akshare`
- `limit_stat`：`akshare`（跌停数补充来自 zhitu market_pool）
- `northbound`：`akshare`
- `valuation_rank`：市场估值快照用 `akshare`；个股估值字段复用 `stock_quote`（`zhitu` 主，`akshare` 备）
- `index_compose`：`akshare`
- `industry_valuation_rank`：成员股获取走 `sector_lookup(children, primary)`（`zhitu`），估值字段复用 `stock_quote`（`zhitu` 主，`akshare` 备）
- `earnings_quality`：`akshare`（复用 `stock_financial` 抽象快照）
- `macro_indicator`：`akshare`
- `dragon_tiger`：`akshare`
- `etf_snapshot`：`akshare`
- `convertible_bond`：`akshare`
- `derivatives_data`：`akshare`
- `margin_trading`：`akshare`
- `block_trade`：`akshare`
- `institute_hold`：`akshare`
- `money_rate`：`akshare`
- `stock_screen`：`akshare`
- `insider_trade`：`akshare`
- `dividend_rank`：`akshare`
- `shareholder_change`：`akshare`
- `disclosure_calendar`：`akshare`
- `sector_quote`：板块指数行情走 `zhitu`
- `stock_candidate_scan`：universe 扩展走 `zhitu`，成员复盘当前复用 `akshare`
- `stock_profile`：公司基本面走 `zhitu`（profile/dividends/unlocks/profits/valuation）
- `sector_review`：成员股获取走 `zhitu`，支持 `sector_type=primary`（一级行业）和 `sector_type=concept`（概念题材），成员复盘复用 `akshare`
- `sector_leaders`：成员股获取走 `zhitu`，成员复盘复用 `akshare`，返回 leaders/followers/draggers 快照
- `sector_rotation_review`：对多个 `sector_review` 结果做横向聚合；支持 `sector_type=primary` 和 `sector_type=concept`；较小 `limit` 起步
- `hot_theme_tracker`：复用 `sector_rotation_review + market_pool` 做主线聚合
- `market_overview` / `market_pool` / `stock_orderbook` / `sector_lookup`：`zhitu`

补充：
- `stock_orderbook(stock-main)`：当前走沪深主板五档接口 `/hs/real/five/{code}`
- `stock_orderbook(stock-bj/star)`：继续走 `bj/tech` 的 `mmwp` 路径

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

### 热点主线跟踪
```json
{"tool":"hot_theme_tracker","payload":{"sector_names":["1000信息","1000工业","1000医药"],"sector_type":"primary","trade_date":"2026-05-06","top_n":3,"member_limit":5}}
```

### 板块成员股
```json
{"tool":"sector_lookup","payload":{"mode":"children","sector_name":"TFG板块趋势","limit":20}}
```

### 板块复盘（一级行业）
```json
{"tool":"sector_review","payload":{"sector_name":"1000信息","sector_type":"primary","trade_date":"2026-04-30","top_n":3,"limit":20}}
```

### 板块复盘（概念题材）
```json
{"tool":"sector_review","payload":{"sector_name":"人工智能","sector_type":"concept","trade_date":"2026-04-30","top_n":3,"limit":20}}
```

### 板块区间复盘
```json
{"tool":"sector_review","payload":{"sector_name":"1000信息","sector_type":"primary","start_date":"2026-04-01","end_date":"2026-04-30","top_n":3,"limit":20}}
```

### 板块轮动复盘（多板块）
```json
{"tool":"sector_rotation_review","payload":{"sector_names":["1000信息","1000工业"],"sector_type":"primary","trade_date":"2026-05-06","top_n":2,"member_top_n":2,"limit":5}}
```

### 候选扫描
```json
{"tool":"stock_candidate_scan","payload":{"pool_type":"strong","trade_date":"2026-05-06","limit":5,"top_n":3}}
```

### 候选扫描（标签精筛）
```json
{"tool":"stock_candidate_scan","payload":{"pool_type":"strong","trade_date":"2026-05-06","top_n":5,"require_source_tags":["pool:strong"],"exclude_risk_flags":["weak_relative_strength"],"must_have_reason_tags":["strong_return","active_volume"],"exclude_reason_tags":["slight_positive_return"]}}
```

### 观察池复盘
```json
{"tool":"watchlist_review","payload":{"symbols":["600519.SH","300750.SZ","000001.SZ"],"watchlist_name":"核心池","trade_date":"2026-05-06","top_n":2}}
```

### 多周期复盘
```json
{"tool":"multi_timeframe_review","payload":{"symbol":"000001.SH","sec_type":"index","intervals":["15","d","w"],"indicators":["macd","ma","kdj"],"limit":60}}
```

### 宏观指标（最新值）
```json
{"tool":"macro_indicator","payload":{"indicator":"cpi","region":"cn","include":["latest"]}}
```

### 宏观指标（历史序列）
```json
{"tool":"macro_indicator","payload":{"indicator":"m2","region":"cn","include":["history"],"history_n":24}}
```

### 宏观概览（一地区核心指标快照）
```json
{"tool":"macro_indicator","payload":{"indicator":"overview","region":"cn","include":["overview"]}}
```

### 龙虎榜（日榜+机构）
```json
{"tool":"dragon_tiger","payload":{"include":["daily_detail","institution"],"trade_date":"2026-05-08","top_n":10}}
```

### 龙虎榜营业部胜率
```json
{"tool":"dragon_tiger","payload":{"include":["broker_rank"],"period":"近一月","top_n":10}}
```

### ETF全市场行情快照（按成交额排序）
```json
{"tool":"etf_snapshot","payload":{"include":["spot"],"sort_by":"turnover","top_n":20}}
```

### ETF折溢价筛选
```json
{"tool":"etf_snapshot","payload":{"include":["spot"],"min_discount":0.1,"sort_by":"discount_rate","top_n":10}}
```

### ETF净值序列
```json
{"tool":"etf_snapshot","payload":{"include":["nav"],"symbol":"510300","history_n":30}}
```

### 可转债双低策略筛选
```json
{"tool":"convertible_bond","payload":{"include":["spot"],"sort_by":"double_low","max_double_low":120,"top_n":20}}
```

### 可转债强赎监控
```json
{"tool":"convertible_bond","payload":{"include":["redeem"],"call_status_filter":"called","top_n":10}}
```

### 期货实时+QVIX
```json
{"tool":"derivatives_data","payload":{"include":["futures_spot","qvix"],"qvix_underlying":"50etf"}}
```

### 期货历史（螺纹钢主力）
```json
{"tool":"derivatives_data","payload":{"include":["futures_hist"],"futures_symbol":"RB0","history_n":60}}
```

### 期权合约列表
```json
{"tool":"derivatives_data","payload":{"include":["option_list"],"option_exchange":"both","option_type_filter":"call"}}
```

### 融资融券汇总+明细
```json
{"tool":"margin_trading","payload":{"include":["summary","detail"],"trade_date":"2026-05-08","exchange":"both","sort_by":"financing_buy","top_n":20}}
```

### 大宗交易（每日明细+个股汇总）
```json
{"tool":"block_trade","payload":{"include":["daily_detail","daily_stat"],"trade_date":"2026-05-06","sort_by":"turnover","top_n":20}}
```

### 大宗交易（行业统计+营业部排行）
```json
{"tool":"block_trade","payload":{"include":["industry_stat","broker_rank"],"period":"近一月","industry_period":"近3日","top_n":10}}
```

### 大宗交易（活跃个股追踪）
```json
{"tool":"block_trade","payload":{"include":["active_stock"],"period":"近三月","sort_by":"total_turnover","top_n":20}}
```

### 机构持仓（季度汇总）
```json
{"tool":"institute_hold","payload":{"include":["summary"],"quarter":"auto","sort_by":"institute_count","top_n":20}}
```

### 机构持仓（个股明细）
```json
{"tool":"institute_hold","payload":{"include":["detail"],"quarter":"auto","symbol":"600519.SH","sort_by":"hold_ratio_change","descending":true}}
```

### 货币市场利率（SHIBOR+回购）
```json
{"tool":"money_rate","payload":{"include":["shibor","repo"],"shibor_days":10,"repo_mode":"latest"}}
```

### 货币市场利率（银行间拆借历史）
```json
{"tool":"money_rate","payload":{"include":["interbank"],"interbank_indicator":"1周","interbank_days":30}}
```

### 货币市场利率（回购历史）
```json
{"tool":"money_rate","payload":{"include":["repo"],"repo_mode":"hist","start_date":"2026-05-01","end_date":"2026-05-13"}}
```

### 选股筛选（涨跌幅>3%，成交额>1亿）
```json
{"tool":"stock_screen","payload":{"market":"main","min_change_pct":3,"min_turnover":100000000,"sort_by":"change_pct","descending":true,"top_n":20}}
```

### 选股筛选（科创板，振幅>5%）
```json
{"tool":"stock_screen","payload":{"market":"star","min_amplitude":5,"sort_by":"amplitude","descending":true,"top_n":20}}
```

### 选股筛选（低价股，10-30元，放量）
```json
{"tool":"stock_screen","payload":{"market":"all","min_price":10,"max_price":30,"min_volume":50000000,"sort_by":"turnover","descending":true,"top_n":30}}
```

### 高管增减持（十大股东+增减持历史）
```json
{"tool":"insider_trade","payload":{"include":["top10","change"],"symbol":"600519.SH","quarter":"auto"}}
```

### 高管增减持（仅十大流通股东变动）
```json
{"tool":"insider_trade","payload":{"include":["top10"],"symbol":"600519.SH","quarter":"20254","top_n":10}}
```

### 股息率/分红排名（高股息排名）
```json
{"tool":"dividend_rank","payload":{"include":["rank"],"sort_by":"avg_annual_dividend","descending":true,"top_n":20}}
```

### 股息率/分红排名（最新分红方案，按股息率排序）
```json
{"tool":"dividend_rank","payload":{"include":["plan"],"report_date":"latest","sort_by":"dividend_yield","descending":true,"top_n":20}}
```

### 股息率/分红排名（单股分红历史）
```json
{"tool":"dividend_rank","payload":{"include":["detail"],"symbol":"600519.SH"}}
```

### 股东变动（单股十大股东变动）
```json
{"tool":"shareholder_change","payload":{"include":["top10"],"symbol":"600519.SH","quarter":"auto"}}
```

### 股东变动（全市场社保基金持股变动）
```json
{"tool":"shareholder_change","payload":{"include":["change"],"quarter":"auto","shareholder_type":"社保","sort_by":"new_hold","descending":true,"top_n":20}}
```

### 股东变动（基金持股汇总）
```json
{"tool":"shareholder_change","payload":{"include":["change"],"quarter":"auto","shareholder_type":"基金","sort_by":"float_cap","descending":true,"top_n":10}}
```

### 披露日历（最新报告期，已披露）
```json
{"tool":"disclosure_calendar","payload":{"period":"auto","status":"disclosed","sort_by":"actual_date","top_n":30}}
```

### 披露日历（待披露）
```json
{"tool":"disclosure_calendar","payload":{"period":"2024年报","status":"pending","sort_by":"first_schedule","top_n":20}}
```

### 披露日历（变更日期）
```json
{"tool":"disclosure_calendar","payload":{"period":"2024年报","status":"changed","top_n":20}}
```


## 5. 榜单工具 return_mode 约定
- `full`：过滤+排序后全量返回
- `ranked_only`：只返回 top_n（用于榜单卡片）
