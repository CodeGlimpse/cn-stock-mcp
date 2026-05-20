from __future__ import annotations

import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"

    mcp_server_name: str = "cn-stock-mcp"
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
    zhitu_daily_quota_per_token: int = 500
    zhitu_token_cooldown_seconds: int = 60

    cache_ttl_list_seconds: int = 86400
    cache_ttl_quote_seconds: int = 10
    cache_ttl_overview_seconds: int = 10
    cache_ttl_history_seconds: int = 3600
    cache_ttl_indicator_seconds: int = 300
    cache_ttl_orderbook_seconds: int = 3
    cache_ttl_pool_seconds: int = 600

    stock_review_batch_max_workers: int = 4
    sector_rotation_max_workers: int = 2

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def _resolve_zhitu_token_config_path(self) -> Path:
        path = Path(self.zhitu_token_config_path)
        if not path.is_absolute():
            path = Path.cwd() / path
        return path

    def _load_zhitu_token_config(self) -> dict:
        path = self._resolve_zhitu_token_config_path()
        if not path.exists():
            return {}

        try:
            raw_text = path.read_text(encoding="utf-8")
            text = "\n".join(line for line in raw_text.splitlines() if not line.strip().startswith("#"))
            return json.loads(text)
        except Exception:
            return {}

    def resolve_zhitu_tokens(self) -> list[str]:
        ordered_tokens: list[str] = []

        def add_token(value: str | None):
            token = str(value or "").strip()
            if token and token not in ordered_tokens:
                ordered_tokens.append(token)

        add_token(self.zhitu_token)

        data = self._load_zhitu_token_config()
        default_name = data.get("default")
        tokens = data.get("tokens", {})

        if isinstance(tokens, dict):
            if default_name and default_name in tokens:
                add_token(tokens.get(default_name))
            for _, value in tokens.items():
                add_token(value)

        return ordered_tokens

    def resolve_zhitu_token(self) -> str:
        tokens = self.resolve_zhitu_tokens()
        return tokens[0] if tokens else ""


def get_settings() -> Settings:
    return Settings()
