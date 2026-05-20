from cn_stock_mcp.app.usecases.market_brief import MarketBriefUseCase


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
    def __init__(self, name: str, should_fail: bool):
        self.name = name
        self.should_fail = should_fail

    def get_market_overview(self, market):
        if self.should_fail:
            from cn_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "overview failed", retryable=True)
        return {"market": market, "indices": []}

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
