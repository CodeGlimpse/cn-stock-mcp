# Minimal Examples (`cn-stock-mcp`)

只保留最常见、最小可工作的调用示例。AI agent 默认先看本页，不必先读 README 里的长样例。

## provider 自检
```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool provider_health --payload '{}'
```

## 实时行情
```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_quote --payload '{"symbols":["600519.SH"],"sec_type":"stock"}'
```

## 历史走势
```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool stock_history --payload '{"symbol":"000001.SH","sec_type":"index","interval":"d","limit":30}'
```

## 市场简报
```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool market_brief --payload '{"brief_type":"close","trade_date":"2026-05-01","top_n":3}'
```

## 板块成员股
```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool sector_lookup --payload '{"mode":"children","sector_type":"primary","sector_name":"银行","limit":20}'
```

## 单板块复盘
```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool sector_review --payload '{"sector_name":"人工智能","sector_type":"concept","trade_date":"2026-04-30","top_n":3,"limit":20}'
```

## 多板块轮动
```bash
PYTHONPATH=src python -m cn_stock_mcp.main --tool sector_rotation_review --payload '{"sector_names":["1000信息","1000工业"],"sector_type":"primary","trade_date":"2026-05-06","top_n":2,"member_top_n":2,"limit":5}'
```
