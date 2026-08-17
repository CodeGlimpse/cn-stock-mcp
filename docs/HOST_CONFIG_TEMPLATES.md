# Host Config Templates (`cn-stock-mcp`)

这页提供可直接复制的 **host-specific / host-oriented 配置模板**。

如果你只想先装起来，优先看：
- `docs/HANDOFF_MINIMAL.md`

如果你已经知道自己用的是哪类宿主，直接从下面复制。

---

## 1) 已核实可直接复制的宿主模板

### OpenClaw
- `docs/OPENCLAW_HOST_TEMPLATE.md`

### Claude Desktop
- `docs/CLAUDE_DESKTOP_TEMPLATE.md`

### Claude Code
- `docs/CLAUDE_CODE_TEMPLATE.md`

### Continue
- `docs/CONTINUE_TEMPLATE.md`

### VS Code
- `docs/VSCODE_TEMPLATE.md`

### Cursor
- `docs/CURSOR_TEMPLATE.md`

### Cline
- `docs/CLINE_TEMPLATE.md`

### Windsurf
- `docs/WINDSURF_TEMPLATE.md`

### Hermes
- `docs/HERMES_TEMPLATE.md`

### Codex
- `docs/CODEX_TEMPLATE.md`

### 通用 `mcpServers` JSON 宿主
如果你的宿主明确支持下面这种标准结构：

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

那就可以直接复用：
- `.mcp.sample.json`

---

## 2) 通用 MCP host：已安装包（最推荐）

适用：
- 你的宿主支持 MCP
- 你已经执行过 `python -m pip install cn-stock-mcp==0.2.0`
- 你已经运行 `cn-stock-mcp --init-config`，并由用户手动填写 token
- 宿主配置里可以填写 `command / args / env`

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
- 这是最适合最终用户的配置形态。
- 根目录也提供了同内容示例：`.mcp.sample.json`

---

## 3) 通用 MCP host：源码目录 / 虚拟环境方式

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
        "PYTHONPATH": "src"
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

## 5) 其他常见 MCP host：如何安全套用

有些常见宿主也支持 MCP，但它们的文档页面、配置文件路径、或外围字段命名会变化很快。

为了避免把“看起来像对、实际不能贴”的模板写死，这里给你的安全策略是：

1. 先确认该宿主是否支持 **标准 `mcpServers` 结构** 或它自己的已核实 MCP 配置结构
2. 如果支持标准 `mcpServers`，优先直接套用：
   - `.mcp.sample.json`
   - 或本页的“已安装包方式”模板
3. 如果宿主使用自定义顶层字段（例如 VS Code 的 `servers`，Hermes 的 `mcp_servers`，Codex 的 `config.toml` 表结构），优先参考对应单独模板页
4. 如果宿主还要求额外外层字段、特定配置文件路径、或 UI 导入方式，再把标准块嵌进去

如果你不确定，优先回到：
- `docs/HANDOFF_MINIMAL.md`
- `docs/FAQ.md`

---

## 6) 不确定该用哪种模板时

按这个顺序选：
1. **是 OpenClaw** → 用 `docs/OPENCLAW_HOST_TEMPLATE.md`
2. **是 Claude Desktop** → 用 `docs/CLAUDE_DESKTOP_TEMPLATE.md`
3. **是 Claude Code** → 用 `docs/CLAUDE_CODE_TEMPLATE.md`
4. **是 Continue** → 用 `docs/CONTINUE_TEMPLATE.md`
5. **是 VS Code** → 用 `docs/VSCODE_TEMPLATE.md`
6. **是 Cursor** → 用 `docs/CURSOR_TEMPLATE.md`
7. **是 Cline** → 用 `docs/CLINE_TEMPLATE.md`
8. **是 Windsurf** → 用 `docs/WINDSURF_TEMPLATE.md`
9. **是 Hermes** → 用 `docs/HERMES_TEMPLATE.md`
10. **是 Codex** → 用 `docs/CODEX_TEMPLATE.md`
11. **能直接安装包且支持标准 `mcpServers`** → 用“已安装包”模板
12. **只能跑源码目录** → 用“源码目录 / 虚拟环境”模板
13. **宿主还支持 rules / instructions** → 在前面模板基础上再加 `.agent-hints.json` 的规则
