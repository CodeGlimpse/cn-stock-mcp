from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "v1"


def _merge_meta(meta: dict[str, Any] | None) -> dict[str, Any]:
    merged = {"schema_version": SCHEMA_VERSION}
    if meta:
        merged.update(meta)
    return merged


def ok_response(data: Any, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "error": None,
        "meta": _merge_meta(meta),
    }


def error_response(error: dict[str, Any], meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "success": False,
        "data": None,
        "error": error,
        "meta": _merge_meta(meta),
    }
