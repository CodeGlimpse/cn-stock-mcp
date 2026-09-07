# cn-stock-mcp v0.2.3

## 交付与验收

- 补全 13 款 Agent 的 Windows 配置指南，新增 OpenCode、Gemini CLI 和 Cherry Studio；统一路径、配置作用域、自查与恢复步骤，并归档官方来源。本轮按用户决定不执行真实测试。

- 首发交付范围明确为 Windows 11 x64、普通 CPython 3.13、Codex 和 retail 10 工具，其他 Host 保留配置参考。
- wheel 携带 stdio、运行时依赖和 retail 验收脚本；真实验收默认只展示计划，需明确启用后才调用上游。
- 验收报告区分 PASS、PARTIAL、FAIL、BLOCKED，保存允许的来源、时间、耗时和错误类别，失败停止，不保存 Token 或原始行情。
- 补充真实 Codex 验收记录、7 天支持与平台退款条款，以及数据权限证据登记。
- 修复 Windows 部署示例中依赖约束校验命令的 PowerShell 语法。

## 发布完整性

- 补齐 cffi 运行时 pin，显式声明 packaging 依赖，确保新环境可以检查完整依赖闭包、extras、版本和约束兼容性。
- 发布只构建一次，Windows gate 安装同一制品，上传前后核对 PyPI/GitHub 哈希。
- 已发布的同名文件必须与原始字节一致；GitHub 只补传缺少的附件，不覆盖同版本文件。
- 增加真实 stdio 固定样本成功响应测试，验证文本与结构化响应一致。

## 验证边界

本版本的离线测试和 CI 不代表实时数据可用、所有 Codex 版本兼容或第三方数据已授权。实际发布状态与验证证据以标签工作流、公开文件哈希、[首发清单](SALE_READINESS.md) 和单独验收记录为准。
