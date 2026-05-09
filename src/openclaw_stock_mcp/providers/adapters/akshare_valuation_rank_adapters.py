from __future__ import annotations

from openclaw_stock_mcp.app.models.valuation_rank import (
    MarketValuationSnapshot,
    StockValuationItem,
    ValuationRankSummary,
)


def _to_float(value):
    if value is None or value == "" or value is False:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value):
    if value is None or value == "" or value is False:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def build_market_valuation_snapshot(
    pe_row: dict | None,
    pb_row: dict | None,
    dy_row: dict | None,
    hl_row: dict | None,
) -> MarketValuationSnapshot:
    date = None
    for row in [pe_row, pb_row, dy_row, hl_row]:
        if row:
            date = str(row.get("date") or row.get("日期") or "")[:10] or date

    return MarketValuationSnapshot(
        date=date,
        pe_ttm_median=_to_float((pe_row or {}).get("middlePETTM")),
        pe_ttm_avg=_to_float((pe_row or {}).get("averagePETTM")),
        pe_lyr_median=_to_float((pe_row or {}).get("middlePELYR")),
        pe_lyr_avg=_to_float((pe_row or {}).get("averagePELYR")),
        pb_median=_to_float((pb_row or {}).get("middlePB")),
        pb_equal_weight_avg=_to_float((pb_row or {}).get("equalWeightAveragePB")),
        pe_ttm_quantile_all=_to_float((pe_row or {}).get("quantileInAllHistoryMiddlePeTtm")),
        pe_ttm_quantile_10y=_to_float((pe_row or {}).get("quantileInRecent10YearsMiddlePeTtm")),
        pb_quantile_all=_to_float((pb_row or {}).get("quantileInAllHistoryMiddlePB")),
        pb_quantile_10y=_to_float((pb_row or {}).get("quantileInRecent10YearsMiddlePB")),
        dividend_yield=_to_float((dy_row or {}).get("股息率")),
        high20_count=_to_int((hl_row or {}).get("high20")),
        low20_count=_to_int((hl_row or {}).get("low20")),
        high60_count=_to_int((hl_row or {}).get("high60")),
        low60_count=_to_int((hl_row or {}).get("low60")),
        close=_to_float((hl_row or {}).get("close")),
    )


def _market_temperature_score(snapshot: MarketValuationSnapshot | None) -> float | None:
    if snapshot is None:
        return None
    pe_q = snapshot.pe_ttm_quantile_10y if snapshot.pe_ttm_quantile_10y is not None else snapshot.pe_ttm_quantile_all
    pb_q = snapshot.pb_quantile_10y if snapshot.pb_quantile_10y is not None else snapshot.pb_quantile_all
    if pe_q is None and pb_q is None:
        return None
    vals = [v for v in [pe_q, pb_q] if v is not None]
    return sum(vals) / len(vals)


def _market_temperature_label(score: float | None) -> str | None:
    if score is None:
        return None
    if score >= 0.85:
        return "overheated"
    if score >= 0.70:
        return "hot"
    if score >= 0.35:
        return "neutral"
    if score >= 0.20:
        return "cool"
    return "deep_value"


def rank_stock_valuation_items(items: list[StockValuationItem], sort_by: str = "pe", descending: bool = False) -> list[StockValuationItem]:
    pe_sorted = sorted([it for it in items if it.pe is not None], key=lambda x: x.pe or 0)
    for idx, it in enumerate(pe_sorted, start=1):
        it.rank_pe = idx

    pb_sorted = sorted([it for it in items if it.pb is not None], key=lambda x: x.pb or 0)
    for idx, it in enumerate(pb_sorted, start=1):
        it.rank_pb = idx

    # Label each stock by percentile in the provided universe
    pe_count = len(pe_sorted)
    pb_count = len(pb_sorted)
    for it in items:
        pe_pct = ((it.rank_pe - 1) / (pe_count - 1)) if (it.rank_pe is not None and pe_count > 1) else None
        pb_pct = ((it.rank_pb - 1) / (pb_count - 1)) if (it.rank_pb is not None and pb_count > 1) else None
        tags = []
        vals = [v for v in [pe_pct, pb_pct] if v is not None]
        avg_pct = (sum(vals) / len(vals)) if vals else None

        if avg_pct is None:
            it.valuation_label = "unknown"
            tags.append("missing_pe_pb")
        elif avg_pct <= 0.30:
            it.valuation_label = "low"
            tags.append("low_valuation")
        elif avg_pct >= 0.70:
            it.valuation_label = "high"
            tags.append("high_valuation")
        else:
            it.valuation_label = "neutral"
            tags.append("neutral_valuation")

        if it.pe is not None and it.pe < 0:
            tags.append("negative_pe")
        if it.pb is not None and it.pb < 1:
            tags.append("below_book_pb")

        it.reason_tags = tags

    key_map = {
        "pe": lambda x: x.pe if x.pe is not None else (float("inf") if not descending else float("-inf")),
        "pb": lambda x: x.pb if x.pb is not None else (float("inf") if not descending else float("-inf")),
        "market_cap": lambda x: x.market_cap if x.market_cap is not None else (float("-inf") if descending else float("inf")),
    }
    key_fn = key_map.get(sort_by, key_map["pe"])
    return sorted(items, key=key_fn, reverse=descending)


def build_valuation_summary(items: list[StockValuationItem], snapshot: MarketValuationSnapshot | None) -> ValuationRankSummary:
    total = len(items)
    pe_count = sum(1 for it in items if it.pe is not None)
    pb_count = sum(1 for it in items if it.pb is not None)
    low_count = sum(1 for it in items if it.valuation_label == "low")
    neutral_count = sum(1 for it in items if it.valuation_label == "neutral")
    high_count = sum(1 for it in items if it.valuation_label == "high")

    score = _market_temperature_score(snapshot)
    label = _market_temperature_label(score)

    return ValuationRankSummary(
        stock_count=total,
        pe_available_count=pe_count,
        pb_available_count=pb_count,
        low_valuation_count=low_count,
        neutral_valuation_count=neutral_count,
        high_valuation_count=high_count,
        market_temperature=label,
        market_temperature_score=score,
    )


def build_valuation_summary_text(summary: ValuationRankSummary, snapshot: MarketValuationSnapshot | None) -> str:
    parts = []
    if summary.market_temperature:
        parts.append(f"市场估值温度: {summary.market_temperature}")
    if summary.market_temperature_score is not None:
        parts.append(f"温度分数{summary.market_temperature_score:.2f}")
    if snapshot and snapshot.pe_ttm_median is not None and snapshot.pb_median is not None:
        parts.append(f"全A中位PE(TTM){snapshot.pe_ttm_median:.2f}")
        parts.append(f"中位PB{snapshot.pb_median:.2f}")
    if snapshot and snapshot.dividend_yield is not None:
        parts.append(f"股息率{snapshot.dividend_yield:.2f}%")
    parts.append(f"样本{summary.stock_count}只")
    parts.append(f"低估/中性/高估={summary.low_valuation_count}/{summary.neutral_valuation_count}/{summary.high_valuation_count}")
    return "，".join(parts)
