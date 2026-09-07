# Windows 最短接入流程

目标为 `cn-stock-mcp==0.2.3`（发布准备），本机 stdio、普通 CPython 3.13、retail 10 工具。公开发布和校验文件就绪后才能按发布地址安装。

## 1. 安装与本地配置

按 [Windows 部署说明](AI_DEPLOY_WINDOWS.md) 安装固定 wheel 并核对 SHA256、依赖约束。由客户本人运行 `--init-config` 并在其配置文件中填写 Token。

## 2. 取得本机路径

按 [Windows 共同准备](WINDOWS_AGENT_SETUP.md) 取得程序、配置文件路径并备份所选 Host 配置。Token 留在 MCP 配置文件；Host 只记录路径和运行选项。

## 3. 选择软件并合并配置

打开 [13 款软件配置总表](HOST_CONFIG_TEMPLATES.md)，按自己的客户端专页填写配置、重载与查看工具。包含 Codex、Claude Code、Claude Desktop、Cursor、VS Code/GitHub Copilot、Cline、Windsurf、Continue、OpenClaw、Hermes、OpenCode、Gemini CLI、Cherry Studio。

本轮交付是配置文档及离线核对，按用户决定不执行真实测试。客户需要进一步查询时，先查看 [retail 样本计划](RETAIL_ACCEPTANCE.md)，再决定是否执行。

配置与运行故障见 [共同排错](WINDOWS_AGENT_SETUP.md#5-常见问题) 和 [FAQ](FAQ.md)。首发交付及售后范围以 [交付约定](COMMERCIAL_DELIVERY_TEMPLATE.md) 为准。
