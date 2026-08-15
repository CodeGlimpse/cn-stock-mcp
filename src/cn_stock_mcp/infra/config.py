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
    provider_trust_env: bool = False
    provider_proxy_url: str = ""

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
    cache_ttl_capital_flow_seconds: int = 300
    capital_flow_stale_max_age_seconds: int = 86400
    capital_flow_circuit_failure_threshold: int = 3
    capital_flow_circuit_reset_seconds: int = 60

    stock_review_batch_max_workers: int = 4
    sector_rotation_max_workers: int = 2

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def _resolve_zhitu_token_config_path(self) -> Path:
        path = Path(self.zhitu_token_config_path)
        if not path.is_absolute():
            path = Path.cwd() / path
        return path

    def _read_zhitu_token_config(self) -> tuple[dict, str, str]:
        path = self._resolve_zhitu_token_config_path()
        if not path.exists():
            return {}, "missing", "token config file not found"

        try:
            raw_text = path.read_text(encoding="utf-8")
            text = "\n".join(line for line in raw_text.splitlines() if not line.strip().startswith("#"))
        except UnicodeDecodeError:
            return {}, "unreadable", "token config is not valid UTF-8"
        except OSError as exc:
            return {}, "unreadable", f"token config cannot be read: {exc.__class__.__name__}"

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            return {}, "invalid", f"token config JSON is invalid at line {exc.lineno}, column {exc.colno}"
        if not isinstance(data, dict):
            return {}, "invalid_shape", "token config root must be a JSON object"
        tokens = data.get("tokens", {})
        if not isinstance(tokens, dict):
            return {}, "invalid_shape", "token config 'tokens' must be a JSON object"
        return data, "ok", "token config parsed"

    def zhitu_token_config_status(self) -> dict[str, str]:
        path = self._resolve_zhitu_token_config_path()
        _, status, message = self._read_zhitu_token_config()
        return {"path": str(path), "status": status, "message": message}

    def _load_zhitu_token_config(self) -> dict:
        data, status, _ = self._read_zhitu_token_config()
        return data if status == "ok" else {}

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
