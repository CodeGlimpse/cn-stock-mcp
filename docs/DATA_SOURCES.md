# Data Sources and Licensing Review

当前代码通过 AKShare、Zhitu 及其下游公开接口取得市场数据。代码依赖和数据内容是两个不同的许可问题：AKShare 的代码许可证不自动授予所有下游数据的商用、缓存或再分发权。

发布前必须由项目维护者逐项记录并复核：

1. AKShare 项目许可证、调用限制和各数据适配器的实际来源。
2. Zhitu API 服务条款、token 使用限制、缓存/展示/再分发和商业使用条件。
3. EastMoney、Sina、交易所或其他下游接口的授权、速率、署名和数据保留要求。
4. 面向中国用户提供市场数据工具的金融信息服务、投资咨询和消费者告知边界。

在上述证据完成前，README 和 Release 不得声称数据可自由商用或可自由再分发。每个响应应显示 provider、source/as_of、fallback 和数据质量语义；`data_quality` 是启发式可用性提示，不是投资置信度。
