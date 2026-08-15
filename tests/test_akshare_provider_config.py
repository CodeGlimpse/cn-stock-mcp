from types import SimpleNamespace

import requests

from cn_stock_mcp.infra.config import Settings
from cn_stock_mcp.providers.akshare_provider import AKShareProvider


def test_akshare_timeout_is_injected_when_upstream_omits_timeout(monkeypatch):
    calls = []

    def fake_request(session, method, url, *args, **kwargs):
        calls.append({"method": method, "url": url, "timeout": kwargs.get("timeout")})
        return SimpleNamespace(status_code=200)

    monkeypatch.setattr(requests.sessions.Session, "request", fake_request)
    provider = AKShareProvider(settings=Settings(akshare_timeout_seconds=7))

    response = provider._call_ak_quietly(requests.get, "https://example.test")

    assert response.status_code == 200
    assert calls == [{"method": "get", "url": "https://example.test", "timeout": 7}]


def test_akshare_timeout_does_not_override_explicit_timeout(monkeypatch):
    calls = []

    def fake_request(session, method, url, *args, **kwargs):
        calls.append(kwargs.get("timeout"))
        return SimpleNamespace(status_code=200)

    monkeypatch.setattr(requests.sessions.Session, "request", fake_request)
    provider = AKShareProvider(settings=Settings(akshare_timeout_seconds=7))

    provider._call_ak_quietly(requests.get, "https://example.test", timeout=3)

    assert calls == [3]


def test_akshare_proxy_settings_are_injected(monkeypatch):
    calls = []

    def fake_request(session, method, url, *args, **kwargs):
        calls.append(kwargs.get("proxies"))
        return SimpleNamespace(status_code=200)

    monkeypatch.setattr(requests.sessions.Session, "request", fake_request)
    provider = AKShareProvider(
        settings=Settings(
            akshare_timeout_seconds=7,
            provider_proxy_url="http://proxy.example:8080",
            provider_trust_env=False,
        )
    )

    provider._call_ak_quietly(requests.get, "https://example.test")

    assert calls == [{"http": "http://proxy.example:8080", "https": "http://proxy.example:8080"}]
