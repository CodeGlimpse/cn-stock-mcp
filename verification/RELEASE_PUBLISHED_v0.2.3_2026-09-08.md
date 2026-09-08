# 0.2.3 正式发行核验记录

日期：2026-09-08。发行提交：`3e771f4e80f643a009b04f9b2a3c8a7dc7c97204`。不可变标签：`v0.2.3`。

本记录在发布后单独保存，不重建 wheel/sdist，不移动标签，不替换已发布文件。此前的[发行前检查记录](RELEASE_READINESS_v0.2.3_2026-09-08.md)和候选制品保留为历史证据。

## 完成状态

- [GitHub Release v0.2.3](https://github.com/CodeGlimpse/cn-stock-mcp/releases/tag/v0.2.3) 已公开，包含两份分发包、Windows 约束、SHA256 清单和最终 Windows 运行时 SBOM。
- [PyPI cn-stock-mcp 0.2.3](https://pypi.org/project/cn-stock-mcp/0.2.3/) 已公开，wheel/sdist 与 GitHub 附件、CI 保存的最终制品字节一致。
- 69 项实际 Windows 运行依赖的 109 份许可证/通知原文及机器清单随安装包交付；安装后的许可证检查通过，见[第三方许可证说明](../docs/THIRD_PARTY_LICENSES.md)。
- 服务约定已统一为代码免费 MIT 开源，收费仅针对部署和代码运行售后，见[服务交付约定](../docs/COMMERCIAL_DELIVERY_TEMPLATE.md)。

首次客户验收 3 天；验收后支持 7 天，2 个工作日内响应；安装失败最多补救 2 次，累计不超过 7 天；约定环境仍不能验收时按成交平台规则退款。报价及渠道由订单处理。

## 远端检查

以下检查均对应发行提交 `3e771f4e80f643a009b04f9b2a3c8a7dc7c97204`：

| 检查 | 结果与证据 |
| --- | --- |
| CI | [34146526964](https://github.com/CodeGlimpse/cn-stock-mcp/actions/runs/34146526964) 成功；Python 3.11、3.12、3.13 及 Windows smoke 全部通过 |
| Secret scan | [34146526927](https://github.com/CodeGlimpse/cn-stock-mcp/actions/runs/34146526927) 成功 |
| CodeQL | [34146526933](https://github.com/CodeGlimpse/cn-stock-mcp/actions/runs/34146526933) 成功 |
| Release | [34147728233](https://github.com/CodeGlimpse/cn-stock-mcp/actions/runs/34147728233) 第 2 次执行成功；build-and-audit、windows-wheel-smoke 和 publish 均通过 |
| 最终制品 | 原运行保存的 `release-3e771f4e80f643a009b04f9b2a3c8a7dc7c97204` 与实际公开下载文件一致 |
| 完整发行报告 | 已下载 `release-verification-3e771f4e80f643a009b04f9b2a3c8a7dc7c97204`；PyPI/GitHub 缺失文件列表均为空 |
| 标签与主分支 | 收尾时通过 GitHub API 确认 main 和 v0.2.3 的提交均为上述发行提交 |

第一次 publish 中，PyPI 两份上传均返回 200，但随后约 30 秒内的完整性检查仍未查询到文件。之后两平台元数据均可见且哈希一致，经用户批准只重跑失败的 publish 作业；原构建、Windows 检查和最终 artifact 均复用。第 2 次发布完成完整性核验，没有重建或覆盖同版本制品。

## 正式制品 SHA256

下表是正式 CI/线上制品哈希，不能与发行前本地候选压缩包的哈希混用。

| 文件 | 字节数 | SHA256 |
| --- | ---: | --- |
| cn_stock_mcp-0.2.3-py3-none-any.whl | 661665 | 5f36f17eab33d4ea1635083e1ffb34174959efc76d97e9e4ee5b664e766a9186 |
| cn_stock_mcp-0.2.3.tar.gz | 444115 | 5ac72fa4e7d27fea13731c41240f2f10388ca7f7cff06e6204986c7dea588f8d |
| constraints-windows-py313.txt | 2073 | 99bdb1f0ae4c89b36569147e62aaaa72ef35ba9dcee71160e7356fdabce40cf7 |
| sbom.json | 89929 | 401406ebc80c79555b18c8453a824738096c69a524f5295ce148343adc300590 |
| sha256sums.txt | 370 | 784b49bdd91c75793c3bcd2a42a293cc2a24ed176304cb5bd0bddcb3f60b262f |

本地使用项目 `verify_release_artifacts.py` 的 `local_manifest` 和 `compare_releases(require_complete=True)`，以公开 PyPI 元数据和经授权获取的 GitHub 元数据核对完整文件集；另对从两平台实际下载的字节计算 SHA256，与 CI 最终 artifact 逐项比较。CI 的完整性报告与该比较结果一致。

wheel 和 sdist 分别通过 `gh attestation verify`，限定仓库 `CodeGlimpse/cn-stock-mcp`、上述 source digest、`refs/tags/v0.2.3`、`.github/workflows/release.yml`，并启用 `--deny-self-hosted-runners`。

最终 SBOM 为 CycloneDX 1.6，70 个 components：69 项实际运行依赖及 pip，包含 pywin32 312。Windows 约束文件有 84 个版本限定；约束不会主动安装所有列出的包。补充检查脚本首次将 84 项全当作必装依赖，误报 defusedxml 缺失；经批准，新建离线脚本按正式 wheel 内记录的 69 项实际依赖核对，全部通过。原脚本与下载文件保留。

## 公开包安装检查

将从 PyPI 公共文件地址下载、已验证哈希及来源证明的 wheel 安装到全新临时 venv；依赖仅通过公共 PyPI，按正式 Windows 约束解析。运行进程使用普通用户令牌，`administrator_token=false`，没有修改系统 Python 或实际 Host 配置。

| 检查 | 结果 |
| --- | --- |
| Python | 普通 CPython 3.13.2 x64，非 free-threaded |
| 安装与 pip check | 成功，无损坏依赖关系 |
| 实际版本与导入位置 | 0.2.3；从新 venv 的 site-packages 导入 |
| doctor | 空配置离线检查，exit code 0 |
| 工具目录 | 精确 10 个 retail 工具 |
| 依赖闭包 | 69 项，固定版本覆盖完整、无冲突 |
| 打包许可证 | 69 packages / 109 notice files / 9 direct dependencies，通过 |
| 验收脚本 | plan_only，10 个计划项 |
| MCP stdio | initialize、tools/list、INVALID_ARGUMENT 检查通过；协议 2025-11-25，successful_call=null |

测试使用新建空配置；子进程清除相关 Token/配置覆盖环境变量，不读取真实 Token 或实际客户配置。没有发送有效行情调用。

## 范围与证据

首发服务范围仍为 Windows 11 x64、普通 CPython 3.13、按订单约定的 Codex 客户端、retail 10 工具。[13 款 Windows Agent 指南](../docs/WINDOWS_AGENT_SETUP.md)提供配置参考，不表示完成 13 款 Host 实测。

按用户决定，本轮没有真实行情查询或实际 AI Host 验收；Live Smoke 没有被触发。客户交付后的验收另按订单执行，未执行项不记为通过。

经营者自行保管私人授权文件，本次没有收集、公开或代审私人协议；软件许可检查不等于核验了所有数据用途授权，见[数据使用边界](../docs/DATA_RIGHTS_REGISTER.md)。

本地证据目录：`F:\agents\code\temp\cn-stock-agent-docs-20260907\sale-final\published-v0.2.3-3e771f4-20260908`。

- `release-run.json`、`github-metadata.json`、`pypi-metadata.json`：公开发行及流程元数据。
- `ci-artifact/`、`ci-verification/`、`github-assets/`、`pypi-files/`：原始 CI 制品、最终核验报告及实际公开文件。
- `published-integrity.json`：完整文件、两平台字节及 Windows SBOM 检查结果。
- `wheel-attestation.json`、`sdist-attestation.json`：严格限定来源的签名证明核验结果。
- `install-context.json`、`install-published-report.json`、`install-published.log`、`installed-published.json`：普通用户安装与空配置检查证据。
- `verify_published_downloads_v2.py`、`verify_published_install.ps1`：本次使用的下载文件核验和离线安装检查脚本。

本次约定的正式发行、软件依赖许可材料、部署与运行售后口径三项已完成。没有以本轮未执行的真实行情/Host 测试作为通过证据。
