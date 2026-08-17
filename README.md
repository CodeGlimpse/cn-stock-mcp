# cn-stock-mcp

中国证券市场行情 MCP 服务。核心交付物是 **通用 MCP server**；OpenClaw skill 只是仓库内附带的平台适配层。

> **如果你是人类用户：** 不要先通读整个仓库，先看 `docs/START_HERE.md`。

> **Windows + AI 自部署：** 先看 `docs/AI_DEPLOY_WINDOWS.md`；它是固定版本、token 脱敏和首次问答验收的执行合同。

> **如果你要把这个 MCP 教给 AI / 集成到 agent：** 先看 `docs/AI_ONBOARDING.md`。

> **如果你在找“给各个 agent 用的 skill 在哪里”：** 先看 `docs/AGENT_AND_SKILL_MAP.md`。

> **如果你是 AI agent：** 不要默认通读本 README。先读 `docs/AGENT_MINIMAL.md`，需要最小示例时再读 `docs/EXAMPLES_MINIMAL.md`。

## 最短开始路径

### 人类用户 / 接收方
- `docs/START_HERE.md`：最友好的仓库入口
- `docs/HANDOFF_MINIMAL.md`：一页安装与接入
- `docs/HOST_CONFIG_TEMPLATES.md`：不同 host 的模板入口
- `docs/AI_ONBOARDING.md`：给 AI 集成人员 / agent 作者的使用说明
- `docs/AGENT_AND_SKILL_MAP.md`：各 agent / host 用什么、有没有 skill、skill 在哪里
- `docs/FAQ.md`：常见错误与排查

### 最终用户 / 本地 AI agent
- `docs/HANDOFF_MINIMAL.md`：一页安装与接入
- `docs/HOST_CONFIG_TEMPLATES.md`：不同 host 的模板入口
- `docs/OPENCLAW_HOST_TEMPLATE.md`：OpenClaw 单独最终配置块
- `docs/CLAUDE_DESKTOP_TEMPLATE.md`：Claude Desktop 单独模板
- `docs/CLAUDE_CODE_TEMPLATE.md`：Claude Code 单独模板
- `docs/CONTINUE_TEMPLATE.md`：Continue 单独模板
- `docs/VSCODE_TEMPLATE.md`：VS Code 单独模板
- `docs/CURSOR_TEMPLATE.md`：Cursor 单独模板
- `docs/CLINE_TEMPLATE.md`：Cline 单独模板
- `docs/WINDSURF_TEMPLATE.md`：Windsurf 单独模板
- `docs/HERMES_TEMPLATE.md`：Hermes 单独模板
- `docs/CODEX_TEMPLATE.md`：Codex 单独模板
- `docs/FAQ.md`：常见错误与排查

### AI agent / AI 集成人员
- `docs/AI_ONBOARDING.md`：人类可读的 AI 集成说明
- `docs/AGENT_MINIMAL.md`：最小规则与路由入口
- `docs/EXAMPLES_MINIMAL.md`：最小可工作示例
- `docs/INTERFACE_SCHEMA.md`：需要详细契约时再看

### 集成 / 联调 / 维护
- `docs/INTEGRATION.md`：完整挂载、自检与联调清单
- `docs/COMPATIBILITY.md`：MCP-only / rules-based / skill-based host 兼容说明
- `docs/HOST_CONFIG_TEMPLATES.md`：已核实宿主模板总入口
- `docs/IMPLEMENTATION_STATUS.md`：当前实现状态与限制
- `docs/OPENCLAW_INTEGRATION.md`：OpenClaw 专属适配说明

## 快速开始

### 安装

```bash
python -m pip install cn-stock-mcp==0.2.0
```

### 本地自检

```bash
cn-stock-mcp --version
cn-stock-mcp --doctor
cn-stock-mcp --doctor-network
```

### 最小 MCP 配置

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

更多模板见：
- `.mcp.sample.json`
- `docs/HOST_CONFIG_TEMPLATES.md`
- `docs/OPENCLAW_HOST_TEMPLATE.md`
- `docs/CLAUDE_DESKTOP_TEMPLATE.md`
- `docs/CLAUDE_CODE_TEMPLATE.md`
- `docs/CONTINUE_TEMPLATE.md`
- `docs/VSCODE_TEMPLATE.md`
- `docs/CURSOR_TEMPLATE.md`
- `docs/CLINE_TEMPLATE.md`
- `docs/WINDSURF_TEMPLATE.md`
- `docs/HERMES_TEMPLATE.md`
- `docs/CODEX_TEMPLATE.md`

## 当前状态

当前已具备：
- MCP Python SDK（FastMCP）stdio transport
- AKShare / 智兔双源与 fallback
- 核心市场数据 / 复盘 / 板块 / 技术指标 / 股池能力
- 打包构建、非 live 回归、provider_health 自检

详细能力与限制见：`docs/IMPLEMENTATION_STATUS.md`

## 文档导航

- `docs/START_HERE.md`：给人类用户的最友好入口
- `docs/AI_ONBOARDING.md`：给 AI 集成人员 / agent 作者的说明
- `docs/AGENT_AND_SKILL_MAP.md`：各 agent / host 的使用方式与 skill 对照
- `docs/README_DOCS.md`：文档总览与阅读顺序
- `docs/HANDOFF_MINIMAL.md`：给最终用户 / 本地 AI agent 的一页接入说明
- `docs/HOST_CONFIG_TEMPLATES.md`：不同 host 的模板入口
- `docs/OPENCLAW_HOST_TEMPLATE.md`：OpenClaw 单独最终配置块
- `docs/CLAUDE_DESKTOP_TEMPLATE.md`：Claude Desktop 单独模板
- `docs/CLAUDE_CODE_TEMPLATE.md`：Claude Code 单独模板
- `docs/CONTINUE_TEMPLATE.md`：Continue 单独模板
- `docs/VSCODE_TEMPLATE.md`：VS Code 单独模板
- `docs/CURSOR_TEMPLATE.md`：Cursor 单独模板
- `docs/CLINE_TEMPLATE.md`：Cline 单独模板
- `docs/WINDSURF_TEMPLATE.md`：Windsurf 单独模板
- `docs/HERMES_TEMPLATE.md`：Hermes 单独模板
- `docs/CODEX_TEMPLATE.md`：Codex 单独模板
- `docs/FAQ.md`：常见错误与排查
- `docs/AI_DEPLOY_WINDOWS.md`：交给 Windows AI agent 的自部署与验收流程
- `docs/SECURITY.md`、`docs/PRIVACY.md`、`docs/DATA_SOURCES.md`：安全、隐私和数据来源边界
- `docs/COMPATIBILITY.md`：MCP-only / rules-based / skill-based host 兼容说明
- `docs/AGENT_MINIMAL.md`：给 AI agent 的最小入口
- `docs/EXAMPLES_MINIMAL.md`：最小可工作的调用示例
- `docs/EXAMPLES_FULL.md`：完整调用样例（按需展开）
- `docs/IMPLEMENTATION_STATUS.md`：当前实现状态与限制（事实源）
- `docs/INTERFACE_SCHEMA.md`：对外输入/输出契约与路由约束
- `docs/ERROR_MODEL.md`：统一错误码与 retry/fallback 语义
- `docs/INTEGRATION.md`：通用 MCP 挂载、自检与联调清单
- `docs/OPENCLAW_INTEGRATION.md`：OpenClaw 专属适配说明

## OpenClaw adapter

仓库内附带 OpenClaw skill adapter：
- `skills/newsbot-stock-routing/`

OpenClaw 专属加载与验证说明见：
- `docs/OPENCLAW_INTEGRATION.md`
- `skills/MIGRATION_NEWSBOT_SKILL.md`
