# Handoff Minimal (`cn-stock-mcp`)

如果你是第一次接触这类工具，只做下面 3 步：

## 第 1 步：安装

```bash
python -m pip install cn-stock-mcp
```

## 第 2 步：先确认程序装好了

```bash
cn-stock-mcp --version
cn-stock-mcp --doctor
```

如果你已经有 token，再继续：

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
      "args": ["--stdio"],
      "env": {
        "ZHITU_TOKEN": "replace-with-your-token"
      }
    }
  }
}
```

---

## 常见错误

### 1. 提示找不到 `cn-stock-mcp`
请重新安装：

```bash
python -m pip install cn-stock-mcp
```

### 2. `--doctor-network` 提示没有 token
说明你还没有在 MCP host 配置里填写：

```json
"ZHITU_TOKEN": "your-token"
```

### 3. `--doctor-network` 提示 provider_health 失败
通常表示：
- token 无效
- 网络访问上游失败
- 上游服务暂时异常

这时先检查 token，再重试。

### 4. 查询“银行”这类板块成员时失败
`sector_lookup` 的 `children/members` 必须显式传 `sector_type`。

正确示例：
```json
{"mode":"children","sector_type":"primary","sector_name":"银行","limit":20}
```

错误示例：
```json
{"mode":"children","sector_name":"银行","limit":20}
```

---

## 只在需要时再看

- `docs/EXAMPLES_MINIMAL.md`：最小调用示例
- `docs/COMPATIBILITY.md`：不同 MCP host / skill host 的兼容说明
- `docs/INTEGRATION.md`：更完整的挂载与联调说明
