# OpenClaw MCP 挂载说明

## 当前方案

项目已接入 **Python MCP SDK (`mcp[cli]`)**，并提供 stdio 启动入口：

```bash
PYTHONPATH=src python -m openclaw_stock_mcp.main --stdio
```

## 本地验证

### 列 tool
```bash
PYTHONPATH=src python -m openclaw_stock_mcp.main --list-tools
```

### 启动 stdio MCP server
```bash
PYTHONPATH=src python -m openclaw_stock_mcp.main --stdio
```

## OpenClaw 挂载思路

后续可通过 OpenClaw 的 MCP server 配置挂载该命令：

- `command`: Python 可执行文件
- `args`: `-m openclaw_stock_mcp.main --stdio`
- `cwd`: 项目目录
- `env`: 至少带上 `.env` 中需要的变量

## 注意

### STDIO 服务端约束
- 不要向 stdout 打日志
- 工具返回走 MCP 协议
- 调试日志应写 stderr 或文件

### 当前状态
- transport 已切到正式 MCP Python SDK 形态
- 仍建议在真实挂载前做一次 stdio smoke test
