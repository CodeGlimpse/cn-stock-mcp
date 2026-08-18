# Codex Template (`cn-stock-mcp`)

这页提供 **OpenAI Codex** 的单独配置模板。

适用：
- 你使用 Codex CLI 或 Codex IDE extension
- 你希望把 `cn-stock-mcp` 作为 MCP server 接进去

根据 Codex 官方 MCP 文档：
- MCP 配置写在 `config.toml`
- 全局位置：`~/.codex/config.toml`
- 项目级位置：`.codex/config.toml`（仅 trusted projects）
- CLI 和 IDE extension 共用这份配置
- 也支持直接用 `codex mcp add ...` 管理

---

## 安全前置条件

先运行 `cn-stock-mcp --init-config`，由用户只在 `%LOCALAPPDATA%\\cn-stock-mcp\\config.json` 的 `zhitu.tokens` 中填写 token。不要把 token 放进 Codex `env`、命令行参数、项目配置、聊天记录或诊断输出；Windows 专用 venv 未加入 PATH 时，把 `command` 替换为绝对 `cn-stock-mcp.exe` 路径。

## 1) 最简单：用 CLI 直接添加

```bash
codex mcp add cn-stock-mcp -- cn-stock-mcp --stdio
```

说明：
- 这是最适合已安装包方式的配置。
- 配置写入后，CLI 和 IDE extension 都会共用。

你还可以查看：

```bash
codex mcp --help
```

在 Codex TUI 里也可以用：

```text
/mcp
```

查看当前活动 MCP server。

---

## 2) 直接编辑 `~/.codex/config.toml`

写入：

```toml
[mcp_servers.cn_stock_mcp]
command = "cn-stock-mcp"
args = ["--stdio"]
enabled_tools = ["stock_search", "market_brief", "stock_snapshot", "stock_quote", "stock_history", "stock_review", "watchlist_review", "trading_calendar", "sector_review", "hot_theme_tracker"]
```

说明：
- `mcp_servers.<server-name>` 是 Codex 文档定义的配置表结构。
- `cn_stock_mcp` 是 Codex 内部使用的 server 名。

---

## 3) 项目级 `.codex/config.toml`

如果你只想让某个项目使用这个 MCP server，可在项目根目录创建：

```text
.codex/config.toml
```

写入同样的块：

```toml
[mcp_servers.cn_stock_mcp]
command = "cn-stock-mcp"
args = ["--stdio"]
enabled_tools = ["stock_search", "market_brief", "stock_snapshot", "stock_quote", "stock_history", "stock_review", "watchlist_review", "trading_calendar", "sector_review", "hot_theme_tracker"]
```

适用：
- 团队项目
- 只想在当前仓库启用
- trusted project 场景

---

## 4) 源码目录 / 虚拟环境方式

如果你拿到的是源码仓库，而不是已安装包：

```toml
[mcp_servers.cn_stock_mcp]
command = "/path/to/cn-stock-mcp/.venv/bin/python"
args = ["-m", "cn_stock_mcp.main", "--stdio"]
cwd = "/path/to/cn-stock-mcp"
env = { PYTHONPATH = "src" }
```

Codex 官方文档还提到 stdio server 可用这些字段：
- `command`
- `args`
- `env`
- `env_vars`
- `cwd`
- `experimental_environment`

但对本项目来说，默认只需要 `command` / `args` / `env`，源码方式再加 `cwd` 就够了。

---

## 5) 推荐先做的本地自检

```bash
cn-stock-mcp --init-config
cn-stock-mcp --version
cn-stock-mcp --doctor
cn-stock-mcp --doctor-network
```

如果本地 doctor 都过不去，就先别怪 Codex。

---

## 6) Codex 接入后看不到 tools

优先排查：
1. `~/.codex/config.toml` 或 `.codex/config.toml` 是否写对
2. 表名是否写成 `[mcp_servers.cn_stock_mcp]`
3. `command` / `args` / `env` / `cwd` 是否填错
4. 是否在 trusted project 外误用了项目级 `.codex/config.toml`
5. `cn-stock-mcp --doctor` 是否本地已失败

更多排查见：
- `docs/FAQ.md`
- `docs/HOST_CONFIG_TEMPLATES.md`
