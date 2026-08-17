from __future__ import annotations

from typing import Any

from cn_stock_mcp.providers.errors import ProviderError
from cn_stock_mcp.infra.security import redact_sensitive_text


def serialize_exception(exc: Exception, provider: str | None = None) -> dict[str, Any]:
    if isinstance(exc, ProviderError):
        return {
            "error_code": exc.code,
            "message": redact_sensitive_text(exc.message),
            "retryable": exc.retryable,
            "provider": provider,
        }
    return {
        "error_code": "INTERNAL_ERROR",
        "message": redact_sensitive_text(exc),
        "retryable": False,
        "provider": provider,
    }
