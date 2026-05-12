from __future__ import annotations

from openclaw_stock_mcp.app.models.index_compose import IndexComposeResult
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.providers.adapters.akshare_index_compose_adapters import (
    adapt_index_compose_rows,
    build_index_compose_summary,
    build_index_compose_summary_text,
)


class IndexComposeUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def _normalize_index_code(self, value: str) -> str:
        code = (value or "").strip()
        if "." in code:
            code = code.split(".", 1)[0]
        return code

    def execute(self, request) -> dict:
        index_code = self._normalize_index_code(request.index_code)
        top_n = getattr(request, "top_n", None)
        include_weight = getattr(request, "include_weight", True)
        sort_by = getattr(request, "sort_by", "weight")
        descending = getattr(request, "descending", True)

        ak_provider = self.router.get_provider("akshare")
        lib = ak_provider._require_ak()

        # Prefer weight endpoint for richer output.
        rows = []
        used_fallback_endpoint = False
        try:
            df = ak_provider._call_ak_quietly(lib.index_stock_cons_weight_csindex, symbol=index_code)
            rows = df.to_dict(orient="records")
        except Exception:
            used_fallback_endpoint = True
            df = ak_provider._call_ak_quietly(lib.index_stock_cons_csindex, symbol=index_code)
            rows = df.to_dict(orient="records")

        items = adapt_index_compose_rows(rows, include_weight=include_weight)

        if sort_by == "weight":
            items = sorted(items, key=lambda x: x.weight if x.weight is not None else -1, reverse=descending)
        elif sort_by == "symbol":
            items = sorted(items, key=lambda x: x.symbol, reverse=descending)

        if top_n:
            items = items[:top_n]

        summary = build_index_compose_summary(index_code, items)
        summary_text = build_index_compose_summary_text(summary)

        result = IndexComposeResult(summary=summary, items=items, source="akshare")
        payload = result.model_dump()
        payload["summary_text"] = summary_text
        payload["used_fallback_endpoint"] = used_fallback_endpoint
        if used_fallback_endpoint:
            payload["endpoint_note"] = "weight endpoint unavailable; fell back to constituents-only endpoint (no weight data)"
        return payload
