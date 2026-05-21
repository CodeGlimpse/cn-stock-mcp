# VS Code Template (`cn-stock-mcp`)

这页提供 **VS Code** 的单独接入模板。

适用：
- 你使用支持 MCP 的 VS Code
- 你希望通过 `mcp.json` 接入 `cn-stock-mcp`

根据 VS Code 文档，MCP server 配置通常写在：
- 工作区：`.vscode/mcp.json`
- 用户配置：通过 `MCP: Open User Configuration` 打开的 `mcp.json`

注意：VS Code 使用的顶层字段是：
- `servers`

而不是：
- `mcpServers`

---

## 1) 工作区级配置（最常用）

创建：

```text
.vscode/mcp.json
```

写入：

```json
{
  "servers": {
    "cnStockMcp": {
      "type": "stdio",
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
- VS Code 文档建议 server name 使用 camelCase，因此这里用 `cnStockMcp`。
- 修改配置后，VS Code 可能需要重新启动 server 才会重新发现 tools。

---

## 2) 用户级配置

如果你想在所有工作区复用，运行：

```text
MCP: Open User Configuration
```

然后把同样的 `servers` 块写进去。

---

## 3) 源码目录 / 虚拟环境方式

如果你还没把包装进 PATH：

```json
{
  "servers": {
    "cnStockMcp": {
      "type": "stdio",
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

如果你希望减少明文 token，可以改用 VS Code 的 `inputs`。

---

## 4) VS Code 的 input 变量方式（更适合敏感信息）

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "zhitu-token",
      "description": "ZHITU Token",
      "password": true
    }
  ],
  "servers": {
    "cnStockMcp": {
      "type": "stdio",
      "command": "cn-stock-mcp",
      "args": ["--stdio"],
      "env": {
        "ZHITU_TOKEN": "${input:zhitu-token}"
      }
    }
  }
}
```

---

## 5) 推荐先做的本地自检

```bash
cn-stock-mcp --version
cn-stock-mcp --doctor
cn-stock-mcp --doctor-network
```

---

## 6) VS Code 接入后看不到 tools

优先排查：
1. `mcp.json` 是否放在对的位置
2. 顶层字段是否写成了 `servers`（不是 `mcpServers`）
3. server name 是否规范
4. `command` / `args` / `env` 是否写错
5. 是否需要在 VS Code 里重启 MCP server / 查看输出日志

更多排查见：
- `docs/FAQ.md`
- `docs/HOST_CONFIG_TEMPLATES.md`
