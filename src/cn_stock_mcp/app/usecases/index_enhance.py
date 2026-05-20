from __future__ import annotations

from cn_stock_mcp.app.models.index_enhance import IndexEnhanceResult
from cn_stock_mcp.app.usecases.index_compose import IndexComposeUseCase
from cn_stock_mcp.app.usecases.stock_history import StockHistoryUseCase
from cn_stock_mcp.app.services.cache_service import CacheService
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.providers.adapters.index_enhance_adapters import (
    build_enhance_members,
    build_index_enhance_summary,
    build_index_enhance_summary_text,
    build_industry_exposure,
    build_weight_exposure,
    calc_enhanced_return,
    calc_index_return,
    normalize_index_code,
    normalize_stock_symbol,
)
from cn_stock_mcp.app.services.fallback import run_with_fallback


class _HistoryRequest:
    def __init__(self, symbol: str, sec_type: str, interval: str, start_date, end_date, limit: int, adjust):
        self.symbol = symbol
        self.sec_type = sec_type
        self.interval = interval
        self.start_date = start_date
        self.end_date = end_date
        self.limit = limit
        self.adjust = adjust
        self.provider = None


class _ComposeRequest:
    def __init__(self, index_code: str, top_n: int, include_weight: bool, sort_by: str, descending: bool):
        self.index_code = index_code
        self.top_n = top_n
        self.include_weight = include_weight
        self.sort_by = sort_by
        self.descending = descending


class IndexEnhanceUseCase:
    _profile_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.index_compose = IndexComposeUseCase()
        self.stock_history = StockHistoryUseCase()
        if IndexEnhanceUseCase._profile_cache is None:
            IndexEnhanceUseCase._profile_cache = CacheService(maxsize=512, ttl=1800)
        self.profile_cache = IndexEnhanceUseCase._profile_cache

    def execute(self, request) -> dict:
        index_code = normalize_index_code(request.index_code)
        limit = request.top_n
        weighting = request.weighting

        compose = self.index_compose.execute(_ComposeRequest(
            index_code=index_code,
            top_n=limit,
            include_weight=True,
            sort_by="weight",
            descending=True,
        ))
        constituents = compose.get("items", [])

        index_symbol = self._index_symbol(index_code)
        history = self.stock_history.execute(_HistoryRequest(
            symbol=index_symbol,
            sec_type="index",
            interval="1d",
            start_date=request.start_date,
            end_date=request.end_date,
            limit=1,
            adjust=None,
        ))
        benchmark_return = calc_index_return(history.get("items", []))

        symbols = [normalize_stock_symbol(self._field(c, "symbol"), self._field(c, "exchange")) for c in constituents]
        quotes = self._get_quotes(symbols)
        industries = self._get_industries(symbols)
        members = build_enhance_members(constituents, quotes, benchmark_return, industries=industries)
        enhanced_return, total_weight = calc_enhanced_return(members, weighting)
        if weighting == "equal":
            total_weight = None

        summary_obj = compose.get("summary")
        index_name = summary_obj.get("index_name") if isinstance(summary_obj, dict) else None
        summary = build_index_enhance_summary(
            index_code=index_code,
            index_name=index_name,
            benchmark_return=benchmark_return,
            enhanced_return=enhanced_return,
            members=members,
            total_weight=total_weight,
            weighting=weighting,
        )
        weight_exposure = build_weight_exposure(members)
        industry_exposure, industry_coverage = build_industry_exposure(members)
        summary_text = build_index_enhance_summary_text(summary)

        result = IndexEnhanceResult(
            summary=summary,
            members=members,
            weight_exposure=weight_exposure,
            industry_exposure=industry_exposure,
            industry_coverage=industry_coverage,
            summary_text=summary_text,
        )
        payload = result.model_dump()
        payload["compose_used_fallback_endpoint"] = compose.get("used_fallback_endpoint", False)
        return payload

    def _get_quotes(self, symbols: list[str]) -> dict[str, object]:
        if not symbols:
            return {}
        results: dict[str, object] = {}
        for symbol in symbols:
            selection = self.router.choose_provider(tool_name="stock_quote", symbol=symbol, sec_type="stock")
            for provider_name in [selection.primary, *selection.fallback]:
                provider = self.router.get_provider(provider_name)
                try:
                    quote = provider.get_quote(symbol, "stock")
                    results[quote.symbol] = quote
                    break
                except Exception:
                    continue
        return results

    def _get_industries(self, symbols: list[str]) -> dict[str, str | None]:
        if not symbols:
            return {}
        out: dict[str, str | None] = {}
        for symbol in symbols:
            cached = self.profile_cache.get(f"index_enhance:industry:{symbol}")
            if cached is not None:
                out[symbol] = cached
                continue
            selection = self.router.choose_provider(tool_name="stock_profile", symbol=symbol, sec_type="stock")
            try:
                detail = run_with_fallback(
                    self.router,
                    selection,
                    lambda provider: provider.get_profile(symbol, include=["profile"]),
                )
                industry = getattr(getattr(detail, "profile", None), "industry", None)
            except Exception:
                industry = None
            self.profile_cache.set(f"index_enhance:industry:{symbol}", industry)
            out[symbol] = industry
        return out

    @staticmethod
    def _field(item, name: str):
        if isinstance(item, dict):
            return item.get(name)
        return getattr(item, name, None)

    @staticmethod
    def _index_symbol(index_code: str) -> str:
        if index_code.startswith(("399", "159")):
            return f"{index_code}.SZ"
        if index_code.startswith("899"):
            return f"{index_code}.BJ"
        return f"{index_code}.SH"
