# Integration Guide (`openclaw-stock-mcp`)

Last Updated: 2026-05-06

## 1) 本地运行与自检

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

> 约束：stdio 模式不要向 stdout 打普通日志，调试日志写 stderr 或文件。

---

## 2) OpenClaw 挂载配置

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

目标：确认 OpenClaw 能拉起服务、识别 tools、完成核心调用。

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
2. `stock_quote`（stock-main / index）
3. `stock_history`（stock）
4. `stock_review`（trade_date）
5. `stock_review_batch`
6. `market_overview` + `market_brief`
7. `sector_lookup`
8. `sector_review`
9. `sector_rotation_review`
10. `stock_candidate_scan`
11. `watchlist_review`
12. `multi_timeframe_review`

### Step 3 - 常见风险点
- 环境变量未透传（尤其 token）
- cwd 或 PYTHONPATH 错误
- 宿主注入代理变量导致上游请求异常
- Python 解释器与依赖环境不一致

---

## 4) 验收标准

满足以下条件即可判定挂载可用：
1. `--list-tools` 与宿主看到的工具集一致。
2. `provider_health` 成功。
3. 回归清单中核心链路（quote/history/review/sector）至少各成功 1 次。
4. stdio 模式下协议输出正常，无 stdout 杂日志干扰。
