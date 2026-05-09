from __future__ import annotations

from openclaw_stock_mcp.app.models.northbound import (
    NorthboundDailySummary,
    NorthboundFlowRecord,
    NorthboundHoldItem,
)


def _to_float(value) -> float | None:
    if value is None or value == "" or value is False:
        return None
    try:
        return float(value)
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


def adapt_em_hist_row(row: dict) -> NorthboundFlowRecord:
    """Adapt a row from ak.stock_hsgt_hist_em() to NorthboundFlowRecord."""
    date_val = str(row.get("日期", ""))[:10]
    return NorthboundFlowRecord(
        date=date_val,
        net_buy_amount=_to_float(row.get("当日成交净买额")),
        buy_amount=_to_float(row.get("买入成交额")),
        sell_amount=_to_float(row.get("卖出成交额")),
        cumulative_net_buy=_to_float(row.get("历史累计净买额")),
        daily_inflow=_to_float(row.get("当日资金流入")),
        balance=_to_float(row.get("当日余额")),
        hold_market_cap=_to_float(row.get("持股市值")),
        leading_stock=row.get("领涨股") or None,
        leading_stock_change=_to_float(row.get("领涨股-涨跌幅")),
        leading_stock_code=row.get("领涨股-代码") or None,
        csi300=_to_float(row.get("沪深300")),
        csi300_change=_to_float(row.get("沪深300-涨跌幅")),
    )


def build_daily_summary_from_flow_summary(rows: list[dict]) -> NorthboundDailySummary:
    """Build NorthboundDailySummary from ak.stock_hsgt_fund_flow_summary_em() rows."""
    summary = NorthboundDailySummary()

    if not rows:
        return summary

    summary.trade_date = str(rows[0].get("交易日", ""))[:10]
    summary.items = rows

    for row in rows:
        board = str(row.get("板块", ""))
        direction = str(row.get("资金方向", ""))
        if direction == "北向":
            net_buy = _to_float(row.get("成交净买额"))
            inflow = _to_float(row.get("资金净流入"))
            up = _to_int(row.get("上涨数"))
            down = _to_int(row.get("下跌数"))
            if board == "沪股通":
                summary.sh_north_net_buy = net_buy
                summary.sh_north_inflow = inflow
                summary.sh_north_up_count = up
                summary.sh_north_down_count = down
            elif board == "深股通":
                summary.sz_north_net_buy = net_buy
                summary.sz_north_inflow = inflow
                summary.sz_north_up_count = up
                summary.sz_north_down_count = down

    # Total
    sh_val = summary.sh_north_net_buy or 0
    sz_val = summary.sz_north_net_buy or 0
    if summary.sh_north_net_buy is not None or summary.sz_north_net_buy is not None:
        summary.total_north_net_buy = (sh_val or 0) + (sz_val or 0) or None

    return summary


def adapt_em_hold_item(row: dict) -> NorthboundHoldItem:
    """Adapt a row from ak.stock_hsgt_hold_stock_em() to NorthboundHoldItem."""
    code = str(row.get("代码", ""))
    return NorthboundHoldItem(
        symbol=_format_symbol(code),
        name=str(row.get("名称", "")),
        price=_to_float(row.get("今日收盘价")),
        change_percent=_to_float(row.get("今日涨跌幅")),
        hold_shares=_to_float(row.get("今日持股-股数")),
        hold_market_cap=_to_float(row.get("今日持股-市值")),
        hold_pct_float=_to_float(row.get("今日持股-占流通股比")),
        hold_pct_total=_to_float(row.get("今日持股-占总股本比")),
        increase_shares=_to_float(row.get("今日增持估计-股数")),
        increase_market_cap=_to_float(row.get("今日增持估计-市值")),
        increase_pct=_to_float(row.get("今日增持估计-市值增幅")),
        sector=str(row.get("所属板块", "")) or None,
        date=str(row.get("日期", ""))[:10] or None,
    )


def build_northbound_summary_text(
    daily: NorthboundDailySummary | None,
    history: list[NorthboundFlowRecord],
    holdings: list[NorthboundHoldItem],
) -> str:
    """Build readable Chinese summary."""
    parts = []

    if daily and daily.trade_date:
        direction = "净流入" if (daily.total_north_net_buy or 0) > 0 else "净流出"
        total = daily.total_north_net_buy
        if total is not None:
            parts.append(f"北向资金{direction}{abs(total):.2f}亿")
            sh = daily.sh_north_net_buy
            sz = daily.sz_north_net_buy
            if sh is not None:
                parts.append(f"沪股通{sh:.2f}亿")
            if sz is not None:
                parts.append(f"深股通{sz:.2f}亿")
        if daily.sh_north_up_count is not None:
            parts.append(f"沪股通涨跌{daily.sh_north_up_count}/{daily.sh_north_down_count}")

    if history:
        latest = history[-1]
        if latest.hold_market_cap is not None and latest.hold_market_cap > 0:
            mc = latest.hold_market_cap / 1e4 if latest.hold_market_cap > 1e4 else latest.hold_market_cap
            unit = "万亿" if latest.hold_market_cap > 1e4 else "亿"
            parts.append(f"持股市值{mc:.2f}{unit}")
        if latest.leading_stock:
            parts.append(f"领涨股{latest.leading_stock}")

    if holdings:
        top3 = holdings[:3]
        hold_str = "，".join(f"{h.name}({h.increase_pct or 0:.1f}%)" for h in top3 if h.increase_pct is not None)
        if hold_str:
            parts.append(f"增持前列:{hold_str}")

    return "，".join(parts) if parts else "北向资金数据暂无"
