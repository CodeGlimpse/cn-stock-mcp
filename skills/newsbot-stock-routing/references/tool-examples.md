# Tool examples

只在需要 payload 示例时再读本文件。

## 高频最小 payload

### 实时行情
```json
{"tool":"stock_quote","payload":{"symbols":["600519.SH"],"sec_type":"stock"}}
```

### 指数历史
```json
{"tool":"stock_history","payload":{"symbol":"000001.SH","sec_type":"index","interval":"d","limit":30}}
```

### 单股复盘
```json
{"tool":"stock_review","payload":{"symbol":"600519.SH","trade_date":"2026-05-01"}}
```

### 市场简报
```json
{"tool":"market_brief","payload":{"brief_type":"close","trade_date":"2026-05-01","top_n":3}}
```

### 板块成员股
```json
{"tool":"sector_lookup","payload":{"mode":"children","sector_type":"primary","sector_name":"银行","limit":20}}
```

### 板块复盘（一级行业）
```json
{"tool":"sector_review","payload":{"sector_name":"1000信息","sector_type":"primary","trade_date":"2026-04-30","top_n":3,"limit":20}}
```

### 板块轮动复盘（多板块）
```json
{"tool":"sector_rotation_review","payload":{"sector_names":["1000信息","1000工业"],"sector_type":"primary","trade_date":"2026-05-06","top_n":2,"member_top_n":2,"limit":5}}
```

### 候选扫描
```json
{"tool":"stock_candidate_scan","payload":{"pool_type":"strong","trade_date":"2026-05-06","limit":5,"top_n":3}}
```

### 观察池复盘
```json
{"tool":"watchlist_review","payload":{"symbols":["600519.SH","300750.SZ","000001.SZ"],"watchlist_name":"核心池","trade_date":"2026-05-06","top_n":2}}
```

### 多周期复盘
```json
{"tool":"multi_timeframe_review","payload":{"symbol":"000001.SH","sec_type":"index","intervals":["15","d","w"],"indicators":["macd","ma","kdj"],"limit":60}}
```

## 长尾示例

长尾能力（宏观、龙虎榜、ETF、可转债、期货/期权、融资融券、大宗交易等）优先参考仓库主文档或后续按需补充分组示例，不默认加载到 skill 主路径。
