from __future__ import annotations

from cn_stock_mcp.app.models.dragon_tiger import (
    ActiveBrokerItem,
    BrokerRankItem,
    DailyDetailItem,
    InstitutionItem,
    StockStatItem,
)


def _to_float(value) -> float | None:
    if value is None or value == "" or value is False:
        return None
    try:
        f = float(value)
        import math
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def _to_int(value) -> int | None:
    if value is None or value == "" or value is False:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _format_symbol(code: str) -> str:
    code = str(code).strip()
    if len(code) != 6:
        return code
    if code.startswith("6"):
        return f"{code}.SH"
    return f"{code}.SZ"


def adapt_daily_detail_row(row: dict) -> DailyDetailItem:
    """Adapt a row from ak.stock_lhb_detail_em()."""
    code = str(row.get("代码", ""))
    return DailyDetailItem(
        symbol=_format_symbol(code),
        name=str(row.get("名称", "")),
        trade_date=str(row.get("上榜日", ""))[:10] or None,
        close=_to_float(row.get("收盘价")),
        change_percent=_to_float(row.get("涨跌幅")),
        net_buy_amount=_to_float(row.get("龙虎榜净买额")),
        buy_amount=_to_float(row.get("龙虎榜买入额")),
        sell_amount=_to_float(row.get("龙虎榜卖出额")),
        turnover_amount=_to_float(row.get("龙虎榜成交额")),
        market_total_amount=_to_float(row.get("市场总成交额")),
        net_buy_ratio=_to_float(row.get("净买额占总成交比")),
        turnover_ratio=_to_float(row.get("成交额占总成交比")),
        turnover_rate=_to_float(row.get("换手率")),
        float_market_cap=_to_float(row.get("流通市值")),
        reason=str(row.get("上榜原因", "")) or None,
        interpretation=str(row.get("解读", "")) or None,
        after_1d=_to_float(row.get("上榜后1日")),
        after_2d=_to_float(row.get("上榜后2日")),
        after_5d=_to_float(row.get("上榜后5日")),
        after_10d=_to_float(row.get("上榜后10日")),
    )


def adapt_institution_row(row: dict) -> InstitutionItem:
    """Adapt a row from ak.stock_lhb_jgmmtj_em()."""
    code = str(row.get("代码", ""))
    return InstitutionItem(
        symbol=_format_symbol(code),
        name=str(row.get("名称", "")),
        close=_to_float(row.get("收盘价")),
        change_percent=_to_float(row.get("涨跌幅")),
        buy_inst_count=_to_int(row.get("买方机构数")),
        sell_inst_count=_to_int(row.get("卖方机构数")),
        inst_buy_total=_to_float(row.get("机构买入总额")),
        inst_sell_total=_to_float(row.get("机构卖出总额")),
        inst_net_buy=_to_float(row.get("机构买入净额")),
        market_total_amount=_to_float(row.get("市场总成交额")),
        inst_net_buy_ratio=_to_float(row.get("机构净买额占总成交额比")),
        turnover_rate=_to_float(row.get("换手率")),
        float_market_cap=_to_float(row.get("流通市值")),
        reason=str(row.get("上榜原因", "")) or None,
        trade_date=str(row.get("上榜日期", ""))[:10] or None,
    )


def adapt_active_broker_row(row: dict) -> ActiveBrokerItem:
    """Adapt a row from ak.stock_lhb_hyyyb_em()."""
    return ActiveBrokerItem(
        broker_name=str(row.get("营业部名称", "")),
        broker_code=str(row.get("营业部代码", "")) or None,
        trade_date=str(row.get("上榜日", ""))[:10] or None,
        buy_count=_to_int(row.get("买入个股数")),
        sell_count=_to_int(row.get("卖出个股数")),
        buy_amount=_to_float(row.get("买入总金额")),
        sell_amount=_to_float(row.get("卖出总金额")),
        net_amount=_to_float(row.get("总买卖净额")),
        buy_stocks=str(row.get("买入股票", "")) or None,
    )


def adapt_broker_rank_row(row: dict) -> BrokerRankItem:
    """Adapt a row from ak.stock_lhb_yybph_em()."""
    return BrokerRankItem(
        broker_name=str(row.get("营业部名称", "")),
        after_1d_count=_to_int(row.get("上榜后1天-买入次数")),
        after_1d_avg_change=_to_float(row.get("上榜后1天-平均涨幅")),
        after_1d_up_prob=_to_float(row.get("上榜后1天-上涨概率")),
        after_2d_count=_to_int(row.get("上榜后2天-买入次数")),
        after_2d_avg_change=_to_float(row.get("上榜后2天-平均涨幅")),
        after_2d_up_prob=_to_float(row.get("上榜后2天-上涨概率")),
        after_5d_count=_to_int(row.get("上榜后5天-买入次数")),
        after_5d_avg_change=_to_float(row.get("上榜后5天-平均涨幅")),
        after_5d_up_prob=_to_float(row.get("上榜后5天-上涨概率")),
        after_10d_count=_to_int(row.get("上榜后10天-买入次数")),
        after_10d_avg_change=_to_float(row.get("上榜后10天-平均涨幅")),
        after_10d_up_prob=_to_float(row.get("上榜后10天-上涨概率")),
    )


def adapt_stock_stat_row(row: dict) -> StockStatItem:
    """Adapt a row from ak.stock_lhb_stock_statistic_em()."""
    code = str(row.get("代码", ""))
    return StockStatItem(
        symbol=_format_symbol(code),
        name=str(row.get("名称", "")),
        last_listed_date=str(row.get("最近上榜日", ""))[:10] or None,
        close=_to_float(row.get("收盘价")),
        change_percent=_to_float(row.get("涨跌幅")),
        listed_count=_to_int(row.get("上榜次数")),
        board_turnover=_to_float(row.get("龙虎榜成交金额")),
        net_buy_amount=_to_float(row.get("龙虎榜净买额")),
        after_1d_avg=_to_float(row.get("上榜后1日")),
        after_2d_avg=_to_float(row.get("上榜后2日")),
        after_5d_avg=_to_float(row.get("上榜后5日")),
        after_10d_avg=_to_float(row.get("上榜后10日")),
    )


def build_dragon_tiger_summary_text(
    daily: list[DailyDetailItem],
    institution: list[InstitutionItem],
    active_broker: list[ActiveBrokerItem],
    broker_rank: list[BrokerRankItem],
    stock_stat: list[StockStatItem],
) -> str:
    parts: list[str] = []

    if daily:
        net_buy_pos = [d for d in daily if d.net_buy_amount is not None and d.net_buy_amount > 0]
        net_buy_neg = [d for d in daily if d.net_buy_amount is not None and d.net_buy_amount < 0]
        parts.append(f"上榜{len(daily)}只")
        if net_buy_pos:
            top = net_buy_pos[0]
            parts.append(f"净买入最高{top.name}({top.net_buy_amount / 1e8:.2f}亿)")
        if net_buy_neg:
            top_neg = net_buy_neg[0]
            parts.append(f"净卖出最高{top_neg.name}({abs(top_neg.net_buy_amount) / 1e8:.2f}亿)")

    if institution:
        inst_net = [i for i in institution if i.inst_net_buy is not None and i.inst_net_buy > 0]
        parts.append(f"机构参与{len(institution)}只")
        if inst_net:
            top_inst = inst_net[0]
            parts.append(f"机构净买入{top_inst.name}({top_inst.inst_net_buy / 1e8:.2f}亿)")

    if active_broker:
        parts.append(f"活跃营业部{len(active_broker)}家")

    if broker_rank:
        best = broker_rank[0]
        if best.after_1d_up_prob is not None:
            parts.append(f"胜率最高营业部{best.broker_name}({best.after_1d_up_prob:.0f}%)")

    if stock_stat:
        most = stock_stat[0]
        if most.listed_count:
            parts.append(f"最频繁上榜{most.name}({most.listed_count}次)")

    return "，".join(parts) if parts else "龙虎榜数据暂无"
