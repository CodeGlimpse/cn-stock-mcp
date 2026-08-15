import httpx


def build_http_client(
    timeout_seconds: int = 15,
    *,
    trust_env: bool = False,
    proxy_url: str | None = None,
) -> httpx.Client:
    return httpx.Client(
        timeout=timeout_seconds,
        trust_env=trust_env,
        proxy=proxy_url or None,
    )
