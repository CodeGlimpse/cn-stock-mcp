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

## 快速开始

### 安装依赖

```bash
pip install -e .
```

### 配置

```bash
cp .env.example .env
```

智兔 token 支持两种方式：

1. 直接写 `.env`
2. 写入 `config/zhitu_tokens.json`

### 列出已注册 tools

```bash
PYTHONPATH=src python -m openclaw_stock_mcp.main --list-tools
```

### 调用单个 tool

```bash
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool stock_quote --payload '{"symbols":["000001.SH"],"sec_type":"index"}'
```

### sector_lookup 本地调用样例（板块列表 / 层级）

```bash
# 概念板块列表（默认）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_lookup --payload '{"mode":"list","sector_type":"concept","limit":10}'

# 一级板块列表
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_lookup --payload '{"mode":"list","sector_type":"primary","limit":10}'

# 层级查询：某一级板块下的子板块（children）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_lookup --payload '{"mode":"children","sector_name":"概念指数","limit":20}'

# 兼容旧模式名 members（语义等同 children）
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool sector_lookup --payload '{"mode":"members","sector_name":"概念指数","limit":20}'
```

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
2. `stock_quote {"symbols":["000001.SH"],"sec_type":"index"}`
3. `stock_history {"symbol":"600519","sec_type":"stock","interval":"1d","limit":5}`
4. `sector_lookup {"mode":"list","sector_type":"concept","limit":10}`

## 说明

### 数据源 API 文档入口
- 统一索引见：`docs/DATA_SOURCE_API_DOCS.md`

### 股票历史的当前实现
- `stock_history(stock)` 当前通过 **AKShare 腾讯历史接口** 实现
- 字段来源与口径：
  - `open/high/low/close`：腾讯历史接口
  - `volume`：优先由 `stock_zh_a_daily` 按日期回填
  - `turnover`：统一为成交额口径（`stock_zh_a_daily.amount` 优先）
  - `prev_close`：按前一条 bar 的 `close` 推导（首条通常为空）

### sector_lookup 当前语义
- `mode=list, sector_type=concept`：概念板块列表
- `mode=list, sector_type=primary`：一级板块列表
- `mode=children`（或兼容 `members`）：一级板块下属板块列表（层级查询）

### Transport 状态
当前已切换为 **MCP Python SDK（FastMCP）stdio transport**。
本地 `--tool` / `--list-tools` 路径仍保留，供调试与 smoke test 使用。
