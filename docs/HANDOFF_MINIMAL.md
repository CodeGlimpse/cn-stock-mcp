# Handoff Minimal (`cn-stock-mcp`)

> 0.2.3 发布准备：当前文档描述待发布版本。执行安装前必须确认同版本 PyPI、GitHub Release 与校验文件已公开；缺失时停止，不改装 main。

如果你是第一次接触这类工具，只做下面 3 步：

## 第 1 步：安装

```bash
python -m pip install cn-stock-mcp==0.2.3
```

收费交付或由 AI Agent 自动部署时，请改按 `AI_DEPLOY_WINDOWS.md` 下载 wheel 并核对 GitHub Release 的 SHA256，不要安装 GitHub `main`。

## 第 2 步：先确认程序装好了

```bash
cn-stock-mcp --version
cn-stock-mcp --doctor
```

初始化本机配置文件，然后由用户手动填入 token：

```bash
cn-stock-mcp --init-config
```

默认路径是 Windows 的 `%LOCALAPPDATA%\cn-stock-mcp\config.json`。不要把 token 写入 Host 配置。

填好 token 后再继续：

```bash
cn-stock-mcp --doctor-network
```

- `--doctor`：只检查本地安装是否正常
- `--doctor-network`：额外检查 token 和上游连通性

## 第 3 步：接入并验收 Codex

首发仅验收 Codex。按 [CODEX_TEMPLATE.md](CODEX_TEMPLATE.md) 使用实际可执行文件绝对路径与 --stdio，备份并合并 TOML 配置，记录实际客户端类型/版本。

按 [RETAIL_ACCEPTANCE.md](RETAIL_ACCEPTANCE.md) 先展示样本查询计划，获准后执行真实 MCP 验收，并在 Codex 完成实际问答。其他 Host 模板继续保留，不代表首发已通过。

---

## 接下来只在需要时再看

- `docs/HOST_CONFIG_TEMPLATES.md`：不同 host 的复制即用模板
- `docs/FAQ.md`：常见错误与排查
- `docs/EXAMPLES_MINIMAL.md`：最小调用示例
- `docs/COMPATIBILITY.md`：不同 host / skill host 的兼容说明
- `docs/INTEGRATION.md`：更完整的挂载与联调说明
