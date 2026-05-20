# OpenClaw Integration (`cn-stock-mcp`)

本页只保留 **OpenClaw 专属适配说明**。

如果你只是想把本项目接到任意 MCP host，请优先看：
- `docs/HANDOFF_MINIMAL.md`
- `docs/COMPATIBILITY.md`
- `.mcp.sample.json`

## 1) OpenClaw MCP 挂载

OpenClaw 侧可直接使用 `.mcp.sample.json` 的配置思路，核心字段：
- `command`
- `args=["-m", "cn_stock_mcp.main", "--stdio"]`
- `cwd`
- `env.PYTHONPATH=src`

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

## 3) OpenClaw 验证命令

```bash
openclaw skills list --eligible
openclaw skills info newsbot-stock-routing
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
