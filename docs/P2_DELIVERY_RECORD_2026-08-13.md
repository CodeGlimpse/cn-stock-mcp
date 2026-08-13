# P2 交付记录：实时数据与兼容性验证

日期：2026-08-13

## 验证环境

- 操作系统：Windows
- Python：普通 CPython 3.13.2，GIL enabled
- ABI：`cp313-win_amd64`
- 项目解释器：`.venv\Scripts\python.exe`
- `mcp`：2.0.0
- `pywin32`：312
- token：已从项目本地配置解析；本记录不保存或回显 token 值

## 验证结果

| 范围 | 命令/检查 | 结果 |
| --- | --- | --- |
| 依赖完整性 | `.venv\Scripts\python.exe -m pip check` | 通过 |
| 实时 smoke | `pytest -q tests\live\test_smoke_transport.py tests\live\test_smoke_provider.py` | 13/13 通过 |
| extended live | `pytest -q tests\live\test_live_extended.py` | 3/3 通过 |
| 日期兼容 | `pytest -q tests\test_zhitu_market_pool.py` | 3/3 通过 |
| MCP stdio | initialize、`tools/list`、无效参数调用 | 通过；52 个工具，错误码 `INVALID_ARGUMENT` |
| 上游健康检查 | `.venv\Scripts\cn-stock-mcp.exe --doctor-network` | `provider_health` 通过 |
| 完整非 live 回归 | `pytest -q -p no:cacheprovider -m "not live"` | 472 通过，16 个 live 用例排除 |
| Provider 复用回归 | `tests\test_provider_router.py tests\test_provider_enabled_switch.py` | 14/14 通过 |
| 聚焦 transport/date 回归 | `tests\test_zhitu_market_pool.py tests\test_mcp_transport.py` | 8/8 通过 |

## 性能修复

根因是多个 UseCase 各自创建 `ProviderRouter`，每个 Router 又重复构造 Zhitu HTTP client；Windows 下反复加载 SSL 证书使 MCP registry 构建明显变慢。

提交 `434a84b perf: reuse providers across routers` 后，ProviderRouter 在进程内共享 AKShare/Zhitu Provider：

| 指标 | 修复前 | 修复后 |
| --- | ---: | ---: |
| 首次 `create_server()` | 约 17.9 秒 | 约 0.33 秒 |
| 后续 `create_server()` | 重复初始化 | 约 0.06 秒 |
| 聚焦测试总耗时 | 约 109 秒 | 约 4 秒 |

共享 Provider 同时保留了 HTTP 连接池、token 健康状态和 Provider 缓存，实时 smoke 验证未出现回归。

## 已确认的兼容行为

- Zhitu 市场池接受 `YYYY-MM-DD` 和 `YYYYMMDD` 输入，并统一以 `YYYY-MM-DD` 请求上游。
- 普通 CPython 3.13.2 下 MCP stdio 进程可以完成初始化、工具枚举和错误响应。
- Python 3.13t/free-threaded 不作为当前 Windows/MCP 开发环境；`pywin32` 没有可用的 `cp313t` wheel。
- Windows 同时安装两个 Python 3.13 构建时，应使用 `py -3.13` 或项目 `.venv`，不要使用默认 `py` / `py -3`。

## 环境性说明

- 受限沙箱首次执行实时测试时，网络请求返回 Windows `WinError 10013`；在允许访问上游接口的验证环境中重跑同一命令后通过。这是执行环境网络权限问题，不是项目代码失败。
- `--doctor-network` 仍可能显示 `cn-stock-mcp` 未加入 PATH；源码开发环境可直接使用 `.venv\Scripts\cn-stock-mcp.exe`。
- pytest 可能因 `.pytest_cache` 写权限不足显示 `PytestCacheWarning`；不影响测试结果。

## 结论

P2 实时数据与兼容性验证通过。当前候选开发环境为普通 CPython 3.13.2 项目虚拟环境；实时上游验证依赖可访问 Zhitu/AKShare 网络接口和有效 token。

交付提交：

- `7a35995 docs: record P2 validation and runtime compatibility`
- `434a84b perf: reuse providers across routers`
