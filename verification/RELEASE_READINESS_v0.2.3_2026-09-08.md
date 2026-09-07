# 0.2.3 发行前检查记录

日期：2026-09-08。变更前检查点：`80453a7`。本记录不进入客户 wheel/sdist，避免检查结果改变被检查的制品。

## 已确认的范围

GitHub 代码免费按 MIT 开源，收费仅针对部署及代码运行售后。首发服务环境为 Windows 11 x64、普通 CPython 3.13、约定的 Codex 客户端及 retail 10 工具；13 款 Windows 配置指南提供参考，不宣称完成所有 Host 实测。

客户首次验收 3 天；验收后支持 7 天，2 个工作日内响应；安装失败最多补救 2 次、累计不超过 7 天，约定环境仍无法验收时按成交平台规则退款。研发阶段的真实行情/实际 AI Host 验收按用户决定不执行，客户交付验收单独记录。

经营者表示已有书面授权并自行保管。没有收集、公开或代审私人协议；本次核对公开条款和软件许可证，不据此声明所有数据用途均获授权。

## 变更内容

- 同步服务、支持、README、数据使用边界和发布说明，清理不再需要的询证草稿。
- 整理 69 项固定 Windows 运行依赖、109 份去重许可证/通知原文及机器清单，随安装包分发。
- 新增纯标准库许可证校验器，检查 pin、直接依赖覆盖、计数、大小、SHA256、重复、缺失及路径越界；约束换行按 LF 规范化，许可证保留原始字节。
- 发布包仍只构建一次。Windows 阶段安装原包，生成最终运行时 SBOM，并检查原包和约束的哈希保持不变；发布阶段复用最终 artifact。
- PyPI 使用独立上传目录，规范 dist 始终保留两份分发包；前后校验两平台哈希，不覆盖已存在的不同字节。

## 验证结果

| 检查 | 结果 |
| --- | --- |
| 完整非 live 回归 | 656 passed，76 deselected，28.62 秒；隔离目录与非真实配置 |
| 新增许可证测试 | 24 passed，包含在完整回归中 |
| 实际许可证附件 | 69 packages / 109 notice files / 9 direct dependencies，通过 |
| 固定版本漏洞审计 | 两份约束文件列出的 92 项，0 个已知漏洞；无自动升级或忽略漏洞 |
| Windows 指南检查 | 13 款，25 条官方来源引用均对应已取得正文 |
| 文档自动检查 | 34 份文档、289 个本地链接、13 JSON / 2 YAML / 1 TOML 块通过；后续纯文本版本与服务口径调整另经差异检查 |
| 文档 PowerShell | 24 段语法通过，未执行客户示例 |
| 发布工作流 | YAML 解析、3 段 PowerShell / 8 段 Bash 语法通过；独立静态复核未发现新增确定阻塞 |
| 最终候选包构建 | wheel / sdist 构建成功，使用现有构建依赖与 --no-isolation |
| 最终包内容 | 55 份文档、109 份原文及 manifest、4 个客户工具、172 个 Python 源文件均与工作区字节一致 |
| 制品排除项 | 没有真实配置、Git、虚拟环境、测试目录、verification 记录或询证草稿 |
| 新建临时 venv 安装 | 固定约束安装成功，pip check 通过 |
| 安装后本地检查 | 版本 0.2.3、doctor 退出 0、retail 正好 10 工具、69 项依赖闭包通过 |
| 安装后许可证与计划 | 打包许可证校验通过；retail 计划模式 10 项通过 |
| 离线 stdio | initialize、tools/list、INVALID_ARGUMENT 通过；未发送有效行情查询 |
| 最终 SBOM | CycloneDX 1.6，70 个 components，包含 Windows pywin32 312；针对新安装环境生成 |
| 本地完整制品清单 | verify_release_artifacts.py --local-only 通过 |

已独立核对 109 份暂存原文的 SHA256 与许可证清单一致，Git 索引没有未解决冲突。pyjwt 的原始 AUTHORS.rst 标题下划线为七个等号，Git 曾将其误判为冲突标记；经用户批准，仅为该文件设置 conflict-marker-size=8，原文和哈希保持不变。

2026-09-07 的漏洞审计使用 --no-deps --disable-pip 查询固定列表，不替代最终标签流程对实际安装环境及发布工具的审计。Live Smoke 工作流只有手动触发入口，计划中的 main/tag 推送不会触发它。

## 本地证据与命令

证据目录：`F:\agents\code\temp\cn-stock-agent-docs-20260907\sale-final`。

- `runtime-and-release-audit.json`：固定版本公开漏洞查询。
- `documentation-check-final.json`、`powershell-snippets-final.json`：文档检查。
- `build-final.log`、`install-final.log`、`install-final-report.json`：构建与新环境安装。
- `verify_installed_final.ps1`、`installed-final.json`：使用临时空配置的安装后检查。
- `release/sbom.json`、`release/sha256sums.txt`、`local-release-integrity.json`：完整本地文件集与哈希。

主要命令为项目 Python 的 `-m pytest -q -x -p no:cacheprovider -m 'not live'`、`scripts/verify_license_bundle.py`、`-m build --no-isolation`、`-m pip check`、`verify_runtime_constraints.py --installed`、打包 stdio/计划检查、`-m cyclonedx_py environment <新运行时Python>` 和 `verify_release_artifacts.py --version 0.2.3 --local-only`。

## 本地候选制品

以下哈希只对应本地候选包。正式发布使用标签工作流重新构建并验证的同一组制品，须以该流程的最终附件和证明再次核对，不能把本地 hash 当作线上 hash。

| 文件 | SHA256 |
| --- | --- |
| cn_stock_mcp-0.2.3-py3-none-any.whl（665137 字节） | c9cc3027ecacb35d63e0908b116a0d3160b18ebc3591a5ad2641ec992b456c7f |
| cn_stock_mcp-0.2.3.tar.gz（452449 字节） | 6cc8723a80375a86c1c00c6a11fad1133712e20332d174dbe245d638ab63b6c8 |
| constraints-windows-py313.txt | 99bdb1f0ae4c89b36569147e62aaaa72ef35ba9dcee71160e7356fdabce40cf7 |
| sbom.json | b014e1213cd53ee4b0b3cf3543fde2b4692c97749667bac4a50bfd5add39b377 |
| sha256sums.txt | 28819e6021040f30ac76c5465160c071b22363d2ba709ea3267e0d1a2d36133e |

候选包不包含 CHANGELOG.md；将该文件日期同步到实际准备完成日未改变候选包内容。

## 远端阶段

记录创建时尚未执行本轮推送、tag 或发布。下一步在取得针对具体 Git/GitHub 操作的权限后，检查远端是否有变化、推送已核对提交、等待 CI/Secret scan/CodeQL，再创建新的 v0.2.3 标签触发发行，并核对 PyPI/GitHub 文件及证明。任何失败或版本冲突均不以覆盖/移动旧标签的方式处理。
