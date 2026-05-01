from openclaw_stock_mcp.app.services.fallback import run_with_fallback
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter


class SectorLookupUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request):
        selection = self.router.choose_provider(
            tool_name="sector_lookup",
            sec_type="sector",
            preferred=getattr(request, "provider", None),
        )
        items = run_with_fallback(
            self.router,
            selection,
            lambda provider: provider.get_sector_lookup(
                mode=request.mode,
                sector_type=request.sector_type,
                sector_name=request.sector_name,
                limit=request.limit,
            ),
        )
        return {
            "mode": request.mode,
            "sector_type": request.sector_type,
            "sector_name": request.sector_name,
            "items": items,
            "total": len(items),
            "source": selection.primary,
        }
