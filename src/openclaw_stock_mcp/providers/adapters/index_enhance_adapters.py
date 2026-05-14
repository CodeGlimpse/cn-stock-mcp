from __future__ import annotations

from collections import defaultdict

from openclaw_stock_mcp.app.models.index_enhance import (
    IndexEnhanceIndustryCoverage,
    IndexEnhanceIndustryExposureItem,
    IndexEnhanceMemberItem,
    IndexEnhanceSummary,
    IndexEnhanceWeightExposure,
)


def normalize_index_code(value: str) -> str:
    code = (value or "").strip()
    if "." in code:
        code = code.split(".", 1)[0]
    return code


def normalize_stock_symbol(value: str, exchange: str | None = None) -> str:
    code = (value or "").strip()
    if "." in code:
        return code
    ex = (exchange or "").upper()
    if ex in {"SH", "SZ", "BJ"}:
        return f"{code}.{ex}"
    if code.startswith(("6", "9")):
        return f"{code}.SH"
    if code.startswith(("4", "8")):
        return f"{code}.BJ"
    return f"{code}.SZ"


def calc_index_return(history_items: list) -> float | None:
    if not history_items:
        return None
    latest = history_items[-1]
    change_pct = getattr(latest, "change_percent", None)
    if change_pct is None and isinstance(latest, dict):
        change_pct = latest.get("change_percent")
    if change_pct is not None:
        return float(change_pct)

    close = getattr(latest, "close", None)
    prev_close = getattr(latest, "prev_close", None)
    if isinstance(latest, dict):
        close = latest.get("close", close)
        prev_close = latest.get("prev_close", prev_close)
    if close is None or prev_close in (None, 0):
        return None
    return (float(close) - float(prev_close)) / float(prev_close) * 100.0


def build_enhance_members(constituents: list, quotes: dict[str, object], benchmark_return: float | None, industries: dict[str, str | None] | None = None) -> list[IndexEnhanceMemberItem]:
    members = []
    industries = industries or {}
    for c in constituents:
        raw_symbol = c.get("symbol") if isinstance(c, dict) else getattr(c, "symbol", "")
        raw_exchange = c.get("exchange") if isinstance(c, dict) else getattr(c, "exchange", None)
        raw_name = c.get("name") if isinstance(c, dict) else getattr(c, "name", None)
        weight = c.get("weight") if isinstance(c, dict) else getattr(c, "weight", None)
        symbol = normalize_stock_symbol(raw_symbol, raw_exchange)
        q = quotes.get(symbol)
        change_percent = getattr(q, "change_percent", None) if q is not None else None
        price = getattr(q, "price", None) if q is not None else None
        source = getattr(q, "source", None) if q is not None else None
        contribution = None
        if weight is not None and change_percent is not None:
            contribution = float(weight) * float(change_percent) / 100.0
        excess = None if benchmark_return is None or change_percent is None else float(change_percent) - float(benchmark_return)
        members.append(IndexEnhanceMemberItem(
            symbol=symbol,
            name=raw_name or (getattr(q, "name", None) if q is not None else None),
            industry=industries.get(symbol),
            weight=weight,
            price=price,
            change_percent=change_percent,
            weighted_contribution=contribution,
            excess_vs_index=excess,
            source=source,
        ))
    return members


def calc_enhanced_return(members: list[IndexEnhanceMemberItem], weighting: str) -> tuple[float | None, float | None]:
    valid = [m for m in members if m.change_percent is not None]
    if not valid:
        return None, None
    if weighting == "equal":
        return sum(float(m.change_percent) for m in valid) / len(valid), None

    weighted = [m for m in valid if m.weight is not None]
    if not weighted:
        return sum(float(m.change_percent) for m in valid) / len(valid), None
    total_weight = sum(float(m.weight) for m in weighted)
    if total_weight <= 0:
        return None, total_weight
    enhanced = sum(float(m.weight) * float(m.change_percent) for m in weighted) / total_weight
    return enhanced, total_weight


def build_index_enhance_summary(index_code: str, index_name: str | None, benchmark_return: float | None, enhanced_return: float | None, members: list[IndexEnhanceMemberItem], total_weight: float | None, weighting: str) -> IndexEnhanceSummary:
    outperform = 0
    underperform = 0
    if benchmark_return is not None:
        outperform = sum(1 for m in members if m.change_percent is not None and m.change_percent > benchmark_return)
        underperform = sum(1 for m in members if m.change_percent is not None and m.change_percent < benchmark_return)
    excess = None if benchmark_return is None or enhanced_return is None else enhanced_return - benchmark_return
    return IndexEnhanceSummary(
        index_code=index_code,
        index_name=index_name,
        benchmark_return=benchmark_return,
        enhanced_return=enhanced_return,
        excess_return=excess,
        member_count=len(members),
        total_weight=total_weight,
        outperform_count=outperform,
        underperform_count=underperform,
        method=f"top_weight_{weighting}_quote",
    )


def build_weight_exposure(members: list[IndexEnhanceMemberItem]) -> IndexEnhanceWeightExposure:
    weighted = [m for m in members if m.weight is not None]
    weighted.sort(key=lambda x: float(x.weight or 0), reverse=True)
    total_weight = sum(float(m.weight or 0) for m in weighted) if weighted else None

    def _ratio(n: int):
        if not weighted or not total_weight:
            return None
        return sum(float(m.weight or 0) for m in weighted[:n]) / total_weight * 100.0

    return IndexEnhanceWeightExposure(
        total_weight=total_weight,
        top1_weight_percent=_ratio(1),
        top3_weight_percent=_ratio(3),
        top5_weight_percent=_ratio(5),
        top10_weight_percent=_ratio(10),
        top_members=weighted[:10],
    )


def build_industry_exposure(members: list[IndexEnhanceMemberItem]) -> tuple[list[IndexEnhanceIndustryExposureItem], IndexEnhanceIndustryCoverage]:
    groups: dict[str, list[IndexEnhanceMemberItem]] = defaultdict(list)
    known = 0
    unknown = 0
    for m in members:
        industry = (m.industry or "").strip() or "unknown"
        groups[industry].append(m)
        if industry == "unknown":
            unknown += 1
        else:
            known += 1

    rows: list[IndexEnhanceIndustryExposureItem] = []
    for industry, items in groups.items():
        weights = [float(i.weight) for i in items if i.weight is not None]
        changes = [float(i.change_percent) for i in items if i.change_percent is not None]
        contribs = [float(i.weighted_contribution) for i in items if i.weighted_contribution is not None]
        excess_contribs = [float(i.weight or 0) * float(i.excess_vs_index or 0) / 100.0 for i in items if i.weight is not None and i.excess_vs_index is not None]
        rows.append(IndexEnhanceIndustryExposureItem(
            industry=industry,
            member_count=len(items),
            weight_sum=sum(weights) if weights else None,
            avg_change_percent=(sum(changes) / len(changes)) if changes else None,
            contribution_sum=sum(contribs) if contribs else None,
            excess_contribution_sum=sum(excess_contribs) if excess_contribs else None,
        ))
    rows.sort(key=lambda x: float(x.weight_sum or 0), reverse=True)
    total = known + unknown
    coverage = IndexEnhanceIndustryCoverage(
        known_count=known,
        unknown_count=unknown,
        coverage_ratio=(known / total) if total else None,
    )
    return rows, coverage


def build_index_enhance_summary_text(summary: IndexEnhanceSummary) -> str:
    if summary.enhanced_return is None or summary.benchmark_return is None:
        return f"{summary.index_code} 指数增强对比：有效数据不足"
    direction = "跑赢" if (summary.excess_return or 0) >= 0 else "跑输"
    return (
        f"{summary.index_code} 增强组合{summary.enhanced_return:.2f}%，"
        f"基准{summary.benchmark_return:.2f}%，{direction}{abs(summary.excess_return or 0):.2f}个百分点；"
        f"样本{summary.member_count}只，跑赢成分{summary.outperform_count}只/跑输{summary.underperform_count}只"
    )
