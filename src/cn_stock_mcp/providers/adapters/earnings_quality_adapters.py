from __future__ import annotations

from cn_stock_mcp.app.models.earnings_quality import EarningsQualityMetrics, EarningsQualityResult
from cn_stock_mcp.app.models.financial import FinancialSnapshot


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def build_metrics(snapshot: FinancialSnapshot, symbol: str) -> EarningsQualityMetrics:
    deduct_ratio = None
    if snapshot.net_profit and snapshot.deduct_net_profit is not None and snapshot.net_profit != 0:
        deduct_ratio = snapshot.deduct_net_profit / snapshot.net_profit

    growth_gap = None
    if snapshot.net_profit_yoy is not None and snapshot.deduct_net_profit_yoy is not None:
        growth_gap = snapshot.net_profit_yoy - snapshot.deduct_net_profit_yoy

    cash_eps_ratio = None
    if snapshot.basic_eps and snapshot.per_operating_cash_flow is not None and snapshot.basic_eps != 0:
        cash_eps_ratio = snapshot.per_operating_cash_flow / snapshot.basic_eps

    return EarningsQualityMetrics(
        symbol=symbol,
        report_date=snapshot.report_date,
        quarter_name=snapshot.quarter_name,
        net_profit=snapshot.net_profit,
        deduct_net_profit=snapshot.deduct_net_profit,
        net_profit_yoy=snapshot.net_profit_yoy,
        deduct_net_profit_yoy=snapshot.deduct_net_profit_yoy,
        operating_revenue=snapshot.operating_revenue,
        revenue_yoy=snapshot.revenue_yoy,
        basic_eps=snapshot.basic_eps,
        per_operating_cash_flow=snapshot.per_operating_cash_flow,
        cash_eps_ratio=cash_eps_ratio,
        roe_weighted=snapshot.roe_weighted,
        sale_net_margin=snapshot.sale_net_margin,
        assets_debt_ratio=snapshot.assets_debt_ratio,
        deduct_profit_ratio=deduct_ratio,
        profit_growth_gap=growth_gap,
    )


def score_earnings_quality(metrics: EarningsQualityMetrics) -> tuple[float | None, str | None, list[str], dict]:
    # Scoring range: 0-100
    tags: list[str] = []
    diagnostics = {}

    if metrics.net_profit is None and metrics.deduct_net_profit is None:
        return None, "unknown", ["missing_profit_data"], {"reason": "missing net/deduct profit"}

    score = 50.0

    # 1) 扣非占比质量（最高 +20）
    if metrics.deduct_profit_ratio is not None:
        r = metrics.deduct_profit_ratio
        diagnostics["deduct_profit_ratio"] = r
        if r >= 0.95:
            score += 20
            tags.append("high_deduct_ratio")
        elif r >= 0.85:
            score += 12
            tags.append("good_deduct_ratio")
        elif r >= 0.70:
            score += 4
        else:
            score -= 12
            tags.append("low_deduct_ratio")

    # 2) 扣非增速与净利增速一致性（最高 +15，最低 -15）
    if metrics.profit_growth_gap is not None:
        gap = metrics.profit_growth_gap
        diagnostics["profit_growth_gap"] = gap
        if abs(gap) <= 0.05:
            score += 15
            tags.append("profit_growth_consistent")
        elif abs(gap) <= 0.15:
            score += 8
        elif abs(gap) <= 0.30:
            score -= 3
        else:
            score -= 15
            tags.append("profit_growth_divergent")

    # 3) 经营现金流/每股收益匹配（最高 +20，最低 -20）
    if metrics.cash_eps_ratio is not None:
        c = metrics.cash_eps_ratio
        diagnostics["cash_eps_ratio"] = c
        if c >= 1.2:
            score += 20
            tags.append("strong_cash_conversion")
        elif c >= 1.0:
            score += 12
            tags.append("cash_conversion_ok")
        elif c >= 0.7:
            score += 2
        elif c >= 0.4:
            score -= 8
        else:
            score -= 20
            tags.append("weak_cash_conversion")

    # 4) ROE质量（最高 +15，最低 -15）
    if metrics.roe_weighted is not None:
        roe = metrics.roe_weighted
        diagnostics["roe_weighted"] = roe
        if roe >= 0.15:
            score += 15
            tags.append("high_roe")
        elif roe >= 0.10:
            score += 8
            tags.append("good_roe")
        elif roe >= 0.05:
            score += 2
        elif roe >= 0.0:
            score -= 4
        else:
            score -= 15
            tags.append("negative_roe")

    # 5) 资产负债率约束（最高 +5，最低 -12）
    if metrics.assets_debt_ratio is not None:
        debt = metrics.assets_debt_ratio
        diagnostics["assets_debt_ratio"] = debt
        if debt <= 0.45:
            score += 5
        elif debt <= 0.65:
            score += 2
        elif debt <= 0.80:
            score -= 4
        else:
            score -= 12
            tags.append("high_leverage")

    # clamp and label
    score = _clamp(score, 0, 100)
    if score >= 80:
        label = "excellent"
    elif score >= 65:
        label = "good"
    elif score >= 45:
        label = "fair"
    elif score >= 30:
        label = "weak"
    else:
        label = "poor"

    return score, label, tags, diagnostics


def build_summary_text(result: EarningsQualityResult) -> str:
    if result.score is None:
        return f"{result.symbol} 盈利质量数据不足"
    return (
        f"{result.symbol} 盈利质量{result.label}（{result.score:.1f}分）"
        f"，标签：{','.join(result.reason_tags) if result.reason_tags else '无'}"
    )
