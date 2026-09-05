# Release Guide

## Release invariants

- `pyproject.toml` 是唯一版本源；源码、MCP server、doctor、tag 和制品必须报告同一版本。
- 发布切点的 `main`、版本 tag、PyPI 文件和 GitHub Release 必须来自同一提交；发布后不得移动已公开 tag 或重建同版本制品。
- Release 附件包括 wheel、sdist、`sha256sums.txt` 和 `sbom.json`；构建来源证明通过 GitHub Artifact Attestations 查询。
- wheel 必须携带客户部署文档与 bundled Skill，`cn-stock-mcp --docs-path` 必须能定位它们。
- 不发布 token、`.env`、用户 `config.json`、诊断包或含凭据的 Host 配置。
- `constraints-release.txt` 固定直接运行、测试和发布工具版本；传递依赖的最终解析结果以 `sbom.json` 为准，不宣称跨时间字节级完全复现。

## Verification order

1. `git status --short --branch` 干净，并确认版本只由 `pyproject.toml` 提供。
2. 运行受影响测试、完整非 live 回归、严格 JSON/脱敏测试、`python -m build` 和 wheel 安装 smoke。
3. 验证 53 个 full 工具、10 个 retail 工具、MCP initialize / tools/list / tools/call，以及 `--docs-path`。
4. 生成 SHA256 和 SBOM，检查 wheel/sdist 内容清单；不得包含 token、测试缓存、旧制品或私有配置。
5. 在 TestPyPI 或受控预发布环境验证安装；为最终发布提交创建新的不可变 tag。
6. 推送 `main` 和 tag；tag workflow 必须先通过干净 Windows wheel gate，再使用 PyPI Trusted Publishing，并创建同版本 GitHub Release。
7. 用公开 PyPI 元数据、GitHub Release API、附件 SHA256 和 provenance 核验发布成功。
8. 在干净 Windows 标准用户环境按 `AI_DEPLOY_WINDOWS.md` 完成从安装到首次 MCP 问答的验收。

PyPI 发布使用 Trusted Publishing，不在仓库 secrets 或工作流中保存长期 PyPI API token。GitHub Artifact Attestations 不能替代 SHA256、消费者自行验证或第三方数据授权审查。

## Historical release evidence

- `v0.2.0` 的发布切点：`1651a510b03edd49852e04139b3ce98ed1a244fc`
- `v0.2.0` Windows 验收：`WINDOWS_ACCEPTANCE_v0.2.0.md`
- `v0.2.0` 公开安装补充验收：`WINDOWS_ACCEPTANCE_POST_RELEASE_2026-08-20.md`

历史记录只证明对应 tag，不自动证明后续提交或新版本。
