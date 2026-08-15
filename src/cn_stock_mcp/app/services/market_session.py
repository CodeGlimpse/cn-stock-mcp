from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, time
from typing import Any
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
_OPEN_MORNING = time(9, 30)
_CLOSE_MORNING = time(11, 30)
_OPEN_AFTERNOON = time(13, 0)
_CLOSE_AFTERNOON = time(15, 0)


def _to_shanghai(value: datetime | None) -> datetime:
    current = value or datetime.now(SHANGHAI)
    if current.tzinfo is None:
        current = current.replace(tzinfo=SHANGHAI)
    return current.astimezone(SHANGHAI)


def _session_status(current: datetime, is_trading_day: bool) -> tuple[str, bool]:
    if not is_trading_day:
        return "non_trading_day", False

    current_time = current.timetz().replace(tzinfo=None)
    if current_time < _OPEN_MORNING:
        return "pre_open", False
    if current_time < _CLOSE_MORNING:
        return "morning_session", True
    if current_time < _OPEN_AFTERNOON:
        return "lunch_break", False
    if current_time < _CLOSE_AFTERNOON:
        return "afternoon_session", True
    return "post_close", False


def build_trading_session_context(
    calendar: Mapping[str, Any],
    *,
    now: datetime | None = None,
    target_date: str | None = None,
) -> dict[str, Any]:
    """Build explicit market-session context without claiming live data freshness."""
    current = _to_shanghai(now)
    current_date = current.date().isoformat()
    query_date = str(target_date or calendar.get("date") or current_date)
    target_is_trading_day = bool(calendar.get("is_trading_day"))
    is_current_date = query_date == current_date

    if is_current_date:
        status, is_market_open = _session_status(current, target_is_trading_day)
        is_trading_day: bool | None = target_is_trading_day
    else:
        status = "historical"
        is_market_open = False
        is_trading_day = None

    latest_valid_market_date = (
        query_date if target_is_trading_day else calendar.get("previous_trading_day")
    )

    return {
        "schema": "market_session_context_v1",
        "timezone": "Asia/Shanghai",
        "observed_at": current.isoformat(timespec="seconds"),
        "current_date": current_date,
        "query_date": query_date,
        "is_current_date": is_current_date,
        "is_trading_day": is_trading_day,
        "target_is_trading_day": target_is_trading_day,
        "session_status": status,
        "is_market_open": is_market_open,
        "latest_valid_market_date": latest_valid_market_date,
        "data_may_be_close_data": status in {"pre_open", "post_close", "non_trading_day", "historical"},
        "session_windows": {
            "morning": {"open": "09:30", "close": "11:30"},
            "afternoon": {"open": "13:00", "close": "15:00"},
        },
    }
