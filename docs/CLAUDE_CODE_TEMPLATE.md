# Claude Code Template (`cn-stock-mcp`)

这页提供 **Claude Code** 的单独接入模板。

适用：
- 你使用 Claude Code
- 你希望通过 MCP 给 Claude Code 接入 `cn-stock-mcp`

根据 Claude Code 文档，MCP server 可以通过：
- `claude mcp add ...`
- 项目根目录 `.mcp.json`
- `~/.claude.json`

进行配置。

---

## 1) 最简单：用命令直接添加本地 stdio server

```bash
claude mcp add --transport stdio --scope user cn-stock-mcp -- cn-stock-mcp --stdio
```

说明：
- 这是最适合已安装包方式的配置。
- 你可以随后运行：

```bash
claude mcp list
claude mcp get cn-stock-mcp
```

检查是否已接入。

---

## 2) 项目级 `.mcp.json` 方式

在项目根目录创建或更新：

```text
.mcp.json
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

说明：
- Claude Code 文档明确支持 `.mcp.json`。
- 这适合项目内共享给团队。

---

## 3) 源码目录 / 虚拟环境方式

如果你还没有把 `cn-stock-mcp` 命令装进 PATH，可写成：

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

如果你需要项目相对路径，Claude Code 文档还支持：
- `${CLAUDE_PROJECT_DIR}`
- `${VAR}`
- `${VAR:-default}`

---

## 4) 推荐先做的本地自检

```bash
cn-stock-mcp --init-config
cn-stock-mcp --version
cn-stock-mcp --doctor
cn-stock-mcp --doctor-network
```

如果本地 doctor 都过不去，就先别怪 Claude Code。

---

## 5) Claude Code 验证方式

```bash
claude mcp list
claude mcp get cn-stock-mcp
```

进入 Claude Code 后，还可以查看：

```text
/mcp
```

---

## 6) 常见问题

### 项目共享配置
适合用：
- 项目根目录 `.mcp.json`

### 仅自己本机使用
适合用：
- `claude mcp add ...`
- 或写入 `~/.claude.json` 对应 scope

更多排查见：
- `docs/FAQ.md`
- `docs/HOST_CONFIG_TEMPLATES.md`
