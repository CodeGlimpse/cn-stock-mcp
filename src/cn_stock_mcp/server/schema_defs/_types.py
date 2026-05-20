from __future__ import annotations

from typing import Literal

SecType = Literal["stock", "index", "fund", "sector"]
ProviderName = Literal["akshare", "zhitu", "mixed"]
Interval = Literal["5m", "15m", "30m", "60m", "1d", "1w", "1M", "1y"]
AdjustType = Literal["none", "qfq", "hfq"]
IndicatorType = Literal["macd", "ma", "boll", "kdj"]
PoolType = Literal["limit_up", "limit_down", "strong", "sub_new", "broken_limit"]
SectorLookupMode = Literal["list", "members", "children"]
SectorType = Literal["concept", "primary"]

__all__ = [
    "SecType", "ProviderName", "Interval", "AdjustType",
    "IndicatorType", "PoolType", "SectorLookupMode", "SectorType",
]
