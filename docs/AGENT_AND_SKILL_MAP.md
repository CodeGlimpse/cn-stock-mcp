# Agent and Skill Map (`cn-stock-mcp`)

这页专门回答一个常见问题：

> 这个仓库给各个 AI agent / host 用的 skill 在哪里？

## 先说结论

### 大多数 agent / host
**没有仓库内专属 skill 文件。**

它们使用这个项目的方式是：
- 直接把 `cn-stock-mcp` 当作 **MCP server** 接进去
- 按各自宿主支持的配置格式写 `command / args / env`

也就是说，下面这些通常是 **MCP 配置接入**，不是“装 skill”：

- Claude Desktop
- Claude Code
- Continue
- VS Code
- Cursor
- Cline
- Windsurf
- Hermes
- Codex

---

## 仓库内真正附带的 skill 在哪里？

### OpenClaw
这个仓库里目前真正附带、可直接称为“skill”的主要是：

- `skills/newsbot-stock-routing/SKILL.md`

相关说明：
- `skills/MIGRATION_NEWSBOT_SKILL.md`
- `docs/OPENCLAW_INTEGRATION.md`
- `docs/OPENCLAW_HOST_TEMPLATE.md`

### 这个 skill 是干什么的？
它是给 **OpenClaw / news agent** 用的路由适配层，作用是：
- 把中国市场简报 / 复盘类请求
- 路由到 `cn-stock-mcp` 的对应 tools

它不是“所有 agent 通用的 skill 标准”。

---

## 各个 agent / host 到底该看哪里？

| Agent / Host | 使用方式 | 需要仓库内 skill 吗？ | 该看哪里 | skill 在哪里 |
|---|---|---:|---|---|
| OpenClaw | MCP + 可选 OpenClaw skill adapter | 可选，需要时用 | `docs/OPENCLAW_HOST_TEMPLATE.md` / `docs/OPENCLAW_INTEGRATION.md` | `skills/newsbot-stock-routing/SKILL.md` |
| Claude Desktop | MCP 配置 | 否 | `docs/CLAUDE_DESKTOP_TEMPLATE.md` | 无 |
| Claude Code | MCP 配置 | 否 | `docs/CLAUDE_CODE_TEMPLATE.md` | 无 |
| Continue | MCP 配置 | 否 | `docs/CONTINUE_TEMPLATE.md` | 无 |
| VS Code | MCP 配置 | 否 | `docs/VSCODE_TEMPLATE.md` | 无 |
| Cursor | MCP 配置 | 否 | `docs/CURSOR_TEMPLATE.md` | 无 |
| Cline | MCP 配置 | 否 | `docs/CLINE_TEMPLATE.md` | 无 |
| Windsurf | MCP 配置 | 否 | `docs/WINDSURF_TEMPLATE.md` | 无 |
| Hermes | MCP 配置 | 否 | `docs/HERMES_TEMPLATE.md` | 无 |
| Codex | MCP 配置 | 否 | `docs/CODEX_TEMPLATE.md` | 无 |

---

## 如果你是 AI agent 作者
除了宿主模板之外，再看：

- `docs/AGENT_MINIMAL.md`
- `docs/EXAMPLES_MINIMAL.md`
- `docs/INTERFACE_SCHEMA.md`

这些文档告诉 agent：
- 默认先调用哪些 tool
- 怎么少浪费 token
- 哪些参数最容易踩坑
- `sector_lookup` / `provider_health` 这些应该怎么用

---

## 最后再强调一次

### 这个仓库最重要的交付物是：
- **MCP server**

### 不是：
- 给每个 AI agent 都单独做了一份 skill

目前仓库内真正成型的 skill 适配层，主要就是：
- `skills/newsbot-stock-routing/SKILL.md`（OpenClaw）
