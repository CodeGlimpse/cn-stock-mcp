from __future__ import annotations

from cn_stock_mcp.app.models.block_trade import (
    BlockTradeActiveStockItem,
    BlockTradeBrokerRankItem,
    BlockTradeDailyItem,
    BlockTradeDailyStatItem,
    BlockTradeIndustryItem,
)
from cn_stock_mcp.infra.time_utils import normalize_symbol


def _to_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value):
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def adapt_block_trade_daily_row(row: dict) -> BlockTradeDailyItem:
    raw_code = str(row.get("证券代码", "")).strip()
    symbol = normalize_symbol(raw_code) if raw_code else ""
    return BlockTradeDailyItem(
        trade_date=str(row.get("交易日期", "")).strip(),
        symbol=symbol,
        name=str(row.get("证券简称", "")).strip(),
        price=_to_float(row.get("成交价")),
        volume=_to_float(row.get("成交量")),
        turnover=_to_float(row.get("成交额")),
        buyer_broker=str(row.get("买方营业部", "")).strip() or None,
        seller_broker=str(row.get("卖方营业部", "")).strip() or None,
    )


def adapt_block_trade_daily_stat_row(row: dict) -> BlockTradeDailyStatItem:
    raw_code = str(row.get("证券代码", "")).strip()
    symbol = normalize_symbol(raw_code) if raw_code else ""
    return BlockTradeDailyStatItem(
        trade_date=str(row.get("交易日期", "")).strip(),
        symbol=symbol,
        name=str(row.get("证券简称", "")).strip(),
        change_percent=_to_float(row.get("涨跌幅")),
        close_price=_to_float(row.get("收盘价")),
        trade_price=_to_float(row.get("成交价")),
        discount_rate=_to_float(row.get("折溢率")),
        trade_count=_to_int(row.get("成交笔数")),
        total_volume=_to_float(row.get("成交总量")),
        total_turnover=_to_float(row.get("成交总额")),
        turnover_to_float_cap=_to_float(row.get("成交总额/流通市值")),
    )


def adapt_block_trade_industry_row(row: dict) -> BlockTradeIndustryItem:
    return BlockTradeIndustryItem(
        industry=str(row.get("行业", "")).strip(),
        listed_count=_to_int(row.get("上榜次数", row.get("上榜家数"))),
        trade_count=_to_int(row.get("成交笔数")),
        total_turnover=_to_float(row.get("总成交额", row.get("成交总额"))),
        avg_discount_rate=_to_float(row.get("平均折溢率", row.get("折溢率"))),
        premium_count=_to_int(row.get("溢价次数")),
        discount_count=_to_int(row.get("折价次数")),
        premium_turnover=_to_float(row.get("溢价成交额")),
        discount_turnover=_to_float(row.get("折价成交额")),
    )


def adapt_block_trade_broker_rank_row(row: dict) -> BlockTradeBrokerRankItem:
    return BlockTradeBrokerRankItem(
        broker_name=str(row.get("营业部名称", "")).strip(),
        buy_count_1d=_to_int(row.get("上榜后1天-买入次数")),
        avg_return_1d=_to_float(row.get("上榜后1天-平均涨幅")),
        win_rate_1d=_to_float(row.get("上榜后1天-上涨概率")),
        buy_count_5d=_to_int(row.get("上榜后5天-买入次数")),
        avg_return_5d=_to_float(row.get("上榜后5天-平均涨幅")),
        win_rate_5d=_to_float(row.get("上榜后5天-上涨概率")),
        buy_count_10d=_to_int(row.get("上榜后10天-买入次数")),
        avg_return_10d=_to_float(row.get("上榜后10天-平均涨幅")),
        win_rate_10d=_to_float(row.get("上榜后10天-上涨概率")),
        buy_count_20d=_to_int(row.get("上榜后20天-买入次数")),
        avg_return_20d=_to_float(row.get("上榜后20天-平均涨幅")),
        win_rate_20d=_to_float(row.get("上榜后20天-上涨概率")),
    )


def adapt_block_trade_active_stock_row(row: dict) -> BlockTradeActiveStockItem:
    raw_code = str(row.get("证券代码", "")).strip()
    symbol = normalize_symbol(raw_code) if raw_code else ""
    return BlockTradeActiveStockItem(
        symbol=symbol,
        name=str(row.get("证券简称", "")).strip(),
        latest_price=_to_float(row.get("最新价")),
        change_percent=_to_float(row.get("涨跌幅")),
        last_listed_date=str(row.get("最近上榜日", "")).strip() or None,
        total_listed_count=_to_int(row.get("上榜次数-总计")),
        premium_listed_count=_to_int(row.get("上榜次数-溢价")),
        discount_listed_count=_to_int(row.get("上榜次数-折价")),
        total_turnover=_to_float(row.get("总成交额")),
        avg_discount_rate=_to_float(row.get("折溢率")),
        turnover_to_float_cap=_to_float(row.get("成交总额/流通市值")),
        avg_return_1d=_to_float(row.get("上榜日后平均涨跌幅-1日")),
        avg_return_5d=_to_float(row.get("上榜日后平均涨跌幅-5日")),
        avg_return_10d=_to_float(row.get("上榜日后平均涨跌幅-10日")),
        avg_return_20d=_to_float(row.get("上榜日后平均涨跌幅-20日")),
    )


def build_block_trade_summary_text(
    daily_detail: list,
    daily_stat: list,
    industry_stat: list,
    broker_rank: list,
    active_stock: list,
) -> str:
    parts = []
    if daily_detail:
        parts.append(f"大宗交易明细 {len(daily_detail)} 笔")
    if daily_stat:
        top_discount = [s for s in daily_stat if s.discount_rate is not None and s.discount_rate < -0.05]
        if top_discount:
            parts.append(f"折价>5%个股 {len(top_discount)} 只")
    if industry_stat:
        parts.append(f"涉及行业 {len(industry_stat)} 个")
    if broker_rank:
        parts.append(f"营业部排行 {len(broker_rank)} 家")
    if active_stock:
        parts.append(f"活跃个股 {len(active_stock)} 只")
    if not parts:
        return "无大宗交易数据"
    return "；".join(parts)
