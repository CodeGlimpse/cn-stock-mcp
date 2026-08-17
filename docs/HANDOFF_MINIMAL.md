# Handoff Minimal (`cn-stock-mcp`)

如果你是第一次接触这类工具，只做下面 3 步：

## 第 1 步：安装

```bash
python -m pip install cn-stock-mcp==0.2.0
```

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

## 第 3 步：把下面配置粘贴到你的 MCP host

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

---

## 接下来只在需要时再看

- `docs/HOST_CONFIG_TEMPLATES.md`：不同 host 的复制即用模板
- `docs/FAQ.md`：常见错误与排查
- `docs/EXAMPLES_MINIMAL.md`：最小调用示例
- `docs/COMPATIBILITY.md`：不同 host / skill host 的兼容说明
- `docs/INTEGRATION.md`：更完整的挂载与联调说明
