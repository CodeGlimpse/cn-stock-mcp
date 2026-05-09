from __future__ import annotations

from openclaw_stock_mcp.app.models.capital_flow import CapitalFlowRecord, MarketFundFlowSummary, SectorFundFlowItem


def _to_float(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def adapt_akshare_market_fund_flow(row: dict) -> CapitalFlowRecord:
    """Adapt a row from ak.stock_market_fund_flow() to CapitalFlowRecord."""
    date_val = str(row.get("日期", ""))[:10]
    return CapitalFlowRecord(
        date=date_val,
        close=_to_float(row.get("上证-收盘价")),
        change_percent=_to_float(row.get("上证-涨跌幅")),
        main_net_inflow=_to_float(row.get("主力净流入-净额")),
        main_net_inflow_pct=_to_float(row.get("主力净流入-净占比")),
        super_large_net_inflow=_to_float(row.get("超大单净流入-净额")),
        super_large_net_inflow_pct=_to_float(row.get("超大单净流入-净占比")),
        large_net_inflow=_to_float(row.get("大单净流入-净额")),
        large_net_inflow_pct=_to_float(row.get("大单净流入-净占比")),
        medium_net_inflow=_to_float(row.get("中单净流入-净额")),
        medium_net_inflow_pct=_to_float(row.get("中单净流入-净占比")),
        small_net_inflow=_to_float(row.get("小单净流入-净额")),
        small_net_inflow_pct=_to_float(row.get("小单净流入-净占比")),
    )


def adapt_akshare_individual_fund_flow(row: dict) -> CapitalFlowRecord:
    """Adapt a row from ak.stock_individual_fund_flow() to CapitalFlowRecord."""
    date_val = str(row.get("日期", ""))[:10]
    return CapitalFlowRecord(
        date=date_val,
        close=_to_float(row.get("收盘价")),
        change_percent=_to_float(row.get("涨跌幅")),
        main_net_inflow=_to_float(row.get("主力净流入-净额")),
        main_net_inflow_pct=_to_float(row.get("主力净流入-净占比")),
        super_large_net_inflow=_to_float(row.get("超大单净流入-净额")),
        super_large_net_inflow_pct=_to_float(row.get("超大单净流入-净占比")),
        large_net_inflow=_to_float(row.get("大单净流入-净额")),
        large_net_inflow_pct=_to_float(row.get("大单净流入-净占比")),
        medium_net_inflow=_to_float(row.get("中单净流入-净额")),
        medium_net_inflow_pct=_to_float(row.get("中单净流入-净占比")),
        small_net_inflow=_to_float(row.get("小单净流入-净额")),
        small_net_inflow_pct=_to_float(row.get("小单净流入-净占比")),
    )


def adapt_akshare_sector_fund_flow(row: dict) -> SectorFundFlowItem:
    """Adapt a row from ak.stock_fund_flow_industry/concept() to SectorFundFlowItem."""
    return SectorFundFlowItem(
        rank=_to_int(row.get("序号")),
        sector_name=str(row.get("行业", "")),
        sector_index=_to_float(row.get("行业指数")),
        sector_change_percent=_to_float(row.get("行业-涨跌幅")),
        inflow=_to_float(row.get("流入资金")),
        outflow=_to_float(row.get("流出资金")),
        net_amount=_to_float(row.get("净额")),
        company_count=_to_int(row.get("公司家数")),
        leading_stock=str(row.get("领涨股", "")) or None,
        leading_stock_change_percent=_to_float(row.get("领涨股-涨跌幅")),
        leading_stock_price=_to_float(row.get("当前价")),
    )


def build_market_fund_flow_summary(records: list[CapitalFlowRecord]) -> MarketFundFlowSummary:
    """Build a summary from the most recent market fund flow record."""
    if not records:
        return MarketFundFlowSummary()

    latest = records[-1]
    direction = "neutral"
    if latest.main_net_inflow is not None:
        if latest.main_net_inflow > 0:
            direction = "inflow"
        elif latest.main_net_inflow < 0:
            direction = "outflow"

    return MarketFundFlowSummary(
        total_main_net_inflow=latest.main_net_inflow,
        avg_main_net_inflow_pct=latest.main_net_inflow_pct,
        total_super_large_net_inflow=latest.super_large_net_inflow,
        total_large_net_inflow=latest.large_net_inflow,
        total_medium_net_inflow=latest.medium_net_inflow,
        total_small_net_inflow=latest.small_net_inflow,
        main_inflow_direction=direction,
    )
