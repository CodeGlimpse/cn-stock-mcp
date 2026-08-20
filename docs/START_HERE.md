# Start Here (`cn-stock-mcp`)

如果你是第一次打开这个仓库，先看这页。

这不是一个“只有开发者能看懂”的代码仓库；它现在更接近一个 **可安装、可自检、可接入多种 AI agent / MCP host 的工具项目**。

---

## 这个项目到底是什么？

`cn-stock-mcp` 的核心交付物是：

- **一个 MCP server**

它提供中国证券市场相关的数据能力，例如：
- 市场简报
- 板块复盘
- 个股复盘
- 实时行情
- 历史走势
- 技术指标
- 股池 / 热点 / 轮动分析

你可以把它理解成：

> 一个给 AI agent / MCP host 调用的中国股票市场数据工具。

---

## 你应该看哪份文档？

### 对外介绍与客户部署

- `PRODUCT_OVERVIEW.md`：产品定位、AI 分析亮点和典型使用场景
- `CUSTOMER_DEPLOYMENT.md`：固定版本安装、智兔 token 获取、Host 接入、排障和免责声明

### 1) 你是普通用户，只想先装起来
按这个顺序看：

1. `HANDOFF_MINIMAL.md`
2. `HOST_CONFIG_TEMPLATES.md`
3. `FAQ.md`

这是最短路径。

---

### 2) 你已经知道自己用什么 AI 工具 / MCP host
直接看对应模板：

- OpenClaw → `OPENCLAW_HOST_TEMPLATE.md`
- Claude Desktop → `CLAUDE_DESKTOP_TEMPLATE.md`
- Claude Code → `CLAUDE_CODE_TEMPLATE.md`
- Continue → `CONTINUE_TEMPLATE.md`
- VS Code → `VSCODE_TEMPLATE.md`
- Cursor → `CURSOR_TEMPLATE.md`
- Cline → `CLINE_TEMPLATE.md`
- Windsurf → `WINDSURF_TEMPLATE.md`
- Hermes → `HERMES_TEMPLATE.md`
- Codex → `CODEX_TEMPLATE.md`

---

### 3) 你在找“给各个 agent 用的 skill 在哪里”
先看：

- `AGENT_AND_SKILL_MAP.md`

这页专门回答：
- 哪些 agent / host 只是用 MCP 配置
- 哪些平台才有仓库内 skill
- skill 文件具体在哪个路径

---

### 4) 你是开发 / 集成 / 联调人员
按这个顺序看：

1. `INTEGRATION.md`
2. `COMPATIBILITY.md`
3. `IMPLEMENTATION_STATUS.md`
4. `INTERFACE_SCHEMA.md`

---

## 最短使用步骤

### 第 1 步：安装

```bash
python -m pip install cn-stock-mcp==0.2.0
```

随后运行 `cn-stock-mcp --init-config`，由用户在 `%LOCALAPPDATA%\cn-stock-mcp\config.json` 手动填写 token。不要把 token 放进 Host 配置。

### 第 2 步：自检

```bash
cn-stock-mcp --version
cn-stock-mcp --doctor
```

如果你已经有 token，再继续：

```bash
cn-stock-mcp --doctor-network
```

### 第 3 步：挂到你的 MCP host

最小配置长这样：

```json
{
  "mcpServers": {
    "cn-stock-mcp": {
      "command": "cn-stock-mcp",
      "args": ["--stdio"]
    }
  }
}
```

如果你不确定该把这段放到哪里，回到：
- `HOST_CONFIG_TEMPLATES.md`

---

## 一个容易误解的点

很多人会把 **MCP server** 和 **skill** 混在一起。

在这个仓库里：

- **主产品是 MCP server**
- **大多数 agent / host 只需要 MCP 配置，不需要仓库内 skill**
- **仓库内真正附带的 skill 主要是 OpenClaw 用的**

也就是说：

- Claude Desktop / Cursor / Cline / VS Code / Continue / Codex 这些，通常是**接 MCP**
- 不是都要从这个仓库里找一个“skill 文件”再装上

如果你想看清楚这件事，直接看：
- `AGENT_AND_SKILL_MAP.md`
