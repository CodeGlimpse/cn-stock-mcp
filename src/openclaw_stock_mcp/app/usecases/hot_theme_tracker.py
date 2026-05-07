from __future__ import annotations

from types import SimpleNamespace

from openclaw_stock_mcp.app.services.metric_schema import (
    REVIEW_ENVELOPE_SCHEMA,
    SENTIMENT_SCORE_SCHEMA,
)
from openclaw_stock_mcp.app.usecases.market_pool import MarketPoolUseCase
from openclaw_stock_mcp.app.usecases.sector_lookup import SectorLookupUseCase
from openclaw_stock_mcp.app.usecases.sector_rotation_review import SectorRotationReviewUseCase
from openclaw_stock_mcp.providers.errors import ProviderError


class HotThemeTrackerUseCase:
    def __init__(self) -> None:
        self.sector_lookup = SectorLookupUseCase()
        self.sector_rotation = SectorRotationReviewUseCase()
        self.market_pool = MarketPoolUseCase()

    def execute(self, request):
        sector_names = self._resolve_sector_names(request)
        if len(sector_names) < 2:
            raise ProviderError("INVALID_ARGUMENT", "hot_theme_tracker requires at least 2 sector names", retryable=False)

        rot_req = SimpleNamespace(
            sector_names=sector_names,
            sector_type=request.sector_type,
            trade_date=request.trade_date,
            start_date=request.start_date,
            end_date=request.end_date,
            adjust=request.adjust,
            provider=request.provider,
            sort_by=request.sort_by,
            descending=request.descending,
            top_n=max(request.top_n, 3),
            limit=request.member_limit,
            member_top_n=request.member_top_n,
            min_relative_strength=request.min_relative_strength,
            min_return=request.min_return,
            max_drawdown_limit=request.max_drawdown_limit,
            min_volume_ratio=request.min_volume_ratio,
        )
        rotation = self.sector_rotation.execute(rot_req)

        items = list(rotation.get("items", []))
        if not items:
            raise ProviderError("EMPTY_RESULT", "No sector rotation items returned", retryable=False)

        theme_items = [self._to_theme_item(it) for it in items]
        ranked = sorted(theme_items, key=lambda x: x["theme_score"], reverse=True)

        pools = self._build_pool_snapshot(request)
        leaders = ranked[: request.top_n]
        laggards = list(reversed(ranked[-request.top_n:])) if ranked else []

        return {
            "subject_type": "hot_theme_tracker",
            "subject_name": request.watch_name,
            "mode": rotation.get("mode"),
            "trade_date": rotation.get("trade_date"),
            "requested_trade_date": request.trade_date,
            "start_date": rotation.get("start_date"),
            "end_date": rotation.get("end_date"),
            "member_count": len(sector_names),
            "reviewed_count": len(ranked),
            "themes": ranked,
            "leaders": leaders,
            "laggards": laggards,
            "buckets": {
                "mainline_themes": [x for x in ranked if x["theme_label"] in {"hot", "warm"}][: request.top_n],
                "watchlist_themes": [x for x in ranked if x["theme_label"] == "neutral"][: request.top_n],
                "risk_themes": [x for x in ranked if x["theme_label"] in {"cool", "cold"}][: request.top_n],
            },
            "rotation": rotation.get("rotation"),
            "sentiment": rotation.get("sentiment"),
            "pool_snapshot": pools,
            "summary": self._build_summary(ranked, rotation.get("trade_date"), pools),
            "partial_failure": bool(rotation.get("partial_failure", False)),
            "errors": list(rotation.get("errors", [])),
            "meta": {
                "review_envelope_schema": REVIEW_ENVELOPE_SCHEMA,
                "sentiment_score_schema": SENTIMENT_SCORE_SCHEMA,
                "theme_score_schema": {
                    "schema": "theme_score_v1",
                    "score": {
                        "range": [0, 100],
                        "higher_is_stronger": True,
                        "unit": "point",
                    },
                    "components": [
                        "avg_return",
                        "avg_relative_strength",
                        "positive_ratio",
                        "stronger_ratio",
                        "rotation_score",
                        "sentiment_normalized",
                    ],
                },
                "upstream": {
                    "sector_rotation_review": True,
                    "market_pool": request.include_pool_snapshot,
                },
                "source_sector_names": sector_names,
            },
        }

    def _resolve_sector_names(self, request) -> list[str]:
        if request.sector_names:
            return request.sector_names

        lookup_req = SimpleNamespace(mode="list", sector_type=request.sector_type, sector_name=None, limit=request.sector_limit, provider="zhitu")
        data = self.sector_lookup.execute(lookup_req)
        items = data.get("items", [])
        names: list[str] = []
        for it in items:
            name = (it.get("name") or "").strip()
            if name and name not in names:
                names.append(name)
        return names[: request.sector_limit]

    def _to_theme_item(self, item: dict) -> dict:
        avg_return = float(item.get("avg_return") or 0.0)
        avg_rs = float(item.get("avg_relative_strength") or 0.0)
        positive_ratio = float(item.get("positive_ratio") or 0.0)
        stronger_ratio = float(item.get("stronger_ratio") or 0.0)
        rotation_score = float((item.get("rotation") or {}).get("score") or 0.0)
        sentiment_norm = float((item.get("sentiment") or {}).get("normalized_score") or 50.0)

        score = (
            40.0
            + avg_return * 3.0
            + avg_rs * 4.0
            + positive_ratio * 20.0
            + stronger_ratio * 20.0
            + rotation_score * 2.0
            + (sentiment_norm - 50.0) * 0.2
        )
        score = max(0.0, min(100.0, round(score, 2)))

        if score >= 75:
            label = "hot"
        elif score >= 60:
            label = "warm"
        elif score >= 45:
            label = "neutral"
        elif score >= 30:
            label = "cool"
        else:
            label = "cold"

        return {
            "sector_name": item.get("sector_name"),
            "theme_score": score,
            "theme_label": label,
            "avg_return": item.get("avg_return"),
            "avg_relative_strength": item.get("avg_relative_strength"),
            "positive_ratio": item.get("positive_ratio"),
            "stronger_ratio": item.get("stronger_ratio"),
            "rotation": item.get("rotation"),
            "sentiment": item.get("sentiment"),
            "structure_tags": item.get("structure_tags", []),
            "leaders": item.get("leaders", []),
            "laggards": item.get("laggards", []),
            "summary": item.get("summary"),
        }

    def _build_pool_snapshot(self, request) -> dict | None:
        if not request.include_pool_snapshot:
            return None

        result: dict[str, dict] = {}
        for pool_type in ("limit_up", "strong"):
            req = SimpleNamespace(pool_type=pool_type, trade_date=request.trade_date, limit=request.pool_top_n, provider="zhitu")
            pool_result = self.market_pool.execute(req)
            if isinstance(pool_result, dict):
                items = list(pool_result.get("items", []))
                count = int(pool_result.get("count", len(items)) or 0)
            else:
                items = list(pool_result or [])
                count = len(items)
            result[pool_type] = {
                "count": count,
                "top_items": items[: request.pool_top_n],
            }
        return result

    def _build_summary(self, ranked: list[dict], trade_date: str | None, pools: dict | None) -> str:
        top = ranked[0] if ranked else None
        weak = ranked[-1] if ranked else None
        parts = [f"热点跟踪{trade_date or ''}".strip()]
        if top:
            parts.append(f"主线偏向 {top['sector_name']}({top['theme_label']}, {top['theme_score']})")
        if weak:
            parts.append(f"相对偏弱 {weak['sector_name']}({weak['theme_label']}, {weak['theme_score']})")
        if pools:
            parts.append(f"涨停池{pools.get('limit_up', {}).get('count', 0)}，强势池{pools.get('strong', {}).get('count', 0)}")
        return "；".join(parts)
