# Agent 配置：官方来源与核对范围

核对日期：2026-09-07。对象为 13 款软件的 Windows 本地 stdio 配置。通过读取官方页面正文核对配置结构、路径、命令及操作步骤；界面名称和软件能力可能随版本变化。

验证级别是官方资料核对与离线配置检查。本轮没有安装这些 Agent、修改用户实际 Host 配置、连接 MCP 或调用行情。实际客户端版本和连接结果应由客户使用时记录，不能把配置片段当作运行证明。

## 来源与关键差异

### Codex

同一 Codex Host 的本地客户端共享配置；支持用户/受信任项目作用域、cwd、超时和工具过滤。

- [官方资料 1](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)

### Claude Code

明确 user、project、local 作用域，以及 stdio 添加、列表和移除命令。

- [官方资料 1](https://code.claude.com/docs/en/mcp)

### Claude Desktop

Developer → Edit Config、Windows 文件位置、完整退出重启与日志入口。

- [官方资料 1](https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers)

### Cursor

用户/项目 mcp.json、command / args / env，以及新版 Customize 管理入口。

- [官方资料 1](https://cursor.com/docs/mcp)

### VS Code / GitHub Copilot

servers 顶层、用户 Profile 与工作区文件、cwd、工具选择和 Agent Host 转发行为。

- [官方资料 1](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
- [官方资料 2](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)

### Cline

IDE 配置入口与 CLI 文件分别说明；disabled、autoApprove 与管理向导。

- [官方资料 1](https://docs.cline.bot/mcp/mcp-overview)
- [官方资料 2](https://docs.cline.bot/getting-started/config)

### Windsurf / Cascade

官方旧地址重定向至 Devin Desktop；当前页面仍明确使用 .codeium/windsurf/mcp_config.json。

- [官方资料 1](https://docs.windsurf.com/windsurf/cascade/mcp)
- [官方资料 2](https://docs.devin.ai/desktop/cascade/mcp)

### Continue

独立 YAML 元数据、JSON 文件导入、mcpServers 目录和 Agent 模式要求。

- [官方资料 1](https://docs.continue.dev/customize/deep-dives/mcp)
- [官方资料 2](https://docs.continue.dev/reference)

### OpenClaw

Windows 原生 Gateway 与 Hub/WSL 区别；mcp.servers、--no-probe、status、doctor 和 unset。

- [官方资料 1](https://docs.openclaw.ai/tools/mcp)
- [官方资料 2](https://docs.openclaw.ai/cli/mcp)
- [官方资料 3](https://docs.openclaw.ai/platforms/windows)
- [官方资料 4](https://docs.openclaw.ai/gateway/configuration)

### Hermes Agent

官方提供原生 Windows 安装；config.yaml / mcp_servers、tools.include 与 /reload-mcp。

- [官方资料 1](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp/)
- [官方资料 2](https://hermes-agent.nousresearch.com/docs/getting-started/installation)

### OpenCode

local 类型、命令数组、environment、工具发现 timeout，以及用户/项目配置层。

- [官方资料 1](https://opencode.ai/docs/mcp-servers/)
- [官方资料 2](https://opencode.ai/docs/config/)
- [官方资料 3](https://opencode.ai/docs/windows-wsl/)

### Gemini CLI

用户/项目 settings.json，CLI 默认 project；timeout 单位、trust 和工具过滤。

- [官方资料 1](https://geminicli.com/docs/tools/mcp-server/)

### Cherry Studio

新版设置入口、手动创建字段、查看工具，以及工作区 Agent 的 MCP 绑定。

- [官方资料 1](https://docs.cherryai.com.cn/advanced-basic/extensions/mcp)
- [官方资料 2](https://docs.cherryai.com.cn/advanced-basic/extensions/mcp/troubleshooting)
- [官方资料 3](https://docs.cherryai.com.cn/cherry-studio/installation/windows)

## 名单与地址变化

- 经用户确认，以 Cherry Studio 替换 Roo Code，保持 13 款。读取的 [Roo Code 官方首页](https://roocodeinc.github.io/Roo-Code/) 有“Extension Shutdown”公告，称扩展已于 5 月 15 日关闭；未继续将其作为现行推荐软件。
- Windsurf 官方旧地址本次重定向到 `docs.devin.ai/desktop/cascade/mcp`，专页保留名称与路径差异说明。
- Cherry Studio 官方索引本次从 `docs.cherry-ai.com` 重定向到 `docs.cherryai.com.cn`，使用新版“工作 / Agent”绑定步骤。
- 部分站点没有可用的 llms.txt 或旧配置页；已改用实际取得的官方正文，不用搜索摘要代替依据。
- 未读取本机 Token 文件、真实 Host 设置或账户资料。原始公开资料与取得时间/哈希保存在本轮临时证据目录，验证结果另存于仓库的 verification 记录。

## 模板约定

服务器命名为 `cn_stock_mcp`，使用客户 Windows 程序绝对路径和 `--stdio`。示例的环境字段仅放配置文件路径、`retail_v1_preview` 与 UTF-8 选项。支持额外白名单的 Host 采用同一 retail 10 工具集合。

配置语法检查只能验证 JSON / YAML / TOML、PowerShell 示例及文档引用；Host 加载、账户策略、实际网络和上游数据仍属于不同验证层。
