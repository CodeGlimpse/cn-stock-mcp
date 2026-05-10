from __future__ import annotations

from openclaw_stock_mcp.app.models.etf_snapshot import (
    ETFNAVItem,
    ETFScaleItem,
    ETFSpotItem,
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
    if code.startswith("5") or code.startswith("6"):
        return f"{code}.SH"
    return f"{code}.SZ"


def adapt_etf_spot_row(row: dict) -> ETFSpotItem:
    """Adapt a row from ak.fund_etf_spot_em()."""
    code = str(row.get("代码", ""))
    return ETFSpotItem(
        symbol=_format_symbol(code),
        name=str(row.get("名称", "")),
        price=_to_float(row.get("最新价")),
        iopv=_to_float(row.get("IOPV实时估值")),
        discount_rate=_to_float(row.get("基金折价率")),
        change_amount=_to_float(row.get("涨跌额")),
        change_percent=_to_float(row.get("涨跌幅")),
        volume=_to_float(row.get("成交量")),
        turnover=_to_float(row.get("成交额")),
        open=_to_float(row.get("开盘价")),
        high=_to_float(row.get("最高价")),
        low=_to_float(row.get("最低价")),
        prev_close=_to_float(row.get("昨收")),
        amplitude=_to_float(row.get("振幅")),
        turnover_rate=_to_float(row.get("换手率")),
        volume_ratio=_to_float(row.get("量比")),
        main_net_inflow=_to_float(row.get("主力净流入-净额")),
        main_net_inflow_ratio=_to_float(row.get("主力净流入-净占比")),
        super_large_net_inflow=_to_float(row.get("超大单净流入-净额")),
        large_net_inflow=_to_float(row.get("大单净流入-净额")),
        latest_shares=_to_float(row.get("最新份额")),
        circulating_market_cap=_to_float(row.get("流通市值")),
        total_market_cap=_to_float(row.get("总市值")),
        trade_date=str(row.get("数据日期", ""))[:10] or None,
    )


def adapt_etf_scale_row(row: dict) -> ETFScaleItem:
    """Adapt a row from ak.fund_etf_scale_sse()."""
    code = str(row.get("基金代码", ""))
    return ETFScaleItem(
        symbol=_format_symbol(code),
        name=str(row.get("基金简称", "")),
        etf_type=str(row.get("ETF类型", "")) or None,
        date=str(row.get("统计日期", ""))[:10] or None,
        shares=_to_float(row.get("基金份额")),
    )


def adapt_etf_nav_row(row: dict) -> ETFNAVItem:
    """Adapt a row from ak.fund_etf_fund_info_em()."""
    return ETFNAVItem(
        date=str(row.get("净值日期", ""))[:10],
        nav=_to_float(row.get("单位净值")),
        acc_nav=_to_float(row.get("累计净值")),
        daily_growth=_to_float(row.get("日增长率")),
        purchase_status=str(row.get("申购状态", "")) or None,
        redeem_status=str(row.get("赎回状态", "")) or None,
    )


def build_etf_snapshot_summary_text(
    spot: list[ETFSpotItem],
    scale: list[ETFScaleItem],
    nav: list[ETFNAVItem],
) -> str:
    parts: list[str] = []

    if spot:
        parts.append(f"ETF快照{len(spot)}只")
        inflow_pos = [s for s in spot if s.main_net_inflow is not None and s.main_net_inflow > 0]
        if inflow_pos:
            top = inflow_pos[0]
            parts.append(f"主力净流入最高{top.name}({top.main_net_inflow / 1e8:.2f}亿)")
        premium = [s for s in spot if s.discount_rate is not None and s.discount_rate > 0]
        if premium:
            parts.append(f"溢价{len(premium)}只")

    if scale:
        parts.append(f"ETF份额{len(scale)}只")

    if nav:
        latest = nav[-1] if nav else None
        if latest and latest.nav is not None:
            parts.append(f"最新净值{latest.nav:.4f}")
            if latest.daily_growth is not None:
                parts.append(f"日增长{latest.daily_growth:.2f}%")

    return "，".join(parts) if parts else "ETF数据暂无"
