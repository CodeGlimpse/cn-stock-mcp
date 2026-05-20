import pandas as pd

import cn_stock_mcp.providers.akshare_provider as akp
from cn_stock_mcp.providers.akshare_provider import AKShareProvider


class _FakeAK:
    def index_zh_a_hist(self, **kwargs):
        return pd.DataFrame(
            [
                {"日期": "2026-04-29", "开盘": 1000, "收盘": 1010, "最高": 1012, "最低": 998, "成交量": 100, "成交额": 1000},
                {"日期": "2026-04-30", "开盘": 1011, "收盘": 1020, "最高": 1025, "最低": 1008, "成交量": 120, "成交额": 1400},
            ]
        )


def test_akshare_index_history_support(monkeypatch):
    monkeypatch.setattr(akp, "ak", _FakeAK())
    p = AKShareProvider()
    bars = p.get_history("899050.BJ", "index", "1d", start="2026-04-29", end="2026-04-30", limit=2, adjust="none")

    assert len(bars) == 2
    assert bars[0].time == "2026-04-29"
    assert bars[1].time == "2026-04-30"
    assert bars[1].prev_close == 1010
