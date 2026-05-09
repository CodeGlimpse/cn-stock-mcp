from __future__ import annotations

from statistics import median, pstdev
from types import SimpleNamespace

from openclaw_stock_mcp.app.services.error_mapper import serialize_exception
from openclaw_stock_mcp.app.services.metric_schema import (
    REVIEW_ENVELOPE_SCHEMA,
    REVIEW_METRIC_SCHEMA,
    SENTIMENT_SCORE_SCHEMA,
    build_sentiment_payload,
)
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver
from openclaw_stock_mcp.app.usecases.market_pool import MarketPoolUseCase
from openclaw_stock_mcp.app.usecases.sector_lookup import SectorLookupUseCase
from openclaw_stock_mcp.app.usecases.stock_review_batch import StockReviewBatchUseCase
from openclaw_stock_mcp.providers.errors import ProviderError


class StockCandidateScanUseCase:
    MAX_UNIVERSE_SYMBOLS = 200

    def __init__(self) -> None:
        self.resolver = SymbolResolver()
        self.sector_lookup = SectorLookupUseCase()
        self.market_pool = MarketPoolUseCase()
        self.batch_review = StockReviewBatchUseCase()

    def execute(self, request):
        universe = self._build_universe(request)
        symbols = universe["symbols"]
        universe_errors = list(universe["errors"])
        source_tags = universe["source_tags"]

        if not symbols:
            raise ProviderError("EMPTY_RESULT", "No candidate universe symbols resolved", retryable=False)

        batch_resp = self.batch_review.execute(
            SimpleNamespace(
                symbols=symbols,
                trade_date=request.trade_date,
                start_date=request.start_date,
                end_date=request.end_date,
                adjust=request.adjust,
                provider="akshare",
                sort_by="relative_strength",
                descending=True,
                top_n=len(symbols),
                min_relative_strength=None,
                min_return=None,
                max_drawdown_limit=None,
                min_volume_ratio=None,
            )
        )

        review_errors = [{"scope": "stock_review", **err} for err in batch_resp.get("errors", [])]
        scored_items = [self._to_candidate_card(item, source_tags.get(item.get("symbol"), [])) for item in batch_resp.get("items", [])]
        filtered_items = self._apply_filters(scored_items, request)
        sorted_items = self._sort_items(filtered_items, request.sort_by, request.descending)
        return_mode = getattr(request, "return_mode", "full")
        output_items = sorted_items[: request.top_n] if return_mode == "ranked_only" else sorted_items

        analysis_items = output_items
        breadth = self._build_breadth(analysis_items)
        stats = self._build_stats(analysis_items)
        sentiment = self._build_sentiment(stats, breadth)
        benchmark_summary = self._build_benchmark_summary(analysis_items)
        continuity = self._build_continuity(analysis_items)
        structure = self._build_structure(analysis_items, len(symbols), breadth, stats, sentiment)
        rankings = self._build_rankings(analysis_items, request.top_n)
        buckets = self._build_buckets(analysis_items, request.top_n)
        summary = self._build_summary(
            mode=batch_resp.get("mode"),
            universe_name=self._universe_name(request),
            member_count=len(symbols),
            reviewed_count=len(scored_items),
            selected_count=len(sorted_items),
            stats=stats,
            breadth=breadth,
            sentiment=sentiment,
            rankings=rankings,
            buckets=buckets,
        )

        errors = universe_errors + review_errors
        effective_mode = batch_resp.get("mode") or ("range_review" if request.start_date and request.end_date else "trade_date_review")

        return {
            "subject_type": "candidate_scan",
            "subject_name": self._universe_name(request),
            "mode": effective_mode,
            "trade_date": batch_resp.get("requested_trade_date") if effective_mode != "range_review" else None,
            "requested_trade_date": batch_resp.get("requested_trade_date") if effective_mode != "range_review" else None,
            "start_date": batch_resp.get("requested_start_date") if effective_mode == "range_review" else None,
            "end_date": batch_resp.get("requested_end_date") if effective_mode == "range_review" else None,
            "member_count": len(symbols),
            "reviewed_count": len(scored_items),
            "breadth": breadth,
            "stats": stats,
            "sentiment": sentiment,
            "benchmark_summary": benchmark_summary,
            "continuity": continuity,
            "rotation": {"applicable": False, "reason": "candidate_scan is selection-oriented, not rotation-oriented"},
            "structure": structure,
            "leaders": rankings["leaders_by_candidate_score"],
            "laggards": rankings["risk_by_drawdown"],
            "rankings": rankings,
            "buckets": buckets,
            "items": output_items,
            "summary": summary,
            "partial_failure": bool(errors) or batch_resp.get("partial_failure", False),
            "errors": errors,
            "meta": {
                "review_envelope_schema": REVIEW_ENVELOPE_SCHEMA,
                "metric_schema": REVIEW_METRIC_SCHEMA,
                "sentiment_score_schema": SENTIMENT_SCORE_SCHEMA,
                "candidate_score_schema": {
                    "schema": "candidate_score_v1",
                    "score": {
                        "higher_is_stronger": True,
                        "unit": "heuristic_point",
                        "note": "selection heuristic combining relative strength, return, volume, drawdown, and streak context",
                    },
                    "labels": {
                        "candidate": "score >= 8 and no severe risk",
                        "watchlist": "4 <= score < 8",
                        "observe": "0 <= score < 4",
                        "risk_alert": "score < 0 or severe risk dominates",
                    },
                },
                "universe": {
                    "requested_symbols": request.symbols or [],
                    "requested_sector_names": request.sector_names or [],
                    "requested_pool_type": request.pool_type,
                    "resolved_symbols": symbols,
                    "resolved_symbol_count": len(symbols),
                    "truncated": universe.get("truncated", False),
                    "source_breakdown": universe.get("source_breakdown", {}),
                    "sector_details": universe.get("sector_details", []),
                    "pool": universe.get("pool", None),
                },
                "filters": {
                    "min_candidate_score": request.min_candidate_score,
                    "min_relative_strength": request.min_relative_strength,
                    "min_return": request.min_return,
                    "max_drawdown_limit": request.max_drawdown_limit,
                    "min_volume_ratio": request.min_volume_ratio,
                    "min_up_streak": getattr(request, "min_up_streak", None),
                    "max_down_streak": getattr(request, "max_down_streak", None),
                    "require_source_tags": getattr(request, "require_source_tags", None),
                    "exclude_risk_flags": getattr(request, "exclude_risk_flags", None),
                    "must_have_reason_tags": getattr(request, "must_have_reason_tags", None),
                    "exclude_reason_tags": getattr(request, "exclude_reason_tags", None),
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

    def _universe_name(self, request) -> str:
        components = []
        if request.symbols:
            components.append("manual")
        if request.sector_names:
            components.append("sector")
        if request.pool_type:
            components.append(f"pool:{request.pool_type}")
        return "+".join(components) if components else "mixed_universe"

    def _extract_value(self, item, key: str):
        if isinstance(item, dict):
            return item.get(key)
        return getattr(item, key, None)

    def _normalize_symbol(self, raw_symbol: str) -> str:
        return self.resolver.resolve(raw_symbol, "stock").symbol

    def _build_universe(self, request):
        symbols: list[str] = []
        source_tags: dict[str, list[str]] = {}
        errors: list[dict] = []
        sector_details: list[dict] = []
        source_breakdown = {"manual": 0, "sector_members": 0, "pool_members": 0}

        def add_symbol(raw_symbol: str, source_tag: str, source_bucket: str):
            try:
                symbol = self._normalize_symbol(raw_symbol)
            except Exception as exc:
                errors.append({"scope": "symbol_resolve", "symbol": raw_symbol, **serialize_exception(exc)})
                return
            if symbol not in source_tags:
                symbols.append(symbol)
                source_tags[symbol] = []
            if source_tag not in source_tags[symbol]:
                source_tags[symbol].append(source_tag)
            source_breakdown[source_bucket] += 1

        for raw_symbol in request.symbols or []:
            add_symbol(raw_symbol, "manual", "manual")

        for sector_name in request.sector_names or []:
            try:
                resp = self.sector_lookup.execute(
                    SimpleNamespace(
                        mode="children",
                        sector_type=request.sector_type,
                        sector_name=sector_name,
                        limit=request.limit,
                        provider="zhitu",
                    )
                )
                resolved_count = 0
                for item in resp.get("items", []):
                    symbol = self._extract_value(item, "symbol")
                    if not symbol:
                        continue
                    add_symbol(symbol, f"sector:{sector_name}", "sector_members")
                    resolved_count += 1
                sector_details.append(
                    {
                        "sector_name": sector_name,
                        "count": resolved_count,
                        "source": resp.get("source"),
                        "meta": resp.get("meta", {}),
                    }
                )
            except Exception as exc:
                errors.append({"scope": "sector_lookup", "sector_name": sector_name, **serialize_exception(exc)})

        pool_meta = None
        if request.pool_type:
            pool_reference_date = request.trade_date or request.end_date or request.start_date
            try:
                resp = self.market_pool.execute(
                    SimpleNamespace(
                        pool_type=request.pool_type,
                        trade_date=pool_reference_date,
                        limit=request.limit,
                        provider="zhitu",
                    )
                )
                for item in resp.get("items", []):
                    symbol = self._extract_value(item, "symbol")
                    if not symbol:
                        continue
                    add_symbol(symbol, f"pool:{request.pool_type}", "pool_members")
                pool_meta = {
                    "pool_type": request.pool_type,
                    "trade_date": resp.get("trade_date"),
                    "requested_trade_date": resp.get("requested_trade_date"),
                    "count": resp.get("count"),
                    "source": resp.get("source"),
                    "meta": resp.get("meta", {}),
                }
            except Exception as exc:
                errors.append({"scope": "market_pool", "pool_type": request.pool_type, **serialize_exception(exc)})

        truncated = False
        if len(symbols) > self.MAX_UNIVERSE_SYMBOLS:
            symbols = symbols[: self.MAX_UNIVERSE_SYMBOLS]
            source_tags = {symbol: source_tags[symbol] for symbol in symbols}
            truncated = True

        return {
            "symbols": symbols,
            "source_tags": source_tags,
            "errors": errors,
            "sector_details": sector_details,
            "pool": pool_meta,
            "source_breakdown": source_breakdown,
            "truncated": truncated,
        }

    def _to_candidate_card(self, item: dict, source_tags: list[str]) -> dict:
        candidate_score, candidate_label, reason_tags, risk_flags, score_breakdown = self._candidate_signal(item)
        return {
            **item,
            "candidate_score": candidate_score,
            "candidate_label": candidate_label,
            "reason_tags": reason_tags,
            "risk_flags": risk_flags,
            "candidate_score_breakdown": score_breakdown,
            "source_tags": source_tags,
            "review_tags": item.get("tags", []),
        }

    def _candidate_signal(self, item: dict) -> tuple[float, str, list[str], list[str], dict]:
        score = 0.0
        reasons: list[str] = []
        risks: list[str] = []
        breakdown = {
            "relative_strength": 0.0,
            "return": 0.0,
            "volume": 0.0,
            "drawdown": 0.0,
            "streak": 0.0,
        }

        relative_strength = item.get("relative_strength")
        return_pct = item.get("return")
        max_drawdown = item.get("max_drawdown")
        volume_ratio = item.get("volume_ratio")
        stats = item.get("stats", {}) or {}
        up_streak = int(stats.get("up_streak", 0) or 0)
        down_streak = int(stats.get("down_streak", 0) or 0)

        if relative_strength is not None:
            if relative_strength >= 10:
                score += 5.0
                breakdown["relative_strength"] += 5.0
                reasons.append("very_strong_relative_strength")
            elif relative_strength >= 5:
                score += 4.0
                breakdown["relative_strength"] += 4.0
                reasons.append("strong_relative_strength")
            elif relative_strength >= 2:
                score += 3.0
                breakdown["relative_strength"] += 3.0
                reasons.append("positive_relative_strength")
            elif relative_strength > 0:
                score += 1.5
                breakdown["relative_strength"] += 1.5
                reasons.append("slight_relative_strength")
            elif relative_strength <= -10:
                score -= 4.0
                breakdown["relative_strength"] -= 4.0
                risks.append("very_weak_relative_strength")
            elif relative_strength < 0:
                score -= 1.5
                breakdown["relative_strength"] -= 1.5
                risks.append("weak_relative_strength")

        if return_pct is not None:
            if return_pct >= 15:
                score += 4.0
                breakdown["return"] += 4.0
                reasons.append("high_momentum")
            elif return_pct >= 8:
                score += 3.0
                breakdown["return"] += 3.0
                reasons.append("strong_return")
            elif return_pct >= 3:
                score += 2.0
                breakdown["return"] += 2.0
                reasons.append("positive_return")
            elif return_pct > 0:
                score += 1.0
                breakdown["return"] += 1.0
                reasons.append("slight_positive_return")
            elif return_pct <= -5:
                score -= 3.0
                breakdown["return"] -= 3.0
                risks.append("negative_return")
            elif return_pct < 0:
                score -= 1.0
                breakdown["return"] -= 1.0
                risks.append("soft_negative_return")

        if volume_ratio is not None:
            if volume_ratio >= 2.0:
                score += 2.0
                breakdown["volume"] += 2.0
                reasons.append("high_volume")
            elif volume_ratio >= 1.2:
                score += 1.0
                breakdown["volume"] += 1.0
                reasons.append("active_volume")

        if max_drawdown is not None:
            if max_drawdown <= 3:
                score += 1.5
                breakdown["drawdown"] += 1.5
                reasons.append("low_drawdown")
            elif max_drawdown <= 5:
                score += 1.0
                breakdown["drawdown"] += 1.0
                reasons.append("controlled_drawdown")
            elif max_drawdown >= 10:
                score -= 2.5
                breakdown["drawdown"] -= 2.5
                risks.append("severe_drawdown")
            elif max_drawdown >= 8:
                score -= 1.5
                breakdown["drawdown"] -= 1.5
                risks.append("drawdown_risk")

        if up_streak >= 3:
            score += 1.5
            breakdown["streak"] += 1.5
            reasons.append("strong_up_streak")
        elif up_streak >= 2:
            score += 1.0
            breakdown["streak"] += 1.0
            reasons.append("up_streak")

        if down_streak >= 3:
            score -= 2.0
            breakdown["streak"] -= 2.0
            risks.append("strong_down_streak")
        elif down_streak >= 2:
            score -= 1.0
            breakdown["streak"] -= 1.0
            risks.append("down_streak")

        severe_risk = any(flag in {"very_weak_relative_strength", "severe_drawdown", "strong_down_streak"} for flag in risks)
        rounded = round(score, 2)
        if severe_risk and rounded < 4:
            label = "risk_alert"
        elif rounded >= 8:
            label = "candidate"
        elif rounded >= 4:
            label = "watchlist"
        elif rounded < 0:
            label = "risk_alert"
        else:
            label = "observe"
        breakdown["total"] = round(score, 2)
        return rounded, label, reasons, risks, breakdown

    def _apply_filters(self, items: list[dict], request) -> list[dict]:
        filtered = []
        for item in items:
            if request.min_candidate_score is not None and item.get("candidate_score") < request.min_candidate_score:
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
            if getattr(request, "min_up_streak", None) is not None:
                up_streak = int((item.get("stats") or {}).get("up_streak", 0) or 0)
                if up_streak < getattr(request, "min_up_streak", None):
                    continue
            if getattr(request, "max_down_streak", None) is not None:
                down_streak = int((item.get("stats") or {}).get("down_streak", 0) or 0)
                if down_streak > getattr(request, "max_down_streak", None):
                    continue
            if getattr(request, "require_source_tags", None):
                tags = set(item.get("source_tags") or [])
                if not all(tag in tags for tag in getattr(request, "require_source_tags", None)):
                    continue
            if getattr(request, "exclude_risk_flags", None):
                risks = set(item.get("risk_flags") or [])
                if any(flag in risks for flag in getattr(request, "exclude_risk_flags", None)):
                    continue
            if getattr(request, "must_have_reason_tags", None):
                reasons = set(item.get("reason_tags") or [])
                if not all(tag in reasons for tag in getattr(request, "must_have_reason_tags", None)):
                    continue
            if getattr(request, "exclude_reason_tags", None):
                reasons = set(item.get("reason_tags") or [])
                if any(tag in reasons for tag in getattr(request, "exclude_reason_tags", None)):
                    continue
            filtered.append(item)
        return filtered

    def _sort_value(self, value, descending: bool):
        if value is None:
            return float("-inf") if descending else float("inf")
        return value

    def _sort_items(self, items: list[dict], sort_by: str, descending: bool) -> list[dict]:
        key_map = {
            "candidate_score": "candidate_score",
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
            "candidate_count": sum(1 for item in items if item.get("candidate_label") == "candidate"),
            "watchlist_count": sum(1 for item in items if item.get("candidate_label") == "watchlist"),
            "observe_count": sum(1 for item in items if item.get("candidate_label") == "observe"),
            "risk_alert_count": sum(1 for item in items if item.get("candidate_label") == "risk_alert"),
        }

    def _build_stats(self, items: list[dict]) -> dict:
        returns = self._metric_values(items, "return")
        relative_strengths = self._metric_values(items, "relative_strength")
        volume_ratios = self._metric_values(items, "volume_ratio")
        drawdowns = self._metric_values(items, "max_drawdown")
        candidate_scores = self._metric_values(items, "candidate_score")
        return {
            "avg_return": self._avg_or_none(returns),
            "median_return": self._median_or_none(returns),
            "avg_relative_strength": self._avg_or_none(relative_strengths),
            "median_relative_strength": self._median_or_none(relative_strengths),
            "avg_volume_ratio": self._avg_or_none(volume_ratios),
            "median_volume_ratio": self._median_or_none(volume_ratios),
            "max_drawdown_worst": max(drawdowns) if drawdowns else None,
            "avg_max_drawdown": self._avg_or_none(drawdowns),
            "avg_candidate_score": self._avg_or_none(candidate_scores),
            "median_candidate_score": self._median_or_none(candidate_scores),
            "best_candidate_score": max(candidate_scores) if candidate_scores else None,
            "worst_candidate_score": min(candidate_scores) if candidate_scores else None,
            "return_stddev": pstdev(returns) if len(returns) >= 2 else None,
            "candidate_score_stddev": pstdev(candidate_scores) if len(candidate_scores) >= 2 else None,
        }

    def _build_sentiment(self, stats: dict, breadth: dict) -> dict:
        score = 0.0
        avg_return = stats.get("avg_return")
        avg_rs = stats.get("avg_relative_strength")
        candidate_count = breadth.get("candidate_count", 0)
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

        if candidate_count > 0:
            score += min(candidate_count * 0.5, 1.5)
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
        candidate_ratio = (breadth.get("candidate_count", 0) / reviewed_count) if reviewed_count else 0.0
        risk_ratio = (breadth.get("risk_alert_count", 0) / reviewed_count) if reviewed_count else 0.0
        stronger_ratio = (breadth.get("stronger_than_benchmark_count", 0) / reviewed_count) if reviewed_count else 0.0
        tags: list[str] = []

        if candidate_ratio >= 0.4:
            tags.append("candidate_dense")
        if risk_ratio >= 0.3:
            tags.append("risk_dense")
        if stronger_ratio >= 0.5:
            tags.append("benchmark_outperform")
        if stats.get("candidate_score_stddev") is not None and stats.get("candidate_score_stddev") >= 3:
            tags.append("high_dispersion")
        tags.append(f"sentiment_{sentiment.get('label')}")

        return {
            "coverage_ratio": (reviewed_count / member_count) if member_count else 0.0,
            "candidate_ratio": candidate_ratio,
            "risk_ratio": risk_ratio,
            "stronger_ratio": stronger_ratio,
            "tags": tags,
        }

    def _rank_by_metric(self, items: list[dict], metric: str, descending: bool, top_n: int) -> list[dict]:
        return sorted(items, key=lambda item: self._sort_value(item.get(metric), descending), reverse=descending)[:top_n]

    def _build_rankings(self, items: list[dict], top_n: int) -> dict:
        return {
            "leaders_by_candidate_score": self._rank_by_metric(items, "candidate_score", True, top_n),
            "leaders_by_relative_strength": self._rank_by_metric(items, "relative_strength", True, top_n),
            "leaders_by_return": self._rank_by_metric(items, "return", True, top_n),
            "leaders_by_volume_ratio": self._rank_by_metric(items, "volume_ratio", True, top_n),
            "risk_by_drawdown": self._rank_by_metric(items, "max_drawdown", True, top_n),
        }

    def _build_buckets(self, items: list[dict], top_n: int) -> dict:
        candidates = [item for item in items if item.get("candidate_label") == "candidate"]
        watchlist = [item for item in items if item.get("candidate_label") == "watchlist"]
        observe = [item for item in items if item.get("candidate_label") == "observe"]
        risk_alerts = [item for item in items if item.get("candidate_label") == "risk_alert"]
        return {
            "candidates": self._rank_by_metric(candidates, "candidate_score", True, top_n),
            "watchlist": self._rank_by_metric(watchlist, "candidate_score", True, top_n),
            "observe": self._rank_by_metric(observe, "candidate_score", True, top_n),
            "risk_alerts": self._rank_by_metric(risk_alerts, "candidate_score", False, top_n),
        }

    def _fmt_pct(self, value):
        return "未知" if value is None else f"{value:.2f}%"

    def _fmt_num(self, value):
        return "未知" if value is None else f"{value:.2f}"

    def _build_summary(self, mode: str | None, universe_name: str, member_count: int, reviewed_count: int, selected_count: int, stats: dict, breadth: dict, sentiment: dict, rankings: dict, buckets: dict) -> str:
        mode_label = "区间扫描" if mode == "range_review" else "单日扫描"
        leader = rankings.get("leaders_by_candidate_score", [{}])[0].get("symbol") if rankings.get("leaders_by_candidate_score") else "未知"
        return (
            f"候选扫描完成：{universe_name}，{mode_label}；候选池 {member_count} 只，成功复盘 {reviewed_count} 只，筛选后保留 {selected_count} 只；"
            f"平均收益 {self._fmt_pct(stats.get('avg_return'))}，平均相对强弱 {self._fmt_pct(stats.get('avg_relative_strength'))}，平均候选分 {self._fmt_num(stats.get('avg_candidate_score'))}，情绪 {sentiment.get('label_zh')}；"
            f"候选 {breadth.get('candidate_count', 0)} 只，观察 {breadth.get('watchlist_count', 0)} 只，风险提示 {breadth.get('risk_alert_count', 0)} 只；"
            f"最高优先 {leader}。"
        )
