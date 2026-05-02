from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
from openclaw_stock_mcp.app.services.provider_types import ProviderSelection
from openclaw_stock_mcp.providers.errors import ProviderError


class _Provider:
    def __init__(self, name, ok=False, retryable=True):
        self.name = name
        self.ok = ok
        self.retryable = retryable

    def op(self):
        if self.ok:
            return {"source": self.name}
        raise ProviderError("PROVIDER_UNAVAILABLE", f"{self.name} failed", retryable=self.retryable)


class _Router:
    def __init__(self):
        self._map = {
            "zhitu": _Provider("zhitu", ok=False, retryable=True),
            "akshare": _Provider("akshare", ok=True),
        }

    def get_provider(self, name: str):
        return self._map[name]


def test_run_with_fallback_meta_uses_fallback():
    router = _Router()
    selection = ProviderSelection(primary="zhitu", fallback=["akshare"])

    result, meta = run_with_fallback_meta(router, selection, lambda p: p.op())

    assert result["source"] == "akshare"
    assert meta.used_fallback is True
    assert meta.final_provider == "akshare"
    assert meta.attempted == ["zhitu", "akshare"]
