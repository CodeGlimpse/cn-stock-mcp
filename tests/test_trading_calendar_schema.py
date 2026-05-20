from cn_stock_mcp.server.schemas import TradingCalendarRequest


def test_trading_calendar_request_defaults_date_when_empty():
    req = TradingCalendarRequest()
    assert req.market == "CN"
    assert req.date is not None
    assert req.start_date is None
    assert req.end_date is None


def test_trading_calendar_request_rejects_mixed_date_and_range():
    try:
        TradingCalendarRequest(date="2026-05-01", start_date="2026-05-01", end_date="2026-05-10")
        assert False, "expected validation error"
    except Exception as exc:
        assert "date cannot be combined" in str(exc)
