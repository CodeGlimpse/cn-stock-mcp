# review_envelope_v1

## 1. 统一顶层字段

`market_brief` 与 `sector_review` 统一优先消费这些字段：

- `subject_type`
- `subject_name`
- `mode`
- `trade_date`
- `requested_trade_date`
- `start_date`
- `end_date`
- `member_count`
- `reviewed_count`
- `breadth`
- `stats`
- `sentiment`
- `benchmark_summary`
- `continuity`
- `rotation`
- `structure`
- `leaders`
- `laggards`
- `rankings`
- `buckets`
- `items`
- `summary`
- `partial_failure`
- `errors`

## 2. item-card 统一结构

`leaders / laggards / items / rankings.* / buckets.*` 中的卡片尽量按同一结构解释：

- `symbol`
- `name`
- `mode`
- `trade_date`
- `start_date`
- `end_date`
- `close`
- `relative_strength`
- `return`
- `max_drawdown`
- `volume_ratio`
- `tags`
- `benchmark`
- `stats`
- `summary`
- `source`

## 3. sentiment 统一语义

读取 `meta.sentiment_score_schema`，当前实现为：

- `schema = sentiment_temperature_v1`
- `score ∈ [-5, 5]`
- `normalized_score ∈ [0, 100]`
- 值越大越强

标签阈值：

- `hot / 偏热`: `score >= 3.0`
- `warm / 偏强`: `1.5 <= score < 3.0`
- `neutral / 中性`: `-1.0 < score < 1.5`
- `cool / 偏弱`: `-2.5 < score <= -1.0`
- `cold / 偏冷`: `score <= -2.5`

## 4. rotation 不是 sentiment

读取 `meta.rotation_score_schema`，当前实现为：

- `schema = rotation_signal_v1`
- `rotation.score` 是**轮动/结构信号分**
- 不能当作情绪温度分解释
- 必须结合：
  - `rotation.label`
  - `rotation.label_zh`
  - `structure.tags`
  - `continuity`
  - `benchmark_summary`

## 5. market_brief 的兼容字段

`market_brief` 仍保留这些补充字段：

- `overview`
- `index_ranking`
- `highlights`
- `pools`

使用原则：

1. **先解释公共 envelope 字段**
2. 再用这些兼容字段补细节
3. 不要让下游逻辑主依赖兼容字段

## 6. 不适用字段处理

统一约定：

- 不适用时返回 `null`
- 或空数组 `[]`
- 或 `applicable=false`
- **不要**因为字段空就推断为“没有风险 / 没有轮动 / 没有基准”

对 `market_brief` 当前尤其注意：

- `benchmark_summary` 可能只是占位不适用
- `continuity` 可能只是占位不适用
- `rotation` 可用，但语义是市场级轮动摘要
