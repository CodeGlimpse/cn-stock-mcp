# OpenClaw：MCP 与可选 Skill

适用 Windows 原生 Gateway，目标 `cn-stock-mcp==0.2.3`。MCP 配置以 [OpenClaw 专页](OPENCLAW_HOST_TEMPLATE.md) 为准。Windows Hub 若连接 WSL/远程 Gateway，其运行路径不属于本页的 Windows 本机环境。

## 1. 先配置 MCP

按专页在 `mcp.servers` 添加 `cn_stock_mcp`，指向已安装包的绝对 `cn-stock-mcp.exe` 路径，参数为 `--stdio`。客户需要检查配置时使用 `openclaw mcp status --verbose`；本轮不执行连接或行情测试。

## 2. 可选加载路由 Skill

`newsbot-stock-routing` 为市场简报/复盘任务提供工具路由提示；它不替代 MCP 安装，也不保管 Token。

wheel 的文档目录与 skills 目录相邻。若采用共同准备的安装位置，skills 根目录是：

```text
C:\Users\YOUR_NAME\AppData\Local\cn-stock-mcp\runtime\venv\share\cn-stock-mcp\skills
```

需要加载时，在已备份的 OpenClaw 配置中合并以下额外目录；已有数组需追加并保留原项：

```json
{
  "skills": {
    "load": {
      "extraDirs": [
        "C:\\Users\\YOUR_NAME\\AppData\\Local\\cn-stock-mcp\\runtime\\venv\\share\\cn-stock-mcp\\skills"
      ]
    }
  }
}
```

官方支持 `skills.load.extraDirs`，同时还有按 Agent/会话管理 Skill 的机制。保存后在 OpenClaw 的 Skills 管理页检查发现结果，按需要给目标 Agent/会话启用。已有 Skill allowlist 时按当前官方规则合并，不用该示例覆盖其他条目。

## 3. 维护与恢复

MCP 工具档和参数以服务端文档为准；Skill 中更广的路由能力不表示 retail 会公开 full 工具。只需要 MCP 查询时无需加载这份可选 Skill。

停用时移除本次添加的 skills 目录或解除对应 Agent/会话绑定；MCP 本体按其配置专页停用。各项修改均保留其他配置并可以恢复本次备份。

官方依据（2026-09-07 核对）：[Skills](https://docs.openclaw.ai/tools/skills)、[Configuration](https://docs.openclaw.ai/gateway/configuration)、[Windows](https://docs.openclaw.ai/platforms/windows)。
