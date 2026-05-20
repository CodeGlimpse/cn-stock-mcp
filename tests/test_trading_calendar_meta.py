from cn_stock_mcp.app.usecases.trading_calendar import TradingCalendarUseCase


class _Provider:
    def get_trading_calendar(self, **kwargs):
        return {
            "market": "CN",
            "date": "2026-05-01",
            "is_trading_day": False,
            "previous_trading_day": "2026-04-30",
            "next_trading_day": "2026-05-06",
            "recent_trading_days": ["2026-04-28", "2026-04-29", "2026-04-30"],
            "source": "akshare",
        }


class _Router:
    def choose_provider(self, **kwargs):
        from cn_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="akshare", fallback=[])

    def get_provider(self, name: str):
        return _Provider()


def test_trading_calendar_response_contains_meta():
    uc = TradingCalendarUseCase()
    uc.router = _Router()

    req = type(
        "Req",
        (),
        {
            "market": "CN",
            "date": "2026-05-01",
            "start_date": None,
            "end_date": None,
            "recent_limit": 3,
            "provider": "akshare",
        },
    )()

    result = uc.execute(req)

    assert result["is_trading_day"] is False
    assert result["source"] == "akshare"
    assert result["meta"]["used_fallback"] is False
    assert result["meta"]["final_provider"] == "akshare"
