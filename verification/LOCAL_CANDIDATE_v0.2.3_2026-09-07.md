# 0.2.3 本地候选包验证记录

验证日期：2026-09-07（Asia/Shanghai）。结论：本地构建、新建虚拟环境安装、依赖闭包和离线 MCP 协议验证通过；真实上游、实际 Codex 客户端、数据权限和公开发布仍待完成。

本记录独立存放在 verification 目录，不加入客户 wheel 的 docs 文件集。记录中的哈希对应本次本地候选包；最终标签工作流生成的正式制品必须另行核验。

## 环境与范围

- 仓库：`F:\agents\code\cn-stock-mcp`，main 分支。
- 实现前检查点：`b870730`；依赖声明修正前检查点：`203700e`。
- 当前 Windows 开发机，普通 CPython 3.13.2 / 64 bit。
- 以 Windows 用户 Lenovo 在新目录 `F:\agents\code\temp\cn-stock-sale-offline-run-20260906\wheel-runtime-v2` 创建 venv 并安装。本次不是全新 Windows 机器或新标准用户账户验收。
- 从 PyPI 使用固定 Windows 约束和发布约束安装，未使用开发环境的 site-packages。
- 全部应用检查使用临时空配置与隔离工作目录；未读取实际 Token 配置，未执行真实行情请求或修改 Codex 配置。
- 首发范围继续为 Windows 11 x64 / 普通 CPython 3.13 / Codex / retail 10 工具。具体 Codex 客户端类型与版本须单独记录。

## 本次修正

已安装依赖检查脚本使用 packaging，但原包未声明它；新环境因此无法运行该脚本。现已在 pyproject 声明 `packaging>=26.3`，在发布约束中固定 `packaging==26.3`，沿用原有 Windows 同版本 pin，并修正注释。

pip 安装报告显示 packaging 26.3 随产品自动安装，`requested=false`；没有通过单独安装该库来绕过缺失的产品依赖声明。发布说明和销售准备清单已同步。

## 验证结果

| 检查 | 结果与范围 |
| --- | --- |
| 完整非 live 回归 | 此次连续任务前段已完成：632 passed、76 deselected，16.59 秒；在隔离目录运行。之后只改动文档、工作流和本次依赖声明/注释 |
| 本次受影响测试 | `tests/test_runtime_constraints.py`：9 passed，0.29 秒 |
| 工作流与文档 | 此前已验证 YAML 无重复键、9 个 workflow shell 脚本语法、Codex TOML、21 份修改文档的本地链接及 21 个 PowerShell 示例；本次文档只更新依赖说明 |
| wheel / sdist 构建 | 使用现有构建依赖离线构建成功；保留旧候选包 |
| 包内容一致性 | 172 个 Python 源文件、49 份文档、3 个客户验证脚本与当前源码字节一致；携带 pyproject、Windows 约束和许可证 |
| 排除文件 | 未包含真实配置、密钥文件、Git、测试目录、虚拟环境或缓存目录；仅按明确定义的文件名/路径规则检查，不替代最终 secret scan |
| 新 venv 安装 | 安装 0.2.3 及 69 个运行时依赖；packaging 26.3 自动安装 |
| pip check | PASS：No broken requirements found |
| 本地 doctor | 退出码 0；未进行网络自检 |
| 工具目录 | 正好 10 个 retail 工具 |
| 完整依赖闭包 | 检查 84 条约束，实际依赖图 69 项；没有缺少 pin 或版本冲突 |
| 包内验收计划 | plan_only，10 个计划项；未启动真实数据验收 |
| 包内 stdio 检查 | initialize、tools/list 和 INVALID_ARGUMENT 错误响应通过；服务端版本 0.2.3，协议 2025-11-25 |
| 实际导入路径 | 位于 wheel-runtime-v2/Lib/site-packages/cn_stock_mcp，未导入工作区源码 |
| SBOM | 针对新 venv 生成 CycloneDX 1.6 JSON，70 个 components，包含 packaging 26.3 |
| 本地制品一致性 | `verify_release_artifacts.py --version 0.2.3 --local-only` 通过 |

stdio 的成功数据响应由此前固定样本子进程测试验证；本次已安装包的 stdio 检查只发送无效参数，不构成有效行情或真实 Codex 验收。

## 候选制品

目录：`F:\agents\code\temp\cn-stock-sale-offline-run-20260906\release`。

| 文件 | 字节数 | SHA256 |
| --- | ---: | --- |
| dist/cn_stock_mcp-0.2.3-py3-none-any.whl | 442926 | 3b97329b662970dd41e1d414207450f85493c6a222b419b300e5df4a555e684e |
| dist/cn_stock_mcp-0.2.3.tar.gz | 323705 | 8df378f9ea803ad8666e517d57c842e722843c3428410eab21e3e5862ace9d40 |
| constraints-windows-py313.txt | — | 99bdb1f0ae4c89b36569147e62aaaa72ef35ba9dcee71160e7356fdabce40cf7 |
| sbom.json | — | b014e1213cd53ee4b0b3cf3543fde2b4692c97749667bac4a50bfd5add39b377 |
| sha256sums.txt | — | de49e9b503b771f991e2c82e4754d8d7d727dca7ce5dec6b03392529d9c690b4 |

同一临时工作目录还保留：

- `build-packaging-fix.log`：构建输出。
- `wheel-install-v2.log`、`wheel-install-v2-report.json`：实际安装结果及包元数据。
- `verify_installed_candidate_v2.ps1`：本地安装后检查命令。
- `installed-candidate-v2.json`：安装后各项检查、实际导入路径和 NOT_RUN 标记。
- `release/candidate-inspection.json`：源码/打包内容计数与制品哈希。
- `release/release-integrity-local.json`：完整本地文件集与哈希校验结果。
- `release/before-packaging-fix/`：缺依赖版本的候选包及其检查记录。

生成 wheel 的 Windows ACL 仅增加了 Lenovo 用户的该文件读取权限；操作前后 SHA256 一致。未扩大目录权限或修改实际 Token 配置 ACL。

## 关键命令

以下命令针对上述临时环境；测试和协议检查需继续使用空配置、空工作目录并清除遗留 Token 环境变量。

```powershell
$repo = 'F:\agents\code\cn-stock-mcp'
$run = 'F:\agents\code\temp\cn-stock-sale-offline-run-20260906'
$devPython = Join-Path $repo '.venv\Scripts\python.exe'
$candidatePython = Join-Path $run 'wheel-runtime-v2\Scripts\python.exe'

& $devPython -X utf8 -B -m pytest -q -x -p no:cacheprovider (Join-Path $repo 'tests\test_runtime_constraints.py')
& $devPython -X utf8 -B -m build --no-isolation --outdir (Join-Path $run 'release\dist') $repo
& (Join-Path $run 'verify_installed_candidate_v2.ps1')
& $devPython -X utf8 -B -m cyclonedx_py environment $candidatePython --pyproject (Join-Path $repo 'pyproject.toml') --output-reproducible --output-format JSON --output-file (Join-Path $run 'release\sbom.json')
& $devPython -X utf8 -B (Join-Path $repo 'scripts\verify_release_artifacts.py') --version 0.2.3 --root (Join-Path $run 'release') --local-only
```

以上为本轮执行命令的定位参考，重跑构建或 SBOM 会改变候选制品，应先选择新输出目录并生成新的完整校验清单。

## 正式售卖前仍需完成

1. 获准让候选 MCP 进程使用用户自有 Token 配置与网络，执行最多 10 次顺序工具调用；任何非 PASS 结果停止，保留未执行项。当前状态为 NOT_RUN。
2. 在约定的实际 Codex 客户端中完成连接、工具调用、问答和配置恢复，记录客户端类型/版本及标准用户环境。当前状态为 NOT_RUN。
3. 完成实际数据用途、上游权限与依赖许可证据审核。SBOM 只提供清单，不代表审核通过。
4. 对最终提交执行远端 CI、依赖审计、secret scan 和 CodeQL；获准后创建新 tag 并发布，核验两平台哈希、构建证明及公开下载后的标准用户安装。

本次没有推送、创建 tag 或发布 0.2.3。售后仍为验收后 7 天支持、2 个工作日响应、3 天首次验收、最多 2 次且累计不超过 7 天补救，无法验收时按平台规则退款；报价与成交渠道不在项目中决定。
