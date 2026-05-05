from __future__ import annotations

from statistics import median, pstdev
from types import SimpleNamespace

from openclaw_stock_mcp.app.services.metric_schema import REVIEW_METRIC_SCHEMA
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.usecases.sector_lookup import SectorLookupUseCase
from openclaw_stock_mcp.app.usecases.stock_review_batch import StockReviewBatchUseCase
from openclaw_stock_mcp.providers.errors import ProviderError


class SectorReviewUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.sector_lookup = SectorLookupUseCase()
        self.batch_review = StockReviewBatchUseCase()

    def execute(self, request):
        members_resp = self.sector_lookup.execute(
            SimpleNamespace(
                mode="children",
                sector_type="primary",
                sector_name=request.sector_name,
                limit=request.limit,
                provider=request.provider,
            )
        )
        members = members_resp.get("items", [])
        symbols = [item.symbol for item in members if getattr(item, "symbol", None)]
        if not symbols:
            raise ProviderError("EMPTY_RESULT", f"No sector members found for {request.sector_name}", retryable=False)

        batch_resp = self.batch_review.execute(
            SimpleNamespace(
                symbols=symbols,
                trade_date=request.trade_date,
                start_date=request.start_date,
                end_date=request.end_date,
                adjust=request.adjust,
                provider="akshare",
                sort_by=request.sort_by,
                descending=request.descending,
                top_n=request.top_n,
                min_relative_strength=request.min_relative_strength,
                min_return=request.min_return,
                max_drawdown_limit=request.max_drawdown_limit,
                min_volume_ratio=request.min_volume_ratio,
            )
        )

        items = batch_resp.get("items", [])
        stats = self._build_sector_stats(items)
        breadth = self._build_breadth(items)
        sentiment = self._build_sentiment(stats, breadth)
        benchmark_summary = self._build_benchmark_summary(items)
        rankings = self._build_rankings(items, request.top_n)
        continuity = self._build_continuity(items)
        rotation = self._build_rotation(
            items=items,
            stats=stats,
            breadth=breadth,
            continuity=continuity,
            rankings=rankings,
            mode=batch_resp.get("mode"),
        )
        structure = self._build_structure(
            items=items,
            member_count=len(symbols),
            breadth=breadth,
            stats=stats,
            sentiment=sentiment,
            rankings=rankings,
            continuity=continuity,
        )
        buckets = self._build_buckets(items, request.top_n)
        summary = self._build_summary(
            sector_name=request.sector_name,
            member_count=len(symbols),
            reviewed_count=len(items),
            stats=stats,
            breadth=breadth,
            sentiment=sentiment,
            benchmark_summary=benchmark_summary,
            rankings=rankings,
            structure=structure,
            continuity=continuity,
            mode=batch_resp.get("mode"),
            rotation=rotation,
        )

        return {
            "sector_name": request.sector_name,
            "mode": batch_resp.get("mode"),
            "trade_date": batch_resp.get("requested_trade_date"),
            "start_date": batch_resp.get("requested_start_date"),
            "end_date": batch_resp.get("requested_end_date"),
            "member_count": len(symbols),
            "reviewed_count": len(items),
            "breadth": breadth,
            "stats": stats,
            "sentiment": sentiment,
            "benchmark_summary": benchmark_summary,
            "continuity": continuity,
            "rotation": rotation,
            "structure": structure,
            "leaders": rankings["leaders_by_return"],
            "laggards": rankings["laggards_by_return"],
            "rankings": rankings,
            "buckets": buckets,
            "items": items,
            "summary": summary,
            "partial_failure": batch_resp.get("partial_failure", False),
            "errors": batch_resp.get("errors", []),
            "meta": {
                "metric_schema": REVIEW_METRIC_SCHEMA,
                "sector_lookup": {
                    "source": members_resp.get("source"),
                    "total": members_resp.get("total"),
                    "meta": members_resp.get("meta", {}),
                },
                "batch_review": {
                    "sort_by": batch_resp.get("sort_by"),
                    "descending": batch_resp.get("descending"),
                    "filters": batch_resp.get("filters", {}),
                    "filtered_from": batch_resp.get("filtered_from"),
                    "groups": batch_resp.get("groups", {}),
                },
            },
        }

    def _metric_values(self, items: list[dict], key: str) -> list[float]:
        values = [item.get(key) for item in items if item.get(key) is not None]
        return [float(v) for v in values]

    def _avg_or_none(self, values: list[float]) -> float | None:
        return (sum(values) / len(values)) if values else None

    def _median_or_none(self, values: list[float]) -> float | None:
        return median(values) if values else None

    def _build_sector_stats(self, items: list[dict]) -> dict:
        returns = self._metric_values(items, "return")
        relative_strengths = self._metric_values(items, "relative_strength")
        volume_ratios = self._metric_values(items, "volume_ratio")
        drawdowns = self._metric_values(items, "max_drawdown")

        return {
            "avg_return": self._avg_or_none(returns),
            "median_return": self._median_or_none(returns),
            "avg_relative_strength": self._avg_or_none(relative_strengths),
            "median_relative_strength": self._median_or_none(relative_strengths),
            "avg_volume_ratio": self._avg_or_none(volume_ratios),
            "median_volume_ratio": self._median_or_none(volume_ratios),
            "max_drawdown_worst": max(drawdowns) if drawdowns else None,
            "avg_max_drawdown": self._avg_or_none(drawdowns),
            "best_return": max(returns) if returns else None,
            "worst_return": min(returns) if returns else None,
            "return_spread": (max(returns) - min(returns)) if len(returns) >= 2 else None,
            "return_stddev": pstdev(returns) if len(returns) >= 2 else None,
            "relative_strength_stddev": pstdev(relative_strengths) if len(relative_strengths) >= 2 else None,
        }

    def _build_breadth(self, items: list[dict]) -> dict:
        positive = sum(1 for item in items if item.get("return") is not None and item.get("return") > 0)
        negative = sum(1 for item in items if item.get("return") is not None and item.get("return") < 0)
        flat = sum(1 for item in items if item.get("return") == 0)
        stronger = sum(1 for item in items if item.get("relative_strength") is not None and item.get("relative_strength") > 0)
        high_volume = sum(1 for item in items if item.get("volume_ratio") is not None and item.get("volume_ratio") >= 1.2)
        up_streak = sum(1 for item in items if item.get("stats", {}).get("up_streak", 0) >= 2)
        down_streak = sum(1 for item in items if item.get("stats", {}).get("down_streak", 0) >= 2)
        return {
            "positive_count": positive,
            "negative_count": negative,
            "flat_count": flat,
            "stronger_than_benchmark_count": stronger,
            "high_volume_count": high_volume,
            "up_streak_count": up_streak,
            "down_streak_count": down_streak,
        }

    def _build_sentiment(self, stats: dict, breadth: dict) -> dict:
        score = 0.0
        avg_return = stats.get("avg_return")
        avg_rs = stats.get("avg_relative_strength")
        positive = breadth.get("positive_count", 0)
        negative = breadth.get("negative_count", 0)
        high_volume = breadth.get("high_volume_count", 0)

        if avg_return is not None:
            if avg_return >= 5:
                score += 2.0
            elif avg_return >= 2:
                score += 1.0
            elif avg_return <= -3:
                score -= 2.0
            elif avg_return < 0:
                score -= 1.0

        if avg_rs is not None:
            if avg_rs >= 2:
                score += 1.5
            elif avg_rs > 0:
                score += 0.5
            elif avg_rs <= -2:
                score -= 1.5
            elif avg_rs < 0:
                score -= 0.5

        if positive > negative:
            score += 0.5
        elif negative > positive:
            score -= 0.5

        if high_volume >= 3:
            score += 0.5

        if score >= 3:
            label, label_zh = "hot", "偏热"
        elif score >= 1.5:
            label, label_zh = "warm", "偏强"
        elif score > -1:
            label, label_zh = "neutral", "中性"
        elif score > -2.5:
            label, label_zh = "cool", "偏弱"
        else:
            label, label_zh = "cold", "偏冷"

        return {"score": score, "label": label, "label_zh": label_zh}

    def _build_benchmark_summary(self, items: list[dict]) -> dict:
        benchmark_items = []
        for item in items:
            benchmark = item.get("benchmark") or {}
            symbol = benchmark.get("symbol")
            name = benchmark.get("name")
            ret = benchmark.get("return")
            if symbol:
                benchmark_items.append({"symbol": symbol, "name": name, "return": ret})

        if not benchmark_items:
            return {
                "dominant_benchmark_symbol": None,
                "dominant_benchmark_name": None,
                "dominant_member_count": 0,
                "avg_benchmark_return": None,
                "benchmark_mix": [],
            }

        counts: dict[tuple[str, str | None], int] = {}
        returns: list[float] = []
        for item in benchmark_items:
            key = (item["symbol"], item["name"])
            counts[key] = counts.get(key, 0) + 1
            if item.get("return") is not None:
                returns.append(float(item["return"]))

        dominant_key = max(counts.items(), key=lambda kv: kv[1])[0]
        mix = [
            {"symbol": symbol, "name": name, "member_count": count}
            for (symbol, name), count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0][0]))
        ]
        return {
            "dominant_benchmark_symbol": dominant_key[0],
            "dominant_benchmark_name": dominant_key[1],
            "dominant_member_count": counts[dominant_key],
            "avg_benchmark_return": self._avg_or_none(returns),
            "benchmark_mix": mix,
        }

    def _rank_by_metric(self, items: list[dict], metric: str, descending: bool, top_n: int) -> list[dict]:
        def key_func(item):
            value = item.get(metric)
            if value is None:
                return float("-inf") if descending else float("inf")
            return value

        ranked = sorted(items, key=key_func, reverse=descending)
        return ranked[:top_n]

    def _build_rankings(self, items: list[dict], top_n: int) -> dict:
        return {
            "leaders_by_return": self._rank_by_metric(items, "return", True, top_n),
            "laggards_by_return": self._rank_by_metric(items, "return", False, top_n),
            "leaders_by_relative_strength": self._rank_by_metric(items, "relative_strength", True, top_n),
            "leaders_by_volume_ratio": self._rank_by_metric(items, "volume_ratio", True, top_n),
            "drawdown_risk": self._rank_by_metric(items, "max_drawdown", True, top_n),
        }

    def _build_continuity(self, items: list[dict]) -> dict:
        up_streaks = [int(item.get("stats", {}).get("up_streak", 0)) for item in items]
        down_streaks = [int(item.get("stats", {}).get("down_streak", 0)) for item in items]
        max_up = max(up_streaks) if up_streaks else 0
        max_down = max(down_streaks) if down_streaks else 0
        avg_up = self._avg_or_none([float(v) for v in up_streaks]) if up_streaks else None
        avg_down = self._avg_or_none([float(v) for v in down_streaks]) if down_streaks else None
        sustained_strength = sum(1 for v in up_streaks if v >= 2)
        sustained_weakness = sum(1 for v in down_streaks if v >= 2)
        return {
            "max_up_streak": max_up,
            "max_down_streak": max_down,
            "avg_up_streak": avg_up,
            "avg_down_streak": avg_down,
            "sustained_strength_count": sustained_strength,
            "sustained_weakness_count": sustained_weakness,
        }

    def _build_structure(self, items: list[dict], member_count: int, breadth: dict, stats: dict, sentiment: dict, rankings: dict, continuity: dict) -> dict:
        reviewed_count = len(items)
        positive_ratio = (breadth.get("positive_count", 0) / reviewed_count) if reviewed_count else 0.0
        stronger_ratio = (breadth.get("stronger_than_benchmark_count", 0) / reviewed_count) if reviewed_count else 0.0
        high_volume_ratio = (breadth.get("high_volume_count", 0) / reviewed_count) if reviewed_count else 0.0
        coverage_ratio = (reviewed_count / member_count) if member_count else 0.0
        tags: list[str] = []

        avg_return = stats.get("avg_return")
        avg_rs = stats.get("avg_relative_strength")
        return_spread = stats.get("return_spread")
        return_stddev = stats.get("return_stddev")
        leader = rankings.get("leaders_by_return", [{}])[0]
        leader_return = leader.get("return")

        if positive_ratio >= 0.6 and avg_rs is not None and avg_rs > 0:
            tags.append("broad_strength")
        if positive_ratio < 0.5 and leader_return is not None and leader_return >= 5:
            tags.append("concentrated_strength")
        if stronger_ratio >= 0.6:
            tags.append("benchmark_outperform")
        if high_volume_ratio >= 0.3:
            tags.append("active_volume")
        if return_spread is not None and return_spread >= 10:
            tags.append("high_dispersion")
        if return_stddev is not None and return_stddev >= 4:
            tags.append("volatile_internal_structure")
        if stats.get("max_drawdown_worst") is not None and stats.get("max_drawdown_worst") >= 8:
            tags.append("drawdown_risk")
        if avg_return is not None and avg_return < 0 and breadth.get("negative_count", 0) > breadth.get("positive_count", 0):
            tags.append("weak_breadth")
        if continuity.get("sustained_strength_count", 0) >= 2:
            tags.append("trend_persistence")
        if continuity.get("sustained_weakness_count", 0) >= 2:
            tags.append("trend_divergence")
        tags.append(f"sentiment_{sentiment.get('label')}")

        return {
            "coverage_ratio": coverage_ratio,
            "positive_ratio": positive_ratio,
            "stronger_ratio": stronger_ratio,
            "high_volume_ratio": high_volume_ratio,
            "tags": tags,
        }

    def _build_rotation(self, items: list[dict], stats: dict, breadth: dict, continuity: dict, rankings: dict, mode: str | None) -> dict:
        reviewed_count = len(items)
        positive_ratio = (breadth.get("positive_count", 0) / reviewed_count) if reviewed_count else 0.0
        negative_ratio = (breadth.get("negative_count", 0) / reviewed_count) if reviewed_count else 0.0
        outperform_ratio = (breadth.get("stronger_than_benchmark_count", 0) / reviewed_count) if reviewed_count else 0.0
        strong_trend_ratio = (continuity.get("sustained_strength_count", 0) / reviewed_count) if reviewed_count else 0.0
        weak_trend_ratio = (continuity.get("sustained_weakness_count", 0) / reviewed_count) if reviewed_count else 0.0
        positive_returns = sorted([float(item.get("return")) for item in items if item.get("return") is not None and item.get("return") > 0], reverse=True)
        total_positive_return = sum(positive_returns) if positive_returns else 0.0
        top1_contribution = (positive_returns[0] / total_positive_return) if total_positive_return > 0 and positive_returns else None
        top3_contribution = (sum(positive_returns[:3]) / total_positive_return) if total_positive_return > 0 and positive_returns else None
        best_return = stats.get("best_return")
        avg_return = stats.get("avg_return")
        avg_rs = stats.get("avg_relative_strength")
        dispersion = stats.get("return_stddev")
        leader_symbols = [item.get("symbol") for item in rankings.get("leaders_by_return", []) if item.get("symbol")]
        laggard_symbols = [item.get("symbol") for item in rankings.get("laggards_by_return", []) if item.get("symbol")]

        score = 0.0
        if avg_return is not None:
            score += avg_return / 5.0
        if avg_rs is not None:
            score += avg_rs / 4.0
        score += positive_ratio - negative_ratio
        score += strong_trend_ratio * 0.5
        score -= weak_trend_ratio * 0.5

        if negative_ratio >= 0.6 and avg_return is not None and avg_return < 0:
            label, label_zh = "broad_decline", "普跌走弱"
        elif top1_contribution is not None and top1_contribution >= 0.65 and best_return is not None and best_return >= 5 and positive_ratio <= 0.5:
            label, label_zh = "leader_driven", "龙头驱动"
        elif positive_ratio >= 0.6 and outperform_ratio >= 0.5 and top3_contribution is not None and top3_contribution <= 0.85:
            label, label_zh = "broad_advance", "普涨轮动"
        elif strong_trend_ratio >= 0.4 and avg_rs is not None and avg_rs > 0:
            label, label_zh = "persistent_uptrend", "持续走强"
        elif dispersion is not None and dispersion >= 4 and positive_ratio >= 0.3 and negative_ratio >= 0.3:
            label, label_zh = "divergent_rotation", "分化轮动"
        else:
            label, label_zh = "mixed_rotation", "混合轮动"

        return {
            "label": label,
            "label_zh": label_zh,
            "score": score,
            "positive_ratio": positive_ratio,
            "negative_ratio": negative_ratio,
            "outperform_ratio": outperform_ratio,
            "strong_trend_ratio": strong_trend_ratio,
            "weak_trend_ratio": weak_trend_ratio,
            "top1_return_contribution": top1_contribution,
            "top3_return_contribution": top3_contribution,
            "leader_symbols": leader_symbols,
            "laggard_symbols": laggard_symbols,
            "range_mode": mode == "range_review",
        }

    def _build_buckets(self, items: list[dict], top_n: int) -> dict:
        strong_candidates = [item for item in items if item.get("relative_strength") is not None and item.get("relative_strength") > 0 and item.get("return") is not None and item.get("return") > 0]
        weak_candidates = [item for item in items if item.get("relative_strength") is not None and item.get("relative_strength") < 0 and item.get("return") is not None and item.get("return") < 0]
        volume_focus = [item for item in items if item.get("volume_ratio") is not None and item.get("volume_ratio") >= 1.2]
        risk_alerts = [item for item in items if item.get("max_drawdown") is not None and item.get("max_drawdown") >= 8]
        leaders = sorted(strong_candidates, key=lambda item: ((item.get("return") or float("-inf")), (item.get("relative_strength") or float("-inf"))), reverse=True)
        leader_symbols = {item.get("symbol") for item in leaders[:1]}
        followers = sorted(
            [
                item
                for item in items
                if item.get("return") is not None
                and item.get("return") > 0
                and item.get("symbol") not in leader_symbols
            ],
            key=lambda item: ((item.get("relative_strength") or float("-inf")), (item.get("return") or float("-inf"))),
            reverse=True,
        )
        draggers = sorted(weak_candidates, key=lambda item: ((item.get("return") or float("inf")), -(item.get("max_drawdown") or float("-inf"))))
        return {
            "strong_candidates": leaders[:top_n],
            "weak_candidates": weak_candidates[:top_n],
            "volume_focus": sorted(volume_focus, key=lambda item: item.get("volume_ratio") or float("-inf"), reverse=True)[:top_n],
            "risk_alerts": sorted(risk_alerts, key=lambda item: item.get("max_drawdown") or float("-inf"), reverse=True)[:top_n],
            "leaders": leaders[:top_n],
            "followers": followers[:top_n],
            "draggers": draggers[:top_n],
        }

    def _fmt_pct(self, value):
        return "未知" if value is None else f"{value:.2f}%"

    def _build_summary(self, sector_name: str, member_count: int, reviewed_count: int, stats: dict, breadth: dict, sentiment: dict, benchmark_summary: dict, rankings: dict, structure: dict, continuity: dict, mode: str | None, rotation: dict | None = None) -> str:
        leader = rankings["leaders_by_return"][0].get("symbol") if rankings.get("leaders_by_return") else "未知"
        laggard = rankings["laggards_by_return"][0].get("symbol") if rankings.get("laggards_by_return") else "未知"
        strong = rankings["leaders_by_relative_strength"][0].get("symbol") if rankings.get("leaders_by_relative_strength") else "未知"
        benchmark_name = benchmark_summary.get("dominant_benchmark_name") or benchmark_summary.get("dominant_benchmark_symbol") or "基准"
        mode_label = "区间复盘" if mode == "range_review" else "单日复盘"
        rotation_part = ""
        if mode == "range_review" and rotation:
            rotation_part = f"轮动 {rotation.get('label_zh')}；"
        return (
            f"板块复盘完成：{sector_name}，{mode_label}；成员 {member_count} 只，成功复盘 {reviewed_count} 只；"
            f"平均收益 {self._fmt_pct(stats.get('avg_return'))}，平均相对{benchmark_name}强弱 {self._fmt_pct(stats.get('avg_relative_strength'))}，情绪 {sentiment.get('label_zh')}；"
            f"{rotation_part}上涨 {breadth.get('positive_count', 0)} 只，下跌 {breadth.get('negative_count', 0)} 只，持续强势 {continuity.get('sustained_strength_count', 0)} 只；"
            f"收益领涨 {leader}，相对强势 {strong}，落后 {laggard}；结构标签 {', '.join(structure.get('tags', []))}。"
        )
