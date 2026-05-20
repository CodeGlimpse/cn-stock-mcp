from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import median, pstdev
from types import SimpleNamespace

from cn_stock_mcp.app.services.error_mapper import serialize_exception
from cn_stock_mcp.app.services.metric_schema import (
    REVIEW_ENVELOPE_SCHEMA,
    REVIEW_METRIC_SCHEMA,
    SENTIMENT_SCORE_SCHEMA,
    build_sentiment_payload,
)
from cn_stock_mcp.app.usecases.sector_review import SectorReviewUseCase
from cn_stock_mcp.infra.config import get_settings
from cn_stock_mcp.providers.errors import ProviderError


class SectorRotationReviewUseCase:
    def __init__(self) -> None:
        self.sector_review = SectorReviewUseCase()
        self.settings = get_settings()

    def execute(self, request):
        items: list[dict] = []
        errors: list[dict] = []

        skip_detail = getattr(request, "skip_member_detail", False)
        # Tighter inner_top_n: only fetch what we'll actually display
        # member_top_n is per-sector display count; top_n is ranking count
        # We need at most member_top_n members per sector for leaders/laggards
        inner_top_n = request.member_top_n if skip_detail else min(
            request.member_top_n * 3,  # 3x buffer for filtering/sorting
            request.limit,
        )

        results = self._collect_sector_results(request, inner_top_n, skip_detail)
        for sector_name in request.sector_names:
            sector_result = results.get(sector_name)
            if sector_result is None:
                continue
            if isinstance(sector_result, Exception):
                errors.append({"sector_name": sector_name, **serialize_exception(sector_result)})
                continue

            card = self._to_sector_card(sector_result, request.sector_type, request.member_top_n)
            if card["reviewed_count"] <= 0 and card.get("mode") != "skip_member_detail":
                errors.append(
                    {
                        "sector_name": sector_name,
                        "error_code": "EMPTY_RESULT",
                        "message": f"No reviewed members available for {sector_name}",
                        "retryable": False,
                        "provider": None,
                    }
                )
                continue
            items.append(card)

        if not items:
            raise ProviderError("EMPTY_RESULT", "No sector rotation results available", retryable=False)

        sorted_items = self._sort_items(items, request.sort_by, request.descending)
        breadth = self._build_breadth(sorted_items)
        stats = self._build_stats(sorted_items)
        sentiment = self._build_sentiment(stats, breadth)
        benchmark_summary = self._build_benchmark_summary(sorted_items)
        continuity = self._build_continuity(sorted_items)
        rankings = self._build_rankings(sorted_items, request.top_n)
        rotation = self._build_rotation(
            sorted_items,
            stats,
            breadth,
            request.start_date is not None and request.end_date is not None,
            rankings,
        )
        structure = self._build_structure(sorted_items, len(request.sector_names), breadth, stats, sentiment, rotation)
        buckets = self._build_buckets(sorted_items, request.top_n)
        summary = self._build_summary(sorted_items, request.sector_type, stats, sentiment, rotation, structure, request.top_n)

        effective_mode = sorted_items[0].get("mode") or ("range_review" if request.start_date and request.end_date else "trade_date_review")
        partial_failure = bool(errors) or any(item.get("partial_failure") for item in sorted_items)

        return {
            "subject_type": "sector_rotation",
            "subject_name": f"{request.sector_type}_sector_set",
            "mode": effective_mode,
            "trade_date": sorted_items[0].get("trade_date") if effective_mode != "range_review" else None,
            "requested_trade_date": request.trade_date if effective_mode != "range_review" else None,
            "start_date": sorted_items[0].get("start_date") if effective_mode == "range_review" else None,
            "end_date": sorted_items[0].get("end_date") if effective_mode == "range_review" else None,
            "member_count": len(request.sector_names),
            "reviewed_count": len(sorted_items),
            "breadth": breadth,
            "stats": stats,
            "sentiment": sentiment,
            "benchmark_summary": benchmark_summary,
            "continuity": continuity,
            "rotation": rotation,
            "structure": structure,
            "leaders": rankings["leaders_by_avg_return"],
            "laggards": rankings["laggards_by_avg_return"],
            "rankings": rankings,
            "buckets": buckets,
            "items": sorted_items,
            "summary": summary,
            "partial_failure": partial_failure,
            "errors": errors,
            "meta": {
                "review_envelope_schema": REVIEW_ENVELOPE_SCHEMA,
                "metric_schema": REVIEW_METRIC_SCHEMA,
                "sentiment_score_schema": SENTIMENT_SCORE_SCHEMA,
                "rotation_score_schema": {
                    "schema": "rotation_signal_v1",
                    "score": {
                        "higher_is_stronger": True,
                        "unit": "heuristic_point",
                        "note": "relative signal used only for cross-sector comparison; not normalized across tools",
                    },
                },
                "item_schema": {
                    "schema": "sector_rotation_item_v1",
                    "fields": [
                        "sector_name",
                        "sector_type",
                        "mode",
                        "trade_date",
                        "start_date",
                        "end_date",
                        "member_count",
                        "reviewed_count",
                        "avg_return",
                        "avg_relative_strength",
                        "avg_volume_ratio",
                        "max_drawdown_worst",
                        "positive_ratio",
                        "negative_ratio",
                        "stronger_ratio",
                        "high_volume_ratio",
                        "sentiment",
                        "rotation",
                        "structure_tags",
                        "leaders",
                        "laggards",
                        "summary",
                        "source",
                    ],
                },
                "requested_sector_names": request.sector_names,
                "sector_type": request.sector_type,
                "filters": {
                    "min_relative_strength": request.min_relative_strength,
                    "min_return": request.min_return,
                    "max_drawdown_limit": request.max_drawdown_limit,
                    "min_volume_ratio": request.min_volume_ratio,
                },
            },
        }

    def _collect_sector_results(self, request, inner_top_n: int, skip_detail: bool = False) -> dict[str, dict | Exception]:
        sector_names = list(request.sector_names)
        if not sector_names:
            return {}

        max_workers = max(1, min(len(sector_names), int(getattr(self.settings, "sector_rotation_max_workers", 2) or 2)))
        if max_workers == 1:
            return {name: self._run_sector_review(name, request, inner_top_n, skip_detail) for name in sector_names}

        results: dict[str, dict | Exception] = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {executor.submit(self._run_sector_review, name, request, inner_top_n, skip_detail): name for name in sector_names}
            for future in as_completed(future_map):
                sector_name = future_map[future]
                try:
                    results[sector_name] = future.result()
                except Exception as exc:  # pragma: no cover
                    results[sector_name] = exc
        return results

    def _run_sector_review(self, sector_name: str, request, inner_top_n: int, skip_detail: bool = False):
        try:
            if skip_detail:
                return self._run_sector_lookup_only(sector_name, request)
            sector_req = SimpleNamespace(
                sector_name=sector_name,
                sector_type=getattr(request, "sector_type", "primary"),
                trade_date=request.trade_date,
                start_date=request.start_date,
                end_date=request.end_date,
                adjust=request.adjust,
                provider=request.provider,
                sort_by="relative_strength",
                descending=True,
                top_n=inner_top_n,
                limit=request.limit,
                min_relative_strength=request.min_relative_strength,
                min_return=request.min_return,
                max_drawdown_limit=request.max_drawdown_limit,
                min_volume_ratio=request.min_volume_ratio,
            )
            injected_sector_review = getattr(self, "sector_review", None)
            if injected_sector_review is not None and injected_sector_review.__class__ is not SectorReviewUseCase:
                return injected_sector_review.execute(sector_req)
            return SectorReviewUseCase().execute(sector_req)
        except Exception as exc:
            return exc

    def _run_sector_lookup_only(self, sector_name: str, request) -> dict:
        """Lightweight sector result: only lookup members, no per-stock review.

        Returns a minimal dict compatible with _to_sector_card() but with
        all review-derived fields set to None/empty. Used when
        skip_member_detail=True for fast sector comparison.
        """
        try:
            from cn_stock_mcp.app.usecases.sector_lookup import SectorLookupUseCase
            lookup = SectorLookupUseCase()
            members_resp = lookup.execute(SimpleNamespace(
                mode="children",
                sector_type=getattr(request, "sector_type", "primary"),
                sector_name=sector_name,
                limit=getattr(request, "limit", 100),
                provider=request.provider,
            ))
        except Exception:
            members_resp = {"items": []}

        members = members_resp.get("items", [])
        symbols = [item.symbol for item in members if getattr(item, "symbol", None)]
        member_count = len(symbols)

        # Get batch quote for basic breadth estimation (no history/review)
        breadth = {
            "positive_count": 0,
            "negative_count": 0,
            "flat_count": member_count,
            "stronger_than_benchmark_count": 0,
            "high_volume_count": 0,
        }

        return {
            "sector_name": sector_name,
            "subject_name": sector_name,
            "mode": "skip_member_detail",
            "trade_date": request.trade_date,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "member_count": member_count,
            "reviewed_count": 0,
            "items": [],
            "breadth": breadth,
            "stats": {
                "avg_return": None,
                "median_return": None,
                "avg_relative_strength": None,
                "median_relative_strength": None,
                "avg_volume_ratio": None,
                "max_drawdown_worst": None,
                "return_stddev": None,
            },
            "sentiment": {"label": "neutral", "label_zh": "中性", "score": 0.0},
            "benchmark_summary": {
                "dominant_benchmark_symbol": None,
                "dominant_benchmark_name": None,
            },
            "continuity": {},
            "rotation": {"label": "unknown", "label_zh": "未知", "score": 0.0},
            "structure": {"tags": ["skip_member_detail"]},
            "leaders": [],
            "laggards": [],
            "summary": f"{sector_name}：成员 {member_count} 只（跳过个股复盘）",
            "partial_failure": False,
            "errors": [],
            "meta": {"sector_lookup": {"source": members_resp.get("source")}},
        }

    def _to_sector_card(self, result: dict, sector_type: str, member_top_n: int) -> dict:
        reviewed_count = int(result.get("reviewed_count") or len(result.get("items", [])) or 0)
        member_count = int(result.get("member_count") or reviewed_count)
        breadth = result.get("breadth", {})
        stats = result.get("stats", {})
        continuity = result.get("continuity", {})
        benchmark_summary = result.get("benchmark_summary", {})
        sentiment = result.get("sentiment", {})
        rotation = result.get("rotation", {})
        structure = result.get("structure", {})
        positive_ratio = (breadth.get("positive_count", 0) / reviewed_count) if reviewed_count else 0.0
        negative_ratio = (breadth.get("negative_count", 0) / reviewed_count) if reviewed_count else 0.0
        stronger_ratio = (breadth.get("stronger_than_benchmark_count", 0) / reviewed_count) if reviewed_count else 0.0
        high_volume_ratio = (breadth.get("high_volume_count", 0) / reviewed_count) if reviewed_count else 0.0
        sources = sorted({item.get("source") for item in result.get("items", []) if item.get("source")})
        batch_review_source = sources[0] if len(sources) == 1 else sources

        return {
            "sector_name": result.get("sector_name") or result.get("subject_name"),
            "sector_type": sector_type,
            "mode": result.get("mode"),
            "trade_date": result.get("trade_date"),
            "requested_trade_date": result.get("requested_trade_date"),
            "start_date": result.get("start_date"),
            "end_date": result.get("end_date"),
            "member_count": member_count,
            "reviewed_count": reviewed_count,
            "avg_return": stats.get("avg_return"),
            "median_return": stats.get("median_return"),
            "avg_relative_strength": stats.get("avg_relative_strength"),
            "median_relative_strength": stats.get("median_relative_strength"),
            "avg_volume_ratio": stats.get("avg_volume_ratio"),
            "max_drawdown_worst": stats.get("max_drawdown_worst"),
            "return_stddev": stats.get("return_stddev"),
            "positive_ratio": positive_ratio,
            "negative_ratio": negative_ratio,
            "stronger_ratio": stronger_ratio,
            "high_volume_ratio": high_volume_ratio,
            "breadth": breadth,
            "stats": stats,
            "sentiment": sentiment,
            "benchmark_summary": benchmark_summary,
            "continuity": continuity,
            "rotation": rotation,
            "structure_tags": list(structure.get("tags", [])),
            "leaders": list(result.get("leaders", []))[:member_top_n],
            "laggards": list(result.get("laggards", []))[:member_top_n],
            "summary": result.get("summary"),
            "partial_failure": bool(result.get("partial_failure", False)),
            "errors": list(result.get("errors", [])),
            "source": {
                "sector_lookup": result.get("meta", {}).get("sector_lookup", {}).get("source"),
                "batch_review": batch_review_source,
            },
        }

    def _metric_values(self, items: list[dict], key: str) -> list[float]:
        values = [item.get(key) for item in items if item.get(key) is not None]
        return [float(v) for v in values]

    def _avg_or_none(self, values: list[float]) -> float | None:
        return (sum(values) / len(values)) if values else None

    def _median_or_none(self, values: list[float]) -> float | None:
        return median(values) if values else None

    def _build_breadth(self, items: list[dict]) -> dict:
        return {
            "positive_sector_count": sum(1 for item in items if item.get("avg_return") is not None and item.get("avg_return") > 0),
            "negative_sector_count": sum(1 for item in items if item.get("avg_return") is not None and item.get("avg_return") < 0),
            "flat_sector_count": sum(1 for item in items if item.get("avg_return") == 0),
            "warm_or_hot_sector_count": sum(1 for item in items if item.get("sentiment", {}).get("label") in {"warm", "hot"}),
            "cool_or_cold_sector_count": sum(1 for item in items if item.get("sentiment", {}).get("label") in {"cool", "cold"}),
            "broad_strength_sector_count": sum(1 for item in items if "broad_strength" in item.get("structure_tags", [])),
            "leader_driven_sector_count": sum(1 for item in items if item.get("rotation", {}).get("label") == "leader_driven"),
            "high_dispersion_sector_count": sum(1 for item in items if "high_dispersion" in item.get("structure_tags", [])),
        }

    def _build_stats(self, items: list[dict]) -> dict:
        sector_returns = self._metric_values(items, "avg_return")
        sector_relative_strengths = self._metric_values(items, "avg_relative_strength")
        sector_positive_ratios = self._metric_values(items, "positive_ratio")
        sector_stronger_ratios = self._metric_values(items, "stronger_ratio")
        stock_member_count_total = sum(int(item.get("member_count") or 0) for item in items)
        stock_reviewed_count_total = sum(int(item.get("reviewed_count") or 0) for item in items)

        return {
            "avg_sector_return": self._avg_or_none(sector_returns),
            "median_sector_return": self._median_or_none(sector_returns),
            "avg_sector_relative_strength": self._avg_or_none(sector_relative_strengths),
            "median_sector_relative_strength": self._median_or_none(sector_relative_strengths),
            "best_sector_return": max(sector_returns) if sector_returns else None,
            "worst_sector_return": min(sector_returns) if sector_returns else None,
            "sector_return_spread": (max(sector_returns) - min(sector_returns)) if len(sector_returns) >= 2 else None,
            "sector_return_stddev": pstdev(sector_returns) if len(sector_returns) >= 2 else None,
            "avg_sector_positive_ratio": self._avg_or_none(sector_positive_ratios),
            "avg_sector_stronger_ratio": self._avg_or_none(sector_stronger_ratios),
            "stock_member_count_total": stock_member_count_total,
            "stock_reviewed_count_total": stock_reviewed_count_total,
            "avg_stock_member_count_per_sector": (stock_member_count_total / len(items)) if items else None,
        }

    def _build_sentiment(self, stats: dict, breadth: dict) -> dict:
        score = 0.0
        avg_return = stats.get("avg_sector_return")
        avg_rs = stats.get("avg_sector_relative_strength")
        positive = breadth.get("positive_sector_count", 0)
        negative = breadth.get("negative_sector_count", 0)
        broad_strength = breadth.get("broad_strength_sector_count", 0)

        if avg_return is not None:
            if avg_return >= 4:
                score += 2.0
            elif avg_return >= 1.5:
                score += 1.0
            elif avg_return <= -2:
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

        if broad_strength >= 1:
            score += 0.5

        return build_sentiment_payload(score)

    def _build_benchmark_summary(self, items: list[dict]) -> dict:
        counts: dict[tuple[str, str | None], int] = {}
        returns: list[float] = []
        for item in items:
            benchmark = item.get("benchmark_summary") or {}
            symbol = benchmark.get("dominant_benchmark_symbol")
            name = benchmark.get("dominant_benchmark_name")
            if symbol:
                key = (symbol, name)
                counts[key] = counts.get(key, 0) + 1
            if benchmark.get("avg_benchmark_return") is not None:
                returns.append(float(benchmark.get("avg_benchmark_return")))

        if not counts:
            return {
                "dominant_benchmark_symbol": None,
                "dominant_benchmark_name": None,
                "dominant_sector_count": 0,
                "avg_benchmark_return": self._avg_or_none(returns),
                "benchmark_mix": [],
            }

        dominant_key = max(counts.items(), key=lambda kv: kv[1])[0]
        mix = [
            {"symbol": symbol, "name": name, "sector_count": count}
            for (symbol, name), count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0][0]))
        ]
        return {
            "dominant_benchmark_symbol": dominant_key[0],
            "dominant_benchmark_name": dominant_key[1],
            "dominant_sector_count": counts[dominant_key],
            "avg_benchmark_return": self._avg_or_none(returns),
            "benchmark_mix": mix,
        }

    def _build_continuity(self, items: list[dict]) -> dict:
        strengths = [int(item.get("continuity", {}).get("sustained_strength_count", 0) or 0) for item in items]
        weaknesses = [int(item.get("continuity", {}).get("sustained_weakness_count", 0) or 0) for item in items]
        return {
            "max_sector_sustained_strength_count": max(strengths) if strengths else 0,
            "max_sector_sustained_weakness_count": max(weaknesses) if weaknesses else 0,
            "avg_sector_sustained_strength_count": self._avg_or_none([float(v) for v in strengths]) if strengths else None,
            "avg_sector_sustained_weakness_count": self._avg_or_none([float(v) for v in weaknesses]) if weaknesses else None,
            "strong_sector_count": sum(1 for value in strengths if value >= 1),
            "weak_sector_count": sum(1 for value in weaknesses if value >= 1),
        }

    def _metric_value(self, item: dict, sort_by: str):
        if sort_by == "avg_relative_strength":
            return item.get("avg_relative_strength")
        if sort_by == "avg_return":
            return item.get("avg_return")
        if sort_by == "positive_ratio":
            return item.get("positive_ratio")
        if sort_by == "stronger_ratio":
            return item.get("stronger_ratio")
        if sort_by == "sentiment_score":
            return item.get("sentiment", {}).get("score")
        if sort_by == "rotation_score":
            return item.get("rotation", {}).get("score")
        return None

    def _sort_value(self, value, descending: bool):
        if value is None:
            return float("-inf") if descending else float("inf")
        return value

    def _sort_items(self, items: list[dict], sort_by: str, descending: bool) -> list[dict]:
        return sorted(items, key=lambda item: self._sort_value(self._metric_value(item, sort_by), descending), reverse=descending)

    def _rank_by(self, items: list[dict], key_func, descending: bool, top_n: int) -> list[dict]:
        return sorted(items, key=lambda item: self._sort_value(key_func(item), descending), reverse=descending)[:top_n]

    def _build_rankings(self, items: list[dict], top_n: int) -> dict:
        return {
            "leaders_by_avg_return": self._rank_by(items, lambda item: item.get("avg_return"), True, top_n),
            "laggards_by_avg_return": self._rank_by(items, lambda item: item.get("avg_return"), False, top_n),
            "leaders_by_avg_relative_strength": self._rank_by(items, lambda item: item.get("avg_relative_strength"), True, top_n),
            "leaders_by_positive_ratio": self._rank_by(items, lambda item: item.get("positive_ratio"), True, top_n),
            "leaders_by_rotation_score": self._rank_by(items, lambda item: item.get("rotation", {}).get("score"), True, top_n),
            "high_dispersion_sectors": self._rank_by(items, lambda item: item.get("return_stddev"), True, top_n),
        }

    def _build_rotation(self, items: list[dict], stats: dict, breadth: dict, range_mode: bool, rankings: dict) -> dict:
        reviewed = len(items)
        positive_ratio = (breadth.get("positive_sector_count", 0) / reviewed) if reviewed else 0.0
        negative_ratio = (breadth.get("negative_sector_count", 0) / reviewed) if reviewed else 0.0
        warm_ratio = (breadth.get("warm_or_hot_sector_count", 0) / reviewed) if reviewed else 0.0
        broad_strength_ratio = (breadth.get("broad_strength_sector_count", 0) / reviewed) if reviewed else 0.0
        leader_driven_ratio = (breadth.get("leader_driven_sector_count", 0) / reviewed) if reviewed else 0.0
        positive_sector_returns = sorted([float(item.get("avg_return")) for item in items if item.get("avg_return") is not None and item.get("avg_return") > 0], reverse=True)
        total_positive_return = sum(positive_sector_returns) if positive_sector_returns else 0.0
        top1_contribution = (positive_sector_returns[0] / total_positive_return) if total_positive_return > 0 and positive_sector_returns else None
        top2_contribution = (sum(positive_sector_returns[:2]) / total_positive_return) if total_positive_return > 0 and positive_sector_returns else None
        avg_return = stats.get("avg_sector_return")
        avg_rs = stats.get("avg_sector_relative_strength")
        dispersion = stats.get("sector_return_stddev")

        score = 0.0
        if avg_return is not None:
            score += avg_return / 4.0
        if avg_rs is not None:
            score += avg_rs / 3.0
        score += positive_ratio - negative_ratio
        score += warm_ratio * 0.5

        if negative_ratio >= 0.6 and avg_return is not None and avg_return < 0:
            label, label_zh = "sector_wide_decline", "板块普弱"
        elif top1_contribution is not None and top1_contribution >= 0.45 and broad_strength_ratio < 0.4:
            label, label_zh = "focused_leadership", "主线集中"
        elif positive_ratio >= 0.6 and broad_strength_ratio >= 0.4:
            label, label_zh = "broad_sector_advance", "板块普涨"
        elif warm_ratio < 0.3 and negative_ratio >= 0.4 and leader_driven_ratio >= 0.2:
            label, label_zh = "defensive_rotation", "防守轮动"
        elif dispersion is not None and dispersion >= 2.5 and positive_ratio >= 0.3 and negative_ratio >= 0.3:
            label, label_zh = "divergent_rotation", "分化轮动"
        else:
            label, label_zh = "mixed_rotation", "混合轮动"

        return {
            "label": label,
            "label_zh": label_zh,
            "score": score,
            "positive_sector_ratio": positive_ratio,
            "negative_sector_ratio": negative_ratio,
            "warm_sector_ratio": warm_ratio,
            "broad_strength_ratio": broad_strength_ratio,
            "leader_driven_ratio": leader_driven_ratio,
            "top1_sector_contribution": top1_contribution,
            "top2_sector_contribution": top2_contribution,
            "leader_sector_names": [item.get("sector_name") for item in rankings.get("leaders_by_avg_return", []) if item.get("sector_name")],
            "laggard_sector_names": [item.get("sector_name") for item in rankings.get("laggards_by_avg_return", []) if item.get("sector_name")],
            "range_mode": range_mode,
        }

    def _build_structure(self, items: list[dict], requested_sector_count: int, breadth: dict, stats: dict, sentiment: dict, rotation: dict) -> dict:
        reviewed = len(items)
        positive_ratio = (breadth.get("positive_sector_count", 0) / reviewed) if reviewed else 0.0
        warm_ratio = (breadth.get("warm_or_hot_sector_count", 0) / reviewed) if reviewed else 0.0
        broad_strength_ratio = (breadth.get("broad_strength_sector_count", 0) / reviewed) if reviewed else 0.0
        leader_driven_ratio = (breadth.get("leader_driven_sector_count", 0) / reviewed) if reviewed else 0.0
        negative_ratio = (breadth.get("negative_sector_count", 0) / reviewed) if reviewed else 0.0

        tags: list[str] = []
        if positive_ratio >= 0.6 and (stats.get("avg_sector_relative_strength") or 0) > 0:
            tags.append("broad_strength")
        if rotation.get("label") == "focused_leadership":
            tags.append("focused_leadership")
        if stats.get("sector_return_stddev") is not None and stats.get("sector_return_stddev") >= 2.5:
            tags.append("high_dispersion")
        if rotation.get("label") == "defensive_rotation":
            tags.append("defensive_bias")
        if negative_ratio > positive_ratio:
            tags.append("weak_breadth")
        if reviewed < requested_sector_count:
            tags.append("partial_sector_failure")
        tags.append(f"sentiment_{sentiment.get('label')}")

        return {
            "coverage_ratio": (reviewed / requested_sector_count) if requested_sector_count else 0.0,
            "positive_sector_ratio": positive_ratio,
            "warm_sector_ratio": warm_ratio,
            "broad_strength_ratio": broad_strength_ratio,
            "leader_driven_ratio": leader_driven_ratio,
            "tags": tags,
        }

    def _build_buckets(self, items: list[dict], top_n: int) -> dict:
        mainline = [
            item for item in items
            if (item.get("avg_return") or 0) > 0
            and (item.get("avg_relative_strength") or 0) > 0
            and (item.get("sentiment", {}).get("score") or 0) >= 1.5
        ]
        broad_strength = [
            item for item in items
            if "broad_strength" in item.get("structure_tags", [])
            or (item.get("positive_ratio") or 0) >= 0.6 and (item.get("stronger_ratio") or 0) >= 0.5
        ]
        leader_driven = [item for item in items if item.get("rotation", {}).get("label") == "leader_driven"]
        risk = [
            item for item in items
            if ((item.get("avg_return") or 0) < 0 and (item.get("negative_ratio") or 0) >= 0.5)
            or item.get("sentiment", {}).get("label") in {"cool", "cold"}
            or ((item.get("max_drawdown_worst") or 0) >= 8)
        ]
        risk_names = {item.get("sector_name") for item in risk}
        mainline_names = {item.get("sector_name") for item in mainline}
        watchlist = [
            item for item in items
            if item.get("sector_name") not in risk_names
            and item.get("sector_name") not in mainline_names
            and (
                (item.get("avg_return") or 0) > 0
                or (item.get("avg_relative_strength") or 0) > 0
                or (item.get("sentiment", {}).get("score") or 0) >= 0.5
            )
        ]

        return {
            "mainline_sectors": self._rank_by(mainline, lambda item: item.get("avg_relative_strength"), True, top_n),
            "broad_strength_sectors": self._rank_by(broad_strength, lambda item: item.get("avg_return"), True, top_n),
            "leader_driven_sectors": self._rank_by(leader_driven, lambda item: item.get("rotation", {}).get("score"), True, top_n),
            "watchlist_sectors": self._rank_by(watchlist, lambda item: item.get("avg_relative_strength"), True, top_n),
            "risk_sectors": self._rank_by(risk, lambda item: item.get("avg_return"), False, top_n),
        }

    def _fmt_pct(self, value):
        return "未知" if value is None else f"{value:.2f}%"

    def _build_summary(self, items: list[dict], sector_type: str, stats: dict, sentiment: dict, rotation: dict, structure: dict, top_n: int) -> str:
        leader = items[0].get("sector_name") if items else "未知"
        laggard = min(items, key=lambda item: item.get("avg_return") if item.get("avg_return") is not None else float("inf")).get("sector_name") if items else "未知"
        mainline_names = [item.get("sector_name") for item in self._rank_by(items, lambda item: item.get("avg_relative_strength"), True, top_n) if item.get("sector_name")]
        mode_label = "区间复盘" if items and items[0].get("mode") == "range_review" else "单日复盘"
        return (
            f"板块轮动复盘完成：{sector_type}，{mode_label}；比较 {len(items)} 个有效板块；"
            f"平均板块收益 {self._fmt_pct(stats.get('avg_sector_return'))}，平均相对强弱 {self._fmt_pct(stats.get('avg_sector_relative_strength'))}，整体情绪 {sentiment.get('label_zh')}；"
            f"轮动结构 {rotation.get('label_zh')}；领涨板块 {leader}，落后板块 {laggard}；"
            f"主线候选 {', '.join(mainline_names[:top_n]) if mainline_names else '暂无'}；结构标签 {', '.join(structure.get('tags', []))}。"
        )
