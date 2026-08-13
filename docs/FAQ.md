# FAQ (`cn-stock-mcp`)

如果你是第一次安装，先看：
- `docs/HANDOFF_MINIMAL.md`
- `docs/HOST_CONFIG_TEMPLATES.md`

---

## 1) 我已经安装了，为什么还是提示找不到 `cn-stock-mcp`？

先重试：

```bash
python -m pip install cn-stock-mcp
```

如果你是源码开发环境，出现下面这种情况并不一定是坏了：
- `python -m cn_stock_mcp.main --doctor` 可以运行
- 但 `cn-stock-mcp` 命令还没进当前 shell 的 PATH

这时：
- 最终用户：应优先用包安装方式
- 开发者：可继续使用 `python -m cn_stock_mcp.main ...`

---

## 2) 为什么 `cn-stock-mcp --doctor` 返回的是 `WARN`，不是 `OK`？

这是当前设计的一部分，不一定代表程序坏了。

`--doctor` 默认只做：
- Python 环境检查
- 包版本检查
- 命令是否在 PATH
- `.env` 是否存在
- token 是否能解析到
- tool registry 是否正常

它**不会默认联网**。

常见 `WARN` 包括：
- 本地源码环境里命令不在 PATH
- 你还没配置 token
- 联网检查被刻意跳过

如果你要进一步检查上游连通性，请运行：

```bash
cn-stock-mcp --doctor-network
```

---

## 3) `--doctor-network` 提示没有 token，怎么办？

说明宿主配置里还没有传：

```json
"ZHITU_TOKEN": "your-token"
```

最简单的处理方式是直接参考：
- `.mcp.sample.json`
- `docs/HOST_CONFIG_TEMPLATES.md`

---

## 4) `provider_health` 失败，通常表示什么？

最常见有三类：
- token 无效
- 网络访问上游失败
- 上游服务临时异常

建议排查顺序：
1. 先确认 token 是否正确
2. 再跑 `cn-stock-mcp --doctor-network`
3. 再单独跑：

```bash
cn-stock-mcp --tool provider_health --payload '{}'
```

如果你在公司网络、代理环境或 VPS 上运行，还要检查代理变量是否影响了上游请求。

---

## 5) 宿主能启动进程，但看不到 tools，通常是什么问题？

最常见是下面几类：
- Python 解释器不对
- 依赖装在别的虚拟环境里
- `cwd` 错了
- 源码运行时漏了 `PYTHONPATH=src`
- 宿主没有把 `env` 透传进去

如果你是源码目录方式挂载，优先对照：
- `docs/HOST_CONFIG_TEMPLATES.md`
- `docs/INTEGRATION.md`

---

## 6) 为什么不建议默认先跑 `provider_health`？

因为它会真的访问上游。

这意味着：
- 会增加延迟
- 会消耗上游额度
- 在离线/无 token 环境下没有意义

正常业务调用时：
- 直接用具体 tool 即可
- 只有在诊断上游问题时再调用 `provider_health`

---

## 7) `sector_lookup` 查“银行”“人工智能”这类板块成员时为什么报错？

因为当前 `children/members` 语义下，**必须显式传 `sector_type`**。

正确示例：

```json
{"mode":"children","sector_type":"primary","sector_name":"银行","limit":20}
```

错误示例：

```json
{"mode":"children","sector_name":"银行","limit":20}
```

---

## 8) 我是人类用户 / AI agent / 集成人员，应该分别先看哪份文档？

### 人类最终用户
1. `docs/HANDOFF_MINIMAL.md`
2. `docs/HOST_CONFIG_TEMPLATES.md`
3. `docs/FAQ.md`

### AI agent
1. `docs/AGENT_MINIMAL.md`
2. `docs/EXAMPLES_MINIMAL.md`
3. `docs/INTERFACE_SCHEMA.md`（需要详细契约时）

### 集成 / 联调人员
1. `docs/INTEGRATION.md`
2. `docs/COMPATIBILITY.md`
3. `docs/OPENCLAW_INTEGRATION.md`（如果你用 OpenClaw）

---

## 9) Windows 上为什么 `py` 会启动 Python 3.13t？

如果同时安装了普通 CPython 3.13 和 free-threaded 3.13t，Windows Python Launcher 会在 `py` 或 `py -3` 的“最新 3.x”选择中优先使用 3.13t。

本项目的 Windows/MCP 开发环境应使用普通 CPython 3.13：

```powershell
py -3.13 -V
& .\.venv\Scripts\python.exe -V
```

不要用 `py -3.13t` 运行本项目。当前 MCP 的 Windows stdio 依赖 `pywin32`，其可用发布物没有 `cp313t` wheel。完整兼容边界见 `docs/COMPATIBILITY.md`。
