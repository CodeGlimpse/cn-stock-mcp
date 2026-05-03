from openclaw_stock_mcp.app.usecases.sector_lookup import SectorLookupUseCase


class _Provider:
    def __init__(self, should_fail: bool, items=None):
        self.should_fail = should_fail
        self.items = items if items is not None else [{"name": "AI概念"}]

    def get_sector_lookup(self, **kwargs):
        if self.should_fail:
            from openclaw_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "sector failed", retryable=True)
        return self.items


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


def test_sector_lookup_children_can_return_stock_members():
    uc = SectorLookupUseCase()
    router = _Router()
    router.providers = {
        "zhitu": _Provider(
            should_fail=False,
            items=[
                {"symbol": "300122.SZ", "name": "智飞生物", "sec_type": "stock"},
                {"symbol": "600276.SH", "name": "恒瑞医药", "sec_type": "stock"},
            ],
        ),
        "akshare": _Provider(should_fail=False),
    }
    uc.router = router

    req = type("Req", (), {"mode": "children", "sector_type": "primary", "sector_name": "1000医药", "limit": 10, "provider": "zhitu"})()
    result = uc.execute(req)

    assert result["total"] == 2
    assert result["source"] == "zhitu"
    assert result["items"][0]["sec_type"] == "stock"
    assert result["items"][0]["symbol"] == "300122.SZ"
