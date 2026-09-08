# 免费代码发行与部署服务准备状态

检查日期：2026-09-08。适用版本：`0.2.3`。GitHub 代码免费开源，收费仅针对部署和代码运行售后；首发约定环境为 **Windows 11 x64 / 普通 CPython 3.13 / Codex / retail 10 工具**。

本页区分软件发行验证、研发验证和客户服务验收。`0.2.3` 已在 [GitHub Release](https://github.com/CodeGlimpse/cn-stock-mcp/releases/tag/v0.2.3) 和 [PyPI](https://pypi.org/project/cn-stock-mcp/0.2.3/) 正式发行；公开制品与发行前本地候选包分别留证。

## 已确定的范围

- 首发服务按订单记录 Codex 客户端类型和版本；13 款 Windows 指南提供配置参考，不等于全部客户端已经实测。
- 客户验收后提供 7 天部署及代码运行售后，2 个工作日内响应；首次验收 3 天。
- 安装失败最多补救 2 次，累计不超过 7 天；约定环境仍不能验收时按成交平台规则退款。
- 报价和成交渠道不在本项目中决定；每笔交付沿用订单的联系入口。

## 准备项目与证据状态

2026-09-07 用户决定本轮不执行真实测试，改为补全 13 款 Windows Agent 配置方法。已有验证记录保留，未实测项不标为通过，也不阻塞本轮文档交付。

| 项目 | 当前状态 | 完成依据 |
| --- | --- | --- |
| 运行时依赖闭包 | 已补充 cffi pin、packaging 依赖声明和已安装依赖图检查 | 固定 wheel 安装后 `pip check` 与 `verify_runtime_constraints.py --installed` |
| 发布文件一致性 | 已通过一次构建、Windows 安装验证、最终运行时 SBOM、两平台 SHA256 及构建来源证明检查 | [正式发行工作流](https://github.com/CodeGlimpse/cn-stock-mcp/actions/runs/34147728233)；公开 wheel/sdist 与 CI 最终制品一致 |
| Windows Agent 配置指南 | 已补全 13 款及共同准备、来源记录；本轮仅文档和离线核对 | [配置总表](HOST_CONFIG_TEMPLATES.md) |
| retail 验收工具 | 已实现计划、限量样本、失败停止、脱敏报告；离线测试通过 | [RETAIL_ACCEPTANCE.md](RETAIL_ACCEPTANCE.md) |
| 真实上游验收 | 本轮按用户决定不执行；前次预检因配置路径阻塞，0 次工具调用 | 研发阶段记为未执行；客户验收另按订单记录实际范围、结果及未执行项 |
| 真实 Codex 验收 | 本轮按用户决定不执行，未形成实际客户端结果 | 版本、标准用户环境、10 工具、实际问答、恢复步骤记录 |
| 0.2.3 制品与公开安装 | 已发布；最终 CI 与 Windows 公开包新建虚拟环境安装检查通过 | `pip check`、69 项依赖闭包、10 工具目录及离线 stdio 通过；未包含真实行情或实际 Host 测试 |
| 售后与退款规则 | 已按用户决定同步 | [COMMERCIAL_DELIVERY_TEMPLATE.md](COMMERCIAL_DELIVERY_TEMPLATE.md) |
| 软件与依赖许可 | 核心 MIT、69 项运行依赖的 109 份原文及完整性验证已整理 | [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) |
| 数据使用边界 | 已核对公开资料；经营者自行保管其授权文件，项目不收录私人协议 | [DATA_RIGHTS_REGISTER.md](DATA_RIGHTS_REGISTER.md)，不将本次工作表述为代审私人授权范围 |

本轮按用户决定不执行真实行情和实际 AI Host 验收，不以此阻塞免费代码发行，也不记录为通过。客户验收在每笔服务交付后按订单进行；配置文档、离线检查和实际查询结果分别记录。

## 每笔交付时填写

- 固定版本、下载地址、wheel SHA256、约定环境。
- 交付时点、验收期限、实际验收结论、支持截止时间。
- 订单联系入口、补救记录及适用平台退款规则。
- 客户确认自备 Token、额度与第三方服务；卖方不接收、不代填 Token。
- 客户确认数据来源、权限边界、已知缺失以及非投资建议性质。

按交付模板保存订单关联信息和脱敏证据；不归档 Token、配置文件、带凭据 URL 或原始上游日志。

## 后续功能，不作为本次承诺

Windows GUI 安装器、DPAPI 向导、多 Host 验收、观察列表持久化、内置定时任务、托管数据服务和完整 53 工具的销售承诺，均需另立范围。首发不应因这些扩展继续无限加功能。
