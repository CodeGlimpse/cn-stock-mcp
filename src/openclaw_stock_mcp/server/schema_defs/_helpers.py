from __future__ import annotations

from datetime import date as dt_date
from typing import Literal


def validate_date_range(trade_date: str | None, start_date: str | None, end_date: str | None) -> tuple[str | None, str | None, str | None]:
    """Validate trade_date vs start_date/end_date mutual exclusivity and date order.
    Returns (trade_date, start_date, end_date) — may fill trade_date with today if all None.
    Raises ValueError on invalid combinations.
    """
    if trade_date and (start_date or end_date):
        raise ValueError("trade_date cannot be combined with start_date/end_date")

    if start_date or end_date:
        if not start_date or not end_date:
            raise ValueError("start_date and end_date must be provided together")
        start = dt_date.fromisoformat(start_date)
        end = dt_date.fromisoformat(end_date)
        if start > end:
            raise ValueError("start_date must be <= end_date")
        return trade_date, start_date, end_date

    if trade_date:
        dt_date.fromisoformat(trade_date)
        return trade_date, start_date, end_date

    # Default to today
    return dt_date.today().isoformat(), start_date, end_date


def validate_date_order(start_date: str | None, end_date: str | None) -> None:
    """Validate start_date <= end_date if both provided. Raises ValueError."""
    if start_date:
        dt_date.fromisoformat(start_date)
    if end_date:
        dt_date.fromisoformat(end_date)
    if start_date and end_date and dt_date.fromisoformat(start_date) > dt_date.fromisoformat(end_date):
        raise ValueError("start_date must be <= end_date")


def dedupe_include(items: list[str] | None) -> list[str] | None:
    """Deduplicate and strip include-type lists, preserving order."""
    if items is None:
        return None
    seen: set[str] = set()
    normalized: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            normalized.append(item)
    return normalized


INTERVAL_ALIAS: dict[str, str | None] = {
    "5": "5m", "15": "15m", "30": "30m", "60": "60m",
    "d": "1d", "w": "1w", "m": "1M", "y": "1y",
    "5m": "5m", "15m": "15m", "30m": "30m", "60m": "60m",
    "1d": "1d", "1w": "1w", "1m": None, "1y": "1y",
}

POOL_TYPE_ALIAS: dict[str, str] = {
    "limit_up": "limit_up", "ztgc": "limit_up", "up": "limit_up", "涨停": "limit_up",
    "limit_down": "limit_down", "dtgc": "limit_down", "down": "limit_down", "跌停": "limit_down",
    "strong": "strong", "qsgc": "strong", "强势": "strong",
    "sub_new": "sub_new", "cxgc": "sub_new", "次新": "sub_new",
    "broken_limit": "broken_limit", "zbgc": "broken_limit", "炸板": "broken_limit",
}

INDICATOR_ALIAS: dict[str, str] = {
    "macd": "macd", "ma": "ma", "boll": "boll", "kdj": "kdj",
}


def normalize_interval(raw: str) -> str:
    """Normalize interval string. Raises ValueError if unsupported."""
    mapped = INTERVAL_ALIAS.get(raw.strip().lower())
    if mapped is None:
        raise ValueError(
            "interval must be one of: 5/15/30/60/d/w/m/y or 5m/15m/30m/60m/1d/1w/1M/1y; 1m is not supported in current version"
        )
    return mapped


def normalize_pool_type(raw: str) -> str:
    """Normalize pool_type string. Raises ValueError if unknown."""
    mapped = POOL_TYPE_ALIAS.get(raw.strip().lower())
    if not mapped:
        raise ValueError(
            "pool_type must be one of: limit_up/limit_down/strong/sub_new/broken_limit "
            "(aliases: ztgc/dtgc/qsgc/cxgc/zbgc, up/down, 涨停/跌停/强势/次新/炸板)"
        )
    return mapped


def normalize_indicator(raw: str) -> str:
    """Normalize indicator string. Raises ValueError if unknown."""
    mapped = INDICATOR_ALIAS.get(raw.strip().lower())
    if not mapped:
        raise ValueError("indicator must be one of: macd/ma/boll/kdj")
    return mapped


def dedupe_str_list(values: list[str] | None) -> list[str] | None:
    """Deduplicate and strip string lists, preserving order. Returns None if empty."""
    if values is None:
        return None
    seen: set[str] = set()
    normalized: list[str] = []
    for raw in values:
        value = (raw or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized or None
