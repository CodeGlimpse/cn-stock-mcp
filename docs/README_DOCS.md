# Docs Guide (`openclaw-stock-mcp`)

Last Updated: 2026-05-06

本目录只保留当前有效的运行文档。阅读顺序：

1. `IMPLEMENTATION_STATUS.md`
   - 看当前已经实现了什么、验证到什么程度、有哪些限制。

2. `INTERFACE_SCHEMA.md`
   - 看 tool 的输入输出契约、枚举、symbol/interval 约束、provider 路由规则。

3. `ERROR_MODEL.md`
   - 看统一错误模型、错误码语义、retry/fallback 建议。

4. `INTEGRATION.md`
   - 看如何本地启动 stdio、如何挂载到 OpenClaw、如何联调与验收。

---

## 文档定位约定（避免重复/过时）

- 功能事实：只在 `IMPLEMENTATION_STATUS.md` 维护。
- 协议契约：只在 `INTERFACE_SCHEMA.md` 维护。
- 错误语义：只在 `ERROR_MODEL.md` 维护。
- 部署联调：只在 `INTEGRATION.md` 维护。

如果某条信息出现在多个文件，以以上“单一事实源”优先。
