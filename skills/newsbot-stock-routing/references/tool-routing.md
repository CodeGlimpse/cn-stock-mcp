# Tool routing

## 0. 低 token 默认规则

- 先用最轻 tool，够回答就停；不要默认走最重聚合工具。
- 默认小参数：`limit/top_n` 先用 `3~5`，只有用户要求更全覆盖时再放大。
- 名称/代码不确定时先 `stock_search`，不要直接猜。
- 常规回答不要先跑 `provider_health`；只在诊断上游异常时使用。
- `sector_lookup(mode=children|members)` 必须显式传 `sector_type=primary|concept`。
- 用户只问单板块时，不要升级到 `sector_rotation_review`。
- 只要轻量股池快照时，不要升级到 `limit_up_pool`。

## 1. 意图 → tool（高频 / 常规）

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
- 北向资金流向 / 历史 → `northbound`
- 估值排名（PE/PB + 市场估值温度）→ `valuation_rank`
- 指数成分与权重分析 → `index_compose`
- 指数增强组合对比（增强收益/基准收益/超额收益/成分贡献/权重暴露/行业暴露）→ `index_enhance`
- 行业估值分位（一级行业横向估值）→ `industry_valuation_rank`
- 盈利质量评估（财报质量打分）→ `earnings_quality`
- 宏观经济指标（CPI/PPI/PMI/GDP/LPR/M2/信贷/出口/非农/BDI/黄金等）→ `macro_indicator`
- 龙虎榜（日榜明细/机构买卖/活跃营业部/营业部胜率/个股上榜统计）→ `dragon_tiger`
- 龙虎榜机构席位深度（单股买卖席位/活跃营业部/机构明细/机构追踪/席位标签）→ `sec_reveal`
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
- 回购明细（公司回购计划/进度/已回购金额）→ `stock_repurchase`
- 多股横向对比（行情+估值+财务+股息分层加载）→ `stock_compare`
- 产业链上下游（行业涨跌/资金流入+概念板块驱动事件/龙头股）→ `industry_chain`
- 权证/期权（ETF期权+商品期权+股指期权）→ `stock_warrant`
- 主力资金流向（全市场趋势+行业净流入排名+单股历史）→ `fund_flow`
- 涨停/跌停股池历史分析（涨停/跌停/强势/昨涨停/次新/炸板，含情绪指标汇总与行业维度情绪汇总）→ `limit_up_pool`
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
  - Zhitu 股票实时行情保持原始数值口径：`volume` = **万手**，`turnover` = **元**，`pe` = **动态市盈率**，`market_cap` / `float_market_cap` = **百元**（即元口径市值 / 100）。
  - 注意：`stock_history.items[].volume` 当前为 **手**，与 `stock_quote.volume` 的 **万手** 不同。
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
  - 使用参数 `flow_type`，不是 `mode`。
  - `flow_type=market` 返回 `records`（历史市场资金流序列）和 `market_summary`（指定 `trade_date` 的当日摘要）。
  - `market_summary.avg_main_net_inflow_pct` 虽字段名带 `avg`，当前实际语义是**当日主力资金净流入占比**，不是区间平均值。
  - `flow_type=industry/concept` 返回榜单型 `items`；其中 `rank` 是**上游原始涨跌幅排名**，不是当前按 `net_amount` 排序后的序号。
- `stock_financial`：`akshare`
  - 当前已恢复 `stock_financial_abstract_new_ths` 路径；`snapshot/history/details` 三层都已验证通过。
  - 三表明细请显式传 `include=["details"]`，并使用 `statement=income|balance|cashflow`。
- `limit_stat`：`akshare`（跌停数补充来自 zhitu market_pool）
- `northbound`：`akshare`（当前仅支持 `daily_summary` / `history`）
- `valuation_rank`：市场估值快照用 `akshare`；个股估值字段复用 `stock_quote`（`zhitu` 主，`akshare` 备）
- `index_compose`：`akshare`
- `index_enhance`：`akshare` + quote/history provider fallback
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
- `stock_repurchase`：`akshare`
- `stock_compare`：`zhitu` 主 + `akshare` 备
- `industry_chain`：`akshare`
- `stock_warrant`：`akshare`
- `fund_flow`：`akshare`
- `limit_up_pool`：`akshare`
- `sec_reveal`：`akshare`
- `sector_quote`：板块指数行情走 `zhitu`
- `stock_candidate_scan`：universe 扩展走 `zhitu`，成员复盘当前复用 `akshare`
- `stock_profile`：公司基本面走 `zhitu`（profile/dividends/unlocks/profits/valuation）
- `sector_review`：成员股获取走 `zhitu`，支持 `sector_type=primary`（一级行业）和 `sector_type=concept`（概念题材），成员复盘复用 `akshare`
- `sector_leaders`：成员股获取走 `zhitu`，成员复盘复用 `akshare`，返回 leaders/followers/draggers 快照
- `sector_rotation_review`：对多个 `sector_review` 结果做横向聚合；支持 `sector_type=primary` 和 `sector_type=concept`；较小 `limit` 起步
- `hot_theme_tracker`：复用 `sector_rotation_review + market_pool` 做主线聚合
- `market_overview` / `market_pool` / `stock_orderbook` / `sector_lookup`：`zhitu`
  - `market_pool(limit_up)` 的 `extra.limit_count` 表示当前连续涨停板数/连板高度；`extra.stat` 通常为 `N/M`，表示 N 天 M 板（最近 N 个交易日内出现 M 次涨停）。

补充：
- `stock_orderbook(stock-main)`：当前走沪深主板五档接口 `/hs/real/five/{code}`
- `stock_orderbook(stock-bj/star)`：继续走 `bj/tech` 的 `mmwp` 路径

如用户明确要求优先顺序，再传：
- `provider_preference: ["akshare", "zhitu"]`
- `provider_preference: ["zhitu", "akshare"]`

## 4. Payload 示例入口

- 高频最小 payload：读 `tool-examples.md`
- 长尾工具示例：按需查仓库主文档或后续分组示例
- 默认先用最小 payload；只有用户明确要求更大覆盖时再放大 `limit/top_n`

## 5. 榜单工具 return_mode 约定
- `full`：过滤+排序后全量返回
- `ranked_only`：只返回 top_n（用于榜单卡片）
