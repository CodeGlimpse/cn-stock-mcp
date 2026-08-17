# OpenClaw Host Template (`cn-stock-mcp`)

这页只提供 **OpenClaw 最终可复制配置块**。

如果你只是普通最终用户，优先看：
- `docs/HANDOFF_MINIMAL.md`

如果你已经确定宿主就是 OpenClaw，直接从下面复制。

---

## 1) 仅接入 `cn-stock-mcp` MCP server

适用：
- 你只想把 `cn-stock-mcp` 挂到 OpenClaw
- 不需要仓库内附带的 OpenClaw skill adapter

优先使用 OpenClaw CLI 添加并实时探测：

```bash
openclaw mcp add cn-stock-mcp --command cn-stock-mcp --arg --stdio
openclaw mcp doctor cn-stock-mcp --probe
```

也可以将下面内容合并到 OpenClaw 配置：

```json5
{
  mcp: {
    servers: {
      "cn-stock-mcp": {
        command: "cn-stock-mcp",
        args: ["--stdio"],
        transport: "stdio",
        enabled: true,
        toolFilter: {
          include: ["stock_search", "market_brief", "stock_snapshot", "stock_quote", "stock_history", "stock_review", "watchlist_review", "trading_calendar", "sector_review", "hot_theme_tracker"]
        }
      }
    }
  }
}
```

说明：
- 这是最适合“已安装包”的 OpenClaw 配置。
- 你也可以先运行：

```bash
cn-stock-mcp --doctor
cn-stock-mcp --doctor-network
```

确认安装与 token 正常。

---

## 2) OpenClaw + 仓库内 skill adapter

适用：
- 你除了挂 MCP server
- 还想启用仓库内的 `skills/newsbot-stock-routing/`

将下面内容合并到：
- `~/.openclaw/openclaw.json`

```json5
{
  mcp: {
    servers: {
      "cn-stock-mcp": {
        command: "cn-stock-mcp",
        args: ["--stdio"],
        transport: "stdio",
        enabled: true,
        toolFilter: {
          include: ["stock_search", "market_brief", "stock_snapshot", "stock_quote", "stock_history", "stock_review", "watchlist_review", "trading_calendar", "sector_review", "hot_theme_tracker"]
        }
      }
    }
  },
  skills: {
    load: {
      extraDirs: [
        "/path/to/cn-stock-mcp/skills"
      ]
    },
    entries: {
      "newsbot-stock-routing": {
        enabled: true
      }
    }
  }
}
```

把：
- `/path/to/cn-stock-mcp/skills`

替换成你的实际仓库路径，例如：

```json5
"/home/openclaw/桌面/openclaw/codes/cn-stock-mcp/skills"
```

---

## 3) 如果你是源码目录运行而不是包安装

当 `cn-stock-mcp` 命令还没有直接进入 PATH 时，可改成：

```json5
{
  mcp: {
    servers: {
      "cn-stock-mcp": {
        command: "/path/to/cn-stock-mcp/.venv/bin/python",
        args: ["-m", "cn_stock_mcp.main", "--stdio"],
        cwd: "/path/to/cn-stock-mcp",
        transport: "stdio",
        env: {
          PYTHONPATH: "src"
        }
      }
    }
  }
}
```

说明：
- 这是 OpenClaw 里的“源码 / 虚拟环境挂载法”。
- 更适合开发阶段，不如包安装方式简洁。

---

## 4) OpenClaw 验证命令

```bash
openclaw mcp doctor cn-stock-mcp --probe
openclaw mcp status --verbose
openclaw mcp reload
```

如果启用了仓库内 skill adapter，再运行：

```bash
openclaw skills list --eligible
openclaw skills info newsbot-stock-routing
```

如果只是验证 MCP server 本体，先运行：

```bash
cn-stock-mcp --list-tools
cn-stock-mcp --tool provider_health --payload '{}'
```

---

## 5) 什么时候该用哪种 OpenClaw 模式？

### 只要工具能力
用：
- **仅接入 MCP server**

### 还想让 OpenClaw 内置路由规则更懂中国股市任务
用：
- **OpenClaw + 仓库内 skill adapter**

### 正在开发 / 调试源码
用：
- **源码目录运行方式**
