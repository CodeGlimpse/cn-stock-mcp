# Docs Guide (`openclaw-stock-mcp`)

Last Updated: 2026-05-06

本目录只保留当前有效的运行文档。**给 AI agent 的最短阅读顺序：**

1. `HANDOFF_MINIMAL.md`
   - 给最终用户 / 本地 AI agent 的最短接入说明。

2. `AGENT_MINIMAL.md`
   - 先看最小路由、最小 payload、最容易踩坑的契约。

3. `EXAMPLES_MINIMAL.md`
   - 只看最小可工作的调用示例，不必先读 README 长样例。

4. `INTEGRATION.md`
   - 看如何本地启动 stdio、如何挂载到 OpenClaw、如何联调与验收。

5. `INTERFACE_SCHEMA.md`
   - 需要详细输入输出契约、枚举、symbol/interval 约束时再看。

6. `IMPLEMENTATION_STATUS.md`
   - 需要确认当前实现状态、验证范围、限制时再看。

7. `ERROR_MODEL.md`
   - 需要统一错误码、retry/fallback 语义时再看。

---

## 文档定位约定（避免重复/过时）

- 功能事实：只在 `IMPLEMENTATION_STATUS.md` 维护。
- 协议契约：只在 `INTERFACE_SCHEMA.md` 维护。
- 错误语义：只在 `ERROR_MODEL.md` 维护。
- 部署联调：只在 `INTEGRATION.md` 维护。

如果某条信息出现在多个文件，以以上“单一事实源”优先。
