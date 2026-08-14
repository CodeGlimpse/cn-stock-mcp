# P2 交付记录：接口文档与数据新鲜度

日期：2026-08-14

## 交付内容

- `docs/INTERFACE_SCHEMA.md` 已同步当前实际注册的 52 个 MCP tool。
- `docs/ERROR_MODEL.md` 已补充成功响应 `meta.freshness` 契约。
- 成功 tool 响应的顶层 `meta` 新增：
  - `observed_at`：服务端完成获取/组装响应的 UTC 时间
  - `as_of`：从业务数据识别出的最新源时间或日期
  - `basis`：`provider_timestamp`、`source_date` 或 `unknown`
  - `status`：`realtime`、`dated` 或 `unknown`
  - `age_seconds`：可计算时的非负年龄秒数

## 设计边界

- 只追加 envelope 元数据，不改变现有 `data` 结构。
- 无源时间字段时返回 `status=unknown`，不把请求完成时间伪装成数据产生时间。
- `observed_at` 表示本次服务端返回时间；缓存命中时不代表底层数据重新从上游抓取。
- `status=realtime` 只表示源提供了时间级字段，仍需结合交易日历和业务语义判断是否适合实时决策。

## 验证

| 范围 | 命令/检查 | 结果 |
| --- | --- | --- |
| freshness / envelope | `tests\test_response_envelope.py` | 5 passed |
| MCP transport 兼容性 | `tests\test_mcp_transport.py` | 7 passed |
| P1 + freshness 聚焦回归 | 34 tests | 34 passed |
| 非 live 回归 | `-m "not live" -k "not test_market_pool_uses_cache_on_second_call"` | 482 passed，23 deselected |
| 文档清单 | 实际 `mcp_server.py` 注册项与 `INTERFACE_SCHEMA.md` 对照 | 52 项一致 |

完整非 live 套件中仍有一个既有环境性限制：`test_market_pool_uses_cache_on_second_call` 会在缓存断言前访问 `finance.sina.com.cn`，受限网络下返回 WinError 10013；本次未修改该无关路径。
