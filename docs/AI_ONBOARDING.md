# AI Onboarding (`cn-stock-mcp`)

这页写给两类人：

1. 想把 `cn-stock-mcp` 接到自己的 AI agent / MCP host 的人
2. 想教自己的 agent **更稳、更省 token、更少踩坑** 地使用这个 MCP 的人

这不是宿主配置模板页；宿主配置请看：
- `HOST_CONFIG_TEMPLATES.md`

这页重点讲：
- 这个 MCP 适合解决什么问题
- agent 默认该怎么选 tool
- 哪些坑最常见
- 什么时候该用 MCP，什么时候不该用 skill adapter

---

## 1) 先理解：这个项目的主产品是什么？

`cn-stock-mcp` 的主产品是：
- **一个 MCP server**

它不是“给所有 agent 都带一份 skill 包”的项目。

大多数 agent / host 的正确使用方式是：
1. 把 `cn-stock-mcp` 接成 MCP server
2. 再给 agent 少量规则 / examples / hints

只有少数平台（例如 OpenClaw）才会额外用到 skill adapter。

如果你在找 skill 在哪，先看：
- `AGENT_AND_SKILL_MAP.md`

---

## 2) 这个 MCP 适合回答什么问题？

它适合中国证券市场数据类问题，例如：

- 今天 A 股市场简报
- 某个板块为什么强/弱
- 板块轮动怎么看
- 某只股票现在多少钱
- 某只股票最近走势怎样
- 技术指标（MA / MACD / RSI 等）
- 某个板块有哪些成员股
- 轻量市场股池快照
- 热点主线 / 复盘

不适合的则是：
- 一般国际新闻
- 公司舆情核验
- 无需市场数据的纯文本问答

---

## 3) agent 默认应该怎么选 tool？

这是最重要的一条：

> **先用最轻 tool，够回答就停。**

默认原则：
1. 先选最轻 tool，再升级到更重 tool
2. 名称/代码不确定，先 `stock_search`
3. 非诊断场景不要先跑 `provider_health`
4. 默认小参数：`limit/top_n=3~5`
5. 不要一开始就上“全市场扫描”或大 payload

---

## 4) 高频问题的最短路由

### 市场简报 / 收盘复盘
优先：
- `market_brief`

### 热点主线
优先：
- `hot_theme_tracker`

### 单板块复盘
优先：
- `sector_review`

### 多板块比较 / 轮动
优先：
- `sector_rotation_review`

### 单股复盘
优先：
- `stock_review`

### 实时价格
优先：
- `stock_quote`

### 历史走势
优先：
- `stock_history`

### 技术指标
优先：
- `technical_indicator`

### 轻量股池快照
优先：
- `market_pool`

### 板块成员
优先：
- `sector_lookup`

### 代码 / 名称检索
优先：
- `stock_search`

---

## 5) 最容易浪费 token 的地方

### 1. 不确定代码时直接猜
错误方式：
- 直接猜 symbol

正确方式：
- 先 `stock_search`

### 2. 简单问题一上来就跑重工具
例如：
- 只是想看当前价格，却直接跑复杂复盘工具

### 3. 默认把 limit 开很大
默认建议：
- `limit=5`
- `top_n=3`

只有用户明确要求更全时再放大。

### 4. 把单板块问题升级成多板块轮动
如果用户只问一个板块：
- 优先 `sector_review`
- 不要默认上 `sector_rotation_review`

### 5. 为了“更完整”擅自扩大 universe
例如：
- `stock_candidate_scan`
- `watchlist_review`

都应该优先收窄 symbols / pools / sectors。

---

## 6) 最容易踩坑的契约

### `sector_lookup`
这是最容易踩坑的一个。

关键规则：
- `mode=list, sector_type=concept` → 概念板块列表
- `mode=list, sector_type=primary` → 一级板块列表
- `mode=children|members` → **成员股列表**，不是子板块
- `mode=children|members` 时：**必须显式传 `sector_type=primary|concept`**

正确示例：

```json
{"mode":"children","sector_type":"primary","sector_name":"银行","limit":20}
```

错误示例：

```json
{"mode":"children","sector_name":"银行","limit":20}
```

---

## 7) 什么时候该用 `provider_health`？

只在这些场景用：
- 怀疑 token 不对
- 怀疑上游连不通
- 怀疑 provider 故障
- 在做诊断 / 部署验证

平时回答正常业务问题时：
- **不要默认先跑 `provider_health`**

因为它会：
- 增加延迟
- 消耗上游请求
- 在离线 / 无 token 情况下没有意义

---

## 8) skill 和 MCP 到底怎么分工？

### 大多数平台
只需要：
- MCP 配置
- 少量规则 / 示例

### 少数平台
还会额外用 skill adapter。

本仓库里目前真正成型的 skill adapter 主要是：
- `skills/newsbot-stock-routing/SKILL.md`

它是给 OpenClaw / news agent 用的，不是“所有 agent 通用 skill”。

---

## 9) 如果你要教 agent 使用这个 MCP，最少需要给它什么？

至少给这 3 样：

1. **MCP 接入配置**
   - 看 `HOST_CONFIG_TEMPLATES.md`

2. **最小调用规则**
   - 看 `AGENT_MINIMAL.md`
   - 看 `.agent-hints.json`

3. **最小 examples**
   - 看 `EXAMPLES_MINIMAL.md`

如果还需要详细参数和契约，再补：
- `INTERFACE_SCHEMA.md`

---

## 10) 推荐阅读顺序

### 人类集成人员
1. `START_HERE.md`
2. `HANDOFF_MINIMAL.md`
3. `HOST_CONFIG_TEMPLATES.md`
4. `AI_ONBOARDING.md`
5. `AGENT_AND_SKILL_MAP.md`

### AI agent 作者
1. `AGENT_MINIMAL.md`
2. `EXAMPLES_MINIMAL.md`
3. `INTERFACE_SCHEMA.md`
4. `.agent-hints.json`

### OpenClaw 使用者
1. `OPENCLAW_HOST_TEMPLATE.md`
2. `OPENCLAW_INTEGRATION.md`
3. `skills/newsbot-stock-routing/SKILL.md`
