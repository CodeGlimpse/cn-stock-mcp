# Handoff Minimal (`openclaw-stock-mcp`)

给最终用户 / 本地 AI agent 的最短接入说明。

## 1) 安装

```bash
cd /path/to/openclaw-stock-mcp
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
cp .env.example .env
```

如需智兔 token，可：
- 直接写 `.env`
- 或写 `config/zhitu_tokens.json`

## 2) 本地自检

```bash
PYTHONPATH=src .venv/bin/python -m openclaw_stock_mcp.main --list-tools
PYTHONPATH=src .venv/bin/python -m openclaw_stock_mcp.main --tool provider_health --payload '{}'
.venv/bin/python -m pytest -q -m "not live"
```

## 3) MCP 挂载

最小配置可直接参考：
- `.mcp.sample.json`

核心字段：
- `command`: Python 解释器
- `args`: `['-m', 'openclaw_stock_mcp.main', '--stdio']`
- `cwd`: 仓库根目录
- `env.PYTHONPATH=src`

本页假设你的宿主只需要 MCP 接入；如果宿主还支持 rules / instructions / skills，再看：
- `docs/COMPATIBILITY.md`

## 4) 最小验收顺序

1. `provider_health {}`
2. `stock_quote {"symbols":["000001.SH"],"sec_type":"index"}`
3. `stock_history {"symbol":"000001.SH","sec_type":"index","interval":"d","limit":20}`
4. `market_brief {"brief_type":"close","trade_date":"2026-05-01","top_n":3}`
5. `sector_lookup {"mode":"list","sector_type":"concept","limit":10}`
6. `sector_review {"sector_name":"人工智能","sector_type":"concept","trade_date":"2026-04-30","top_n":3,"limit":20}`

## 5) AI agent 最重要的硬规则

- 名称/代码不确定时，先 `stock_search`
- 默认小参数：`limit/top_n=3~5`
- 不要默认先跑 `provider_health`
- `sector_lookup(mode=children|members)` **必须显式传** `sector_type=primary|concept`

正确示例：
```json
{"mode":"children","sector_type":"primary","sector_name":"银行","limit":20}
```

错误示例：
```json
{"mode":"children","sector_name":"银行","limit":20}
```

## 6) 需要更多信息时再看

- AI agent 最小入口：`docs/AGENT_MINIMAL.md`
- 最小示例：`docs/EXAMPLES_MINIMAL.md`
- 完整示例：`docs/EXAMPLES_FULL.md`
- 挂载/联调：`docs/INTEGRATION.md`
- 协议/参数：`docs/INTERFACE_SCHEMA.md`
- 错误码：`docs/ERROR_MODEL.md`
