from types import SimpleNamespace

from openclaw_stock_mcp.app.usecases.multi_timeframe_review import MultiTimeframeReviewUseCase
from openclaw_stock_mcp.providers.errors import ProviderError


class _Bar:
    def __init__(self, close):
        self.close = close


class _History:
    def execute(self, req):
        data = {
            "5m": [100, 102, 104],
            "15m": [100, 101, 102],
            "1d": [100, 98, 96],
            "1w": [100, 103, 106],
        }
        seq = data.get(req.interval)
        if seq is None:
            raise ProviderError("EMPTY_RESULT", "no bars", retryable=False)
        return {
            "items": [_Bar(x) for x in seq],
            "source": "akshare",
            "meta": {"interval": req.interval},
        }


class _Indicator:
    def execute(self, req):
        if req.indicator == "macd":
            if req.interval in {"5m", "15m", "1w"}:
                values = {"dif": 1.0, "dea": 0.5, "macd": 0.2}
            else:
                values = {"dif": -1.0, "dea": -0.5, "macd": -0.2}
            return {"items": [{"time": "t", "values": values}], "source": "akshare", "meta": {}}

        if req.indicator == "kdj":
            if req.interval in {"5m", "15m", "1w"}:
                values = {"k": 60, "d": 40}
            else:
                values = {"k": 30, "d": 50}
            return {"items": [{"time": "t", "values": values}], "source": "akshare", "meta": {}}

        if req.indicator == "ma":
            return {"items": [{"time": "t", "values": {"ma5": 101, "ma10": 99}}], "source": "akshare", "meta": {}}

        raise ProviderError("UNSUPPORTED", "indicator unsupported", retryable=False)


def _req(**overrides):
    base = dict(
        symbol="600519.SH",
        sec_type="stock",
        intervals=["15m", "1d", "1w"],
        indicators=["macd", "kdj", "ma"],
        trade_date="2026-05-06",
        start_date=None,
        end_date=None,
        limit=50,
        provider="mixed",
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _build_usecase() -> MultiTimeframeReviewUseCase:
    uc = MultiTimeframeReviewUseCase()
    uc.stock_history = _History()
    uc.technical_indicator = _Indicator()
    return uc


def test_multi_timeframe_review_happy_path():
    result = _build_usecase().execute(_req())

    assert result["subject_type"] == "multi_timeframe"
    assert result["member_count"] == 3
    assert result["reviewed_count"] == 3
    assert result["partial_failure"] is False
    assert result["meta"]["alignment_score_schema"]["schema"] == "multi_timeframe_alignment_v1"
    assert result["meta"]["review_envelope_schema"]["schema"] == "review_envelope_v1"
    assert result["items"][0]["interval"] in {"15m", "1w"}


def test_multi_timeframe_review_partial_failure_on_indicator_error():
    class _IndicatorWithError(_Indicator):
        def execute(self, req):
            if req.indicator == "ma" and req.interval == "1d":
                raise ProviderError("PROVIDER_UNAVAILABLE", "ma fail", retryable=True)
            return super().execute(req)

    uc = _build_usecase()
    uc.technical_indicator = _IndicatorWithError()

    result = uc.execute(_req())
    assert result["partial_failure"] is True
    assert any(e.get("indicator") == "ma" and e.get("interval") == "1d" for e in result["errors"])


def test_multi_timeframe_review_raises_when_no_cards():
    class _BadHistory:
        def execute(self, req):
            raise ProviderError("EMPTY_RESULT", "no bars", retryable=False)

    uc = _build_usecase()
    uc.stock_history = _BadHistory()

    try:
        uc.execute(_req(intervals=["15m", "1d"]))
        assert False, "expected ProviderError"
    except ProviderError as exc:
        assert exc.code == "EMPTY_RESULT"
