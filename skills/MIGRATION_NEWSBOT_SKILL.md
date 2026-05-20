# Newsbot skill migration

仅保留最小迁移说明。

- 当前 skill 目录：`skills/newsbot-stock-routing/`
- OpenClaw 通过 `skills.load.extraDirs += /home/openclaw/桌面/openclaw/codes/cn-stock-mcp/skills` 加载
- 修改 `market_brief / sector_review / review_envelope_v1 / sentiment_temperature_v1 / rotation_signal_v1 / provider routing / payload validation` 时，同步审阅该 skill

验证命令：

```bash
openclaw skills list --eligible | grep newsbot-stock-routing
openclaw skills info newsbot-stock-routing
```
