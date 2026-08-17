# Hermes Template (`cn-stock-mcp`)

这页提供 **Hermes Agent** 的单独配置模板。

适用：
- 你使用 Hermes Agent
- 你希望把 `cn-stock-mcp` 作为 MCP server 配进 Hermes

根据 Hermes 官方文档：
- Hermes 从 `~/.hermes/config.yaml` 读取 MCP 配置
- MCP server 定义写在 `mcp_servers:` 下
- 本地 stdio server 用 `command` / `args` / `env`
- 远程 server 用 `url` / `headers`

---

## 1) 最推荐：在 `~/.hermes/config.yaml` 里添加一个 stdio server

```yaml
mcp_servers:
  cn_stock_mcp:
    command: "cn-stock-mcp"
    args: ["--stdio"]
    tools:
      include: [stock_search, market_brief, stock_snapshot, stock_quote, stock_history, stock_review, watchlist_review, trading_calendar, sector_review, hot_theme_tracker]
```

说明：
- `cn_stock_mcp` 是 Hermes 内部使用的 server 名。
- Hermes 会自动发现并注册对应工具。

---

## 2) 源码目录 / 虚拟环境方式

```yaml
mcp_servers:
  cn_stock_mcp:
    command: "/path/to/cn-stock-mcp/.venv/bin/python"
    args: ["-m", "cn_stock_mcp.main", "--stdio"]
    env:
      PYTHONPATH: "src"
```

---

## 3) Hermes 的 MCP 特性说明

Hermes 官方文档里还明确支持：
- `enabled: false`
- `tools.include`
- `tools.exclude`
- `tools.prompts`
- `tools.resources`
- `supports_parallel_tool_calls`
- `sampling` 配置

所以如果你后面想对 `cn-stock-mcp` 做更严格的工具白名单，也可以这样写：

```yaml
mcp_servers:
  cn_stock_mcp:
    command: "cn-stock-mcp"
    args: ["--stdio"]
    tools:
      include: [stock_search, market_brief, stock_snapshot, stock_quote, stock_history, stock_review, watchlist_review, trading_calendar, sector_review, hot_theme_tracker]
      prompts: false
      resources: false
```

不过对最终用户来说，**第一版不建议先加太多过滤条件**。

---

## 4) 修改后如何生效

Hermes 官方文档建议：
- 启动 Hermes：`hermes chat`
- 修改 MCP 配置后执行：`/reload-mcp`

---

## 5) 推荐先做的本地自检

```bash
cn-stock-mcp --init-config
cn-stock-mcp --version
cn-stock-mcp --doctor
cn-stock-mcp --doctor-network
```

---

## 6) Hermes 接入后看不到 tools

优先排查：
1. `~/.hermes/config.yaml` 是否写在 `mcp_servers:` 下
2. `enabled: false` 是否误开
3. `tools.include` 是否把大部分工具过滤没了
4. `command` / `args` / `env` 是否写错
5. 修改后是否执行了 `/reload-mcp`

更多排查见：
- `docs/FAQ.md`
- `docs/HOST_CONFIG_TEMPLATES.md`
