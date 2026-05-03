from __future__ import annotations

from typing import Any


def ok_response(data: Any, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "error": None,
        "meta": meta or {},
    }


def error_response(error: dict[str, Any], meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "success": False,
        "data": None,
        "error": error,
        "meta": meta or {},
    }
