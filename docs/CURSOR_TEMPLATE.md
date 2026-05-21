# Cursor Template (`cn-stock-mcp`)

这页提供 **Cursor** 的单独配置模板。

适用：
- 你使用 Cursor
- 你希望把 `cn-stock-mcp` 作为 MCP server 接进去

根据 Cursor 官方 MCP 文档：
- 配置文件支持 `mcp.json`
- 项目级位置：`.cursor/mcp.json`
- 全局位置：`~/.cursor/mcp.json`
- 顶层字段使用 `mcpServers`

---

## 1) 项目级配置（最推荐）

创建：

```text
.cursor/mcp.json
```

写入：

```json
{
  "mcpServers": {
    "cn-stock-mcp": {
      "command": "cn-stock-mcp",
      "args": ["--stdio"],
      "env": {
        "ZHITU_TOKEN": "replace-with-your-token"
      }
    }
  }
}
```

说明：
- 这是最适合项目内共享的方式。
- Cursor 会把项目级 MCP 只作用于当前工程。

---

## 2) 全局配置

创建：

```text
~/.cursor/mcp.json
```

写入同样的：

```json
{
  "mcpServers": {
    "cn-stock-mcp": {
      "command": "cn-stock-mcp",
      "args": ["--stdio"],
      "env": {
        "ZHITU_TOKEN": "replace-with-your-token"
      }
    }
  }
}
```

适用：
- 你想在所有项目里都能直接使用 `cn-stock-mcp`

---

## 3) 源码目录 / 虚拟环境方式

如果你拿到的是源码仓库，而不是已安装包：

```json
{
  "mcpServers": {
    "cn-stock-mcp": {
      "command": "/path/to/cn-stock-mcp/.venv/bin/python",
      "args": ["-m", "cn_stock_mcp.main", "--stdio"],
      "env": {
        "PYTHONPATH": "src",
        "ZHITU_TOKEN": "replace-with-your-token"
      }
    }
  }
}
```

如果服务脚本就在工作区内，也可以使用 Cursor 文档支持的变量，比如：
- `${workspaceFolder}`
- `${userHome}`
- `${env:NAME}`

---

## 4) Cursor 对 stdio server 的补充说明

Cursor 官方文档提到：
- `mcpServers` 支持 `command` / `args` / `env`
- stdio server 还可使用 `envFile`
- 远程 server 支持 `url` / `headers` / OAuth

本项目当前最推荐的是 **本地 stdio 配置**，不要额外复杂化。

---

## 5) 推荐先做的本地自检

```bash
cn-stock-mcp --version
cn-stock-mcp --doctor
cn-stock-mcp --doctor-network
```

---

## 6) Cursor 接入后看不到 tools

优先排查：
1. `mcp.json` 是否放在 `.cursor/` 或 `~/.cursor/`
2. 顶层字段是否写成 `mcpServers`
3. `command` / `args` / `env` 是否填错
4. Cursor 的 MCP Logs 是否有报错
5. `cn-stock-mcp --doctor` 本地是否已经失败

更多排查见：
- `docs/FAQ.md`
- `docs/HOST_CONFIG_TEMPLATES.md`
