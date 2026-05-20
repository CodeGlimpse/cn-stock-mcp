from __future__ import annotations

from typing import Any
from uuid import uuid4

SCHEMA_VERSION = "v1"


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


def ok_response(data: Any, meta: dict[str, Any] | None = None, request_id: str | None = None) -> dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "error": None,
        "meta": _merge_meta(meta, request_id=request_id),
    }


def error_response(error: dict[str, Any], meta: dict[str, Any] | None = None, request_id: str | None = None) -> dict[str, Any]:
    return {
        "success": False,
        "data": None,
        "error": error,
        "meta": _merge_meta(meta, request_id=request_id),
    }
