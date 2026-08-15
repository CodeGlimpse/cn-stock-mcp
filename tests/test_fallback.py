import pytest

from cn_stock_mcp.app.services.fallback import run_with_fallback_meta
from cn_stock_mcp.app.services.provider_types import ProviderSelection
from cn_stock_mcp.providers.errors import ProviderError


class _Provider:
    def __init__(self, name, ok=False, retryable=True, code="PROVIDER_UNAVAILABLE", result=None):
        self.name = name
        self.ok = ok
        self.retryable = retryable
        self.code = code
        self.result = result

    def op(self):
        if self.ok:
            return self.result if self.result is not None else {"source": self.name}
        raise ProviderError(self.code, f"{self.name} failed", retryable=self.retryable)


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


def test_run_with_fallback_meta_uses_fallback_on_unsupported_error():
    router = _Router()
    router._map["zhitu"] = _Provider("zhitu", ok=False, retryable=False, code="UNSUPPORTED_MARKET")
    selection = ProviderSelection(primary="zhitu", fallback=["akshare"])

    result, meta = run_with_fallback_meta(router, selection, lambda p: p.op())

    assert result["source"] == "akshare"
    assert meta.used_fallback is True
    assert meta.final_provider == "akshare"
    assert meta.attempted == ["zhitu", "akshare"]


def test_run_with_fallback_meta_uses_fallback_on_empty_result_when_requested():
    router = _Router()
    router._map["zhitu"] = _Provider("zhitu", ok=True, result=[])
    router._map["akshare"] = _Provider("akshare", ok=True, result=[{"source": "akshare"}])
    selection = ProviderSelection(primary="zhitu", fallback=["akshare"])

    result, meta = run_with_fallback_meta(
        router,
        selection,
        lambda p: p.op(),
        should_fallback_result=lambda items: len(items) == 0,
    )

    assert result == [{"source": "akshare"}]
    assert meta.used_fallback is True
    assert meta.final_provider == "akshare"
    assert meta.attempted == ["zhitu", "akshare"]


def test_run_with_fallback_meta_does_not_swallow_unexpected_exceptions():
    router = _Router()

    class _BrokenProvider:
        name = "zhitu"

        def op(self):
            raise ValueError("adapter bug")

    router._map["zhitu"] = _BrokenProvider()
    selection = ProviderSelection(primary="zhitu", fallback=["akshare"])

    with pytest.raises(ValueError, match="adapter bug"):
        run_with_fallback_meta(router, selection, lambda p: p.op())


def test_run_with_fallback_meta_does_not_swallow_result_policy_errors():
    router = _Router()
    router._map["zhitu"] = _Provider("zhitu", ok=True, result=[])
    selection = ProviderSelection(primary="zhitu", fallback=["akshare"])

    def broken_policy(_result):
        raise ValueError("fallback policy bug")

    with pytest.raises(ValueError, match="fallback policy bug"):
        run_with_fallback_meta(
            router,
            selection,
            lambda p: p.op(),
            should_fallback_result=broken_policy,
        )
