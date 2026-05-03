from openclaw_stock_mcp.app.usecases.stock_review import StockReviewUseCase


class _Bar:
    def __init__(self, time, open_, high, low, close, prev_close=None, volume=None, turnover=None):
        self.time = time
        self.open = open_
        self.high = high
        self.low = low
        self.close = close
        self.prev_close = prev_close
        self.volume = volume
        self.turnover = turnover


class _Provider:
    def get_trading_calendar(self, market="CN", date=None, **kwargs):
        return {
            "market": market,
            "date": date,
            "is_trading_day": True,
            "previous_trading_day": "2026-04-30",
            "next_trading_day": "2026-05-06",
        }

    def get_history(self, symbol, sec_type, interval, start=None, end=None, limit=None, adjust=None):
        if interval == "1d":
            return [
                _Bar("2026-04-28", 10, 10.5, 9.8, 10.0, 9.7, 100, 1000),
                _Bar("2026-04-29", 10.1, 10.6, 10.0, 10.4, 10.0, 120, 1200),
                _Bar("2026-04-30", 10.5, 10.9, 10.3, 10.8, 10.4, 130, 1300),
                _Bar("2026-05-02", 10.9, 11.4, 10.8, 11.2, 10.8, 140, 1400),
            ]
        if interval == "1w":
            return [
                _Bar("2026-04-25", 9.8, 10.6, 9.6, 10.4, 9.5, 500, 5000),
                _Bar("2026-05-02", 10.5, 11.4, 10.3, 11.2, 10.4, 530, 5300),
            ]
        return [
            _Bar("2026-03-31", 9.0, 9.8, 8.9, 9.7, 8.8, 1000, 10000),
            _Bar("2026-04-30", 9.8, 11.4, 9.6, 11.2, 9.7, 1100, 11000),
        ]


class _Router:
    def choose_provider(self, **kwargs):
        from openclaw_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="akshare", fallback=[])

    def get_provider(self, name: str):
        return _Provider()


class _Resolver:
    class _Resolved:
        symbol = "600519.SH"
        sec_type = "stock"

    def resolve(self, symbol, sec_type):
        return self._Resolved()


def test_stock_review_trade_date_mode_contains_summary_and_stats():
    uc = StockReviewUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    req = type("Req", (), {"symbol": "600519.SH", "trade_date": "2026-05-02", "start_date": None, "end_date": None, "adjust": "none", "provider": "akshare"})()
    result = uc.execute(req)

    assert result["mode"] == "trade_date_review"
    assert result["stats"]["return_5d"] is not None
    assert result["summary"]
    assert result["meta"]["history"]["weekly"]["interval"] == "1w"


def test_stock_review_range_mode_contains_period_return():
    uc = StockReviewUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    req = type("Req", (), {"symbol": "600519.SH", "trade_date": None, "start_date": "2026-04-28", "end_date": "2026-05-02", "adjust": "none", "provider": "akshare"})()
    result = uc.execute(req)

    assert result["mode"] == "range_review"
    assert result["stats"]["period_return"] is not None
    assert result["summary"]
