# 股票行情 MCP 项目详细设计说明书 v1

## 1. 项目概述

### 1.1 项目名称
暂定：

- `openclaw-stock-mcp`
- 或 `market-data-mcp`
- 或 `cn-market-mcp`

我建议用 **`openclaw-stock-mcp`**，语义直接。

---

### 1.2 项目目标

建设一个面向 OpenClaw Agent 的 MCP 服务，提供以下能力：

1. 查询 A 股、北交所、科创板、指数、基金的基础列表
2. 查询实时行情快照
3. 查询历史 K 线 / 分时线
4. 查询常用技术指标（优先从智兔获取，AKShare 作为补充）
5. 查询市场概览、板块、股池等辅助行情信息
6. 统一输出字段，屏蔽 AKShare 与智兔的接口差异
7. 为 Skill 提供稳定、少而精、适合 LLM 使用的工具集合

---

### 1.3 非目标

v1 **不做**这些事，避免项目失控：

1. 不做自动交易
2. 不做下单 / 券商账户集成
3. 不做复杂量化策略执行
4. 不做数据库型行情中台
5. 不把 AKShare / 智兔所有接口原样暴露成 MCP tools
6. 不做网页端 UI
7. 不做多租户权限系统

---

## 2. 设计原则

### 2.1 面向 Agent 的任务语义，而不是面向上游 API
tool 名必须表达“用途”，而不是表达“调用了哪个接口”。

**正确：**
- `stock_search`
- `stock_quote`
- `stock_history`
- `market_overview`

**不推荐：**
- `akshare_stock_zh_a_spot_em`
- `zhitu_hs_real_ssjy`

---

### 2.2 统一领域模型
AKShare 与智兔字段名不同、市场划分不同、代码格式也不同。  
MCP 层必须定义自己的标准模型，agent 只认 MCP 的稳定输出。

---

### 2.3 Provider 可插拔
底层 provider 至少支持：

- `akshare`
- `zhitu`

后续应允许扩：

- `tushare`
- `eastmoney-http`
- `yfinance`
- 自建内部行情源

---

### 2.4 内部做路由与回退
优先级、重试、超时、fallback 都应该在 MCP 内部做，不应让 Skill 承担底层数据源切换逻辑。

---

### 2.5 对 LLM 友好
- 输入参数要少而明确
- 输出字段稳定、扁平、可推理
- 错误结构化
- 支持批量查询，减少 agent 多轮 tool call

---

## 3. 数据源能力分析

### 3.1 AKShare 角色定位

AKShare 适合作为：

- **主基础数据源**
- 提供股票、指数、基金、历史行情等通用能力
- Python 本地直连 provider

优点：
- Python 生态天然适配
- 覆盖广
- 不需要单独 token（部分底层源除外）

缺点：
- 接口命名偏原始数据源风格
- 字段不统一
- 某些源稳定性受上游网站影响
- 历史上存在接口变更和抓取失效风险

项目内定位：
> `akshare_provider` 作为默认优先 provider 之一，尤其适合基础列表、历史数据、通用行情。

---

### 3.2 智兔角色定位

根据补充文档，目前可确认智兔提供了下列股票相关能力：

#### 沪深股票
- `/hs/list/all`
- `/hs/list/sectors`
- `/hs/list/primary`
- `/hs/sectors/{name}`
- `/hs/pool/ztgc/{date}`
- `/hs/pool/dtgc/{date}`
- `/hs/pool/qsgc/{date}`
- 以及文档未完全展开但明显存在的实时/历史类能力

#### 沪深指数
- `/hz/list/hszs`
- `/hz/real/ssjy/{symbol}`
- `/hz/latest/fsjy/{symbol}/{interval}`
- `/hz/history/fsjy/{symbol}/{interval}`
- `/hz/history/macd/{symbol}/{interval}`
- `/hz/history/ma/{symbol}/{interval}`
- `/hz/history/boll/{symbol}/{interval}`
- `/hz/history/kdj/{symbol}/{interval}`

#### 北交所
- `/bj/list/all`
- `/bj/list/index`
- `/bj/stock/real/ssjy/{symbol}`
- `/bj/stock/real/mmwp/{symbol}`
- `/bj/index/real/ssjy/{symbol}`

#### 科创板
- `/tech/list/all`
- `/tech/real/ssjy/{symbol}`
- `/tech/real/mmwp/{symbol}`

#### 基金
- `/fund/list/all`
- `/fund/list/etf`
- `/fund/real/ssjy/{symbol}`

优点：
- HTTP + JSON
- 文档清晰
- Token 统一认证
- 频率限制明确
- 对指数技术指标支持较直接

缺点：
- 付费/额度约束
- 代码体系按市场拆得比较细
- 某些接口看起来强依赖“文档路径 + 代码格式”，适配层必须谨慎

项目内定位：
> `zhitu_provider` 作为实时行情、指数、北交所、科创板、技术指标、股池/板块类能力的重要 provider。

---

## 4. 项目边界与能力范围

### 4.1 v1 支持市场范围

#### 必做
- A 股主板（SH / SZ）
- 北交所（BJ）
- 科创板（688xxx）
- 沪深主要指数
- 场内基金 / ETF

#### 可选但不承诺完整
- 创业板
- 概念板块/行业板块
- 股池（涨停/跌停/强势）

#### 暂不做
- 港股
- 美股
- 期货
- 外汇
- 加密货币

原因很简单：你当前需求明确是“股票行情信息”，且智兔当前文档主要集中在中国证券市场。

---

### 4.2 v1 支持的数据类别

#### 核心
- 基础列表
- 实时行情
- 历史行情
- 市场概览

#### 增强
- 买卖五档盘口
- 技术指标（MACD / MA / BOLL / KDJ）
- 板块列表
- 股池列表

---

## 5. 总体架构设计

### 5.1 逻辑架构

```text
OpenClaw Agent / Skill
        ↓
      MCP Tools
        ↓
   Usecase / Domain Layer
        ↓
Provider Router / Symbol Resolver / Cache / Normalizer
        ↓
  ┌───────────────┬───────────────┐
  │ AKShare       │ Zhitu API     │
  │ Python SDK    │ HTTP + Token  │
  └───────────────┴───────────────┘
```

---

### 5.2 模块分层

#### 1）MCP Server 层
负责：
- tool 注册
- schema 定义
- tool 参数校验
- 输出结果封装

#### 2）Usecase 层
负责：
- `stock_search`
- `stock_quote`
- `stock_history`
- `market_overview`
- `technical_indicator`
- `market_pool`

#### 3）Domain/Service 层
负责：
- symbol 解析
- provider 选择
- 字段标准化
- fallback
- 缓存
- 错误转换

#### 4）Provider 层
负责：
- AKShare 具体实现
- 智兔 HTTP 调用
- 原始响应解析

#### 5）Infra 层
负责：
- 配置
- 日志
- HTTP 客户端
- 限流
- 重试
- 缓存实现

---

## 6. 推荐项目目录结构

```text
openclaw-stock-mcp/
├── src/
│   └── openclaw_stock_mcp/
│       ├── main.py
│       ├── server/
│       │   ├── mcp_server.py
│       │   ├── tool_registry.py
│       │   └── schemas.py
│       ├── app/
│       │   ├── usecases/
│       │   │   ├── stock_search.py
│       │   │   ├── stock_quote.py
│       │   │   ├── stock_history.py
│       │   │   ├── market_overview.py
│       │   │   ├── orderbook.py
│       │   │   ├── technical_indicator.py
│       │   │   └── market_pool.py
│       │   ├── services/
│       │   │   ├── symbol_resolver.py
│       │   │   ├── provider_router.py
│       │   │   ├── normalizer.py
│       │   │   ├── cache_service.py
│       │   │   └── summary_builder.py
│       │   └── models/
│       │       ├── instrument.py
│       │       ├── quote.py
│       │       ├── bar.py
│       │       ├── indicator.py
│       │       ├── market_pool.py
│       │       └── common.py
│       ├── providers/
│       │   ├── base.py
│       │   ├── akshare_provider.py
│       │   ├── zhitu_provider.py
│       │   ├── adapters/
│       │   │   ├── akshare_adapters.py
│       │   │   └── zhitu_adapters.py
│       │   └── errors.py
│       ├── infra/
│       │   ├── config.py
│       │   ├── http_client.py
│       │   ├── rate_limit.py
│       │   ├── retry.py
│       │   ├── logging.py
│       │   └── time_utils.py
│       └── tests/
│           ├── unit/
│           ├── integration/
│           └── fixtures/
├── docs/
│   ├── design-v1.md
│   ├── provider-mapping.md
│   ├── tools.md
│   └── skill-integration.md
├── pyproject.toml
├── README.md
├── .env.example
└── uv.lock / poetry.lock
```

---

## 7. 技术栈建议

### 7.1 语言
**Python 3.11+**

原因：
- AKShare 原生 Python
- MCP Python SDK 使用顺手
- 数据建模、适配、测试成本低

---

### 7.2 依赖建议
- MCP SDK / FastMCP
- `pydantic`：输入输出 schema
- `httpx`：智兔 HTTP 调用
- `tenacity`：重试
- `cachetools` 或 `aiocache`：缓存
- `pytest`：测试
- `respx`：mock HTTP
- `pandas`：如 AKShare 输出 DataFrame，方便适配
- `orjson`：高性能 JSON（可选）

---

### 7.3 包管理
推荐：
- `uv` 或 `poetry`

如果你想简单点，用 `uv` 即可。

---

## 8. 核心领域模型设计

### 8.1 Instrument
表示证券基础标识。

```python
class Instrument(BaseModel):
    symbol: str
    name: str | None = None
    market: Literal["CN"]
    exchange: Literal["SH", "SZ", "BJ", "BK", "INDEX", "FUND"] | None = None
    board: str | None = None
    sec_type: Literal["stock", "index", "fund", "sector"]
    raw_symbol: str | None = None
    source: str | None = None
```

---

### 8.2 Quote
```python
class Quote(BaseModel):
    symbol: str
    name: str | None = None
    sec_type: str
    market: str
    exchange: str | None = None
    board: str | None = None

    price: float | None = None
    open: float | None = None
    high: float | None = None
    low: float | None = None
    prev_close: float | None = None

    change: float | None = None
    change_percent: float | None = None
    amplitude: float | None = None

    volume: float | None = None
    turnover: float | None = None
    turnover_rate: float | None = None

    pe: float | None = None
    pb: float | None = None
    market_cap: float | None = None
    float_market_cap: float | None = None

    timestamp: str | None = None
    currency: str | None = "CNY"
    trading_status: str | None = None

    source: str
```

---

### 8.3 Bar
```python
class Bar(BaseModel):
    time: str
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None
    turnover: float | None = None
    prev_close: float | None = None
```

---

### 8.4 OrderBook
```python
class OrderBookLevel(BaseModel):
    price: float | None = None
    volume: float | None = None

class OrderBook(BaseModel):
    symbol: str
    timestamp: str | None = None
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    source: str
```

---

### 8.5 IndicatorSeries
```python
class IndicatorPoint(BaseModel):
    time: str
    values: dict[str, float | None]

class IndicatorSeries(BaseModel):
    symbol: str
    interval: str
    indicator: Literal["macd", "ma", "boll", "kdj"]
    items: list[IndicatorPoint]
    source: str
```

---

### 8.6 市场池 / 板块项
```python
class MarketPoolItem(BaseModel):
    symbol: str
    name: str
    price: float | None = None
    change_percent: float | None = None
    turnover: float | None = None
    turnover_rate: float | None = None
    market_cap: float | None = None
    extra: dict[str, Any] = {}
```

---

## 9. Symbol 标准化规则

这个是整个项目的关键之一。

### 9.1 用户输入可能形态
- `600519`
- `000001`
- `688001`
- `430017`
- `000001.SH`
- `899050.BJ`
- `平安银行`
- `北证50`
- `港股医药ETF`

---

### 9.2 内部规范

#### 股票
- 上证：`600519.SH`
- 深证：`000001.SZ`
- 北交所：`430017.BJ`
- 科创板：`688001.SH`

#### 指数
- `000001.SH`
- `399001.SZ`
- `899050.BJ`

#### 基金
- `159001.SZ`
- `510300.SH`

#### 板块
- 原样保留，如 `101076.BKZS`

---

### 9.3 解析规则建议
1. 若用户输入已带后缀，优先按后缀解析
2. 若是 6 位数字：
   - `60/68` → `SH`
   - `00/30` → `SZ`
   - `43/83/87/92` 等北交常见段 → `BJ`（这里要保守，最好结合列表确认）
3. 若是名称：
   - 先查缓存列表
   - 模糊匹配
   - 若多结果，按置信度排序
4. 若是指数/基金/板块，必须带 `sec_type` 辅助或先 search

---

### 9.4 为什么不能只靠代码前缀硬猜
因为：
- 北交所与新三板/历史代码体系容易混
- 指数和股票会重名
- 基金和股票都可能是 6 位代码

所以：
> 代码前缀只能做初步推断，最终应尽量通过列表数据校验。

---

## 10. Provider 抽象接口设计

建议定义统一 provider interface：

```python
class MarketDataProvider(Protocol):
    name: str

    def search_instruments(
        self,
        query: str,
        sec_types: list[str] | None = None,
        market: str | None = None,
        limit: int = 10,
    ) -> list[Instrument]:
        ...

    def get_quote(
        self,
        symbol: str,
        sec_type: str,
    ) -> Quote:
        ...

    def get_quotes(
        self,
        symbols: list[str],
        sec_type: str | None = None,
    ) -> list[Quote]:
        ...

    def get_history(
        self,
        symbol: str,
        sec_type: str,
        interval: str,
        start: str | None = None,
        end: str | None = None,
        limit: int | None = None,
        adjust: str | None = None,
    ) -> list[Bar]:
        ...

    def get_orderbook(
        self,
        symbol: str,
        sec_type: str,
    ) -> OrderBook:
        ...

    def get_indicator(
        self,
        symbol: str,
        sec_type: str,
        interval: str,
        indicator: str,
        start: str | None = None,
        end: str | None = None,
        limit: int | None = None,
    ) -> IndicatorSeries:
        ...

    def get_market_overview(
        self,
        market: str = "CN",
    ) -> dict:
        ...

    def get_market_pool(
        self,
        pool_type: str,
        trade_date: str | None = None,
    ) -> list[MarketPoolItem]:
        ...
```

---

## 11. Provider 实现策略

### 11.1 `akshare_provider`
职责：
- 搜索股票/指数/基金列表
- 获取基础行情和历史行情
- 作为通用兜底源

#### 适合承担
- 股票名称 / 代码映射
- A 股历史 K 线
- 指数历史数据
- 基金基础数据
- 市场概览

#### 风险
- 同一类数据可能有多个接口来源
- 某些返回 DataFrame 列名中文、且不同函数不统一
- 某些接口一旦上游网站变化就失效

#### 设计建议
- 不让 usecase 直接碰 AKShare 原始 DataFrame
- 所有 DataFrame 都在 adapter 层转为领域模型

---

### 11.2 `zhitu_provider`
职责：
- 提供实时行情、指数指标、盘口、股池、板块辅助能力
- 对北交所 / 科创板 / 指数技术指标做强补充

#### 适合承担
- 指数实时行情
- 指数历史分时 / 技术指标
- 北交所实时
- 科创板实时
- ETF / 基金实时
- 五档盘口
- 涨停/跌停/强势股池
- 板块列表

#### 设计建议
- 将智兔路径映射封装在 provider 内部
- 所有 token、base url 由 config 注入
- 对 rate limit 做 provider 级限流

---

## 12. Provider 路由与回退策略

### 12.1 默认优先级

#### 股票列表 / 基础解析
- 优先：AKShare
- 回退：智兔列表接口

#### A股实时行情
- 优先：智兔（已实测普通沪深股票实时接口 `/hs/real/ssjy/{code}`）
- 回退：AKShare

#### 北交所实时
- 优先：智兔

#### 科创板实时
- 优先：智兔

#### 指数实时 / 历史指标
- 优先：智兔

#### 基金实时
- 优先：智兔

#### 历史 K 线
- 优先：AKShare
- 回退：智兔（当该 symbol/interval 能力存在时）

---

### 12.2 失败回退原则
满足以下条件可 fallback：
- timeout
- 5xx
- 上游空数据但按业务判断不应为空
- 可重试错误

不应 fallback 的情况：
- 参数非法
- symbol 不存在
- 当前 provider 明确不支持该市场/类型，且另一个 provider 也无映射能力

---

### 12.3 tool 参数保留 provider 偏好
允许高级调用者传：

```json
{
  "provider": "zhitu"
}
```

或：

```json
{
  "provider_preference": ["zhitu", "akshare"]
}
```

但默认不要求 Skill 显式传。

---

## 13. MCP Tools 设计

v1 不建议太多工具。建议分两层：

- **对 agent 暴露的主工具**：少而稳
- **对高级场景暴露的增强工具**：可选

---

### 13.1 主工具一：`stock_search`

#### 用途
根据名称/代码模糊查证券。

#### 输入
```json
{
  "query": "平安银行",
  "sec_types": ["stock", "fund", "index"],
  "market": "CN",
  "limit": 10
}
```

#### 输出
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
      "confidence": 0.99
    }
  ],
  "source": "akshare"
}
```

#### 说明
- 这是 Skill 的入口工具之一
- 名称输入优先先走它

---

### 13.2 主工具二：`stock_quote`

#### 用途
查询一个或多个标的的实时快照。

#### 输入
```json
{
  "symbols": ["000001.SZ", "600519.SH"],
  "sec_type": "stock",
  "fields": ["price", "change_percent", "volume", "turnover"],
  "provider_preference": ["zhitu", "akshare"]
}
```

#### 输出
```json
{
  "items": [
    {
      "symbol": "000001.SZ",
      "name": "平安银行",
      "price": 12.34,
      "change": 0.12,
      "change_percent": 0.98,
      "open": 12.20,
      "high": 12.45,
      "low": 12.10,
      "prev_close": 12.22,
      "volume": 1234567,
      "turnover": 123456789.0,
      "timestamp": "2026-04-30T15:00:00+08:00",
      "source": "zhitu"
    }
  ],
  "partial_failure": false
}
```

#### 说明
- 支持批量
- 支持股票/指数/基金
- `fields` 可做裁剪，但不是必须

---

### 13.3 主工具三：`stock_history`

#### 用途
查询历史行情 / K 线 / 分时线。

#### 输入
```json
{
  "symbol": "000001.SH",
  "sec_type": "index",
  "interval": "1d",
  "start_date": "2026-01-01",
  "end_date": "2026-04-30",
  "limit": 120,
  "adjust": "none"
}
```

#### 输出
```json
{
  "symbol": "000001.SH",
  "sec_type": "index",
  "interval": "1d",
  "items": [
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
  ],
  "source": "zhitu"
}
```

#### interval 标准
统一暴露：
- `5m`
- `15m`
- `30m`
- `60m`
- `1d`
- `1w`
- `1M`
- `1y`

补充说明：
- 当前版本 **不支持 `1m`**
- 这样做是为了避免与 `1M` 月线语义混淆

内部映射：
- 智兔：`5 / 15 / 30 / 60 / d / w / m / y`
- AKShare：按具体函数映射

---

### 13.4 主工具四：`market_overview`

#### 用途
查询中国市场主要指数概览。

#### 输入
```json
{
  "market": "CN"
}
```

#### 输出
```json
{
  "market": "CN",
  "indices": [
    {"symbol": "000001.SH", "name": "上证指数", "price": 3208.9, "change_percent": 0.43},
    {"symbol": "399001.SZ", "name": "深证成指", "price": 10234.5, "change_percent": -0.11},
    {"symbol": "899050.BJ", "name": "北证50", "price": 880.3, "change_percent": 1.21}
  ],
  "timestamp": "2026-04-30T15:00:00+08:00",
  "source": "mixed"
}
```

---

### 13.5 增强工具五：`stock_orderbook`

#### 用途
查询五档盘口。

#### 输入
```json
{
  "symbol": "688001.SH",
  "sec_type": "stock"
}
```

#### 输出
```json
{
  "symbol": "688001.SH",
  "bids": [
    {"price": 11.63, "volume": 424},
    {"price": 11.62, "volume": 1291}
  ],
  "asks": [
    {"price": 11.64, "volume": 7330},
    {"price": 11.65, "volume": 7698}
  ],
  "timestamp": "2025-02-21T15:00:19+08:00",
  "source": "zhitu"
}
```

#### 说明
v1 可只支持北交所/科创板；普通 A 股是否支持要看智兔完整文档和 AKShare 实测。

---

### 13.6 增强工具六：`technical_indicator`

#### 用途
查询 MACD / MA / BOLL / KDJ。

#### 输入
```json
{
  "symbol": "000001.SH",
  "sec_type": "index",
  "interval": "1d",
  "indicator": "macd",
  "start_date": "2026-01-01",
  "end_date": "2026-04-30",
  "limit": 60
}
```

#### 输出
```json
{
  "symbol": "000001.SH",
  "indicator": "macd",
  "interval": "1d",
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

#### 说明
v1 建议先只支持 **指数技术指标**，因为智兔文档这一块最明确。

---

### 13.7 增强工具七：`market_pool`

#### 用途
查询涨停/跌停/强势股池。

#### 输入
```json
{
  "pool_type": "limit_up",
  "trade_date": "2026-04-30"
}
```

#### 输出
```json
{
  "pool_type": "limit_up",
  "trade_date": "2026-04-30",
  "items": [
    {
      "symbol": "603099.SH",
      "name": "长白山",
      "price": 29.18,
      "change_percent": 9.99,
      "turnover": 1462451424.0,
      "turnover_rate": 19.22,
      "extra": {
        "limit_count": 7,
        "first_limit_time": "09:31:27",
        "last_limit_time": "13:03:12"
      }
    }
  ],
  "source": "zhitu"
}
```

#### pool_type 映射
- `limit_up` → `/hs/pool/ztgc/{date}`
- `limit_down` → `/hs/pool/dtgc/{date}`
- `strong` → `/hs/pool/qsgc/{date}`

---

### 13.8 增强工具八：`sector_lookup`
#### 用途
查询概念板块/一级板块列表与明细。

这可以拆成两个：
- `sector_search`
- `sector_members`

但 v1 也可以先不暴露，内部预留。

---

## 14. 输入参数标准

### 14.1 sec_type
统一枚举：
- `stock`
- `index`
- `fund`
- `sector`

---

### 14.2 interval
统一枚举：
- `5m`
- `15m`
- `30m`
- `60m`
- `1d`
- `1w`
- `1M`
- `1y`

补充说明：
- 当前版本 **不支持 `1m`**
- 如后续确认上游 provider 有稳定 `1m` 数据，再单独开放
- `1M`
- `1y`

---

### 14.3 adjust
仅股票历史数据适用：
- `none`
- `qfq`
- `hfq`

指数/基金忽略该参数。

---

### 14.4 日期格式
对外统一：
- `YYYY-MM-DD`
- 或时间精确到秒：`YYYY-MM-DDTHH:mm:ss+08:00`

内部转换：
- 智兔需要时转为 `YYYYMMDD` 或 `YYYYMMDDhhmmss`

---

## 15. 标准化映射策略

### 15.1 智兔字段到统一 Quote 映射

常见字段：
- `p` → `price`
- `o` → `open`
- `h` → `high`
- `l` → `low`
- `yc` → `prev_close`
- `ud` → `change`
- `pc` → `change_percent`
- `zf` → `amplitude`
- `cje` → `turnover`
- `v` / `tv` → `volume`
- `t` → `timestamp`
- `pe` → `pe`
- `tr` / `hs` → `turnover_rate`
- `pb_ratio` / `sjl` → `pb`
- `lt` → `float_market_cap`
- `sz` / `zsz` → `market_cap`

### 15.2 AKShare 字段映射
AKShare 需要按具体接口单独适配。原则是：
- Adapter 层统一转英文标准字段
- 上层永不感知中文列名

---

## 16. 错误模型设计

统一错误结构：

```json
{
  "error": {
    "code": "SYMBOL_NOT_FOUND",
    "message": "Instrument not found: 平安银航",
    "provider": "resolver",
    "retryable": false,
    "details": {}
  }
}
```

### 推荐错误码
- `INVALID_ARGUMENT`
- `SYMBOL_NOT_FOUND`
- `AMBIGUOUS_SYMBOL`
- `UNSUPPORTED_SEC_TYPE`
- `UNSUPPORTED_MARKET`
- `UNSUPPORTED_INTERVAL`
- `PROVIDER_AUTH_FAILED`
- `PROVIDER_RATE_LIMITED`
- `PROVIDER_TIMEOUT`
- `PROVIDER_UNAVAILABLE`
- `UPSTREAM_SCHEMA_CHANGED`
- `EMPTY_RESULT`
- `INTERNAL_ERROR`

### 说明
- `AMBIGUOUS_SYMBOL` 很重要，给 Skill 提示先 search 再 quote
- `UPSTREAM_SCHEMA_CHANGED` 对 AKShare 特别重要

---

## 17. 缓存设计

必须做，不然后面 agent 很容易打爆。

### 17.1 缓存层级
- 进程内缓存：v1 足够
- 后续如需横向扩展，再上 Redis

### 17.2 TTL 建议

#### 列表类
- 股票列表：24h
- 指数列表：24h
- 基金列表：24h
- 板块列表：24h

#### 快照类
- quote：10s
- market_overview：10s
- orderbook：2~5s

#### 历史类
- history：1h
- technical_indicator：5m~1h
- market_pool：10m

### 17.3 cache key 设计
例如：
- `search:{query}:{sec_types}:{limit}`
- `quote:{symbol}:{sec_type}`
- `history:{symbol}:{interval}:{start}:{end}:{adjust}`
- `indicator:{symbol}:{interval}:{indicator}:{start}:{end}:{limit}`

---

## 18. 限流与重试

### 18.1 智兔限流
文档显示不同套餐频率不同。v1 设计上不要写死套餐数值，配置化：

```env
ZHITU_RATE_LIMIT_PER_MINUTE=300
```

内部使用 token bucket / leaky bucket。

### 18.2 AKShare 限制
AKShare 本身不一定限制，但底层数据源可能限制或封禁。  
建议：
- 对高频接口做请求合并
- 对失败接口做短期熔断

### 18.3 重试策略
仅对这些场景重试：
- 网络超时
- 临时 5xx
- 连接错误

不对这些重试：
- 4xx 参数错误
- symbol 不存在
- token 认证失败

推荐：
- 最大 2~3 次
- 指数退避
- 整体 tool 调用超时要有上限

---

## 19. 配置设计

`.env.example` 建议：

```env
APP_ENV=dev
LOG_LEVEL=INFO

MCP_SERVER_NAME=openclaw-stock-mcp
MCP_SERVER_VERSION=0.1.0

DEFAULT_MARKET=CN
DEFAULT_PROVIDER_ORDER=akshare,zhitu
ENABLE_PROVIDER_FALLBACK=true

AKSHARE_ENABLED=true
AKSHARE_TIMEOUT_SECONDS=20

ZHITU_ENABLED=true
ZHITU_BASE_URL=https://api.zhituapi.com
ZHITU_TOKEN=
ZHITU_TIMEOUT_SECONDS=15
ZHITU_RATE_LIMIT_PER_MINUTE=300

CACHE_TTL_LIST_SECONDS=86400
CACHE_TTL_QUOTE_SECONDS=10
CACHE_TTL_OVERVIEW_SECONDS=10
CACHE_TTL_HISTORY_SECONDS=3600
CACHE_TTL_INDICATOR_SECONDS=300
CACHE_TTL_ORDERBOOK_SECONDS=3
CACHE_TTL_POOL_SECONDS=600
```

---

## 20. 日志与可观测性

### 20.1 日志必须包含
- request id
- tool name
- provider
- symbol
- sec_type
- latency
- cache hit/miss
- fallback 여부
- error code

### 20.2 脱敏要求
- 不打印智兔 token
- 不完整打印敏感 header
- 原始响应只截断摘要

### 20.3 建议加的指标
如果后面要稳定运行，最好记录：
- tool 调用次数
- provider 成功率
- provider 平均时延
- fallback 触发次数
- cache 命中率

---

## 21. Skill 集成设计

Skill 的职责不是“懂智兔接口”，而是“知道什么时候调用哪个 MCP tool”。

### 21.1 Skill 调用原则
1. 用户输入名称不明确 → 先 `stock_search`
2. 用户问当前价格/涨跌 → `stock_quote`
3. 用户问近期走势 → `stock_history`
4. 用户问技术指标 → `technical_indicator`
5. 用户问大盘 → `market_overview`
6. 用户问涨停股/强势股 → `market_pool`

### 21.2 Skill 回复原则
- 默认用中文
- 默认说明时间点
- 不擅自给投资建议
- 只陈述数据与趋势，不输出“买入/卖出建议”除非用户明确要求分析

### 21.3 Skill 错误回退
- `AMBIGUOUS_SYMBOL` → 让 agent 先展示候选
- `SYMBOL_NOT_FOUND` → 建议改用名称或完整代码
- `PROVIDER_RATE_LIMITED` → 稍后重试
- `EMPTY_RESULT` → 提示可能非交易时段 / 日期不存在

---

## 22. 测试策略

### 22.1 单元测试
覆盖：
- symbol 解析
- interval 映射
- 日期格式转换
- provider 字段适配
- 错误码转换

### 22.2 集成测试
覆盖：
- AKShare provider 实调（可选 nightly）
- 智兔 provider mock / 实调
- fallback 流程
- cache 命中流程

### 22.3 回归测试重点
- 上游字段变化
- symbol 正规化
- 指数 / 基金 / 北交所特殊路径
- 智兔技术指标路径

---

## 23. 开发里程碑建议

### Phase 1：骨架
- MCP server
- config
- logging
- provider interface
- domain models

### Phase 2：AKShare provider
- search
- quote
- history
- overview

### Phase 3：Zhitu provider
- list
- real quote
- index history
- indicators
- orderbook
- pool

### Phase 4：Router + Cache + Fallback
- provider order
- timeout
- retry
- fallback
- TTL cache

### Phase 5：Tool 完整输出
- summary
- partial failure
- structured errors

### Phase 6：Skill 对接
- 编写 Skill 使用说明
- 验证 agent 调用链

---

## 24. v1 推荐的最小交付范围

如果你想先做一个真正能用的 v1，我建议只交付下面这些：

### 必做 tool
- `stock_search`
- `stock_quote`
- `stock_history`
- `market_overview`

### 可选增强
- `technical_indicator`
- `market_pool`

### 暂缓
- `stock_orderbook`
- `sector_lookup`

原因：
- 前四个已经覆盖 80% 以上的“查行情”需求
- `technical_indicator` 对指数分析很有价值
- `market_pool` 适合题材/短线场景
- 五档盘口对 agent 的泛用性没那么高，可以第二阶段再做

---

## 25. 关键风险与规避建议

### 风险 1：AKShare 上游不稳定
**规避：**
- adapter 隔离
- fallback 到智兔
- 错误码标准化

### 风险 2：智兔额度/限流
**规避：**
- 配置化限流
- 缓存
- 支持 provider 优先级切换

### 风险 3：symbol 格式混乱
**规避：**
- 强制 canonical symbol
- 所有 tool 内部统一 resolve

### 风险 4：LLM 乱用工具
**规避：**
- tool 数量控制
- schema 清晰
- Skill 明确调用顺序

### 风险 5：输出过大
**规避：**
- 历史数据加 limit
- 默认 limit 合理
- 板块/股池支持 top_n

---

## 26. 明确结论

这套项目 v1 最合理的定位是：

> **一个面向 OpenClaw Agent 的中国证券市场行情 MCP 能力层**  
> 底层整合 AKShare 与智兔，对上暴露统一、可维护、适合 LLM 使用的工具接口。

### 建议的 v1 核心决策
1. **语言选 Python**
2. **AKShare 直连，智兔 HTTP**
3. **先做 4 个核心 tool**
4. **统一 symbol / quote / history / indicator 模型**
5. **内部做 provider fallback**
6. **Skill 只负责调用策略，不碰底层 provider 细节**

---

## 27. 后续建议

建议下一步直接进入“设计落地”阶段，可继续补齐：

1. 《接口与 Schema 设计文档 v1.1》
2. 项目骨架代码
3. Skill 设计草案
4. Provider 映射表与测试样例
