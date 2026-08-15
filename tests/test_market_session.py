from datetime import datetime

from cn_stock_mcp.app.services.market_session import build_trading_session_context


def _calendar(is_trading_day=True):
    return {
        "date": "2026-08-17",
        "is_trading_day": is_trading_day,
        "previous_trading_day": "2026-08-14",
    }


def test_market_session_context_reports_morning_session_and_latest_date():
    context = build_trading_session_context(
        _calendar(),
        now=datetime.fromisoformat("2026-08-17T10:15:00+08:00"),
    )

    assert context["is_trading_day"] is True
    assert context["session_status"] == "morning_session"
    assert context["is_market_open"] is True
    assert context["latest_valid_market_date"] == "2026-08-17"
    assert context["data_may_be_close_data"] is False


def test_market_session_context_reports_non_trading_day_and_close_data_hint():
    context = build_trading_session_context(
        _calendar(False),
        now=datetime.fromisoformat("2026-08-17T14:00:00+08:00"),
    )

    assert context["is_trading_day"] is False
    assert context["session_status"] == "non_trading_day"
    assert context["is_market_open"] is False
    assert context["latest_valid_market_date"] == "2026-08-14"
    assert context["data_may_be_close_data"] is True


def test_market_session_context_marks_explicit_past_date_as_historical():
    context = build_trading_session_context(
        {**_calendar(), "date": "2026-08-14"},
        now=datetime.fromisoformat("2026-08-17T10:15:00+08:00"),
    )

    assert context["is_current_date"] is False
    assert context["is_trading_day"] is None
    assert context["target_is_trading_day"] is True
    assert context["session_status"] == "historical"
