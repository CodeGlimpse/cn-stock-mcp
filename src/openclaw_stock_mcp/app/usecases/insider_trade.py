from __future__ import annotations

from openclaw_stock_mcp.app.models.insider_trade import InsiderTradeResult
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver
from openclaw_stock_mcp.providers.adapters.akshare_insider_trade_adapters import (
    adapt_change_row,
    adapt_top10_row,
    build_insider_summary,
)


class InsiderTradeUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()

    def execute(self, request) -> dict:
        include = request.include
        symbol = request.symbol
        sec_type = getattr(request, "sec_type", "stock")
        quarter = request.quarter
        top_n = request.top_n

        provider = self.router.get_provider("akshare")
        resolved = self.resolver.resolve(symbol, sec_type)
        code = resolved.symbol.split(".", 1)[0]

        top10 = []
        change = []
        effective_quarter = quarter

        if quarter == "auto":
            effective_quarter = self._latest_quarter()

        if "top10" in include:
            # AKShare expects symbol in "sh600519" / "sz000001" format
            ak_symbol = self._to_ak_symbol(code, resolved.symbol)
            ak_date = effective_quarter[:4] + effective_quarter[4:]  # YYYYMMDD, e.g. 20250930
            rows = provider.get_insider_top10(symbol=ak_symbol, date=ak_date)
            top10 = [adapt_top10_row(r) for r in rows]
            if top_n:
                top10 = top10[:top_n]

        if "change" in include:
            rows = provider.get_insider_change(symbol=code)
            change = [adapt_change_row(r) for r in rows]
            if top_n:
                change = change[:top_n]

        summary = build_insider_summary(top10, change, resolved.symbol, effective_quarter)

        result = InsiderTradeResult(
            top10=top10,
            top10_count=len(top10),
            change=change,
            change_count=len(change),
            symbol=resolved.symbol,
            quarter=effective_quarter,
            summary=summary,
        )
        return result.model_dump()

    @staticmethod
    def _to_ak_symbol(code: str, full_symbol: str) -> str:
        """Convert to AKShare symbol format: sh600519, sz000001, bj920000."""
        if full_symbol.endswith(".SH"):
            return f"sh{code}"
        if full_symbol.endswith(".SZ"):
            return f"sz{code}"
        if full_symbol.endswith(".BJ"):
            return f"bj{code}"
        return code

    @staticmethod
    def _latest_quarter() -> str:
        """Return the most recent quarter that likely has data."""
        from datetime import date
        today = date.today()
        year = today.year
        month = today.month
        current_q = (month - 1) // 3 + 1
        # Data usually 1 quarter behind
        q = current_q - 1
        y = year
        if q <= 0:
            q += 4
            y -= 1
        # Return YYYYMMDD format (quarter-end date)
        quarter_end_months = {1: "0331", 2: "0630", 3: "0930", 4: "1231"}
        return f"{y}{quarter_end_months[q]}"
