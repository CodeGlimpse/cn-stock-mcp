from __future__ import annotations

from collections.abc import Callable
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


_NO_RESULT = object()
_FALLBACKABLE_ERROR_CODES = {
    "PROVIDER_UNAVAILABLE",
    "PROVIDER_TIMEOUT",
    "PROVIDER_RATE_LIMIT",
    "UNSUPPORTED_MARKET",
    "UNSUPPORTED_SEC_TYPE",
    "UNSUPPORTED_INTERVAL",
}


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


def _should_try_next_provider(exc: ProviderError) -> bool:
    return exc.retryable or exc.code in _FALLBACKABLE_ERROR_CODES


def _should_try_next_result(result: Any, should_fallback_result: Callable[[Any], bool] | None, has_next: bool) -> bool:
    if not has_next or should_fallback_result is None:
        return False
    try:
        return bool(should_fallback_result(result))
    except Exception:
        return False


def _build_meta(selection, attempted: list[str], final_provider: str | None, last_error: Exception | None) -> FallbackMeta:
    return FallbackMeta(
        attempted=list(attempted),
        selected_primary=selection.primary,
        selected_fallback=list(selection.fallback),
        final_provider=final_provider,
        used_fallback=final_provider is not None and final_provider != selection.primary,
        last_error=_err_to_dict(last_error) if last_error else None,
    )


def run_with_fallback(router, selection, invoke, should_fallback_result: Callable[[Any], bool] | None = None):
    last_error: Exception | None = None
    candidate_result: Any = _NO_RESULT
    provider_names = [selection.primary, *selection.fallback]

    for idx, name in enumerate(provider_names):
        provider = router.get_provider(name)
        has_next = idx < len(provider_names) - 1
        try:
            result = invoke(provider)
            if _should_try_next_result(result, should_fallback_result, has_next):
                if candidate_result is _NO_RESULT:
                    candidate_result = result
                continue
            return result
        except ProviderError as exc:
            last_error = exc
            if candidate_result is not _NO_RESULT and not _should_try_next_provider(exc):
                return candidate_result
            if not _should_try_next_provider(exc):
                raise
            continue
        except Exception as exc:  # pragma: no cover
            last_error = exc
            continue

    if candidate_result is not _NO_RESULT:
        return candidate_result
    if last_error:
        raise last_error
    raise RuntimeError("No provider available")


def run_with_fallback_meta(router, selection, invoke, should_fallback_result: Callable[[Any], bool] | None = None):
    last_error: Exception | None = None
    attempted: list[str] = []
    candidate_result: Any = _NO_RESULT
    candidate_provider: str | None = None
    provider_names = [selection.primary, *selection.fallback]

    for idx, name in enumerate(provider_names):
        provider = router.get_provider(name)
        attempted.append(name)
        has_next = idx < len(provider_names) - 1
        try:
            result = invoke(provider)
            if _should_try_next_result(result, should_fallback_result, has_next):
                if candidate_result is _NO_RESULT:
                    candidate_result = result
                    candidate_provider = name
                continue
            meta = _build_meta(selection, attempted, name, last_error)
            return result, meta
        except ProviderError as exc:
            last_error = exc
            if candidate_result is not _NO_RESULT and not _should_try_next_provider(exc):
                meta = _build_meta(selection, attempted, candidate_provider, last_error)
                return candidate_result, meta
            if not _should_try_next_provider(exc):
                raise
            continue
        except Exception as exc:  # pragma: no cover
            last_error = exc
            continue

    if candidate_result is not _NO_RESULT:
        meta = _build_meta(selection, attempted, candidate_provider, last_error)
        return candidate_result, meta
    if last_error:
        raise last_error
    raise RuntimeError("No provider available")
