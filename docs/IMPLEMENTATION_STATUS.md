# 实现状态说明

更新时间：2026-05-11

## 已完成

### 架构与文档
- `docs/design-v1.md`
- `docs/interface-schema-v1.1.md`
- `docs/provider-mapping.md`

### 基础代码结构
- schema / models / providers / services / usecases / MCP Python SDK stdio transport

### 正式 MCP tool（项目内注册中心）
- `stock_search`
- `stock_quote`
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
- `sector_quote`
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
- `industry_valuation_rank`
- `earnings_quality`
- `macro_indicator`
- `dragon_tiger`
- `etf_snapshot`
- `convertible_bond`
- `derivatives_data`
- `margin_trading`

### market_pool（股池）当前实现
- 标准类型已扩展为：`limit_up / limit_down / strong / sub_new / broken_limit`
- 当前别名映射：
  - `ztgc / up / 涨停 -> limit_up`
  - `dtgc / down / 跌停 -> limit_down`
  - `qsgc / 强势 -> strong`
  - `cxgc / 次新 -> sub_new`
  - `zbgc / 炸板 -> broken_limit`
- 当前 Zhitu 路径：
  - `limit_up -> /hs/pool/ztgc/{trade_date}`
  - `limit_down -> /hs/pool/dtgc/{trade_date}`
  - `strong -> /hs/pool/qsgc/{trade_date}`
  - `sub_new -> /hs/pool/cxgc/{trade_date}`
  - `broken_limit -> /hs/pool/zbgc/{trade_date}`
- 已补充统一 adapter：
  - `adapt_zhitu_limit_up_item`
  - `adapt_zhitu_limit_down_item`
  - `adapt_zhitu_strong_item`
  - `adapt_zhitu_sub_new_item`
  - `adapt_zhitu_broken_limit_item`

### hot_theme_tracker（热点主线跟踪）
- 已正式注册为 MCP tool：`hot_theme_tracker`
- 当前输入契约：`HotThemeTrackerRequest`
  - `sector_names[]` 可选
  - `sector_type=primary`
  - `watch_name`
  - `trade_date` 或 `start_date + end_date`
  - `top_n / sector_limit / member_limit / member_top_n / pool_top_n`
  - `include_pool_snapshot`
- 当前内部路径：
  - `sector_lookup(list)`：解析候选板块
  - `sector_rotation_review`：生成板块轮动卡片
  - `market_pool(limit_up/strong)`：生成股池快照
- 当前输出重点：
  - `themes`（完整主题卡）
  - `leaders / laggards`
  - `buckets.mainline_themes / watchlist_themes / risk_themes`
  - `pool_snapshot`
  - `meta.theme_score_schema=schema:theme_score_v1`
- 当前限制：
  - ~~v1 先聚焦 `primary` 板块~~（已移除：concept 板块路径已完整验证通过）
  - pool snapshot 当前只取 `limit_up + strong`

### sector_lookup（板块列表/成员股）当前实现
- 输入模式：`list | children | members(兼容别名)`
- `list + concept`：调用 `/hs/list/sectors`（概念板块列表）
- `list + primary`：调用 `/hs/list/primary`（一级板块列表）
- `children` / `members`：调用 `/hs/sectors/{sector_name}`（按一级板块名称查询股票成员列表）
- `SectorLookupRequest` 增加参数校验：
  - `mode=list` 默认 `sector_type=concept`
  - `mode=children` 默认 `sector_type=primary`
  - `mode in {members, children}` 时强制要求 `sector_name`

### stock_review（个股复盘摘要）
- 新增 `stock_review` tool
- 当前 provider：`akshare`
- 支持两种模式：
  - `trade_date`：单日复盘（若为非交易日，自动回退到有效交易日）
  - `start_date + end_date`：区间复盘
- 输出包含：
  - `latest_bar`
  - `stats`（近5日/20日、4周、3月、区间收益、高低点、均量均额等）
  - 增强指标：
    - 波动率：`volatility_pct`
    - 最大回撤：`max_drawdown_pct`
    - 连涨/连跌：`up_streak / down_streak`
    - 量能变化：`volume_ratio / turnover_ratio`
    - 相对强弱：`relative_strength_pct`
  - `benchmark`（自动匹配指数基准）
  - `windows.daily / weekly / monthly`
  - 可直接阅读的 `summary` 文本

### sector_quote（板块指数行情）
- 新增 `sector_quote` tool
- 当前 provider：`zhitu`
- 支持板块指数实时行情
- 输出包含：
  - `symbol`：板块指数代码（如 `101076.BKZS`）
  - `name`：板块名称
  - `sector_type`：`primary`（一级行业）或 `concept`（概念题材）
  - 价格字段：`price`、`open`、`high`、`low`、`prev_close`、`change`、`change_percent`
  - 量能字段：`volume`、`turnover`、`turnover_rate`、`amplitude`
  - 时间戳：`timestamp`
- Zhitu API 路径：`/hz/real/ssjy/{symbol}`（复用指数行情接口）

### stock_review_batch（批量个股复盘）
- 新增 `stock_review_batch` tool
- 复用 `stock_review` 的单股能力，生成批量复盘卡片
- 支持排序字段：
  - `relative_strength`
  - `return`
  - `max_drawdown`
  - `volume_ratio`
- 支持筛选条件：
  - `min_relative_strength`
  - `min_return`
  - `max_drawdown_limit`
  - `min_volume_ratio`
- 输出包含：
  - `items`（批量卡片）
  - `tags`（如 `stronger_than_benchmark / high_volume / drawdown_risk / up_streak / down_streak`）
  - `groups`（强势候选 / 风险候选 / 放量关注）
  - `partial_failure / errors`
  - `summary`（批量筛查摘要）

### sector_review（板块复盘 / 板块成员聚合分析）
- 新增 `sector_review` tool
- 当前路径：
  - `sector_lookup(children)` 获取板块成员股（当前 provider：`zhitu`）
  - `stock_review_batch` 对成员股做批量复盘（当前复用 `akshare` 路径）
- **支持板块类型：**
  - `sector_type=primary`：一级行业板块（默认）
  - `sector_type=concept`：概念板块（题材）
- 支持两种模式：
  - `trade_date`：单日板块复盘
  - `start_date + end_date`：区间板块复盘
- 支持参数：
  - `sector_type`：板块类型（`primary` / `concept`）
  - `sort_by / descending / top_n / limit`
  - `min_relative_strength / min_return / max_drawdown_limit / min_volume_ratio`
- 已与 `market_brief` 对齐到统一 `review_envelope_v1`
  - 新增统一字段：`subject_type / subject_name / requested_trade_date`
  - `leaders / laggards / items` 统一为同一类 review item-card
  - `meta.review_envelope_schema / meta.sentiment_score_schema / meta.rotation_score_schema` 明确暴露
- 输出包含：
  - `breadth`（上涨/下跌/放量/连涨连跌分布）
  - `stats`（平均收益、相对强弱、量比、回撤、离散度）
  - `sentiment`（偏热 / 偏强 / 中性 / 偏弱 / 偏冷；统一 `score=[-5,5]`、`normalized_score=[0,100]`）
  - `benchmark_summary`（板块成员基准分布与平均基准收益）
  - `continuity`（持续强势/弱势、连涨连跌情况）
  - `rotation`（区间模式下的轮动判断，如 `leader_driven / broad_advance / divergent_rotation`）
  - `structure`（板块结构标签，如 `broad_strength / high_dispersion / benchmark_outperform / trend_divergence`）
  - `rankings`（收益 / 相对强弱 / 量比 / 回撤风险榜）
  - `buckets`（`leaders / followers / draggers / risk_alerts / strong_candidates / weak_candidates`）
  - 可直接阅读的 `summary` 文本

### sector_rotation_review（多板块轮动复盘 / 跨板块横向比较）
- 新增 `sector_rotation_review` tool
- 当前路径：
  - 对每个 `sector_name` 复用 `sector_review`
  - 再聚合得到跨板块 `rankings / buckets / rotation / sentiment / structure`
- 当前支持：
  - `trade_date`：单日轮动复盘
  - `start_date + end_date`：区间轮动复盘
- 当前参数：
  - `sector_names[] / sector_type / sort_by / descending / top_n / limit / member_top_n`
  - `min_relative_strength / min_return / max_drawdown_limit / min_volume_ratio`
- 当前排序字段：
  - `avg_relative_strength`
  - `avg_return`
  - `positive_ratio`
  - `stronger_ratio`
  - `sentiment_score`
  - `rotation_score`
- 当前输出包含：
  - 顶层 `subject_type=sector_rotation`
  - 板块层 `breadth / stats / sentiment / benchmark_summary / continuity / rotation / structure`
  - 跨板块 `rankings`（如 `leaders_by_avg_return / leaders_by_avg_relative_strength / leaders_by_rotation_score`）
  - 跨板块 `buckets`（如 `mainline_sectors / broad_strength_sectors / leader_driven_sectors / watchlist_sectors / risk_sectors`）
  - `items`（每个板块一张 card）
  - `meta.item_schema.schema=sector_rotation_item_v1`
- 当前限制：
  - ~~v1 先只支持 `sector_type=primary`~~（已移除：concept 板块已完整验证通过）
  - live 路径仍偏重，较大 `limit` 或较多板块时耗时会明显上升
- 当前性能优化：
  - `stock_review` 改为日线一次取数，周/月线本地聚合
  - `stock_review_batch` 增加受控并发
  - `sector_rotation_review` 增加受控并发
  - 交易日历 / 历史数据 / 基准指数结果增加线程安全共享缓存
- 已完成真实验收：
  - `provider_health` 正常
  - `sector_lookup(mode=list, sector_type=primary)` 正常
  - `sector_review(1000信息, trade_date=2026-05-06, limit=3)` 正常
  - `sector_rotation_review([1000信息,1000工业], trade_date=2026-05-06, limit=1)` 已真实返回成功
  - `sector_rotation_review([1000信息,1000工业], trade_date=2026-05-06, limit=5)` 已真实返回成功
  - `sector_rotation_review([1000信息,1000工业,1000医药], trade_date=2026-05-06, limit=5)` 已真实返回成功
  - `sector_rotation_review([1000信息,1000工业,1000医药,1000公用,1000可选], trade_date=2026-05-06, limit=5)` 已真实返回成功

### stock_candidate_scan（候选扫描 / 股票 universe 筛选）
- 新增 `stock_candidate_scan` tool
- 当前路径：
  - `symbols[]`：直接作为手工 universe
  - `sector_names[]`：通过 `sector_lookup(children)` 扩展成员股
  - `pool_type`：通过 `market_pool` 扩展池成员
  - 合并去重后复用 `stock_review_batch`，再补 `candidate_score / candidate_label / reason_tags / risk_flags`
- 当前支持：
  - `trade_date`：单日候选扫描
  - `start_date + end_date`：区间候选扫描
- 当前参数：
  - `symbols[] / sector_names[] / sector_type / pool_type`
  - `sort_by / descending / top_n / limit`
  - `min_candidate_score / min_relative_strength / min_return / max_drawdown_limit / min_volume_ratio`
- 当前排序字段：
  - `candidate_score`
  - `relative_strength`
  - `return`
  - `volume_ratio`
  - `max_drawdown`
- 当前输出包含：
  - 顶层 `subject_type=candidate_scan`
  - `candidate_score_schema=candidate_score_v1`
  - `items` 中每项新增：`candidate_score / candidate_label / reason_tags / risk_flags / source_tags`
  - `rankings`（候选分 / 相对强弱 / 收益 / 量比 / 回撤）
  - `buckets`（`candidates / watchlist / observe / risk_alerts`）
- 当前定位：
  - 从板块、股池、自选池里做第一轮筛查
  - 为后续 `stock_review / stock_review_batch` 提供优先级
- 已完成真实验收：
  - `stock_candidate_scan(pool_type=strong, trade_date=2026-05-06, limit=3, top_n=2)` 已真实返回成功

### watchlist_review（观察池复盘 / 持续跟踪分层）
- 新增 `watchlist_review` tool
- 当前路径：
  - 显式传入 `symbols[]` 作为观察池
  - 复用 `stock_review_batch` 批量复盘
  - 再补 `watchlist_score / status_label / reason_tags / risk_flags`
- 当前支持：
  - `trade_date`：单日观察池复盘
  - `start_date + end_date`：区间观察池复盘
- 当前参数：
  - `symbols[] / watchlist_name`
  - `sort_by / descending / top_n`
  - `min_watchlist_score / min_relative_strength / min_return / max_drawdown_limit / min_volume_ratio`
- 当前排序字段：
  - `watchlist_score`
  - `relative_strength`
  - `return`
  - `volume_ratio`
  - `max_drawdown`
- 当前输出包含：
  - 顶层 `subject_type=watchlist`
  - `watchlist_score_schema=watchlist_score_v1`
  - `items` 中每项新增：`watchlist_score / status_label / reason_tags / risk_flags`
  - `rankings`（观察分 / 相对强弱 / 收益 / 量比）
  - `buckets`（`focus / monitor / observe / risk_alerts`）
- 当前定位：
  - 复盘一个固定观察池 / 核心池 / 自选池
  - 给出继续重点看、跟踪、观察、风险预警的分层

### multi_timeframe_review（多周期复盘 / 跨周期共振分析）
- 新增 `multi_timeframe_review` tool
- 当前路径：
  - 对 `intervals[]` 中每个周期分别调用 `stock_history`
  - 对 `indicators[]` 中每个指标分别调用 `technical_indicator`
  - 再聚合成跨周期 `trend_score / trend_label / signal_tags / conflict_notes`
- 当前支持：
  - 单只标的跨多个周期复盘
  - `trade_date` 或 `start_date + end_date`
- 当前参数：
  - `symbol / sec_type / intervals[] / indicators[] / limit`
- 当前输出包含：
  - 顶层 `subject_type=multi_timeframe`
  - `items`（每个周期一张 card）
  - `trend_score / trend_label / signal_tags / conflict_notes`
  - `alignment_score_schema=multi_timeframe_alignment_v1`
  - `buckets`（`bullish_timeframes / neutral_timeframes / bearish_timeframes / conflict_points`）
- 当前定位：
  - 判断短中长周期是否一致
  - 判断不同周期之间的结构冲突
- 已完成真实验收：
  - `multi_timeframe_review(symbol=000001.SH, sec_type=index, intervals=[15,d,w], indicators=[macd,ma,kdj], limit=60)` 已真实返回成功
- 指标获取失败不再静默跳过，记录到 `errors` 列表（含 interval/indicator/error_code/message/retryable），`partial_failure` 真实反映

### trading_calendar（交易日历 / 复盘日期辅助）
- 新增 `trading_calendar` tool
- 当前 provider：`akshare`
- 支持两类查询：
  - 单日查询：是否交易日、上一个交易日、下一个交易日、最近 N 个交易日
  - 区间查询：返回区间内交易日列表
- `TradingCalendarRequest` 增加参数校验：
  - `date` 不能与 `start_date/end_date` 混用
  - 区间模式强制要求 `start_date` + `end_date` 成对提供
  - `start_date <= end_date`

### stock_history(stock) 复盘增强
- 当前 provider：`akshare`
- 已支持周期：`1d / 1w / 1M`（输入别名仍可用：`d / w / m`）
- **当前不支持 `1m`；传入 `1m` 会在 schema 层直接报错，避免误映射为 `1M` 月线**
- `1w / 1M` 通过日线结果聚合得到：
  - 周线：按自然周聚合
  - 月线：按自然月聚合
- 字段口径：
  - `open`：周期首日开盘
  - `high`：周期内最高
  - `low`：周期内最低
  - `close`：周期末日收盘
  - `volume`：周期内成交量求和
  - `turnover`：周期内成交额求和
  - `prev_close`：聚合后按前一根 K 线 close 回填
- 区间语义：
  - `limit` 在聚合后应用
  - `start_date/end_date` 指定区间时，边界周/月可能是不完整周期
  - usecase 会在 `meta` 输出：`derived_from / aggregation / limit_applied_after_aggregation / partial_period_at_range_edges`

### stock_history(index) 多周期输入别名支持
- 已支持输入：`5/15/30/60/d/w/m/y`
- **当前不支持 `1m`；仅支持从 `5m` 起的分钟级周期**
- 内部标准化映射：
  - `5 -> 5m`
  - `15 -> 15m`
  - `30 -> 30m`
  - `60 -> 60m`
  - `d -> 1d`
  - `w -> 1w`
  - `m -> 1M`
  - `y -> 1y`
- 与既有格式 `5m/15m/30m/60m/1d/1w/1M/1y` 兼容

### technical_indicator 多指标 / 多周期输入别名支持
- 已支持指标：`macd / ma / boll / kdj`（大小写不敏感，统一转小写）
- 已支持周期输入：`5/15/30/60/d/w/m/y`
- **当前不支持 `1m`；仅支持从 `5m` 起的分钟级周期**
- 内部标准化映射：
  - `5 -> 5m`
  - `15 -> 15m`
  - `30 -> 30m`
  - `60 -> 60m`
  - `d -> 1d`
  - `w -> 1w`
  - `m -> 1M`
  - `y -> 1y`
- 与既有格式 `5m/15m/30m/60m/1d/1w/1M/1y` 兼容

### stock_quote(stock-main) 双源路由定稿
- 路由策略：`zhitu` 主，`akshare` 备
- 适用范围：`stock` 且非 `BJ`、非 `688`（即 A 股主板/常规沪深股票）
- **北交所 stock_quote 现已增加 akshare fallback：**
  - 路由策略：`zhitu` 主，`akshare` 备
  - AKShare 走 `stock_bj_a_spot_em()` 全表拉取 + 本地代码过滤
  - 内置 10 秒 TTL 缓存，避免频繁拉全表
  - 字段通过 `adapt_akshare_quote_row` 映射到统一 `Quote` 模型
- 维持既有策略：
  - `index/fund`：`zhitu` 主，`akshare` 备
  - `stock-bj`：`zhitu` 主，`akshare` 备（新增）
  - `stock-star(688)`：`zhitu` 主（无备）
- `provider_preference` 已生效：
  - 支持按请求显式指定优先顺序（如 `['akshare','zhitu']`）
  - 顺序即执行顺序，自动 fallback

### market_pool 类型扩充
- 标准类型仍为：`limit_up / limit_down / strong`
- `trade_date` 为空时：
  - 若当天是交易日，使用当天
  - 若当天不是交易日，自动回退到上一个有效交易日
- 返回中补充：
  - `requested_trade_date`
  - `meta.calendar.requested_is_trading_day`
  - `meta.calendar.effective_trade_date`
  - `meta.calendar.adjusted_to_previous_trading_day`
- 新增可用别名：
  - `ztgc / up / 涨停` -> `limit_up`
  - `dtgc / down / 跌停` -> `limit_down`
  - `qsgc / 强势` -> `strong`
- 兼容现有 provider 路径映射，不影响旧调用

### market_brief（一键市场简报 / 复盘增强）
- 聚合接口：组合 `market_overview/历史指数日线 + market_pool + trading_calendar`
- 支持两种模式：
  - `trade_date` 为空：实时模式
  - `trade_date` 非空：复盘模式
- 复盘模式特性：
  - 先通过 `trading_calendar` 解析有效交易日
  - 若传入非交易日，自动回退到上一个交易日
  - 指数概览改为通过指数 `stock_history(index, 1d)` 重建，不再读取当前实时行情
- 支持参数：
  - `brief_type`: `pre_open / intraday / close`
  - `trade_date`: 可选，默认当天
  - `include_pools`: 是否包含股池摘要
  - `top_n`: 股池展示条数
- 已与 `sector_review` 对齐到统一 `review_envelope_v1`
  - 新增统一字段：`subject_type / subject_name / stats / benchmark_summary / continuity / rotation / rankings / buckets / items`
  - `leaders / laggards` 改为同一类 review item-card
  - `meta.review_envelope_schema / meta.sentiment_score_schema / meta.rotation_score_schema` 明确暴露
- 输出包含：
  - 指数概览数据（兼容字段：`overview`）
  - 指数强弱排序（兼容字段：`index_ranking`）
  - 市场宽度摘要：`breadth`
  - 情绪温度：`sentiment`（与 `sector_review` 共用 `sentiment_temperature_v1`）
  - 市场结构：`structure`
  - 市场轮动：`rotation`
  - 关键高亮（兼容字段：`highlights`）
  - 股池统计（兼容字段：`pools`）
  - 统一榜单与分层：`leaders / laggards / rankings / buckets / items`
  - 可直接给 newsbot 使用的 `summary` 文本
  - `meta.review_mode / meta.calendar / meta.overview / meta.pools`

## 已验证通过（智兔主链路）
- 指数实时行情
- 基金实时行情
- 科创板实时行情
- 北交所指数实时行情
- 指数历史日线
- 北证50 历史回退已补齐（AKShare index history fallback）
- MACD 技术指标
- 市场概览
- 涨停股池
- 科创板五档盘口

## AKShare 现状
- 股票搜索：可用
- Eastmoney 历史接口：失败（远端直接断开）
- 腾讯历史接口：已验证可用，作为股票历史替代实现
- 股票历史当前通过腾讯历史接口恢复可用
- 指数历史 fallback 已增强：AKShare 现支持 `index_zh_a_hist` 的 `1d/1w/1M`，用于补齐北证50等指数历史覆盖
- 已增强字段完整度：
  - `volume`：优先通过 `stock_zh_a_daily` 按日期回填
  - `prev_close`：按前一条 bar 的 `close` 推导；已通过前推 start_date 10 个自然日确保首条 prev_close 可填充（仅上市首日仍为空）
  - `turnover`：统一为成交额口径（`stock_zh_a_daily.amount` 优先）

## 当前建议

### 当前主交付路径
以 **智兔** 作为主 provider：
- 普通沪深股票实时
- 指数实时 / 历史 / 技术指标
- 基金实时
- 北交所 / 科创板实时
- 市场概览
- 股池
- 盘口
- 板块列表 / 成员股

### 当前补充路径
以 **AKShare** 作为补充 provider：
- 搜索
- 股票历史（腾讯历史接口 + 字段增强）
- 指数历史 fallback
- 交易日历 / 复盘日期辅助

## 已知限制
1. AKShare 股票历史字段仍依赖上游可用性与口径
2. `stock_history(stock)` 中首条 `prev_close` 已通过前推 start_date 填充；仅上市首日仍为空
3. `sector_lookup(children/members)` 依赖智兔一级板块名称；无效板块名会返回空列表
4. `market_pool` 少量记录可能含上游异常值，当前已通过 `extra.data_quality / anomaly_flags` 标记可疑数据
5. `1m` 周期当前未实现；需等可靠 provider 明确后再开放
6. 智兔多 token 已支持 `429` 自动切换，但当前只做了最小冷却策略，尚未做更细粒度的配额统计与长期调度
7. `sector_rotation_review` 当前虽已补充受控并发与共享缓存，但 live 请求在较大板块数或较大 `limit` 下仍会明显变慢
8. 科创板 `stock_quote` 当前仍为 `zhitu` 单源（AKShare `stock_kc_a_spot_em()` 当前环境不稳定，待验证后补 fallback）
9. `stock_orderbook` / `stock_profile` / `event_calendar` 仍为 `zhitu` 单源
10. ~~`margin_trading` 静默吞错~~ → 已修复（P0），现返回 `partial_failure` + `errors`
11. ~~`limit_stat` 跌停数获取失败静默当 0~~ → 已修复（P1），现返回 `partial_failure` + `errors`
12. ~~`multi_timeframe_review` 指标获取失败静默跳过~~ → 已修复（P1），现记录 indicator errors 并真实反映 `partial_failure`
13. ~~`index_compose` 权重接口降级无标记~~ → 已修复（P1），现返回 `used_fallback_endpoint` + `endpoint_note`

## 仍待处理
1. 增强 token alias / 多 token 选择策略
2. 继续补自动化测试与发布前验收样例
3. 如有需要，继续增强 AKShare 股票历史字段完整度
4. 如需继续增强 `sector_rotation_review` 的实用性，优先考虑更细粒度 benchmark 复用、轻量化个股复盘路径


### stock_candidate_scan（二轮增强）
- 新增过滤参数：`min_up_streak`、`max_down_streak`、`require_source_tags`、`exclude_risk_flags`、`must_have_reason_tags`、`exclude_reason_tags`
- 新增解释字段：`candidate_score_breakdown`（分项得分 + total）
- 保持原有接口兼容（老参数全部可继续使用）

### macro_indicator（宏观经济指标）
- 新增 `macro_indicator` tool
- 当前 provider：`akshare`
- 支持 4 个 region：`cn` / `usa` / `euro` / `global`
- 支持 4 种 include 模式：
  - `latest`：最新值 + 预期差（beat/miss/in_line）
  - `history`：最近 N 期序列
  - `calendar`：近期待公布事件（actual=None 且有 forecast/previous）
  - `overview`：一地区核心指标快照（cn: 10个/usa: 6个/euro: 3个）
- 输入契约：`MacroIndicatorRequest`
  - `indicator`：指标标识（cpi/ppi/pmi/gdp/lpr/m2/credit/exports/imports/fx_reserves/rrr/non_farm/jobless/rate/bdi/gold 等）
  - `region`：cn/usa/euro/global
  - `include`：latest/history/calendar/overview
  - `history_n`：history 模式取最近 N 期（默认 12）
  - `start_date / end_date`：可选日期范围过滤
- AKShare 宏观接口返回结构分 4 类：
  - format=A：标准金融日历格式 `[商品, 日期, 今值, 预测值, 前值]`
  - format=A2：美国部分接口微调 `[时间, 发布日期, 现值, 前值]`
  - format=B：NBS 宽表，每个接口列名不同，需配置 `b_date_col / b_value_col`
  - format=C：特殊结构（如 LPR `[TRADE_DATE, LPR1Y, LPR5Y, ...]`），需配置 `c_col_map`
- 通过 `INDICATOR_REGISTRY` 映射表统一管理，扩展只改映射表不改 tool 契约
- 输出包含：
  - `latest`：MacroDataPoint(date, actual, forecast, previous, surprise)
  - `history`：list[MacroDataPoint]
  - `calendar`：list[MacroCalendarItem]
  - `overview`：dict[str, MacroOverviewItem]
  - `summary`：可读文本摘要
- 当前已注册指标：cn 16 个 / usa 8 个 / euro 3 个 / global 2 个 = 29 个
- added models: `MacroDataPoint`, `MacroCalendarItem`, `MacroOverviewItem`, `MacroIndicatorResult`, `MacroEntry`, `INDICATOR_REGISTRY`, `OVERVIEW_PRESETS` in `app/models/macro.py`
- added `akshare_macro_adapters` with 4 format normalizers + calendar/overview/summary builders
- added `AKShareProvider.get_macro_raw()` method
- added `MacroIndicatorUseCase` with overview preset aggregation
- added `macro_indicator` to provider router → akshare
- added MCP tool registration
- added tests: `test_akshare_macro_adapters.py` (27 tests)

### dragon_tiger（龙虎榜明细）
- 新增 `dragon_tiger` tool
- 当前 provider：`akshare`
- 支持 5 种 include 模式：
  - `daily_detail`：日龙虎榜明细（上榜股+买卖额+上榜原因+解读+上榜后1/2/5/10日涨跌）
  - `institution`：机构买卖统计（买方/卖方机构数/机构净买额/占比）
  - `active_broker`：活跃营业部（席位名/买卖金额/买入股票列表）
  - `broker_rank`：营业部胜率排行（上榜后1/2/5/10天平均涨幅+上涨概率，按时间段聚合）
  - `stock_stat`：个股上榜统计（上榜次数/净买额/后市统计，按时间段聚合）
- 输入契约：`DragonTigerRequest`
  - `include`：daily_detail/institution/active_broker/broker_rank/stock_stat
  - `trade_date` / `start_date + end_date`：A 类接口日期范围
  - `period`：近一月/近三月/近六月/近一年（B 类接口时间段）
  - `sort_by`：net_buy_amount/turnover_amount/buy_amount/inst_net_buy/listed_count
  - `descending` / `top_n`
- 输出包含：
  - `daily_detail`：list[DailyDetailItem]（symbol/name/买卖额/上榜原因/解读/后市涨跌）
  - `institution`：list[InstitutionItem]（机构参与明细）
  - `active_broker`：list[ActiveBrokerItem]（席位动向）
  - `broker_rank`：list[BrokerRankItem]（胜率排行）
  - `stock_stat`：list[StockStatItem]（个股上榜统计）
  - `summary`：可读文本摘要
- AKShare 接口：
  - `stock_lhb_detail_em` → daily_detail
  - `stock_lhb_jgmmtj_em` → institution
  - `stock_lhb_hyyyb_em` → active_broker
  - `stock_lhb_yybph_em` → broker_rank
  - `stock_lhb_stock_statistic_em` → stock_stat
- added models: DailyDetailItem, InstitutionItem, ActiveBrokerItem, BrokerRankItem, StockStatItem, DragonTigerResult
- added `akshare_dragon_tiger_adapters` with 5 adapt functions + summary builder
- added `AKShareProvider` methods: get_dragon_tiger_daily/institution/active_broker/broker_rank/stock_stat
- added `DragonTigerUseCase` with sort/top_n support
- added `dragon_tiger` to provider router → akshare
- added MCP tool registration
- added tests: `test_akshare_dragon_tiger_adapters.py` (12 tests)

### etf_snapshot（ETF 行情快照）
- 新增 `etf_snapshot` tool
- 当前 provider：`akshare`
- 支持 3 种 include 模式：
  - `spot`：全市场 ETF 实时行情快照（IOPV/基金折价率/主力净流入/份额/市值）
  - `scale`：上交所 ETF 份额规模
  - `nav`：ETF 净值序列（单位净值/累计净值/日增长率）
- 输入契约：`ETFSnapshotRequest`
  - `include`：spot/scale/nav
  - `symbol`：单只 ETF 代码（nav 模式必填）
  - `sort_by`：turnover/change_percent/discount_rate/main_net_inflow/volume/total_market_cap
  - `descending` / `top_n`（默认 20）
  - `min_discount` / `max_discount`：折溢价率筛选
  - `history_n`：nav 模式取最近 N 期（默认 30）
- 输出包含：
  - `spot`：list[ETFSpotItem]（IOPV/折价率/主力资金流/份额/市值）
  - `scale`：list[ETFScaleItem]（份额/类型/日期）
  - `nav`：list[ETFNAVItem]（净值/累计净值/日增长率）
  - `summary`：可读文本摘要
- AKShare 接口：
  - `fund_etf_spot_em` → spot（~1400+ ETF 全市场快照）
  - `fund_etf_scale_sse` → scale
  - `fund_etf_fund_info_em` → nav
- added models: ETFSpotItem, ETFScaleItem, ETFNAVItem, ETFSnapshotResult
- added `akshare_etf_snapshot_adapters` with 3 adapt functions + summary builder
- added `AKShareProvider` methods: get_etf_spot_em/get_etf_scale_sse/get_etf_nav
- added `ETFSnapshotUseCase` with sort/filter/discount screening
- added `etf_snapshot` to provider router → akshare
- added MCP tool registration
- added tests: `test_akshare_etf_snapshot_adapters.py` (8 tests)

### convertible_bond（可转债）
- 新增 `convertible_bond` tool
- 当前 provider：`akshare`
- 支持 3 种 include 模式：
  - `spot`：集思录可转债实时快照（现价/涨跌幅/正股/转股价/转股价值/转股溢价率/债券评级/双低/到期税前收益/剩余年限/剩余规模）
  - `redeem`：强赎监控（强赎天计数/强赎触发价/强赎状态/最后交易日）
  - `index`：可转债等权指数历史
- 输入契约：`ConvertibleBondRequest`
  - `include`：spot/redeem/index
  - `sort_by`：double_low/conv_premium/ytm/change_percent/turnover/remaining_years（默认 double_low 升序）
  - `descending` / `top_n`
  - `min_double_low` / `max_double_low`：双低区间筛选
  - `max_conv_premium`：溢价率上限筛选
  - `min_ytm`：到期收益率下限筛选
  - `call_status_filter`：all/called/near_call/safe（强赎状态筛选）
  - `history_n`：index 模式取最近 N 期（默认 60）
- 输出包含：
  - `spot`：list[CBSpotItem]（双低/溢价率/YTM/评级/转股价值等）
  - `redeem`：list[CBRedeemItem]（强赎天计数/强赎状态/最后交易日）
  - `index`：list[CBIndexPoint]（等权指数历史）
  - `summary`：可读文本摘要
- AKShare 接口：
  - `bond_cb_jsl` → spot（集思录快照）
  - `bond_cb_redeem_jsl` → redeem（强赎监控）
  - `bond_cb_index_jsl` → index（等权指数）
- added models: CBSpotItem, CBRedeemItem, CBIndexPoint, ConvertibleBondResult
- added `akshare_convertible_bond_adapters` with 3 adapt functions + summary builder
- added `AKShareProvider` methods: get_cb_spot/get_cb_redeem/get_cb_index
- added `ConvertibleBondUseCase` with double-low sort/filter + call-status screening
- added `convertible_bond` to provider router → akshare
- added MCP tool registration
- added tests: `test_akshare_convertible_bond_adapters.py` (9 tests)

### derivatives_data（期货/期权）
- 新增 `derivatives_data` tool
- 当前 provider：`akshare`
- 支持 4 种 include 模式：
  - `futures_spot`：期货主力合约实时快照（价格/持仓/涨跌幅）
  - `futures_hist`：期货合约历史日线（含持仓量/结算价）
  - `option_list`：期权合约列表（SSE/SZSE，含行权价/合约单位/到期日/持仓）
  - `qvix`：期权隐含波动率指数（支持 50ETF/300ETF/500ETF/50指数/300指数/1000指数/科创板/创业板）
- 输入契约：`DerivativesDataRequest`
  - `include`：futures_spot/futures_hist/option_list/qvix
  - `futures_symbol`：期货合约代码（默认 RB0=螺纹钢主力）
  - `option_exchange`：SSE/SZSE/both
  - `qvix_underlying`：50etf/300etf/500etf/100etf/50index/300index/1000index/kcb/cyb
  - `option_type_filter`：all/call/put
  - `history_n`：历史期数（默认 60）
- 输出包含：
  - `futures_spot`：list[FuturesSpotItem]
  - `futures_hist`：list[FuturesHistItem]（含持仓量/结算价）
  - `option_list`：list[OptionContractItem]（SSE+SZSE）
  - `qvix`：list[QVIXItem]
  - `summary`：可读文本摘要
- AKShare 接口：
  - `futures_zh_realtime` → futures_spot
  - `futures_zh_daily_sina` → futures_hist
  - `option_current_day_sse/szse` → option_list
  - `index_option_*_qvix` → qvix（9 个标的）
- 注意：EM 期权接口(option_current_em)当前代理不稳定，使用 SSE/SZSE 官方接口替代
- added models: FuturesSpotItem, FuturesHistItem, OptionContractItem, QVIXItem, DerivativesDataResult
- added `akshare_derivatives_data_adapters` with 5 adapt functions + summary builder
- added `AKShareProvider` methods: get_futures_spot/get_futures_hist/get_option_list_sse/szse/get_qvix
- added `DerivativesDataUseCase`
- added `derivatives_data` to provider router → akshare
- added MCP tool registration
- added tests: `test_akshare_derivatives_data_adapters.py` (10 tests)

### margin_trading（融资融券）
- 新增 `margin_trading` tool
- 当前 provider：`akshare`
- 支持 2 种 include 模式：
  - `summary`：两市融资融券汇总（融资余额/融资买入额/融券余量/融券卖出量/两融余额）
  - `detail`：个股融资融券明细（融资余额/买入额/偿还额/融券余量/卖出量）
- 输入契约：`MarginTradingRequest`
  - `include`：summary/detail
  - `trade_date` / `start_date + end_date`：日期范围（SSE 汇总支持区间，SZSE/明细为单日）
  - `exchange`：SSE/SZSE/both
  - `sort_by`：financing_buy/financing_balance/securities_sell/securities_volume
  - `descending` / `top_n`
- 输出包含：
  - `summary`：list[MarginSummaryItem]（按日期+交易所）
  - `detail`：list[MarginDetailItem]（个股明细，支持排序截断）
  - `summary_text`：可读文本摘要
  - `partial_failure`：bool，部分交易所数据获取失败时为 True
  - `errors`：list，失败的 exchange+section+error_code+message（对齐项目其他 tool 的 partial_failure 模式）
- AKShare 接口：
  - `stock_margin_sse` → SSE 汇总（支持日期区间）
  - `stock_margin_szse` → SZSE 汇总（单日）
  - `stock_margin_detail_sse` → SSE 个股明细（单日）
  - `stock_margin_detail_szse` → SZSE 个股明细（单日）
- 注意：SZSE 汇总单位为亿元，SSE 为元；SSE 明细含融资偿还额/融券偿还额，SZSE 含融券余额/两融余额
- added models: MarginSummaryItem, MarginDetailItem, MarginTradingResult
- added `akshare_margin_trading_adapters` with 4 adapt functions + summary builder
- added `AKShareProvider` methods: get_margin_sse/szse_summary/detail
- added `MarginTradingUseCase` with SSE/SZSE dual-exchange + sort/top_n
- added `margin_trading` to provider router → akshare
- added MCP tool registration
- added tests: `test_akshare_margin_trading_adapters.py` (9 adapter tests + 3 partial_failure usecase tests)
