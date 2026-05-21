# Host Config Templates (`cn-stock-mcp`)

这页提供可直接复制的 **host-specific / host-oriented 配置模板**。

如果你只想先装起来，优先看：
- `docs/HANDOFF_MINIMAL.md`

如果你已经知道自己用的是哪类宿主，直接从下面复制。

---

## 1) 通用 MCP host：已安装包（最推荐）

适用：
- 你的宿主支持 MCP
- 你已经执行过 `python -m pip install cn-stock-mcp`
- 宿主配置里可以填写 `command / args / env`

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
- 这是最适合最终用户的配置形态。
- 根目录也提供了同内容示例：`.mcp.sample.json`

---

## 2) 通用 MCP host：源码目录 / 虚拟环境方式

适用：
- 你拿到的是源码仓库
- 你想直接用项目虚拟环境运行
- 宿主支持 `cwd`

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

说明：
- `/path/to/cn-stock-mcp` 改成你的实际项目目录。
- 如果你的宿主会自动注入代理变量，而你又不希望上游请求走代理，可以显式补：

```json
{
  "HTTP_PROXY": "",
  "HTTPS_PROXY": "",
  "ALL_PROXY": "",
  "http_proxy": "",
  "https_proxy": "",
  "all_proxy": ""
}
```

---

## 3) OpenClaw：MCP 接入 + 可选 skill adapter

### 3.1 仅接入 MCP server

OpenClaw 如果使用通用 MCP 配置块，可以直接复用下面这一段：

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

### 3.2 同时启用仓库内附带的 OpenClaw skill adapter

如果你还想启用仓库内的 `skills/newsbot-stock-routing/`，再追加：

```json5
{
  skills: {
    load: {
      extraDirs: [
        "/path/to/cn-stock-mcp/skills"
      ]
    },
    entries: {
      "newsbot-stock-routing": { enabled: true }
    }
  }
}
```

更多 OpenClaw 专属说明见：
- `docs/OPENCLAW_INTEGRATION.md`

---

## 4) MCP + custom instructions / rules host

适用：
- 宿主不仅支持 MCP
- 还支持 system prompt / rules / agent instructions

这类宿主建议：
1. 先使用上面的 MCP 配置模板
2. 再补最小规则

可直接参考仓库里的：
- `.agent-hints.json`
- `docs/AGENT_MINIMAL.md`

建议规则最小集：
- 名称/代码不确定时，先 `stock_search`
- 默认小参数：`limit=5`、`top_n=3`
- 不要默认先跑 `provider_health`
- `sector_lookup(mode=children|members)` 时必须显式传 `sector_type=primary|concept`

---

## 5) 不确定该用哪种模板时

按这个顺序选：
1. **能直接安装包** → 用“已安装包”模板
2. **只能跑源码目录** → 用“源码目录 / 虚拟环境”模板
3. **是 OpenClaw** → 用 OpenClaw 模板
4. **宿主还支持 rules / instructions** → 在前面模板基础上再加 `.agent-hints.json` 的规则
