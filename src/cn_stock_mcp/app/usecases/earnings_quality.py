from __future__ import annotations

from cn_stock_mcp.app.models.earnings_quality import EarningsQualityResult
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.providers.adapters.earnings_quality_adapters import (
    build_metrics,
    score_earnings_quality,
    build_summary_text,
)


class EarningsQualityUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request) -> dict:
        symbol = request.symbol

        provider = self.router.get_provider("akshare")
        # Reuse financial abstract API
        _, snapshot, _ = provider.get_financial_abstract(symbol)

        metrics = build_metrics(snapshot, symbol)
        score, label, tags, diagnostics = score_earnings_quality(metrics)

        result = EarningsQualityResult(
            symbol=symbol,
            report_date=metrics.report_date,
            quarter_name=metrics.quarter_name,
            score=score,
            label=label,
            diagnostics=diagnostics,
            reason_tags=tags,
            metrics=metrics,
            source="akshare",
        )
        result.summary = build_summary_text(result)
        return result.model_dump()
