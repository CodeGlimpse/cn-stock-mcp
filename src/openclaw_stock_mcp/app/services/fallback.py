from __future__ import annotations

from openclaw_stock_mcp.providers.errors import ProviderError


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
