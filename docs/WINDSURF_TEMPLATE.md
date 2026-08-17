# Windsurf Template (`cn-stock-mcp`)

这页提供 **Windsurf / Cascade** 的单独配置模板。

适用：
- 你使用 Windsurf
- 你希望把 `cn-stock-mcp` 作为 MCP server 接进 Cascade

根据 Windsurf 官方文档：
- 配置文件是 `~/.codeium/windsurf/mcp_config.json`
- 顶层字段使用 `mcpServers`
- 支持 `stdio` / `Streamable HTTP` / `SSE`
- 本地 server 直接用 `command` / `args` / `env`

---

## 1) 手工配置 `mcp_config.json`

编辑：

```text
~/.codeium/windsurf/mcp_config.json
```

写入：

```json
{
  "mcpServers": {
    "cn-stock-mcp": {
      "command": "cn-stock-mcp",
      "args": ["--stdio"]
    }
  }
}
```

---

## 2) 源码目录 / 虚拟环境方式

```json
{
  "mcpServers": {
    "cn-stock-mcp": {
      "command": "/path/to/cn-stock-mcp/.venv/bin/python",
      "args": ["-m", "cn_stock_mcp.main", "--stdio"],
      "env": {
        "PYTHONPATH": "src"
      }
    }
  }
}
```

---

## 3) Windsurf 的几个特殊点

Windsurf 官方文档还说明了：
- 支持 MCP Marketplace
- 支持 `windsurf://windsurf-mcp-registry?...` deeplink
- 支持 `serverUrl` / `url` 形式的远程 MCP
- 支持 `${env:VAR}` 与 `${file:/path}` 插值

但对本项目来说，**最简单仍然是本地 stdio**。

---

## 4) 推荐先做的本地自检

```bash
cn-stock-mcp --version
cn-stock-mcp --doctor
cn-stock-mcp --doctor-network
```

---

## 5) Windsurf 接入后看不到 tools

优先排查：
1. `~/.codeium/windsurf/mcp_config.json` 是否写对
2. 是否在 Cascade 的 MCP 页面里真正启用了该 server
3. `command` / `args` / `env` 是否填错
4. 团队版是否被管理员 whitelist / registry 策略拦住
5. `cn-stock-mcp --doctor` 是否本地已失败

更多排查见：
- `docs/FAQ.md`
- `docs/HOST_CONFIG_TEMPLATES.md`
