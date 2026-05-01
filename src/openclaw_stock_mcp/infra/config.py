from __future__ import annotations

import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"

    mcp_server_name: str = "openclaw-stock-mcp"
    mcp_server_version: str = "0.1.0"

    default_market: str = "CN"
    default_provider_order: str = "akshare,zhitu"
    enable_provider_fallback: bool = True

    akshare_enabled: bool = True
    akshare_timeout_seconds: int = 20

    zhitu_enabled: bool = True
    zhitu_base_url: str = "https://api.zhituapi.com"
    zhitu_token: str = ""
    zhitu_token_config_path: str = "config/zhitu_tokens.json"
    zhitu_timeout_seconds: int = 15
    zhitu_rate_limit_per_minute: int = 300

    cache_ttl_list_seconds: int = 86400
    cache_ttl_quote_seconds: int = 10
    cache_ttl_overview_seconds: int = 10
    cache_ttl_history_seconds: int = 3600
    cache_ttl_indicator_seconds: int = 300
    cache_ttl_orderbook_seconds: int = 3
    cache_ttl_pool_seconds: int = 600

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def resolve_zhitu_token(self) -> str:
        if self.zhitu_token:
            return self.zhitu_token

        path = Path(self.zhitu_token_config_path)
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.exists():
            return ""

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return ""

        default_name = data.get("default")
        tokens = data.get("tokens", {})
        if default_name and default_name in tokens:
            return str(tokens[default_name])

        if tokens:
            first_value = next(iter(tokens.values()))
            return str(first_value)
        return ""


def get_settings() -> Settings:
    return Settings()
