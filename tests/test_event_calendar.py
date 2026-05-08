from openclaw_stock_mcp.app.usecases.event_calendar import EventCalendarUseCase


class _Record:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def model_dump(self):
        return dict(self.__dict__)


class _Profile:
    class _P:
        name = "测试公司"

    def __init__(self):
        self.profile = self._P()
        self.dividends = [_Record(announce_date="2026-05-01", ex_dividend_date="2026-05-10", record_date="2026-05-09", progress="实施")]
        self.unlocks = [_Record(unlock_date="2026-05-10", unlock_amount=100.0, unlock_value=200.0, batch=1, announce_date="2026-05-01")]
        self.quarter_profits = [_Record(period="2026-03-31", revenue=1.0, net_profit=2.0, eps=0.1)]


class _Provider:
    name = "zhitu"

    def get_profile(self, symbol, include=None):
        return _Profile()


class _Router:
    def choose_provider(self, **kwargs):
        from openclaw_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="zhitu", fallback=[])

    def get_provider(self, name):
        return _Provider()


class _Resolver:
    class _Resolved:
        sec_type = "stock"

        def __init__(self, symbol):
            self.symbol = symbol

    def resolve(self, symbol, sec_type):
        return self._Resolved(symbol)


def test_event_calendar_generates_timeline_items():
    uc = EventCalendarUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    req = type(
        "Req",
        (),
        {
            "symbols": ["600519.SH"],
            "event_types": ["dividend", "unlock", "profit"],
            "start_date": "2026-03-01",
            "end_date": "2026-05-31",
            "provider": None,
        },
    )()

    result = uc.execute(req)
    assert result["partial_failure"] is False
    assert result["count"] == 3
    assert {i["event_type"] for i in result["items"]} == {"dividend", "unlock", "profit"}


def test_event_calendar_next_event_only_returns_one_future_item():
    uc = EventCalendarUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    req = type(
        "Req",
        (),
        {
            "symbols": ["600519.SH"],
            "event_types": ["dividend", "unlock", "profit"],
            "start_date": None,
            "end_date": None,
            "next_event_only": True,
            "provider": None,
        },
    )()

    result = uc.execute(req)
    assert result["partial_failure"] is False
    assert result["count"] == 1
    assert result["meta"]["next_event_only"] is True
    assert result["items"][0]["event_type"] == "unlock"


def test_event_calendar_next_event_priority():
    uc = EventCalendarUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    req = type(
        "Req",
        (),
        {
            "symbols": ["600519.SH"],
            "event_types": ["dividend", "unlock", "profit"],
            "start_date": None,
            "end_date": None,
            "next_event_only": True,
            "event_priority": ["dividend", "unlock", "profit"],
            "provider": None,
        },
    )()

    result = uc.execute(req)
    assert result["count"] == 1
    assert result["items"][0]["event_date"] == "2026-05-10"
    assert result["items"][0]["event_type"] == "dividend"
