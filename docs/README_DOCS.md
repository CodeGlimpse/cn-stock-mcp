# Docs Guide (`cn-stock-mcp`)

Last Updated: 2026-05-21

本目录只保留当前有效的运行文档。

## 1) 给最终用户 / 本地 AI agent 的最短阅读顺序

1. `HANDOFF_MINIMAL.md`
   - 一页安装与接入说明。

2. `HOST_CONFIG_TEMPLATES.md`
   - 按宿主类型选择模板入口。

3. `OPENCLAW_HOST_TEMPLATE.md` / `CLAUDE_DESKTOP_TEMPLATE.md` / `CLAUDE_CODE_TEMPLATE.md` / `CONTINUE_TEMPLATE.md` / `VSCODE_TEMPLATE.md` / `CURSOR_TEMPLATE.md` / `CLINE_TEMPLATE.md` / `WINDSURF_TEMPLATE.md` / `HERMES_TEMPLATE.md` / `CODEX_TEMPLATE.md`
   - 宿主专属的最终可复制配置块。

4. `FAQ.md`
   - 常见错误与排查。

## 2) 给 AI agent 的最短阅读顺序

1. `AGENT_MINIMAL.md`
   - 最小路由、最小 payload、最容易踩坑的契约。

2. `EXAMPLES_MINIMAL.md`
   - 最小可工作的调用示例。

3. `INTERFACE_SCHEMA.md`
   - 需要详细输入输出契约、枚举、symbol/interval 约束时再看。

## 3) 给集成 / 联调人员的阅读顺序

1. `INTEGRATION.md`
   - 本地启动 stdio、通用挂载、自检与联调清单。

2. `COMPATIBILITY.md`
   - MCP-only / rules-based / skill-based host 的适配边界。

3. `HOST_CONFIG_TEMPLATES.md`
   - 已核实宿主模板总入口。

4. `IMPLEMENTATION_STATUS.md`
   - 当前实现状态、验证范围、限制。

5. `ERROR_MODEL.md`
   - 统一错误码、retry/fallback 语义。

6. `OPENCLAW_INTEGRATION.md`
   - 仅在你使用 OpenClaw 时再看。

---

## 文档定位约定（避免重复/过时）

- 功能事实：只在 `IMPLEMENTATION_STATUS.md` 维护。
- 协议契约：只在 `INTERFACE_SCHEMA.md` 维护。
- 错误语义：只在 `ERROR_MODEL.md` 维护。
- 部署联调：只在 `INTEGRATION.md` 维护。
- 最终用户快速入口：只在 `HANDOFF_MINIMAL.md` / `HOST_CONFIG_TEMPLATES.md` / `FAQ.md` 维护。
- 宿主专属最终配置：只在各自的 `*_TEMPLATE.md` 维护。

如果某条信息出现在多个文件，以以上“单一事实源”优先。
