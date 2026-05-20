from __future__ import annotations

from cn_stock_mcp.app.models.derivatives_data import DerivativesDataResult
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.providers.adapters.akshare_derivatives_data_adapters import (
    adapt_futures_hist_row,
    adapt_futures_spot_row,
    adapt_option_sse_row,
    adapt_option_szse_row,
    adapt_qvix_row,
    build_derivatives_summary_text,
)


class DerivativesDataUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request) -> dict:
        include = request.include
        futures_symbol = request.futures_symbol
        option_exchange = request.option_exchange
        qvix_underlying = request.qvix_underlying
        history_n = request.history_n
        option_type_filter = request.option_type_filter

        provider = self.router.get_provider("akshare")

        futures_spot = []
        futures_hist = []
        option_list = []
        qvix = []

        if "futures_spot" in include:
            rows = provider.get_futures_spot()
            futures_spot = [adapt_futures_spot_row(r) for r in rows]

        if "futures_hist" in include:
            rows = provider.get_futures_hist(symbol=futures_symbol)
            hist_items = [adapt_futures_hist_row(r) for r in rows]
            futures_hist = hist_items[-history_n:]

        if "option_list" in include:
            if option_exchange in ("SSE", "both"):
                rows = provider.get_option_list_sse()
                option_list.extend(adapt_option_sse_row(r) for r in rows)
            if option_exchange in ("SZSE", "both"):
                rows = provider.get_option_list_szse()
                option_list.extend(adapt_option_szse_row(r) for r in rows)

            # Filter by option type
            if option_type_filter == "call":
                option_list = [o for o in option_list if o.option_type and "购" in o.option_type]
            elif option_type_filter == "put":
                option_list = [o for o in option_list if o.option_type and "沽" in o.option_type]

        if "qvix" in include:
            rows = provider.get_qvix(underlying=qvix_underlying)
            qvix_items = [adapt_qvix_row(r) for r in rows]
            qvix = qvix_items[-history_n:]

        summary = build_derivatives_summary_text(futures_spot, futures_hist, option_list, qvix)

        result = DerivativesDataResult(
            futures_spot=futures_spot,
            futures_spot_count=len(futures_spot),
            futures_hist=futures_hist,
            futures_hist_count=len(futures_hist),
            option_list=option_list,
            option_list_count=len(option_list),
            qvix=qvix,
            qvix_count=len(qvix),
            summary=summary,
        )
        return result.model_dump()
