from __future__ import annotations

from openclaw_stock_mcp.app.models.fund_flow import (
    FundFlowResult,
    IndustryFundFlowItem,
    MarketFundFlowItem,
    StockFundFlowItem,
)


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
    return s if s and s != "NaN" and s != "NaT" and s != "--" and s != "-" else None


def adapt_market_fund_flow_row(row: dict) -> MarketFundFlowItem:
    return MarketFundFlowItem(
        date=_clean_str(row.get("日期")),
        sh_close=_to_float(row.get("上证-收盘价")),
        sh_change_pct=_to_float(row.get("上证-涨跌幅")),
        sz_close=_to_float(row.get("深证-收盘价")),
        sz_change_pct=_to_float(row.get("深证-涨跌幅")),
        main_net_inflow=_to_float(row.get("主力净流入-净额")),
        main_net_pct=_to_float(row.get("主力净流入-净占比")),
        huge_net_inflow=_to_float(row.get("超大单净流入-净额")),
        huge_net_pct=_to_float(row.get("超大单净流入-净占比")),
        big_net_inflow=_to_float(row.get("大单净流入-净额")),
        big_net_pct=_to_float(row.get("大单净流入-净占比")),
        mid_net_inflow=_to_float(row.get("中单净流入-净额")),
        mid_net_pct=_to_float(row.get("中单净流入-净占比")),
        small_net_inflow=_to_float(row.get("小单净流入-净额")),
        small_net_pct=_to_float(row.get("小单净流入-净占比")),
    )


def adapt_industry_fund_flow_row(row: dict) -> IndustryFundFlowItem:
    return IndustryFundFlowItem(
        name=_clean_str(row.get("行业")),
        index=_to_float(row.get("行业指数")),
        change_pct=_to_float(row.get("行业-涨跌幅")),
        inflow=_to_float(row.get("流入资金")),
        outflow=_to_float(row.get("流出资金")),
        net_inflow=_to_float(row.get("净额")),
        company_count=_to_int(row.get("公司家数")),
        leader=_clean_str(row.get("领涨股")),
        leader_change_pct=_to_float(row.get("领涨股-涨跌幅")),
        leader_price=_to_float(row.get("当前价")),
    )


def adapt_stock_fund_flow_row(row: dict) -> StockFundFlowItem:
    return StockFundFlowItem(
        date=_clean_str(row.get("日期")),
        close=_to_float(row.get("收盘价")),
        change_pct=_to_float(row.get("涨跌幅")),
        main_net_inflow=_to_float(row.get("主力净流入-净额")),
        main_net_pct=_to_float(row.get("主力净流入-净占比")),
        huge_net_inflow=_to_float(row.get("超大单净流入-净额")),
        huge_net_pct=_to_float(row.get("超大单净流入-净占比")),
        big_net_inflow=_to_float(row.get("大单净流入-净额")),
        big_net_pct=_to_float(row.get("大单净流入-净占比")),
        mid_net_inflow=_to_float(row.get("中单净流入-净额")),
        mid_net_pct=_to_float(row.get("中单净流入-净占比")),
        small_net_inflow=_to_float(row.get("小单净流入-净额")),
        small_net_pct=_to_float(row.get("小单净流入-净占比")),
    )


def build_fund_flow_summary(market: list, industry: list, stock: list) -> str:
    parts = []
    if market:
        latest = market[-1] if market else None
        if latest and latest.main_net_inflow is not None:
            direction = "净流入" if latest.main_net_inflow > 0 else "净流出"
            parts.append(f"全市场近{len(market)}日主力{direction}({latest.main_net_inflow / 1e8:.1f}亿)")
        else:
            parts.append(f"全市场{len(market)}日资金流")
    if industry:
        net_in = [i for i in industry if i.net_inflow is not None and i.net_inflow > 0]
        net_out = [i for i in industry if i.net_inflow is not None and i.net_inflow < 0]
        parts.append(f"行业 {len(industry)} 个(净流入 {len(net_in)} / 净流出 {len(net_out)})")
    if stock:
        parts.append(f"个股 {len(stock)} 日资金流")
    if not parts:
        return "无资金流数据"
    return "；".join(parts)
