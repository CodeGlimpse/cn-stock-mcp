from __future__ import annotations

import json
import time

from cn_stock_mcp.app.services.cache_service import CacheService
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.app.models.capital_flow import CapitalFlowRecord, MarketFundFlowSummary, SectorFundFlowItem
from cn_stock_mcp.infra.config import get_settings
from cn_stock_mcp.providers.errors import ProviderError


class CapitalFlowUseCase:
    _shared_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        settings = get_settings()
        self.cache_ttl_seconds = max(int(settings.cache_ttl_capital_flow_seconds or 300), 10)
        self.stale_max_age_seconds = max(int(settings.capital_flow_stale_max_age_seconds or 86400), self.cache_ttl_seconds)
        if CapitalFlowUseCase._shared_cache is None:
            CapitalFlowUseCase._shared_cache = CacheService(
                maxsize=512,
                ttl=self.stale_max_age_seconds,
            )
        self.cache = CapitalFlowUseCase._shared_cache

    def _cache_key(self, request) -> str:
        values = {
            "flow_type": request.flow_type,
            "symbol": getattr(request, "symbol", None),
            "start_date": getattr(request, "start_date", None),
            "end_date": getattr(request, "end_date", None),
            "limit": getattr(request, "limit", 60),
            "sort_by": getattr(request, "sort_by", "net_amount"),
            "descending": getattr(request, "descending", True),
            "top_n": getattr(request, "top_n", None),
        }
        return f"capital_flow:{json.dumps(values, ensure_ascii=False, sort_keys=True)}"

    @staticmethod
    def _with_cache_meta(payload: dict, age_seconds: int, stale: bool) -> dict:
        result = {**payload}
        meta = dict(payload.get("meta") or {})
        meta.update(
            {
                "provider_used": "cache",
                "cache_hit": True,
                "stale": stale,
                "stale_age_seconds": age_seconds if stale else None,
            }
        )
        result["meta"] = meta
        return result

    def _filter_records_by_date(
        self,
        records: list[CapitalFlowRecord],
        start_date: str | None,
        end_date: str | None,
    ) -> list[CapitalFlowRecord]:
        if not start_date and not end_date:
            return records
        filtered = records
        if start_date:
            filtered = [r for r in filtered if r.date >= start_date]
        if end_date:
            filtered = [r for r in filtered if r.date <= end_date]
        return filtered

    def _sort_sector_items(
        self,
        items: list[SectorFundFlowItem],
        sort_by: str,
        descending: bool,
        top_n: int | None,
    ) -> list[SectorFundFlowItem]:
        key_map = {
            "net_amount": lambda x: x.net_amount or 0.0,
            "inflow": lambda x: x.inflow or 0.0,
            "outflow": lambda x: x.outflow or 0.0,
            "sector_change_percent": lambda x: x.sector_change_percent or 0.0,
            "company_count": lambda x: x.company_count or 0,
        }
        key_fn = key_map.get(sort_by, key_map["net_amount"])
        items_sorted = sorted(items, key=key_fn, reverse=descending)
        if top_n:
            items_sorted = items_sorted[:top_n]
        return items_sorted

    def _build_sector_summary(self, items: list[SectorFundFlowItem]) -> str:
        if not items:
            return "无板块资金流向数据"
        inflow_sectors = [it for it in items if it.net_amount is not None and it.net_amount > 0]
        outflow_sectors = [it for it in items if it.net_amount is not None and it.net_amount < 0]
        parts = []
        if inflow_sectors:
            top3 = ", ".join(f"{s.sector_name}({s.net_amount:.1f}亿)" for s in inflow_sectors[:3])
            parts.append(f"主力净流入前三: {top3}")
        if outflow_sectors:
            bot3 = ", ".join(f"{s.sector_name}({s.net_amount:.1f}亿)" for s in outflow_sectors[-3:])
            parts.append(f"主力净流出前三: {bot3}")
        return "; ".join(parts) if parts else "板块资金流向数据暂无显著方向"

    def _build_flow_summary_text(
        self,
        flow_type: str,
        symbol: str | None,
        records: list[CapitalFlowRecord] | None,
        summary: MarketFundFlowSummary | None,
        sector_items: list[SectorFundFlowItem] | None,
    ) -> str:
        def amount_text(value: float | None) -> str:
            return f"{value / 1e8:.2f}亿" if value is not None else "N/A"

        if flow_type == "market":
            if not summary or not records:
                return "大盘资金流向数据暂无"
            latest = records[-1]
            direction = summary.main_inflow_direction or "neutral"
            direction_cn = {"inflow": "净流入", "outflow": "净流出", "neutral": "中性"}.get(direction, "中性")
            main_val = latest.main_net_inflow
            main_pct = latest.main_net_inflow_pct
            main_str = amount_text(main_val)
            pct_str = f"{main_pct:.2f}%" if main_pct is not None else "N/A"
            return f"大盘资金{direction_cn}，主力净流入{main_str}（占比{pct_str}），超大单{amount_text(latest.super_large_net_inflow)}，大单{amount_text(latest.large_net_inflow)}"

        if flow_type in ("industry", "concept"):
            if not sector_items:
                return f"{'行业' if flow_type == 'industry' else '概念'}板块资金流向数据暂无"
            return self._build_sector_summary(sector_items)

        if flow_type == "individual":
            if not records:
                return f"{symbol or '个股'}资金流向数据暂无"
            latest = records[-1]
            direction = "净流入" if (latest.main_net_inflow or 0) > 0 else "净流出"
            main_val = latest.main_net_inflow
            main_str = amount_text(main_val)
            pct_str = f"{latest.main_net_inflow_pct:.2f}%" if latest.main_net_inflow_pct is not None else "N/A"
            return f"{symbol or '个股'}主力{direction}{main_str}（占比{pct_str}），超大单{amount_text(latest.super_large_net_inflow)}"

        return "资金流向数据暂无"

    def execute(self, request) -> dict:
        cache_key = self._cache_key(request)
        cache_entry = self.cache.get(cache_key)
        now = time.time()
        if isinstance(cache_entry, dict) and isinstance(cache_entry.get("payload"), dict):
            age_seconds = max(0, int(now - float(cache_entry.get("stored_at", now))))
            if age_seconds <= self.cache_ttl_seconds:
                return self._with_cache_meta(cache_entry["payload"], age_seconds, stale=False)

        flow_type = request.flow_type
        symbol = getattr(request, "symbol", None)
        start_date = getattr(request, "start_date", None)
        end_date = getattr(request, "end_date", None)
        limit = getattr(request, "limit", 60)
        sort_by = getattr(request, "sort_by", "net_amount")
        descending = getattr(request, "descending", True)
        top_n = getattr(request, "top_n", None)

        try:
            provider = self.router.get_provider("akshare")
        except ProviderError:
            raise

        records: list[CapitalFlowRecord] | None = None
        summary: MarketFundFlowSummary | None = None
        sector_items: list[SectorFundFlowItem] | None = None

        started_at = time.perf_counter()
        try:
            if flow_type == "market":
                records, summary = provider.get_market_capital_flow(limit=limit)
                records = self._filter_records_by_date(records, start_date, end_date)
                summary_records = records
                from cn_stock_mcp.providers.adapters.akshare_capital_flow_adapters import build_market_fund_flow_summary
                summary = build_market_fund_flow_summary(summary_records)

            elif flow_type == "individual":
                if not symbol:
                    raise ValueError("symbol is required when flow_type=individual")
                records = provider.get_individual_capital_flow(symbol=symbol, limit=limit)
                records = self._filter_records_by_date(records, start_date, end_date)

            elif flow_type in ("industry", "concept"):
                sector_items = provider.get_sector_capital_flow(flow_type=flow_type)
                sector_items = self._sort_sector_items(sector_items, sort_by, descending, top_n)

            else:
                raise ValueError(f"Unsupported flow_type: {flow_type}")
        except ProviderError as exc:
            if not exc.retryable or not getattr(request, "allow_stale", False):
                raise
            if isinstance(cache_entry, dict) and isinstance(cache_entry.get("payload"), dict):
                age_seconds = max(0, int(now - float(cache_entry.get("stored_at", now))))
                if age_seconds <= self.stale_max_age_seconds:
                    return self._with_cache_meta(cache_entry["payload"], age_seconds, stale=True)
            raise

        summary_text = self._build_flow_summary_text(flow_type, symbol, records, summary, sector_items)

        result: dict = {
            "flow_type": flow_type,
            "source": "akshare",
            "summary": summary_text,
        }

        if flow_type in ("market", "individual"):
            result["records"] = records
            result["count"] = len(records)
            if summary is not None:
                result["market_summary"] = summary

        if flow_type in ("industry", "concept"):
            result["items"] = sector_items
            result["count"] = len(sector_items or [])

        if symbol:
            result["symbol"] = symbol

        if start_date or end_date:
            result["date_range"] = {"start_date": start_date, "end_date": end_date}

        provider_meta = getattr(provider, "last_capital_flow_meta", {})
        if not isinstance(provider_meta, dict):
            provider_meta = {}
        result["meta"] = {
            "provider_used": getattr(provider, "name", None) or "akshare",
            "fallback_chain": [getattr(provider, "name", None) or "akshare"],
            "latency_ms": int((time.perf_counter() - started_at) * 1000),
            "cache_hit": False,
            "stale": False,
            **provider_meta,
        }
        self.cache.set(
            cache_key,
            {
                "payload": result,
                "stored_at": time.time(),
            },
        )

        return result
