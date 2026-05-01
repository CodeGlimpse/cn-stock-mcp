from __future__ import annotations

from datetime import date, datetime


def normalize_exchange(value: str | None) -> str | None:
    if not value:
        return None
    mapping = {
        "sh": "SH",
        "sz": "SZ",
        "bj": "BJ",
        "bk": "BK",
        "SH": "SH",
        "SZ": "SZ",
        "BJ": "BJ",
        "BK": "BK",
    }
    return mapping.get(value, value.upper())


def normalize_symbol(raw: str, exchange: str | None = None) -> str:
    raw = raw.strip()
    if "." in raw:
        left, right = raw.split(".", 1)
        return f"{left.upper()}.{right.upper()}"

    lower = raw.lower()
    if lower.startswith("sh") and len(raw) >= 8:
        return f"{raw[2:].upper()}.SH"
    if lower.startswith("sz") and len(raw) >= 8:
        return f"{raw[2:].upper()}.SZ"
    if lower.startswith("bj") and len(raw) >= 8:
        return f"{raw[2:].upper()}.BJ"

    ex = normalize_exchange(exchange)
    if ex:
        return f"{raw.upper()}.{ex}"

    if raw.isdigit() and len(raw) == 6:
        if raw.startswith(("60", "68")):
            return f"{raw}.SH"
        if raw.startswith(("00", "30")):
            return f"{raw}.SZ"
        if raw.startswith(("43", "83", "87", "92")):
            return f"{raw}.BJ"

    return raw.upper()


def detect_board(symbol: str, sec_type: str) -> str | None:
    if sec_type == "index":
        return "index"
    if sec_type == "fund":
        return "fund"
    if sec_type == "sector":
        return "sector"

    code = symbol.split(".", 1)[0]
    if code.startswith("688"):
        return "star"
    if code.startswith("300"):
        return "chinext"
    if symbol.endswith(".BJ"):
        return "beijing"
    return "main"


def normalize_time_string(raw) -> str | None:
    if raw is None or raw == "":
        return None

    if isinstance(raw, datetime):
        return raw.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    if isinstance(raw, date):
        return raw.strftime("%Y-%m-%d")

    value = str(raw).strip()
    patterns = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y-%m-%d%H:%M:%S",
    ]

    for pattern in patterns:
        try:
            dt = datetime.strptime(value, pattern)
            if pattern == "%Y-%m-%d":
                return dt.strftime("%Y-%m-%d")
            return dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        except ValueError:
            continue

    return value
