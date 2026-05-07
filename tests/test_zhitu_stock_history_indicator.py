import pytest

from openclaw_stock_mcp.providers.errors import ProviderError
from openclaw_stock_mcp.providers.zhitu_provider import ZhituProvider


class _Zhitu(ZhituProvider):
    def __init__(self):
        self._instrument_name_cache = {}
        self.calls = []

    def _get_json(self, path: str, params=None):
        self.calls.append((path, params or {}))
        if path == "/hs/history/600519.SH/5/n":
            return [
                {"t": "2026-05-07 09:35:00", "o": 1500.0, "h": 1505.0, "l": 1498.0, "c": 1502.0, "v": 1000.0, "a": 1502000.0, "pc": 1499.0},
                {"t": "2026-05-07 09:40:00", "o": 1502.0, "h": 1508.0, "l": 1501.0, "c": 1507.0, "v": 1200.0, "a": 1808400.0, "pc": 1502.0},
            ]
        if path == "/hs/history/600519.SH/d/f":
            return [
                {"t": "2026-05-06", "o": 1490.0, "h": 1510.0, "l": 1488.0, "c": 1500.0, "v": 20000.0, "a": 30000000.0, "pc": 1480.0},
            ]
        if path == "/hs/history/macd/600519.SH/d/n":
            return [
                {"t": "2026-05-06", "diff": 1.2, "dea": 0.8, "macd": 0.7, "ema12": 1498.0, "ema26": 1490.0},
            ]
        if path == "/hs/history/ma/600519.SH/5/n":
            return [
                {"t": "2026-05-07 09:35:00", "ma3": 1500.0, "ma5": 1499.5},
            ]
        return {"error": "数据不存在"}


def test_zhitu_stock_history_5m_uses_stock_history_route_with_none_adjust():
    p = _Zhitu()

    bars = p.get_history("600519.SH", "stock", "5m", start="2026-05-07", end="2026-05-07", limit=2, adjust="qfq")

    assert len(bars) == 2
    path, params = p.calls[0]
    assert path == "/hs/history/600519.SH/5/n"
    assert params["st"] == "20260507"
    assert params["et"] == "20260507"
    assert params["lt"] == 2


def test_zhitu_stock_history_daily_maps_qfq_to_f():
    p = _Zhitu()

    bars = p.get_history("600519.SH", "stock", "1d", start="2026-05-06", end="2026-05-06", limit=1, adjust="qfq")

    assert len(bars) == 1
    path, params = p.calls[0]
    assert path == "/hs/history/600519.SH/d/f"
    assert params["st"] == "20260506"
    assert params["et"] == "20260506"
    assert params["lt"] == 1


def test_zhitu_stock_indicator_uses_stock_indicator_route():
    p = _Zhitu()

    series = p.get_indicator("600519.SH", "stock", "1d", "macd", start="2026-05-01", end="2026-05-06", limit=10)

    assert series.symbol == "600519.SH"
    assert series.sec_type == "stock"
    assert series.indicator == "macd"
    path, params = p.calls[0]
    assert path == "/hs/history/macd/600519.SH/d/n"
    assert params["st"] == "20260501"
    assert params["et"] == "20260506"
    assert params["lt"] == 10


def test_zhitu_stock_indicator_5m_forces_none_adjust():
    p = _Zhitu()

    series = p.get_indicator("600519.SH", "stock", "5m", "ma", start="2026-05-07", end="2026-05-07", limit=1)

    assert series.indicator == "ma"
    path, params = p.calls[0]
    assert path == "/hs/history/ma/600519.SH/5/n"
    assert params["lt"] == 1


def test_zhitu_stock_history_error_payload_raises_provider_error():
    p = _Zhitu()
    with pytest.raises(ProviderError) as exc:
        p.get_history("000001.SZ", "stock", "1d", start="2026-04-30", end="2026-04-30", adjust="none")

    assert exc.value.code == "PROVIDER_UNAVAILABLE"
    assert exc.value.retryable is True
