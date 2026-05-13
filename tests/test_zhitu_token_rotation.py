import httpx

from openclaw_stock_mcp.providers.errors import ProviderRateLimitError
from openclaw_stock_mcp.providers.zhitu_provider import ZhituProvider


class _Response:
    def __init__(self, status_code: int, payload=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else []
        self.request = httpx.Request('GET', 'https://api.zhituapi.com/test')

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError('error', request=self.request, response=self)

    def json(self):
        return self._payload


class _Client:
    def __init__(self):
        self.calls = []

    def get(self, url, params=None):
        token = (params or {}).get('token')
        self.calls.append({'url': url, 'token': token})
        if token == 'TOKEN_A':
            return _Response(429)
        return _Response(200, payload=[{'ok': True, 'token': token}])


class _RateLimitedClient:
    def __init__(self):
        self.calls = []

    def get(self, url, params=None):
        token = (params or {}).get('token')
        self.calls.append({'url': url, 'token': token})
        return _Response(429)


class _Zhitu(ZhituProvider):
    def __init__(self):
        self.settings = type('S', (), {'zhitu_base_url': 'https://api.zhituapi.com', 'zhitu_timeout_seconds': 15, 'zhitu_token_cooldown_seconds': 60, 'zhitu_daily_quota_per_token': 500})()
        self.base_url = self.settings.zhitu_base_url.rstrip('/')
        self.tokens = ['TOKEN_A', 'TOKEN_B']
        self.token = self.tokens[0]
        self.client = _Client()
        self._instrument_name_cache = {}
        self._token_cooldowns = {}
        self._daily_quota = int(self.settings.zhitu_daily_quota_per_token)
        self._daily_counters = {token: {"date": "", "count": 0} for token in self.tokens}
        self._token_stats = {
            token: {
                'total_requests': 0,
                'success_count': 0,
                'failure_count': 0,
                'rate_limit_count': 0,
                'last_success_at': None,
                'last_failure_at': None,
            }
            for token in self.tokens
        }


class _ZhituAll429(ZhituProvider):
    def __init__(self):
        self.settings = type('S', (), {'zhitu_base_url': 'https://api.zhituapi.com', 'zhitu_timeout_seconds': 15, 'zhitu_token_cooldown_seconds': 60, 'zhitu_daily_quota_per_token': 500})()
        self.base_url = self.settings.zhitu_base_url.rstrip('/')
        self.tokens = ['TOKEN_A', 'TOKEN_B']
        self.token = self.tokens[0]
        self.client = _RateLimitedClient()
        self._instrument_name_cache = {}
        self._token_cooldowns = {}
        self._daily_quota = int(self.settings.zhitu_daily_quota_per_token)
        self._daily_counters = {token: {"date": "", "count": 0} for token in self.tokens}
        self._token_stats = {
            token: {
                'total_requests': 0,
                'success_count': 0,
                'failure_count': 0,
                'rate_limit_count': 0,
                'last_success_at': None,
                'last_failure_at': None,
            }
            for token in self.tokens
        }


def test_zhitu_provider_switches_token_on_429():
    provider = _Zhitu()

    result = provider._get_json('/hz/list/hszs')

    assert result == [{'ok': True, 'token': 'TOKEN_B'}]
    assert [call['token'] for call in provider.client.calls] == ['TOKEN_A', 'TOKEN_B']
    assert provider.token == 'TOKEN_B'
    assert 'TOKEN_A' in provider._token_cooldowns



def test_zhitu_provider_raises_rate_limit_when_all_tokens_limited():
    provider = _ZhituAll429()

    try:
        provider._get_json('/hz/list/hszs')
        assert False, 'expected ProviderRateLimitError'
    except ProviderRateLimitError as exc:
        assert exc.code == 'PROVIDER_RATE_LIMIT'
        assert exc.retryable is True

    assert [call['token'] for call in provider.client.calls] == ['TOKEN_A', 'TOKEN_B']


def test_zhitu_token_health_contains_observability_fields():
    provider = _Zhitu()
    provider._get_json('/hz/list/hszs')

    rows = provider.get_token_health()
    by_token = {row['token']: row for row in rows}

    assert set(by_token.keys()) == {'TOKEN_A', 'TOKEN_B'}

    a = by_token['TOKEN_A']
    assert a['total_requests'] == 1
    assert a['failure_count'] == 1
    assert a['rate_limit_count'] == 1
    assert a['cooldown_remaining_seconds'] >= 0

    b = by_token['TOKEN_B']
    assert b['total_requests'] == 1
    assert b['success_count'] == 1
    assert b['failure_count'] == 0
    assert b['success_rate'] == 1.0
