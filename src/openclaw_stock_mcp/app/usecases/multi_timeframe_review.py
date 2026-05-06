from __future__ import annotations

from statistics import median, pstdev
from types import SimpleNamespace

from openclaw_stock_mcp.app.services.metric_schema import (
    REVIEW_ENVELOPE_SCHEMA,
    REVIEW_METRIC_SCHEMA,
    SENTIMENT_SCORE_SCHEMA,
    build_sentiment_payload,
)
from openclaw_stock_mcp.app.usecases.stock_history import StockHistoryUseCase
from openclaw_stock_mcp.app.usecases.technical_indicator import TechnicalIndicatorUseCase
from openclaw_stock_mcp.providers.errors import ProviderError


class MultiTimeframeReviewUseCase:
    def __init__(self) -> None:
        self.stock_history = StockHistoryUseCase()
        self.technical_indicator = TechnicalIndicatorUseCase()

    def execute(self, request):
        cards = []
        errors = []

        for interval in request.intervals:
            try:
                card = self._build_timeframe_card(request, interval)
                cards.append(card)
            except Exception as exc:
                errors.append({"interval": interval, "error_code": getattr(exc, "code", "ERROR"), "message": str(exc), "retryable": getattr(exc, "retryable", False), "provider": getattr(exc, "provider", None)})

        if not cards:
            raise ProviderError("EMPTY_RESULT", "No timeframe review results available", retryable=False)

        cards = self._sort_cards(cards, request.intervals)
        breadth = self._build_breadth(cards)
        stats = self._build_stats(cards)
        sentiment = self._build_sentiment(stats, breadth)
        benchmark_summary = self._build_benchmark_summary(cards)
        continuity = self._build_continuity(cards)
        structure = self._build_structure(cards, breadth, stats, sentiment)
        alignment_score, alignment_label, conflict_points = self._build_alignment(cards)
        summary = self._build_summary(request.symbol, cards, stats, sentiment, alignment_label, conflict_points)

        return {
            "subject_type": "multi_timeframe",
            "subject_name": request.symbol,
            "mode": "range_review" if request.start_date and request.end_date else "trade_date_review",
            "trade_date": request.trade_date if not (request.start_date and request.end_date) else None,
            "requested_trade_date": request.trade_date if not (request.start_date and request.end_date) else None,
            "start_date": request.start_date if request.start_date and request.end_date else None,
            "end_date": request.end_date if request.start_date and request.end_date else None,
            "member_count": len(request.intervals),
            "reviewed_count": len(cards),
            "breadth": breadth,
            "stats": stats,
            "sentiment": sentiment,
            "benchmark_summary": benchmark_summary,
            "continuity": continuity,
            "rotation": {"applicable": False, "reason": "multi_timeframe review focuses on cross-timeframe alignment, not sector rotation"},
            "structure": structure,
            "leaders": cards[: min(2, len(cards))],
            "laggards": cards[-min(2, len(cards)):],
            "rankings": {
                "timeframes_by_score": sorted(cards, key=lambda x: x.get("timeframe_score", 0), reverse=True),
                "strongest_trend_timeframes": sorted(cards, key=lambda x: x.get("trend_score", 0), reverse=True),
            },
            "buckets": {
                "bullish_timeframes": [card for card in cards if card.get("trend_label") == "bullish"],
                "neutral_timeframes": [card for card in cards if card.get("trend_label") == "neutral"],
                "bearish_timeframes": [card for card in cards if card.get("trend_label") == "bearish"],
                "conflict_points": conflict_points,
            },
            "items": cards,
            "summary": summary,
            "partial_failure": bool(errors),
            "errors": errors,
            "meta": {
                "review_envelope_schema": REVIEW_ENVELOPE_SCHEMA,
                "metric_schema": REVIEW_METRIC_SCHEMA,
                "sentiment_score_schema": SENTIMENT_SCORE_SCHEMA,
                "alignment_score_schema": {
                    "schema": "multi_timeframe_alignment_v1",
                    "score": {
                        "higher_is_stronger": True,
                        "unit": "heuristic_point",
                        "note": "cross-timeframe alignment score combining trend polarity and conflict severity",
                    },
                },
                "requested_intervals": request.intervals,
                "requested_indicators": request.indicators,
            },
        }

    def _build_timeframe_card(self, request, interval: str) -> dict:
        history_resp = self.stock_history.execute(
            SimpleNamespace(
                symbol=request.symbol,
                sec_type=request.sec_type,
                interval=interval,
                start_date=request.start_date,
                end_date=request.end_date,
                limit=request.limit,
                adjust="none",
                provider=None,
            )
        )
        items = history_resp.get("items", [])
        if len(items) < 2:
            raise ProviderError("EMPTY_RESULT", f"Not enough bars for interval {interval}", retryable=False)

        closes = [bar.close for bar in items if getattr(bar, "close", None) is not None]
        latest = closes[-1] if closes else None
        prev = closes[-2] if len(closes) >= 2 else None
        first = closes[0] if closes else None
        timeframe_return = (((latest - first) / first) * 100) if latest not in (None,) and first not in (None, 0) else None
        slope = (((latest - prev) / prev) * 100) if latest not in (None,) and prev not in (None, 0) else None

        indicator_payloads = {}
        for indicator in request.indicators or []:
            try:
                series = self.technical_indicator.execute(
                    SimpleNamespace(
                        symbol=request.symbol,
                        sec_type=request.sec_type,
                        interval=interval,
                        indicator=indicator,
                        start_date=request.start_date,
                        end_date=request.end_date,
                        limit=min(request.limit, 120),
                        provider=None,
                    )
                )
                indicator_payloads[indicator] = series
            except Exception:
                continue

        trend_score, trend_label, signal_tags, conflict_notes = self._evaluate_timeframe(interval, items, indicator_payloads)
        return {
            "interval": interval,
            "bar_count": len(items),
            "latest_close": latest,
            "timeframe_return": timeframe_return,
            "latest_slope": slope,
            "trend_score": trend_score,
            "timeframe_score": trend_score,
            "trend_label": trend_label,
            "signal_tags": signal_tags,
            "conflict_notes": conflict_notes,
            "history_meta": history_resp.get("meta", {}),
            "indicator_meta": {name: payload.get("meta", {}) for name, payload in indicator_payloads.items() if isinstance(payload, dict)},
            "indicator_snapshot": self._extract_indicator_snapshot(indicator_payloads),
            "source": {
                "history": history_resp.get("source"),
                "indicators": {name: payload.get("source") for name, payload in indicator_payloads.items() if isinstance(payload, dict)},
            },
        }

    def _extract_indicator_snapshot(self, indicator_payloads: dict) -> dict:
        snapshot = {}
        for name, payload in indicator_payloads.items():
            items = payload.get("items", []) if isinstance(payload, dict) else []
            if not items:
                continue
            point = items[-1]
            snapshot[name] = {
                "time": point.get("time") if isinstance(point, dict) else getattr(point, "time", None),
                "values": point.get("values") if isinstance(point, dict) else getattr(point, "values", {}),
            }
        return snapshot

    def _point_values(self, point):
        if isinstance(point, dict):
            return point.get("values", {}) or {}
        return getattr(point, "values", {}) or {}

    def _evaluate_timeframe(self, interval: str, bars, indicator_payloads: dict) -> tuple[float, str, list[str], list[str]]:
        score = 0.0
        tags: list[str] = []
        conflicts: list[str] = []

        closes = [bar.close for bar in bars if getattr(bar, "close", None) is not None]
        latest = closes[-1]
        prev = closes[-2] if len(closes) >= 2 else None
        ma5 = sum(closes[-5:]) / min(5, len(closes)) if closes else None
        ma10 = sum(closes[-10:]) / min(10, len(closes)) if closes else None

        if latest is not None and ma5 is not None:
            if latest > ma5:
                score += 1.5
                tags.append("above_ma_short")
            else:
                score -= 1.0
                tags.append("below_ma_short")

        if ma5 is not None and ma10 is not None:
            if ma5 >= ma10:
                score += 1.0
                tags.append("ma_short_over_mid")
            else:
                score -= 1.0
                tags.append("ma_short_under_mid")

        if latest is not None and prev not in (None, 0):
            delta = ((latest - prev) / prev) * 100
            if delta >= 2:
                score += 1.0
                tags.append("positive_latest_slope")
            elif delta <= -2:
                score -= 1.0
                tags.append("negative_latest_slope")

        macd_payload = indicator_payloads.get("macd")
        if isinstance(macd_payload, dict) and macd_payload.get("items"):
            values = self._point_values(macd_payload["items"][-1])
            dif = values.get("dif") or values.get("DIF")
            dea = values.get("dea") or values.get("DEA")
            macd = values.get("macd") or values.get("MACD")
            if dif is not None and dea is not None:
                if dif >= dea:
                    score += 1.5
                    tags.append("macd_bullish")
                else:
                    score -= 1.5
                    tags.append("macd_bearish")
            if macd is not None and macd < 0 and latest is not None and ma5 is not None and latest > ma5:
                conflicts.append(f"{interval}: price above short MA but MACD remains weak")

        kdj_payload = indicator_payloads.get("kdj")
        if isinstance(kdj_payload, dict) and kdj_payload.get("items"):
            values = self._point_values(kdj_payload["items"][-1])
            k = values.get("k") or values.get("K")
            d = values.get("d") or values.get("D")
            if k is not None and d is not None:
                if k >= d:
                    score += 1.0
                    tags.append("kdj_bullish")
                else:
                    score -= 1.0
                    tags.append("kdj_bearish")

        if score >= 2.5:
            label = "bullish"
        elif score <= -2.5:
            label = "bearish"
        else:
            label = "neutral"
        return round(score, 2), label, tags, conflicts

    def _sort_cards(self, cards: list[dict], requested_intervals: list[str]) -> list[dict]:
        order = {interval: idx for idx, interval in enumerate(requested_intervals)}
        return sorted(cards, key=lambda item: order.get(item.get("interval"), 999))

    def _build_breadth(self, cards: list[dict]) -> dict:
        return {
            "bullish_count": sum(1 for card in cards if card.get("trend_label") == "bullish"),
            "neutral_count": sum(1 for card in cards if card.get("trend_label") == "neutral"),
            "bearish_count": sum(1 for card in cards if card.get("trend_label") == "bearish"),
            "conflict_count": sum(1 for card in cards if card.get("conflict_notes")),
        }

    def _metric_values(self, cards: list[dict], key: str) -> list[float]:
        values = [card.get(key) for card in cards if card.get(key) is not None]
        return [float(v) for v in values]

    def _avg_or_none(self, values: list[float]) -> float | None:
        return (sum(values) / len(values)) if values else None

    def _build_stats(self, cards: list[dict]) -> dict:
        trend_scores = self._metric_values(cards, "trend_score")
        returns = self._metric_values(cards, "timeframe_return")
        return {
            "avg_trend_score": self._avg_or_none(trend_scores),
            "median_trend_score": median(trend_scores) if trend_scores else None,
            "best_trend_score": max(trend_scores) if trend_scores else None,
            "worst_trend_score": min(trend_scores) if trend_scores else None,
            "trend_score_stddev": pstdev(trend_scores) if len(trend_scores) >= 2 else None,
            "avg_timeframe_return": self._avg_or_none(returns),
            "median_timeframe_return": median(returns) if returns else None,
        }

    def _build_sentiment(self, stats: dict, breadth: dict) -> dict:
        score = 0.0
        avg_trend = stats.get("avg_trend_score")
        if avg_trend is not None:
            if avg_trend >= 3:
                score += 2.0
            elif avg_trend >= 1:
                score += 1.0
            elif avg_trend <= -3:
                score -= 2.0
            elif avg_trend < -1:
                score -= 1.0
        score += breadth.get("bullish_count", 0) * 0.5
        score -= breadth.get("bearish_count", 0) * 0.5
        score -= breadth.get("conflict_count", 0) * 0.25
        return build_sentiment_payload(score)

    def _build_benchmark_summary(self, cards: list[dict]) -> dict:
        history_sources = [card.get("source", {}).get("history") for card in cards if card.get("source", {}).get("history")]
        if not history_sources:
            return {"dominant_source": None, "source_mix": []}
        counts = {}
        for source in history_sources:
            counts[source] = counts.get(source, 0) + 1
        dominant = max(counts.items(), key=lambda x: x[1])[0]
        return {
            "dominant_source": dominant,
            "source_mix": [{"source": k, "count": v} for k, v in sorted(counts.items(), key=lambda x: (-x[1], x[0]))],
        }

    def _build_continuity(self, cards: list[dict]) -> dict:
        return {
            "bullish_timeframe_count": sum(1 for card in cards if card.get("trend_label") == "bullish"),
            "bearish_timeframe_count": sum(1 for card in cards if card.get("trend_label") == "bearish"),
            "conflict_timeframe_count": sum(1 for card in cards if card.get("conflict_notes")),
        }

    def _build_structure(self, cards: list[dict], breadth: dict, stats: dict, sentiment: dict) -> dict:
        tags = []
        if breadth.get("bullish_count", 0) >= max(1, len(cards) - 1):
            tags.append("broad_bullish_alignment")
        if breadth.get("bearish_count", 0) >= max(1, len(cards) - 1):
            tags.append("broad_bearish_alignment")
        if breadth.get("conflict_count", 0) >= 2:
            tags.append("high_conflict")
        if stats.get("trend_score_stddev") is not None and stats.get("trend_score_stddev") >= 2:
            tags.append("high_dispersion")
        tags.append(f"sentiment_{sentiment.get('label')}")
        return {"tags": tags}

    def _build_alignment(self, cards: list[dict]) -> tuple[float, str, list[str]]:
        bullish = sum(1 for card in cards if card.get("trend_label") == "bullish")
        bearish = sum(1 for card in cards if card.get("trend_label") == "bearish")
        neutral = sum(1 for card in cards if card.get("trend_label") == "neutral")
        conflicts = []
        for card in cards:
            conflicts.extend(card.get("conflict_notes", []))

        score = bullish * 2.0 - bearish * 2.0 - len(conflicts) * 0.5 - neutral * 0.5
        if bullish >= max(2, len(cards) - 1) and not conflicts:
            label = "aligned_bullish"
        elif bearish >= max(2, len(cards) - 1) and not conflicts:
            label = "aligned_bearish"
        elif conflicts or (bullish > 0 and bearish > 0):
            label = "mixed_conflict"
        else:
            label = "mixed_neutral"
        return round(score, 2), label, conflicts

    def _build_summary(self, symbol: str, cards: list[dict], stats: dict, sentiment: dict, alignment_label: str, conflict_points: list[str]) -> str:
        intervals = ", ".join(card.get("interval", "?") for card in cards)
        top = max(cards, key=lambda card: card.get("trend_score", -999))
        return (
            f"多周期复盘完成：{symbol}；周期 {intervals}；平均趋势分 {stats.get('avg_trend_score') if stats.get('avg_trend_score') is not None else '未知'}，情绪 {sentiment.get('label_zh')}；"
            f"整体结构 {alignment_label}；当前最强周期 {top.get('interval')}（{top.get('trend_label')}）。"
            + (f" 冲突点 {len(conflict_points)} 处。" if conflict_points else "")
        )
