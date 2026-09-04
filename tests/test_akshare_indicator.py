from cn_stock_mcp.app.models.bar import Bar
from cn_stock_mcp.providers.akshare_provider import AKShareProvider


def _bars(count: int = 80) -> list[Bar]:
    return [
        Bar(
            time=f"2026-01-{(index % 28) + 1:02d}",
            open=100.0 + index,
            high=102.0 + index,
            low=99.0 + index,
            close=101.0 + index,
            volume=1000.0 + index,
        )
        for index in range(count)
    ]


def test_akshare_derived_indicator_supports_all_public_types(monkeypatch):
    provider = AKShareProvider()
    monkeypatch.setattr(provider, "get_history", lambda **kwargs: _bars())

    for indicator in ("ma", "macd", "boll", "kdj"):
        series = provider.get_indicator(
            "510050.SH", "fund", "1d", indicator, limit=5
        )
        assert series.source == "akshare_derived"
        assert series.sec_type == "fund"
        assert len(series.items) == 5
        assert series.items[-1].values


def test_akshare_derived_ma_has_expected_latest_average(monkeypatch):
    provider = AKShareProvider()
    bars = _bars()
    monkeypatch.setattr(provider, "get_history", lambda **kwargs: bars)

    series = provider.get_indicator("600519.SH", "stock", "1d", "ma", limit=1)

    expected = sum(float(bar.close) for bar in bars[-5:]) / 5
    assert series.items[-1].values["ma5"] == expected
