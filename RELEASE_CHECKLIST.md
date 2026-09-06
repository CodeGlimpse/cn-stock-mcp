# Release Checklist

## 代码与制品

- [ ] 已确认 Git diff、版本和本地提交，工作区没有待交付改动。
- [ ] 受影响测试与隔离的完整非 live 回归通过。
- [ ] wheel/sdist 构建成功，版本一致，内容不含真实配置、Token、测试缓存或旧制品。
- [ ] wheel 包含客户文档、Skill、验收工具；安装后的 --docs-path 可定位。
- [ ] Windows 运行时约束检查、pip check、--installed 依赖闭包检查通过。
- [ ] retail 正好 10 工具；full 保留 53 工具。
- [ ] stdio 初始化、工具目录、错误与固定样本成功响应测试通过。
- [ ] JSON、脱敏与数据质量回归通过。
- [ ] 最终提交的依赖审计、secret scan、CodeQL 和 CI 通过。

## 首发交付

- [ ] Codex + Windows 11 x64 + 普通 CPython 3.13 的实际版本记录完成。
- [ ] 经授权的 retail 真实样本验收报告已归档，非 PASS 项与未执行项已闭环。
- [ ] 实际 Codex 客户端调用及问答验收完成，不能用脚本/模板代替。
- [ ] 标准用户固定 wheel 安装、配置恢复和首次问答通过。
- [ ] 数据权限与依赖许可记录完成。
- [ ] 7 天支持、2 工作日响应、3 天首次验收、2 次/累计 7 天补救、平台退款条款一致。
- [ ] 订单的版本/hash、交付时点、联系入口、验收/支持截止时间可填写；报价不在本项目中决定。
- [ ] 其他 Host 仅保留模板，没有被描述为首发已验收。

## 发布

- [ ] pyproject、当前文档、CHANGELOG、release note 已同步；历史记录保留。
- [ ] 获得提交推送、新 tag 和远程发布授权。
- [ ] 标签工作流一次构建并在 Windows 安装同一 artifact，通过后再发布。
- [ ] 上传前通过 `verify_release_artifacts.py` 远端哈希冲突检查。
- [ ] PyPI Trusted Publishing 与 GitHub Release 成功，不覆盖同版本附件。
- [ ] --require-complete 核验两平台同一 wheel/sdist 与全部附件哈希通过。
- [ ] SHA256、SBOM、构建证明和发布验证报告可取得。
- [ ] 公开下载后的标准用户安装验收记录完成。

命令、恢复流程和证据边界见 [Release Guide](docs/RELEASE_GUIDE.md)。
