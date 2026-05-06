# 接口与 Schema 设计文档 v1.1

> 项目：`openclaw-stock-mcp`
> 版本：v1.1
> 目标：定义 MCP tools 的输入/输出结构、统一字段规范、provider 路由约束、错误模型与实现边界，作为后续代码实现的直接依据。

---

## 1. 文档目标

本文件用于明确以下内容：

1. MCP tool 列表与职责边界
2. 每个 tool 的输入 schema
3. 每个 tool 的输出 schema
4. 通用枚举与字段规范
5. symbol 标准化规则
6. provider 路由规则
7. 错误码与错误响应结构
8. 分页、限制、排序、时间格式等通用约定

本文件优先服务于：
- MCP 服务端实现
- Skill 编写
- 后续测试样例设计
- provider adapter 开发

---

## 2. 设计原则

### 2.1 面向任务，不面向上游 API
Schema 必须表达“agent 想完成什么”，而不是“某个上游接口叫什么”。

### 2.2 输入尽量稳定、少而明确
避免 agent 需要记忆过多 provider 特定参数。

### 2.3 输出统一、扁平、可推理
优先保证：
- 字段语义稳定
- 不随 provider 改变
- 尽量不返回原始混乱字段

### 2.4 保留可追踪性
所有核心输出必须带：
- `source`
- 尽量带 `timestamp`
- 必要时带 `partial_failure`

---

## 3. MCP Tools 清单

v1.1 定义以下 tools：

### 核心 tools
1. `stock_search`
2. `stock_quote`
3. `stock_history`
4. `market_overview`

### 增强 tools
5. `technical_indicator`
6. `market_pool`
7. `stock_orderbook`（可选实现）
8. `sector_lookup`（可选实现）
9. `sector_review`（板块复盘 / 板块成员聚合分析）
10. `market_brief`（市场简报 / 市场级复盘聚合）

---

## 4. 通用类型与枚举

### 4.1 Market
当前固定：

```json
"CN"
```

v1 暂不暴露多市场枚举。

---

### 4.2 SecType

```json
["stock", "index", "fund", "sector"]
```

含义：
- `stock`: 股票
- `index`: 指数
- `fund`: 基金 / ETF
- `sector`: 概念板块 / 行业板块

---

### 4.3 Exchange

```json
["SH", "SZ", "BJ", "BK"]
```

含义：
- `SH`: 上海证券交易所
- `SZ`: 深圳证券交易所
- `BJ`: 北京证券交易所
- `BK`: 板块/概念类交易域

---

### 4.4 Board

建议统一值：

```json
[
  "main",
  "chinext",
  "star",
  "beijing",
  "fund",
  "index",
  "sector"
]
```

说明：
- `main`: 主板
- `chinext`: 创业板
- `star`: 科创板
- `beijing`: 北交所
- `fund`: 基金
- `index`: 指数
- `sector`: 板块

---

### 4.5 Interval

对外统一支持：

```json
["5m", "15m", "30m", "60m", "1d", "1w", "1M", "1y"]
```

说明：
- `5m`: 5分钟
- `15m`: 15分钟
- `30m`: 30分钟
- `60m`: 60分钟
- `1d`: 日线
- `1w`: 周线
- `1M`: 月线
- `1y`: 年线
- `1m`：当前版本**不支持**，避免与 `1M` 月线语义混淆

---

### 4.6 Adjust

```json
["none", "qfq", "hfq"]
```

仅对股票历史数据有效：
- `none`: 不复权
- `qfq`: 前复权
- `hfq`: 后复权

---

### 4.7 IndicatorType

```json
["macd", "ma", "boll", "kdj"]
```

---

### 4.8 PoolType

```json
["limit_up", "limit_down", "strong"]
```

映射：
- `limit_up` → 涨停股池
- `limit_down` → 跌停股池
- `strong` → 强势股池

---

## 5. Symbol 规范

### 5.1 对外接受的输入格式
支持以下输入：
- `600519`
- `000001`
- `430017`
- `688001`
- `000001.SH`
- `399001.SZ`
- `899050.BJ`
- `平安银行`
- `北证50`
- `货币ETF`

### 5.2 对外推荐标准格式
统一返回 canonical symbol：

- 股票：`600519.SH`
- 股票：`000001.SZ`
- 北交所：`430017.BJ`
- 指数：`000001.SH`
- 指数：`899050.BJ`
- 基金：`159001.SZ`
- 板块：`101076.BKZS`

### 5.3 内部 symbol 字段要求
输出中的 `symbol` 字段必须是标准化结果，而不是用户原始输入。

### 5.4 raw_symbol
当需要追踪原始输入时，可额外返回：

```json
"raw_symbol": "600519"
```

但 `raw_symbol` 不是所有工具都必须返回。

---

## 6. 通用对象 Schema

以下是逻辑 schema，不要求逐字照抄 JSON Schema Draft 规范，但实现时建议用 Pydantic 保持一致。

---

### 6.1 Instrument

```json
{
  "symbol": "000001.SZ",
  "name": "平安银行",
  "market": "CN",
  "exchange": "SZ",
  "board": "main",
  "sec_type": "stock",
  "raw_symbol": "000001",
  "source": "akshare",
  "confidence": 0.99
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| symbol | string | 是 | 标准化代码 |
| name | string/null | 否 | 名称 |
| market | string | 是 | 当前固定 `CN` |
| exchange | string/null | 否 | `SH`/`SZ`/`BJ`/`BK` |
| board | string/null | 否 | 板块归属 |
| sec_type | string | 是 | `stock`/`index`/`fund`/`sector` |
| raw_symbol | string/null | 否 | 原始代码 |
| source | string/null | 否 | provider 名称 |
| confidence | number/null | 否 | 仅搜索结果常用，0~1 |

---

### 6.2 Quote

```json
{
  "symbol": "000001.SZ",
  "name": "平安银行",
  "market": "CN",
  "exchange": "SZ",
  "board": "main",
  "sec_type": "stock",
  "price": 12.34,
  "open": 12.20,
  "high": 12.45,
  "low": 12.10,
  "prev_close": 12.22,
  "change": 0.12,
  "change_percent": 0.98,
  "amplitude": 2.86,
  "volume": 1234567,
  "turnover": 123456789.0,
  "turnover_rate": 1.23,
  "pe": 8.88,
  "pb": 0.95,
  "market_cap": 250000000000.0,
  "float_market_cap": 180000000000.0,
  "currency": "CNY",
  "trading_status": "trading",
  "timestamp": "2026-04-30T15:00:00+08:00",
  "source": "zhitu"
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| symbol | string | 是 | 标准化代码 |
| name | string/null | 否 | 名称 |
| market | string | 是 | `CN` |
| exchange | string/null | 否 | 交易所 |
| board | string/null | 否 | 板块 |
| sec_type | string | 是 | 类型 |
| price | number/null | 否 | 最新价 |
| open | number/null | 否 | 开盘价 |
| high | number/null | 否 | 最高价 |
| low | number/null | 否 | 最低价 |
| prev_close | number/null | 否 | 前收 |
| change | number/null | 否 | 涨跌额 |
| change_percent | number/null | 否 | 涨跌幅，单位 % |
| amplitude | number/null | 否 | 振幅，单位 % |
| volume | number/null | 否 | 成交量 |
| turnover | number/null | 否 | 成交额 |
| turnover_rate | number/null | 否 | 换手率，单位 % |
| pe | number/null | 否 | 市盈率 |
| pb | number/null | 否 | 市净率 |
| market_cap | number/null | 否 | 总市值 |
| float_market_cap | number/null | 否 | 流通市值 |
| currency | string | 否 | 默认 `CNY` |
| trading_status | string/null | 否 | `trading` / `closed` / `halted` / `unknown` |
| timestamp | string/null | 否 | 更新时间，ISO 8601 优先 |
| source | string | 是 | provider 名 |

---

### 6.3 Bar

```json
{
  "time": "2026-04-30",
  "open": 3200.1,
  "high": 3215.8,
  "low": 3188.3,
  "close": 3208.9,
  "volume": 123456789,
  "turnover": 4567891234.0,
  "prev_close": 3198.2
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| time | string | 是 | 时间点，日线推荐 `YYYY-MM-DD`，分钟线推荐 ISO 风格或 `YYYY-MM-DD HH:mm:ss` |
| open | number/null | 否 | 开盘价 |
| high | number/null | 否 | 最高价 |
| low | number/null | 否 | 最低价 |
| close | number/null | 否 | 收盘价 |
| volume | number/null | 否 | 成交量 |
| turnover | number/null | 否 | 成交额 |
| prev_close | number/null | 否 | 前收 |

---

### 6.4 OrderBook

```json
{
  "symbol": "688001.SH",
  "timestamp": "2026-04-30T14:59:59+08:00",
  "bids": [
    {"price": 11.63, "volume": 424},
    {"price": 11.62, "volume": 1291}
  ],
  "asks": [
    {"price": 11.64, "volume": 7330},
    {"price": 11.65, "volume": 7698}
  ],
  "source": "zhitu"
}
```

说明：
- `bids` 按买一到买五顺序
- `asks` 按卖一到卖五顺序
- 若只返回部分档位，数组长度可小于 5

---

### 6.5 IndicatorSeries

```json
{
  "symbol": "000001.SH",
  "name": "上证指数",
  "sec_type": "index",
  "interval": "1d",
  "indicator": "macd",
  "items": [
    {
      "time": "2026-04-30",
      "values": {
        "diff": -8.113,
        "dea": -13.269,
        "macd": 10.312,
        "ema12": 3284.4412,
        "ema26": 3292.5544
      }
    }
  ],
  "source": "zhitu"
}
```

字段说明：
- `values` 为不同指标的值集合
- `values` 的 key 由 `indicator` 类型决定

#### 6.5.1 MACD values
```json
{"diff": 0.0, "dea": 0.0, "macd": 0.0, "ema12": 0.0, "ema26": 0.0}
```

#### 6.5.2 MA values
```json
{"ma3": 0.0, "ma5": 0.0, "ma10": 0.0, "ma15": 0.0, "ma20": 0.0, "ma30": 0.0, "ma60": 0.0, "ma120": 0.0, "ma200": 0.0, "ma250": 0.0}
```

#### 6.5.3 BOLL values
```json
{"u": 0.0, "m": 0.0, "d": 0.0}
```

#### 6.5.4 KDJ values
```json
{"k": 0.0, "d": 0.0, "j": 0.0}
```

---

### 6.6 MarketPoolItem

```json
{
  "symbol": "603099.SH",
  "name": "长白山",
  "price": 29.18,
  "change_percent": 9.99,
  "turnover": 1462451424.0,
  "turnover_rate": 19.22,
  "market_cap": 7781430600.0,
  "float_market_cap": 7781430600.0,
  "extra": {
    "limit_count": 7,
    "first_limit_time": "09:31:27",
    "last_limit_time": "13:03:12",
    "board_burst_count": 3,
    "stat": "7/7"
  }
}
```

说明：
- 由于不同股池字段不完全一致，允许把非通用字段放在 `extra`
- `extra` 内字段名要求尽量英文语义化

---

## 7. Tool 详细 Schema

---

## 7.1 `stock_search`

### 7.1.1 用途
根据名称、代码、简称等搜索证券。

### 7.1.2 输入 Schema

```json
{
  "type": "object",
  "properties": {
    "query": {"type": "string"},
    "sec_types": {
      "type": "array",
      "items": {"type": "string", "enum": ["stock", "index", "fund", "sector"]}
    },
    "market": {"type": "string", "enum": ["CN"]},
    "limit": {"type": "integer", "minimum": 1, "maximum": 50},
    "provider": {"type": "string", "enum": ["akshare", "zhitu"]}
  },
  "required": ["query"]
}
```

### 7.1.3 输入约束
- `query` 非空，去除首尾空格后长度 >= 1
- `limit` 默认 10
- `sec_types` 默认 `['stock', 'index', 'fund']`
- `market` 默认 `CN`

### 7.1.4 输出 Schema

```json
{
  "items": [Instrument],
  "total": 1,
  "source": "akshare"
}
```

### 7.1.5 说明
- 搜索结果按相关性降序
- `confidence` 建议由 resolver 层计算
- 若 query 为标准 symbol，也允许直接返回精确结果

---

## 7.2 `stock_quote`

### 7.2.1 用途
查询一个或多个标的的实时行情快照。

### 7.2.2 输入 Schema

```json
{
  "type": "object",
  "properties": {
    "symbols": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1,
      "maxItems": 50
    },
    "sec_type": {"type": "string", "enum": ["stock", "index", "fund"]},
    "fields": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "price", "open", "high", "low", "prev_close",
          "change", "change_percent", "amplitude",
          "volume", "turnover", "turnover_rate",
          "pe", "pb", "market_cap", "float_market_cap",
          "timestamp"
        ]
      }
    },
    "provider": {"type": "string", "enum": ["akshare", "zhitu"]},
    "provider_preference": {
      "type": "array",
      "items": {"type": "string", "enum": ["akshare", "zhitu"]}
    }
  },
  "required": ["symbols"]
}
```

### 7.2.3 输入约束
- `symbols` 去重后处理
- 单次最多 50 个 symbol，避免滥用
- `sec_type` 可选；缺省时内部先 resolve
- `fields` 为可选裁剪，不影响底层实际获取

### 7.2.4 输出 Schema

```json
{
  "items": [Quote],
  "partial_failure": false,
  "errors": []
}
```

其中 `errors` 可选，格式为：

```json
[
  {
    "symbol": "BADCODE",
    "error": {
      "code": "SYMBOL_NOT_FOUND",
      "message": "Instrument not found",
      "retryable": false
    }
  }
]
```

### 7.2.5 输出约束
- 成功项与失败项允许并存
- 若全部失败，则 tool 直接返回顶层 `error`
- 若部分成功，则 `partial_failure=true`

---

## 7.3 `stock_history`

### 7.3.1 用途
查询历史 K 线 / 分时线。

### 7.3.2 输入 Schema

```json
{
  "type": "object",
  "properties": {
    "symbol": {"type": "string"},
    "sec_type": {"type": "string", "enum": ["stock", "index", "fund"]},
    "interval": {"type": "string", "enum": ["5m", "15m", "30m", "60m", "1d", "1w", "1M", "1y"]},
    "start_date": {"type": "string"},
    "end_date": {"type": "string"},
    "limit": {"type": "integer", "minimum": 1, "maximum": 5000},
    "adjust": {"type": "string", "enum": ["none", "qfq", "hfq"]},
    "provider": {"type": "string", "enum": ["akshare", "zhitu"]},
    "provider_preference": {
      "type": "array",
      "items": {"type": "string", "enum": ["akshare", "zhitu"]}
    }
  },
  "required": ["symbol", "interval"]
}
```

### 7.3.3 输入约束
- `limit` 默认 200
- `limit` 上限建议 1000；文档上允许更大，但实现上不建议放开到 5000
- `start_date <= end_date`
- `adjust` 仅股票有效；对指数和基金应忽略或拒绝
- 不允许同时既不给 `limit` 也不给时间范围且拉全量超长历史

### 7.3.4 输出 Schema

```json
{
  "symbol": "000001.SH",
  "name": "上证指数",
  "market": "CN",
  "sec_type": "index",
  "interval": "1d",
  "start_date": "2026-01-01",
  "end_date": "2026-04-30",
  "adjust": "none",
  "items": [Bar],
  "count": 120,
  "source": "zhitu"
}
```

### 7.3.5 输出约束
- `items` 按时间升序
- `count == len(items)`
- `adjust` 若不适用可返回 `null` 或省略

---

## 7.4 `market_overview`

### 7.4.1 用途
查询市场主要指数概况。

### 7.4.2 输入 Schema

```json
{
  "type": "object",
  "properties": {
    "market": {"type": "string", "enum": ["CN"]},
    "include": {
      "type": "array",
      "items": {"type": "string", "enum": ["main_indices", "beijing_indices", "fund_indices"]}
    },
    "provider": {"type": "string", "enum": ["akshare", "zhitu", "mixed"]}
  }
}
```

### 7.4.3 输入约束
- `market` 默认 `CN`
- `include` 默认 `['main_indices', 'beijing_indices']`
- `provider` 默认 `mixed`

### 7.4.4 输出 Schema

```json
{
  "market": "CN",
  "timestamp": "2026-04-30T15:00:00+08:00",
  "indices": [Quote],
  "source": "mixed"
}
```

### 7.4.5 说明
- `indices` 内每项是 `sec_type=index` 的 Quote 子集
- 建议最少包含：上证指数、深证成指、创业板指、北证50

---

## 7.5 `technical_indicator`

### 7.5.1 用途
查询技术指标序列。

### 7.5.2 输入 Schema

```json
{
  "type": "object",
  "properties": {
    "symbol": {"type": "string"},
    "sec_type": {"type": "string", "enum": ["index", "stock", "fund"]},
    "interval": {"type": "string", "enum": ["5m", "15m", "30m", "60m", "1d", "1w", "1M", "1y"]},
    "indicator": {"type": "string", "enum": ["macd", "ma", "boll", "kdj"]},
    "start_date": {"type": "string"},
    "end_date": {"type": "string"},
    "limit": {"type": "integer", "minimum": 1, "maximum": 2000},
    "provider": {"type": "string", "enum": ["zhitu", "akshare"]}
  },
  "required": ["symbol", "interval", "indicator"]
}
```

### 7.5.3 输入约束
- v1 推荐只正式支持 `sec_type=index`
- `limit` 默认 200
- 当前优先 provider 为 `zhitu`

### 7.5.4 输出 Schema

```json
{
  "symbol": "000001.SH",
  "name": "上证指数",
  "market": "CN",
  "sec_type": "index",
  "interval": "1d",
  "indicator": "macd",
  "items": [IndicatorPoint],
  "count": 60,
  "source": "zhitu"
}
```

---

## 7.6 `market_pool`

### 7.6.1 用途
查询涨停/跌停/强势股池。

### 7.6.2 输入 Schema

```json
{
  "type": "object",
  "properties": {
    "pool_type": {"type": "string", "enum": ["limit_up", "limit_down", "strong"]},
    "trade_date": {"type": "string"},
    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
    "provider": {"type": "string", "enum": ["zhitu"]}
  },
  "required": ["pool_type"]
}
```

### 7.6.3 输入约束
- `trade_date` 默认最近交易日
- `limit` 默认 100
- v1 provider 固定为 `zhitu`

### 7.6.4 输出 Schema

```json
{
  "pool_type": "limit_up",
  "trade_date": "2026-04-30",
  "items": [MarketPoolItem],
  "count": 100,
  "source": "zhitu"
}
```

---

## 7.7 `stock_orderbook`

### 7.7.1 用途
查询五档盘口。

### 7.7.2 输入 Schema

```json
{
  "type": "object",
  "properties": {
    "symbol": {"type": "string"},
    "sec_type": {"type": "string", "enum": ["stock"]},
    "provider": {"type": "string", "enum": ["zhitu"]}
  },
  "required": ["symbol"]
}
```

### 7.7.3 输出 Schema

```json
OrderBook
```

### 7.7.4 说明
- v1 可限定仅支持北交所、科创板
- 若 symbol 对应市场不支持，应返回 `UNSUPPORTED_MARKET`

---

## 7.8 `sector_lookup`

### 7.8.1 用途
查询板块列表或板块成员。

### 7.8.2 输入 Schema

```json
{
  "type": "object",
  "properties": {
    "mode": {"type": "string", "enum": ["list", "members", "children"]},
    "sector_type": {"type": "string", "enum": ["concept", "primary"]},
    "sector_name": {"type": "string"},
    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
    "provider": {"type": "string", "enum": ["zhitu"]}
  },
  "required": ["mode"]
}
```

### 7.8.3 输出 Schema

#### list 模式
```json
{
  "mode": "list",
  "sector_type": "concept",
  "items": [Instrument],
  "count": 100,
  "source": "zhitu"
}
```

#### members / children 模式
```json
{
  "mode": "children",
  "sector_name": "TFG板块趋势",
  "items": [Instrument],
  "count": 50,
  "source": "zhitu"
}
```

说明：
- `members` 是兼容旧模式名，语义等同 `children`
- 当前返回的是**股票成员列表**，不是子板块列表

---

## 7.9 `sector_review`

### 7.9.1 用途
对指定板块做聚合复盘：先获取板块成员股，再对成员股做批量复盘，输出板块层面的强弱、情绪、结构与候选分层。

### 7.9.2 输入 Schema

```json
{
  "type": "object",
  "properties": {
    "sector_name": {"type": "string"},
    "trade_date": {"type": "string"},
    "start_date": {"type": "string"},
    "end_date": {"type": "string"},
    "adjust": {"type": "string", "enum": ["none", "qfq", "hfq"]},
    "provider": {"type": "string", "enum": ["zhitu"]},
    "sort_by": {"type": "string", "enum": ["relative_strength", "return", "max_drawdown", "volume_ratio"]},
    "descending": {"type": "boolean"},
    "top_n": {"type": "integer", "minimum": 1, "maximum": 20},
    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
    "min_relative_strength": {"type": "number"},
    "min_return": {"type": "number"},
    "max_drawdown_limit": {"type": "number"},
    "min_volume_ratio": {"type": "number"}
  },
  "required": ["sector_name"]
}
```

### 7.9.3 输入约束
- `trade_date` 与 `start_date/end_date` 互斥
- 区间模式必须同时提供 `start_date + end_date`
- 默认模式为 `trade_date=today`
- `provider` 当前固定为 `zhitu`，用于获取板块成员；成员股复盘当前复用 `akshare` 路径

### 7.9.4 输出 Schema

```json
{
  "subject_type": "sector",
  "subject_name": "TFG板块趋势",
  "sector_name": "TFG板块趋势",
  "mode": "trade_date_review",
  "trade_date": "2026-04-30",
  "requested_trade_date": "2026-04-30",
  "start_date": null,
  "end_date": null,
  "member_count": 20,
  "reviewed_count": 18,
  "breadth": {},
  "stats": {},
  "sentiment": {
    "label": "warm",
    "label_zh": "偏强",
    "score": 2.0,
    "normalized_score": 70.0,
    "score_semantics": "sentiment_temperature_v1"
  },
  "benchmark_summary": {},
  "continuity": {},
  "rotation": {},
  "structure": {"tags": ["broad_strength"]},
  "leaders": [],
  "laggards": [],
  "rankings": {},
  "buckets": {},
  "items": [],
  "summary": "...",
  "partial_failure": false,
  "errors": [],
  "meta": {
    "review_envelope_schema": {"schema": "review_envelope_v1"},
    "sentiment_score_schema": {"schema": "sentiment_temperature_v1"},
    "rotation_score_schema": {"schema": "rotation_signal_v1"}
  }
}
```

### 7.9.5 输出说明
- `sector_review` 采用统一 `review_envelope_v1`
- `subject_type=sector`
- `subject_name=sector_name`
- `breadth`：上涨/下跌/放量/连涨连跌分布
- `stats`：平均收益、相对强弱、量比、回撤、离散度
- `sentiment`：板块情绪温度；`score` 统一为 `[-5, 5]`，`normalized_score` 统一为 `[0, 100]`
- `benchmark_summary`：板块成员基准分布与平均基准收益
- `continuity`：持续强势/弱势、连涨连跌情况
- `rotation`：区间模式下的轮动判断，如 `leader_driven / broad_advance / divergent_rotation`
- `structure.tags`：板块结构标签，如 `broad_strength / concentrated_strength / high_dispersion / trend_divergence`
- `leaders / laggards / items`：统一 review item-card 结构
- `rankings`：收益 / 相对强弱 / 量比 / 回撤风险榜单
- `buckets`：`leaders / followers / draggers / risk_alerts / strong_candidates / weak_candidates`
- `meta.review_envelope_schema`：声明当前返回遵循的公共 review envelope
- `meta.sentiment_score_schema`：声明 `sentiment.score` 的统一语义
- `meta.rotation_score_schema`：声明 `rotation.score` 的独立语义，避免与 `sentiment.score` 混用

---

## 7.10 `market_brief`

### 7.10.1 用途
生成市场级简报与复盘聚合结果：结合指数概览、历史指数日线、交易日历与市场股池，输出与 `sector_review` 同构的 review envelope，同时保留市场简报专有兼容字段。

### 7.10.2 输入 Schema

```json
{
  "type": "object",
  "properties": {
    "brief_type": {"type": "string", "enum": ["pre_open", "intraday", "close"]},
    "market": {"type": "string", "enum": ["CN"]},
    "trade_date": {"type": "string"},
    "include_pools": {"type": "boolean"},
    "top_n": {"type": "integer", "minimum": 1, "maximum": 50},
    "provider": {"type": "string", "enum": ["akshare", "zhitu", "mixed"]}
  }
}
```

### 7.10.3 输入约束
- `trade_date` 为空时走实时模式，`mode=realtime_brief`
- `trade_date` 非空时走复盘模式，`mode=trade_date_review`
- 若 `trade_date` 落在非交易日，自动回退到上一个交易日，并通过 `meta.calendar` 返回
- `include_pools=false` 时仍返回统一 envelope，但 `pools / buckets` 可能为空

### 7.10.4 输出 Schema

```json
{
  "subject_type": "market",
  "subject_name": "CN",
  "brief_type": "close",
  "mode": "trade_date_review",
  "trade_date": "2026-05-01",
  "requested_trade_date": "2026-05-03",
  "start_date": null,
  "end_date": null,
  "member_count": 4,
  "reviewed_count": 4,
  "market": "CN",
  "overview": {},
  "index_ranking": [],
  "breadth": {},
  "stats": {},
  "sentiment": {
    "label": "warm",
    "label_zh": "偏强",
    "score": 2.0,
    "normalized_score": 70.0,
    "score_semantics": "sentiment_temperature_v1"
  },
  "benchmark_summary": {
    "applicable": false,
    "benchmark_mix": []
  },
  "continuity": {
    "applicable": false
  },
  "rotation": {
    "label": "broad_advance",
    "label_zh": "普涨轮动",
    "score": 1.5
  },
  "structure": {},
  "highlights": {},
  "leaders": [],
  "laggards": [],
  "rankings": {},
  "buckets": {},
  "items": [],
  "pools": {},
  "summary": "...",
  "partial_failure": false,
  "errors": [],
  "meta": {
    "review_envelope_schema": {"schema": "review_envelope_v1"},
    "sentiment_score_schema": {"schema": "sentiment_temperature_v1"},
    "rotation_score_schema": {"schema": "rotation_signal_v1"}
  }
}
```

### 7.10.5 输出说明
- `market_brief` 与 `sector_review` 共用同一套 `review_envelope_v1`
- `subject_type=market`
- `subject_name=market`
- `member_count / reviewed_count` 在当前实现中等于参与排序的指数数量
- `leaders / laggards / items` 与 `sector_review` 统一为同一类 review item-card 结构
- `stats / sentiment / structure / rotation / rankings / buckets` 可按统一方式被下游消费
- `benchmark_summary / continuity` 在市场级简报中当前多为“不适用”，因此返回 `null / [] / applicable=false`，而不是省略键
- 以下字段是 `market_brief` 的兼容专有字段：
  - `overview`
  - `index_ranking`
  - `highlights`
  - `pools`
- `meta.review_envelope_schema`：声明当前返回遵循的公共 review envelope
- `meta.sentiment_score_schema`：声明 `sentiment.score` 的统一语义
- `meta.rotation_score_schema`：声明 `rotation.score` 的独立语义，避免与 `sentiment.score` 混用

---

## 8. 通用输出包装约定

### 8.1 成功响应
每个 tool 成功时直接返回业务对象，不强制包裹 `success=true`。

### 8.2 部分失败
批量接口如 `stock_quote` 支持：

```json
{
  "items": [...],
  "partial_failure": true,
  "errors": [...]
}
```

### 8.3 全部失败
直接返回统一错误对象：

```json
{
  "error": {
    "code": "PROVIDER_TIMEOUT",
    "message": "Provider request timed out",
    "provider": "zhitu",
    "retryable": true,
    "details": {}
  }
}
```

---

## 9. 错误码设计

### 9.1 通用错误码

| 错误码 | 含义 | 是否可重试 |
|---|---|---:|
| INVALID_ARGUMENT | 参数非法 | 否 |
| SYMBOL_NOT_FOUND | 未找到证券 | 否 |
| AMBIGUOUS_SYMBOL | 标的歧义 | 否 |
| UNSUPPORTED_SEC_TYPE | 不支持的证券类型 | 否 |
| UNSUPPORTED_MARKET | 不支持的市场/板块 | 否 |
| UNSUPPORTED_INTERVAL | 不支持的周期 | 否 |
| EMPTY_RESULT | 返回为空 | 否/视情况 |
| PROVIDER_AUTH_FAILED | provider 认证失败 | 否 |
| PROVIDER_RATE_LIMITED | provider 限流 | 是 |
| PROVIDER_TIMEOUT | provider 超时 | 是 |
| PROVIDER_UNAVAILABLE | provider 不可用 | 是 |
| UPSTREAM_SCHEMA_CHANGED | 上游字段变化 | 否 |
| INTERNAL_ERROR | 内部异常 | 视情况 |

---

### 9.2 错误对象 Schema

```json
{
  "code": "SYMBOL_NOT_FOUND",
  "message": "Instrument not found: 000000",
  "provider": "resolver",
  "retryable": false,
  "details": {
    "symbol": "000000"
  }
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| code | string | 是 | 错误码 |
| message | string | 是 | 人类可读错误信息 |
| provider | string/null | 否 | 错误来源 |
| retryable | boolean | 是 | 是否建议重试 |
| details | object | 否 | 扩展信息 |

---

## 10. Provider 路由表

### 10.1 默认优先级

| Tool | 主 provider | 备 provider | 说明 |
|---|---|---|---|
| stock_search | akshare | zhitu | 搜索/基础解析优先本地能力 |
| stock_quote(stock) | zhitu | akshare | 已实测：普通沪深股票实时主走智兔，akshare 作为备源 |
| stock_quote(index) | zhitu | akshare | 指数智兔文档更明确 |
| stock_quote(fund) | zhitu | akshare | 基金实时智兔文档明确 |
| stock_history(stock) | akshare | zhitu | 历史数据优先 AKShare |
| stock_history(index) | zhitu | akshare | 指数分时智兔较清晰 |
| market_overview | mixed | - | 可混合取数 |
| technical_indicator | zhitu | - | v1 主要依赖智兔 |
| market_pool | zhitu | - | 智兔独有明确文档 |
| stock_orderbook | zhitu | - | 智兔独有明确文档 |
| sector_lookup | zhitu | - | 智兔独有明确文档 |

### 10.2 route 决策顺序
1. 若请求显式指定 `provider`，先尝试指定 provider
2. 若显式指定 `provider_preference`，按列表顺序尝试
3. 否则走默认路由表
4. 若命中可重试错误，可回退到下一个 provider
5. 若命中业务错误（如 symbol 不存在），不回退

---

## 11. 时间与日期规范

### 11.1 输入
优先支持：
- `YYYY-MM-DD`
- `YYYY-MM-DDTHH:mm:ss+08:00`

### 11.2 输出
推荐统一：
- 日线：`YYYY-MM-DD`
- 分钟线/实时：`YYYY-MM-DDTHH:mm:ss+08:00`

### 11.3 provider 转换
- 智兔历史接口需要 `YYYYMMDD` 或 `YYYYMMDDhhmmss`
- adapter 层负责转换

---

## 12. 分页与 limit 约定

v1 大部分接口不用复杂分页，统一采用 `limit`。

### 建议默认值
- `stock_search.limit = 10`
- `stock_quote.symbols <= 50`
- `stock_history.limit = 200`
- `technical_indicator.limit = 200`
- `market_pool.limit = 100`
- `sector_lookup.limit = 100`

### 为什么不用 offset/page
因为当前主要面向 agent 场景，更多是“拿前若干条最有用的数据”，不是前端表格翻页。

---

## 13. summary 字段策略

v1.1 不强制所有接口输出 `summary`，但允许在这些接口加可选 `summary`：
- `stock_quote`
- `market_overview`
- `market_pool`

例如：

```json
"summary": "平安银行最新价 12.34 元，涨幅 0.98%。"
```

原则：
- summary 是辅助，不是主数据
- 不影响结构化解析
- 不要只返回 summary 而省略结构化字段

---

## 14. Pydantic 模型建议

建议至少建立以下模型：

- `Instrument`
- `Quote`
- `Bar`
- `OrderBookLevel`
- `OrderBook`
- `IndicatorPoint`
- `IndicatorSeries`
- `MarketPoolItem`
- `ToolError`
- `PartialItemError`

以及 tool request 模型：
- `StockSearchRequest`
- `StockQuoteRequest`
- `StockHistoryRequest`
- `MarketOverviewRequest`
- `TechnicalIndicatorRequest`
- `MarketPoolRequest`
- `StockOrderbookRequest`
- `SectorLookupRequest`

---

## 15. 实现注意事项

### 15.1 不要把 provider 原始字段直接透出
例如不要在最终响应里把 `p`, `pc`, `yc`, `cje` 原样返回给 agent。

### 15.2 保留 provider 原始响应只用于日志/调试
不进入对外 schema。

### 15.3 symbol resolve 尽量在 tool 入口统一做
不要每个 provider 自己乱解析。

### 15.4 对股池、板块类半结构化数据，允许 `extra`
但主字段必须稳定。

### 15.5 历史数据必须升序返回
这样 Skill 或 agent 做趋势推理最自然。

---

## 16. 示例：完整错误响应

```json
{
  "error": {
    "code": "AMBIGUOUS_SYMBOL",
    "message": "Multiple instruments matched query: 平安",
    "provider": "resolver",
    "retryable": false,
    "details": {
      "query": "平安",
      "candidates": [
        {"symbol": "000001.SZ", "name": "平安银行", "sec_type": "stock"},
        {"symbol": "601318.SH", "name": "中国平安", "sec_type": "stock"}
      ]
    }
  }
}
```

---

## 17. 示例：完整部分失败响应

```json
{
  "items": [
    {
      "symbol": "000001.SZ",
      "name": "平安银行",
      "market": "CN",
      "exchange": "SZ",
      "board": "main",
      "sec_type": "stock",
      "price": 12.34,
      "change": 0.12,
      "change_percent": 0.98,
      "timestamp": "2026-04-30T15:00:00+08:00",
      "source": "zhitu"
    }
  ],
  "partial_failure": true,
  "errors": [
    {
      "symbol": "BADCODE",
      "error": {
        "code": "SYMBOL_NOT_FOUND",
        "message": "Instrument not found",
        "provider": "resolver",
        "retryable": false,
        "details": {"symbol": "BADCODE"}
      }
    }
  ]
}
```

---

## 18. v1.1 明确结论

本版本 schema 设计的核心结论是：

1. **以 4 个核心 tool 为主，增强 tool 逐步实现**
2. **symbol 必须统一成 canonical symbol**
3. **Quote / Bar / Indicator / PoolItem 是最关键的四类标准模型**
4. **provider 路由与 fallback 放在 MCP 内部做**
5. **错误必须结构化，支持 partial failure**
6. **时间、limit、interval、sec_type 必须全局统一**

---

## 19. 下一步建议

基于本文件，下一步最适合继续产出的内容是：

1. `provider-mapping.md`：逐个接口映射 AKShare / 智兔到内部模型
2. `README.md` 初稿
3. `pyproject.toml`
4. `src/openclaw_stock_mcp/server/schemas.py`
5. `src/openclaw_stock_mcp/app/models/*.py`

如果你要，我下一步可以直接继续写 **`provider-mapping.md`**，或者直接开始生成 **Pydantic schema 代码**。