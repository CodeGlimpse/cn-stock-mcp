# 实现状态说明

更新时间：2026-05-02

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
- `trading_calendar`
- `market_overview`
- `technical_indicator`
- `market_pool`
- `stock_orderbook`
- `sector_lookup`
- `provider_health`

### sector_lookup（板块列表/层级）当前实现
- 输入模式：`list | children | members(兼容别名)`
- `list + concept`：调用 `/hs/list/sectors`（概念板块列表）
- `list + primary`：调用 `/hs/list/primary`（一级板块列表）
- `children` / `members`：调用 `/hs/sectors/{sector_name}`（层级查询：一级板块下属板块）
- `SectorLookupRequest` 增加参数校验：
  - `mode=list` 默认 `sector_type=concept`
  - `mode=children` 默认 `sector_type=primary`
  - `mode in {members, children}` 时强制要求 `sector_name`

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
- 输出包含：
  - 指数概览数据
  - 指数强弱排序：`index_ranking`
  - 市场宽度摘要：`breadth`
  - 情绪温度：`sentiment`
  - 关键高亮：`highlights`
  - 股池统计（涨停/跌停/强势）
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
- 实时行情
- 指数历史
- 技术指标
- 市场概览
- 股池
- 盘口
- 板块列表/层级

### 当前补充路径
以 **AKShare** 作为补充 provider：
- 搜索
- 股票历史（腾讯历史接口 + 字段增强）
- 交易日历 / 复盘日期辅助

## 已知限制
1. AKShare 股票历史字段仍依赖上游可用性与口径
2. `stock_history(stock)` 中首条 `prev_close` 可能为空（无前序数据）
3. `sector_lookup` 的 `children/members` 语义依据智兔文档推断为“一级板块下属板块”，建议后续做一次在线样本验收固化

## 仍待处理
1. 增强 token alias / 多 token 选择策略
2. 增加自动化测试
3. 如有需要，继续增强 AKShare 股票历史字段完整度
4. 为 `sector_lookup` 增补自动化测试与线上回归样例
