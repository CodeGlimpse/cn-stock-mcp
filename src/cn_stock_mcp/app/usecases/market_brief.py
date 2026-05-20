from __future__ import annotations

from datetime import datetime

from cn_stock_mcp.app.models.quote import Quote
from cn_stock_mcp.app.services.fallback import run_with_fallback_meta
from cn_stock_mcp.app.services.metric_schema import (
    REVIEW_ENVELOPE_SCHEMA,
    REVIEW_METRIC_SCHEMA,
    SENTIMENT_SCORE_SCHEMA,
    build_sentiment_payload,
)
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.providers.errors import ProviderError


class MarketBriefUseCase:
    REVIEW_INDICES = [
        ("000001.SH", "上证指数"),
        ("399001.SZ", "深证成指"),
        ("399006.SZ", "创业板指"),
        ("899050.BJ", "北证50"),
    ]

    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request):
        requested_trade_date = request.trade_date or datetime.now().strftime("%Y-%m-%d")
        review_mode = request.trade_date is not None

        calendar_meta: dict = {}
        effective_trade_date = requested_trade_date

        if review_mode:
            effective_trade_date, calendar_meta = self._resolve_review_trade_date(
                request.market,
                requested_trade_date,
            )
            overview, overview_meta = self._build_historical_overview(
                request.market,
                effective_trade_date,
                provider=request.provider,
            )
        else:
            overview_selection = self.router.choose_provider(
                tool_name="market_overview",
                sec_type="index",
                preferred=(None if request.provider == "mixed" else request.provider),
            )
            overview, overview_meta = run_with_fallback_meta(
                self.router,
                overview_selection,
                lambda provider: provider.get_market_overview(request.market),
            )
            overview_meta = {
                "selected_primary": overview_meta.selected_primary,
                "selected_fallback": overview_meta.selected_fallback,
                "attempted": overview_meta.attempted,
                "final_provider": overview_meta.final_provider,
                "used_fallback": overview_meta.used_fallback,
                "mode": "realtime",
            }

        pools: dict[str, dict] = {}
        pools_meta: dict[str, dict] = {}
        if request.include_pools:
            for pool_type in ("limit_up", "limit_down", "strong"):
                pool_selection = self.router.choose_provider(
                    tool_name="market_pool",
                    sec_type="stock",
                    preferred=(getattr(request, "provider", None) or "zhitu"),
                )
                items, pool_meta = run_with_fallback_meta(
                    self.router,
                    pool_selection,
                    lambda provider, _pool_type=pool_type: provider.get_market_pool(
                        pool_type=_pool_type,
                        trade_date=effective_trade_date,
                    ),
                )
                top_items = items[: request.top_n] if request.top_n else items
                pools[pool_type] = {
                    "count": len(items),
                    "top_items": top_items,
                    "source": pool_meta.final_provider or pool_selection.primary,
                }
                pools_meta[pool_type] = {
                    "selected_primary": pool_meta.selected_primary,
                    "selected_fallback": pool_meta.selected_fallback,
                    "attempted": pool_meta.attempted,
                    "final_provider": pool_meta.final_provider,
                    "used_fallback": pool_meta.used_fallback,
                }

        indices = overview.get("indices", []) if isinstance(overview, dict) else []
        index_ranking = self._build_index_ranking(indices)
        breadth = self._build_breadth(pools)
        sentiment = self._build_sentiment(index_ranking, breadth)
        highlights = self._build_highlights(index_ranking, breadth)

        stats = self._build_stats(index_ranking, breadth)
        continuity = self._build_continuity(index_ranking)
        leaders = self._build_item_cards(index_ranking[: request.top_n], mode=("trade_date_review" if review_mode else "realtime_brief"), trade_date=effective_trade_date)
        laggards = self._build_item_cards(list(reversed(index_ranking[-request.top_n:])), mode=("trade_date_review" if review_mode else "realtime_brief"), trade_date=effective_trade_date) if index_ranking and request.top_n else []
        rankings = self._build_rankings(leaders, laggards, index_ranking, request.top_n, effective_trade_date, review_mode)
        buckets = self._build_buckets(pools, request.top_n, effective_trade_date, review_mode)
        benchmark_summary = self._build_benchmark_summary(index_ranking)
        rotation = self._build_rotation(index_ranking, breadth, review_mode)
        structure = self._build_structure(index_ranking, breadth)
        items = self._build_item_cards(index_ranking, mode=("trade_date_review" if review_mode else "realtime_brief"), trade_date=effective_trade_date)
        summary = self._build_summary(
            indices,
            pools,
            requested_trade_date=requested_trade_date,
            effective_trade_date=effective_trade_date,
            brief_type=request.brief_type,
            review_mode=review_mode,
            adjusted_to_previous_trading_day=calendar_meta.get("adjusted_to_previous_trading_day", False),
            sentiment=sentiment,
            highlights=highlights,
        )

        partial_failure = bool(overview_meta.get("partial_failure"))
        errors = list(overview_meta.get("errors", []))

        return {
            "subject_type": "market",
            "subject_name": request.market,
            "brief_type": request.brief_type,
            "mode": "trade_date_review" if review_mode else "realtime_brief",
            "trade_date": effective_trade_date,
            "requested_trade_date": requested_trade_date,
            "start_date": None,
            "end_date": None,
            "member_count": len(index_ranking),
            "reviewed_count": len(index_ranking),
            "market": request.market,
            "overview": overview,
            "index_ranking": index_ranking,
            "breadth": breadth,
            "stats": stats,
            "sentiment": sentiment,
            "benchmark_summary": benchmark_summary,
            "continuity": continuity,
            "rotation": rotation,
            "structure": structure,
            "highlights": highlights,
            "leaders": leaders,
            "laggards": laggards,
            "rankings": rankings,
            "buckets": buckets,
            "items": items,
            "pools": pools,
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
                        "note": "relative signal used only for market internal comparison; not normalized across tools",
                    },
                },
                "review_mode": review_mode,
                "calendar": calendar_meta,
                "overview": overview_meta,
                "pools": pools_meta,
            },
        }

    def _resolve_review_trade_date(self, market: str, requested_trade_date: str) -> tuple[str, dict]:
        provider = self.router.get_provider("akshare")
        calendar = provider.get_trading_calendar(
            market=market,
            date=requested_trade_date,
            recent_limit=5,
        )
        is_trading_day = bool(calendar.get("is_trading_day"))
        effective_trade_date = requested_trade_date if is_trading_day else calendar.get("previous_trading_day")
        if not effective_trade_date:
            raise ProviderError(
                "INVALID_ARGUMENT",
                f"No effective trading day found for requested date: {requested_trade_date}",
                retryable=False,
            )
        return effective_trade_date, {
            "requested_trade_date": requested_trade_date,
            "effective_trade_date": effective_trade_date,
            "requested_is_trading_day": is_trading_day,
            "adjusted_to_previous_trading_day": effective_trade_date != requested_trade_date,
            "previous_trading_day": calendar.get("previous_trading_day"),
            "next_trading_day": calendar.get("next_trading_day"),
            "recent_trading_days": calendar.get("recent_trading_days", []),
            "source": calendar.get("source"),
        }

    def _build_historical_overview(self, market: str, trade_date: str, provider: str | None):
        previous_trade_date = self.router.get_provider("akshare").get_trading_calendar(
            market=market,
            date=trade_date,
            recent_limit=2,
        ).get("previous_trading_day")

        indices: list[Quote] = []
        per_index_meta: list[dict] = []
        errors: list[dict] = []

        preferred = None if provider == "mixed" else provider

        for symbol, name in self.REVIEW_INDICES:
            selection = self.router.choose_provider(
                tool_name="stock_history",
                symbol=symbol,
                sec_type="index",
                preferred=preferred,
            )
            try:
                bars, fallback_meta = run_with_fallback_meta(
                    self.router,
                    selection,
                    lambda p, _symbol=symbol: p.get_history(
                        symbol=_symbol,
                        sec_type="index",
                        interval="1d",
                        start=previous_trade_date or trade_date,
                        end=trade_date,
                        limit=2,
                        adjust="none",
                    ),
                )
                if not bars:
                    raise ProviderError("PROVIDER_UNAVAILABLE", f"No index history returned for {symbol}", retryable=True)
                target_bar = bars[-1]
                prev_close = target_bar.prev_close
                if prev_close is None and len(bars) >= 2:
                    prev_close = bars[-2].close
                change = None
                change_percent = None
                if target_bar.close is not None and prev_close not in (None, 0):
                    change = target_bar.close - prev_close
                    change_percent = (change / prev_close) * 100
                indices.append(
                    Quote(
                        symbol=symbol,
                        name=name,
                        sec_type="index",
                        exchange=symbol.split(".", 1)[1],
                        board="index",
                        price=target_bar.close,
                        open=target_bar.open,
                        high=target_bar.high,
                        low=target_bar.low,
                        prev_close=prev_close,
                        change=change,
                        change_percent=change_percent,
                        volume=target_bar.volume,
                        turnover=target_bar.turnover,
                        timestamp=target_bar.time,
                        source=fallback_meta.final_provider or selection.primary,
                    )
                )
                per_index_meta.append(
                    {
                        "symbol": symbol,
                        "name": name,
                        "selected_primary": fallback_meta.selected_primary,
                        "selected_fallback": fallback_meta.selected_fallback,
                        "attempted": fallback_meta.attempted,
                        "final_provider": fallback_meta.final_provider,
                        "used_fallback": fallback_meta.used_fallback,
                    }
                )
            except Exception as exc:
                errors.append({"symbol": symbol, "name": name, "error": str(exc)})

        return (
            {
                "market": market,
                "trade_date": trade_date,
                "indices": indices,
                "source": "historical-index-history",
            },
            {
                "mode": "historical",
                "history_interval": "1d",
                "trade_date": trade_date,
                "previous_trading_day": previous_trade_date,
                "per_index": per_index_meta,
                "partial_failure": len(errors) > 0,
                "errors": errors,
            },
        )

    def _build_index_ranking(self, indices: list[Quote]) -> list[dict]:
        ranked = []
        for q in indices:
            ranked.append(
                {
                    "symbol": q.symbol,
                    "name": q.name,
                    "change_percent": q.change_percent,
                    "change": q.change,
                    "price": q.price,
                    "source": q.source,
                }
            )
        ranked.sort(key=lambda x: (-9999 if x["change_percent"] is None else -x["change_percent"], x["symbol"]))
        return ranked

    def _build_breadth(self, pools: dict[str, dict]) -> dict:
        limit_up_count = pools.get("limit_up", {}).get("count", 0)
        limit_down_count = pools.get("limit_down", {}).get("count", 0)
        strong_count = pools.get("strong", {}).get("count", 0)
        ratio = None
        if limit_down_count == 0:
            ratio = None if limit_up_count == 0 else float(limit_up_count)
        else:
            ratio = round(limit_up_count / limit_down_count, 4)
        return {
            "limit_up_count": limit_up_count,
            "limit_down_count": limit_down_count,
            "strong_count": strong_count,
            "limit_up_down_spread": limit_up_count - limit_down_count,
            "limit_up_down_ratio": ratio,
        }

    def _build_sentiment(self, index_ranking: list[dict], breadth: dict) -> dict:
        score = 0.0
        up = breadth.get("limit_up_count", 0)
        down = breadth.get("limit_down_count", 0)
        strong = breadth.get("strong_count", 0)

        if up >= 80:
            score += 2.0
        elif up >= 40:
            score += 1.0

        if down <= 5:
            score += 1.0
        elif down >= 20:
            score -= 2.0
        elif down >= 10:
            score -= 1.0

        if strong >= 300:
            score += 1.0
        elif strong >= 150:
            score += 0.5

        strongest = index_ranking[0].get("change_percent") if index_ranking else None
        weakest = index_ranking[-1].get("change_percent") if index_ranking else None
        if strongest is not None and strongest >= 1.5:
            score += 1.0
        if weakest is not None and weakest <= -1.5:
            score -= 1.0

        return build_sentiment_payload(score)

    def _build_highlights(self, index_ranking: list[dict], breadth: dict) -> dict:
        strongest = index_ranking[0] if index_ranking else None
        weakest = index_ranking[-1] if index_ranking else None
        return {
            "strongest_index": strongest,
            "weakest_index": weakest,
            "limit_up_leads_limit_down": breadth.get("limit_up_count", 0) > breadth.get("limit_down_count", 0),
        }

    def _build_structure(self, index_ranking: list[dict], breadth: dict) -> dict:
        index_count = len(index_ranking)
        advancing_count = sum(1 for item in index_ranking if item.get("change_percent") is not None and item.get("change_percent") > 0)
        declining_count = sum(1 for item in index_ranking if item.get("change_percent") is not None and item.get("change_percent") < 0)
        spread = breadth.get("limit_up_down_spread", 0)
        tags: list[str] = []

        if spread > 0:
            tags.append("limit_up_advantage")
        elif spread < 0:
            tags.append("limit_down_pressure")

        if breadth.get("strong_count", 0) >= 150:
            tags.append("broad_activity")

        if advancing_count >= max(3, index_count):
            tags.append("index_breadth_positive")
        elif declining_count >= max(3, index_count):
            tags.append("index_breadth_negative")

        return {
            "coverage_ratio": 1.0 if index_count else 0.0,
            "positive_ratio": (advancing_count / index_count) if index_count else 0.0,
            "stronger_ratio": None,
            "high_volume_ratio": None,
            "index_count": index_count,
            "advancing_index_count": advancing_count,
            "declining_index_count": declining_count,
            "tags": tags,
        }

    def _build_stats(self, index_ranking: list[dict], breadth: dict) -> dict:
        changes = [float(item.get("change_percent")) for item in index_ranking if item.get("change_percent") is not None]
        return {
            "avg_return": (sum(changes) / len(changes)) if changes else None,
            "median_return": None,
            "avg_relative_strength": None,
            "median_relative_strength": None,
            "avg_volume_ratio": None,
            "median_volume_ratio": None,
            "max_drawdown_worst": None,
            "avg_max_drawdown": None,
            "best_return": max(changes) if changes else None,
            "worst_return": min(changes) if changes else None,
            "return_spread": ((max(changes) - min(changes)) if len(changes) >= 2 else None),
            "return_stddev": None,
            "relative_strength_stddev": None,
            "limit_up_count": breadth.get("limit_up_count"),
            "limit_down_count": breadth.get("limit_down_count"),
            "strong_count": breadth.get("strong_count"),
        }

    def _build_continuity(self, index_ranking: list[dict]) -> dict:
        return {
            "max_up_streak": None,
            "max_down_streak": None,
            "avg_up_streak": None,
            "avg_down_streak": None,
            "sustained_strength_count": None,
            "sustained_weakness_count": None,
            "applicable": False,
            "subject_size": len(index_ranking),
        }

    def _build_benchmark_summary(self, index_ranking: list[dict]) -> dict:
        return {
            "dominant_benchmark_symbol": None,
            "dominant_benchmark_name": None,
            "dominant_member_count": 0,
            "avg_benchmark_return": None,
            "benchmark_mix": [],
            "applicable": False,
            "subject_size": len(index_ranking),
        }

    def _build_rotation(self, index_ranking: list[dict], breadth: dict, review_mode: bool) -> dict:
        strongest = index_ranking[0].get("change_percent") if index_ranking else None
        weakest = index_ranking[-1].get("change_percent") if index_ranking else None
        spread = breadth.get("limit_up_down_spread", 0)
        score = 0.0
        if spread > 0:
            score += 1.0
        elif spread < 0:
            score -= 1.0
        if strongest is not None:
            score += strongest / 3.0
        if weakest is not None:
            score += weakest / 3.0

        if spread > 0 and strongest is not None and strongest > 0:
            label, label_zh = "broad_advance", "普涨轮动"
        elif spread < 0 and weakest is not None and weakest < 0:
            label, label_zh = "broad_decline", "普跌走弱"
        else:
            label, label_zh = "mixed_rotation", "混合轮动"

        return {
            "label": label,
            "label_zh": label_zh,
            "score": round(score, 2),
            "positive_ratio": None,
            "negative_ratio": None,
            "outperform_ratio": None,
            "strong_trend_ratio": None,
            "weak_trend_ratio": None,
            "top1_return_contribution": None,
            "top3_return_contribution": None,
            "leader_symbols": [self._value(item, "symbol") for item in index_ranking[:1] if self._value(item, "symbol")],
            "laggard_symbols": [self._value(item, "symbol") for item in index_ranking[-1:] if self._value(item, "symbol")],
            "range_mode": review_mode,
            "applicable": review_mode,
        }

    def _value(self, item, key: str, default=None):
        if isinstance(item, dict):
            return item.get(key, default)
        return getattr(item, key, default)

    def _build_item_cards(self, ranking_items: list[dict], mode: str, trade_date: str) -> list[dict]:
        cards = []
        for item in ranking_items:
            cards.append(
                {
                    "symbol": self._value(item, "symbol"),
                    "name": self._value(item, "name"),
                    "mode": mode,
                    "trade_date": trade_date,
                    "start_date": None,
                    "end_date": None,
                    "close": self._value(item, "price"),
                    "relative_strength": None,
                    "return": self._value(item, "change_percent"),
                    "max_drawdown": None,
                    "volume_ratio": None,
                    "tags": [],
                    "benchmark": None,
                    "stats": {
                        "change": self._value(item, "change"),
                    },
                    "summary": None,
                    "source": self._value(item, "source"),
                }
            )
        return cards

    def _build_rankings(self, leaders: list[dict], laggards: list[dict], index_ranking: list[dict], top_n: int, trade_date: str, review_mode: bool) -> dict:
        items = self._build_item_cards(index_ranking, mode=("trade_date_review" if review_mode else "realtime_brief"), trade_date=trade_date)
        sorted_by_return = sorted(items, key=lambda item: (float("-inf") if item.get("return") is None else item.get("return")), reverse=True)
        sorted_by_return_asc = sorted(items, key=lambda item: (float("inf") if item.get("return") is None else item.get("return")))
        return {
            "leaders_by_return": sorted_by_return[:top_n],
            "laggards_by_return": sorted_by_return_asc[:top_n],
            "leaders_by_relative_strength": [],
            "leaders_by_volume_ratio": [],
            "drawdown_risk": [],
        }

    def _build_buckets(self, pools: dict[str, dict], top_n: int, trade_date: str, review_mode: bool) -> dict:
        def pool_cards(pool_type: str):
            top_items = pools.get(pool_type, {}).get("top_items", [])
            cards = []
            for item in top_items[:top_n]:
                cards.append(
                    {
                        "symbol": self._value(item, "symbol"),
                        "name": self._value(item, "name"),
                        "mode": "trade_date_review" if review_mode else "realtime_brief",
                        "trade_date": trade_date,
                        "start_date": None,
                        "end_date": None,
                        "close": self._value(item, "price"),
                        "relative_strength": None,
                        "return": self._value(item, "change_percent"),
                        "max_drawdown": None,
                        "volume_ratio": None,
                        "tags": [pool_type],
                        "benchmark": None,
                        "stats": {},
                        "summary": None,
                        "source": self._value(item, "source") or pools.get(pool_type, {}).get("source"),
                    }
                )
            return cards

        return {
            "strong_candidates": pool_cards("strong"),
            "weak_candidates": pool_cards("limit_down"),
            "volume_focus": [],
            "risk_alerts": pool_cards("limit_down"),
            "leaders": pool_cards("limit_up"),
            "followers": pool_cards("strong"),
            "draggers": pool_cards("limit_down"),
        }

    def _build_summary(
        self,
        indices,
        pools,
        requested_trade_date: str,
        effective_trade_date: str,
        brief_type: str,
        review_mode: bool,
        adjusted_to_previous_trading_day: bool,
        sentiment: dict,
        highlights: dict,
    ) -> str:
        index_parts = []
        for q in indices[:4]:
            name = getattr(q, "name", None) or getattr(q, "symbol", "指数")
            cp = getattr(q, "change_percent", None)
            if cp is None:
                index_parts.append(f"{name} 涨跌幅未知")
            else:
                index_parts.append(f"{name} {cp:.2f}%")

        pool_part = ""
        if pools:
            up = pools.get("limit_up", {}).get("count", 0)
            down = pools.get("limit_down", {}).get("count", 0)
            strong = pools.get("strong", {}).get("count", 0)
            pool_part = f"；涨停 {up} 家，跌停 {down} 家，强势 {strong} 家"

        index_text = "，".join(index_parts) if index_parts else "指数概览暂不可用"

        strongest = highlights.get("strongest_index") or {}
        weakest = highlights.get("weakest_index") or {}
        strongest_text = strongest.get("name")
        strongest_cp = strongest.get("change_percent")
        weakest_text = weakest.get("name")
        weakest_cp = weakest.get("change_percent")
        extra = ""
        if strongest_text and weakest_text and strongest_cp is not None and weakest_cp is not None:
            extra = f"；最强指数 {strongest_text} {strongest_cp:.2f}%，最弱指数 {weakest_text} {weakest_cp:.2f}%，情绪 {sentiment.get('label_zh')}"
        elif sentiment.get("label_zh"):
            extra = f"；情绪 {sentiment.get('label_zh')}"

        if review_mode and adjusted_to_previous_trading_day:
            prefix = f"{requested_trade_date}（非交易日，按 {effective_trade_date} 复盘，{brief_type}）"
        elif review_mode:
            prefix = f"{effective_trade_date}（复盘，{brief_type}）"
        else:
            prefix = f"{effective_trade_date}（{brief_type}）"

        return f"{prefix}市场简报：{index_text}{pool_part}{extra}。"
