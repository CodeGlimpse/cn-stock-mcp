from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openclaw_stock_mcp.providers.errors import ProviderError


@dataclass
class FallbackMeta:
    attempted: list[str]
    selected_primary: str
    selected_fallback: list[str]
    final_provider: str | None
    used_fallback: bool
    last_error: dict[str, Any] | None


def _err_to_dict(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, ProviderError):
        return {
            "error_code": exc.code,
            "message": exc.message,
            "retryable": exc.retryable,
        }
    return {
        "error_code": "INTERNAL_ERROR",
        "message": str(exc),
        "retryable": False,
    }


def run_with_fallback(router, selection, invoke):
    last_error: Exception | None = None
    provider_names = [selection.primary, *selection.fallback]
    for name in provider_names:
        provider = router.get_provider(name)
        try:
            return invoke(provider)
        except ProviderError as exc:
            last_error = exc
            if not exc.retryable:
                raise
            continue
        except Exception as exc:  # pragma: no cover
            last_error = exc
            continue
    if last_error:
        raise last_error
    raise RuntimeError("No provider available")


def run_with_fallback_meta(router, selection, invoke):
    last_error: Exception | None = None
    attempted: list[str] = []
    provider_names = [selection.primary, *selection.fallback]

    for name in provider_names:
        provider = router.get_provider(name)
        attempted.append(name)
        try:
            result = invoke(provider)
            meta = FallbackMeta(
                attempted=attempted,
                selected_primary=selection.primary,
                selected_fallback=list(selection.fallback),
                final_provider=name,
                used_fallback=name != selection.primary,
                last_error=None,
            )
            return result, meta
        except ProviderError as exc:
            last_error = exc
            if not exc.retryable:
                raise
            continue
        except Exception as exc:  # pragma: no cover
            last_error = exc
            continue

    if last_error:
        raise last_error
    raise RuntimeError("No provider available")
