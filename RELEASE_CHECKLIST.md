# Release Checklist

软件代码免费按 MIT 开源，收费仅针对部署及代码运行售后。下面分别记录发行检查和每笔客户服务；历史证据与本轮结果见 verification 目录。

## 代码与制品

- [ ] 已确认 Git diff、版本和本地提交，工作区没有待交付改动。
- [ ] 受影响测试与隔离的完整非 live 回归通过。
- [ ] wheel/sdist 构建成功，版本一致，内容不含真实配置、Token、测试缓存或旧制品。
- [ ] wheel 包含客户文档、Skill、验收工具；安装后的 --docs-path 可定位。
- [ ] Windows 运行时约束检查、pip check、--installed 依赖闭包检查通过。
- [ ] retail 正好 10 工具；full 保留 53 工具。
- [ ] stdio 初始化、工具目录、错误与固定样本成功响应测试通过。
- [ ] JSON、脱敏与数据质量回归通过。
- [ ] 许可证附件验证通过，固定依赖版本、原文 SHA256、安装包内容一致。
- [ ] 最终提交的依赖审计、secret scan、CodeQL 和 CI 通过。

## 每笔客户服务

- [ ] Codex + Windows 11 x64 + 普通 CPython 3.13 的实际版本记录完成。
- [ ] 研发阶段真实行情和实际 AI Host 验收按用户决定记录为未执行，不宣传实测通过。
- [ ] 客户在交付后按订单约定进行验收，记录已执行和未执行项，不能用模板代替实际结果。
- [ ] 标准用户固定 wheel 安装、配置恢复和首次问答通过。
- [ ] 软件及依赖许可说明完整；具体授权协议由经营者自行保管，不收录私人协议。
- [ ] 7 天支持、2 工作日响应、3 天首次验收、2 次/累计 7 天补救、平台退款条款一致。
- [ ] 订单的版本/hash、交付时点、联系入口、验收/支持截止时间可填写；报价不在本项目中决定。
- [ ] 其他 Host 仅保留模板，没有被描述为首发已验收。

## 发布

- [ ] pyproject、当前文档、CHANGELOG、release note 已同步；历史记录保留。
- [ ] 获得提交推送、新 tag 和远程发布授权。
- [ ] 标签工作流一次构建并在 Windows 安装同一 artifact，通过后再发布。
- [ ] 最终 SBOM 来自经过验证的 Windows 运行环境，未误用 Linux 构建环境清单。
- [ ] 上传前通过 `verify_release_artifacts.py` 远端哈希冲突检查。
- [ ] PyPI Trusted Publishing 与 GitHub Release 成功，不覆盖同版本附件。
- [ ] --require-complete 核验两平台同一 wheel/sdist 与全部附件哈希通过。
- [ ] SHA256、SBOM、构建证明和发布验证报告可取得。
- [ ] 公开下载后的标准用户安装验收记录完成。

命令、恢复流程和证据边界见 [Release Guide](docs/RELEASE_GUIDE.md)。
