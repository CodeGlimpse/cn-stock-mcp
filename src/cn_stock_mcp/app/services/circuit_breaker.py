from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import TypeVar

from cn_stock_mcp.providers.errors import ProviderError


T = TypeVar("T")


@dataclass
class _CircuitState:
    failures: int = 0
    opened_until: float = 0.0


class EndpointCircuitBreaker:
    """Small in-process breaker for unstable upstream endpoints."""

    def __init__(self, failure_threshold: int = 3, reset_seconds: int = 60) -> None:
        self.failure_threshold = max(int(failure_threshold or 3), 1)
        self.reset_seconds = max(int(reset_seconds or 60), 1)
        self._states: dict[str, _CircuitState] = {}
        self._lock = RLock()

    def call(self, endpoint: str, operation: Callable[[], T]) -> T:
        now = monotonic()
        with self._lock:
            state = self._states.get(endpoint)
            if state and state.opened_until > now:
                remaining = max(1, int(state.opened_until - now))
                raise ProviderError(
                    "PROVIDER_CIRCUIT_OPEN",
                    f"Provider endpoint circuit is open: {endpoint} ({remaining}s remaining)",
                    retryable=True,
                )

        try:
            result = operation()
        except Exception:
            self._record_failure(endpoint)
            raise

        self._record_success(endpoint)
        return result

    def _record_failure(self, endpoint: str) -> None:
        with self._lock:
            state = self._states.setdefault(endpoint, _CircuitState())
            state.failures += 1
            if state.failures >= self.failure_threshold:
                state.opened_until = monotonic() + self.reset_seconds

    def _record_success(self, endpoint: str) -> None:
        with self._lock:
            self._states.pop(endpoint, None)

    def is_open(self, endpoint: str) -> bool:
        with self._lock:
            state = self._states.get(endpoint)
            return bool(state and state.opened_until > monotonic())
