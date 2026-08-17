# Continue Template (`cn-stock-mcp`)

这页提供 **Continue** 的单独配置模板。

适用：
- 你使用 Continue
- 你希望在 Continue 的 agent mode 中接入 `cn-stock-mcp`

根据 Continue 文档，MCP 可以通过 `mcpServers` 配置，并且：
- 可以放在 `.continue/mcpServers/` 下的独立配置文件里
- 也可以直接复用来自 Claude Desktop / Cursor / Cline 等的 JSON MCP 配置

---

## 1) 最简单：直接复用标准 JSON MCP 配置

在你的工作区创建：

```text
.continue/mcpServers/cn-stock-mcp.json
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

这是最适合最终用户的 Continue 方式。

---

## 2) Continue 原生 block 文件方式

如果你想用 Continue 文档里更“原生”的 block file 形式，可在：

```text
.continue/mcpServers/cn-stock-mcp.yaml
```

写入：

```yaml
name: cn-stock-mcp
version: 0.2.0
schema: v1
mcpServers:
  - name: cn-stock-mcp
    type: stdio
    command: cn-stock-mcp
    args:
      - --stdio
```

说明：
- Continue 文档要求 standalone block file 带 `name` / `version` / `schema`。
- MCP 只在 Continue 的 **agent mode** 中可用。

---

## 3) 源码目录 / 虚拟环境方式

如果你拿到的是源码仓库，而不是已安装包：

```json
{
  "mcpServers": {
    "cn-stock-mcp": {
      "command": "/path/to/cn-stock-mcp/.venv/bin/python",
      "args": ["-m", "cn_stock_mcp.main", "--stdio"],
      "cwd": "/path/to/cn-stock-mcp",
      "env": {
        "PYTHONPATH": "src"
      }
    }
  }
}
```

---

## 4) 使用前建议先做的自检

```bash
cn-stock-mcp --version
cn-stock-mcp --doctor
cn-stock-mcp --doctor-network
```

如果 `--doctor-network` 失败，先检查 token / 网络，再排查 Continue。

---

## 5) 接入后看不到 tools 怎么办

优先检查：
1. 是否在 Continue 的 **agent mode**
2. 配置文件路径是否正确
3. 是否写成了 `.continue/mcpServers/`（注意是复数）
4. `cn-stock-mcp --doctor` 本地是否已报错

更多排查见：
- `docs/FAQ.md`
- `docs/HOST_CONFIG_TEMPLATES.md`
