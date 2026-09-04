from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from enum import Enum
from typing import Any


def to_json_safe(value: Any) -> Any:
    """Convert application values into strict RFC 8259 JSON-compatible data.

    In particular, Python's non-finite floats are converted to ``None`` so a
    provider returning NaN/Infinity cannot produce invalid JSON on stdio.
    """

    if hasattr(value, "model_dump"):
        return to_json_safe(value.model_dump(mode="python"))
    if isinstance(value, Mapping):
        return {str(key): to_json_safe(child) for key, child in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [to_json_safe(child) for child in value]
    if isinstance(value, (set, frozenset)):
        return [to_json_safe(child) for child in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return to_json_safe(value.value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if value is None or isinstance(value, (str, int, bool)):
        return value
    # Pydantic error contexts and a few provider libraries may leave an
    # exception/other opaque object in a response.  Stringifying it keeps the
    # stdio contract valid; secret-bearing text is already redacted at the
    # response/log boundary.
    return str(value)


def dumps_json(value: Any, **kwargs: Any) -> str:
    """Serialize values using strict JSON (never NaN/Infinity)."""

    options = {"ensure_ascii": False, "allow_nan": False}
    options.update(kwargs)
    return json.dumps(to_json_safe(value), **options)
