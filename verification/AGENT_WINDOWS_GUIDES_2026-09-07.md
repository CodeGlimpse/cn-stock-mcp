# 13 款 Windows Agent 配置指南交付记录

日期：2026-09-07。目标版本：0.2.3（发布准备）。变更前检查点：`0622eda`。

## 已确认的任务范围

用户要求补全主流 Agent 软件的配置方法，只写 Windows，不进行真实测试。最终名单为 Codex、Claude Code、Claude Desktop、Cursor、VS Code/GitHub Copilot、Cline、Windsurf/Cascade、Continue、OpenClaw、Hermes Agent、OpenCode、Gemini CLI、Cherry Studio。

Roo Code 官方首页出现扩展关闭公告后，已询问用户并获确认，以 Cherry Studio 替换，仍保持 13 款。没有继续前一阶段的 Token 路径确认、真实 MCP 连接或行情验收。

## 交付内容

- 13 份 Windows 专页：配置入口、用户/项目作用域、可复制配置或 UI 字段表、重载、自查、停用与恢复步骤。
- `docs/WINDOWS_AGENT_SETUP.md`：安装前置、实际路径、Token 保管、备份、配置格式和共同排错。
- `docs/HOST_CONFIG_TEMPLATES.md`：13 款软件总表。
- `docs/HOST_CONFIGURATION_SOURCES.md`：官方来源、核对日期、格式差异及站点变更。
- 同步 README、文档导航、部署提示词、OpenClaw 可选 Skill 说明、发布准备说明与状态文件。
- 原有正式售后和订单条款保留其范围；文档覆盖数量不作为客户端实测或新增商业支持承诺。

## 资料核对

实际读取官方页面正文，未以搜索摘要替代。各指南共引用 25 条官方来源，所有引用均能对应到本轮已取得的正文；Markdown 正文地址与同站点页面地址归一化后核对。

已记录 Windsurf 官方入口重定向到 Devin Desktop、Cherry Studio 文档迁移及新版 Agent 绑定方式。OpenClaw 和 OpenCode 明确区分 Windows 原生后端与 WSL/远程后端；本轮不提供其他操作系统的安装步骤。

资料和临时检查脚本保存在 `F:\agents\code\temp\cn-stock-agent-docs-20260907`。其中 initial、followup、final-sources、cherry 各目录的 manifest.json 记录请求地址、最终地址、读取时间、HTTP 结果和正文 SHA256。未把完整外部页面复制进产品文档。

## 验证结果

| 检查 | 结果 |
| --- | --- |
| 修改的 Markdown 文件 | 31 份（不含本记录） |
| JSON / YAML / TOML | 14 / 2 / 1 个代码块解析通过，并检查重复键 |
| PowerShell 示例 | 25 段通过 PowerShell Parser 语法检查；没有执行示例命令 |
| 本地文件链接 | 187 个引用目标存在 |
| Host 配置结构 | 13 款核对完成，包括专属顶层键、命令形式、Windows 绝对路径、stdio 参数、非秘密环境字段及支持的工具白名单 |
| 官方来源引用 | 25 条均对应本轮取得的官方正文 |
| Git 差异 | `git diff --check` 通过 |
| wheel / sdist | 使用现有构建依赖、`python -m build --no-isolation` 构建成功 |
| 打包内容 | 两种制品均包含 54 份文档，与仓库逐字节一致；13 份指南、共同准备、索引和来源页齐全 |
| 程序内容 | wheel 内 172 个 Python 源文件与当前源码一致；本轮没有改动程序或依赖声明 |
| 排除文件 | 按文件名/路径规则确认制品没有真实配置、Git、虚拟环境、测试缓存或 verification 记录目录 |
| 实际安装 / Host 连接 / 行情 | NOT_RUN_USER_REQUEST |

配置语法和文档内容检查不证明某个客户端版本已成功运行；本轮没有作此结论。此前的安装、依赖和协议记录保留为对应旧候选包的历史证据。

## 关键检查命令与输出

使用项目 `.venv\Scripts\python.exe -X utf8 -B` 执行临时目录下的 `check_guides.py`，输出 `documentation-check.json` 与 `powershell-snippets.json`。PowerShell 只调用 `System.Management.Automation.Language.Parser.ParseInput` 检查这些片段。

以 `-m build --no-isolation --outdir F:\agents\code\temp\cn-stock-agent-docs-20260907\release\dist F:\agents\code\cn-stock-mcp` 构建，并执行 `inspect_documentation_candidate.py`，输出 `package-check.json` 和 `release/package-sha256sums.txt`。

## 文档候选包

目录：`F:\agents\code\temp\cn-stock-agent-docs-20260907\release\dist`。

| 文件 | 字节数 | SHA256 |
| --- | ---: | --- |
| cn_stock_mcp-0.2.3-py3-none-any.whl | 459908 | e4d55b626e998b88748de8b829f446668bfabdbc22d2de8f60640e673ac14f2b |
| cn_stock_mcp-0.2.3.tar.gz | 333372 | 6aa16aaeb478978cec5faafbc6d968d52abc7e54c0f9b4d11b40bf5df568b4ea |

本轮使用新的输出目录，前一阶段的候选制品和证据仍保留在原目录。这里的 package-sha256sums.txt 只覆盖上述两个文档候选包，不是正式发布所需的完整 Release 清单；没有生成发布 tag、推送或公开发布 0.2.3。
