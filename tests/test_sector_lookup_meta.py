from openclaw_stock_mcp.app.usecases.sector_lookup import SectorLookupUseCase


class _Provider:
    def __init__(self, should_fail: bool):
        self.should_fail = should_fail

    def get_sector_lookup(self, **kwargs):
        if self.should_fail:
            from openclaw_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "sector failed", retryable=True)
        return [{"name": "AI概念"}]


class _Router:
    def __init__(self):
        self.providers = {
            "zhitu": _Provider(should_fail=True),
            "akshare": _Provider(should_fail=False),
        }

    def choose_provider(self, **kwargs):
        from openclaw_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="zhitu", fallback=["akshare"])

    def get_provider(self, name: str):
        return self.providers[name]


def test_sector_lookup_response_contains_meta():
    uc = SectorLookupUseCase()
    uc.router = _Router()

    req = type("Req", (), {"mode": "list", "sector_type": "concept", "sector_name": None, "limit": 10, "provider": "zhitu"})()
    result = uc.execute(req)

    assert result["total"] == 1
    assert result["source"] == "akshare"
    assert result["meta"]["used_fallback"] is True
