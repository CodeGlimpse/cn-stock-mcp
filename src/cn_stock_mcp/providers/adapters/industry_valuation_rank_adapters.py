from __future__ import annotations

from statistics import median

from cn_stock_mcp.app.models.industry_valuation_rank import (
    IndustryValuationItem,
    IndustryValuationSummary,
)


def _safe_mean(vals: list[float]) -> float | None:
    return (sum(vals) / len(vals)) if vals else None


def build_sector_item(sector_name: str, symbols: list[str], quotes: list) -> IndustryValuationItem:
    pe_vals = [float(q.pe) for q in quotes if q.pe is not None]
    pb_vals = [float(q.pb) for q in quotes if q.pb is not None]
    pe_positive_vals = [v for v in pe_vals if v > 0]
    pb_below_one_vals = [v for v in pb_vals if v < 1]

    quote_coverage = len(quotes)
    item = IndustryValuationItem(
        sector_name=sector_name,
        member_count=len(symbols),
        quote_coverage_count=quote_coverage,
        pe_median=median(pe_positive_vals) if pe_positive_vals else None,
        pb_median=median(pb_vals) if pb_vals else None,
        pe_mean=_safe_mean(pe_positive_vals),
        pb_mean=_safe_mean(pb_vals),
        pe_positive_ratio=(len(pe_positive_vals) / len(pe_vals)) if pe_vals else None,
        pb_below_one_ratio=(len(pb_below_one_vals) / len(pb_vals)) if pb_vals else None,
        sample_symbols=symbols[:5],
    )
    return item


def rank_items(items: list[IndustryValuationItem], sort_by: str = "pe_median", descending: bool = False) -> list[IndustryValuationItem]:
    pe_sorted = sorted([x for x in items if x.pe_median is not None], key=lambda x: x.pe_median)
    for i, x in enumerate(pe_sorted, 1):
        x.pe_rank = i

    pb_sorted = sorted([x for x in items if x.pb_median is not None], key=lambda x: x.pb_median)
    for i, x in enumerate(pb_sorted, 1):
        x.pb_rank = i

    pe_count = len(pe_sorted)
    pb_count = len(pb_sorted)
    for x in items:
        pe_pct = ((x.pe_rank - 1) / (pe_count - 1)) if (x.pe_rank and pe_count > 1) else None
        pb_pct = ((x.pb_rank - 1) / (pb_count - 1)) if (x.pb_rank and pb_count > 1) else None
        vals = [v for v in [pe_pct, pb_pct] if v is not None]
        pct = sum(vals) / len(vals) if vals else None
        x.valuation_percentile = pct
        tags = []
        if pct is None:
            x.valuation_label = "unknown"
            tags.append("insufficient_pe_pb")
        elif pct <= 0.30:
            x.valuation_label = "low"
            tags.append("low_valuation")
        elif pct >= 0.70:
            x.valuation_label = "high"
            tags.append("high_valuation")
        else:
            x.valuation_label = "neutral"
            tags.append("neutral_valuation")

        if x.pb_below_one_ratio is not None and x.pb_below_one_ratio >= 0.2:
            tags.append("many_below_book")
        x.reason_tags = tags

    key_map = {
        "pe_median": lambda x: x.pe_median if x.pe_median is not None else (float("inf") if not descending else float("-inf")),
        "pb_median": lambda x: x.pb_median if x.pb_median is not None else (float("inf") if not descending else float("-inf")),
        "valuation_percentile": lambda x: x.valuation_percentile if x.valuation_percentile is not None else (float("inf") if not descending else float("-inf")),
        "quote_coverage_count": lambda x: x.quote_coverage_count,
    }
    key_fn = key_map.get(sort_by, key_map["pe_median"])
    return sorted(items, key=key_fn, reverse=descending)


def build_summary(items: list[IndustryValuationItem]) -> IndustryValuationSummary:
    return IndustryValuationSummary(
        sector_count=len(items),
        priced_sector_count=sum(1 for x in items if x.pe_median is not None or x.pb_median is not None),
        low_valuation_count=sum(1 for x in items if x.valuation_label == "low"),
        neutral_valuation_count=sum(1 for x in items if x.valuation_label == "neutral"),
        high_valuation_count=sum(1 for x in items if x.valuation_label == "high"),
    )


def build_summary_text(summary: IndustryValuationSummary) -> str:
    return (
        f"行业样本{summary.sector_count}，可估值{summary.priced_sector_count}，"
        f"低估/中性/高估={summary.low_valuation_count}/{summary.neutral_valuation_count}/{summary.high_valuation_count}"
    )
