from cn_stock_mcp.app.usecases.market_pool import MarketPoolUseCase


class _Item:
    def __init__(self, symbol, price=None, turnover=None, market_cap=None, float_market_cap=None):
        self.symbol = symbol
        self.price = price
        self.turnover = turnover
        self.market_cap = market_cap
        self.float_market_cap = float_market_cap
        self.extra = {}


class _Provider:
    def __init__(self, should_fail: bool, name: str):
        self.should_fail = should_fail
        self.name = name
        self.pool_calls = []
        self.calendar_calls = []

    def get_market_pool(self, **kwargs):
        self.pool_calls.append(kwargs)
        if self.should_fail:
            from cn_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "pool failed", retryable=True)
        pool_type = kwargs.get("pool_type")
        if pool_type == "sub_new":
            return [
                _Item("603325.SH", price=84.93, turnover=930814816.0, market_cap=5662283100.0, float_market_cap=1387300295.76),
            ]
        if pool_type == "broken_limit":
            return [
                _Item("002611.SZ", price=5.14, turnover=955617568.0, market_cap=6376778576.0, float_market_cap=5201681387.8),
            ]
        return [
            _Item("600000.SH", price=0, turnover=0, market_cap=0, float_market_cap=0),
            _Item("600519.SH", price=1384.79, turnover=7316111748.0, market_cap=1734131271030.0, float_market_cap=1734131271030.0),
        ]

    def get_trading_calendar(self, market="CN", date=None, recent_limit=5, **kwargs):
        self.calendar_calls.append({"market": market, "date": date, "recent_limit": recent_limit})
        if date == "2026-05-03":
            return {
                "market": market,
                "date": date,
                "is_trading_day": False,
                "previous_trading_day": "2026-04-30",
                "next_trading_day": "2026-05-06",
                "recent_trading_days": ["2026-04-28", "2026-04-29", "2026-04-30"],
                "source": self.name,
            }
        return {
            "market": market,
            "date": date,
            "is_trading_day": True,
            "previous_trading_day": "2026-05-01",
            "next_trading_day": "2026-05-06",
            "recent_trading_days": ["2026-04-29", "2026-04-30", "2026-05-02"],
            "source": self.name,
        }


class _Router:
    def __init__(self):
        self.providers = {
            "zhitu": _Provider(should_fail=True, name="zhitu"),
            "akshare": _Provider(should_fail=False, name="akshare"),
        }

    def choose_provider(self, **kwargs):
        from cn_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="zhitu", fallback=["akshare"])

    def get_provider(self, name: str):
        return self.providers[name]


def test_market_pool_response_contains_meta():
    uc = MarketPoolUseCase()
    uc.router = _Router()

    req = type("Req", (), {"pool_type": "limit_up", "trade_date": "2026-05-02", "limit": 1, "provider": "zhitu"})()
    result = uc.execute(req)

    assert result["count"] == 1
    assert result["trade_date"] == "2026-05-02"
    assert result["source"] == "akshare"
    assert result["meta"]["used_fallback"] is True
    assert result["meta"]["calendar"]["requested_is_trading_day"] is True


def test_market_pool_anomaly_flags_are_added_for_suspect_rows():
    uc = MarketPoolUseCase()
    uc.router = _Router()

    req = type("Req", (), {"pool_type": "limit_down", "trade_date": "2026-05-02", "limit": 2, "provider": "zhitu"})()
    result = uc.execute(req)

    assert result["items"][0].extra["data_quality"] == "suspect"
    assert "zero_price" in result["items"][0].extra["anomaly_flags"]
    assert result["items"][1].extra["data_quality"] == "normal"


def test_market_pool_auto_resolves_effective_trade_date_when_not_provided():
    uc = MarketPoolUseCase()
    uc.router = _Router()
    original_resolver = uc._resolve_effective_trade_date
    uc._resolve_effective_trade_date = lambda requested_trade_date: original_resolver("2026-05-03")

    req = type("Req", (), {"pool_type": "limit_up", "trade_date": None, "limit": 2, "provider": "zhitu"})()
    result = uc.execute(req)

    assert result["requested_trade_date"] == "2026-05-03"
    assert result["trade_date"] == "2026-04-30"
    assert result["meta"]["calendar"]["adjusted_to_previous_trading_day"] is True
    assert uc.router.providers["zhitu"].pool_calls[0]["trade_date"] == "2026-04-30"


def test_market_pool_supports_sub_new_and_broken_limit_types():
    uc = MarketPoolUseCase()
    uc.router = _Router()

    req_sub_new = type("Req", (), {"pool_type": "sub_new", "trade_date": "2026-05-02", "limit": 10, "provider": "zhitu"})()
    req_broken_limit = type("Req", (), {"pool_type": "broken_limit", "trade_date": "2026-05-02", "limit": 10, "provider": "zhitu"})()

    result_sub_new = uc.execute(req_sub_new)
    result_broken_limit = uc.execute(req_broken_limit)

    assert result_sub_new["pool_type"] == "sub_new"
    assert result_sub_new["count"] == 1
    assert result_broken_limit["pool_type"] == "broken_limit"
    assert result_broken_limit["count"] == 1
