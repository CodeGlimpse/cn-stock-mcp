# Security Policy

## Scope

本项目是本地运行的 stdio MCP server。它不连接券商、不保存交易账户、不执行下单或自动交易，也不提供远程管理服务。

## Sensitive data

Zhitu token 默认保存在 Windows 用户目录 `%LOCALAPPDATA%\cn-stock-mcp\config.json`。Host 配置不应保存 token。token 仅按 Zhitu 上游协议发送到配置的 API endpoint；网络代理、上游访问日志和第三方网络设备可能看到查询参数，因此应使用专用、可轮换的 token。

项目的 doctor、MCP envelope、错误和日志不得输出 token 原文、尾号、指纹或完整请求 URL。

## Reporting a vulnerability

请通过 GitHub Security Advisories（如果仓库已启用）或项目 Issues 提交最小必要信息。不要在公开 Issue 中粘贴 token、配置文件、完整日志或用户数据。发布版本只承诺维护仓库 `SUPPORT.md` 中列出的安全支持范围。

## Release controls

- 依赖审计、CodeQL、secret scanning 和构建 smoke 必须通过。
- 发布制品必须包含 SHA256、SBOM 和 GitHub 构建来源证明。
- 发布前必须完成 token 脱敏回归和干净 Windows 安装验收。
