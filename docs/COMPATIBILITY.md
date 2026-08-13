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

## 5) Windows Python 运行时兼容性

当前已验证的 Windows 开发环境是：

- 普通 CPython 3.13.2（GIL enabled，`cp313-win_amd64`）
- 项目虚拟环境：`.venv`
- `mcp 2.0.0` 与 `pywin32 312`

Python 3.13t（free-threaded）目前不作为本项目 Windows/MCP 的支持开发环境。MCP 的 Windows stdio 实现依赖 `pywin32`，而当前可用的 `pywin32` 发布物没有 `cp313t` wheel；强行跳过依赖、改 wheel 标签或复制 DLL 都不能证明兼容性。

Windows 下请明确选择普通解释器：

```powershell
py -3.13 -m venv .venv
& .\.venv\Scripts\python.exe -m pip check
& .\.venv\Scripts\cn-stock-mcp.exe --doctor
```

如果机器同时安装了 3.13t，不要使用不带版本号的 `py` 或 `py -3`，因为 Windows Python Launcher 会优先选择 free-threaded 构建；使用 `py -3.13` 或项目 `.venv` 的解释器。
