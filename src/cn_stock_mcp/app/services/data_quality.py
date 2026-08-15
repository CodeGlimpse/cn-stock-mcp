from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel


DATA_QUALITY_SCHEMA = "data_quality_v1"


def _as_mapping(value: Any) -> Mapping[str, Any] | None:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="python")
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value if isinstance(value, Mapping) else None


def _meta(data: Any) -> Mapping[str, Any]:
    mapping = _as_mapping(data)
    nested = _as_mapping(mapping.get("meta")) if mapping else None
    return nested or {}


def _has_nested_flag(meta: Mapping[str, Any], key: str) -> bool:
    if bool(meta.get(key)):
        return True
    per_symbol = meta.get("per_symbol")
    if isinstance(per_symbol, Mapping):
        return any(
            bool(item_mapping and item_mapping.get(key))
            for item in per_symbol.values()
            for item_mapping in [_as_mapping(item)]
        )
    if isinstance(per_symbol, Sequence) and not isinstance(per_symbol, (str, bytes, bytearray)):
        return any(
            bool(item_mapping and item_mapping.get(key))
            for item in per_symbol
            for item_mapping in [_as_mapping(item)]
        )
    return False


def _has_empty_result(data: Any, meta: Mapping[str, Any]) -> bool:
    if bool(meta.get("provider_empty_result")):
        return True
    mapping = _as_mapping(data)
    if not mapping:
        return False
    count = mapping.get("count")
    if count == 0:
        return True
    for key in ("items", "records", "quotes", "results", "rows"):
        value = mapping.get(key)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and not value:
            return True
    return False


def _collect_anomalies(value: Any, path: tuple[str, ...] = (), found: list[str] | None = None) -> list[str]:
    found = found if found is not None else []
    if len(found) >= 20:
        return found
    mapping = _as_mapping(value)
    if mapping is not None:
        for key, child in mapping.items():
            _collect_anomalies(child, (*path, str(key)), found)
        return found
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _collect_anomalies(child, (*path, str(index)), found)
        return found
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        found.append(".".join(path))
    elif isinstance(value, str) and value.strip().lower() in {"nan", "inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"}:
        found.append(".".join(path))
    return found


def build_data_quality(data: Any, freshness: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build explainable data quality metadata, never an investment judgment."""
    mapping = _as_mapping(data) or {}
    meta = _meta(data)
    freshness = freshness or {}

    used_fallback = _has_nested_flag(meta, "used_fallback")
    partial_failure = (
        bool(mapping.get("partial_failure"))
        or bool(meta.get("partial_failure"))
        or bool(mapping.get("errors"))
    )
    stale = bool(meta.get("stale"))
    empty_result = _has_empty_result(data, meta)
    missing_fields = meta.get("missing_fields")
    if not isinstance(missing_fields, list):
        missing_fields = []
    anomalies = _collect_anomalies(data)

    status = freshness.get("status", "unknown")
    age_seconds = freshness.get("age_seconds")
    age_penalty = 0
    aged_data = False
    if isinstance(age_seconds, (int, float)):
        if status == "realtime":
            if age_seconds > 1800:
                age_penalty, aged_data = 25, True
            elif age_seconds > 300:
                age_penalty, aged_data = 15, True
            elif age_seconds > 60:
                age_penalty, aged_data = 5, True
        elif status == "dated":
            if age_seconds > 604800:
                age_penalty, aged_data = 20, True
            elif age_seconds > 172800:
                age_penalty, aged_data = 10, True
    freshness_unknown = status == "unknown"

    penalties = {
        "fallback": 15 if used_fallback else 0,
        "partial_failure": 25 if partial_failure else 0,
        "stale": 25 if stale else 0,
        "empty_result": 20 if empty_result else 0,
        "missing_fields": min(25, len(missing_fields) * 5),
        "anomalies": min(20, len(anomalies) * 10),
        "age": age_penalty,
        "freshness_unknown": 5 if freshness_unknown else 0,
    }
    score = max(0, min(100, 100 - sum(penalties.values())))
    label = "high" if score >= 80 else "medium" if score >= 60 else "low"

    flags: list[str] = []
    if used_fallback:
        flags.append("provider_fallback")
    if partial_failure:
        flags.append("partial_failure")
    if stale:
        flags.append("stale_cache")
    if empty_result:
        flags.append("empty_result")
    if missing_fields:
        flags.append("missing_fields")
    if anomalies:
        flags.append("anomalous_values")
    if aged_data:
        flags.append("aged_data")
    if freshness_unknown:
        flags.append("freshness_unknown")

    return {
        "schema": DATA_QUALITY_SCHEMA,
        "score": score,
        "label": label,
        "flags": flags,
        "factors": {
            "used_fallback": used_fallback,
            "partial_failure": partial_failure,
            "stale": stale,
            "empty_result": empty_result,
            "missing_field_count": len(missing_fields),
            "missing_fields": missing_fields,
            "anomaly_count": len(anomalies),
            "anomaly_fields": anomalies,
            "freshness_status": status,
            "age_seconds": age_seconds,
            "age_penalty": age_penalty,
        },
        "note": "Heuristic data quality only; not an investment confidence or recommendation score.",
    }
