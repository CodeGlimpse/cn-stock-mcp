from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import uuid4

SCHEMA_VERSION = "v1"
_OBSERVABILITY_KEYS = (
    "provider_used",
    "fallback_chain",
    "latency_ms",
    "used_fallback",
    "final_provider",
    "attempted",
)


def new_request_id() -> str:
    return f"req_{uuid4().hex}"


def _merge_meta(meta: dict[str, Any] | None, request_id: str | None = None) -> dict[str, Any]:
    merged = {
        "schema_version": SCHEMA_VERSION,
        "request_id": request_id or new_request_id(),
    }
    if meta:
        merged.update(meta)
    return merged


def _extract_observability_meta(data: Any) -> dict[str, Any]:
    """Promote stable use-case observability fields without changing data shape."""
    if not isinstance(data, Mapping):
        return {}
    nested = data.get("meta")
    if not isinstance(nested, Mapping):
        return {}
    return {
        key: nested[key]
        for key in _OBSERVABILITY_KEYS
        if key in nested
    }


def ok_response(data: Any, meta: dict[str, Any] | None = None, request_id: str | None = None) -> dict[str, Any]:
    merged_meta = _merge_meta(meta, request_id=request_id)
    for key, value in _extract_observability_meta(data).items():
        merged_meta.setdefault(key, value)
    return {
        "success": True,
        "data": data,
        "error": None,
        "meta": merged_meta,
    }


def error_response(error: dict[str, Any], meta: dict[str, Any] | None = None, request_id: str | None = None) -> dict[str, Any]:
    return {
        "success": False,
        "data": None,
        "error": error,
        "meta": _merge_meta(meta, request_id=request_id),
    }
