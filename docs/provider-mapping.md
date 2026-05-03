# Provider 映射设计文档 v1.0

> 项目：`openclaw-stock-mcp`
> 目标：定义 AKShare / 智兔 与内部统一领域模型之间的字段映射、路由规则、能力边界、实现优先级与注意事项。

---

## 1. 文档目标

本文件用于解决以下问题：

1. 每个 MCP tool 应该调用哪个 provider
2. provider 的原始接口如何映射到内部 schema
3. 不同 provider 的 symbol / 时间 / 字段差异如何归一化
4. 哪些能力以 AKShare 为主，哪些能力以智兔为主
5. 哪些能力 v1 先不做，避免 implementation 漫无边界

这份文档应作为以下实现的直接依据：
- `providers/akshare_provider.py`
- `providers/zhitu_provider.py`
- `providers/adapters/akshare_adapters.py`
- `providers/adapters/zhitu_adapters.py`
- `app/services/provider_router.py`

---

## 2. Provider 总体定位

### 2.1 AKShare

定位：
- 本地 Python provider
- 偏基础列表、基础行情、历史行情、通用兜底

适合承担：
- 股票/指数/基金基础列表
- 名称与代码解析
- A 股历史 K 线
- 通用市场概览
- 当智兔不可用时的回退源

主要风险：
- 接口命名与字段不统一
- 某些上游抓取源波动
- 需要对 DataFrame 做适配

---

### 2.2 智兔

定位：
- 远程 HTTP provider
- 偏实时行情、指数数据、指标数据、盘口、股池、板块

适合承担：
- 指数实时与历史分时
- 指标（MACD / MA / BOLL / KDJ）
- 北交所实时
- 科创板实时
- 基金实时
- 五档盘口
- 股池
- 板块列表与板块成员

主要风险：
- token 认证与额度限制
- 分市场路径不同，需要内部做明确路由

---

## 3. 内部领域模型回顾

本文映射的目标模型包括：

- `Instrument`
- `Quote`
- `Bar`
- `IndicatorSeries`
- `OrderBook`
- `MarketPoolItem`

映射原则：
1. 上游 provider 原始字段只在 adapter 层出现
2. usecase 层不感知 provider 原始字段名
3. 所有 symbol 先统一 canonical 化再进入上层
4. 所有时间字段尽量转成统一格式

---

## 4. Tool 到 Provider 的推荐映射

| Tool | 主 provider | 备 provider | 当前建议 |
|---|---|---|---|
| stock_search | AKShare | 智兔 | 先用 AKShare 打基础列表能力 |
| stock_quote(stock-main) | 智兔 | AKShare | 已定稿：主走智兔，失败回退 AKShare |
| stock_quote(index) | 智兔 | AKShare | 智兔指数接口明确 |
| stock_quote(fund) | 智兔 | AKShare | 智兔基金实时明确 |
| stock_quote(stock-bj) | 智兔 | - | 智兔文档明确 |
| stock_quote(stock-star) | 智兔 | - | 智兔文档明确 |
| stock_history(stock) | AKShare | 智兔 | 历史 K 线优先 AKShare |
| stock_history(index) | 智兔 | AKShare | 指数分时智兔更清楚 |
| market_overview | mixed | - | 可混合多个 provider |
| technical_indicator | 智兔 | - | v1 主要依赖智兔 |
| market_pool | 智兔 | - | 涨停/跌停/强势股池 |
| stock_orderbook | 智兔 | - | 北交所/科创板 |
| sector_lookup | 智兔 | - | 板块列表/成员 |

---

## 5. AKShare 映射设计

> 说明：AKShare 接口很多，且函数名在不同版本可能变化。v1 不在文档里把 AKShare 具体函数名完全写死到“唯一选择”，而是先定义“能力映射层”，代码里再绑定到当前实测可用函数。

---

## 5.1 AKShare → Instrument（基础列表）

### 5.1.1 股票列表
目标：支持 `stock_search`、symbol resolver。

建议从 AKShare 获取：
- A 股股票基础列表
- 指数基础列表
- 基金基础列表

内部统一字段：

| 内部字段 | AKShare 常见来源字段 | 说明 |
|---|---|---|
| symbol | 代码/证券代码 | 需 canonical 化 |
| name | 名称/证券简称 | 原样保留 |
| market | 固定 `CN` | 内部补充 |
| exchange | 由代码规则或原字段判断 | `SH`/`SZ`/`BJ` |
| board | 由 symbol 推断 | `main`/`chinext`/`star`/`fund`/`index` |
| sec_type | 由列表类别决定 | `stock` / `index` / `fund` |
| source | 固定 `akshare` | |

### 5.1.2 symbol 规则补充
- `600/601/603/605/688` → `SH`
- `000/001/002/003/300` → `SZ`
- 北交所代码若 AKShare 列表中可得，按列表优先
- 基金和指数尽量依据数据表类型，而不是仅看数字前缀

---

## 5.2 AKShare → Quote

AKShare 的不同行情接口字段可能是中文列名，例如：
- 最新价
- 涨跌幅
- 涨跌额
- 成交量
- 成交额
- 今开
- 最高
- 最低
- 昨收
- 换手率
- 市盈率-动态
- 市净率

统一映射：

| 内部 Quote 字段 | AKShare 常见中文字段 |
|---|---|
| price | 最新价 |
| change_percent | 涨跌幅 |
| change | 涨跌额 |
| volume | 成交量 |
| turnover | 成交额 |
| open | 今开 / 开盘 |
| high | 最高 |
| low | 最低 |
| prev_close | 昨收 |
| turnover_rate | 换手率 |
| pe | 市盈率-动态 / 市盈率 |
| pb | 市净率 |
| market_cap | 总市值 |
| float_market_cap | 流通市值 |
| timestamp | 行情时间（若无则由调用时刻补充） |
| source | 固定 `akshare` |

### 5.2.1 注意事项
1. AKShare 有些 spot 接口是全市场快照，单 symbol 查询时建议：
   - 若支持批量抓全表后过滤，可用于多 symbol 查询
   - 否则要谨慎性能
2. 若 AKShare 返回 DataFrame 中数值列为字符串，adapter 层负责转数值
3. 若部分字段为空，不应报错，允许返回 `null`

---

## 5.3 AKShare → Bar（历史行情）

AKShare 历史数据通常能提供：
- 日期
- 开盘
- 收盘
- 最高
- 最低
- 成交量
- 成交额
- 振幅
- 涨跌幅
- 涨跌额
- 换手率

内部核心只映射必要字段：

| 内部 Bar 字段 | AKShare 常见字段 |
|---|---|
| time | 日期 / 时间 |
| open | 开盘 |
| high | 最高 |
| low | 最低 |
| close | 收盘 |
| volume | 成交量 |
| turnover | 成交额 |
| prev_close | 若能推导则补，否则空 |

### 5.3.1 prev_close 规则
- 若源里无前收，则可由前一条 `close` 计算
- 第一条历史数据 `prev_close` 可为空

### 5.3.2 adjust 规则
- 股票历史：透传 `none / qfq / hfq` 到 AKShare 对应参数
- 指数历史：忽略 adjust
- 基金历史：视 AKShare 接口能力决定，不能乱映射

---

## 5.4 AKShare → market_overview

若智兔不可用，可由 AKShare 获取主要指数快照后组装：
- 上证指数
- 深证成指
- 创业板指
- 北证50（若数据可取）

输出为 `Quote[]` 的子集。

### 5.4.1 source 约定
- 全部由 AKShare 构成：`source = "akshare"`
- 若混用多个 provider：`source = "mixed"`

---

## 5.5 AKShare 当前不作为主实现的能力

v1 中，以下能力不建议以 AKShare 作为首发实现：
- 五档盘口
- 涨停/跌停/强势股池
- 指数技术指标序列
- 北交所/科创板实时专门接口
- 板块成员查询

原因：智兔文档清晰度更高。

---

## 6. 智兔映射设计

---

## 6.1 智兔路径总览

### 6.1.1 沪深股票相关
- `/hs/list/all`
- `/hs/list/sectors`
- `/hs/list/primary`
- `/hs/sectors/{name}`
- `/hs/pool/ztgc/{date}`
- `/hs/pool/dtgc/{date}`
- `/hs/pool/qsgc/{date}`

### 6.1.2 沪深指数相关
- `/hz/list/hszs`
- `/hz/real/ssjy/{symbol}`
- `/hz/latest/fsjy/{symbol}/{interval}`
- `/hz/history/fsjy/{symbol}/{interval}`
- `/hz/history/macd/{symbol}/{interval}`
- `/hz/history/ma/{symbol}/{interval}`
- `/hz/history/boll/{symbol}/{interval}`
- `/hz/history/kdj/{symbol}/{interval}`

### 6.1.3 北交所相关
- `/bj/list/all`
- `/bj/list/index`
- `/bj/stock/real/ssjy/{symbol}`
- `/bj/stock/real/mmwp/{symbol}`
- `/bj/index/real/ssjy/{symbol}`

### 6.1.4 科创板相关
- `/tech/list/all`
- `/tech/real/ssjy/{symbol}`
- `/tech/real/mmwp/{symbol}`

### 6.1.5 基金相关
- `/fund/list/all`
- `/fund/list/etf`
- `/fund/real/ssjy/{symbol}`

---

## 6.2 智兔 → Instrument

### 6.2.1 沪深股票列表 `/hs/list/all`
原始字段：
- `dm`: 代码，如 `000001`
- `mc`: 名称
- `jys`: 交易所，`sh` / `sz`

映射：

| 内部字段 | 智兔字段 | 规则 |
|---|---|---|
| symbol | `dm` + `jys` | `000001` + `sz` → `000001.SZ` |
| name | `mc` | 原样 |
| market | - | 固定 `CN` |
| exchange | `jys` | `sh` → `SH`, `sz` → `SZ` |
| board | symbol 推断 | `main/chinext/star` |
| sec_type | - | 固定 `stock` |
| source | - | `zhitu` |

### 6.2.2 沪深指数列表 `/hz/list/hszs`
原始字段：
- `dm`: `000001.SH`
- `mc`: 指数名称
- `jys`: `sh` / `sz`

映射：

| 内部字段 | 智兔字段 |
|---|---|
| symbol | `dm` |
| name | `mc` |
| market | 固定 `CN` |
| exchange | `jys` → `SH/SZ` |
| board | 固定 `index` |
| sec_type | 固定 `index` |
| source | `zhitu` |

### 6.2.3 北交所股票列表 `/bj/list/all`
原始字段：
- `dm`: `430017.BJ`
- `mc`
- `jys`

映射：
- `symbol = dm`
- `exchange = BJ`
- `board = beijing`
- `sec_type = stock`

### 6.2.4 北交所指数列表 `/bj/list/index`
- `symbol = dm`
- `exchange = BJ`
- `board = index`
- `sec_type = index`

### 6.2.5 科创板股票列表 `/tech/list/all`
原始字段：
- `dm`: `688001.SH` 风格或仅数字，依接口实测确认

映射原则：
- 若有后缀，直接 canonical 化
- 若无后缀，补 `.SH`
- `board = star`
- `sec_type = stock`

### 6.2.6 基金列表 `/fund/list/all` 与 `/fund/list/etf`
- `symbol = dm`
- `exchange = jys -> SH/SZ`
- `board = fund`
- `sec_type = fund`

### 6.2.7 板块列表 `/hs/list/sectors`
- `symbol = dm`（例如 `101076.BKZS`）
- `name = mc`
- `exchange = BK`
- `board = sector`
- `sec_type = sector`

---

## 6.3 智兔 → Quote

智兔实时行情常见字段：
- `p`: 最新价
- `o`: 开盘价
- `h`: 最高价
- `l`: 最低价
- `yc`: 前收盘价
- `cje`: 成交总额
- `v`: 成交总量
- `pv`: 原始成交总量
- `ud`: 涨跌额
- `pc`: 涨跌幅
- `zf`: 振幅
- `t`: 更新时间
- `pe`: 市盈率
- `tr` / `hs`: 换手率
- `pb_ratio` / `sjl`: 市净率
- `lt`: 流通市值
- `sz` / `zsz`: 总市值

映射表：

| 内部 Quote 字段 | 智兔字段 | 说明 |
|---|---|---|
| price | `p` | 最新价 |
| open | `o` | 开盘 |
| high | `h` | 最高 |
| low | `l` | 最低 |
| prev_close | `yc` | 前收 |
| change | `ud` | 涨跌额 |
| change_percent | `pc` | 涨跌幅（%） |
| amplitude | `zf` | 振幅（%） |
| turnover | `cje` | 成交额 |
| volume | `v` 或 `tv` | 优先取明确成交量字段 |
| turnover_rate | `tr` 或 `hs` | 换手率 |
| pe | `pe` | 市盈率 |
| pb | `pb_ratio` 或 `sjl` | 市净率 |
| float_market_cap | `lt` | 流通市值 |
| market_cap | `sz` 或 `zsz` | 总市值 |
| timestamp | `t` | 需标准化时间格式 |
| source | - | 固定 `zhitu` |

### 6.3.1 时间标准化
智兔示例中时间可能是：
- `2025-02-2115:29:05`
- `2025-07-21 15:00`
- `2025-04-30 00:00:00`

adapter 层需要统一转为：
- 实时：`2025-02-21T15:29:05+08:00`
- 分钟线：`2025-07-21T15:00:00+08:00`
- 日线：允许保留 `2025-04-30`

---

## 6.4 智兔 → Bar

### 6.4.1 指数历史/最新分时 `/hz/latest/fsjy` `/hz/history/fsjy`
原始字段：
- `t`
- `o`
- `h`
- `l`
- `c`
- `v`
- `a`
- `pc`

映射：

| 内部 Bar 字段 | 智兔字段 |
|---|---|
| time | `t` |
| open | `o` |
| high | `h` |
| low | `l` |
| close | `c` |
| volume | `v` |
| turnover | `a` |
| prev_close | `pc` |

### 6.4.2 股票/基金历史
- 智兔当前补充文档未完整给出股票/基金历史路径
- v1 股票历史优先 AKShare
- 若后续确认智兔存在稳定历史接口，再补映射

---

## 6.5 智兔 → IndicatorSeries

### 6.5.1 MACD `/hz/history/macd/{symbol}/{interval}`
原始字段：
- `t`
- `diff`
- `dea`
- `macd`
- `ema12`
- `ema26`

映射：

```json
{
  "time": "t",
  "values": {
    "diff": "diff",
    "dea": "dea",
    "macd": "macd",
    "ema12": "ema12",
    "ema26": "ema26"
  }
}
```

### 6.5.2 MA `/hz/history/ma/{symbol}/{interval}`
原始字段：
- `ma3`
- `ma5`
- `ma10`
- `ma15`
- `ma20`
- `ma30`
- `ma60`
- `ma120`
- `ma200`
- `ma250`

映射到 `values` 原样同名保留。

### 6.5.3 BOLL `/hz/history/boll/{symbol}/{interval}`
原始字段：
- `u`
- `d`
- `m`

映射：

```json
{"u": 0.0, "m": 0.0, "d": 0.0}
```

### 6.5.4 KDJ `/hz/history/kdj/{symbol}/{interval}`
原始字段：
- `k`
- `d`
- `j`

映射：

```json
{"k": 0.0, "d": 0.0, "j": 0.0}
```

---

## 6.6 智兔 → OrderBook

### 6.6.1 北交所盘口 `/bj/stock/real/mmwp/{symbol}`
### 6.6.2 科创板盘口 `/tech/real/mmwp/{symbol}`

原始字段示例：
- `t`
- `pb1 ~ pb5`
- `vb1 ~ vb5`
- `ps1 ~ ps5`
- `vs1 ~ vs5`

映射：

| 内部字段 | 智兔字段 |
|---|---|
| timestamp | `t` |
| bids[0].price | `pb1` |
| bids[0].volume | `vb1` |
| bids[1].price | `pb2` |
| bids[1].volume | `vb2` |
| ... | ... |
| asks[0].price | `ps1` |
| asks[0].volume | `vs1` |
| asks[1].price | `ps2` |
| asks[1].volume | `vs2` |
| ... | ... |

### 6.6.3 顺序约定
- `bids`：买一到买五
- `asks`：卖一到卖五

### 6.6.4 空值处理
如果某档为空：
- 可跳过该档
- 或保留 `price=null, volume=null`

推荐：跳过全空档位。

---

## 6.7 智兔 → MarketPoolItem

### 6.7.1 涨停股池 `/hs/pool/ztgc/{date}`
原始字段示例：
- `dm`
- `mc`
- `p`
- `zf`
- `cje`
- `lt`
- `zsz`
- `hs`
- `lbc`
- `fbt`
- `lbt`
- `zj`
- `zbc`
- `tj`

映射：

| 内部字段 | 智兔字段 |
|---|---|
| symbol | `dm` → canonical |
| name | `mc` |
| price | `p` |
| change_percent | `zf` |
| turnover | `cje` |
| float_market_cap | `lt` |
| market_cap | `zsz` |
| turnover_rate | `hs` |
| extra.limit_count | `lbc` |
| extra.first_limit_time | `fbt` |
| extra.last_limit_time | `lbt` |
| extra.limit_fund | `zj` |
| extra.board_burst_count | `zbc` |
| extra.stat | `tj` |

### 6.7.2 跌停股池 `/hs/pool/dtgc/{date}`
原始字段可能有：
- `pe`
- `fba`
- `zbc`
- `lbc`
- `lbt`

映射建议：

| extra 字段 | 智兔字段 |
|---|---|
| consecutive_limit_down_count | `lbc` |
| last_limit_time | `lbt` |
| limit_fund | `zj` |
| board_trade_amount | `fba` |
| board_open_count | `zbc` |

### 6.7.3 强势股池 `/hs/pool/qsgc/{date}`
原始字段常见：
- `ztp`
- `zf`
- `cje`
- `lt`
- `zsz`
- `zs`
- `nh`
- `lb`
- `hs`
- `tj`

映射建议：

| 内部字段 | 智兔字段 |
|---|---|
| price | `p` |
| change_percent | `zf` |
| turnover | `cje` |
| float_market_cap | `lt` |
| market_cap | `zsz` |
| turnover_rate | `hs` |
| extra.limit_price | `ztp` |
| extra.speed | `zs` |
| extra.new_high | `nh` |
| extra.volume_ratio | `lb` |
| extra.stat | `tj` |

---

## 6.8 智兔 → sector_lookup

### 6.8.1 概念指数列表 `/hs/list/sectors`
映射到 `Instrument(sec_type=sector, board=sector, exchange=BK)`

### 6.8.2 一级市场列表 `/hs/list/primary`
该接口文档字段展示略混乱，但核心目标是得到一级板块名称。

建议：
- 若返回只有名称字段，则构造：
  - `symbol = mc`
  - `name = mc`
  - `sec_type = sector`
  - `board = sector`
  - `exchange = BK`
- 等实测接口结果后再精修

### 6.8.3 板块成员 `/hs/sectors/{name}`
原始字段示例：
- `dm`
- `mc`
- `jys`

映射到 `Instrument(sec_type=sector or stock?)`

这里要区分两种理解：
1. 如果返回的是“板块列表项”，则 `sec_type=sector`
2. 如果返回的是“板块成分股”，则 `sec_type=stock`

当前已通过在线样本确认：`/hs/sectors/{name}` 返回的是**股票成员列表**，因此：
- `sector_lookup.list` 返回板块项（`sec_type=sector`）
- `sector_lookup.children/members` 返回股票成员（`sec_type=stock`）

**当前实现**：
- `list` 模式：已开放
- `children/members` 模式：已开放，要求 `sector_name` 传真实可用的一级板块名称，例如 `TFG板块趋势`

---

## 7. symbol canonical 化规则

---

## 7.1 智兔 symbol 标准化

### 7.1.1 纯代码 + jys
- `dm=000001`, `jys=sz` → `000001.SZ`
- `dm=688001`, `jys=sh` → `688001.SH`

### 7.1.2 已带后缀代码
- `430017.BJ` → 保留
- `000001.SH` → 保留
- `101076.BKZS` → 保留

### 7.1.3 含前缀代码
股池接口中可能返回：
- `sz000657`
- `sh603099`

规范化规则：
- `sz000657` → `000657.SZ`
- `sh603099` → `603099.SH`

实现建议：
- 匹配 `^(sh|sz)(\d{6})$`
- 转成 `{digits}.{EXCHANGE}`

---

## 7.2 AKShare symbol 标准化

若返回仅数字代码：
- 通过列表类别 + 规则判断交易所
- 最终统一加后缀

若返回已带市场后缀：
- 统一大小写

---

## 8. interval 映射规则

### 8.1 内部 -> 智兔

| 内部 interval | 智兔 interval |
|---|---|
| 5m | `5` |
| 15m | `15` |
| 30m | `30` |
| 60m | `60` |
| 1d | `d` |
| 1w | `w` |
| 1M | `m` |
| 1y | `y` |

### 8.2 内部 -> AKShare
AKShare 各接口参数不完全统一，代码中建议单独封装：
- `map_interval_to_akshare(interval, sec_type)`

### 8.3 1m 支持说明
当前已完成真实上游探测：
- 智兔指数历史 `1m` 候选路由返回 `400`
- 智兔指标 `1m` 候选路由返回 `404`
- AKShare 当前 `index` / `stock` 历史均不支持 `1m`
- AKShare indicator 当前未实现

因此：
- v1 **明确不支持 `1m`**，并在 schema 层直接拒绝
- 这样做是为了避免将 `1m` 错误解释为 `1M` 月线
- 后续只有在上游新增并实测验证了稳定 `1m` 接口后，才重新开放

---

## 9. 日期格式映射

### 9.1 内部输入格式
- `2026-04-30`
- `2026-04-30T15:00:00+08:00`

### 9.2 智兔历史接口参数
- `st=20250101`
- `et=20250430`
- 或 `YYYYMMDDhhmmss`

### 9.3 映射规则
- 若输入只有日期 → 转 `YYYYMMDD`
- 若输入有时间 → 转 `YYYYMMDDHHMMSS`
- 输出统一还原为标准格式

---

## 10. provider router 设计要点

### 10.1 route key
建议路由时先得到：
- `sec_type`
- `exchange`
- `board`
- `tool_name`

例如：
- `stock_quote + stock + BJ`
- `stock_quote + index + SH`
- `stock_history + stock + main`
- `technical_indicator + index`

### 10.2 典型决策

#### case 1：`stock_quote(symbol=430017.BJ)`
- route → 智兔 `/bj/stock/real/ssjy/430017`

#### case 2：`stock_quote(symbol=688001.SH)`
- route → 智兔 `/tech/real/ssjy/688001`

#### case 3：`stock_quote(symbol=000001.SZ, sec_type=stock)`
- route → 智兔 `/hs/real/ssjy/000001`

#### case 4：`stock_quote(symbol=000001.SH, sec_type=index)`
- route → 智兔 `/hz/real/ssjy/000001.SH`

#### case 5：`technical_indicator(symbol=000001.SH, indicator=macd)`
- route → 智兔 `/hz/history/macd/000001.SH/d?...`

---

## 11. v1 实现优先级建议

### 第一优先级
1. AKShare 列表与 symbol resolver
2. 智兔指数实时 + 历史 + 指标
3. 智兔北交所/科创板/基金实时
4. AKShare 股票历史

### 第二优先级
5. 智兔股池
6. 智兔板块列表
7. 智兔盘口

### 第三优先级
8. A 股普通股票实时的 AKShare/智兔双源对比优化
9. 板块成员查询
10. provider 健康检查工具

---

## 12. 当前不确定点（实现前需实测）

这些点我现在不能确认，代码落地前最好先做小样本探测：

1. 智兔是否提供普通沪深股票实时交易接口页面（这次补充文档里未完整看到）
2. 科创板 `/tech/list/all` 返回的 `dm` 是否总带 `.SH`
3. 北交所 `/bj/stock/real/ssjy/{symbol}` 是否要求只传数字而不能传 `.BJ`
4. `sector_lookup members` 实际返回的是板块列表还是成分股
5. AKShare 当前可用的最稳股票历史/列表接口是哪一组
6. AKShare 对基金/指数实时是否足够稳定
7. `1m` 周期当前已完成上游探测并确认**不支持**；如未来上游新增稳定接口，再重新评估开放

这些不确定点不影响先写骨架，但会影响具体 adapter 绑定。

---

## 13. adapter 层函数建议

建议在 `adapters/zhitu_adapters.py` 中定义：

- `adapt_zhitu_stock_list_item(raw) -> Instrument`
- `adapt_zhitu_index_list_item(raw) -> Instrument`
- `adapt_zhitu_fund_list_item(raw) -> Instrument`
- `adapt_zhitu_sector_list_item(raw) -> Instrument`
- `adapt_zhitu_quote(raw, symbol, sec_type, exchange, board) -> Quote`
- `adapt_zhitu_bar(raw) -> Bar`
- `adapt_zhitu_macd_item(raw) -> IndicatorPoint`
- `adapt_zhitu_ma_item(raw) -> IndicatorPoint`
- `adapt_zhitu_boll_item(raw) -> IndicatorPoint`
- `adapt_zhitu_kdj_item(raw) -> IndicatorPoint`
- `adapt_zhitu_orderbook(raw, symbol) -> OrderBook`
- `adapt_zhitu_limit_up_item(raw) -> MarketPoolItem`
- `adapt_zhitu_limit_down_item(raw) -> MarketPoolItem`
- `adapt_zhitu_strong_item(raw) -> MarketPoolItem`

建议在 `adapters/akshare_adapters.py` 中定义：

- `adapt_akshare_stock_list_row(row) -> Instrument`
- `adapt_akshare_index_list_row(row) -> Instrument`
- `adapt_akshare_fund_list_row(row) -> Instrument`
- `adapt_akshare_quote_row(row, sec_type) -> Quote`
- `adapt_akshare_bar_row(row) -> Bar`

---

## 14. 明确结论

本文件落下来的关键决定是：

1. **AKShare 负责基础列表、symbol resolver、历史行情兜底**
2. **智兔负责指数、实时、指标、股池、盘口、板块类能力**
3. **所有 provider 原始字段统一在 adapter 层转换**
4. **symbol / interval / date 必须先经过规范化，再进入 provider**
5. **普通沪深股票实时当前已实测可走智兔主线路，AKShare 作为备源保留**
6. **有歧义的智兔接口先收敛能力边界，不要抢实现**

---

## 15. 下一步建议

基于这份映射文档，下一步最适合继续产出的是：

1. `README.md` 初稿
2. `pyproject.toml`
3. `src/openclaw_stock_mcp/app/models/*.py`
4. `src/openclaw_stock_mcp/server/schemas.py`
5. `src/openclaw_stock_mcp/providers/base.py`
6. `src/openclaw_stock_mcp/infra/config.py`

如果你要继续，我建议下一步直接开始**生成项目骨架代码**，因为文档层已经够支撑开工了。