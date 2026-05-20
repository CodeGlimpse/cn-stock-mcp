from __future__ import annotations

from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.app.models.financial import StockFinancialResult
from cn_stock_mcp.providers.adapters.akshare_financial_adapters import build_financial_summary_text


class StockFinancialUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request) -> dict:
        symbol = request.symbol
        include = getattr(request, "include", ["snapshot", "history"])
        statement = getattr(request, "statement", "income")
        report_date = getattr(request, "report_date", None)
        history_n = getattr(request, "history_n", 8)

        provider = self.router.get_provider("akshare")

        snapshot = None
        history = []
        details = []
        detail_statement = None

        if "snapshot" in include or "history" in include:
            raw_rows, snapshot, history = provider.get_financial_abstract(symbol)

            # Filter history to requested count
            if history_n and len(history) > history_n:
                history = history[:history_n]

            # If a specific report_date is requested and differs from snapshot, rebuild
            if report_date and snapshot and snapshot.report_date != report_date:
                from cn_stock_mcp.providers.adapters.akshare_financial_adapters import build_financial_snapshot_from_abstract
                snapshot = build_financial_snapshot_from_abstract(symbol, raw_rows, report_date=report_date)

            if "snapshot" not in include:
                snapshot = None
            if "history" not in include:
                history = []

        if "details" in include:
            details = provider.get_financial_detail(symbol, statement=statement)
            detail_statement = statement

        summary_text = build_financial_summary_text(snapshot, symbol)

        result = StockFinancialResult(
            symbol=symbol,
            snapshot=snapshot,
            history=history,
            details=details,
            detail_statement=detail_statement,
            source="akshare",
        )

        # Convert to dict and add summary
        result_dict = result.model_dump()
        result_dict["summary"] = summary_text
        return result_dict
