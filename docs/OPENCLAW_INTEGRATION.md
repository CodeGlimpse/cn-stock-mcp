# OpenClaw Integration (`cn-stock-mcp`)

本页只保留 **OpenClaw 专属适配说明**。

如果你只是想直接复制 OpenClaw 配置，优先看：
- `docs/OPENCLAW_HOST_TEMPLATE.md`

如果你只是想把本项目接到任意 MCP host，请优先看：
- `docs/HANDOFF_MINIMAL.md`
- `docs/COMPATIBILITY.md`
- `.mcp.sample.json`

## 1) OpenClaw MCP 挂载

OpenClaw 侧可使用两种形态：
- **包安装方式**：`command: "cn-stock-mcp"`, `args: ["--stdio"]`
- **源码目录方式**：`command: "/path/to/.venv/bin/python"`, `args: ["-m", "cn_stock_mcp.main", "--stdio"]`, `cwd`, `env.PYTHONPATH=src`

最终可复制配置见：
- `docs/OPENCLAW_HOST_TEMPLATE.md`

## 2) OpenClaw skill adapter

仓库内置 OpenClaw skill adapter：
- `skills/newsbot-stock-routing/`

加载方式示例：

```json5
{
  skills: {
    load: {
      extraDirs: [
        "/home/openclaw/桌面/openclaw/codes/cn-stock-mcp/skills"
      ]
    },
    entries: {
      "newsbot-stock-routing": { enabled: true }
    }
  }
}
```

说明：
- `skills.load.extraDirs` 由 OpenClaw 本地文档确认支持。
- `skills.entries.<skill>.enabled` 由 OpenClaw 本地文档确认支持。
- 这层是 OpenClaw 平台适配，不是通用 MCP 标准的一部分。

## 3) OpenClaw 验证命令

```bash
openclaw skills list --eligible
openclaw skills info newsbot-stock-routing
```

如果只是验证 MCP server 本体，先运行：

```bash
cn-stock-mcp --list-tools
cn-stock-mcp --tool provider_health --payload '{}'
```

## 4) 维护规则

修改以下内容时，同步审阅 `skills/newsbot-stock-routing/`：
- provider routing
- payload validation
- `market_brief`
- `sector_review`
- `sector_rotation_review`
- `review_envelope_v1`
- `sentiment_temperature_v1`
- `rotation_signal_v1`
