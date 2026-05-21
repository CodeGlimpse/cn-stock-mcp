# cn-stock-mcp

中国证券市场行情 MCP 服务。核心交付物是 **通用 MCP server**；OpenClaw skill 只是仓库内附带的平台适配层。

> **给最终用户：** 不要先通读整个仓库。优先按下面顺序阅读：
> 1. `docs/HANDOFF_MINIMAL.md`
> 2. `docs/HOST_CONFIG_TEMPLATES.md`
> 3. `docs/FAQ.md`

> **给 AI agent：** 不要默认通读本 README。先读 `docs/AGENT_MINIMAL.md`，需要最小示例时再读 `docs/EXAMPLES_MINIMAL.md`。

## 最短开始路径

### 最终用户 / 本地 AI agent
- `docs/HANDOFF_MINIMAL.md`：一页安装与接入
- `docs/HOST_CONFIG_TEMPLATES.md`：不同 host 的复制即用模板
- `docs/FAQ.md`：常见错误与排查

### AI agent
- `docs/AGENT_MINIMAL.md`：最小规则与路由入口
- `docs/EXAMPLES_MINIMAL.md`：最小可工作示例
- `docs/INTERFACE_SCHEMA.md`：需要详细契约时再看

### 集成 / 联调 / 维护
- `docs/INTEGRATION.md`：完整挂载、自检与联调清单
- `docs/COMPATIBILITY.md`：MCP-only / rules-based / skill-based host 兼容说明
- `docs/IMPLEMENTATION_STATUS.md`：当前实现状态与限制
- `docs/OPENCLAW_INTEGRATION.md`：OpenClaw 专属适配说明

## 快速开始

### 安装

```bash
python -m pip install cn-stock-mcp
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
      "args": ["--stdio"],
      "env": {
        "ZHITU_TOKEN": "replace-with-your-token"
      }
    }
  }
}
```

更多模板见：
- `.mcp.sample.json`
- `docs/HOST_CONFIG_TEMPLATES.md`

## 当前状态

当前已具备：
- MCP Python SDK（FastMCP）stdio transport
- AKShare / 智兔双源与 fallback
- 核心市场数据 / 复盘 / 板块 / 技术指标 / 股池能力
- 打包构建、非 live 回归、provider_health 自检

详细能力与限制见：`docs/IMPLEMENTATION_STATUS.md`

## 文档导航

- `docs/README_DOCS.md`：文档总览与阅读顺序
- `docs/HANDOFF_MINIMAL.md`：给最终用户 / 本地 AI agent 的一页接入说明
- `docs/HOST_CONFIG_TEMPLATES.md`：不同 host 的复制即用模板
- `docs/FAQ.md`：常见错误与排查
- `docs/COMPATIBILITY.md`：MCP-only / rules-based / skill-based host 兼容说明
- `docs/AGENT_MINIMAL.md`：给 AI agent 的最小入口
- `docs/EXAMPLES_MINIMAL.md`：最小可工作的调用示例
- `docs/EXAMPLES_FULL.md`：完整调用样例（按需展开）
- `docs/IMPLEMENTATION_STATUS.md`：当前实现状态与限制（事实源）
- `docs/INTERFACE_SCHEMA.md`：对外输入/输出契约与路由约束
- `docs/ERROR_MODEL.md`：统一错误码与 retry/fallback 语义
- `docs/INTEGRATION.md`：通用 MCP 挂载、自检与联调清单
- `docs/OPENCLAW_INTEGRATION.md`：OpenClaw 专属适配说明

## 开发与验证

本地源码开发时：

```bash
python -m pip install -e .
.venv/bin/python -m pytest -q -m "not live"
bash scripts/smoke_live.sh
```

调试命令：

```bash
cn-stock-mcp --list-tools
cn-stock-mcp --tool provider_health --payload '{}'
```

## OpenClaw adapter

仓库内附带 OpenClaw skill adapter：
- `skills/newsbot-stock-routing/`

OpenClaw 专属加载与验证说明见：
- `docs/OPENCLAW_INTEGRATION.md`
- `skills/MIGRATION_NEWSBOT_SKILL.md`
