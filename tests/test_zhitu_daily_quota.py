"""Tests for Zhitu daily quota tracking and per-token exhaustion."""
import httpx

from cn_stock_mcp.providers.errors import ProviderRateLimitError
from cn_stock_mcp.providers.zhitu_provider import ZhituProvider


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
        return _Response(200, payload=[{'ok': True, 'token': token}])


class _Zhitu(ZhituProvider):
    def __init__(self, daily_quota=2):
        self.settings = type('S', (), {
            'zhitu_base_url': 'https://api.zhituapi.com',
            'zhitu_timeout_seconds': 15,
            'zhitu_token_cooldown_seconds': 60,
            'zhitu_daily_quota_per_token': daily_quota,
        })()
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


def test_daily_counter_increments_on_success():
    provider = _Zhitu(daily_quota=10)
    provider._get_json('/test')
    assert provider._daily_counters['TOKEN_A']['count'] == 1


def test_daily_counter_increments_on_failure():
    """Failed requests also consume daily quota (the upstream still counted it)."""
    class FailClient:
        calls = []
        def get(self, url, params=None):
            self.calls.append({'url': url, 'token': (params or {}).get('token')})
            raise httpx.TimeoutException('timeout')

    provider = _Zhitu(daily_quota=10)
    provider.client = FailClient()
    try:
        provider._get_json('/test')
    except Exception:
        pass
    assert provider._daily_counters['TOKEN_A']['count'] == 1


def test_exhausted_token_is_skipped():
    provider = _Zhitu(daily_quota=2)
    # Use TOKEN_A's quota
    provider._get_json('/test1')
    provider._get_json('/test2')
    assert provider._daily_remaining('TOKEN_A') == 0
    # Next call should use TOKEN_B
    provider._get_json('/test3')
    assert provider.client.calls[-1]['token'] == 'TOKEN_B'


def test_all_tokens_exhausted_still_tries():
    """When all tokens have quota=0, we still try (the upstream may allow overage)."""
    provider = _Zhitu(daily_quota=1)
    provider._get_json('/test1')  # uses TOKEN_A, quota now 0
    provider._get_json('/test2')  # uses TOKEN_B, quota now 0
    # Both exhausted, but should still try (not raise)
    provider._get_json('/test3')  # falls back to highest-score token
    assert len(provider.client.calls) == 3


def test_daily_counter_resets_on_new_day():
    provider = _Zhitu(daily_quota=2)
    counter = provider._ensure_daily_counter('TOKEN_A')
    counter['date'] = '2000-01-01'  # force old date
    counter['count'] = 100
    # Now ensure — should reset
    counter2 = provider._ensure_daily_counter('TOKEN_A')
    assert counter2['count'] == 0


def test_token_health_includes_daily_quota_fields():
    provider = _Zhitu(daily_quota=500)
    provider._get_json('/test')
    rows = provider.get_token_health()
    a = [r for r in rows if r['token'] == 'TOKEN_A'][0]
    assert a['daily_quota'] == 500
    assert a['daily_used'] == 1
    assert a['daily_remaining'] == 499
