# Output rules

## 1. 统一输出优先级

### `market_brief`
优先说：
1. `sentiment`
2. `structure`
3. `leaders / laggards`
4. `rotation`
5. 再补 `highlights / pools / overview`

### `sector_review(trade_date_review)`
优先说：
1. `sentiment`
2. `stats.avg_return / stats.avg_relative_strength`
3. `leaders / laggards`
4. `structure.tags`

### `sector_review(range_review)`
优先说：
1. `rotation.label_zh`
2. `structure.tags`
3. `benchmark_summary`
4. `continuity`
5. 再补 `leaders / laggards`

### `sector_rotation_review`
优先说：
1. `rotation.label_zh`
2. `rankings`（尤其 `leaders_by_avg_relative_strength / leaders_by_avg_return`）
3. `buckets`（如 `mainline_sectors / risk_sectors`）
4. `structure.tags`
5. 再补各板块 `leaders / laggards`

### `stock_review / stock_review_batch`
优先说：
- 收益
- 相对强弱
- 回撤
- 量比
- tags / groups

### `stock_candidate_scan`
优先说：
- `candidate_score / candidate_label`
- `reason_tags / risk_flags`
- `rankings`（尤其 `leaders_by_candidate_score`）
- `buckets`（`candidates / watchlist / risk_alerts`）
- 再补基础收益 / 相对强弱 / 回撤 / 量比

## 2. 日期解释规则

如果：
- `requested_trade_date != trade_date`

必须明确写：
- 用户请求日期
- 实际采用的有效交易日
- 原因是“非交易日自动回退”

## 3. 失败处理

- `INVALID_ARGUMENT`：改 payload，不要原样重试
- `EMPTY_RESULT`：常见于板块名无效、成员为空、筛选后无结果
- `PROVIDER_*`：最多重试 1 次，或换源
- `partial_failure=true`：输出成功项，并列出失败项
- `provider_health` 只用于诊断，不用于常规回答

## 4. 风险提示

- `market_pool` 若存在 `extra.data_quality == "suspect"` 或 `anomaly_flags`，必须提示上游异常值风险
- `sector_lookup(children)` 要明确写“成员股”，不要写“子板块”
- `sector_rotation_review` 的 `items` 是板块卡片，不是个股卡片；不要按股票字段去解读。
- `rotation.score` 不能写成“情绪分”
- 看到空字段时，不要脑补“没有问题”

## 5. 表达风格

- 面向 news agent：**先结论，后证据，再观察点**
- 区分：
  1. 工具返回的事实
  2. 基于事实的解读
- 当工具返回结构已经足够明确时，直接给结论，不要重复字段名堆砌
