from __future__ import annotations

from openclaw_stock_mcp.app.models.money_rate import MoneyRateResult
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.providers.adapters.akshare_money_rate_adapters import (
    adapt_interbank_row,
    adapt_repo_row,
    adapt_shibor_row,
    build_money_rate_summary_text,
)


class MoneyRateUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request) -> dict:
        include = request.include
        shibor_days = request.shibor_days
        interbank_indicator = request.interbank_indicator
        interbank_days = request.interbank_days
        repo_mode = request.repo_mode
        start_date = getattr(request, "start_date", None)
        end_date = getattr(request, "end_date", None)

        provider = self.router.get_provider("akshare")

        shibor = []
        interbank = []
        repo = []

        if "shibor" in include:
            rows = provider.get_shibor_all()
            # rows are chronological; take last N days
            if shibor_days and shibor_days < len(rows):
                rows = rows[-shibor_days:]
            shibor = [adapt_shibor_row(r) for r in rows]

        if "interbank" in include:
            rows = provider.get_interbank_rate(indicator=interbank_indicator)
            if interbank_days and interbank_days < len(rows):
                rows = rows[-interbank_days:]
            interbank = [adapt_interbank_row(r) for r in rows]

        if "repo" in include:
            if repo_mode == "latest":
                rows = provider.get_repo_rate_latest()
                repo = [adapt_repo_row(r) for r in rows]
            else:
                # historical — need date range
                eff_start = start_date or "20260101"
                eff_end = end_date or "20261231"
                rows = provider.get_repo_rate_hist(
                    start_date=eff_start, end_date=eff_end
                )
                repo = [adapt_repo_row(r) for r in rows]

        summary = build_money_rate_summary_text(shibor, interbank, repo)

        result = MoneyRateResult(
            shibor=shibor,
            shibor_count=len(shibor),
            interbank=interbank,
            interbank_count=len(interbank),
            repo=repo,
            repo_count=len(repo),
            summary=summary,
        )
        return result.model_dump()
