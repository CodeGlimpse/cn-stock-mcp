from __future__ import annotations

from cn_stock_mcp.app.models.margin_trading import (
    MarginDetailItem,
    MarginSummaryItem,
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


def _format_symbol(code: str, exchange: str | None = None) -> str:
    code = str(code).strip()
    if len(code) != 6:
        return code
    if exchange == "SSE" or code.startswith("6") or code.startswith("5"):
        return f"{code}.SH"
    return f"{code}.SZ"


def adapt_margin_sse_summary_row(row: dict) -> MarginSummaryItem:
    """Adapt a row from ak.stock_margin_sse()."""
    date_val = str(row.get("信用交易日期", ""))
    # SSE dates are like "20250508"
    if len(date_val) == 8 and date_val.isdigit():
        date_val = f"{date_val[:4]}-{date_val[4:6]}-{date_val[6:8]}"
    return MarginSummaryItem(
        trade_date=date_val[:10] or None,
        financing_balance=_to_float(row.get("融资余额")),
        financing_buy=_to_float(row.get("融资买入额")),
        financing_repay=_to_float(row.get("融资偿还额")) if "融资偿还额" in row else None,
        securities_volume=_to_float(row.get("融券余量")),
        securities_amount=_to_float(row.get("融券余量金额")),
        securities_sell=_to_float(row.get("融券卖出量")),
        total_balance=_to_float(row.get("融资融券余额")),
        exchange="SSE",
    )


def adapt_margin_szse_summary_row(row: dict) -> MarginSummaryItem:
    """Adapt a row from ak.stock_margin_szse()."""
    # SZSE summary values are in 亿元
    return MarginSummaryItem(
        trade_date=None,
        financing_balance=_to_float(row.get("融资余额")),
        financing_buy=_to_float(row.get("融资买入额")),
        securities_volume=_to_float(row.get("融券余量")),
        securities_amount=_to_float(row.get("融券余额")),
        securities_sell=_to_float(row.get("融券卖出量")),
        total_balance=_to_float(row.get("融资融券余额")),
        exchange="SZSE",
    )


def adapt_margin_sse_detail_row(row: dict) -> MarginDetailItem:
    """Adapt a row from ak.stock_margin_detail_sse()."""
    code = str(row.get("标的证券代码", ""))
    return MarginDetailItem(
        symbol=_format_symbol(code, "SSE"),
        name=str(row.get("标的证券简称", "")) or None,
        financing_balance=_to_float(row.get("融资余额")),
        financing_buy=_to_float(row.get("融资买入额")),
        financing_repay=_to_float(row.get("融资偿还额")),
        securities_volume=_to_float(row.get("融券余量")),
        securities_sell=_to_float(row.get("融券卖出量")),
        securities_repay=_to_float(row.get("融券偿还量")),
        exchange="SSE",
    )


def adapt_margin_szse_detail_row(row: dict) -> MarginDetailItem:
    """Adapt a row from ak.stock_margin_detail_szse()."""
    code = str(row.get("证券代码", ""))
    return MarginDetailItem(
        symbol=_format_symbol(code, "SZSE"),
        name=str(row.get("证券简称", "")) or None,
        financing_balance=_to_float(row.get("融资余额")),
        financing_buy=_to_float(row.get("融资买入额")),
        securities_volume=_to_float(row.get("融券余量")),
        securities_sell=_to_float(row.get("融券卖出量")),
        securities_amount=_to_float(row.get("融券余额")),
        total_balance=_to_float(row.get("融资融券余额")),
        exchange="SZSE",
    )


def build_margin_summary_text(
    summary: list[MarginSummaryItem],
    detail: list[MarginDetailItem],
) -> str:
    parts: list[str] = []

    if summary:
        latest = summary[-1]
        if latest.financing_balance is not None:
            fb = latest.financing_balance
            if fb > 1e8:
                parts.append(f"融资余额{fb / 1e8:.0f}亿")
            else:
                parts.append(f"融资余额{fb:.0f}亿")
        if latest.total_balance is not None:
            tb = latest.total_balance
            if tb > 1e8:
                parts.append(f"两融余额{tb / 1e8:.0f}亿")
            else:
                parts.append(f"两融余额{tb:.0f}亿")

    if detail:
        buy_top = sorted(
            [d for d in detail if d.financing_buy is not None],
            key=lambda d: d.financing_buy,
            reverse=True,
        )
        if buy_top:
            top = buy_top[0]
            parts.append(f"融资买入最多{top.name}({top.financing_buy / 1e8:.2f}亿)")

        sell_top = sorted(
            [d for d in detail if d.securities_sell is not None],
            key=lambda d: d.securities_sell,
            reverse=True,
        )
        if sell_top:
            top = sell_top[0]
            parts.append(f"融券卖出最多{top.name}")

    return "，".join(parts) if parts else "融资融券数据暂无"
