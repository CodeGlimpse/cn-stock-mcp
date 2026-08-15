import pytest

from cn_stock_mcp.app.services.circuit_breaker import EndpointCircuitBreaker
from cn_stock_mcp.providers.errors import ProviderError


def test_endpoint_circuit_breaker_opens_after_threshold():
    breaker = EndpointCircuitBreaker(failure_threshold=2, reset_seconds=60)

    with pytest.raises(ValueError):
        breaker.call("endpoint-a", lambda: (_ for _ in ()).throw(ValueError("one")))
    with pytest.raises(ValueError):
        breaker.call("endpoint-a", lambda: (_ for _ in ()).throw(ValueError("two")))

    with pytest.raises(ProviderError) as exc:
        breaker.call("endpoint-a", lambda: "unreachable")

    assert exc.value.code == "PROVIDER_CIRCUIT_OPEN"
    assert breaker.is_open("endpoint-a") is True


def test_endpoint_circuit_breaker_success_resets_failures():
    breaker = EndpointCircuitBreaker(failure_threshold=2, reset_seconds=60)

    with pytest.raises(ValueError):
        breaker.call("endpoint-a", lambda: (_ for _ in ()).throw(ValueError("one")))
    assert breaker.call("endpoint-a", lambda: "ok") == "ok"
    with pytest.raises(ValueError):
        breaker.call("endpoint-a", lambda: (_ for _ in ()).throw(ValueError("again")))

    assert breaker.is_open("endpoint-a") is False
