# 数据源 API 文档索引

> 项目：`openclaw-stock-mcp`
> 用途：集中维护上游数据源文档入口，便于 provider 适配、排障与功能扩展。

## AKShare

- 官网文档入口：
  - https://akshare.akfamily.xyz/

## 智兔（Zhitu API）

- A 股接口：
  - https://www.zhituapi.com/hsstockapi.html
- 沪深指数接口：
  - https://www.zhituapi.com/hsindexapi.html
- 北交所接口：
  - https://www.zhituapi.com/bjdataapi.html
- 科创板接口：
  - https://www.zhituapi.com/kcdataapi.html
- 基金行情接口：
  - https://www.zhituapi.com/fundmarketapi.html

## 维护约定

1. 新增/替换上游数据源时，先更新本文件。
2. provider 映射实现（`docs/provider-mapping.md`）中的能力说明应与本文件保持一致。
3. 若发现链接失效，优先在本文件记录可替代入口，并标注失效时间。
