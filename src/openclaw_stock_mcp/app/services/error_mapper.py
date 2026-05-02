from __future__ import annotations

from typing import Any

from openclaw_stock_mcp.providers.errors import ProviderError


def serialize_exception(exc: Exception, provider: str | None = None) -> dict[str, Any]:
    if isinstance(exc, ProviderError):
        return {
            "error_code": exc.code,
            "message": exc.message,
            "retryable": exc.retryable,
            "provider": provider,
        }
    return {
        "error_code": "INTERNAL_ERROR",
        "message": str(exc),
        "retryable": False,
        "provider": provider,
    }
