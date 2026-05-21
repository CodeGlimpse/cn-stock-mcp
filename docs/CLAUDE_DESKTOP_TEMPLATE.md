# Claude Desktop Template (`cn-stock-mcp`)

这页提供 **Claude Desktop 的单独配置模板**。

适用：
- 你使用 Claude Desktop
- Claude Desktop 支持本地 MCP server
- 你想直接把 `cn-stock-mcp` 接进去

Claude Desktop 的 MCP 配置文件通常是：
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`

---

## 1) 最推荐：已安装包方式

先安装：

```bash
python -m pip install cn-stock-mcp
```

再把下面内容写进 Claude Desktop 配置文件：

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

保存后，**完全退出并重启 Claude Desktop**。

---

## 2) 源码目录 / 虚拟环境方式

适用：
- 你拿到的是源码仓库
- 你没有把包安装进全局 / 当前 PATH

```json
{
  "mcpServers": {
    "cn-stock-mcp": {
      "command": "/path/to/cn-stock-mcp/.venv/bin/python",
      "args": ["-m", "cn_stock_mcp.main", "--stdio"],
      "cwd": "/path/to/cn-stock-mcp",
      "env": {
        "PYTHONPATH": "src",
        "ZHITU_TOKEN": "replace-with-your-token"
      }
    }
  }
}
```

把 `/path/to/cn-stock-mcp` 替换成你的实际项目目录。

---

## 3) 推荐先做的本地自检

在接入 Claude Desktop 前，建议先跑：

```bash
cn-stock-mcp --version
cn-stock-mcp --doctor
cn-stock-mcp --doctor-network
```

如果 `--doctor-network` 失败，先不要急着怪 Claude Desktop，优先检查：
- token 是否正确
- 本地网络是否能访问上游
- 当前 Python 环境是否就是你实际挂载的那个环境

---

## 4) 接入后如果看不到 tools

优先排查：
1. Claude Desktop 是否已完全重启
2. JSON 是否写错
3. `command` / `cwd` / `env` 是否填错
4. `cn-stock-mcp --doctor` 是否本地就已经报错

更多排查见：
- `docs/FAQ.md`
- `docs/HOST_CONFIG_TEMPLATES.md`
