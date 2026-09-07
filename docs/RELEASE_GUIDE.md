# Release Guide

## 发布不变量

- `pyproject.toml` 是唯一版本源；源码、MCP server、doctor、tag 和制品必须报告相同版本。
- 最终提交创建新的不可变 tag；公开后不移动 tag，不重建或覆盖同版本文件。
- Release 包含 wheel、sdist、Windows 运行时约束、SHA256 清单和 Windows 运行时 SBOM；wheel/sdist 的构建证明通过 GitHub Artifact Attestations 查询。
- wheel 必须携带部署文档、Skill、四个验证工具和第三方许可证附件，`--docs-path` 可定位文档及相邻目录。
- 不发布 Token、真实 .env、用户配置、诊断包或含凭据的 Host 配置。
- Windows CPython 3.13 使用完整运行时约束；其他平台不能据此声称相同依赖解析。

## 本地准备

1. 检查 Git 状态和实际 diff，保留所有无关改动。新版本更新 pyproject、当前部署文档、变更记录与 release note；不改写历史发布证据。
2. 在没有真实 .env、配置或 Token 环境变量的隔离目录运行受影响测试，再完成非 live 回归。测试不使用客户凭据。
3. 用新输出目录构建 wheel/sdist，保留旧制品。检查文档、tools、Skill、许可证及文件内容；校验版本和无秘密文件。
4. 隔离安装最终 wheel，执行 pip check、依赖闭包检查、doctor、retail 10 工具和 MCP stdio。依赖复用安装只证明本机隔离安装；干净机器依赖下载由 Windows gate 和客户标准用户验收补足。
5. 核对软件许可、第三方原文及服务口径。经营者已决定本轮不执行真实行情和实际 AI Host 验收，相关状态明确记录为未执行；客户交付后的验收按订单独立进行。私人授权文件由经营者自行保管。
6. 完成审核和本地提交；获准后才推送提交、创建/推送新 tag 并发布。不得因本地验证通过而自动推送。

## 标签工作流

`build-and-audit` 在 Linux 校验版本、非 live 测试、许可证附件与依赖审计，只构建一次 wheel/sdist。此阶段的 SBOM 仅描述构建环境，用于过渡制品校验；保存名为 `release-build-<commit-sha>` 的 artifact，保留 90 天。

`windows-wheel-smoke` 下载这份构建制品，验证 SHA256、审计 Windows 约束，在新 venv 安装原 wheel，执行 pip check、依赖闭包、许可证附件、空配置 doctor、文档/tools 与离线 stdio 检查。随后由独立审计环境针对该 Windows venv 生成最终 `sbom.json`，重新生成完整校验清单，并确认 wheel、sdist、约束文件字节未变。最终文件保存为 `release-<commit-sha>`；不会重建安装包，也不访问真实行情或真实客户配置。

`publish` 只下载 Windows 确认后的 `release-<commit-sha>`。先比较 PyPI/GitHub 同版本哈希，再生成构建证明。两份分发包复制到独立 `pypi-upload` 目录并验证字节一致，交给 PyPI Trusted Publishing；GitHub 附件始终取规范 `dist` 和最终清单。只补传缺少附件，不覆盖既有文件。最后核对两平台完整文件集与哈希，保存验证报告。

只有目标版本的 wheel 和 sdist 可存在于 dist。校验清单必须覆盖两份包、Windows 约束和 SBOM。元数据 API 的认证错误、限流、网络故障不能当成“尚未发布”。

## 中断与恢复

- 发布阶段失败时，检查失败原因并重跑失败作业，复用同一份 artifact。PyPI 已存在文件只有在哈希完全相同时才能跳过。
- GitHub 已存在附件只核对，不覆盖；缺少附件才上传。
- 不要对已有 artifact 的同次运行直接重跑构建并覆盖。重新构建可能改变压缩包时间戳、SBOM 或哈希，脚本会拒绝与已发布字节冲突。
- 若原 artifact 已丢失，先寻找原始制品和校验依据；不能确认原始字节时应发布新版本。不得移动旧 tag、删除旧包或使用 clobber。
- 发布后检查 wheel/sdist 在 PyPI 与 GitHub 的 SHA256、约束、SBOM、来源证明，并完成公开下载的标准用户安装。
- Actions 成功不自动证明数据许可或某个 Codex 客户端的实际运行。

## 历史证据

- v0.2.0 发布切点：`1651a510b03edd49852e04139b3ce98ed1a244fc`。
- [v0.2.0 Windows 验收](WINDOWS_ACCEPTANCE_v0.2.0.md)。
- [v0.2.0 公开安装补充验收](WINDOWS_ACCEPTANCE_POST_RELEASE_2026-08-20.md)。

历史记录只证明对应版本，不能替代新版本验证。
