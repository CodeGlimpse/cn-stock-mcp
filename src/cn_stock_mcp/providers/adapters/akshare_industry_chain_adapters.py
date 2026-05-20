from __future__ import annotations

from cn_stock_mcp.app.models.industry_chain import ConceptListItem, IndustryListItem


def _to_float(value):
    if value is None or value == "" or value == "NaN" or value == "-":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value):
    if value is None or value == "" or value == "NaN" or value == "-":
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


def adapt_industry_row(row: dict) -> IndustryListItem:
    return IndustryListItem(
        name=_clean_str(row.get("板块")),
        code=None,
        change_pct=_to_float(row.get("涨跌幅")),
        volume=_to_float(row.get("总成交量")),
        turnover=_to_float(row.get("总成交额")),
        net_inflow=_to_float(row.get("净流入")),
        up_count=_to_int(row.get("上涨家数")),
        down_count=_to_int(row.get("下跌家数")),
        avg_price=_to_float(row.get("均价")),
        leader=_clean_str(row.get("领涨股")),
        leader_price=_to_float(row.get("领涨股-最新价")),
        leader_change_pct=_to_float(row.get("领涨股-涨跌幅")),
    )


def adapt_concept_row(row: dict) -> ConceptListItem:
    return ConceptListItem(
        name=_clean_str(row.get("概念名称")),
        code=None,
        date=_clean_str(row.get("日期")),
        driver_event=_clean_str(row.get("驱动事件")),
        leader=_clean_str(row.get("龙头股")),
        member_count=_to_int(row.get("成分股数量")),
    )


def build_industry_chain_summary(industry: list, concept: list) -> str:
    parts = []
    if industry:
        up = [i for i in industry if i.change_pct is not None and i.change_pct > 0]
        down = [i for i in industry if i.change_pct is not None and i.change_pct < 0]
        parts.append(f"行业 {len(industry)} 个（涨 {len(up)} 跌 {len(down)}）")
    if concept:
        parts.append(f"概念板块 {len(concept)} 个")
    if not parts:
        return "无产业链数据"
    return "；".join(parts)
