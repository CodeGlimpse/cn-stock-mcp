# cn-stock-mcp

中国证券市场行情 MCP 服务。核心交付物是**通用 MCP server**；OpenClaw skill 只是仓库内附带的一个平台适配层。

> **给 AI agent：** 不要默认通读本 README。先读 `docs/AGENT_MINIMAL.md`，需要最小示例时再读 `docs/EXAMPLES_MINIMAL.md`；只有在需要完整背景、长样例或发布说明时再展开本文件。

## 当前状态

当前已具备：
- MCP Python SDK（FastMCP）stdio transport
- AKShare / 智兔双源与 fallback
- 核心市场数据 / 复盘 / 板块 / 技术指标 / 股池能力
- 打包构建、非 live 回归、provider_health 自检

详细能力与限制见：`docs/IMPLEMENTATION_STATUS.md`

## 文档导航

- `docs/README_DOCS.md`：文档总览与阅读顺序
- `docs/HANDOFF_MINIMAL.md`：给最终用户 / 本地 AI agent 的最短接入说明
- `docs/COMPATIBILITY.md`：MCP-only / rules-based / skill-based host 兼容说明
- `docs/AGENT_MINIMAL.md`：给 AI agent 的最小入口
- `docs/EXAMPLES_MINIMAL.md`：最小可工作的调用示例
- `docs/EXAMPLES_FULL.md`：完整调用样例（按需展开）
- `docs/IMPLEMENTATION_STATUS.md`：当前实现状态与限制（事实源）
- `docs/INTERFACE_SCHEMA.md`：对外输入/输出契约与路由约束
- `docs/ERROR_MODEL.md`：统一错误码与 retry/fallback 语义
- `docs/INTEGRATION.md`：通用 MCP 挂载、自检与联调清单
- `docs/OPENCLAW_INTEGRATION.md`：OpenClaw 专属适配说明

## 快速开始

### 安装依赖

```bash
pip install -e .
```

### 开发环境安装（推荐）

```bash
# 方式1：使用 Makefile
make setup-dev

# 方式2：使用 requirements-dev
pip install -r requirements-dev.txt
```

### 运行测试

```bash
# 推荐：使用项目虚拟环境，避免系统 Python 依赖缺失
.venv/bin/python -m pytest -q -m "not live"

# 仅跑 live smoke（tests/live/ 中标记为 smoke 的高信号测试）
bash scripts/smoke_live.sh

# 默认：仅跑稳定回归（不含 live 网络测试）
make test

# 跑全部测试（含 live）
make test-all
```

补充：
- `tests/live/test_smoke_transport.py`：MCP tool / transport 层 smoke
- `tests/live/test_smoke_provider.py`：少量 provider 直连 smoke
- `tests/live/test_live_extended.py`：更重、更脆的 live 扩展回归
- `tests/live/conftest.py` 提供 `recent_trade_date` fixture，避免 live case 写死旧交易日
- `.github/workflows/live-smoke.yml` 提供可选的 GitHub Actions 手动/定时 smoke job

### 配置

```bash
cp .env.example .env
```

智兔 token 支持两种方式：

1. 直接写 `.env`
2. 写入 `config/zhitu_tokens.json`

说明：
- `config/zhitu_tokens.json` 支持配置多个 token
- 当前版本会按 `default` 优先顺序加载多个 token
- 当某个智兔 token 遇到 `429` 限流时，会自动尝试切换到下一个可用 token

### 列出已注册 tools

```bash
PYTHONPATH=src python -m cn_stock_mcp.main --list-tools
```

### 调用单个 tool

```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_quote --payload '{"symbols":["000001.SH"],"sec_type":"index"}'
```

### 返回结构（统一 envelope）

所有 `--tool` / MCP 调用统一返回顶层字段：

- `success`
- `data`
- `error`
- `meta`

详细结构见：
- `docs/INTERFACE_SCHEMA.md`
- `docs/ERROR_MODEL.md`

### 调用样例导航

为避免 README 过长，调用样例已拆分：

- 最小样例：`docs/EXAMPLES_MINIMAL.md`
- 完整样例：`docs/EXAMPLES_FULL.md`

AI agent 默认先看最小样例；只有在需要更完整 payload 模板时再看完整样例。

### 运行 smoke test

```bash
PYTHONPATH=src python scripts/smoke_test.py
bash scripts/smoke_live.sh
```

更完整的联调与验收顺序见：`docs/INTEGRATION.md`

### 运行 provider 自检

```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool provider_health --payload '{}'
```

更多自检/挂载说明见：`docs/INTEGRATION.md`

## 通用 MCP 接入

最小 MCP 配置示例见：
- `.mcp.sample.json`
- `docs/HANDOFF_MINIMAL.md`
- `docs/INTEGRATION.md`

如果宿主还支持 rules / instructions / skills，再看：
- `docs/COMPATIBILITY.md`

## OpenClaw adapter

仓库内附带 OpenClaw skill adapter：
- `skills/newsbot-stock-routing/`

OpenClaw 专属加载与验证说明见：
- `docs/OPENCLAW_INTEGRATION.md`
- `skills/MIGRATION_NEWSBOT_SKILL.md`

## 说明

### 数据源 API 文档入口
- 统一索引见：`docs/INTERFACE_SCHEMA.md`（“上游数据源文档入口”章节）

### 股票历史的当前实现
- `stock_history(stock)` 当前通过 **AKShare 腾讯历史接口** 实现
- 周/月线由日线聚合
- 详细字段口径见：`docs/INTERFACE_SCHEMA.md`

### sector_lookup 当前语义
- `mode=list, sector_type=concept`：概念板块列表
- `mode=list, sector_type=primary`：一级板块列表
- `mode=children`（或兼容 `members`）：查询板块成员股
  - **必须显式传 `sector_type`**
  - `sector_type=primary`：按一级板块语义解析后查询
  - `sector_type=concept`：按概念板块语义解析后查询
- 因此，`children/members` 查询“医药 / 人工智能 / 银行”这类人类友好名称时，必须显式传 `sector_type`

### Transport 状态
当前使用 **MCP Python SDK（FastMCP）stdio transport**；本地 `--tool` / `--list-tools` 仅保留给调试与 smoke test。

### 事件与板块快照样例

已下沉到：`docs/EXAMPLES_FULL.md`

### 榜单工具统一语义（v1）
- `return_mode=full`：返回过滤+排序后全量
- `return_mode=ranked_only`：仅返回 `top_n`
- 统一 `meta`：`filtered_from / filtered_count / ranked_count`
