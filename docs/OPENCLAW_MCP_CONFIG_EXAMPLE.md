# OpenClaw MCP 挂载配置样例

项目路径：
`/home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp`

## 方案 1：直接使用项目虚拟环境中的 Python（推荐）

前提：你已经在项目目录或独立路径准备好可运行环境，例如：
- `/tmp/openclaw-stock-mcp-venv/bin/python`

OpenClaw MCP server 配置样例：

```json
{
  "command": "/tmp/openclaw-stock-mcp-venv/bin/python",
  "args": [
    "-m",
    "openclaw_stock_mcp.main",
    "--stdio"
  ],
  "cwd": "/home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp",
  "env": {
    "PYTHONPATH": "src",
    "HTTP_PROXY": "",
    "HTTPS_PROXY": "",
    "ALL_PROXY": "",
    "http_proxy": "",
    "https_proxy": "",
    "all_proxy": ""
  }
}
```

## 方案 2：使用系统 Python + 已安装依赖

```json
{
  "command": "python3",
  "args": [
    "-m",
    "openclaw_stock_mcp.main",
    "--stdio"
  ],
  "cwd": "/home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp",
  "env": {
    "PYTHONPATH": "src",
    "HTTP_PROXY": "",
    "HTTPS_PROXY": "",
    "ALL_PROXY": "",
    "http_proxy": "",
    "https_proxy": "",
    "all_proxy": ""
  }
}
```

## OpenClaw /mcp 示例

如果你使用 OpenClaw 的 `/mcp set`：

```text
/mcp set openclaw-stock-mcp={"command":"/tmp/openclaw-stock-mcp-venv/bin/python","args":["-m","openclaw_stock_mcp.main","--stdio"],"cwd":"/home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp","env":{"PYTHONPATH":"src","HTTP_PROXY":"","HTTPS_PROXY":"","ALL_PROXY":"","http_proxy":"","https_proxy":"","all_proxy":""}}
```

## 挂载前检查

先在命令行验证：

### 列 tools
```bash
cd /home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp
. /tmp/openclaw-stock-mcp-venv/bin/activate
PYTHONPATH=src python -m openclaw_stock_mcp.main --list-tools
```

### provider 自检
```bash
cd /home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp
. /tmp/openclaw-stock-mcp-venv/bin/activate
HTTP_PROXY= HTTPS_PROXY= ALL_PROXY= http_proxy= https_proxy= all_proxy= \
PYTHONPATH=src python -m openclaw_stock_mcp.main --tool provider_health --payload '{}'
```

### stdio 启动检查
```bash
cd /home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp
. /tmp/openclaw-stock-mcp-venv/bin/activate
PYTHONPATH=src python -m openclaw_stock_mcp.main --stdio
```

若进程能保持运行且不向 stdout 打普通日志，说明适合挂载。
