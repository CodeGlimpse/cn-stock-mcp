from openclaw_stock_mcp.app.usecases.multi_timeframe_review import MultiTimeframeReviewUseCase


class _Bar:
    def __init__(self, time, close):
        self.time = time
        self.close = close


class _History:
    def execute(self, request):
        mapping = {
            "15m": [10, 10.2, 10.4, 10.6, 10.8, 11.0],
            "1d": [10, 10.4, 10.8, 11.2, 11.5, 11.8],
            "1w": [9.5, 10.0, 10.5, 11.0, 11.3, 11.6],
        }
        closes = mapping[request.interval]
        return {
            "symbol": request.symbol,
            "sec_type": request.sec_type,
            "interval": request.interval,
            "items": [_Bar(f"t{i}", c) for i, c in enumerate(closes)],
            "count": len(closes),
            "source": "akshare" if request.sec_type == "stock" else "zhitu",
            "meta": {"used_fallback": False},
        }


class _Indicator:
    def execute(self, request):
        values_map = {
            ("15m", "macd"): {"dif": 1.2, "dea": 0.8, "macd": 0.4},
            ("1d", "macd"): {"dif": 1.5, "dea": 1.0, "macd": 0.5},
            ("1w", "macd"): {"dif": 1.6, "dea": 1.1, "macd": 0.5},
            ("15m", "kdj"): {"k": 70, "d": 60},
            ("1d", "kdj"): {"k": 75, "d": 68},
            ("1w", "kdj"): {"k": 80, "d": 72},
            ("15m", "ma"): {"ma5": 10.8, "ma10": 10.4},
            ("1d", "ma"): {"ma5": 11.2, "ma10": 10.8},
            ("1w", "ma"): {"ma5": 11.0, "ma10": 10.5},
        }
        values = values_map[(request.interval, request.indicator)]
        return {
            "symbol": request.symbol,
            "indicator": request.indicator,
            "items": [{"time": "t-last", "values": values}],
            "source": "zhitu",
            "meta": {"used_fallback": False},
        }


def test_multi_timeframe_review_builds_alignment_and_items():
    uc = MultiTimeframeReviewUseCase()
    uc.stock_history = _History()
    uc.technical_indicator = _Indicator()

    req = type(
        "Req",
        (),
        {
            "symbol": "600519.SH",
            "intervals": ["15m", "1d", "1w"],
            "indicators": ["macd", "ma", "kdj"],
            "sec_type": "stock",
            "trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "limit": 60,
            "provider": "mixed",
        },
    )()

    result = uc.execute(req)

    assert result["subject_type"] == "multi_timeframe"
    assert result["member_count"] == 3
    assert result["reviewed_count"] == 3
    assert result["items"][0]["interval"] == "15m"
    assert result["items"][1]["interval"] == "1d"
    assert result["items"][0]["trend_label"] in {"bullish", "neutral", "bearish"}
    assert result["breadth"]["bullish_count"] >= 1
    assert result["meta"]["alignment_score_schema"]["schema"] == "multi_timeframe_alignment_v1"
    assert result["meta"]["review_envelope_schema"]["schema"] == "review_envelope_v1"
    assert result["summary"]


def test_multi_timeframe_review_collects_partial_failures():
    uc = MultiTimeframeReviewUseCase()
    uc.stock_history = _History()

    class _IndicatorPartial(_Indicator):
        def execute(self, request):
            if request.interval == "1d" and request.indicator == "macd":
                raise Exception("indicator failed")
            return super().execute(request)

    uc.technical_indicator = _IndicatorPartial()

    req = type(
        "Req",
        (),
        {
            "symbol": "600519.SH",
            "intervals": ["15m", "1d"],
            "indicators": ["macd", "ma"],
            "sec_type": "stock",
            "trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "limit": 60,
            "provider": "mixed",
        },
    )()

    result = uc.execute(req)

    assert result["reviewed_count"] == 2
    assert result["partial_failure"] is True
    assert result["items"][1]["indicator_snapshot"].get("macd") is None
    assert any(e.get("indicator") == "macd" and e.get("interval") == "1d" for e in result["errors"])
