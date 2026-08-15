# ERROR_MODEL.md

`cn-stock-mcp` 的 tool 调用统一返回 envelope：

```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": {
    "schema_version": "v1",
    "request_id": "req_xxx",
    "tool": "stock_quote",
    "freshness": {
      "observed_at": "2026-08-14T08:00:00Z",
      "as_of": "2026-08-14T07:59:55Z",
      "basis": "provider_timestamp",
      "status": "realtime",
      "age_seconds": 5
    },
    "data_quality": {
      "schema": "data_quality_v1",
      "score": 100,
      "label": "high",
      "flags": []
    }
  }
}
```

失败时：

```json
{
  "success": false,
  "data": null,
  "error": {
    "error_code": "INVALID_ARGUMENT",
    "message": "Invalid request payload",
    "retryable": false,
    "provider": null
  },
  "meta": {
    "schema_version": "v1",
    "request_id": "req_xxx",
    "tool": "stock_quote"
  }
}
```

---

## 1. 统一字段约定

### 顶层字段
- `success`: 本次 tool 调用是否成功
- `data`: 成功时的业务数据；失败时固定为 `null`
- `error`: 失败时的结构化错误；成功时固定为 `null`
- `meta`: 协议与追踪信息

### meta 字段
- `schema_version`: 当前响应协议版本，现为 `v1`
- `request_id`: 本次 tool 调用唯一请求 ID，用于串联日志
- `tool`: 被调用的 tool 名称
- `freshness`: 成功响应的数据新鲜度元数据；失败响应不保证存在
- `data_quality`: 成功响应的数据质量启发式评分；包含 `schema`、`score`、`label`、`flags`、`factors`，不表示投资信心
- `provider_used` / `fallback_chain` / `latency_ms`: 成功响应中的稳定可观测字段；若业务 payload 的 `data.meta` 提供这些字段，统一响应层会同步提升到顶层 `meta`
- `used_fallback` / `final_provider` / `attempted`: provider fallback 过程的可观测字段，存在时同步提升到顶层 `meta`

为保持兼容，业务 `data.meta` 中的原字段不会被删除；调用方可优先读取顶层 `meta`，并对旧响应保留 `data.meta` 回退读取。

### freshness 字段
- `observed_at`: server 完成获取/组装响应的 UTC 时间
- `as_of`: 从业务 payload 识别出的最新源时间/日期，无法识别时为 `null`
- `basis`: `provider_timestamp`、`source_date` 或 `unknown`
- `status`: `realtime`（源提供时间级字段）、`dated`（仅有日期级字段）或 `unknown`
- `age_seconds`: 观察时间与 `as_of` 的非负秒差；`as_of` 不可识别时为 `null`

`status=realtime` 表示源数据带有时间级字段，不承诺数据一定处于交易时段；调用方仍应结合 `as_of`、交易日历和业务字段判断是否适合当前决策。

### data_quality 字段

统一成功响应的 `meta.data_quality` 使用 `data_quality_v1`，综合 provider fallback、部分失败、stale、数据年龄、显式缺失字段、异常数值和空结果。`label` 只有 `high`、`medium`、`low` 三档；它是数据可用性提示，不是交易信号、投资建议或模型置信度。

### error 字段
- `error_code`: 稳定错误码，供调用方做程序分支
- `message`: 面向人类的错误说明
- `retryable`: 是否建议自动重试
- `provider`: 触发错误的 provider；无法确认时为 `null`
- `details`: 仅部分错误存在（如 `INVALID_ARGUMENT`）

---

## 2. 错误码字典

### TOOL_NOT_FOUND
- 含义：请求的 tool 未注册
- 典型来源：server registry
- `retryable`: `false`
- 调用方建议：
  - 检查 tool 名称拼写
  - 检查服务版本是否支持该 tool
  - 不要自动重试

### INVALID_ARGUMENT
- 含义：请求参数不合法，或 provider 侧识别到参数错误
- 典型来源：
  - pydantic 参数校验失败
  - provider 对模式/字段做额外校验（如缺少 `trade_date` / `sector_name`）
- `retryable`: `false`
- 调用方建议：
  - 直接提示用户修正参数
  - 使用 `details` 或 `message` 构造提示
  - 不要自动重试

### PROVIDER_AUTH_FAILED
- 含义：provider 鉴权失败，或 token 缺失/无效
- 典型来源：智兔 token 缺失、401/403
- `retryable`: `false`
- 调用方建议：
  - 提示配置错误
  - 检查 `.env` / token 文件
  - 不要自动重试，除非配置已更新

### PROVIDER_TIMEOUT
- 含义：上游 provider 请求超时
- 典型来源：HTTP timeout
- `retryable`: `true`
- 调用方建议：
  - 可以短次数自动重试
  - 若支持 fallback，则优先切换 provider
  - 记录 `request_id` 便于排障

### PROVIDER_UNAVAILABLE
- 含义：provider 当前不可用、远端异常、依赖缺失、上游断开等
- 典型来源：
  - HTTP 5xx / 网络异常
  - AKShare 上游接口异常
  - 本地 akshare 未安装
- `retryable`: 通常为 `true`，但少数实现可为 `false`
- 调用方建议：
  - 若 `retryable=true`，可短次数重试或换源
  - 若已有 fallback，优先采用 fallback 结果
  - 若 `retryable=false`，按失败处理并提示

### PROVIDER_CIRCUIT_OPEN
- 含义：某个不稳定的 provider endpoint 已连续失败，进程内熔断器暂时拒绝继续访问
- 典型来源：AKShare 资金流 endpoint 在达到失败阈值后再次调用
- `retryable`: `true`
- 调用方建议：
  - 短时间内不要立即密集重试，等待熔断恢复窗口
  - 如果业务允许，改用其他 tool/provider 或使用显式允许的 stale 缓存
  - 记录 endpoint、`request_id` 和错误消息

### UNSUPPORTED_INTERVAL
- 含义：当前 provider / route 不支持指定周期
- 典型来源：
  - AKShare minimal history 仅支持 `1d`
  - provider 对技术指标周期支持有限
- `retryable`: `false`
- 调用方建议：
  - 引导用户改用支持的 interval
  - 不要自动重试

### UNSUPPORTED_SEC_TYPE
- 含义：当前 provider / route 不支持该证券类型
- 典型来源：
  - AKShare quote 未实现
  - Zhitu history 仅支持 index route
- `retryable`: `false`
- 调用方建议：
  - 引导用户更换 tool / sec_type / provider
  - 不要自动重试

### UNSUPPORTED_MARKET
- 含义：当前 provider / route 不支持该市场或代码路由
- 典型来源：
  - Zhitu 对特定市场行情/盘口未实现
  - AKShare 对相关接口未实现
- `retryable`: `false`
- 调用方建议：
  - 引导用户更换标的或 provider
  - 不要自动重试

### INTERNAL_ERROR
- 含义：未被 provider error 模型覆盖的内部异常
- 典型来源：代码缺陷、序列化异常、未知异常
- `retryable`: `false`
- 调用方建议：
  - 记录 `request_id`
  - 不建议盲目重试
  - 进入排障流程

---

## 3. retryable 解释规则

`retryable` 只表达“技术上是否值得自动再试一次”，不等于“最终一定成功”。

建议调用方策略：

- `retryable = false`
  - 默认不要自动重试
  - 优先提示用户修正参数 / 配置 / 使用方式

- `retryable = true`
  - 可做有限次数重试（建议 1~2 次）
  - 如支持 fallback，优先换 provider 而不是原地硬重试
  - 保留 `request_id` 进入日志排查

---

## 4. fallback 与错误处理建议

### 主源失败，fallback 成功
此时整体 `success=true`，不会暴露顶层 `error`；调用方应查看业务 `data.meta` 中的 fallback 信息，例如：
- `used_fallback`
- `selected_primary`
- `final_provider`
- `attempted`

这类场景说明：
- 本次用户请求已经成功
- 但主 provider 可能存在短暂异常
- 可在监控侧统计 fallback 命中率

### 主源失败，fallback 也失败
此时整体 `success=false`，顶层 `error` 表示最终失败原因。
调用方应：
- 展示结构化错误
- 记录 `request_id`
- 视 `retryable` 决定是否重试

### 资金流 stale-if-error

`capital_flow` 的 `allow_stale` 默认为 `false`。上游失败时，默认返回原始 provider 错误，不把旧缓存伪装成成功；只有请求显式传 `allow_stale=true`、错误可重试且缓存未超过允许年龄时，才返回成功结果。此时业务 `data.meta` 必须包含：

- `stale: true`
- `stale_age_seconds`: 旧缓存年龄（秒）
- `provider_used: "cache"`

调用方应向用户说明这是旧数据，并结合 `stale_age_seconds` 判断是否可接受。

---

## 5. 调用方推荐决策表

| error_code | retryable | 推荐动作 |
|---|---:|---|
| TOOL_NOT_FOUND | false | 检查版本/工具名，不重试 |
| INVALID_ARGUMENT | false | 提示用户修参数，不重试 |
| PROVIDER_AUTH_FAILED | false | 检查 token/配置，不重试 |
| PROVIDER_TIMEOUT | true | 可重试 1~2 次，优先换源 |
| PROVIDER_UNAVAILABLE | true/false | 若可重试则换源或短重试，否则直接失败 |
| PROVIDER_CIRCUIT_OPEN | true | 等待熔断恢复，避免密集重试；必要时改用缓存或其他源 |
| UNSUPPORTED_INTERVAL | false | 改 interval |
| UNSUPPORTED_SEC_TYPE | false | 改 sec_type / tool / provider |
| UNSUPPORTED_MARKET | false | 改市场 / 标的 / provider |
| INTERNAL_ERROR | false | 记录 request_id，进入排障 |

---

## 6. 示例

### 6.1 参数错误
```json
{
  "success": false,
  "data": null,
  "error": {
    "error_code": "INVALID_ARGUMENT",
    "message": "Invalid request payload",
    "retryable": false,
    "provider": null,
    "details": []
  },
  "meta": {
    "schema_version": "v1",
    "request_id": "req_xxx",
    "tool": "stock_history"
  }
}
```

### 6.2 上游超时
```json
{
  "success": false,
  "data": null,
  "error": {
    "error_code": "PROVIDER_TIMEOUT",
    "message": "Zhitu request timed out: /hz/real/ssjy/000001.SH",
    "retryable": true,
    "provider": null
  },
  "meta": {
    "schema_version": "v1",
    "request_id": "req_xxx",
    "tool": "stock_quote"
  }
}
```

### 6.3 主源失败但 fallback 成功
```json
{
  "success": true,
  "data": {
    "items": [],
    "meta": {
      "per_symbol": [
        {
          "symbol": "600519.SH",
          "selected_primary": "zhitu",
          "attempted": ["zhitu", "akshare"],
          "final_provider": "akshare",
          "used_fallback": true
        }
      ]
    }
  },
  "error": null,
  "meta": {
    "schema_version": "v1",
    "request_id": "req_xxx",
    "tool": "stock_quote"
  }
}
```

---

## 7. 当前实现边界

- 当前错误模型已覆盖 server 层与 provider 层的主要失败路径
- `provider` 字段目前不一定总能精确回填到最终失败源，必要时结合 `request_id` 查日志
- 未来如新增错误码，应保持：
  1. 旧错误码语义不变
  2. `schema_version` 变更前尽量只追加，不破坏既有字段
