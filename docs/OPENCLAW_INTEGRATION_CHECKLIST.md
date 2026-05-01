# 挂载联调清单

## 目标
验证 `openclaw-stock-mcp` 能被 OpenClaw 作为 MCP stdio server 拉起、列出工具并成功调用。

## 前置条件
1. 项目路径存在：
   - `/home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp`
2. Python 环境存在：
   - `/tmp/openclaw-stock-mcp-venv/bin/python`
3. `.env` 已配置智兔 token
4. 本地 smoke test 已通过主要链路

## 联调步骤

### Step 1：本地命令验证
- `--list-tools`
- `provider_health`
- `--stdio`

### Step 2：OpenClaw MCP 配置
使用文档中的 JSON 或 `/mcp set` 样例完成配置。

### Step 3：宿主识别验证
确认 OpenClaw 侧能看到以下 tools：
- `stock_search`
- `stock_quote`
- `stock_history`
- `market_overview`
- `technical_indicator`
- `market_pool`
- `stock_orderbook`
- `provider_health`

### Step 4：宿主调用验证
建议按顺序测试：
1. `provider_health`
2. `stock_quote(index)`
3. `stock_history(index)`
4. `stock_quote(fund)`
5. `market_pool(limit_up)`
6. `stock_orderbook(star)`
7. `stock_history(stock)`

## 预期风险点
1. 宿主对 stdio tool schema 的兼容差异
2. 环境变量或 cwd 传递错误
3. Python 解释器路径与依赖环境不一致
4. 宿主仍然注入代理环境导致外部请求异常

## 建议
- 首次挂载优先用 `/tmp/openclaw-stock-mcp-venv/bin/python`
- 强制清空代理相关环境变量
- 如果 OpenClaw 支持日志，优先看 stderr
