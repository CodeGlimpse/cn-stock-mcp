# 客户复制给本地 Agent 的安装部署提示词

更新日期：2026-09-08。适用已发布版本：`cn-stock-mcp==0.2.3`。以下 SHA256 来自正式发行文件；安装时仍须核对 [GitHub Release](https://github.com/CodeGlimpse/cn-stock-mcp/releases/tag/v0.2.3) 与 [PyPI](https://pypi.org/project/cn-stock-mcp/0.2.3/)。

客户把下面整个代码块复制给具备本机文件和 PowerShell 执行能力的 Agent 即可，无需预先填写占位符。默认接入 Codex；执行安装的 Agent 与接入 MCP 的客户端可以是不同软件。首发服务范围和验收期限按[交付约定](COMMERCIAL_DELIVERY_TEMPLATE.md)执行，其他客户端指南仅作配置参考。

```text
请在我这台 Windows 电脑上实际安装并配置 cn-stock-mcp==0.2.3，默认接入 Codex。请执行部署，不要只给我操作建议。你是执行安装的本地 Agent，接入 MCP 的目标客户端不一定是你自身；如果我明确指定其他客户端，先确认交付范围，再使用对应指南。

一、先确认环境与授权
先确认你能在我的电脑上执行 PowerShell、操作本地文件，以及目标客户端的名称、类型和版本。Codex 桌面、CLI、IDE 扩展要区分记录；无法确认时询问我，不把你的运行环境自动当成目标客户端。没有本机执行能力时明确说明，不能宣称已安装。

本次范围是 Windows 11 x64、普通 CPython 3.13（非 free-threaded）、独立 venv、本机 stdio、retail_v1_preview 10 工具。先只读检查环境；安装、联网下载或处理 Host 配置前，一次列清准确路径、拟执行命令、网络来源、备份及影响，取得我的确认后连续完成已授权步骤。遇到新的权限边界再申请，不关闭权限审批、沙箱或安全设置。缺少 Python 时另行说明官方用户级安装方案；不修改系统 PATH、全局 Python 包或全局执行策略。

二、使用固定版本资料和文件
发行页：https://github.com/CodeGlimpse/cn-stock-mcp/releases/tag/v0.2.3
PyPI：https://pypi.org/project/cn-stock-mcp/0.2.3/
Windows 部署说明：https://raw.githubusercontent.com/CodeGlimpse/cn-stock-mcp/v0.2.3/docs/AI_DEPLOY_WINDOWS.md
Codex 配置指南：https://raw.githubusercontent.com/CodeGlimpse/cn-stock-mcp/v0.2.3/docs/CODEX_TEMPLATE.md
其他客户端索引：https://raw.githubusercontent.com/CodeGlimpse/cn-stock-mcp/v0.2.3/docs/HOST_CONFIG_TEMPLATES.md

先阅读上述部署说明及实际客户端专页，按该版本执行。只安装 PyPI 的固定 wheel，不克隆源码、不安装 main、其他版本或来源不明的镜像。使用公共 PyPI 时让 pip 忽略用户的私有源配置，例如使用 --isolated 并显式指定 --index-url https://pypi.org/simple。先仅下载目标 wheel（--no-deps、--only-binary=:all:），再按约束安装依赖。

正式文件的 SHA256：
cn_stock_mcp-0.2.3-py3-none-any.whl
5f36f17eab33d4ea1635083e1ffb34174959efc76d97e9e4ee5b664e766a9186
constraints-windows-py313.txt
99bdb1f0ae4c89b36569147e62aaaa72ef35ba9dcee71160e7356fdabce40cf7
sha256sums.txt
784b49bdd91c75793c3bcd2a42a293cc2a24ed176304cb5bd0bddcb3f60b262f

从同版本 GitHub Release 下载约束文件和 sha256sums.txt，核对以上三个哈希，再核对校验清单中 wheel 与约束的条目。文件缺失、下载失败或任一哈希不同就停止，不跳过校验、不换装其他版本。若无法联网，说明缺少什么文件，不能编造下载或校验结果。

三、隔离安装并保护已有环境
默认安装位置为当前最终用户的 %LOCALAPPDATA%\cn-stock-mcp\runtime\venv；所有命令最终替换为本机绝对路径。执行前检查已有安装及配置是否存在，只检查 Token 配置文件的路径和存在性，不读取内容。已有可用安装时先确认版本与处理方案，不覆盖旧 venv、不删除旧目录、不重置 Token 配置。

使用受支持的 Python 创建独立 venv，将已校验的 wheel 与同版本约束文件配合安装：pip install -c <约束文件绝对路径> <wheel绝对路径>。检查每条命令的退出码，失败时停止并报告原因。不要把其他项目的 .env 或配置带入部署进程；部署操作和 MCP 启动使用本项目独立工作目录。

四、由我本人填写 Token
默认配置路径为 %LOCALAPPDATA%\cn-stock-mcp\config.json。文件不存在时，在最终使用人的 Windows 账号下运行已安装程序的 --init-config 创建空模板；如果你与我不是同一执行账号，让我本人执行该命令，避免生成我无法编辑的文件。已有文件保留原样。

只告诉我配置文件的绝对路径和需要手动填写的字段 zhitu.tokens.primary，然后暂停让我自行填写。不要读取、索取、代填、复制、回显、截图或上传 Token；也不要要求我把配置文件、Token 尾号或截图发到聊天。Token 不得放入 Host 配置、命令行、环境变量、日志或报告。只有 MCP 应用在运行时读取自己的配置，Agent 不读取 Token 值。

如果我没有 Token，让我本人查看官方页面并完成申请：
https://zhituapi.com/gettoken.html
https://www.zhituapi.com/access.html
https://zhituapi.com/termsofservice.html
登录、验证码、套餐选择、付款及 Token 复制由我本人完成。如果我选择暂不配置 Token，继续能完成的安装、配置和离线检查，把“Token 待配置、真实行情未验证”列为待办，不反复催我要 Token。

五、检查安装并配置目标客户端
运行安装环境的 pip check，以及已安装程序的 --version、--doctor --json、--list-tools --json。--doctor 可以提示未运行网络检查，但退出码应为 0。用 --docs-path 定位包内 docs 及同级 tools，运行打包的 verify_runtime_constraints.py（指定随包约束并加 --installed）和 verify_license_bundle.py（--root 指向 docs 的父目录）。约束文件中的每个版本限定不等于必装依赖，以实际安装依赖闭包检查为准。

需要验证 stdio 时，使用包内 verify_mcp_stdio.py，指定实际 --command、--expected-version 0.2.3、--expected-tools 10 和独立 --cwd；保留默认离线握手、目录及无效参数检查，不增加有效行情调用。

在已经获准的目标 Host 配置路径旁创建带时间戳的本地备份，备份不上传。使用本地解析/编辑工具合并本服务器条目，保留其他 MCP server、模型设置和未知字段，避免重复键或重复服务器；不要将整份现有配置输出到聊天。客户端格式不同，不能套用别的软件模板；遇到实际版本与指南不符时核对该客户端官方文档。

Host 启动命令使用已安装 cn-stock-mcp.exe 的绝对路径，参数包含 --stdio；支持工作目录字段时指向本项目 runtime，否则遵循该客户端的启动机制，不凭空添加配置字段。环境设置仅包含路径和运行选项，例如 CN_STOCK_MCP_CONFIG、TOOL_PROFILE=retail_v1_preview、PYTHONUTF8=1；其中 CN_STOCK_MCP_CONFIG 是文件路径，绝不是 Token。按所选客户端指南设置并重载。若要重启正在执行部署的客户端，先交付当前进度与恢复步骤，由我执行重启，不能丢失尚未完成的工作。

核对本服务器的以下 10 个工具；客户端可能添加服务器前缀，不把其他服务器工具计入：
stock_search、market_brief、stock_snapshot、stock_quote、stock_history、stock_review、watchlist_review、trading_calendar、sector_review、hot_theme_tracker。

六、真实查询由我另行决定
默认不运行 --doctor-network、--run-live 或任何有效行情查询。先分别报告安装检查、stdio 检查和实际 Host 连接/工具发现结果；无法操作 Host 界面时给我检查步骤，并保留“Host 尚待客户确认”。配置保存成功和脚本检查通过都不能代替实际 Host 结果。

如果我明确要求真实查询，再展示随包 retail 验收工具的计划、请求范围及可能消耗的额度，获得确认后执行；非 PASS 即停止。未执行的项目写“未执行”，不写“通过”，也不循环重试凑结果。实际问答注明代码、来源、数据时间或 unknown、交易时段、fallback、partial failure 和 data_quality，仅做数据查询整理，不给投资建议、买卖指令或收益承诺。

七、交付结果
最后给我一份简短脱敏报告：软件/Python/目标 Host 的实际版本；安装及可执行文件路径；Token 配置文件路径（不含内容）；Host 配置与备份路径；三个文件的校验结果；依赖、许可证、本地自检、stdio、实际 Host 连接及工具目录的分别结果；真实行情是否执行；仍需我操作的具体步骤及本次修改的回退办法。

遇到失败，保留已有文件和证据，准确说明阻塞位置和拟处理方案，取得同意后才修复或回退。本次只回退自己改动的服务器条目，不整文件覆盖后续改动，不擅自删除配置或降低访问权限。不能完成的部分明确列出，不能用“配置已保存”冒充全部验收完成。
```

这段提示词需要客户自己的本机 Agent 和实际授权才能执行。客户填写 Token、确认权限或重载客户端时，Agent 可能需要暂停等待；普通网页聊天工具不能凭提示词取得本机执行能力。

本页为发布后的客户提示词修订，正式安装包仍使用不可变的 `v0.2.3` 文件。发布文件及校验结果见发行页；[客户逐单验收说明](RETAIL_ACCEPTANCE.md)和[服务交付约定](COMMERCIAL_DELIVERY_TEMPLATE.md)另行记录实际交付结果。
