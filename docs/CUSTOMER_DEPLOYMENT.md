# cn-stock-mcp 客户部署与排障说明

适用版本：`cn-stock-mcp==0.2.0`

本文件面向客户、交付人员和负责部署的 AI Agent。Windows 是首发版本的重点部署平台；完整的 Agent 执行合同见 [AI_DEPLOY_WINDOWS.md](AI_DEPLOY_WINDOWS.md)。

## 1. 先了解产品边界

`cn-stock-mcp` 是本机运行的 MCP stdio server：

- 不连接券商
- 不保存交易账户
- 不下单、不买卖、不自动交易
- 不提供投资参考、投资建议或风险建议
- 默认不启用遥测或远程管理服务

行情和分析数据来自 AKShare、智兔（Zhitu）及其下游公开接口，可能延迟、缺失、限流或发生字段变化。

## 2. 推荐部署方式：Windows 用户级虚拟环境

### 环境要求

- Windows x64
- 普通 CPython 3.13（不要使用 `3.13t` free-threaded 版本）
- 可访问 PyPI 的网络
- 能够运行 PowerShell

### 安装固定版本

```powershell
$root = Join-Path $env:LOCALAPPDATA "cn-stock-mcp"
$venv = Join-Path $root "runtime\venv"

py -3.13 -m venv $venv
& "$venv\Scripts\python.exe" -m pip install --upgrade pip
& "$venv\Scripts\python.exe" -m pip install cn-stock-mcp==0.2.0

$mcpExe = Join-Path $venv "Scripts\cn-stock-mcp.exe"
& $mcpExe --version
```

预期版本输出：

```text
0.2.0
```

不要把 `pip install cn-stock-mcp`（不带版本）作为验收证据，也不要把 token 放在 pip 命令中。

### 创建配置文件

建议由最终使用者本人在自己的 Windows 账号下运行：

```powershell
& $mcpExe --init-config
```

默认配置文件：

```text
%LOCALAPPDATA%\cn-stock-mcp\config.json
```

程序会创建空 token 模板并尝试收紧 ACL。部署 Agent、MCP Host 和用户编辑配置文件时，最好使用同一个 Windows 账号；如果 Agent 在沙箱或服务账号中运行，不要让它代替用户创建最终凭据文件，见“权限问题”。

## 3. 如何获取智兔（Zhitu）token

智兔 token 不是本项目免费附带的凭据，需要客户自行向智兔官方申请或购买。

官方入口：

- [智兔证书获取页面](https://zhituapi.com/gettoken.html)
- [智兔接入说明](https://www.zhituapi.com/access.html)
- [智兔服务条款](https://zhituapi.com/termsofservice.html)

申请流程以智兔官网当前页面为准，通常包括：

1. 打开官方证书获取页面。
2. 查看当前可用证书类型、请求额度、频率、有效期和使用限制。
3. 按页面要求申请免费证书或购买适合自己的证书。
4. 按官方页面提示获取 Token 证书字符串。
5. 保存好 token；不要把它发送给销售、AI Agent、MCP Host、聊天窗口或工单附件。

智兔的套餐、价格、额度和申请流程可能变化，本文不承诺具体价格或额度。使用前请阅读智兔当前服务条款；token 可能有期限和次数限制，且不得超出上游条款进行转让、转售、再分发或第三方使用。

### 手动写入 token

用记事本打开配置文件：

```powershell
notepad "$env:LOCALAPPDATA\cn-stock-mcp\config.json"
```

只修改 `primary` 的值，结构类似：

```json
{
  "tool_profile": "retail_v1_preview",
  "zhitu": {
    "default": "primary",
    "tokens": {
      "primary": "在这里粘贴你自己的智兔 token"
    }
  }
}
```

上面的文字只是占位说明，不是有效 token。保存后不要把文件内容复制到聊天、截图、日志或 Host 配置中。服务启动时会自动读取该文件。

## 4. 安装后的检查

### 不需要 token 的本地检查

```powershell
& $mcpExe --doctor --json
& $mcpExe --list-tools --json
```

`--doctor` 在没有 token 或跳过网络检查时显示 `WARN` 可能是正常现象，但退出码应为 `0`。默认 `retail_v1_preview` 应返回 10 个工具。

### 填写 token 后的网络检查

```powershell
& $mcpExe --doctor-network --json
```

该命令会访问 Provider 和上游接口，可能消耗额度。如果 token 无效、过期、额度耗尽或网络受限，会报告相应错误。

### 首次问答

在 MCP Host 中重载 server 后，使用：

> 查询 `000001.SZ` 最新行情，给出数据来源、数据时间、交易时段和数据质量；不要提供投资建议。

验收应能看到代码、来源、`freshness/as_of`、交易时段或 `session_context`、`data_quality`，且没有 token、下单指令、收益承诺或荐股结论。

## 5. 接入常用 AI Host

所有 Host 都使用本地 stdio：

```text
command = cn-stock-mcp.exe 的绝对路径
args = ["--stdio"]
```

配置前先备份原文件，并保留原有字段和其他 MCP server。不要添加 `ZHITU_TOKEN` 环境变量。

- [Codex](CODEX_TEMPLATE.md)
- [Claude Code](CLAUDE_CODE_TEMPLATE.md)
- [OpenClaw](OPENCLAW_HOST_TEMPLATE.md)
- [Hermes Agent](HERMES_TEMPLATE.md)
- [其他 Host 总入口](HOST_CONFIG_TEMPLATES.md)

默认使用 `retail_v1_preview`。它包含 10 个高层工具；只有在用户明确需要时才切换 `full` 工具档。

## 6. 常见问题排查

### `cn-stock-mcp` 找不到

虚拟环境的 Scripts 目录未必在 PATH 中。使用绝对路径：

```powershell
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\cn-stock-mcp.exe" --version
```

也可以确认安装：

```powershell
& "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv\Scripts\python.exe" -m pip show cn-stock-mcp
```

### 配置文件没有权限打开

`--init-config` 会移除继承 ACL，只授权执行命令的账号和 `SYSTEM`。如果 AI Agent 以沙箱账号创建文件，而用户以另一个 Windows 账号编辑，就可能出现拒绝访问。

先在用户自己的 PowerShell 中确认身份和路径：

```powershell
whoami
$config = Join-Path $env:LOCALAPPDATA "cn-stock-mcp\config.json"
icacls $config
```

如果确认该文件属于自己的部署环境，可在用户账号下补充当前用户权限：

```powershell
$me = (whoami).Trim()
icacls $config /grant:r "$($me):(F)" "SYSTEM:(F)"
```

如果仍然拒绝访问，请使用管理员 PowerShell，或让最终用户账号重新执行 `--init-config`。不要为了省事把 token 文件改成所有用户可读，也不要把 token 改放到 Host 配置中。

### `--doctor` 显示 token 缺失

确认用户填写的是：

```text
%LOCALAPPDATA%\cn-stock-mcp\config.json
```

并且 JSON 结构中存在 `zhitu.tokens.primary`。不要把 token 放到命令行或 Host 的 `env` 中。Agent 可以读取状态，但不应读取或回显 token 值。

### `PROVIDER_AUTH_FAILED`

通常表示 token 缺失、错误、过期或没有可用额度。请用户在智兔官方页面核验证书状态，并手动更新本地配置。不要把 token 发给排障人员。

### `PROVIDER_TIMEOUT`、`PROVIDER_UNAVAILABLE`

按顺序检查：

1. 能否访问 PyPI 和智兔 API 域名。
2. 公司代理、防火墙、VPN 或 DNS 是否拦截请求。
3. `--doctor-network --json` 的错误类别和 Provider 名称。
4. 稍后重试，确认是否为上游临时故障。

项目不保证第三方接口 SLA；不要因为一次上游失败就重复高频调用。

### Host 能启动但看不到工具

检查：

- Host 使用的是正确的绝对 `cn-stock-mcp.exe` 路径
- 参数是否为 `--stdio`
- Host 配置是否保留了正确的 JSON/TOML/YAML 结构
- 是否在修改前备份并重载了 Host
- 用户配置是否选择了 `retail_v1_preview` 或明确的 `full`

先运行 `--list-tools --json`，再排查 Host；不要把 token 放入 Host 配置。

### 返回 `partial_failure`、数据为空或 freshness unknown

这表示部分 Provider、字段或时间信息不可用，不一定是安装错误。查看响应中的：

- `error_code`
- `provider_used`
- `fallback_chain`
- `freshness`
- `data_quality`

`data_quality` 是数据可用性提示，不是投资置信度。

## 7. 升级、回滚和卸载

升级前备份 Host 配置，并保留 token 文件。安装新版本后重新运行 `--version`、`--doctor` 和 `--list-tools`。如果 Host 连接异常，先恢复 Host 配置备份。

卸载时只删除本项目虚拟环境：

```powershell
Remove-Item -LiteralPath "$env:LOCALAPPDATA\cn-stock-mcp\runtime\venv" -Recurse
```

删除前请确认路径确实是本项目虚拟环境。token 配置文件由用户自行决定是否保留或删除；不要把它上传到工单、网盘或代码仓库。

## 8. 免责声明与数据授权边界

本工具仅提供证券市场数据查询、整理和分析接口，不构成任何投资参考、投资建议、风险建议、买卖指令、收益承诺或个性化投资服务。用户应独立判断并核验数据，不应仅凭 AI 输出进行投资决策。

数据可能延迟、缺失、错误、被限流或因第三方接口变更而不可用。`freshness`、`session_context` 和 `data_quality` 只描述数据状态，不代表投资置信度或未来表现。

AKShare、智兔及其下游数据的授权、缓存、展示、商业使用和再分发限制由相应权利方和服务条款决定。本项目不向客户转让第三方数据授权，也不保证任何数据可自由商用或再分发。请阅读：

- [项目数据来源声明](DATA_SOURCES.md)
- [项目隐私说明](PRIVACY.md)
- [项目安全策略](SECURITY.md)
- [项目支持范围](SUPPORT.md)
- [智兔服务条款](https://zhituapi.com/termsofservice.html)
