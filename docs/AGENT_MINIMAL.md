# Agent Minimal Guide (`cn-stock-mcp`)

给 AI agent 的最小入口。目标：**少读文档、少试错、少放大 payload、少浪费 token。**

## 1) 默认策略

1. 先选最轻 tool，再升级到更重 tool。
2. 默认小参数：`limit/top_n=3~5`；只有用户要求更全覆盖时再放大。
3. 名称不确定先 `stock_search`，不要直接猜 symbol/sector。
4. 非诊断场景不要先跑 `provider_health`。
5. `children/members` 必须显式传 `sector_type=primary|concept`。

## 2) 首发工具档与风险边界

`--init-config` 默认使用 `retail_v1_preview`，只可调用：

`stock_search`、`market_brief`、`stock_snapshot`、`stock_quote`、`stock_history`、`stock_review`、`watchlist_review`、`trading_calendar`、`sector_review`、`hot_theme_tracker`。

调用列表外工具前，先确认用户已启用 `tool_profile=full`；收到 `TOOL_NOT_FOUND` 时不要猜测或重复调用。回答必须保留数据来源、时间/新鲜度、fallback 或 partial failure 信息，并明确“仅供数据参考，不构成投资建议”；不得给出荐股、买卖指令、收益承诺或个性化风险建议。

## 3) 高频意图最短路由

- 市场简报 / 收盘复盘 → `market_brief`
- 热点主线 → `hot_theme_tracker`
- 单板块复盘 → `sector_review`
- 多板块比较 → `sector_rotation_review`
- 单股复盘 → `stock_review`
- 实时价格 → `stock_quote`
- 历史走势 → `stock_history`
- 技术指标 → `technical_indicator`
- 轻量股池快照 → `market_pool`
- 板块成员 → `sector_lookup`
- 代码检索 → `stock_search`

## 4) 低 token 调用习惯

### `sector_review`
- 默认 `top_n=3`, `limit=5`
- 用户只问一个板块，不要升级到 `sector_rotation_review`

### `sector_rotation_review`
- 默认先 `limit=3~5`
- 如果只要板块级结论，优先考虑 `skip_member_detail=true`

### `stock_candidate_scan`
- universe 尽量收窄：先 symbols / 少量 sector / 单个 pool
- 不要一开始就全市场扫描

### `watchlist_review`
- 只传用户真的关心的 symbols
- 不要为了“更完整”擅自扩大池子

### `market_pool`
- 轻量实时快照优先
- 不要为了回答简单涨停问题直接升级到 `limit_up_pool`

## 5) 最容易踩坑的契约

### `sector_lookup`
- `mode=list, sector_type=concept` → 概念板块列表
- `mode=list, sector_type=primary` → 一级板块列表
- `mode=children|members` → **成员股列表**，不是子板块
- `mode=children|members` 时：**必须传 `sector_type`**

正确示例：
```json
{"mode":"children","sector_type":"primary","sector_name":"银行","limit":20}
```

错误示例：
```json
{"mode":"children","sector_name":"银行","limit":20}
```

## 6) 需要更多信息时再读

- 最小调用示例：`docs/EXAMPLES_MINIMAL.md`
- 部署/挂载：`docs/INTEGRATION.md`
- 协议/参数：`docs/INTERFACE_SCHEMA.md`
- 运行事实与限制：`docs/IMPLEMENTATION_STATUS.md`
- 错误码：`docs/ERROR_MODEL.md`
