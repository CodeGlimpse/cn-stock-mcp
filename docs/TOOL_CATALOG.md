# Tool Catalog (`cn-stock-mcp`)

> 本文件由当前 MCP registry 和 Pydantic schema 生成。请使用 `cn-stock-mcp --list-tools --json` 获取机器可读目录，或使用 `cn-stock-mcp --describe-tool <name>` 查询单个工具。

工具总数：**53**

## 工具索引

| Tool | Provider route | Description |
|---|---|---|
| `block_trade` | `akshare` | Get block trade (大宗交易) data: daily trade detail with buyer/seller broker, daily stock summary with discount rate, industry aggregation, broker success-rate ranking, and active stock tracking. Supports date range and period-based queries. |
| `capital_flow` | `akshare` | Get capital flow data: market-level, individual stock, or sector (industry/concept) fund flow ranking. |
| `convertible_bond` | `akshare` | Get convertible bond (可转债) data: real-time snapshot with double-low/premium/YTM, call/redeem monitoring, and bond index history. Supports double-low strategy screening and call-status filtering. |
| `derivatives_data` | `akshare` | Get derivatives data: futures real-time quotes and history, option contract lists (SSE/SZSE), and QVIX implied volatility index. Supports multiple futures symbols and QVIX underlyings. |
| `disclosure_calendar` | `akshare` | Get disclosure calendar (披露日历): financial report disclosure schedule with first-scheduled date, change history, and actual disclosure date. Filter by market, period, status (disclosed/pending/changed). |
| `dividend_rank` | `akshare` | Get dividend data (股息率/分红排名): market-wide historical dividend ranking by cumulative/average yield, per-report-period dividend plan with yield/EPS/BVPS, and per-stock historical dividend detail. Supports sorting and filtering. |
| `dragon_tiger` | `akshare` | Get dragon-tiger board (龙虎榜) data: daily listed stocks with buy/sell detail, institution participation, active broker tracking, broker success-rate ranking, and stock board statistics. |
| `earnings_quality` | `akshare` | Evaluate earnings quality from financial snapshot (deduct ratio, growth consistency, cash conversion, ROE, leverage). |
| `etf_snapshot` | `akshare` | Get ETF market snapshot: real-time quotes with IOPV/discount rate/main net inflow, ETF share/scale, and NAV history. Supports full-market sorting and discount-rate filtering. |
| `event_calendar` | `zhitu` | Build event timeline (dividend/unlock/profit) for one or more stocks. |
| `fund_flow` | `akshare` | Get fund flow data (主力资金流向): market-level 120-day trend (主力/超大单/大单/中单/小单), industry 90-sector ranking with net inflow, individual stock 120-day history. Sina source. |
| `hot_theme_tracker` | `akshare, zhitu` | Track hot themes by combining sector rotation and pool snapshots. |
| `index_compose` | `akshare` | Get index constituents and weights for index benchmarking/enhanced strategy construction. |
| `index_enhance` | `akshare` | Compare an enhanced top-constituent portfolio against its benchmark index: benchmark return, weighted/equal enhanced return, excess return, member contribution and outperform/underperform counts. |
| `industry_chain` | `akshare` | Get industry chain data (产业链上下游): THS industry board summary with change/inflow/leaders, concept board summary with driver events/leaders. For understanding sector relationships and theme tracking. |
| `industry_valuation_rank` | `zhitu, akshare` | Rank primary sectors by valuation percentile using member stock PE/PB aggregation. |
| `insider_trade` | `akshare` | Get insider/shareholder trade data (高管增减持): top 10 free-float shareholders with holding changes, and historical insider trade records (buy/sell by executives/controlling shareholders). Single-stock query. |
| `institute_hold` | `akshare` | Get institute holding (机构持仓) data: quarterly market-wide summary with institution count and holding ratio changes, and per-stock detail with individual institution breakdown. Supports auto-quarter detection. |
| `limit_stat` | `akshare` | Get limit statistics for a trading day: seal rate, consecutive board distribution, broken limit count, yesterday-continue rate, sector breakdown. |
| `limit_up_pool` | `akshare` | Get limit-up/limit-down pool analysis (涨停/跌停股池历史分析): limit-up, limit-down, strong/continuous, previous-day limit performance, sub-new, and broken-limit pools by trade date. EastMoney source. |
| `macro_indicator` | `akshare` | Get macro economic indicators (CPI/PPI/PMI/GDP/LPR/M2/etc.) for CN/USA/Euro/Global regions. Supports latest value, history, calendar, and overview modes. |
| `margin_trading` | `akshare` | Get margin trading (融资融券) data: market-level summary with financing/securities balance, and stock-level detail with financing buy/sell and securities volume. Supports SSE/SZSE exchanges. |
| `market_brief` | `akshare, zhitu` | Generate a compact market brief by combining overview and pool data. |
| `market_overview` | `zhitu, akshare` | Get high-level overview of China market major indices. |
| `market_pool` | `zhitu` | Get market pools such as limit-up, limit-down, strong, sub-new, and broken-limit stocks. |
| `money_rate` | `akshare` | Get money market rates (货币市场利率): SHIBOR full-term curve (O/N~1Y), interbank rate by tenor, repo fixing rates (FR/FDR). Supports latest and historical modes. |
| `multi_timeframe_review` | `akshare, zhitu` | Review a symbol across multiple timeframes and summarize alignment/conflicts. |
| `northbound` | `akshare` | Get northbound capital data: daily flow summary and historical trend. |
| `provider_health` | `akshare, zhitu` | Run provider self checks for zhitu and akshare. |
| `sec_reveal` | `akshare` | Deep dragon-tiger seat reveal (龙虎榜机构席位深度): stock buy/sell seat detail, active broker seats, institution detail, and institution trace/ranking. EastMoney + Sina sources. |
| `sector_leaders` | `akshare, zhitu` | Get leaders/followers/draggers snapshot for a sector. |
| `sector_lookup` | `zhitu` | Lookup sector lists and members. |
| `sector_review` | `akshare, zhitu` | Generate a review summary for a sector by aggregating its member stocks. |
| `sector_rotation_review` | `akshare, zhitu` | Compare multiple sectors and summarize cross-sector rotation signals. |
| `shareholder_change` | `akshare` | Get shareholder change data (股东变动): top 10 shareholders with holding changes per stock, and market-wide shareholder holding change summary (by shareholder type: fund/SSF/QFII/etc). Quarterly data. |
| `stock_candidate_scan` | `akshare, zhitu` | Scan a stock universe and rank candidate setups. |
| `stock_compare` | `zhitu, akshare` | Compare multiple stocks side-by-side (多股横向对比): real-time quote, PE/PB/market_cap valuation, financial indicators (ROE/margin/debt), dividend yield. 2-10 symbols, layered data loading minimizes API calls. |
| `stock_financial` | `akshare` | Get financial statement data for a stock: core metrics snapshot, history trend, and detailed income/balance/cashflow statements. |
| `stock_history` | `akshare, zhitu` | Get historical price bars for an instrument. |
| `stock_orderbook` | `zhitu` | Get order book data for supported instruments. |
| `stock_profile` | `zhitu` | Get company profile including basic info, dividends, unlocks, and quarterly profits. |
| `stock_quote` | `akshare, zhitu` | Get real-time quotes for one or more instruments. |
| `stock_repurchase` | `akshare` | Get stock repurchase data (回购明细): company buyback plans with price range, quantity, progress, and actual repurchase amount. Filter by progress status (董事会预案/股东大会通过/实施中/完成实施). |
| `stock_review` | `akshare` | Generate a review summary for a stock on a trade date or over a date range. |
| `stock_review_batch` | `akshare, zhitu` | Batch review multiple stocks and rank the results for replay workflows. |
| `stock_screen` | `akshare` | Screen/filter A-share stocks by market, price range, change percent, volume, turnover, amplitude. Returns sorted results from real-time Sina source. Like a basic stock screener. |
| `stock_search` | `akshare, zhitu` | Search stocks, indices, funds, or sectors by keyword or code. |
| `stock_snapshot` | `composite, zhitu, akshare` | Get a bounded multi-source stock snapshot combining quote, recent history, financial summary, valuation, events, and risk tags; no trading actions. |
| `stock_warrant` | `akshare` | Get option/warrant data (权证/期权): ETF options (50ETF/300ETF/etc), commodity options (4 exchanges), CFFEX index options. Real-time quotes with price/volume/open_interest/strike. |
| `technical_indicator` | `akshare, zhitu` | Get technical indicator series such as MACD, MA, BOLL, KDJ. |
| `trading_calendar` | `akshare` | Query China trading-day calendar for review and backtesting workflows. |
| `valuation_rank` | `zhitu, akshare` | Rank stock valuation using PE/PB and combine with market valuation temperature (PE/PB quantiles, dividend yield). |
| `watchlist_review` | `akshare, zhitu` | Review and prioritize a watchlist of symbols. |

## 统一说明

成功响应的顶层 `meta` 包含 freshness 和 `data_quality_v1`。freshness 的 `status=realtime` 只表示源数据带有时间级字段，不代表交易所当前处于交易时段。

常见错误：`INVALID_ARGUMENT`、`PROVIDER_TIMEOUT`、`PROVIDER_UNAVAILABLE`、`PROVIDER_AUTH_FAILED`、`UNSUPPORTED_MARKET`。

## 工具详情

### `block_trade`

Get block trade (大宗交易) data: daily trade detail with buyer/seller broker, daily stock summary with discount rate, industry aggregation, broker success-rate ranking, and active stock tracking. Supports date range and period-based queries.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "daily_detail",
    "daily_stat"
  ],
  "period": "近一月",
  "industry_period": "近3日",
  "sort_by": "turnover",
  "descending": true,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "daily_detail",
        "daily_stat"
      ],
      "items": {
        "enum": [
          "daily_detail",
          "daily_stat",
          "industry_stat",
          "broker_rank",
          "active_stock"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "period": {
      "default": "近一月",
      "enum": [
        "近一月",
        "近三月",
        "近六月",
        "近一年"
      ],
      "title": "Period",
      "type": "string"
    },
    "industry_period": {
      "default": "近3日",
      "enum": [
        "近3日",
        "近5日",
        "近10日",
        "近30日"
      ],
      "title": "Industry Period",
      "type": "string"
    },
    "sort_by": {
      "default": "turnover",
      "enum": [
        "turnover",
        "discount_rate",
        "turnover_to_float_cap",
        "listed_count",
        "avg_return_5d"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 500,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "BlockTradeRequest",
  "type": "object"
}
```

### `capital_flow`

Get capital flow data: market-level, individual stock, or sector (industry/concept) fund flow ranking.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "flow_type": "market",
  "limit": 20,
  "sort_by": "net_amount",
  "descending": true,
  "allow_stale": false,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "flow_type": {
      "default": "market",
      "enum": [
        "market",
        "individual",
        "industry",
        "concept"
      ],
      "title": "Flow Type",
      "type": "string"
    },
    "symbol": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Symbol"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "limit": {
      "default": 60,
      "maximum": 500,
      "minimum": 1,
      "title": "Limit",
      "type": "integer"
    },
    "sort_by": {
      "default": "net_amount",
      "enum": [
        "net_amount",
        "inflow",
        "outflow",
        "sector_change_percent",
        "company_count"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 200,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "allow_stale": {
      "default": false,
      "description": "Allow a clearly marked cached result when the upstream is unavailable",
      "title": "Allow Stale",
      "type": "boolean"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "CapitalFlowRequest",
  "type": "object"
}
```

### `convertible_bond`

Get convertible bond (可转债) data: real-time snapshot with double-low/premium/YTM, call/redeem monitoring, and bond index history. Supports double-low strategy screening and call-status filtering.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "spot"
  ],
  "sort_by": "double_low",
  "descending": false,
  "history_n": 60,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "spot"
      ],
      "items": {
        "enum": [
          "spot",
          "redeem",
          "index"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "sort_by": {
      "default": "double_low",
      "enum": [
        "double_low",
        "conv_premium",
        "ytm",
        "change_percent",
        "turnover",
        "remaining_years"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": false,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 500,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "min_double_low": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "双低下限",
      "title": "Min Double Low"
    },
    "max_double_low": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "双低上限",
      "title": "Max Double Low"
    },
    "max_conv_premium": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "溢价率上限筛选",
      "title": "Max Conv Premium"
    },
    "min_ytm": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "到期收益率下限筛选",
      "title": "Min Ytm"
    },
    "call_status_filter": {
      "anyOf": [
        {
          "enum": [
            "all",
            "called",
            "near_call",
            "safe"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "强赎状态筛选",
      "title": "Call Status Filter"
    },
    "history_n": {
      "default": 60,
      "maximum": 500,
      "minimum": 1,
      "title": "History N",
      "type": "integer"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "ConvertibleBondRequest",
  "type": "object"
}
```

### `derivatives_data`

Get derivatives data: futures real-time quotes and history, option contract lists (SSE/SZSE), and QVIX implied volatility index. Supports multiple futures symbols and QVIX underlyings.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "futures_spot",
    "qvix"
  ],
  "futures_symbol": "RB0",
  "option_exchange": "both",
  "qvix_underlying": "50etf",
  "history_n": 60,
  "option_type_filter": "all",
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "futures_spot",
        "qvix"
      ],
      "items": {
        "enum": [
          "futures_spot",
          "futures_hist",
          "option_list",
          "qvix"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "futures_symbol": {
      "default": "RB0",
      "description": "期货合约代码，如 RB0=螺纹钢主力, I0=铁矿石主力, AU0=黄金主力",
      "title": "Futures Symbol",
      "type": "string"
    },
    "option_exchange": {
      "default": "both",
      "description": "期权交易所选择",
      "enum": [
        "SSE",
        "SZSE",
        "both"
      ],
      "title": "Option Exchange",
      "type": "string"
    },
    "qvix_underlying": {
      "default": "50etf",
      "enum": [
        "50etf",
        "300etf",
        "500etf",
        "100etf",
        "50index",
        "300index",
        "1000index",
        "kcb",
        "cyb"
      ],
      "title": "Qvix Underlying",
      "type": "string"
    },
    "history_n": {
      "default": 60,
      "maximum": 500,
      "minimum": 1,
      "title": "History N",
      "type": "integer"
    },
    "option_type_filter": {
      "default": "all",
      "description": "认购/认沽筛选",
      "enum": [
        "all",
        "call",
        "put"
      ],
      "title": "Option Type Filter",
      "type": "string"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "DerivativesDataRequest",
  "type": "object"
}
```

### `disclosure_calendar`

Get disclosure calendar (披露日历): financial report disclosure schedule with first-scheduled date, change history, and actual disclosure date. Filter by market, period, status (disclosed/pending/changed).

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "market": "沪深京",
  "period": "auto",
  "sec_type": "stock",
  "status": "all",
  "sort_by": "first_schedule",
  "descending": false,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "market": {
      "default": "沪深京",
      "enum": [
        "沪深京",
        "深市",
        "沪市",
        "京市"
      ],
      "title": "Market",
      "type": "string"
    },
    "period": {
      "default": "auto",
      "description": "报告期：YYYY年报/YYYY一季/YYYY半年/YYYY三季，如 '2024年报'/'2025一季'，或 'auto'",
      "title": "Period",
      "type": "string"
    },
    "symbol": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Symbol"
    },
    "sec_type": {
      "default": "stock",
      "title": "Sec Type",
      "type": "string"
    },
    "status": {
      "default": "all",
      "enum": [
        "all",
        "disclosed",
        "pending",
        "changed"
      ],
      "title": "Status",
      "type": "string"
    },
    "sort_by": {
      "default": "first_schedule",
      "enum": [
        "first_schedule",
        "actual_date"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": false,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 1000,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "DisclosureCalendarRequest",
  "type": "object"
}
```

### `dividend_rank`

Get dividend data (股息率/分红排名): market-wide historical dividend ranking by cumulative/average yield, per-report-period dividend plan with yield/EPS/BVPS, and per-stock historical dividend detail. Supports sorting and filtering.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "rank",
    "plan"
  ],
  "report_date": "latest",
  "sec_type": "stock",
  "sort_by": "avg_annual_dividend",
  "descending": true,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "rank",
        "plan"
      ],
      "items": {
        "enum": [
          "rank",
          "plan",
          "detail"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "report_date": {
      "default": "latest",
      "enum": [
        "latest",
        "20241231",
        "20231231",
        "20221231",
        "20211231",
        "20201231"
      ],
      "title": "Report Date",
      "type": "string"
    },
    "symbol": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Symbol"
    },
    "sec_type": {
      "default": "stock",
      "title": "Sec Type",
      "type": "string"
    },
    "sort_by": {
      "default": "avg_annual_dividend",
      "enum": [
        "avg_annual_dividend",
        "total_dividend",
        "dividend_count",
        "dividend_yield",
        "cash_dividend_ratio",
        "eps"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 500,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "DividendRankRequest",
  "type": "object"
}
```

### `dragon_tiger`

Get dragon-tiger board (龙虎榜) data: daily listed stocks with buy/sell detail, institution participation, active broker tracking, broker success-rate ranking, and stock board statistics.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "daily_detail",
    "institution"
  ],
  "period": "近一月",
  "sort_by": "net_buy_amount",
  "descending": true,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "daily_detail",
        "institution"
      ],
      "items": {
        "enum": [
          "daily_detail",
          "institution",
          "active_broker",
          "broker_rank",
          "stock_stat"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "period": {
      "default": "近一月",
      "enum": [
        "近一月",
        "近三月",
        "近六月",
        "近一年"
      ],
      "title": "Period",
      "type": "string"
    },
    "sort_by": {
      "default": "net_buy_amount",
      "enum": [
        "net_buy_amount",
        "turnover_amount",
        "buy_amount",
        "inst_net_buy",
        "listed_count"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 500,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "DragonTigerRequest",
  "type": "object"
}
```

### `earnings_quality`

Evaluate earnings quality from financial snapshot (deduct ratio, growth consistency, cash conversion, ROE, leverage).

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "symbol": "600519.SH",
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "symbol": {
      "minLength": 1,
      "title": "Symbol",
      "type": "string"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "required": [
    "symbol"
  ],
  "title": "EarningsQualityRequest",
  "type": "object"
}
```

### `etf_snapshot`

Get ETF market snapshot: real-time quotes with IOPV/discount rate/main net inflow, ETF share/scale, and NAV history. Supports full-market sorting and discount-rate filtering.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "spot"
  ],
  "sort_by": "turnover",
  "descending": true,
  "top_n": 20,
  "history_n": 30,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "spot"
      ],
      "items": {
        "enum": [
          "spot",
          "scale",
          "nav"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "symbol": {
      "anyOf": [
        {
          "minLength": 1,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Symbol"
    },
    "sort_by": {
      "default": "turnover",
      "enum": [
        "turnover",
        "change_percent",
        "discount_rate",
        "main_net_inflow",
        "volume",
        "total_market_cap"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "default": 20,
      "maximum": 200,
      "minimum": 1,
      "title": "Top N",
      "type": "integer"
    },
    "min_discount": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "折价率下限筛选（负数=折价）",
      "title": "Min Discount"
    },
    "max_discount": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "溢价率上限筛选（正数=溢价）",
      "title": "Max Discount"
    },
    "history_n": {
      "default": 30,
      "maximum": 500,
      "minimum": 1,
      "title": "History N",
      "type": "integer"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "ETFSnapshotRequest",
  "type": "object"
}
```

### `event_calendar`

Build event timeline (dividend/unlock/profit) for one or more stocks.

Provider route: `zhitu`; fallback: `none`

最小示例：

```json
{
  "symbols": [
    "600519.SH"
  ],
  "next_event_only": false,
  "provider": "zhitu"
}
```

Input schema：

```json
{
  "properties": {
    "symbols": {
      "items": {
        "type": "string"
      },
      "maxItems": 100,
      "minItems": 1,
      "title": "Symbols",
      "type": "array"
    },
    "event_types": {
      "anyOf": [
        {
          "items": {
            "enum": [
              "dividend",
              "unlock",
              "profit"
            ],
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Event Types"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "next_event_only": {
      "default": false,
      "title": "Next Event Only",
      "type": "boolean"
    },
    "event_priority": {
      "anyOf": [
        {
          "items": {
            "enum": [
              "dividend",
              "unlock",
              "profit"
            ],
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Event Priority"
    },
    "provider": {
      "anyOf": [
        {
          "const": "zhitu",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "zhitu",
      "title": "Provider"
    }
  },
  "required": [
    "symbols"
  ],
  "title": "EventCalendarRequest",
  "type": "object"
}
```

### `fund_flow`

Get fund flow data (主力资金流向): market-level 120-day trend (主力/超大单/大单/中单/小单), industry 90-sector ranking with net inflow, individual stock 120-day history. Sina source.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "market",
    "industry"
  ],
  "period": "即时",
  "sort_by": "net_inflow",
  "descending": true,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "market",
        "industry"
      ],
      "items": {
        "enum": [
          "market",
          "industry",
          "stock"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "period": {
      "default": "即时",
      "enum": [
        "即时",
        "3日",
        "5日",
        "10日"
      ],
      "title": "Period",
      "type": "string"
    },
    "symbol": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Stock code required when include='stock', e.g. 600519",
      "title": "Symbol"
    },
    "sort_by": {
      "default": "net_inflow",
      "enum": [
        "net_inflow",
        "inflow",
        "change_pct"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 200,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "FundFlowRequest",
  "type": "object"
}
```

### `hot_theme_tracker`

Track hot themes by combining sector rotation and pool snapshots.

Provider route: `akshare`; fallback: `zhitu`

最小示例：

```json
{
  "sector_type": "primary",
  "adjust": "none",
  "provider": "zhitu",
  "sort_by": "avg_relative_strength",
  "descending": true,
  "top_n": 5,
  "sector_limit": 10,
  "member_limit": 20,
  "member_top_n": 3,
  "pool_top_n": 5,
  "include_pool_snapshot": true
}
```

Input schema：

```json
{
  "properties": {
    "sector_names": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "maxItems": 20,
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Sector Names"
    },
    "sector_type": {
      "default": "primary",
      "enum": [
        "concept",
        "primary"
      ],
      "title": "Sector Type",
      "type": "string"
    },
    "watch_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Watch Name"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "adjust": {
      "default": "none",
      "enum": [
        "none",
        "qfq",
        "hfq"
      ],
      "title": "Adjust",
      "type": "string"
    },
    "provider": {
      "anyOf": [
        {
          "const": "zhitu",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "zhitu",
      "title": "Provider"
    },
    "sort_by": {
      "default": "avg_relative_strength",
      "enum": [
        "avg_relative_strength",
        "avg_return",
        "positive_ratio",
        "stronger_ratio",
        "sentiment_score",
        "rotation_score"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "default": 5,
      "maximum": 20,
      "minimum": 1,
      "title": "Top N",
      "type": "integer"
    },
    "sector_limit": {
      "default": 10,
      "maximum": 30,
      "minimum": 2,
      "title": "Sector Limit",
      "type": "integer"
    },
    "member_limit": {
      "default": 20,
      "maximum": 200,
      "minimum": 1,
      "title": "Member Limit",
      "type": "integer"
    },
    "member_top_n": {
      "default": 3,
      "maximum": 10,
      "minimum": 1,
      "title": "Member Top N",
      "type": "integer"
    },
    "pool_top_n": {
      "default": 5,
      "maximum": 20,
      "minimum": 1,
      "title": "Pool Top N",
      "type": "integer"
    },
    "include_pool_snapshot": {
      "default": true,
      "title": "Include Pool Snapshot",
      "type": "boolean"
    },
    "min_relative_strength": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Relative Strength"
    },
    "min_return": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Return"
    },
    "max_drawdown_limit": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Max Drawdown Limit"
    },
    "min_volume_ratio": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Volume Ratio"
    }
  },
  "title": "HotThemeTrackerRequest",
  "type": "object"
}
```

### `index_compose`

Get index constituents and weights for index benchmarking/enhanced strategy construction.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "index_code": "example",
  "include_weight": true,
  "sort_by": "weight",
  "descending": true,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "index_code": {
      "minLength": 1,
      "title": "Index Code",
      "type": "string"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 1000,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "include_weight": {
      "default": true,
      "title": "Include Weight",
      "type": "boolean"
    },
    "sort_by": {
      "default": "weight",
      "enum": [
        "weight",
        "symbol"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "required": [
    "index_code"
  ],
  "title": "IndexComposeRequest",
  "type": "object"
}
```

### `index_enhance`

Compare an enhanced top-constituent portfolio against its benchmark index: benchmark return, weighted/equal enhanced return, excess return, member contribution and outperform/underperform counts.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "index_code": "example",
  "top_n": 50,
  "weighting": "weight",
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "index_code": {
      "description": "Index code, e.g. 000300 or 000300.SH",
      "minLength": 1,
      "title": "Index Code",
      "type": "string"
    },
    "top_n": {
      "default": 50,
      "description": "Top-weight constituents used as the enhanced sample",
      "maximum": 300,
      "minimum": 1,
      "title": "Top N",
      "type": "integer"
    },
    "weighting": {
      "default": "weight",
      "description": "Use index weights or equal weights for the sample portfolio",
      "enum": [
        "weight",
        "equal"
      ],
      "title": "Weighting",
      "type": "string"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional YYYYMMDD start date for benchmark history lookup",
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional YYYYMMDD end date for benchmark history lookup",
      "title": "End Date"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "required": [
    "index_code"
  ],
  "title": "IndexEnhanceRequest",
  "type": "object"
}
```

### `industry_chain`

Get industry chain data (产业链上下游): THS industry board summary with change/inflow/leaders, concept board summary with driver events/leaders. For understanding sector relationships and theme tracking.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "industry_list"
  ],
  "sort_by": "change_pct",
  "descending": true,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "industry_list"
      ],
      "items": {
        "enum": [
          "industry_list",
          "concept_list"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "sort_by": {
      "default": "change_pct",
      "enum": [
        "change_pct",
        "net_inflow",
        "turnover",
        "volume",
        "up_count"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 200,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "IndustryChainRequest",
  "type": "object"
}
```

### `industry_valuation_rank`

Rank primary sectors by valuation percentile using member stock PE/PB aggregation.

Provider route: `zhitu`; fallback: `akshare`

最小示例：

```json
{
  "sector_names": [
    "银行",
    "证券"
  ],
  "sector_type": "primary",
  "sort_by": "pe_median",
  "descending": false,
  "member_limit": 200,
  "provider": "zhitu"
}
```

Input schema：

```json
{
  "properties": {
    "sector_names": {
      "items": {
        "type": "string"
      },
      "maxItems": 30,
      "minItems": 1,
      "title": "Sector Names",
      "type": "array"
    },
    "sector_type": {
      "default": "primary",
      "enum": [
        "concept",
        "primary"
      ],
      "title": "Sector Type",
      "type": "string"
    },
    "sort_by": {
      "default": "pe_median",
      "enum": [
        "pe_median",
        "pb_median",
        "valuation_percentile",
        "quote_coverage_count"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": false,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 30,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "member_limit": {
      "default": 200,
      "maximum": 500,
      "minimum": 10,
      "title": "Member Limit",
      "type": "integer"
    },
    "provider": {
      "anyOf": [
        {
          "enum": [
            "zhitu",
            "akshare"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "zhitu",
      "title": "Provider"
    }
  },
  "required": [
    "sector_names"
  ],
  "title": "IndustryValuationRankRequest",
  "type": "object"
}
```

### `insider_trade`

Get insider/shareholder trade data (高管增减持): top 10 free-float shareholders with holding changes, and historical insider trade records (buy/sell by executives/controlling shareholders). Single-stock query.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "top10",
    "change"
  ],
  "symbol": "600519.SH",
  "sec_type": "stock",
  "quarter": "auto",
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "top10",
        "change"
      ],
      "items": {
        "enum": [
          "top10",
          "change"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "symbol": {
      "title": "Symbol",
      "type": "string"
    },
    "sec_type": {
      "default": "stock",
      "title": "Sec Type",
      "type": "string"
    },
    "quarter": {
      "default": "auto",
      "enum": [
        "auto",
        "20261",
        "20254",
        "20253",
        "20252",
        "20251",
        "20244",
        "20243",
        "20242",
        "20241"
      ],
      "title": "Quarter",
      "type": "string"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 50,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "required": [
    "symbol"
  ],
  "title": "InsiderTradeRequest",
  "type": "object"
}
```

### `institute_hold`

Get institute holding (机构持仓) data: quarterly market-wide summary with institution count and holding ratio changes, and per-stock detail with individual institution breakdown. Supports auto-quarter detection.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "summary"
  ],
  "quarter": "auto",
  "sec_type": "stock",
  "sort_by": "institute_count",
  "descending": true,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "summary"
      ],
      "items": {
        "enum": [
          "summary",
          "detail"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "quarter": {
      "default": "auto",
      "enum": [
        "auto",
        "20261",
        "20254",
        "20253",
        "20252",
        "20251",
        "20244",
        "20243",
        "20242",
        "20241"
      ],
      "title": "Quarter",
      "type": "string"
    },
    "symbol": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Symbol"
    },
    "sec_type": {
      "default": "stock",
      "title": "Sec Type",
      "type": "string"
    },
    "sort_by": {
      "default": "institute_count",
      "enum": [
        "institute_count",
        "hold_ratio",
        "hold_ratio_change",
        "float_ratio",
        "float_ratio_change"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 500,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "InstituteHoldRequest",
  "type": "object"
}
```

### `limit_stat`

Get limit statistics for a trading day: seal rate, consecutive board distribution, broken limit count, yesterday-continue rate, sector breakdown.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "summary",
    "limit_up",
    "broken_limit",
    "previous_day"
  ],
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "include": {
      "default": [
        "summary",
        "limit_up",
        "broken_limit",
        "previous_day"
      ],
      "items": {
        "enum": [
          "summary",
          "limit_up",
          "broken_limit",
          "previous_day",
          "limit_down"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "min_consecutive_boards": {
      "anyOf": [
        {
          "maximum": 50,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Consecutive Boards"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 500,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "LimitStatRequest",
  "type": "object"
}
```

### `limit_up_pool`

Get limit-up/limit-down pool analysis (涨停/跌停股池历史分析): limit-up, limit-down, strong/continuous, previous-day limit performance, sub-new, and broken-limit pools by trade date. EastMoney source.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "limit_up",
    "limit_down",
    "strong"
  ],
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "limit_up",
        "limit_down",
        "strong"
      ],
      "items": {
        "enum": [
          "limit_up",
          "limit_down",
          "strong",
          "previous",
          "sub_new",
          "broken"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "YYYYMMDD, defaults to today",
      "title": "Trade Date"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 500,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "LimitUpPoolRequest",
  "type": "object"
}
```

### `macro_indicator`

Get macro economic indicators (CPI/PPI/PMI/GDP/LPR/M2/etc.) for CN/USA/Euro/Global regions. Supports latest value, history, calendar, and overview modes.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "indicator": "ma",
  "region": "cn",
  "include": [
    "latest"
  ],
  "history_n": 12,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "indicator": {
      "minLength": 1,
      "title": "Indicator",
      "type": "string"
    },
    "region": {
      "default": "cn",
      "enum": [
        "cn",
        "usa",
        "euro",
        "global"
      ],
      "title": "Region",
      "type": "string"
    },
    "include": {
      "default": [
        "latest"
      ],
      "items": {
        "enum": [
          "latest",
          "history",
          "calendar",
          "overview"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "history_n": {
      "default": 12,
      "maximum": 500,
      "minimum": 1,
      "title": "History N",
      "type": "integer"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "required": [
    "indicator"
  ],
  "title": "MacroIndicatorRequest",
  "type": "object"
}
```

### `margin_trading`

Get margin trading (融资融券) data: market-level summary with financing/securities balance, and stock-level detail with financing buy/sell and securities volume. Supports SSE/SZSE exchanges.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "summary",
    "detail"
  ],
  "exchange": "both",
  "sort_by": "financing_buy",
  "descending": true,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "summary",
        "detail"
      ],
      "items": {
        "enum": [
          "summary",
          "detail"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "exchange": {
      "default": "both",
      "description": "交易所选择",
      "enum": [
        "SSE",
        "SZSE",
        "both"
      ],
      "title": "Exchange",
      "type": "string"
    },
    "sort_by": {
      "default": "financing_buy",
      "enum": [
        "financing_buy",
        "financing_balance",
        "securities_sell",
        "securities_volume"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 500,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "MarginTradingRequest",
  "type": "object"
}
```

### `market_brief`

Generate a compact market brief by combining overview and pool data.

Provider route: `akshare`; fallback: `zhitu`

最小示例：

```json
{
  "brief_type": "close",
  "market": "CN",
  "include_pools": true,
  "top_n": 5,
  "provider": "mixed"
}
```

Input schema：

```json
{
  "properties": {
    "brief_type": {
      "default": "close",
      "enum": [
        "pre_open",
        "intraday",
        "close"
      ],
      "title": "Brief Type",
      "type": "string"
    },
    "market": {
      "const": "CN",
      "default": "CN",
      "title": "Market",
      "type": "string"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "include_pools": {
      "default": true,
      "title": "Include Pools",
      "type": "boolean"
    },
    "top_n": {
      "default": 5,
      "maximum": 50,
      "minimum": 1,
      "title": "Top N",
      "type": "integer"
    },
    "provider": {
      "anyOf": [
        {
          "enum": [
            "akshare",
            "zhitu",
            "mixed"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "mixed",
      "title": "Provider"
    }
  },
  "title": "MarketBriefRequest",
  "type": "object"
}
```

### `market_overview`

Get high-level overview of China market major indices.

Provider route: `zhitu`; fallback: `akshare`

最小示例：

```json
{
  "market": "CN",
  "provider": "mixed"
}
```

Input schema：

```json
{
  "properties": {
    "market": {
      "const": "CN",
      "default": "CN",
      "title": "Market",
      "type": "string"
    },
    "include": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Include"
    },
    "provider": {
      "anyOf": [
        {
          "enum": [
            "akshare",
            "zhitu",
            "mixed"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "mixed",
      "title": "Provider"
    }
  },
  "title": "MarketOverviewRequest",
  "type": "object"
}
```

### `market_pool`

Get market pools such as limit-up, limit-down, strong, sub-new, and broken-limit stocks.

Provider route: `zhitu`; fallback: `none`

最小示例：

```json
{
  "pool_type": "limit_up",
  "limit": 5,
  "provider": "zhitu"
}
```

Input schema：

```json
{
  "properties": {
    "pool_type": {
      "title": "Pool Type",
      "type": "string"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "limit": {
      "default": 100,
      "maximum": 500,
      "minimum": 1,
      "title": "Limit",
      "type": "integer"
    },
    "provider": {
      "anyOf": [
        {
          "const": "zhitu",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "zhitu",
      "title": "Provider"
    }
  },
  "required": [
    "pool_type"
  ],
  "title": "MarketPoolRequest",
  "type": "object"
}
```

### `money_rate`

Get money market rates (货币市场利率): SHIBOR full-term curve (O/N~1Y), interbank rate by tenor, repo fixing rates (FR/FDR). Supports latest and historical modes.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "shibor",
    "repo"
  ],
  "shibor_days": 10,
  "interbank_indicator": "隔夜",
  "interbank_days": 30,
  "repo_mode": "latest",
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "shibor",
        "repo"
      ],
      "items": {
        "enum": [
          "shibor",
          "interbank",
          "repo"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "shibor_days": {
      "default": 10,
      "description": "Number of recent days for SHIBOR curve",
      "maximum": 365,
      "minimum": 1,
      "title": "Shibor Days",
      "type": "integer"
    },
    "interbank_indicator": {
      "default": "隔夜",
      "enum": [
        "隔夜",
        "1周",
        "2周",
        "1月",
        "3月",
        "6月",
        "9月",
        "1年"
      ],
      "title": "Interbank Indicator",
      "type": "string"
    },
    "interbank_days": {
      "default": 30,
      "description": "Number of recent days for interbank rate",
      "maximum": 365,
      "minimum": 1,
      "title": "Interbank Days",
      "type": "integer"
    },
    "repo_mode": {
      "default": "latest",
      "enum": [
        "latest",
        "hist"
      ],
      "title": "Repo Mode",
      "type": "string"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "MoneyRateRequest",
  "type": "object"
}
```

### `multi_timeframe_review`

Review a symbol across multiple timeframes and summarize alignment/conflicts.

Provider route: `akshare`; fallback: `zhitu`

最小示例：

```json
{
  "symbol": "600519.SH",
  "intervals": [
    "1d",
    "1w"
  ],
  "sec_type": "stock",
  "limit": 120,
  "provider": "mixed"
}
```

Input schema：

```json
{
  "properties": {
    "symbol": {
      "title": "Symbol",
      "type": "string"
    },
    "intervals": {
      "items": {
        "type": "string"
      },
      "maxItems": 8,
      "minItems": 2,
      "title": "Intervals",
      "type": "array"
    },
    "indicators": {
      "anyOf": [
        {
          "items": {
            "enum": [
              "macd",
              "ma",
              "boll",
              "kdj"
            ],
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Indicators"
    },
    "sec_type": {
      "default": "stock",
      "enum": [
        "stock",
        "index",
        "fund"
      ],
      "title": "Sec Type",
      "type": "string"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "limit": {
      "default": 120,
      "maximum": 500,
      "minimum": 20,
      "title": "Limit",
      "type": "integer"
    },
    "provider": {
      "anyOf": [
        {
          "enum": [
            "akshare",
            "zhitu",
            "mixed"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "mixed",
      "title": "Provider"
    }
  },
  "required": [
    "symbol",
    "intervals"
  ],
  "title": "MultiTimeframeReviewRequest",
  "type": "object"
}
```

### `northbound`

Get northbound capital data: daily flow summary and historical trend.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "daily_summary",
    "history"
  ],
  "history_n": 30,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "daily_summary",
        "history"
      ],
      "items": {
        "enum": [
          "daily_summary",
          "history"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "history_n": {
      "default": 30,
      "maximum": 500,
      "minimum": 1,
      "title": "History N",
      "type": "integer"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "NorthboundRequest",
  "type": "object"
}
```

### `provider_health`

Run provider self checks for zhitu and akshare.

Provider route: `akshare`; fallback: `zhitu`

最小示例：

```json
{}
```

Input schema：

```json
{
  "properties": {},
  "title": "EmptyRequest",
  "type": "object"
}
```

### `sec_reveal`

Deep dragon-tiger seat reveal (龙虎榜机构席位深度): stock buy/sell seat detail, active broker seats, institution detail, and institution trace/ranking. EastMoney + Sina sources.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "institution_detail",
    "institution_trace"
  ],
  "period": "5",
  "sort_by": "net_amount",
  "descending": true,
  "top_n": 20,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "institution_detail",
        "institution_trace"
      ],
      "items": {
        "enum": [
          "stock_seat_detail",
          "active_broker",
          "institution_detail",
          "institution_trace"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "symbol": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Stock code required for stock_seat_detail, e.g. 300965",
      "title": "Symbol"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "YYYYMMDD, used for stock_seat_detail",
      "title": "Trade Date"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "YYYYMMDD, used for active_broker",
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "YYYYMMDD, used for active_broker",
      "title": "End Date"
    },
    "period": {
      "default": "5",
      "enum": [
        "5",
        "10",
        "30",
        "60"
      ],
      "title": "Period",
      "type": "string"
    },
    "sort_by": {
      "default": "net_amount",
      "enum": [
        "net_amount",
        "buy_amount",
        "sell_amount",
        "inst_net_amount",
        "inst_buy_amount",
        "total_buy_amount"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 500,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": 20,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "SecRevealRequest",
  "type": "object"
}
```

### `sector_leaders`

Get leaders/followers/draggers snapshot for a sector.

Provider route: `akshare`; fallback: `zhitu`

最小示例：

```json
{
  "sector_name": "银行",
  "sector_type": "primary",
  "adjust": "none",
  "provider": "zhitu",
  "sort_by": "relative_strength",
  "descending": true,
  "top_n": 3,
  "limit": 100,
  "return_mode": "full"
}
```

Input schema：

```json
{
  "properties": {
    "sector_name": {
      "minLength": 1,
      "title": "Sector Name",
      "type": "string"
    },
    "sector_type": {
      "default": "primary",
      "enum": [
        "primary",
        "concept"
      ],
      "title": "Sector Type",
      "type": "string"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "adjust": {
      "default": "none",
      "enum": [
        "none",
        "qfq",
        "hfq"
      ],
      "title": "Adjust",
      "type": "string"
    },
    "provider": {
      "anyOf": [
        {
          "const": "zhitu",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "zhitu",
      "title": "Provider"
    },
    "sort_by": {
      "default": "relative_strength",
      "enum": [
        "relative_strength",
        "return",
        "volume_ratio",
        "max_drawdown"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "default": 3,
      "maximum": 20,
      "minimum": 1,
      "title": "Top N",
      "type": "integer"
    },
    "limit": {
      "default": 100,
      "maximum": 500,
      "minimum": 1,
      "title": "Limit",
      "type": "integer"
    },
    "return_mode": {
      "default": "full",
      "enum": [
        "full",
        "ranked_only"
      ],
      "title": "Return Mode",
      "type": "string"
    },
    "min_relative_strength": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Relative Strength"
    },
    "min_return": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Return"
    },
    "max_drawdown_limit": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Max Drawdown Limit"
    },
    "min_volume_ratio": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Volume Ratio"
    }
  },
  "required": [
    "sector_name"
  ],
  "title": "SectorLeadersRequest",
  "type": "object"
}
```

### `sector_lookup`

Lookup sector lists and members.

Provider route: `zhitu`; fallback: `none`

最小示例：

```json
{
  "mode": "list",
  "limit": 5,
  "provider": "zhitu",
  "sector_type": "primary"
}
```

Input schema：

```json
{
  "properties": {
    "mode": {
      "enum": [
        "list",
        "members",
        "children"
      ],
      "title": "Mode",
      "type": "string"
    },
    "sector_type": {
      "anyOf": [
        {
          "enum": [
            "concept",
            "primary"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Sector Type"
    },
    "sector_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Sector Name"
    },
    "limit": {
      "default": 100,
      "maximum": 500,
      "minimum": 1,
      "title": "Limit",
      "type": "integer"
    },
    "provider": {
      "anyOf": [
        {
          "const": "zhitu",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "zhitu",
      "title": "Provider"
    }
  },
  "required": [
    "mode"
  ],
  "title": "SectorLookupRequest",
  "type": "object"
}
```

### `sector_review`

Generate a review summary for a sector by aggregating its member stocks.

Provider route: `akshare`; fallback: `zhitu`

最小示例：

```json
{
  "sector_name": "银行",
  "sector_type": "primary",
  "adjust": "none",
  "provider": "zhitu",
  "sort_by": "relative_strength",
  "descending": true,
  "top_n": 5,
  "limit": 5
}
```

Input schema：

```json
{
  "properties": {
    "sector_name": {
      "minLength": 1,
      "title": "Sector Name",
      "type": "string"
    },
    "sector_type": {
      "default": "primary",
      "enum": [
        "concept",
        "primary"
      ],
      "title": "Sector Type",
      "type": "string"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "adjust": {
      "default": "none",
      "enum": [
        "none",
        "qfq",
        "hfq"
      ],
      "title": "Adjust",
      "type": "string"
    },
    "provider": {
      "anyOf": [
        {
          "const": "zhitu",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "zhitu",
      "title": "Provider"
    },
    "sort_by": {
      "default": "relative_strength",
      "enum": [
        "relative_strength",
        "return",
        "max_drawdown",
        "volume_ratio"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "default": 5,
      "maximum": 20,
      "minimum": 1,
      "title": "Top N",
      "type": "integer"
    },
    "limit": {
      "default": 100,
      "maximum": 500,
      "minimum": 1,
      "title": "Limit",
      "type": "integer"
    },
    "min_relative_strength": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Relative Strength"
    },
    "min_return": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Return"
    },
    "max_drawdown_limit": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Max Drawdown Limit"
    },
    "min_volume_ratio": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Volume Ratio"
    }
  },
  "required": [
    "sector_name"
  ],
  "title": "SectorReviewRequest",
  "type": "object"
}
```

### `sector_rotation_review`

Compare multiple sectors and summarize cross-sector rotation signals.

Provider route: `akshare`; fallback: `zhitu`

最小示例：

```json
{
  "sector_names": [
    "银行",
    "证券"
  ],
  "sector_type": "primary",
  "adjust": "none",
  "provider": "zhitu",
  "sort_by": "avg_relative_strength",
  "descending": true,
  "top_n": 5,
  "limit": 100,
  "member_top_n": 3,
  "skip_member_detail": false
}
```

Input schema：

```json
{
  "properties": {
    "sector_names": {
      "items": {
        "type": "string"
      },
      "maxItems": 15,
      "minItems": 2,
      "title": "Sector Names",
      "type": "array"
    },
    "sector_type": {
      "default": "primary",
      "enum": [
        "concept",
        "primary"
      ],
      "title": "Sector Type",
      "type": "string"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "adjust": {
      "default": "none",
      "enum": [
        "none",
        "qfq",
        "hfq"
      ],
      "title": "Adjust",
      "type": "string"
    },
    "provider": {
      "anyOf": [
        {
          "const": "zhitu",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "zhitu",
      "title": "Provider"
    },
    "sort_by": {
      "default": "avg_relative_strength",
      "enum": [
        "avg_relative_strength",
        "avg_return",
        "positive_ratio",
        "stronger_ratio",
        "sentiment_score",
        "rotation_score"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "default": 5,
      "maximum": 15,
      "minimum": 1,
      "title": "Top N",
      "type": "integer"
    },
    "limit": {
      "default": 100,
      "maximum": 500,
      "minimum": 1,
      "title": "Limit",
      "type": "integer"
    },
    "member_top_n": {
      "default": 3,
      "maximum": 10,
      "minimum": 1,
      "title": "Member Top N",
      "type": "integer"
    },
    "skip_member_detail": {
      "default": false,
      "description": "When True, skip per-member stock_review expansion and return only sector-level aggregate (sector_lookup + quote-level breadth). Much faster for sector comparison only.",
      "title": "Skip Member Detail",
      "type": "boolean"
    },
    "min_relative_strength": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Relative Strength"
    },
    "min_return": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Return"
    },
    "max_drawdown_limit": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Max Drawdown Limit"
    },
    "min_volume_ratio": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Volume Ratio"
    }
  },
  "required": [
    "sector_names"
  ],
  "title": "SectorRotationReviewRequest",
  "type": "object"
}
```

### `shareholder_change`

Get shareholder change data (股东变动): top 10 shareholders with holding changes per stock, and market-wide shareholder holding change summary (by shareholder type: fund/SSF/QFII/etc). Quarterly data.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "top10",
    "change"
  ],
  "sec_type": "stock",
  "quarter": "auto",
  "sort_by": "total_hold",
  "descending": true,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "top10",
        "change"
      ],
      "items": {
        "enum": [
          "top10",
          "change"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "symbol": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Symbol"
    },
    "sec_type": {
      "default": "stock",
      "title": "Sec Type",
      "type": "string"
    },
    "quarter": {
      "default": "auto",
      "enum": [
        "auto",
        "20261",
        "20254",
        "20253",
        "20252",
        "20251",
        "20244",
        "20243",
        "20242",
        "20241"
      ],
      "title": "Quarter",
      "type": "string"
    },
    "shareholder_type": {
      "default": null,
      "enum": [
        "基金",
        "社保",
        "QFII",
        "券商",
        "保险",
        "信托",
        "个人",
        "其它",
        null
      ],
      "title": "Shareholder Type"
    },
    "sort_by": {
      "default": "total_hold",
      "enum": [
        "total_hold",
        "new_hold",
        "increase_hold",
        "decrease_hold",
        "float_cap"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 500,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "ShareholderChangeRequest",
  "type": "object"
}
```

### `stock_candidate_scan`

Scan a stock universe and rank candidate setups.

Provider route: `akshare`; fallback: `zhitu`

最小示例：

```json
{
  "sector_type": "primary",
  "adjust": "none",
  "provider": "mixed",
  "sort_by": "candidate_score",
  "descending": true,
  "top_n": 20,
  "limit": 20
}
```

Input schema：

```json
{
  "properties": {
    "symbols": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "maxItems": 100,
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Symbols"
    },
    "sector_names": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "maxItems": 10,
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Sector Names"
    },
    "sector_type": {
      "default": "primary",
      "enum": [
        "concept",
        "primary"
      ],
      "title": "Sector Type",
      "type": "string"
    },
    "pool_type": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Pool Type"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "adjust": {
      "default": "none",
      "enum": [
        "none",
        "qfq",
        "hfq"
      ],
      "title": "Adjust",
      "type": "string"
    },
    "provider": {
      "anyOf": [
        {
          "enum": [
            "akshare",
            "zhitu",
            "mixed"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "mixed",
      "title": "Provider"
    },
    "sort_by": {
      "default": "candidate_score",
      "enum": [
        "candidate_score",
        "relative_strength",
        "return",
        "volume_ratio",
        "max_drawdown"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "default": 20,
      "maximum": 100,
      "minimum": 1,
      "title": "Top N",
      "type": "integer"
    },
    "limit": {
      "default": 20,
      "maximum": 100,
      "minimum": 1,
      "title": "Limit",
      "type": "integer"
    },
    "min_candidate_score": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Candidate Score"
    },
    "min_relative_strength": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Relative Strength"
    },
    "min_return": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Return"
    },
    "max_drawdown_limit": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Max Drawdown Limit"
    },
    "min_volume_ratio": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Volume Ratio"
    },
    "min_up_streak": {
      "anyOf": [
        {
          "maximum": 50,
          "minimum": 0,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Up Streak"
    },
    "max_down_streak": {
      "anyOf": [
        {
          "maximum": 50,
          "minimum": 0,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Max Down Streak"
    },
    "require_source_tags": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "maxItems": 20,
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Require Source Tags"
    },
    "exclude_risk_flags": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "maxItems": 20,
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Exclude Risk Flags"
    },
    "must_have_reason_tags": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "maxItems": 30,
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Must Have Reason Tags"
    },
    "exclude_reason_tags": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "maxItems": 30,
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Exclude Reason Tags"
    }
  },
  "title": "StockCandidateScanRequest",
  "type": "object"
}
```

### `stock_compare`

Compare multiple stocks side-by-side (多股横向对比): real-time quote, PE/PB/market_cap valuation, financial indicators (ROE/margin/debt), dividend yield. 2-10 symbols, layered data loading minimizes API calls.

Provider route: `zhitu`; fallback: `akshare`

最小示例：

```json
{
  "symbols": [
    "600519.SH"
  ],
  "sec_type": "stock",
  "include": [
    "quote",
    "valuation"
  ]
}
```

Input schema：

```json
{
  "properties": {
    "symbols": {
      "description": "2-10 stock symbols to compare, e.g. ['600519.SH', '000858.SZ']",
      "items": {
        "type": "string"
      },
      "maxItems": 10,
      "minItems": 2,
      "title": "Symbols",
      "type": "array"
    },
    "sec_type": {
      "default": "stock",
      "title": "Sec Type",
      "type": "string"
    },
    "include": {
      "default": [
        "quote",
        "valuation"
      ],
      "items": {
        "enum": [
          "quote",
          "valuation",
          "financial",
          "dividend"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "provider": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Provider"
    }
  },
  "required": [
    "symbols"
  ],
  "title": "StockCompareRequest",
  "type": "object"
}
```

### `stock_financial`

Get financial statement data for a stock: core metrics snapshot, history trend, and detailed income/balance/cashflow statements.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "symbol": "600519.SH",
  "include": [
    "snapshot",
    "history"
  ],
  "statement": "income",
  "history_n": 8,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "symbol": {
      "minLength": 1,
      "title": "Symbol",
      "type": "string"
    },
    "include": {
      "default": [
        "snapshot",
        "history"
      ],
      "items": {
        "enum": [
          "snapshot",
          "history",
          "details"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "statement": {
      "default": "income",
      "enum": [
        "income",
        "balance",
        "cashflow"
      ],
      "title": "Statement",
      "type": "string"
    },
    "report_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Report Date"
    },
    "history_n": {
      "default": 8,
      "maximum": 30,
      "minimum": 1,
      "title": "History N",
      "type": "integer"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "required": [
    "symbol"
  ],
  "title": "StockFinancialRequest",
  "type": "object"
}
```

### `stock_history`

Get historical price bars for an instrument.

Provider route: `akshare`; fallback: `zhitu`

最小示例：

```json
{
  "symbol": "600519.SH",
  "interval": "1d",
  "limit": 200,
  "adjust": "none"
}
```

Input schema：

```json
{
  "properties": {
    "symbol": {
      "title": "Symbol",
      "type": "string"
    },
    "interval": {
      "title": "Interval",
      "type": "string"
    },
    "sec_type": {
      "anyOf": [
        {
          "enum": [
            "stock",
            "index",
            "fund"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Sec Type"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "limit": {
      "default": 200,
      "maximum": 1000,
      "minimum": 1,
      "title": "Limit",
      "type": "integer"
    },
    "adjust": {
      "default": "none",
      "enum": [
        "none",
        "qfq",
        "hfq"
      ],
      "title": "Adjust",
      "type": "string"
    },
    "provider": {
      "anyOf": [
        {
          "enum": [
            "zhitu",
            "akshare"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Provider"
    },
    "provider_preference": {
      "anyOf": [
        {
          "items": {
            "enum": [
              "akshare",
              "zhitu"
            ],
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Provider Preference"
    }
  },
  "required": [
    "symbol",
    "interval"
  ],
  "title": "StockHistoryRequest",
  "type": "object"
}
```

### `stock_orderbook`

Get order book data for supported instruments.

Provider route: `zhitu`; fallback: `none`

最小示例：

```json
{
  "symbol": "600519.SH",
  "sec_type": "stock",
  "provider": "zhitu"
}
```

Input schema：

```json
{
  "properties": {
    "symbol": {
      "title": "Symbol",
      "type": "string"
    },
    "sec_type": {
      "const": "stock",
      "default": "stock",
      "title": "Sec Type",
      "type": "string"
    },
    "provider": {
      "anyOf": [
        {
          "const": "zhitu",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "zhitu",
      "title": "Provider"
    }
  },
  "required": [
    "symbol"
  ],
  "title": "StockOrderbookRequest",
  "type": "object"
}
```

### `stock_profile`

Get company profile including basic info, dividends, unlocks, and quarterly profits.

Provider route: `zhitu`; fallback: `none`

最小示例：

```json
{
  "symbol": "600519.SH",
  "provider": "zhitu"
}
```

Input schema：

```json
{
  "properties": {
    "symbol": {
      "minLength": 1,
      "title": "Symbol",
      "type": "string"
    },
    "include": {
      "anyOf": [
        {
          "items": {
            "enum": [
              "profile",
              "dividends",
              "unlocks",
              "profits",
              "valuation"
            ],
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Include"
    },
    "provider": {
      "anyOf": [
        {
          "const": "zhitu",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "zhitu",
      "title": "Provider"
    }
  },
  "required": [
    "symbol"
  ],
  "title": "StockProfileRequest",
  "type": "object"
}
```

### `stock_quote`

Get real-time quotes for one or more instruments.

Provider route: `akshare`; fallback: `zhitu`

最小示例：

```json
{
  "symbols": [
    "600519.SH"
  ]
}
```

Input schema：

```json
{
  "properties": {
    "symbols": {
      "items": {
        "type": "string"
      },
      "maxItems": 50,
      "minItems": 1,
      "title": "Symbols",
      "type": "array"
    },
    "sec_type": {
      "anyOf": [
        {
          "enum": [
            "stock",
            "index",
            "fund"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Sec Type"
    },
    "fields": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Fields"
    },
    "provider": {
      "anyOf": [
        {
          "enum": [
            "zhitu",
            "akshare"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Provider"
    },
    "provider_preference": {
      "anyOf": [
        {
          "items": {
            "enum": [
              "akshare",
              "zhitu"
            ],
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Provider Preference"
    }
  },
  "required": [
    "symbols"
  ],
  "title": "StockQuoteRequest",
  "type": "object"
}
```

### `stock_repurchase`

Get stock repurchase data (回购明细): company buyback plans with price range, quantity, progress, and actual repurchase amount. Filter by progress status (董事会预案/股东大会通过/实施中/完成实施).

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "status": "all",
  "sec_type": "stock",
  "sort_by": "done_amount",
  "descending": true,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "status": {
      "default": "all",
      "enum": [
        "all",
        "董事会预案",
        "股东大会通过",
        "实施中",
        "完成实施"
      ],
      "title": "Status",
      "type": "string"
    },
    "symbol": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Symbol"
    },
    "sec_type": {
      "default": "stock",
      "title": "Sec Type",
      "type": "string"
    },
    "sort_by": {
      "default": "done_amount",
      "enum": [
        "done_amount",
        "plan_amount_max",
        "plan_ratio_max",
        "latest_price",
        "start_date"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 500,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "StockRepurchaseRequest",
  "type": "object"
}
```

### `stock_review`

Generate a review summary for a stock on a trade date or over a date range.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "symbol": "600519.SH",
  "adjust": "none",
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "symbol": {
      "title": "Symbol",
      "type": "string"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "adjust": {
      "default": "none",
      "enum": [
        "none",
        "qfq",
        "hfq"
      ],
      "title": "Adjust",
      "type": "string"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "required": [
    "symbol"
  ],
  "title": "StockReviewRequest",
  "type": "object"
}
```

### `stock_review_batch`

Batch review multiple stocks and rank the results for replay workflows.

Provider route: `akshare`; fallback: `zhitu`

最小示例：

```json
{
  "symbols": [
    "600519.SH"
  ],
  "adjust": "none",
  "provider": "akshare",
  "sort_by": "relative_strength",
  "descending": true,
  "top_n": 20
}
```

Input schema：

```json
{
  "properties": {
    "symbols": {
      "items": {
        "type": "string"
      },
      "maxItems": 50,
      "minItems": 1,
      "title": "Symbols",
      "type": "array"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "adjust": {
      "default": "none",
      "enum": [
        "none",
        "qfq",
        "hfq"
      ],
      "title": "Adjust",
      "type": "string"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    },
    "sort_by": {
      "default": "relative_strength",
      "enum": [
        "relative_strength",
        "return",
        "max_drawdown",
        "volume_ratio"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "default": 20,
      "maximum": 50,
      "minimum": 1,
      "title": "Top N",
      "type": "integer"
    },
    "min_relative_strength": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Relative Strength"
    },
    "min_return": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Return"
    },
    "max_drawdown_limit": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Max Drawdown Limit"
    },
    "min_volume_ratio": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Volume Ratio"
    }
  },
  "required": [
    "symbols"
  ],
  "title": "StockReviewBatchRequest",
  "type": "object"
}
```

### `stock_screen`

Screen/filter A-share stocks by market, price range, change percent, volume, turnover, amplitude. Returns sorted results from real-time Sina source. Like a basic stock screener.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "market": "all",
  "sort_by": "change_pct",
  "descending": true,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "market": {
      "default": "all",
      "enum": [
        "all",
        "sh",
        "sz",
        "bj",
        "main",
        "star",
        "gem"
      ],
      "title": "Market",
      "type": "string"
    },
    "min_price": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Minimum latest price (inclusive)",
      "title": "Min Price"
    },
    "max_price": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Maximum latest price (inclusive)",
      "title": "Max Price"
    },
    "min_change_pct": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Minimum change percent (inclusive)",
      "title": "Min Change Pct"
    },
    "max_change_pct": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Maximum change percent (inclusive)",
      "title": "Max Change Pct"
    },
    "min_volume": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Minimum volume (inclusive)",
      "title": "Min Volume"
    },
    "min_turnover": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Minimum turnover (CNY, inclusive)",
      "title": "Min Turnover"
    },
    "min_amplitude": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Minimum amplitude percent (inclusive)",
      "title": "Min Amplitude"
    },
    "sort_by": {
      "default": "change_pct",
      "enum": [
        "change_pct",
        "turnover",
        "volume",
        "latest_price",
        "amplitude"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 500,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "StockScreenRequest",
  "type": "object"
}
```

### `stock_search`

Search stocks, indices, funds, or sectors by keyword or code.

Provider route: `akshare`; fallback: `zhitu`

最小示例：

```json
{
  "query": "贵州茅台",
  "market": "CN",
  "limit": 10
}
```

Input schema：

```json
{
  "properties": {
    "query": {
      "minLength": 1,
      "title": "Query",
      "type": "string"
    },
    "sec_types": {
      "anyOf": [
        {
          "items": {
            "enum": [
              "stock",
              "index",
              "fund",
              "sector"
            ],
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Sec Types"
    },
    "market": {
      "const": "CN",
      "default": "CN",
      "title": "Market",
      "type": "string"
    },
    "limit": {
      "default": 10,
      "maximum": 50,
      "minimum": 1,
      "title": "Limit",
      "type": "integer"
    },
    "provider": {
      "anyOf": [
        {
          "enum": [
            "zhitu",
            "akshare"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Provider"
    }
  },
  "required": [
    "query"
  ],
  "title": "StockSearchRequest",
  "type": "object"
}
```

### `stock_snapshot`

Get a bounded multi-source stock snapshot combining quote, recent history, financial summary, valuation, events, and risk tags; no trading actions.

Provider route: `composite`; fallback: `zhitu, akshare`

最小示例：

```json
{
  "symbols": [
    "600519.SH"
  ],
  "sec_type": "stock",
  "include": [
    "quote",
    "history",
    "financial",
    "valuation",
    "events",
    "risk"
  ],
  "history_interval": "1d",
  "history_limit": 20,
  "adjust": "none",
  "max_total_timeout_seconds": 30
}
```

Input schema：

```json
{
  "description": "Bounded multi-source snapshot; this tool never performs trading actions.",
  "properties": {
    "symbols": {
      "items": {
        "type": "string"
      },
      "maxItems": 5,
      "minItems": 1,
      "title": "Symbols",
      "type": "array"
    },
    "sec_type": {
      "const": "stock",
      "default": "stock",
      "title": "Sec Type",
      "type": "string"
    },
    "include": {
      "items": {
        "enum": [
          "quote",
          "history",
          "financial",
          "valuation",
          "events",
          "risk"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "history_interval": {
      "const": "1d",
      "default": "1d",
      "title": "History Interval",
      "type": "string"
    },
    "history_limit": {
      "default": 20,
      "maximum": 60,
      "minimum": 5,
      "title": "History Limit",
      "type": "integer"
    },
    "adjust": {
      "default": "none",
      "enum": [
        "none",
        "qfq",
        "hfq"
      ],
      "title": "Adjust",
      "type": "string"
    },
    "max_total_timeout_seconds": {
      "default": 30,
      "maximum": 60,
      "minimum": 5,
      "title": "Max Total Timeout Seconds",
      "type": "integer"
    },
    "provider": {
      "anyOf": [
        {
          "enum": [
            "zhitu",
            "akshare"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Provider"
    }
  },
  "required": [
    "symbols"
  ],
  "title": "StockSnapshotRequest",
  "type": "object"
}
```

### `stock_warrant`

Get option/warrant data (权证/期权): ETF options (50ETF/300ETF/etc), commodity options (4 exchanges), CFFEX index options. Real-time quotes with price/volume/open_interest/strike.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "include": [
    "etf_option"
  ],
  "etf_type": "50ETF期权",
  "commodity_exchange": "郑商所",
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "include": {
      "default": [
        "etf_option"
      ],
      "items": {
        "enum": [
          "etf_option",
          "commodity_option",
          "index_option"
        ],
        "type": "string"
      },
      "title": "Include",
      "type": "array"
    },
    "etf_type": {
      "default": "50ETF期权",
      "enum": [
        "50ETF期权",
        "300ETF期权",
        "500ETF期权",
        "创业板ETF期权",
        "科创50ETF期权"
      ],
      "title": "Etf Type",
      "type": "string"
    },
    "commodity_exchange": {
      "default": "郑商所",
      "enum": [
        "郑商所",
        "大商所",
        "上期所",
        "广期所"
      ],
      "title": "Commodity Exchange",
      "type": "string"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 500,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "StockWarrantRequest",
  "type": "object"
}
```

### `technical_indicator`

Get technical indicator series such as MACD, MA, BOLL, KDJ.

Provider route: `akshare`; fallback: `zhitu`

最小示例：

```json
{
  "symbol": "600519.SH",
  "interval": "1d",
  "indicator": "ma",
  "sec_type": "index",
  "limit": 200
}
```

Input schema：

```json
{
  "properties": {
    "symbol": {
      "title": "Symbol",
      "type": "string"
    },
    "interval": {
      "title": "Interval",
      "type": "string"
    },
    "indicator": {
      "title": "Indicator",
      "type": "string"
    },
    "sec_type": {
      "default": "index",
      "enum": [
        "stock",
        "index",
        "fund"
      ],
      "title": "Sec Type",
      "type": "string"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "limit": {
      "default": 200,
      "maximum": 2000,
      "minimum": 1,
      "title": "Limit",
      "type": "integer"
    },
    "provider": {
      "anyOf": [
        {
          "enum": [
            "zhitu",
            "akshare"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Provider"
    }
  },
  "required": [
    "symbol",
    "interval",
    "indicator"
  ],
  "title": "TechnicalIndicatorRequest",
  "type": "object"
}
```

### `trading_calendar`

Query China trading-day calendar for review and backtesting workflows.

Provider route: `akshare`; fallback: `none`

最小示例：

```json
{
  "market": "CN",
  "recent_limit": 5,
  "provider": "akshare"
}
```

Input schema：

```json
{
  "properties": {
    "market": {
      "const": "CN",
      "default": "CN",
      "title": "Market",
      "type": "string"
    },
    "date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Date"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "recent_limit": {
      "default": 5,
      "maximum": 60,
      "minimum": 1,
      "title": "Recent Limit",
      "type": "integer"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    }
  },
  "title": "TradingCalendarRequest",
  "type": "object"
}
```

### `valuation_rank`

Rank stock valuation using PE/PB and combine with market valuation temperature (PE/PB quantiles, dividend yield).

Provider route: `zhitu`; fallback: `akshare`

最小示例：

```json
{
  "symbols": [
    "600519.SH"
  ],
  "sec_type": "stock",
  "sort_by": "pe",
  "descending": false,
  "provider": "zhitu"
}
```

Input schema：

```json
{
  "properties": {
    "symbols": {
      "items": {
        "type": "string"
      },
      "maxItems": 200,
      "minItems": 1,
      "title": "Symbols",
      "type": "array"
    },
    "sec_type": {
      "const": "stock",
      "default": "stock",
      "title": "Sec Type",
      "type": "string"
    },
    "sort_by": {
      "default": "pe",
      "enum": [
        "pe",
        "pb",
        "market_cap"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": false,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "anyOf": [
        {
          "maximum": 200,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Top N"
    },
    "provider": {
      "anyOf": [
        {
          "enum": [
            "zhitu",
            "akshare"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "zhitu",
      "title": "Provider"
    }
  },
  "required": [
    "symbols"
  ],
  "title": "ValuationRankRequest",
  "type": "object"
}
```

### `watchlist_review`

Review and prioritize a watchlist of symbols.

Provider route: `akshare`; fallback: `zhitu`

最小示例：

```json
{
  "symbols": [
    "600519.SH"
  ],
  "adjust": "none",
  "provider": "akshare",
  "sort_by": "watchlist_score",
  "descending": true,
  "top_n": 20
}
```

Input schema：

```json
{
  "properties": {
    "symbols": {
      "items": {
        "type": "string"
      },
      "maxItems": 100,
      "minItems": 1,
      "title": "Symbols",
      "type": "array"
    },
    "watchlist_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Watchlist Name"
    },
    "trade_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Trade Date"
    },
    "start_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Start Date"
    },
    "end_date": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "End Date"
    },
    "adjust": {
      "default": "none",
      "enum": [
        "none",
        "qfq",
        "hfq"
      ],
      "title": "Adjust",
      "type": "string"
    },
    "provider": {
      "anyOf": [
        {
          "const": "akshare",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "akshare",
      "title": "Provider"
    },
    "sort_by": {
      "default": "watchlist_score",
      "enum": [
        "watchlist_score",
        "relative_strength",
        "return",
        "max_drawdown",
        "volume_ratio"
      ],
      "title": "Sort By",
      "type": "string"
    },
    "descending": {
      "default": true,
      "title": "Descending",
      "type": "boolean"
    },
    "top_n": {
      "default": 20,
      "maximum": 100,
      "minimum": 1,
      "title": "Top N",
      "type": "integer"
    },
    "min_watchlist_score": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Watchlist Score"
    },
    "min_relative_strength": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Relative Strength"
    },
    "min_return": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Return"
    },
    "max_drawdown_limit": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Max Drawdown Limit"
    },
    "min_volume_ratio": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Volume Ratio"
    }
  },
  "required": [
    "symbols"
  ],
  "title": "WatchlistReviewRequest",
  "type": "object"
}
```
