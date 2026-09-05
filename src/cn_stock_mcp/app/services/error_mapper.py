from __future__ import annotations

from typing import Any

from cn_stock_mcp.providers.errors import ProviderError
from cn_stock_mcp.infra.security import redact_sensitive_text


def _known_secrets() -> list[str]:
    try:
        from cn_stock_mcp.infra.config import get_settings

        return get_settings().resolve_zhitu_tokens()
    except Exception:
        return []


def serialize_exception(exc: Exception, provider: str | None = None) -> dict[str, Any]:
    secrets = _known_secrets()
    if isinstance(exc, ProviderError):
        return {
            "error_code": exc.code,
            "message": redact_sensitive_text(exc.message, secrets),
            "retryable": exc.retryable,
            "provider": provider,
        }
    return {
        "error_code": "INTERNAL_ERROR",
        "message": redact_sensitive_text(exc, secrets),
        "retryable": False,
        "provider": provider,
    }
