# 客户复制给本地 AI Agent 的部署提示词

适用版本：`cn-stock-mcp==0.2.2`

将下面整个代码块复制给具备本机文件和 PowerShell 执行权限的 AI Agent。普通网页聊天机器人如果无法操作客户电脑，必须停止并说明，不能假装部署成功。

```text
请在我的 Windows 电脑上部署 cn-stock-mcp==0.2.2，并接入我当前使用的 MCP Host。

执行前先确认你具备本机 PowerShell、文件读写和 Host 配置权限。读取固定标签文档：
https://raw.githubusercontent.com/CodeGlimpse/cn-stock-mcp/v0.2.2/docs/AI_DEPLOY_WINDOWS.md

严格按该文档操作，并遵守以下边界：
1. 只安装 PyPI 的固定版本 0.2.2；先下载 wheel 和同版本 `constraints-windows-py313.txt`，再用同版本 GitHub Release 的 `sha256sums.txt` 分别核验 SHA256，并使用约束文件安装。不要安装 GitHub main、其他分支或未固定版本。
2. 系统安装、联网下载、修改 Host 配置前，先向我说明目标、命令和影响；修改 Host 配置前创建带时间戳备份，保留其他 MCP server，失败时恢复备份。
3. 运行 --init-config 后，只告诉我配置文件绝对路径，并暂停让我本人填写智兔 Token。你不得读取、索取、复制、回显、截图、上传或写入 Token，也不得把 Token 放入聊天、命令行、环境变量或 Host 配置。
4. 如果我还没有 Token，指导我本人打开智兔官方页面申请；登录、验证码、付款/套餐选择和 Token 复制必须由我完成：
   https://zhituapi.com/gettoken.html
   https://www.zhituapi.com/access.html
   https://zhituapi.com/termsofservice.html
5. 我确认已保存 Token 后，重启或重载 MCP Host，再运行脱敏状态检查。不要读取配置文件内容，只运行 --doctor、--doctor-network、--list-tools 和 MCP 协议验收。
6. 验收版本必须为 0.2.2；默认 retail_v1_preview 必须正好显示 10 个工具；验证 MCP initialize、tools/list，并用 stock_quote 完成一次问答。
7. 首次问答必须说明 symbol、数据来源、数据时间或 unknown、交易时段、fallback/partial failure 和 data_quality；不得给出投资参考、投资建议、风险建议、买卖指令或收益承诺。
8. 最终只报告安装位置、版本、Host 配置备份位置、配置文件路径、10 个工具名称、doctor/协议验收结果和仍需我处理的问题；报告中不得包含 Token、Token 尾号、完整带凭据 URL、配置文件内容或个人目录以外的无关信息。
9. 任一步骤缺少权限、固定 Release/校验文件不存在、哈希不匹配、上游失败或 Host 类型无法确认时，停止并准确说明，不要绕过安全检查。
```

这段提示词不能赋予云端 Agent 本机权限，也不能代替客户本人同意系统安装或 Host 配置修改。卖方不接收、不保存、不代填智兔 Token。
