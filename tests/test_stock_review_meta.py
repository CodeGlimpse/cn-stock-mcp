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
        if sec_type == "index":
            return [
                _Bar("2026-04-28", 100, 101, 99, 100.0, 99.0, 1000, 10000),
                _Bar("2026-05-02", 100.2, 100.8, 99.9, 100.5, 100.0, 1200, 12000),
            ]
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
        exchange = "SH"
        board = "main"

    def resolve(self, symbol, sec_type):
        return self._Resolved()


def test_stock_review_trade_date_mode_contains_summary_and_stats():
    uc = StockReviewUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    req = type("Req", (), {"symbol": "600519.SH", "trade_date": "2026-05-02", "start_date": None, "end_date": None, "adjust": "none", "provider": "akshare"})()
    result = uc.execute(req)

    assert result["mode"] == "trade_date_review"
    assert result["stats"]["return_pct_5d"] is not None
    assert result["stats"]["volatility_pct"] is not None
    assert result["stats"]["max_drawdown_pct"] is not None
    assert result["stats"]["relative_strength_pct"] is not None
    assert result["benchmark"]["symbol"] == "000001.SH"
    assert result["summary"]
    assert result["meta"]["history"]["weekly"]["interval"] == "1w"


def test_stock_review_range_mode_contains_return_pct():
    uc = StockReviewUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    req = type("Req", (), {"symbol": "600519.SH", "trade_date": None, "start_date": "2026-04-28", "end_date": "2026-05-02", "adjust": "none", "provider": "akshare"})()
    result = uc.execute(req)

    assert result["mode"] == "range_review"
    assert result["stats"]["return_pct"] is not None
    assert result["stats"]["volatility_pct"] is not None
    assert result["stats"]["max_drawdown_pct"] is not None
    assert result["stats"]["relative_strength_pct"] is not None
    assert result["summary"]


class _CountingProvider:
    def __init__(self):
        self.calls = []

    def get_trading_calendar(self, market="CN", date=None, **kwargs):
        self.calls.append(("calendar", date))
        return {
            "market": market,
            "date": date,
            "is_trading_day": True,
            "previous_trading_day": "2026-04-30",
            "next_trading_day": "2026-05-06",
        }

    def get_history(self, symbol, sec_type, interval, start=None, end=None, limit=None, adjust=None):
        self.calls.append((sec_type, interval, symbol, start, end, limit))
        if sec_type == "index":
            return [
                _Bar("2026-04-28", 100, 101, 99, 100.0, 99.0, 1000, 10000),
                _Bar("2026-05-02", 100.2, 100.8, 99.9, 100.5, 100.0, 1200, 12000),
            ]
        return [
            _Bar("2026-04-01", 9.5, 9.8, 9.4, 9.6, 9.4, 100, 1000),
            _Bar("2026-04-07", 9.7, 10.0, 9.6, 9.9, 9.6, 100, 1000),
            _Bar("2026-04-14", 10.0, 10.2, 9.8, 10.1, 9.9, 100, 1000),
            _Bar("2026-04-21", 10.1, 10.4, 10.0, 10.3, 10.1, 100, 1000),
            _Bar("2026-04-28", 10.3, 10.5, 10.2, 10.4, 10.3, 100, 1000),
            _Bar("2026-04-29", 10.4, 10.6, 10.3, 10.5, 10.4, 100, 1000),
            _Bar("2026-04-30", 10.5, 10.8, 10.4, 10.7, 10.5, 100, 1000),
            _Bar("2026-05-02", 10.8, 11.0, 10.7, 10.9, 10.7, 100, 1000),
        ]


class _CountingRouter:
    def __init__(self):
        self.provider = _CountingProvider()

    def choose_provider(self, **kwargs):
        from openclaw_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="akshare", fallback=[])

    def get_provider(self, name: str):
        return self.provider


def test_stock_review_trade_date_uses_single_stock_history_fetch_and_derives_week_month():
    StockReviewUseCase._shared_calendar_cache = None
    StockReviewUseCase._shared_history_cache = None
    StockReviewUseCase._shared_benchmark_cache = None
    uc = StockReviewUseCase()
    uc.router = _CountingRouter()
    uc.resolver = _Resolver()

    req = type("Req", (), {"symbol": "600519.SH", "trade_date": "2026-05-02", "start_date": None, "end_date": None, "adjust": "none", "provider": "akshare"})()
    result = uc.execute(req)

    stock_calls = [c for c in uc.router.provider.calls if c[0] == "stock"]
    index_calls = [c for c in uc.router.provider.calls if c[0] == "index"]

    assert len(stock_calls) == 1
    assert stock_calls[0][1] == "1d"
    assert len(index_calls) == 1
    assert result["meta"]["history"]["weekly"]["derived_from"] == "1d"
    assert result["meta"]["history"]["monthly"]["derived_from"] == "1d"


def test_stock_review_range_uses_single_stock_history_fetch_and_derives_week_month():
    StockReviewUseCase._shared_calendar_cache = None
    StockReviewUseCase._shared_history_cache = None
    StockReviewUseCase._shared_benchmark_cache = None
    uc = StockReviewUseCase()
    uc.router = _CountingRouter()
    uc.resolver = _Resolver()

    req = type("Req", (), {"symbol": "600519.SH", "trade_date": None, "start_date": "2026-04-01", "end_date": "2026-05-02", "adjust": "none", "provider": "akshare"})()
    result = uc.execute(req)

    stock_calls = [c for c in uc.router.provider.calls if c[0] == "stock"]
    index_calls = [c for c in uc.router.provider.calls if c[0] == "index"]

    assert len(stock_calls) == 1
    assert stock_calls[0][1] == "1d"
    assert len(index_calls) == 1
    assert result["meta"]["history"]["weekly"]["derived_from"] == "1d"
    assert result["meta"]["history"]["monthly"]["derived_from"] == "1d"
