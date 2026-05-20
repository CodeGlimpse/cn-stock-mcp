# Tool routing extended

只在用户明确问到长尾能力时再读本文件。

## 长尾能力 → tool

- 宏观经济指标（CPI/PPI/PMI/GDP/LPR/M2/信贷/出口/非农/BDI/黄金等）→ `macro_indicator`
- 龙虎榜（日榜明细/机构买卖/活跃营业部/营业部胜率/个股上榜统计）→ `dragon_tiger`
- 龙虎榜机构席位深度（单股买卖席位/活跃营业部/机构明细/机构追踪/席位标签）→ `sec_reveal`
- ETF 行情快照（全市场实时+IOPV折溢价+资金流+份额+净值）→ `etf_snapshot`
- 可转债（双低/溢价率/YTM/强赎监控/等权指数）→ `convertible_bond`
- 期货/期权（期货实时+历史/期权合约/QVIX隐含波动率）→ `derivatives_data`
- 融资融券（两市汇总+个股明细/融资买入排序）→ `margin_trading`
- 大宗交易（每日明细+个股汇总/折溢率+行业统计+营业部胜率排行+活跃个股追踪）→ `block_trade`
- 机构持仓（季度汇总+个股明细/增持减持变动）→ `institute_hold`
- 货币市场利率（SHIBOR曲线+银行间拆借+回购定盘利率）→ `money_rate`
- 选股筛选（市场/价格/涨跌幅/成交量/成交额/振幅多条件）→ `stock_screen`
- 高管增减持（十大流通股东变动+增减持历史）→ `insider_trade`
- 股息率/分红排名（历史分红排名+分红方案+单股分红明细）→ `dividend_rank`
- 股东变动（十大股东变动+全市场股东持股汇总）→ `shareholder_change`
- 披露日历（财报披露时间表/预约日/变更/实际披露日）→ `disclosure_calendar`
- 回购明细（公司回购计划/进度/已回购金额）→ `stock_repurchase`
- 多股横向对比（行情+估值+财务+股息分层加载）→ `stock_compare`
- 产业链上下游（行业涨跌/资金流入+概念板块驱动事件/龙头股）→ `industry_chain`
- 权证/期权（ETF期权+商品期权+股指期权）→ `stock_warrant`
- 主力资金流向（全市场趋势+行业净流入排名+单股历史）→ `fund_flow`

## 读取顺序

1. 先回到 `quick-routing-core.md` 确认是不是高频问题。
2. 只有确实是长尾能力时，再在本文件里找对应 tool。
3. 需要详细 payload 示例时，再读 `tool-examples.md`。
