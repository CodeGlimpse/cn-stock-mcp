# Cline Template (`cn-stock-mcp`)

这页提供 **Cline** 的单独配置模板。

适用：
- 你使用 Cline
- 你希望把 `cn-stock-mcp` 接到 Cline 的 MCP servers

根据 Cline 官方文档：
- CLI 配置文件是 `~/.cline/mcp.json`
- IDE 扩展可以从 MCP 配置面板打开对应 JSON
- 顶层字段使用 `mcpServers`
- 本地 server 用 `command + args`
- 远程 server 用 `url`

---

## 1) CLI 方式：编辑 `~/.cline/mcp.json`

写入：

```json
{
  "mcpServers": {
    "cn-stock-mcp": {
      "command": "cn-stock-mcp",
      "args": ["--stdio"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

说明：
- `autoApprove` 建议默认留空，不要直接放开。
- 这样更适合面向真实用户的安全默认值。

---

## 2) IDE 扩展方式

在 Cline 面板里：
1. 打开 **MCP Servers**
2. 进入 **Configure**
3. 点击 **Configure MCP Servers**
4. 在打开的 JSON 里添加同样的 `mcpServers` 块

可直接使用：

```json
{
  "mcpServers": {
    "cn-stock-mcp": {
      "command": "cn-stock-mcp",
      "args": ["--stdio"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

---

## 3) 源码目录 / 虚拟环境方式

```json
{
  "mcpServers": {
    "cn-stock-mcp": {
      "command": "/path/to/cn-stock-mcp/.venv/bin/python",
      "args": ["-m", "cn_stock_mcp.main", "--stdio"],
      "env": {
        "PYTHONPATH": "src"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

---

## 4) Cline CLI 向导方式

Cline 官方文档还支持：

```bash
cline mcp
```

它会交互式引导你：
- 添加 server
- 修改 server
- 启停 server
- 删除 server

如果你不想手改 JSON，可以先走向导，再对照本页修正。

---

## 5) 推荐先做的本地自检

```bash
cn-stock-mcp --version
cn-stock-mcp --doctor
cn-stock-mcp --doctor-network
```

---

## 6) Cline 接入后看不到 tools

优先排查：
1. 是否写到了正确的 MCP config JSON
2. `mcpServers` 顶层字段是否正确
3. server 是否被 `disabled: true`
4. `autoApprove` 是否误配置成不合理值
5. `cn-stock-mcp --doctor` 是否本地就已失败

更多排查见：
- `docs/FAQ.md`
- `docs/HOST_CONFIG_TEMPLATES.md`
