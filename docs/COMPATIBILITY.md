# Compatibility (`cn-stock-mcp`)

本项目的核心交付物是 **MCP server**。只要宿主支持 MCP（stdio transport），就可以接入。

如果你只想找可复制配置，优先看：
- `docs/HOST_CONFIG_TEMPLATES.md`

## 1) 支持层级

### A. MCP-only host

适用：
- 只支持 MCP
- 不支持 skill / rules 包

建议使用：
- `.mcp.sample.json`
- `docs/HANDOFF_MINIMAL.md`
- `docs/HOST_CONFIG_TEMPLATES.md`
- `docs/EXAMPLES_MINIMAL.md`

### B. MCP + custom instructions / rules host

适用：
- 支持 MCP
- 也支持额外 system prompt、规则文件或 agent 文档
- 但不一定有原生 skill 包机制

建议使用：
- `.mcp.sample.json`
- `docs/HANDOFF_MINIMAL.md`
- `docs/HOST_CONFIG_TEMPLATES.md`
- `docs/AGENT_MINIMAL.md`
- `docs/EXAMPLES_MINIMAL.md`
- `.agent-hints.json`

### C. MCP + native skill host

适用：
- 支持 MCP
- 也支持自己的 skill / plugin / capability package 机制

建议使用：
- 先使用通用 MCP 交付物
- 再针对宿主做一层薄 adapter
- 不要把某个平台的 skill 直接当成跨平台 skill 标准

当前仓库内已提供的宿主专属示例：
- OpenClaw

相关文档：
- `docs/HOST_CONFIG_TEMPLATES.md`
- `docs/OPENCLAW_INTEGRATION.md`

## 2) 当前仓库中的平台专属内容

以下内容是 **OpenClaw adapter**，不是通用 MCP 标准的一部分：

- `skills/newsbot-stock-routing/`
- `skills/MIGRATION_NEWSBOT_SKILL.md`
- `docs/OPENCLAW_INTEGRATION.md`

## 3) 当前仓库中的通用交付物

以下内容应视为跨平台的 canonical docs：

- `.mcp.sample.json`
- `docs/HANDOFF_MINIMAL.md`
- `docs/HOST_CONFIG_TEMPLATES.md`
- `docs/FAQ.md`
- `docs/AGENT_MINIMAL.md`
- `docs/EXAMPLES_MINIMAL.md`
- `docs/EXAMPLES_FULL.md`
- `docs/INTERFACE_SCHEMA.md`
- `docs/ERROR_MODEL.md`
- `.agent-hints.json`

## 4) 推荐定位

- **MCP server**：跨平台核心产品
- **agent docs**：跨平台指导层
- **skills/**：特定宿主的薄适配层
