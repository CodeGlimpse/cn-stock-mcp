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

## 已验证通过（智兔主链路）
- 指数实时行情
- 基金实时行情
- 科创板实时行情
- 北交所指数实时行情
- 指数历史日线
- MACD 技术指标
- 市场概览
- 涨停股池
- 科创板五档盘口

## AKShare 现状
- 股票搜索：可用
- Eastmoney 历史接口：失败（远端直接断开）
- 腾讯历史接口：已验证可用，作为股票历史替代实现
- 股票历史当前通过腾讯历史接口恢复可用
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

## 已知限制
1. AKShare 股票历史字段仍依赖上游可用性与口径
2. `stock_history(stock)` 中首条 `prev_close` 可能为空（无前序数据）
3. `sector_lookup` 的 `children/members` 语义依据智兔文档推断为“一级板块下属板块”，建议后续做一次在线样本验收固化

## 仍待处理
1. 增强 token alias / 多 token 选择策略
2. 增加自动化测试
3. 如有需要，继续增强 AKShare 股票历史字段完整度
4. 为 `sector_lookup` 增补自动化测试与线上回归样例
