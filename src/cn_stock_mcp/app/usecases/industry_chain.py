from __future__ import annotations

from cn_stock_mcp.app.models.industry_chain import IndustryChainResult
from cn_stock_mcp.app.services.cache_service import CacheService
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.infra.config import get_settings
from cn_stock_mcp.providers.adapters.akshare_industry_chain_adapters import (
    adapt_concept_row,
    adapt_industry_row,
    build_industry_chain_summary,
)


class IndustryChainUseCase:
    _shared_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        settings = get_settings()
        if IndustryChainUseCase._shared_cache is None:
            IndustryChainUseCase._shared_cache = CacheService(maxsize=8, ttl=300)
        self.cache = IndustryChainUseCase._shared_cache

    def execute(self, request) -> dict:
        include = request.include
        sort_by = request.sort_by
        descending = request.descending
        top_n = request.top_n

        provider = self.router.get_provider("akshare")

        industry = []
        concept = []

        if "industry_list" in include:
            cache_key = "industry:summary"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_industry_summary()
                self.cache.set(cache_key, raw_rows)
            industry = [adapt_industry_row(r) for r in raw_rows]
            industry = self._sort_industry(industry, sort_by, descending)
            if top_n:
                industry = industry[:top_n]

        if "concept_list" in include:
            cache_key = "concept:summary"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_concept_summary()
                self.cache.set(cache_key, raw_rows)
            concept = [adapt_concept_row(r) for r in raw_rows]
            if top_n:
                concept = concept[:top_n]

        summary = build_industry_chain_summary(industry, concept)

        result = IndustryChainResult(
            industry_list=industry,
            industry_count=len(industry),
            concept_list=concept,
            concept_count=len(concept),
            summary=summary,
        )
        return result.model_dump()

    @staticmethod
    def _sort_industry(items: list, key: str, descending: bool = True) -> list:
        key_map = {
            "change_pct": "change_pct",
            "net_inflow": "net_inflow",
            "turnover": "turnover",
            "volume": "volume",
            "up_count": "up_count",
        }
        sort_key = key_map.get(key, "change_pct")

        def _get_val(item):
            v = getattr(item, sort_key, None)
            if v is None:
                return float("-inf") if descending else float("inf")
            return v

        return sorted(items, key=_get_val, reverse=descending)
