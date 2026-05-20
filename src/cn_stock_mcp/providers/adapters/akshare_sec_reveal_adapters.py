from __future__ import annotations

from cn_stock_mcp.app.models.sec_reveal import (
    ActiveBrokerItem,
    InstitutionDetailItem,
    InstitutionTraceItem,
    SeatDetailItem,
)
from cn_stock_mcp.providers.adapters.broker_tags import broker_tags, summarize_broker_tags


def _to_float(value):
    if value is None or value == "" or value == "NaN" or value == "-" or value == "--":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value):
    if value is None or value == "" or value == "NaN" or value == "-" or value == "--":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _clean_str(value):
    if value is None:
        return None
    s = str(value).strip()
    return s if s and s not in {"NaN", "NaT", "--", "-"} else None


def adapt_seat_detail_row(row: dict, side: str | None = None) -> SeatDetailItem:
    broker_name = _clean_str(row.get("交易营业部名称"))
    return SeatDetailItem(
        rank=_to_int(row.get("序号")),
        broker_name=broker_name,
        broker_tags=broker_tags(broker_name),
        buy_amount=_to_float(row.get("买入金额")),
        buy_ratio=_to_float(row.get("买入金额-占总成交比例")),
        sell_amount=_to_float(row.get("卖出金额")),
        sell_ratio=_to_float(row.get("卖出金额-占总成交比例")),
        net_amount=_to_float(row.get("净额")),
        reason_type=_clean_str(row.get("类型")),
        side=side,
    )


def adapt_active_broker_row(row: dict) -> ActiveBrokerItem:
    broker_name = _clean_str(row.get("营业部名称"))
    return ActiveBrokerItem(
        rank=_to_int(row.get("序号")),
        broker_name=broker_name,
        broker_tags=broker_tags(broker_name),
        trade_date=_clean_str(row.get("上榜日")),
        buy_stock_count=_to_int(row.get("买入个股数")),
        sell_stock_count=_to_int(row.get("卖出个股数")),
        buy_amount=_to_float(row.get("买入总金额")),
        sell_amount=_to_float(row.get("卖出总金额")),
        net_amount=_to_float(row.get("总买卖净额")),
        bought_stocks=_clean_str(row.get("买入股票")),
        broker_code=_clean_str(row.get("营业部代码")),
    )


def adapt_institution_detail_row(row: dict) -> InstitutionDetailItem:
    buy = _to_float(row.get("机构席位买入额"))
    sell = _to_float(row.get("机构席位卖出额"))
    net = None if buy is None and sell is None else (buy or 0.0) - (sell or 0.0)
    return InstitutionDetailItem(
        code=_clean_str(row.get("股票代码")),
        name=_clean_str(row.get("股票名称")),
        trade_date=_clean_str(row.get("交易日期")),
        inst_buy_amount=buy,
        inst_sell_amount=sell,
        inst_net_amount=net,
        reason_type=_clean_str(row.get("类型")),
    )


def adapt_institution_trace_row(row: dict) -> InstitutionTraceItem:
    return InstitutionTraceItem(
        code=_clean_str(row.get("股票代码")),
        name=_clean_str(row.get("股票名称")),
        total_buy_amount=_to_float(row.get("累积买入额")),
        buy_count=_to_int(row.get("买入次数")),
        total_sell_amount=_to_float(row.get("累积卖出额")),
        sell_count=_to_int(row.get("卖出次数")),
        net_amount=_to_float(row.get("净额")),
    )


def build_sec_reveal_summary(stock_buy, stock_sell, active, inst_detail, inst_trace) -> str:
    parts = []
    tag_summary = summarize_broker_tags([*stock_buy, *stock_sell, *active])
    if stock_buy or stock_sell:
        buy_net = sum((i.net_amount or 0.0) for i in stock_buy)
        sell_net = sum((i.net_amount or 0.0) for i in stock_sell)
        parts.append(f"个股席位买榜{len(stock_buy)}席/卖榜{len(stock_sell)}席，合计净额{(buy_net + sell_net) / 1e8:.2f}亿")
    if active:
        net_in = [i for i in active if i.net_amount is not None and i.net_amount > 0]
        parts.append(f"活跃营业部{len(active)}家，净买入{len(net_in)}家")
    if inst_detail:
        pos = [i for i in inst_detail if i.inst_net_amount is not None and i.inst_net_amount > 0]
        parts.append(f"机构明细{len(inst_detail)}条，净买入{len(pos)}条")
    if inst_trace:
        pos = [i for i in inst_trace if i.net_amount is not None and i.net_amount > 0]
        parts.append(f"机构追踪{len(inst_trace)}只，净买入{len(pos)}只")
    if tag_summary:
        top_tags = "、".join(f"{k}{v}" for k, v in sorted(tag_summary.items(), key=lambda x: x[1], reverse=True)[:3])
        parts.append(f"席位标签：{top_tags}")
    return "；".join(parts) if parts else "无席位数据"
