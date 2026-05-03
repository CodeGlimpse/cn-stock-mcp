import pandas as pd

from openclaw_stock_mcp.providers.akshare_provider import AKShareProvider
import openclaw_stock_mcp.providers.akshare_provider as akp


class _FakeAK:
    def stock_zh_a_hist_tx(self, **kwargs):
        return pd.DataFrame(
            [
                {"date": "2026-04-27", "open": 10, "high": 11, "low": 9, "close": 10.5},
                {"date": "2026-04-28", "open": 10.6, "high": 11.2, "low": 10.1, "close": 11.0},
                {"date": "2026-04-29", "open": 11.0, "high": 11.5, "low": 10.8, "close": 11.3},
                {"date": "2026-05-06", "open": 11.4, "high": 12.0, "low": 11.2, "close": 11.9},
                {"date": "2026-05-07", "open": 12.0, "high": 12.3, "low": 11.7, "close": 12.1},
            ]
        )

    def stock_zh_a_daily(self, **kwargs):
        return pd.DataFrame(
            [
                {"date": "2026-04-27", "volume": 100, "amount": 1000},
                {"date": "2026-04-28", "volume": 120, "amount": 1200},
                {"date": "2026-04-29", "volume": 130, "amount": 1300},
                {"date": "2026-05-06", "volume": 140, "amount": 1400},
                {"date": "2026-05-07", "volume": 150, "amount": 1500},
            ]
        )


def test_akshare_stock_history_weekly_aggregation(monkeypatch):
    monkeypatch.setattr(akp, "ak", _FakeAK())
    p = AKShareProvider()
    bars = p.get_history("600519.SH", "stock", "1w", start="2026-04-27", end="2026-05-07", limit=None, adjust="none")

    assert len(bars) == 2
    assert bars[0].time == "2026-04-29"
    assert bars[0].open == 10
    assert bars[0].close == 11.3
    assert bars[0].high == 11.5
    assert bars[0].low == 9
    assert bars[0].volume == 350.0
    assert bars[0].turnover == 3500.0

    assert bars[1].time == "2026-05-07"
    assert bars[1].open == 11.4
    assert bars[1].close == 12.1
    assert bars[1].prev_close == 11.3
