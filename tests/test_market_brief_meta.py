from cn_stock_mcp.app.usecases.market_brief import MarketBriefUseCase
from cn_stock_mcp.app.models.quote import Quote


class _Bar:
    def __init__(self, time, close, prev_close=None, open_=None, high=None, low=None, volume=None, turnover=None):
        self.time = time
        self.close = close
        self.prev_close = prev_close
        self.open = open_ if open_ is not None else close
        self.high = high if high is not None else close
        self.low = low if low is not None else close
        self.volume = volume
        self.turnover = turnover


class _Provider:
    def __init__(self, name: str, should_fail: bool, empty_overview: bool = False):
        self.name = name
        self.should_fail = should_fail
        self.empty_overview = empty_overview

    def get_market_overview(self, market):
        if self.should_fail:
            from cn_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "overview failed", retryable=True)
        if self.empty_overview:
            return {"market": market, "indices": []}
        return {
            "market": market,
            "indices": [
                Quote(
                    symbol="000001.SH",
                    name="上证指数",
                    sec_type="index",
                    exchange="SH",
                    board="index",
                    price=101.0,
                    prev_close=100.0,
                    change=1.0,
                    change_percent=1.0,
                    source=self.name,
                )
            ],
        }

    def get_market_pool(self, pool_type, trade_date):
        if self.should_fail:
            from cn_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "pool failed", retryable=True)
        mapping = {
            "limit_up": [{"symbol": "600000.SH"}] * 3,
            "limit_down": [{"symbol": "600001.SH"}],
            "strong": [{"symbol": "600002.SH"}] * 5,
        }
        return mapping[pool_type]

    def get_trading_calendar(self, market="CN", date=None, **kwargs):
        return {
            "market": market,
            "date": date,
            "is_trading_day": True,
            "previous_trading_day": "2026-04-30",
            "next_trading_day": "2026-05-06",
            "recent_trading_days": ["2026-04-28", "2026-04-29", "2026-04-30"],
            "source": self.name,
        }

    def get_history(self, symbol, sec_type, interval, start=None, end=None, limit=None, adjust=None):
        if self.should_fail:
            from cn_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "history failed", retryable=True)
        close_map = {
            "000001.SH": 101.0,
            "399001.SZ": 99.5,
            "399006.SZ": 103.2,
            "899050.BJ": 98.0,
        }
        close = close_map[symbol]
        return [
            _Bar(time="2026-04-30", close=100.0, prev_close=99.0),
            _Bar(time="2026-05-02", close=close, prev_close=100.0),
        ]


class _Router:
    def __init__(self):
        self.providers = {
            "zhitu": _Provider("zhitu", should_fail=True),
            "akshare": _Provider("akshare", should_fail=False),
        }

    def choose_provider(self, tool_name, **kwargs):
        from cn_stock_mcp.app.services.provider_types import ProviderSelection

        if tool_name in {"market_overview", "stock_history", "market_pool"}:
            return ProviderSelection(primary="zhitu", fallback=["akshare"])
        return ProviderSelection(primary="akshare", fallback=[])

    def get_provider(self, name: str):
        return self.providers[name]


def test_market_brief_response_contains_meta_for_overview_and_pools():
    uc = MarketBriefUseCase()
    uc.router = _Router()

    req = type(
        "Req",
        (),
        {
            "brief_type": "close",
            "market": "CN",
            "trade_date": None,
            "include_pools": True,
            "top_n": 1,
            "provider": "mixed",
        },
    )()

    result = uc.execute(req)

    assert "meta" in result
    assert result["subject_type"] == "market"
    assert result["subject_name"] == "CN"
    assert result["mode"] == "realtime_brief"
    assert result["member_count"] == result["reviewed_count"]
    assert result["meta"]["overview"]["used_fallback"] is True
    assert result["meta"]["overview"]["mode"] == "realtime"
    assert result["meta"]["pools"]["limit_up"]["used_fallback"] is True
    assert result["meta"]["review_envelope_schema"]["schema"] == "review_envelope_v1"
    assert result["meta"]["sentiment_score_schema"]["schema"] == "sentiment_temperature_v1"
    assert result["breadth"]["limit_up_count"] == 3
    assert "stats" in result and "rotation" in result and "continuity" in result and "benchmark_summary" in result
    assert result["sentiment"]["label"] in {"neutral", "warm", "hot", "cool", "cold"}
    assert 0.0 <= result["sentiment"]["normalized_score"] <= 100.0
    assert "leaders" in result
    assert "laggards" in result
    assert result["buckets"]["leaders"][0]["symbol"] == "600000.SH"


def test_market_brief_review_mode_uses_historical_overview_and_builds_ranking():
    uc = MarketBriefUseCase()
    uc.router = _Router()

    req = type(
        "Req",
        (),
        {
            "brief_type": "close",
            "market": "CN",
            "trade_date": "2026-05-02",
            "include_pools": True,
            "top_n": 1,
            "provider": "mixed",
        },
    )()

    result = uc.execute(req)

    assert result["meta"]["review_mode"] is True
    assert result["mode"] == "trade_date_review"
    assert result["meta"]["overview"]["mode"] == "historical"
    assert result["overview"]["source"] == "historical-index-history"
    assert result["trade_date"] == "2026-05-02"
    assert len(result["index_ranking"]) == 4
    assert result["index_ranking"][0]["symbol"] == "399006.SZ"
    assert result["highlights"]["strongest_index"]["symbol"] == "399006.SZ"
    assert result["highlights"]["weakest_index"]["symbol"] == "899050.BJ"
    assert result["sentiment"]["label_zh"]
    assert result["sentiment"]["score_semantics"] == "sentiment_temperature_v1"
    assert result["structure"]["index_count"] == 4


def test_market_brief_rejects_empty_index_overview():
    from cn_stock_mcp.app.services.provider_types import ProviderSelection
    from cn_stock_mcp.providers.errors import ProviderError

    class _EmptyRouter:
        def choose_provider(self, **kwargs):
            return ProviderSelection(primary="akshare", fallback=[])

        def get_provider(self, name):
            return _Provider(name, should_fail=False, empty_overview=True)

    uc = MarketBriefUseCase()
    uc.router = _EmptyRouter()
    req = type(
        "Req",
        (),
        {
            "brief_type": "close",
            "market": "CN",
            "trade_date": None,
            "include_pools": False,
            "top_n": 1,
            "provider": "mixed",
        },
    )()

    try:
        uc.execute(req)
    except ProviderError as exc:
        assert exc.code == "PROVIDER_UNAVAILABLE"
        assert "no index data" in exc.message
    else:
        raise AssertionError("market_brief must reject an empty index overview")


def test_market_brief_without_pools_marks_breadth_unavailable():
    uc = MarketBriefUseCase()
    uc.router = _Router()
    req = type(
        "Req",
        (),
        {"brief_type": "close", "market": "CN", "trade_date": None, "include_pools": False, "top_n": 1, "provider": "mixed"},
    )()

    result = uc.execute(req)

    assert result["breadth"]["limit_up_count"] is None
    assert result["breadth"]["limit_down_count"] is None


def test_market_brief_marks_failed_optional_pool_unknown_not_zero():
    class _PoolFailRouter(_Router):
        def choose_provider(self, tool_name, **kwargs):
            from cn_stock_mcp.app.services.provider_types import ProviderSelection
            if tool_name == "market_overview":
                return ProviderSelection(primary="akshare", fallback=[])
            return ProviderSelection(primary="zhitu", fallback=[])

    uc = MarketBriefUseCase()
    uc.router = _PoolFailRouter()
    req = type(
        "Req",
        (),
        {"brief_type": "close", "market": "CN", "trade_date": None, "include_pools": True, "top_n": 1, "provider": "mixed"},
    )()

    result = uc.execute(req)

    assert result["partial_failure"] is True
    assert result["pools"]["limit_up"]["count"] is None
    assert result["breadth"]["limit_up_count"] is None
