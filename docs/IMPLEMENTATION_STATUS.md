# 实现状态说明

更新时间：2026-05-01

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
- `provider_health`

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

### 当前补充路径
以 **AKShare** 作为补充 provider：
- 搜索
- 股票历史（腾讯历史接口 + 字段增强）

## 已知限制
1. AKShare 股票历史字段仍依赖上游可用性与口径
2. `stock_history(stock)` 中首条 `prev_close` 可能为空（无前序数据）

## 仍待处理
1. 增强 token alias / 多 token 选择策略
2. 增加自动化测试
3. 如有需要，继续增强 AKShare 股票历史字段完整度
