# Docs Guide (`cn-stock-mcp`)

Last Updated: 2026-09-05

本目录只保留当前有效的运行文档。

Windows + AI 自部署请先阅读 `AI_DEPLOY_WINDOWS.md`；发布边界见 `SECURITY.md`、`PRIVACY.md`、`DATA_SOURCES.md` 和 `SUPPORT.md`。

wheel 安装后可运行 `cn-stock-mcp --docs-path` 定位本目录的已安装副本。

## 先看哪一页？

### 如果你是人类用户 / 项目接收方
先看：

1. `PRODUCT_OVERVIEW.md`
   - 对外产品定位、功能亮点和适用场景。

2. `CUSTOMER_DEPLOYMENT.md`
   - 客户安装、智兔 token 获取、Host 接入、排障和免责声明。

3. `START_HERE.md`
   - 整个仓库的最友好入口。

4. `AI_DEPLOY_WINDOWS.md`
   - 固定版本安装、token 交接和首次问答验收合同。

5. `AI_DEPLOY_PROMPT.md`
   - 客户直接复制给具备本机权限的 AI Agent 的部署提示词。

6. `HANDOFF_MINIMAL.md`
   - 一页安装与接入说明。

7. `HOST_CONFIG_TEMPLATES.md`
   - 按宿主类型选择模板入口。

8. `AI_ONBOARDING.md`
   - 给 AI 集成人员 / agent 作者的使用说明。

9. `AGENT_AND_SKILL_MAP.md`
   - 解释哪些平台只是接 MCP，哪些才有仓库内 skill，以及 skill 文件在哪。

10. `FAQ.md`
   - 常见错误与排查。

11. `COMMERCIAL_DELIVERY_TEMPLATE.md`
   - 一次性销售范围、验收、支持、退款字段和 MIT 边界模板。

---

## 给最终用户 / 本地 AI agent 的阅读顺序

1. `HANDOFF_MINIMAL.md`
2. `HOST_CONFIG_TEMPLATES.md`
3. `OPENCLAW_HOST_TEMPLATE.md` / `CLAUDE_DESKTOP_TEMPLATE.md` / `CLAUDE_CODE_TEMPLATE.md` / `CONTINUE_TEMPLATE.md` / `VSCODE_TEMPLATE.md` / `CURSOR_TEMPLATE.md` / `CLINE_TEMPLATE.md` / `WINDSURF_TEMPLATE.md` / `HERMES_TEMPLATE.md` / `CODEX_TEMPLATE.md`
4. `FAQ.md`

---

## 给 AI agent / AI 集成人员的阅读顺序

1. `AI_ONBOARDING.md`
   - 人类可读的 AI 集成说明。

2. `AGENT_MINIMAL.md`
   - 最小路由、最小 payload、最容易踩坑的契约。

3. `EXAMPLES_MINIMAL.md`
   - 最小可工作的调用示例。

4. `INTERFACE_SCHEMA.md`
   - 需要详细输入输出契约、枚举、symbol/interval 约束时再看。

---

## 给集成 / 联调人员的阅读顺序

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

7. `P2_DELIVERY_RECORD_2026-08-13.md`
   - 本次实时数据、日期兼容、stdio 和 Python 运行时验证记录。

8. `P2_DELIVERY_RECORD_2026-08-14.md`
   - 接口文档同步与统一数据新鲜度元数据交付记录。

9. `TOOL_CATALOG.md`
   - 从 MCP registry 自动生成的 53 个工具目录、参数 schema、最小示例和 Provider route。

10. `RELEASE_NOTE_v0.2.1.md`
   - 当前修复版本的变更、升级方法与已知边界。

---

## 文档定位约定（避免重复/过时）

- 仓库人类入口：只在 `START_HERE.md` 维护。
- AI 集成说明：只在 `AI_ONBOARDING.md` 维护。
- 功能事实：只在 `IMPLEMENTATION_STATUS.md` 维护。
- 协议契约：只在 `INTERFACE_SCHEMA.md` 维护。
- 错误语义：只在 `ERROR_MODEL.md` 维护。
- 部署联调：只在 `INTEGRATION.md` 维护。
- 最终用户快速入口：只在 `HANDOFF_MINIMAL.md` / `HOST_CONFIG_TEMPLATES.md` / `FAQ.md` 维护。
- agent / skill 对照关系：只在 `AGENT_AND_SKILL_MAP.md` 维护。
- 宿主专属最终配置：只在各自的 `*_TEMPLATE.md` 维护。
- 阶段性交付证据：以带日期的 `P2_DELIVERY_RECORD_*.md` 为准，不改写历史验证记录。

如果某条信息出现在多个文件，以以上“单一事实源”优先。
