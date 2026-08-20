# v0.2.0 Release Guide

## Release invariants

- `pyproject.toml` 是唯一版本源，源码、MCP server、doctor 和制品均报告 `0.2.0`。
- 发布切点的 `main`、`v0.2.0` tag、PyPI 文件和 GitHub Release 必须来自同一提交；发布后允许把验收记录等文档提交到 `main`，但不得移动 tag、重建同版本制品或声称它们包含这些后续提交。
- Release 附件包括 wheel、sdist、SHA256 文件和 SBOM；构建来源证明通过 GitHub Artifact Attestations 查询，不作为普通 Release 附件。
- 不发布 token、`.env`、`config/zhitu_tokens.json`、诊断包或含凭据的 Host 配置。
- `constraints-release.txt` 固定直接运行、测试和发布工具版本；pip 仍解析传递依赖，最终解析结果以 `sbom.json` 为准。这是首版的可复现边界，不宣称跨时间字节级完全复现。

## Verification order

1. `git status --short --branch` 干净，确认当前分支、远端和 HEAD。
2. 运行受影响测试、完整非 live 回归、`python -m build` 和 wheel 安装 smoke。
3. 生成 SHA256 和 SBOM，检查内容清单；校验文件使用 Release 附件的平铺文件名。
4. 在 TestPyPI 或受控预发布环境验证安装，再发布正式 PyPI。
5. 创建 GitHub Release，上传同一批制品和校验文件。
6. 用公开 PyPI 元数据、GitHub Release API、下载校验和确认发布成功。
7. 在干净 Windows 用户环境执行 `docs/AI_DEPLOY_WINDOWS.md`。

PyPI 发布使用 Trusted Publishing，不在仓库 secrets 或工作流中保存长期 PyPI API token。GitHub Actions Artifact Attestations 用于记录构建来源；它们不能替代 SHA256 或第三方数据授权审查。

## v0.2.0 发布切点

`v0.2.0` 的发布切点是提交 `1651a510b03edd49852e04139b3ce98ed1a244fc`。
发布后的 Windows 验收补充记录位于 `docs/WINDOWS_ACCEPTANCE_POST_RELEASE_2026-08-20.md`，
属于后续文档提交，不改变已经公开的 `v0.2.0` tag、PyPI 文件或 GitHub Release。
