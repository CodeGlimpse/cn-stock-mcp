from __future__ import annotations

from statistics import median, pstdev
from types import SimpleNamespace

from openclaw_stock_mcp.app.services.metric_schema import (
    REVIEW_ENVELOPE_SCHEMA,
    REVIEW_METRIC_SCHEMA,
    SENTIMENT_SCORE_SCHEMA,
    build_sentiment_payload,
)
from openclaw_stock_mcp.app.usecases.stock_review_batch import StockReviewBatchUseCase


class WatchlistReviewUseCase:
    def __init__(self) -> None:
        self.batch_review = StockReviewBatchUseCase()

    def execute(self, request):
        batch_resp = self.batch_review.execute(
            SimpleNamespace(
                symbols=request.symbols,
                trade_date=request.trade_date,
                start_date=request.start_date,
                end_date=request.end_date,
                adjust=request.adjust,
                provider=request.provider,
                sort_by="relative_strength",
                descending=True,
                top_n=len(request.symbols),
                min_relative_strength=None,
                min_return=None,
                max_drawdown_limit=None,
                min_volume_ratio=None,
            )
        )

        scored_items = [self._to_watchlist_card(item) for item in batch_resp.get("items", [])]
        filtered_items = self._apply_filters(scored_items, request)
        sorted_items = self._sort_items(filtered_items, request.sort_by, request.descending)
        return_mode = getattr(request, "return_mode", "full")
        output_items = sorted_items[: request.top_n] if return_mode == "ranked_only" else sorted_items

        breadth = self._build_breadth(output_items)
        stats = self._build_stats(output_items)
        sentiment = self._build_sentiment(stats, breadth)
        benchmark_summary = self._build_benchmark_summary(output_items)
        continuity = self._build_continuity(output_items)
        structure = self._build_structure(output_items, len(request.symbols), breadth, stats, sentiment)
        rankings = self._build_rankings(output_items, request.top_n)
        buckets = self._build_buckets(output_items, request.top_n)
        summary = self._build_summary(
            watchlist_name=request.watchlist_name or "custom_watchlist",
            mode=batch_resp.get("mode"),
            member_count=len(request.symbols),
            reviewed_count=len(scored_items),
            selected_count=len(output_items),
            stats=stats,
            breadth=breadth,
            sentiment=sentiment,
            rankings=rankings,
        )

        effective_mode = batch_resp.get("mode") or ("range_review" if request.start_date and request.end_date else "trade_date_review")
        return {
            "subject_type": "watchlist",
            "subject_name": request.watchlist_name or "custom_watchlist",
            "mode": effective_mode,
            "trade_date": batch_resp.get("requested_trade_date") if effective_mode != "range_review" else None,
            "requested_trade_date": batch_resp.get("requested_trade_date") if effective_mode != "range_review" else None,
            "start_date": batch_resp.get("requested_start_date") if effective_mode == "range_review" else None,
            "end_date": batch_resp.get("requested_end_date") if effective_mode == "range_review" else None,
            "member_count": len(request.symbols),
            "reviewed_count": len(scored_items),
            "breadth": breadth,
            "stats": stats,
            "sentiment": sentiment,
            "benchmark_summary": benchmark_summary,
            "continuity": continuity,
            "rotation": {"applicable": False, "reason": "watchlist review focuses on prioritization within an explicit pool"},
            "structure": structure,
            "leaders": rankings["leaders_by_watchlist_score"],
            "laggards": rankings["risk_by_watchlist_score"],
            "rankings": rankings,
            "buckets": buckets,
            "items": output_items,
            "summary": summary,
            "partial_failure": batch_resp.get("partial_failure", False),
            "errors": batch_resp.get("errors", []),
            "meta": {
                "review_envelope_schema": REVIEW_ENVELOPE_SCHEMA,
                "metric_schema": REVIEW_METRIC_SCHEMA,
                "sentiment_score_schema": SENTIMENT_SCORE_SCHEMA,
                "watchlist_score_schema": {
                    "schema": "watchlist_score_v1",
                    "score": {
                        "higher_is_stronger": True,
                        "unit": "heuristic_point",
                        "note": "priority score for explicit watchlist review, combining strength, return, volume, drawdown, and streak context",
                    },
                    "labels": {
                        "focus": "score >= 6 and no severe risk",
                        "monitor": "2.5 <= score < 6",
                        "observe": "-1 <= score < 2.5",
                        "risk_alert": "score < -1 or severe risk dominates",
                    },
                },
                "watchlist": {
                    "name": request.watchlist_name or "custom_watchlist",
                    "requested_symbols": request.symbols,
                },
                "filters": {
                    "min_watchlist_score": request.min_watchlist_score,
                    "min_relative_strength": request.min_relative_strength,
                    "min_return": request.min_return,
                    "max_drawdown_limit": request.max_drawdown_limit,
                    "min_volume_ratio": request.min_volume_ratio,
                    "return_mode": return_mode,
                },
                "filtered_from": len(scored_items),
                "filtered_count": len(filtered_items),
                "ranked_count": min(len(sorted_items), request.top_n),
                "batch_review": {
                    "sort_by": batch_resp.get("sort_by"),
                    "descending": batch_resp.get("descending"),
                    "filtered_from": batch_resp.get("filtered_from"),
                    "total_symbols": batch_resp.get("total_symbols"),
                },
            },
        }

    def _to_watchlist_card(self, item: dict) -> dict:
        watchlist_score, status_label, reason_tags, risk_flags = self._watchlist_signal(item)
        return {
            **item,
            "watchlist_score": watchlist_score,
            "status_label": status_label,
            "reason_tags": reason_tags,
            "risk_flags": risk_flags,
            "review_tags": item.get("tags", []),
        }

    def _watchlist_signal(self, item: dict) -> tuple[float, str, list[str], list[str]]:
        score = 0.0
        reasons: list[str] = []
        risks: list[str] = []

        relative_strength = item.get("relative_strength")
        return_pct = item.get("return")
        max_drawdown = item.get("max_drawdown")
        volume_ratio = item.get("volume_ratio")
        stats = item.get("stats", {}) or {}
        up_streak = int(stats.get("up_streak", 0) or 0)
        down_streak = int(stats.get("down_streak", 0) or 0)

        if relative_strength is not None:
            if relative_strength >= 10:
                score += 4.0
                reasons.append("very_strong_relative_strength")
            elif relative_strength >= 5:
                score += 3.0
                reasons.append("strong_relative_strength")
            elif relative_strength >= 2:
                score += 2.0
                reasons.append("positive_relative_strength")
            elif relative_strength > 0:
                score += 1.0
                reasons.append("slight_relative_strength")
            elif relative_strength <= -10:
                score -= 3.5
                risks.append("very_weak_relative_strength")
            elif relative_strength < 0:
                score -= 1.5
                risks.append("weak_relative_strength")

        if return_pct is not None:
            if return_pct >= 15:
                score += 3.5
                reasons.append("high_momentum")
            elif return_pct >= 8:
                score += 2.5
                reasons.append("strong_return")
            elif return_pct >= 3:
                score += 1.5
                reasons.append("positive_return")
            elif return_pct > 0:
                score += 0.5
                reasons.append("slight_positive_return")
            elif return_pct <= -5:
                score -= 2.5
                risks.append("negative_return")
            elif return_pct < 0:
                score -= 1.0
                risks.append("soft_negative_return")

        if volume_ratio is not None:
            if volume_ratio >= 2.0:
                score += 1.5
                reasons.append("high_volume")
            elif volume_ratio >= 1.2:
                score += 0.75
                reasons.append("active_volume")

        if max_drawdown is not None:
            if max_drawdown <= 3:
                score += 1.0
                reasons.append("low_drawdown")
            elif max_drawdown <= 5:
                score += 0.5
                reasons.append("controlled_drawdown")
            elif max_drawdown >= 10:
                score -= 2.5
                risks.append("severe_drawdown")
            elif max_drawdown >= 8:
                score -= 1.5
                risks.append("drawdown_risk")

        if up_streak >= 3:
            score += 1.25
            reasons.append("strong_up_streak")
        elif up_streak >= 2:
            score += 0.75
            reasons.append("up_streak")

        if down_streak >= 3:
            score -= 2.0
            risks.append("strong_down_streak")
        elif down_streak >= 2:
            score -= 1.0
            risks.append("down_streak")

        severe_risk = any(flag in {"very_weak_relative_strength", "severe_drawdown", "strong_down_streak"} for flag in risks)
        rounded = round(score, 2)
        if severe_risk and rounded < 4:
            label = "risk_alert"
        elif rounded >= 6:
            label = "focus"
        elif rounded >= 2.5:
            label = "monitor"
        elif rounded < -1:
            label = "risk_alert"
        else:
            label = "observe"
        return rounded, label, reasons, risks

    def _apply_filters(self, items: list[dict], request) -> list[dict]:
        filtered = []
        for item in items:
            if request.min_watchlist_score is not None and item.get("watchlist_score") < request.min_watchlist_score:
                continue
            if request.min_relative_strength is not None:
                if item.get("relative_strength") is None or item.get("relative_strength") < request.min_relative_strength:
                    continue
            if request.min_return is not None:
                if item.get("return") is None or item.get("return") < request.min_return:
                    continue
            if request.max_drawdown_limit is not None:
                if item.get("max_drawdown") is None or item.get("max_drawdown") > request.max_drawdown_limit:
                    continue
            if request.min_volume_ratio is not None:
                if item.get("volume_ratio") is None or item.get("volume_ratio") < request.min_volume_ratio:
                    continue
            filtered.append(item)
        return filtered

    def _sort_value(self, value, descending: bool):
        if value is None:
            return float("-inf") if descending else float("inf")
        return value

    def _sort_items(self, items: list[dict], sort_by: str, descending: bool) -> list[dict]:
        key_map = {
            "watchlist_score": "watchlist_score",
            "relative_strength": "relative_strength",
            "return": "return",
            "volume_ratio": "volume_ratio",
            "max_drawdown": "max_drawdown",
        }
        key_name = key_map[sort_by]
        return sorted(items, key=lambda item: self._sort_value(item.get(key_name), descending), reverse=descending)

    def _metric_values(self, items: list[dict], key: str) -> list[float]:
        values = [item.get(key) for item in items if item.get(key) is not None]
        return [float(v) for v in values]

    def _avg_or_none(self, values: list[float]) -> float | None:
        return (sum(values) / len(values)) if values else None

    def _median_or_none(self, values: list[float]) -> float | None:
        return median(values) if values else None

    def _build_breadth(self, items: list[dict]) -> dict:
        return {
            "positive_count": sum(1 for item in items if item.get("return") is not None and item.get("return") > 0),
            "negative_count": sum(1 for item in items if item.get("return") is not None and item.get("return") < 0),
            "stronger_than_benchmark_count": sum(1 for item in items if item.get("relative_strength") is not None and item.get("relative_strength") > 0),
            "high_volume_count": sum(1 for item in items if item.get("volume_ratio") is not None and item.get("volume_ratio") >= 1.2),
            "focus_count": sum(1 for item in items if item.get("status_label") == "focus"),
            "monitor_count": sum(1 for item in items if item.get("status_label") == "monitor"),
            "observe_count": sum(1 for item in items if item.get("status_label") == "observe"),
            "risk_alert_count": sum(1 for item in items if item.get("status_label") == "risk_alert"),
        }

    def _build_stats(self, items: list[dict]) -> dict:
        returns = self._metric_values(items, "return")
        relative_strengths = self._metric_values(items, "relative_strength")
        volume_ratios = self._metric_values(items, "volume_ratio")
        drawdowns = self._metric_values(items, "max_drawdown")
        watchlist_scores = self._metric_values(items, "watchlist_score")
        return {
            "avg_return": self._avg_or_none(returns),
            "median_return": self._median_or_none(returns),
            "avg_relative_strength": self._avg_or_none(relative_strengths),
            "median_relative_strength": self._median_or_none(relative_strengths),
            "avg_volume_ratio": self._avg_or_none(volume_ratios),
            "median_volume_ratio": self._median_or_none(volume_ratios),
            "max_drawdown_worst": max(drawdowns) if drawdowns else None,
            "avg_max_drawdown": self._avg_or_none(drawdowns),
            "avg_watchlist_score": self._avg_or_none(watchlist_scores),
            "median_watchlist_score": self._median_or_none(watchlist_scores),
            "best_watchlist_score": max(watchlist_scores) if watchlist_scores else None,
            "worst_watchlist_score": min(watchlist_scores) if watchlist_scores else None,
            "return_stddev": pstdev(returns) if len(returns) >= 2 else None,
            "watchlist_score_stddev": pstdev(watchlist_scores) if len(watchlist_scores) >= 2 else None,
        }

    def _build_sentiment(self, stats: dict, breadth: dict) -> dict:
        score = 0.0
        avg_return = stats.get("avg_return")
        avg_rs = stats.get("avg_relative_strength")
        focus_count = breadth.get("focus_count", 0)
        risk_count = breadth.get("risk_alert_count", 0)

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

        if focus_count > 0:
            score += min(focus_count * 0.5, 1.5)
        if risk_count > 0:
            score -= min(risk_count * 0.5, 1.5)

        return build_sentiment_payload(score)

    def _build_benchmark_summary(self, items: list[dict]) -> dict:
        benchmark_items = []
        for item in items:
            benchmark = item.get("benchmark") or {}
            symbol = benchmark.get("symbol")
            name = benchmark.get("name")
            ret = benchmark.get("return") or benchmark.get("return_pct")
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

    def _build_continuity(self, items: list[dict]) -> dict:
        up_streaks = [int(item.get("stats", {}).get("up_streak", 0) or 0) for item in items]
        down_streaks = [int(item.get("stats", {}).get("down_streak", 0) or 0) for item in items]
        return {
            "max_up_streak": max(up_streaks) if up_streaks else 0,
            "max_down_streak": max(down_streaks) if down_streaks else 0,
            "avg_up_streak": self._avg_or_none([float(v) for v in up_streaks]) if up_streaks else None,
            "avg_down_streak": self._avg_or_none([float(v) for v in down_streaks]) if down_streaks else None,
            "sustained_strength_count": sum(1 for v in up_streaks if v >= 2),
            "sustained_weakness_count": sum(1 for v in down_streaks if v >= 2),
        }

    def _build_structure(self, items: list[dict], member_count: int, breadth: dict, stats: dict, sentiment: dict) -> dict:
        reviewed_count = len(items)
        focus_ratio = (breadth.get("focus_count", 0) / reviewed_count) if reviewed_count else 0.0
        risk_ratio = (breadth.get("risk_alert_count", 0) / reviewed_count) if reviewed_count else 0.0
        stronger_ratio = (breadth.get("stronger_than_benchmark_count", 0) / reviewed_count) if reviewed_count else 0.0
        tags: list[str] = []

        if focus_ratio >= 0.3:
            tags.append("focus_dense")
        if risk_ratio >= 0.3:
            tags.append("risk_dense")
        if stronger_ratio >= 0.5:
            tags.append("benchmark_outperform")
        if stats.get("watchlist_score_stddev") is not None and stats.get("watchlist_score_stddev") >= 3:
            tags.append("high_dispersion")
        tags.append(f"sentiment_{sentiment.get('label')}")

        return {
            "coverage_ratio": (reviewed_count / member_count) if member_count else 0.0,
            "focus_ratio": focus_ratio,
            "risk_ratio": risk_ratio,
            "stronger_ratio": stronger_ratio,
            "tags": tags,
        }

    def _rank_by_metric(self, items: list[dict], metric: str, descending: bool, top_n: int) -> list[dict]:
        return sorted(items, key=lambda item: self._sort_value(item.get(metric), descending), reverse=descending)[:top_n]

    def _build_rankings(self, items: list[dict], top_n: int) -> dict:
        return {
            "leaders_by_watchlist_score": self._rank_by_metric(items, "watchlist_score", True, top_n),
            "leaders_by_relative_strength": self._rank_by_metric(items, "relative_strength", True, top_n),
            "leaders_by_return": self._rank_by_metric(items, "return", True, top_n),
            "leaders_by_volume_ratio": self._rank_by_metric(items, "volume_ratio", True, top_n),
            "risk_by_watchlist_score": self._rank_by_metric(items, "watchlist_score", False, top_n),
        }

    def _build_buckets(self, items: list[dict], top_n: int) -> dict:
        focus = [item for item in items if item.get("status_label") == "focus"]
        monitor = [item for item in items if item.get("status_label") == "monitor"]
        observe = [item for item in items if item.get("status_label") == "observe"]
        risk_alerts = [item for item in items if item.get("status_label") == "risk_alert"]
        return {
            "focus": self._rank_by_metric(focus, "watchlist_score", True, top_n),
            "monitor": self._rank_by_metric(monitor, "watchlist_score", True, top_n),
            "observe": self._rank_by_metric(observe, "watchlist_score", True, top_n),
            "risk_alerts": self._rank_by_metric(risk_alerts, "watchlist_score", False, top_n),
        }

    def _fmt_pct(self, value):
        return "未知" if value is None else f"{value:.2f}%"

    def _fmt_num(self, value):
        return "未知" if value is None else f"{value:.2f}"

    def _build_summary(self, watchlist_name: str, mode: str | None, member_count: int, reviewed_count: int, selected_count: int, stats: dict, breadth: dict, sentiment: dict, rankings: dict) -> str:
        mode_label = "区间复盘" if mode == "range_review" else "单日复盘"
        leader = rankings.get("leaders_by_watchlist_score", [{}])[0].get("symbol") if rankings.get("leaders_by_watchlist_score") else "未知"
        return (
            f"观察池复盘完成：{watchlist_name}，{mode_label}；池内 {member_count} 只，成功复盘 {reviewed_count} 只，筛选后保留 {selected_count} 只；"
            f"平均收益 {self._fmt_pct(stats.get('avg_return'))}，平均相对强弱 {self._fmt_pct(stats.get('avg_relative_strength'))}，平均观察分 {self._fmt_num(stats.get('avg_watchlist_score'))}，情绪 {sentiment.get('label_zh')}；"
            f"重点 {breadth.get('focus_count', 0)} 只，跟踪 {breadth.get('monitor_count', 0)} 只，观察 {breadth.get('observe_count', 0)} 只，风险提示 {breadth.get('risk_alert_count', 0)} 只；"
            f"当前最高优先 {leader}。"
        )
