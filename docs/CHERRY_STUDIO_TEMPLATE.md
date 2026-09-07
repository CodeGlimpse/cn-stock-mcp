# Cherry Studio：Windows 配置指南

目标版本：`cn-stock-mcp==0.2.3`（发布准备）。官方资料核对日期：2026-09-07。本页提供配置方法，本轮未进行 Host 连接或行情实测。

先完成 [Windows 共同准备](WINDOWS_AGENT_SETUP.md)，取得实际程序和配置路径。将示例中的 `YOUR_NAME` 及路径替换为本机值；按共同准备说明备份、合并配置。MCP 使用独立的普通 CPython 3.13 环境。

官方资料明确提供手动创建和从 JSON 导入入口；本页采用手动字段表，避免依赖不同版本的导入包装格式。

## 1. 配置入口与作用范围

在 Windows 客户端打开 `设置 → MCP → MCP 服务器 → 添加`，选择手动创建的本地命令/stdio 服务器。服务器由应用设置管理；本页不要求编辑其内部数据库文件。

按以下字段逐项填写。命令输入框只填程序路径；`--stdio` 填入参数栏。环境变量按键值添加；若界面采用多行文本，每行填一组 `KEY=VALUE`。

## 2. 可复制配置

```text
名称: cn_stock_mcp
连接类型: stdio（本地命令）
命令: C:\Users\YOUR_NAME\AppData\Local\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe
参数（单独一个参数）: --stdio

环境变量（按键值逐项填写）:
CN_STOCK_MCP_CONFIG=C:\Users\YOUR_NAME\AppData\Local\cn-stock-mcp\config.json
TOOL_PROFILE=retail_v1_preview
PYTHONUTF8=1
```



## 3. 使配置生效与查看工具

先在服务器设置中启用 `cn_stock_mcp`，等待连接状态并查看工具。随后打开 `工作 → 目标 Agent 菜单 → 编辑 → MCP`，给该 Agent 启用本服务器。修改后新发一条消息，让会话加载工具配置；使用支持工具调用的模型。

查看本服务器的工具列表，默认应包含 [共同准备中列出的 10 个工具](WINDOWS_AGENT_SETUP.md#4-查看工具与客户自查)。连接、发现工具与取得真实行情分别记录；本页没有预先认定任何客户端已实测通过。

## 4. 常见问题

- 设置中已连接、Agent 仍没有工具：检查该 Agent 的 MCP 绑定和工具开关；服务器不会自动绑定给所有 Agent。
- 将参数拼在命令框：分开填写程序路径和 `--stdio`。
- 找不到 MCP 提示词/资源：本项目主要提供工具；连接成功并不要求一定出现提示词或资源标签内容。
- 界面与旧教程不同：本次依据新版官方的“工作 / Agent”文档；旧版从当前助手的 MCP 开关选择服务器。

通用的路径、JSON 转义、Token 文件和多环境问题见 [Windows 共同准备](WINDOWS_AGENT_SETUP.md#5-常见问题)。

## 5. 停用与恢复

先在目标 Agent 的 MCP 设置中解除绑定，再在 `设置 → MCP` 停用服务器。移除前保存本服务器的无秘密配置字段；需要恢复时重新按表填写并绑定 Agent。

## 官方依据

- [Cherry Studio：MCP 与外部工具](https://docs.cherryai.com.cn/advanced-basic/extensions/mcp)
- [Cherry Studio：MCP 排错](https://docs.cherryai.com.cn/advanced-basic/extensions/mcp/troubleshooting)
- [Cherry Studio：Windows 安装](https://docs.cherryai.com.cn/cherry-studio/installation/windows)
