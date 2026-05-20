# Integration Guide (`openclaw-stock-mcp`)

Last Updated: 2026-05-20

## 1) 本地运行与自检

> AI agent 建议先读 `docs/AGENT_MINIMAL.md` 与 `docs/EXAMPLES_MINIMAL.md`，再决定是否需要展开本页的完整联调说明。

项目目录：`/home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp`

### 列出 tools
```bash
cd /home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp
PYTHONPATH=src python -m openclaw_stock_mcp.main --list-tools
```

### provider 健康检查
```bash
cd /home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp
HTTP_PROXY= HTTPS_PROXY= ALL_PROXY= http_proxy= https_proxy= all_proxy= \
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool provider_health --payload '{}'
```

### 启动 stdio MCP 服务
```bash
cd /home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp
PYTHONPATH=src python -m openclaw_stock_mcp.main --stdio
```

### 非 live 稳定回归
```bash
cd /home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp
.venv/bin/python -m pytest -q -m "not live"
```

### live smoke（推荐）
```bash
cd /home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp
bash scripts/smoke_live.sh
```

> 说明：`scripts/smoke_live.sh` 是对 `pytest -q tests/live -m "live and smoke" --maxfail=1 -rA` 的薄包装；与 `.github/workflows/live-smoke.yml` 使用同一命令。

> 约束：stdio 模式不要向 stdout 打普通日志，调试日志写 stderr 或文件。

---

## 2) 通用 MCP 挂载配置

### 方案 A：项目虚拟环境 Python（推荐）

```json
{
  "command": "/tmp/openclaw-stock-mcp-venv/bin/python",
  "args": ["-m", "openclaw_stock_mcp.main", "--stdio"],
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

### 方案 B：系统 Python（依赖已安装）

```json
{
  "command": "python3",
  "args": ["-m", "openclaw_stock_mcp.main", "--stdio"],
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

---

## 3) 联调清单

目标：确认宿主能拉起服务、识别 tools、完成核心调用。

### Step 1 - 识别工具
至少应看到：
- stock_search
- stock_quote
- stock_history
- stock_review
- stock_review_batch
- watchlist_review
- trading_calendar
- market_overview
- market_brief
- technical_indicator
- multi_timeframe_review
- market_pool
- stock_orderbook
- stock_candidate_scan
- sector_lookup
- sector_review
- sector_rotation_review
- provider_health

### Step 2 - 调用回归（建议顺序）
1. `provider_health`
2. `stock_quote`（stock-main / index / BJ）
3. `stock_history`（stock）
4. `market_overview`
5. `sector_lookup`（先 list；`children/members` 现在要求显式传 `sector_type=primary|concept`，缺少参数会直接报错，不会请求上游）
6. `stock_review`（优先使用最近有效交易日，不要长期写死旧 `trade_date`）
7. `market_pool` 或 provider 直连最小路径
8. 更重的 `sector_review` / `sector_rotation_review` / `stock_candidate_scan` / `watchlist_review` / `multi_timeframe_review` 放到 extended live 回归

### Step 3 - 常见风险点
- 环境变量未透传（尤其 token）
- cwd 或 PYTHONPATH 错误
- 宿主注入代理变量导致上游请求异常
- Python 解释器与依赖环境不一致
- live 测试写死旧 `trade_date` 或脆弱 `sector_name`，导致 smoke 偶发失败
- 把 smoke 和 extended live 回归混在一起，导致 CI 信号噪声过大

---

## 4) 验收标准

满足以下条件即可判定挂载可用：
1. `--list-tools` 与宿主看到的工具集一致。
2. `provider_health` 成功。
3. `live smoke` 命令（`bash scripts/smoke_live.sh`）至少能稳定跑通核心链路。
4. 更重的 live extended 用例可单独执行，不与默认 smoke 混跑。
5. stdio 模式下协议输出正常，无 stdout 杂日志干扰。
