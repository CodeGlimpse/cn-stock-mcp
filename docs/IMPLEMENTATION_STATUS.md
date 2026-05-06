# 实现状态说明

更新时间：2026-05-06

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
- 支持两种模式：
  - `trade_date`：单日板块复盘
  - `start_date + end_date`：区间板块复盘
- 支持参数：
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
  - v1 先只支持 `sector_type=primary`
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
- 维持既有策略：
  - `index/fund`：`zhitu` 主，`akshare` 备
  - `stock-bj`：`zhitu` 主（无备）
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
  - `prev_close`：按前一条 bar 的 `close` 推导（首条为空）
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
2. `stock_history(stock)` 中首条 `prev_close` 可能为空（无前序数据）
3. `sector_lookup(children/members)` 依赖智兔一级板块名称；无效板块名会返回空列表
4. `market_pool` 少量记录可能含上游异常值，当前已通过 `extra.data_quality / anomaly_flags` 标记可疑数据
5. `1m` 周期当前未实现；需等可靠 provider 明确后再开放
6. 智兔多 token 已支持 `429` 自动切换，但当前只做了最小冷却策略，尚未做更细粒度的配额统计与长期调度
7. `sector_rotation_review` 当前虽已补充受控并发与共享缓存，但 live 请求在较大板块数或较大 `limit` 下仍会明显变慢

## 仍待处理
1. 增强 token alias / 多 token 选择策略
2. 继续补自动化测试与发布前验收样例
3. 如有需要，继续增强 AKShare 股票历史字段完整度
4. 如需继续增强 `sector_rotation_review` 的实用性，优先考虑更细粒度 benchmark 复用、轻量化个股复盘路径，以及概念板块支持边界
