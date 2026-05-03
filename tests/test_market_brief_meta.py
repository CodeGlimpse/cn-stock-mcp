from openclaw_stock_mcp.app.usecases.market_brief import MarketBriefUseCase


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
            from openclaw_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "overview failed", retryable=True)
        return {"market": market, "indices": []}

    def get_market_pool(self, pool_type, trade_date):
        if self.should_fail:
            from openclaw_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "pool failed", retryable=True)
        return [{"symbol": "600000.SH"}]

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
            from openclaw_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "history failed", retryable=True)
        return [
            _Bar(time="2026-04-30", close=100.0, prev_close=99.0),
            _Bar(time="2026-05-02", close=101.0, prev_close=100.0),
        ]


class _Router:
    def __init__(self):
        self.providers = {
            "zhitu": _Provider("zhitu", should_fail=True),
            "akshare": _Provider("akshare", should_fail=False),
        }

    def choose_provider(self, tool_name, **kwargs):
        from openclaw_stock_mcp.app.services.provider_types import ProviderSelection

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
    assert result["meta"]["overview"]["used_fallback"] is True
    assert result["meta"]["overview"]["mode"] == "realtime"
    assert result["meta"]["pools"]["limit_up"]["used_fallback"] is True


def test_market_brief_review_mode_uses_historical_overview():
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
    assert result["meta"]["overview"]["mode"] == "historical"
    assert result["overview"]["source"] == "historical-index-history"
    assert result["trade_date"] == "2026-05-02"
