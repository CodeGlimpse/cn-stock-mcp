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

## 当前已验证通过的能力

### 智兔主链路
- `stock_quote(index)`
- `stock_quote(fund)`
- `stock_quote(star)`
- `stock_quote(BJ index)`
- `stock_history(index)`
- `technical_indicator(index)`
- `market_overview()`
- `market_pool(limit_up)`
- `stock_orderbook(star)`

### AKShare
- `stock_search()` 基本可用
- `stock_history(stock)` 已改走 **腾讯历史接口**，当前可用
- `stock_history(index)` 在 Zhitu 不可用或北证50等边角场景下，已具备 **AKShare index history fallback**
- `trading_calendar()` 交易日历 / 复盘日期辅助可用
- `stock_review()` 个股复盘摘要可用
- `stock_review_batch()` 批量复盘排序可用

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
```

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
  - `volatility_20d / period_volatility`
  - `max_drawdown_20d / max_drawdown_period`
  - `up_streak / down_streak`
  - `volume_ratio_5d / turnover_ratio_5d`
  - `relative_strength_20d / relative_strength_period`
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
- 返回中新增：`index_ranking / breadth / sentiment / highlights`，便于复盘时快速看指数强弱与情绪温度

### sector_review 板块复盘样例

```bash
# 单日板块复盘：查看板块成员整体强弱、情绪、龙头/跟风/掉队
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_review --payload '{"sector_name":"TFG板块趋势","trade_date":"2026-04-30","top_n":3,"limit":20}'

# 区间板块复盘：适合看一段时间的行业强弱、结构分化与轮动特征
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_review --payload '{"sector_name":"TFG板块趋势","start_date":"2026-04-01","end_date":"2026-04-30","top_n":3,"limit":20}'
```

说明：
- 先通过 `sector_lookup(mode=children)` 获取板块成员股
- 再复用 `stock_review_batch` 生成成员股复盘卡片
- 返回除 `items` 外，还包含：
  - `breadth`（上涨/下跌/放量/连涨连跌分布）
  - `stats`（平均收益、相对强弱、回撤、离散度）
  - `sentiment`（偏热 / 偏强 / 中性 / 偏弱 / 偏冷）
  - `benchmark_summary`（板块成员基准分布与平均基准收益）
  - `continuity`（持续强势/弱势、连涨连跌情况）
  - `rotation`（区间模式下的轮动判断，如 `龙头驱动 / 普涨轮动 / 分化轮动`）
  - `structure`（板块结构标签，如 `broad_strength / high_dispersion / trend_divergence`）
  - `rankings`（收益/相对强弱/量比/回撤风险榜）
  - `buckets`（`leaders / followers / draggers / risk_alerts / strong_candidates / weak_candidates` 等分层）

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

## 说明

### 数据源 API 文档入口
- 统一索引见：`docs/DATA_SOURCE_API_DOCS.md`

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
