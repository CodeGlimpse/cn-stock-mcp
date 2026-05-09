# openclaw-stock-mcp

面向 OpenClaw Agent 的中国证券市场行情 MCP 服务。

## 当前状态

当前已具备：
- 文档
- 领域模型
- provider 抽象
- AKShare / 智兔双源最小链路
- usecase + fallback
- MCP Python SDK（FastMCP）stdio transport
- smoke test 脚本
- provider_health 自检

## 文档导航

- `docs/README_DOCS.md`：文档总览与阅读顺序
- `docs/IMPLEMENTATION_STATUS.md`：当前实现状态与限制（事实源）
- `docs/INTERFACE_SCHEMA.md`：对外输入/输出契约与路由约束
- `docs/ERROR_MODEL.md`：统一错误码与 retry/fallback 语义
- `docs/INTEGRATION.md`：本地启动、OpenClaw 挂载与联调清单

## 当前已验证通过的能力

### 智兔主链路
- `stock_quote(index)`
- `stock_quote(fund)`
- `stock_quote(star)`
- `stock_quote(BJ index)`
- `stock_history(index)`
- `stock_history(stock)`（支持分钟级；日线以上支持复权）
- `technical_indicator(index)`
- `technical_indicator(stock)`
- `market_overview()`
- `market_pool(limit_up)`
- `market_pool(sub_new)`
- `market_pool(broken_limit)`
- `stock_orderbook(main)`
- `stock_orderbook(star)`
- `stock_profile()`（公司基本面：profile/dividends/unlocks/profits/valuation）
- `sector_quote()`（板块指数行情：primary/concept）
- `sector_leaders()`（板块龙头/跟风/拖累快照）
- `event_calendar()`（事件时间轴：dividend/unlock/profit，支持 next_event_only 盘前提醒）

### AKShare
- `stock_search()` 基本可用
- `stock_history(stock)` 已改走 **腾讯历史接口**，当前可用
- `stock_history(index)` 在 Zhitu 不可用或北证50等边角场景下，已具备 **AKShare index history fallback**
- `trading_calendar()` 交易日历 / 复盘日期辅助可用
- `stock_review()` 个股复盘摘要可用
- `stock_review_batch()` 批量复盘排序可用
- `sector_rotation_review()` 多板块横向轮动复盘可用（当前建议 primary 板块；live 验收已通过最小规模样例）
- `stock_candidate_scan()` 候选扫描可用（支持 symbols / primary 板块 / strong池 组合成 universe）
- `watchlist_review()` 观察池复盘可用（适合持续跟踪固定股票池）
- `multi_timeframe_review()` 多周期复盘可用（适合看单只标的不同周期是否共振或冲突）
- `hot_theme_tracker()` 热点主线跟踪可用（复用板块轮动 + 股池快照）
- `capital_flow()` 资金流向可用（market/individual/industry/concept）
- `stock_financial()` 财务三层数据可用（snapshot/history/details）
- `limit_stat()` 短线情绪统计可用（封板率/连板分布/炸板/昨涨停今继续率）
- `northbound()` 北向资金可用（当日流向/历史/持股排行）
- `valuation_rank()` 估值排名可用（市场估值温度 + 个股PE/PB排名）
- `index_compose()` 指数组成可用（成分股/权重/集中度统计）
- `industry_valuation_rank()` 行业估值分位可用（一级行业成员股 PE/PB 聚合与分位排序）

## 快速开始

### 安装依赖

```bash
pip install -e .
```

### 开发环境安装（推荐）

```bash
# 方式1：使用 Makefile
make setup-dev

# 方式2：使用 requirements-dev
pip install -r requirements-dev.txt
```

### 运行测试

```bash
# 推荐：使用项目虚拟环境，避免系统 Python 依赖缺失
.venv/bin/python -m pytest -q -m "not live"

# 默认：仅跑稳定回归（不含 live 网络测试）
make test

# 跑全部测试（含 live）
make test-all
```

### 配置

```bash
cp .env.example .env
```

智兔 token 支持两种方式：

1. 直接写 `.env`
2. 写入 `config/zhitu_tokens.json`

说明：
- `config/zhitu_tokens.json` 支持配置多个 token
- 当前版本会按 `default` 优先顺序加载多个 token
- 当某个智兔 token 遇到 `429` 限流时，会自动尝试切换到下一个可用 token

### 列出已注册 tools

```bash
PYTHONPATH=src python -m openclaw_stock_mcp.main --list-tools
```

### 调用单个 tool

```bash
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_quote --payload '{"symbols":["000001.SH"],"sec_type":"index"}'
```

### 返回结构（统一 envelope）

`--tool` 本地调用与 MCP tool 调用的返回已统一为顶层 envelope：

```json
{
  "success": true,
  "data": {
    "items": [],
    "partial_failure": false,
    "errors": [],
    "meta": {
      "per_symbol": []
    }
  },
  "error": null,
  "meta": {
    "schema_version": "v1",
    "request_id": "req_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "tool": "stock_quote"
  }
}
```

失败场景示例（参数校验失败）：

```json
{
  "success": false,
  "data": null,
  "error": {
    "error_code": "INVALID_ARGUMENT",
    "message": "Invalid request payload",
    "retryable": false,
    "provider": null,
    "details": []
  },
  "meta": {
    "schema_version": "v1",
    "request_id": "req_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "tool": "stock_quote"
  }
}
```

详细错误码、retry 语义与调用方处理建议见：`docs/ERROR_MODEL.md`

### stock_quote(stock-main) 双源路由样例

```bash
# 默认路由（stock-main）：zhitu 主，akshare 备
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_quote --payload '{"symbols":["600519.SH"],"sec_type":"stock"}'

# 批量行情（沪深主板自动走 /hs/public/ssjymore 批量接口，最多 20 支）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_quote --payload '{"symbols":["600519.SH","000001.SZ","601318.SH"],"sec_type":"stock"}'

# 显式指定 provider_preference（先 akshare，再 zhitu）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_quote --payload '{"symbols":["600519.SH"],"sec_type":"stock","provider_preference":["akshare","zhitu"]}'
```


### trading_calendar 复盘日期辅助样例

```bash
# 单日判断：是否交易日、前后交易日、最近交易日
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool trading_calendar --payload '{"date":"2026-05-01"}'

# 区间交易日列表
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool trading_calendar --payload '{"start_date":"2026-04-27","end_date":"2026-05-08"}'
```

### stock_history(index) 多周期调用样例（5/15/30/60/d/w/m/y）

```bash
# 5分钟
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_history --payload '{"symbol":"000001.SH","sec_type":"index","interval":"5","limit":20}'

# 日线
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_history --payload '{"symbol":"000001.SH","sec_type":"index","interval":"d","limit":30}'

# 周线
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_history --payload '{"symbol":"000001.SH","sec_type":"index","interval":"w","limit":30}'

# 月线
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_history --payload '{"symbol":"000001.SH","sec_type":"index","interval":"m","limit":24}'
```

### stock_history(stock) 分钟级 / 复权样例

```bash
# 股票 5 分钟（分钟级自动按不复权请求）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_history --payload '{"symbol":"600519.SH","sec_type":"stock","interval":"5","start_date":"2026-05-07","end_date":"2026-05-07","limit":20,"adjust":"qfq"}'

# 股票日线前复权
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_history --payload '{"symbol":"600519.SH","sec_type":"stock","interval":"d","start_date":"2026-04-01","end_date":"2026-05-07","limit":30,"adjust":"qfq"}'

# 股票周线后复权
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_history --payload '{"symbol":"600519.SH","sec_type":"stock","interval":"w","start_date":"2026-01-01","end_date":"2026-05-07","limit":20,"adjust":"hfq"}'
```

说明：
- `stock_history(stock)` 当前默认优先走 **Zhitu**，`akshare` 作为 fallback。
- 分钟级（`5/15/30/60`）在 Zhitu 上**仅支持不复权**；即使传入 `qfq/hfq`，底层也会自动按 `n` 请求。
- 日线及以上支持：`none / qfq / hfq`，并映射到 Zhitu 的 `n / f / b`。

### technical_indicator 多指标 / 多周期调用样例

```bash
# MACD + 日线（d）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool technical_indicator --payload '{"symbol":"000001.SH","sec_type":"index","indicator":"macd","interval":"d","limit":30}'

# MA + 15分钟（15）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool technical_indicator --payload '{"symbol":"000001.SH","sec_type":"index","indicator":"ma","interval":"15","limit":50}'

# BOLL + 周线（w）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool technical_indicator --payload '{"symbol":"000001.SH","sec_type":"index","indicator":"boll","interval":"w","limit":40}'

# KDJ + 月线（m）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool technical_indicator --payload '{"symbol":"000001.SH","sec_type":"index","indicator":"kdj","interval":"m","limit":24}'
```

### technical_indicator(stock) 股票指标样例

```bash
# 股票日线 MACD
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool technical_indicator --payload '{"symbol":"600519.SH","sec_type":"stock","indicator":"macd","interval":"d","start_date":"2026-04-01","end_date":"2026-05-07","limit":30}'

# 股票 5 分钟 MA（分钟级仅请求不复权数据）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool technical_indicator --payload '{"symbol":"600519.SH","sec_type":"stock","indicator":"ma","interval":"15","start_date":"2026-05-07","end_date":"2026-05-07","limit":20}'
```

说明：
- `technical_indicator(stock)` 当前优先走 **Zhitu**，`akshare` 作为 fallback。
- 股票指标当前支持 `macd / ma / boll / kdj`，对应 Zhitu 股票技术指标路径。
- 分钟级指标当前仅请求 **不复权** 数据。

### market_pool 类型扩充调用样例

```bash
# 标准类型：不传 trade_date 时，自动回退到最近有效交易日
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool market_pool --payload '{"pool_type":"limit_up","limit":50}'

# 显式指定 trade_date
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool market_pool --payload '{"pool_type":"limit_up","trade_date":"2026-05-01","limit":50}'

# 类型别名：ztgc -> limit_up
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool market_pool --payload '{"pool_type":"ztgc","trade_date":"2026-05-01","limit":50}'

# 类型别名：dtgc -> limit_down
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool market_pool --payload '{"pool_type":"dtgc","trade_date":"2026-05-01","limit":50}'

# 类型别名：qsgc -> strong
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool market_pool --payload '{"pool_type":"qsgc","trade_date":"2026-05-01","limit":50}'

# 类型别名：cxgc -> sub_new
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool market_pool --payload '{"pool_type":"cxgc","trade_date":"2026-05-01","limit":50}'

# 类型别名：zbgc -> broken_limit
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool market_pool --payload '{"pool_type":"zbgc","trade_date":"2026-05-01","limit":50}'
```

### hot_theme_tracker 热点主线跟踪样例

```bash
# 显式指定主线候选板块
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool hot_theme_tracker --payload '{"sector_names":["1000信息","1000工业","1000医药"],"sector_type":"primary","trade_date":"2026-05-06","top_n":3,"member_limit":5}'

# 不指定 sector_names：自动从 primary 板块列表中截取前 N 个做热度跟踪
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool hot_theme_tracker --payload '{"sector_type":"primary","trade_date":"2026-05-06","sector_limit":8,"top_n":3}'
```

说明：
- 当前 v1 用于 **主线热点 / 次主线 / 风险主题** 的快速跟踪
- 内部路径：
  - `sector_lookup(list)` 解析候选板块
  - `sector_rotation_review` 生成跨板块轮动卡片
  - `market_pool(limit_up/strong)` 生成股池快照
- 输出重点：
  - `themes`（完整主题卡列表）
  - `leaders / laggards`
  - `buckets.mainline_themes / watchlist_themes / risk_themes`
  - `pool_snapshot`（涨停池 / 强势池）
  - `theme_score_schema=theme_score_v1`

### stock_review 个股复盘摘要样例

```bash
# 单日复盘：若落在非交易日，会自动回退到有效交易日
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_review --payload '{"symbol":"600519.SH","trade_date":"2026-05-01"}'

# 区间复盘：输出区间涨跌、高低点、日均成交额等
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_review --payload '{"symbol":"600519.SH","start_date":"2026-04-01","end_date":"2026-05-01"}'
```

说明：
- `trade_date` 模式：输出单日/近5日/近20日/4周/3月复盘摘要
- `start_date + end_date` 模式：输出区间收益、高低点、均量/均额等
- 返回结构含 `windows.daily / weekly / monthly`，便于后续脚本继续加工
- 增强版额外提供：
  - `volatility_pct`
  - `max_drawdown_pct`
  - `up_streak / down_streak`
  - `volume_ratio / turnover_ratio`
  - `relative_strength_pct`
  - `benchmark`（自动按股票所在市场/板块选择指数基准）

### stock_review_batch 批量复盘样例

```bash
# 批量复盘：按相对强弱排序，适合看股票池
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_review_batch --payload '{"symbols":["600519.SH","000001.SZ","300750.SZ"],"trade_date":"2026-05-01","sort_by":"relative_strength","top_n":3}'

# 区间批量复盘：按区间收益排序
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_review_batch --payload '{"symbols":["600519.SH","000001.SZ","300750.SZ"],"start_date":"2026-04-01","end_date":"2026-05-01","sort_by":"return","top_n":3}'
```

说明：
- `items` 中每一项都是一张个股复盘卡片
- 可按 `relative_strength / return / max_drawdown / volume_ratio` 排序
- 支持筛选：`min_relative_strength / min_return / max_drawdown_limit / min_volume_ratio`
- 返回附带：`tags`、`groups`、批量 `summary`
- 适合自选池、候选池、观察池的批量筛查

### market_brief 一键市场简报样例

```bash
# 收盘简报（默认，实时模式）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool market_brief --payload '{}'

# 复盘模式：指定 trade_date，自动按有效交易日生成历史市场简报
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool market_brief --payload '{"brief_type":"close","trade_date":"2026-05-01","top_n":3}'

# 不含股池，仅指数概览简报
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool market_brief --payload '{"include_pools":false}'
```

说明：
- `trade_date` 为空：走实时模式
- `trade_date` 非空：走复盘模式
- 若 `trade_date` 落在非交易日，会自动回退到上一个交易日，并在 `data.meta.calendar` 中标明
- 复盘模式下，指数概览由历史日线重建，不再直接读取当前实时行情
- `market_brief` 与 `sector_review` 现统一对齐到 `review_envelope_v1`
  - 公共顶层字段：`subject_type / subject_name / mode / trade_date / requested_trade_date / start_date / end_date / member_count / reviewed_count / breadth / stats / sentiment / benchmark_summary / continuity / rotation / structure / leaders / laggards / rankings / buckets / items / summary / partial_failure / errors / meta`
  - `market_brief` 仍保留兼容字段：`overview / index_ranking / highlights / pools`
- `sentiment` 评分语义统一为 `sentiment_temperature_v1`
  - `score`: `[-5, 5]`
  - `normalized_score`: `[0, 100]`
- `rotation.score` 与 `sentiment.score` 不同语义，单独通过 `meta.rotation_score_schema` 标明

### sector_review 板块复盘样例

```bash
# 一级行业板块复盘（默认）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_review --payload '{"sector_name":"1000信息","sector_type":"primary","trade_date":"2026-04-30","top_n":3,"limit":20}'

# 概念题材板块复盘
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_review --payload '{"sector_name":"人工智能","sector_type":"concept","trade_date":"2026-04-30","top_n":3,"limit":20}'

# 区间板块复盘：适合看一段时间的行业强弱、结构分化与轮动特征
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_review --payload '{"sector_name":"1000信息","sector_type":"primary","start_date":"2026-04-01","end_date":"2026-04-30","top_n":3,"limit":20}'
```

说明：
- `sector_type=primary`：一级行业板块（默认）
- `sector_type=concept`：概念题材板块
- 先通过 `sector_lookup(mode=children)` 获取板块成员股
- 再复用 `stock_review_batch` 生成成员股复盘卡片
- `sector_review` 现采用与 `market_brief` 相同的 `review_envelope_v1`
  - `subject_type=sector`
  - `subject_name=sector_name`
  - `leaders / laggards / items` 与 `market_brief` 统一为同一类 item-card 结构
- 返回除 `items` 外，还包含：
  - `breadth`（上涨/下跌/放量/连涨连跌分布）
  - `stats`（平均收益、相对强弱、回撤、离散度）
  - `sentiment`（偏热 / 偏强 / 中性 / 偏弱 / 偏冷；统一 `score/normalized_score` 语义）
  - `benchmark_summary`（板块成员基准分布与平均基准收益）
  - `continuity`（持续强势/弱势、连涨连跌情况）
  - `rotation`（区间模式下的轮动判断，如 `龙头驱动 / 普涨轮动 / 分化轮动`）
  - `structure`（板块结构标签，如 `broad_strength / high_dispersion / trend_divergence`）
  - `rankings`（收益/相对强弱/量比/回撤风险榜）
  - `buckets`（`leaders / followers / draggers / risk_alerts / strong_candidates / weak_candidates` 等分层）
- `rotation.score` 通过 `meta.rotation_score_schema` 单独声明，不与 `sentiment.score` 混用

### sector_quote 板块指数行情样例

```bash
# 获取概念板块指数行情（如人工智能概念）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_quote --payload '{"symbols":["101076.BKZS"],"sector_type":"concept"}'

# 获取多个板块指数行情（按涨跌幅排序，取前 5）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_quote --payload '{"symbols":["101076.BKZS","101077.BKZS"],"sector_type":"concept","sort_by":"change_percent","top_n":5}'

# 榜单筛选：成交额>=2e8，按涨跌幅排序，仅返回 top_n
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_quote --payload '{"symbols":["101076.BKZS","101077.BKZS"],"sort_by":"change_percent","top_n":3,"min_turnover":200000000,"return_mode":"ranked_only"}'
```

说明：
- `symbols`：板块指数代码（如 `101076.BKZS`）
- `sector_type`：可选 `primary`（一级行业）或 `concept`（概念题材）
- `sort_by`：可选 `change_percent`（涨跌幅）或 `turnover`（成交额）
- `descending`：是否降序，默认 `true`
- `top_n`：可选，截取前 N 条（1~50）
- `min_turnover`：可选，按最小成交额过滤
- `min_change_percent`：可选，按最小涨跌幅过滤
- `exclude_null_fields`：可选，剔除排序字段为空的项
- `return_mode`：`full`（默认，返回过滤+排序后全量）或 `ranked_only`（只返回 top_n）
- `provider`：仅支持 `zhitu`
- 返回包含：
  - `symbol`、`name`、`sector_type`
  - 价格字段：`price`、`open`、`high`、`low`、`prev_close`、`change`、`change_percent`
  - 量能字段：`volume`、`turnover`、`turnover_rate`、`amplitude`
  - 时间戳：`timestamp`

### stock_profile 公司基本面样例

```bash
# 获取公司完整基本面信息
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_profile --payload '{"symbol":"000001.SZ"}'

# 仅获取公司简介和分红历史
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_profile --payload '{"symbol":"600519.SH","include":["profile","dividends","valuation"]}'
```

说明：
- `include` 参数可选：`profile`（公司简介）、`dividends`（分红）、`unlocks`（解禁）、`profits`（季度利润）
- 返回包含：
  - `profile`：公司名称、行业、概念标签列表、经营范围、上市日期等
  - `dividends`：近年分红记录
  - `unlocks`：解禁限售计划
  - `quarter_profits`：近一年季度利润
  - `dividend_summary`：分红统计（年度、平均值）
  - `unlock_risk`：解禁风险摘要

### sector_rotation_review 板块轮动复盘样例

```bash
# 单日板块轮动复盘：横向比较多个一级板块
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_rotation_review --payload '{"sector_names":["1000信息","1000工业"],"sector_type":"primary","trade_date":"2026-05-06","top_n":1,"member_top_n":1,"limit":1}'

# 区间板块轮动复盘：适合看一段时间的强弱切换与主线集中度
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_rotation_review --payload '{"sector_names":["1000信息","1000工业","1000医药"],"sector_type":"primary","start_date":"2026-04-01","end_date":"2026-04-30","top_n":2,"member_top_n":2,"limit":3}'
```

说明：
- 当前 v1 定位为 **多个一级板块(primary) 的横向比较**，不替代单板块 `sector_review`
- 内部路径：对每个板块复用 `sector_review`，再聚合得到跨板块 `rankings / buckets / rotation / sentiment / structure`
- 顶层 `subject_type=sector_rotation`，并在 `meta.item_schema` 暴露 `sector_rotation_item_v1`
- `items` 中每一项都是一张 **板块卡片**，而不是个股卡片
- 建议排序字段：
  - `avg_relative_strength`（默认）
  - `avg_return`
  - `positive_ratio`
  - `stronger_ratio`
  - `sentiment_score`
  - `rotation_score`
- `member_top_n` 控制每个板块返回多少个 `leaders / laggards` 摘要
- 当前 live 路径仍相对较重，但已补充受控并发与共享缓存优化；验收已通过 `2 个 primary 板块 + limit=5`、`3 个 primary 板块 + limit=5`、`5 个 primary 板块 + limit=5` 的真实样例，较大 `limit` 仍建议按需逐步放大

### stock_candidate_scan 候选扫描样例

```bash
# 从 strong 池扫描候选
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_candidate_scan --payload '{"pool_type":"strong","trade_date":"2026-05-06","limit":3,"top_n":2}'

# 从多个一级板块 + 手工自选组合一个候选 universe
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_candidate_scan --payload '{"symbols":["600519.SH"],"sector_names":["1000信息","1000工业"],"sector_type":"primary","trade_date":"2026-05-06","limit":5,"top_n":3}'

# 组合精筛：来源 + 风险 + 信号标签
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_candidate_scan --payload '{"pool_type":"strong","trade_date":"2026-05-06","top_n":5,"require_source_tags":["pool:strong"],"exclude_risk_flags":["weak_relative_strength"],"must_have_reason_tags":["strong_return","active_volume"],"exclude_reason_tags":["slight_positive_return"]}'
```

说明：
- 当前 v1 用于 **从一个股票 universe 里找值得优先看的候选**，不替代 `stock_review_batch`
- universe 目前支持三种来源，可单独或组合使用：
  - `symbols[]`
  - `sector_names[]`（当前建议 `primary`）
  - `pool_type`（如 `strong / limit_up / limit_down`）
- 内部路径：
  - `sector_lookup(children)` 解析板块成员
  - `market_pool` 解析池成员
  - 合并去重后复用 `stock_review_batch` 做批量复盘
  - 再根据 `relative_strength / return / volume_ratio / drawdown / streak` 生成 `candidate_score`
- 输出重点：
  - `candidate_score / candidate_label / reason_tags / risk_flags`
  - `rankings`（候选分 / 相对强弱 / 收益 / 量比 / 回撤）
  - `buckets`（`candidates / watchlist / observe / risk_alerts`）
- 当前最适合：
  - 从强势池、候选行业、自选池里做第一轮筛查
  - 给后续 `stock_review` / `stock_review_batch` 提供优先级

### watchlist_review 观察池复盘样例

```bash
# 单日观察池复盘
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool watchlist_review --payload '{"symbols":["600519.SH","300750.SZ","000001.SZ"],"watchlist_name":"核心池","trade_date":"2026-05-06","top_n":2}'

# 区间观察池复盘
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool watchlist_review --payload '{"symbols":["600519.SH","300750.SZ","000001.SZ"],"watchlist_name":"核心池","start_date":"2026-04-01","end_date":"2026-05-06","top_n":3}'
```

说明：
- 当前 v1 用于 **固定股票池的持续跟踪和优先级划分**，不替代 `stock_review_batch`
- 内部路径：直接复用 `stock_review_batch`，再补 `watchlist_score / status_label / reason_tags / risk_flags`
- 输出重点：
  - `watchlist_score / status_label`
  - `reason_tags / risk_flags`
  - `rankings`（观察分 / 相对强弱 / 收益 / 量比）
  - `buckets`（`focus / monitor / observe / risk_alerts`）
- 当前最适合：
  - 跟踪固定观察池、自选池、核心池
  - 在“继续重点看 / 正常跟踪 / 暂时观察 / 风险警报”之间分层

### multi_timeframe_review 多周期复盘样例

```bash
# 单只指数多周期复盘
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool multi_timeframe_review --payload '{"symbol":"000001.SH","sec_type":"index","intervals":["15","d","w"],"indicators":["macd","ma","kdj"],"limit":60}'

# 单只股票多周期复盘
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool multi_timeframe_review --payload '{"symbol":"600519.SH","sec_type":"stock","intervals":["30","d","w"],"indicators":["macd","ma","kdj"],"limit":60}'
```

说明：
- 当前 v1 用于 **单只标的跨多个周期的共振/冲突分析**
- 输入重点：
  - `symbol`
  - `intervals[]`（至少 2 个）
  - `indicators[]`（默认 `macd / ma / kdj`）
- 内部路径：
  - `stock_history` 拉各周期 bars
  - `technical_indicator` 拉各周期指标
  - 再汇总成 `trend_score / trend_label / signal_tags / conflict_notes`
- 输出重点：
  - 每个周期一张 `timeframe card`
  - 顶层 `alignment_score_schema=multi_timeframe_alignment_v1`
  - `buckets` 中可直接看 `bullish_timeframes / neutral_timeframes / bearish_timeframes / conflict_points`
- 当前最适合：
  - 判断短中期是否共振
  - 判断“日线强但短线弱”这类冲突

### sector_lookup 本地调用样例（板块列表 / 成员股）

### 运行 smoke test

```bash
PYTHONPATH=src python scripts/smoke_test.py
```

### 运行 provider 自检

```bash
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool provider_health --payload '{}'
```

## 正式发布模式（OpenClaw 挂载）

推荐 MCP 配置（示例）：

```json
{
  "command": "/tmp/openclaw-stock-mcp-venv/bin/python",
  "args": [
    "-m",
    "openclaw_stock_mcp.main",
    "--stdio"
  ],
  "cwd": "/home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp",
  "env": {
    "PYTHONPATH": "src",
    "HTTP_PROXY": "",
    "HTTPS_PROXY": "",
    "ALL_PROXY": "",
    "http_proxy": "",
    "https_proxy": "",
    "all_proxy": ""
  }
}
```

挂载后建议验收顺序：

1. `provider_health {}`
2. `trading_calendar {"date":"2026-05-01"}`
3. `stock_quote {"symbols":["000001.SH"],"sec_type":"index"}`
4. `stock_history {"symbol":"600519","sec_type":"stock","interval":"1d","limit":5}`
5. `sector_lookup {"mode":"list","sector_type":"concept","limit":10}`
6. `stock_history {"symbol":"000001.SH","sec_type":"index","interval":"d","limit":20}`
7. `sector_rotation_review {"sector_names":["1000信息","1000工业"],"sector_type":"primary","trade_date":"2026-05-06","top_n":2,"member_top_n":2,"limit":5}`
8. `hot_theme_tracker {"sector_names":["1000信息","1000工业","1000医药"],"sector_type":"primary","trade_date":"2026-05-06","top_n":3,"member_limit":5}`
9. `stock_candidate_scan {"pool_type":"strong","trade_date":"2026-05-06","limit":3,"top_n":2}`
10. `watchlist_review {"symbols":["600519.SH","300750.SZ","000001.SZ"],"watchlist_name":"核心池","trade_date":"2026-05-06","top_n":2}`
11. `multi_timeframe_review {"symbol":"000001.SH","sec_type":"index","intervals":["15","d","w"],"indicators":["macd","ma","kdj"],"limit":60}`

## OpenClaw news agent integration

推荐把这套 MCP 与 `news` 专用 agent 一起使用，并采用：

- **repo 内维护 skill**
- **OpenClaw 用 `skills.load.extraDirs` 挂载**
- **`news` agent / `fernwehnewsbot` 负责市场数据与复盘场景**

### 1. repo-managed skill

本仓库内置了给 OpenClaw `news` agent 使用的 routing skill：

- `skills/newsbot-stock-routing/`

这个 skill 的职责是：

- 把 CN 市场数据 / 行情 / 复盘 / 板块轮动 / 热点主线请求路由到对应工具
- 统一解释 `review_envelope_v1`
- 约束 payload 安全规则
- 明确 `sentiment.score` 与 `rotation.score` 的不同语义

建议将它视为以下内容的唯一 source of truth：

- tool routing
- provider routing 约定
- payload 安全规则
- `market_brief` / `sector_review` 的统一输出解释方式

### 2. OpenClaw 配置示例

在 `~/.openclaw/openclaw.json` 中添加：

```json5
{
  skills: {
    load: {
      extraDirs: [
        "/home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp/skills"
      ],
      watch: true,
      watchDebounceMs: 250,
    },
    entries: {
      "newsbot-stock-routing": {
        enabled: true,
      },
    },
  },
}
```

说明：

- `extraDirs` 让 OpenClaw 从本仓库直接加载 skill
- 这样代码、schema、测试、文档、skill 可在同一 repo 内同步演进
- 不建议长期维护一个脱离 repo 的 workspace-local 复制版 skill

### 3. 推荐 agent 侧分工

推荐由 `news` agent 处理以下请求：

- 市场简报 / 收盘复盘
- 板块强弱 / 板块轮动 / 龙头跟风拖累 / 热点主线
- 单股复盘 / 股票池批量对比
- 技术指标 / 交易日 / 涨停跌停强势股池

推荐分工逻辑：

- **数据获取与结构化分析**：走 `openclaw-stock-mcp`
- **新闻背景、政策、宏观、国际比较、知识讲解**：由 `news` agent 常规研究能力补充

### 4. skill 验证命令

当你修改了 skill、OpenClaw 配置、或本仓库 schema 后，建议执行：

```bash
openclaw skills list --eligible
openclaw skills info newsbot-stock-routing
```

期望结果：

- `newsbot-stock-routing` 状态为 `Ready`
- Source 为 `openclaw-extra`
- Config requirement 中可看到：`mcp.servers.openclaw-stock-mcp`

### 5. 真实 smoke test 建议

建议至少验证这些真实路径：

1. `market_brief` 非交易日回退
   - 检查 `requested_trade_date != trade_date`
2. `sector_review` 单日复盘
   - 检查 `subject_type=sector`
   - 检查 `sentiment.score_semantics=sentiment_temperature_v1`
3. `sector_review` 区间复盘
   - 检查 `rotation.label_zh`
   - 检查 `meta.rotation_score_schema.schema=rotation_signal_v1`
4. `market_brief`
   - 检查 `meta.review_envelope_schema.schema=review_envelope_v1`
   - 检查 `leaders / laggards / buckets` 正常生成
5. `sector_rotation_review` 单日轮动复盘
   - 检查 `subject_type=sector_rotation`
   - 检查 `meta.item_schema.schema=sector_rotation_item_v1`
   - 检查 `rotation.label_zh / rankings / buckets` 正常生成
6. `stock_candidate_scan` 候选扫描
   - 检查 `subject_type=candidate_scan`
   - 检查 `meta.candidate_score_schema.schema=candidate_score_v1`
   - 检查 `candidate_score / candidate_label / buckets` 正常生成
7. `watchlist_review` 观察池复盘
   - 检查 `subject_type=watchlist`
   - 检查 `meta.watchlist_score_schema.schema=watchlist_score_v1`
   - 检查 `watchlist_score / status_label / buckets` 正常生成
8. `multi_timeframe_review` 多周期复盘
   - 检查 `subject_type=multi_timeframe`
   - 检查 `meta.alignment_score_schema.schema=multi_timeframe_alignment_v1`
   - 检查 `trend_label / conflict_points / items` 正常生成

### 6. 维护规则

当修改以下任一项时，请在同一组变更中一起审阅并更新 `skills/newsbot-stock-routing/`：

- `market_brief`
- `sector_review`
- `sector_rotation_review`
- `review_envelope_v1`
- `sentiment_temperature_v1`
- `rotation_signal_v1`
- provider routing 行为
- payload 参数校验规则

本仓库内额外提供：

- `skills/MIGRATION_NEWSBOT_SKILL.md`

用于说明 newsbot skill 从 workspace-local 迁移到 repo-managed 的背景与维护约定。

## 说明

### 数据源 API 文档入口
- 统一索引见：`docs/INTERFACE_SCHEMA.md`（“上游数据源文档入口”章节）

### 股票历史的当前实现
- `stock_history(stock)` 当前通过 **AKShare 腾讯历史接口** 实现
- 复盘增强：股票已支持 `1d / 1w / 1M`
  - `1w / 1M` 由日线聚合得到
  - `limit` 在聚合后应用
  - 当传入 `start_date/end_date` 时，区间边界可能出现不完整周/月，这一点会在 `data.meta.partial_period_at_range_edges` 标明
- 字段来源与口径：
  - `open/high/low/close`：腾讯历史接口（日线基础）
  - `volume`：优先由 `stock_zh_a_daily` 按日期回填；周/月按日线求和
  - `turnover`：统一为成交额口径（`stock_zh_a_daily.amount` 优先）；周/月按日线求和
  - `prev_close`：日线按前一条 bar 的 `close` 推导；周/月使用聚合后前一根 K 线 `close` 回填

### sector_lookup 当前语义
- `mode=list, sector_type=concept`：概念板块列表
- `mode=list, sector_type=primary`：一级板块列表
- `mode=children`（或兼容 `members`）：按一级板块名称查询**股票成员列表**
- `children/members` 的 `sector_name` 需要传入真实可用的一级板块名称，例如：`TFG板块趋势`

### Transport 状态
当前已切换为 **MCP Python SDK（FastMCP）stdio transport**。
本地 `--tool` / `--list-tools` 路径仍保留，供调试与 smoke test 使用。


### event_calendar 事件时间轴样例

```bash
# 查询单只股票的分红/解禁/业绩事件（区间）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool event_calendar --payload '{"symbols":["600519.SH"],"event_types":["dividend","unlock","profit"],"start_date":"2026-01-01","end_date":"2026-12-31"}'

# 只看每只股票最近未来事件（盘前提醒）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool event_calendar --payload '{"symbols":["600519.SH"],"next_event_only":true}'

# 指定事件优先级（同日冲突时生效）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool event_calendar --payload '{"symbols":["600519.SH"],"next_event_only":true,"event_priority":["dividend","unlock","profit"]}'
```


### sector_leaders 板块龙头快照样例

```bash
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_leaders --payload '{"sector_name":"1000信息","sector_type":"primary","trade_date":"2026-05-08","top_n":3}'
```


### 榜单工具统一语义（v1）
- `return_mode=full`：返回过滤+排序后全量
- `return_mode=ranked_only`：仅返回 `top_n`
- 统一 `meta`：`filtered_from / filtered_count / ranked_count`
