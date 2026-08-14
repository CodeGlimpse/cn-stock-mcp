from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import BaseModel


_REALTIME_FIELDS = {"timestamp", "tick_time"}
_DATE_FIELDS = {"as_of", "as_of_date", "trade_date", "report_date"}
_SERIES_CONTAINERS = {
    "bars",
    "data",
    "history",
    "indices",
    "items",
    "latest",
    "points",
    "quotes",
    "records",
    "series",
    "snapshot",
}
_EVENT_CONTAINERS = {"dividends", "unlocks"}
_SHANGHAI = ZoneInfo("Asia/Shanghai")


@dataclass(frozen=True)
class _FreshnessCandidate:
    parsed: datetime
    kind: str


def _as_mapping(value: Any) -> Mapping[str, Any] | None:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="python")
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value if isinstance(value, Mapping) else None


def _parse_datetime(value: Any) -> tuple[datetime, bool] | None:
    if isinstance(value, datetime):
        parsed = value if value.tzinfo else value.replace(tzinfo=_SHANGHAI)
        return parsed.astimezone(timezone.utc), False
    if isinstance(value, date):
        parsed = datetime(value.year, value.month, value.day, tzinfo=_SHANGHAI)
        return parsed.astimezone(timezone.utc), True
    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None
    if len(text) == 8 and text.isdigit():
        text = f"{text[:4]}-{text[4:6]}-{text[6:]}"
    text = text.replace("/", "-")
    try:
        if len(text) == 10:
            parsed_date = date.fromisoformat(text)
            parsed = datetime.combine(parsed_date, datetime.min.time(), tzinfo=_SHANGHAI)
            return parsed.astimezone(timezone.utc), True
        normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=_SHANGHAI)
    return parsed.astimezone(timezone.utc), False


def _field_kind(key: str, path: tuple[str, ...]) -> tuple[str, str] | None:
    normalized = key.lower()
    if normalized in _REALTIME_FIELDS:
        return normalized, "timestamp"
    if normalized in _DATE_FIELDS:
        return normalized, "date"
    if normalized == "date" and (
        not path
        or any(part in _SERIES_CONTAINERS for part in path)
    ) and not any(part in _EVENT_CONTAINERS for part in path):
        return normalized, "date"
    if normalized == "time" and any(part in _SERIES_CONTAINERS for part in path):
        return normalized, "timestamp"
    return None


def _collect_candidates(value: Any, path: tuple[str, ...] = ()) -> list[_FreshnessCandidate]:
    mapping = _as_mapping(value)
    if mapping is not None:
        candidates: list[_FreshnessCandidate] = []
        for key, child in mapping.items():
            key_text = str(key)
            kind = _field_kind(key_text, path)
            if kind is not None:
                parsed = _parse_datetime(child)
                if parsed is not None:
                    parsed_value, _ = parsed
                    candidates.append(
                        _FreshnessCandidate(
                            parsed=parsed_value,
                            kind=kind[1],
                        )
                    )
            candidates.extend(_collect_candidates(child, (*path, key_text.lower())))
        return candidates
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        candidates = []
        for child in value:
            candidates.extend(_collect_candidates(child, path))
        return candidates
    return []


def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def build_data_freshness(data: Any, observed_at: datetime | None = None) -> dict[str, Any]:
    """Build non-invasive freshness metadata for a successful tool response.

    ``observed_at`` records when this server finished obtaining the response.
    ``as_of`` is populated only from recognizable source date/time fields; it
    is intentionally left unknown when the payload does not expose one.
    """
    observed = observed_at or datetime.now(timezone.utc)
    if observed.tzinfo is None:
        observed = observed.replace(tzinfo=timezone.utc)
    observed = observed.astimezone(timezone.utc)

    candidates = _collect_candidates(data)
    realtime = [candidate for candidate in candidates if candidate.kind == "timestamp"]
    dated = [candidate for candidate in candidates if candidate.kind == "date"]
    selected = max(realtime or dated, key=lambda candidate: candidate.parsed, default=None)
    if selected is None:
        return {
            "observed_at": _iso_utc(observed),
            "as_of": None,
            "basis": "unknown",
            "status": "unknown",
            "age_seconds": None,
        }

    age_seconds = max(0, int((observed - selected.parsed).total_seconds()))
    return {
        "observed_at": _iso_utc(observed),
        "as_of": (
            _iso_utc(selected.parsed)
            if selected.kind == "timestamp"
            else selected.parsed.astimezone(_SHANGHAI).date().isoformat()
        ),
        "basis": "provider_timestamp" if selected.kind == "timestamp" else "source_date",
        "status": "realtime" if selected.kind == "timestamp" else "dated",
        "age_seconds": age_seconds,
    }
