from __future__ import annotations

import json
import os
import re
import stat
import subprocess
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from cn_stock_mcp import __version__
from cn_stock_mcp.app.services.tool_profiles import SAFE_FALLBACK_PROFILE, TOOL_PROFILES


class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"

    mcp_server_name: str = "cn-stock-mcp"

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
    zhitu_token_config_path: str = ""
    tool_profile: str = "full"
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
    sector_rotation_member_limit: int = 100
    sector_rotation_total_member_budget: int = 300
    hot_theme_total_member_budget: int = 300

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def mcp_server_version(self) -> str:
        """Return the installed package version; never allow config drift."""
        return __version__

    def _default_zhitu_token_config_path(self) -> Path:
        override = os.environ.get("CN_STOCK_MCP_CONFIG", "").strip()
        if override:
            return Path(override).expanduser()
        if os.name == "nt":
            root = os.environ.get("LOCALAPPDATA", "").strip()
            base = Path(root) if root else Path.home() / "AppData" / "Local"
        else:
            root = os.environ.get("XDG_CONFIG_HOME", "").strip()
            base = Path(root) if root else Path.home() / ".config"
        return base / "cn-stock-mcp" / "config.json"

    def _resolve_zhitu_token_config_path(self) -> Path:
        path = Path(self.zhitu_token_config_path).expanduser() if self.zhitu_token_config_path.strip() else self._default_zhitu_token_config_path()
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
        source = data.get("zhitu", data)
        if not isinstance(source, dict):
            return {}, "invalid_shape", "token config 'zhitu' must be a JSON object"
        tokens = source.get("tokens", {})
        if not isinstance(tokens, dict):
            return {}, "invalid_shape", "token config 'tokens' must be a JSON object"
        return data, "ok", "token config parsed"

    def zhitu_token_config_status(self) -> dict[str, str]:
        path = self._resolve_zhitu_token_config_path()
        _, status, message = self._read_zhitu_token_config()
        result = {"path": str(path), "status": status, "message": message}
        if status == "ok":
            permission_status, permission_message = _config_permission_status(path)
            result["permission_status"] = permission_status
            if permission_status == "insecure":
                result["status"] = "insecure_permissions"
                result["message"] = f"{message}; {permission_message}"
            elif permission_status == "unknown":
                result["message"] = f"{message}; file permissions could not be verified"
        return result

    def _load_zhitu_token_config(self) -> dict:
        data, status, _ = self._read_zhitu_token_config()
        return data if status == "ok" else {}

    def resolve_zhitu_tokens(self) -> list[str]:
        ordered_tokens: list[str] = []

        def add_token(value: str | None):
            if value is None:
                return
            # Do not stringify arbitrary JSON objects/numbers into a token;
            # malformed configuration should never produce a surprising
            # credential-like request.
            if not isinstance(value, str):
                return
            token = value.strip()
            if token and token not in ordered_tokens:
                ordered_tokens.append(token)

        data = self._load_zhitu_token_config()
        source = data.get("zhitu", data)
        default_name = source.get("default") if isinstance(source, dict) else None
        tokens = source.get("tokens", {}) if isinstance(source, dict) else {}

        if isinstance(tokens, dict):
            if default_name and default_name in tokens:
                add_token(tokens.get(default_name))
            for _, value in tokens.items():
                add_token(value)
        if isinstance(source, dict):
            add_token(source.get("token"))

        # The user-owned file is the documented source of truth.  Keep the
        # legacy environment-backed field as a final compatibility fallback;
        # this prevents a stale process environment from silently overriding a
        # token the user just placed in the config file.
        add_token(self.zhitu_token)

        return ordered_tokens

    def resolve_zhitu_token(self) -> str:
        tokens = self.resolve_zhitu_tokens()
        return tokens[0] if tokens else ""

    def resolve_tool_profile(self) -> str:
        data = self._load_zhitu_token_config()
        configured = data.get("tool_profile") if isinstance(data, dict) else None
        profile = str(self.tool_profile or "full").strip()
        if profile == "full" and isinstance(configured, str) and configured.strip():
            profile = configured.strip()
        profile = profile or "full"
        if profile not in TOOL_PROFILES:
            return SAFE_FALLBACK_PROFILE
        return profile


def get_settings() -> Settings:
    return Settings()


def initialize_user_config(path: str | None = None) -> tuple[Path, bool]:
    """Create a token config template without ever accepting a token value."""
    settings = Settings(zhitu_token_config_path=path or "")
    target = settings._resolve_zhitu_token_config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    created = not target.exists()
    if created:
        target.write_text(
            '{\n  "tool_profile": "retail_v1_preview",\n  "zhitu": {\n    "default": "primary",\n    "tokens": {\n      "primary": ""\n    }\n  }\n}\n',
            encoding="utf-8",
        )
    _harden_config_permissions(target)
    return target, created


def _harden_config_permissions(path: Path) -> None:
    if os.name == "nt":
        try:
            account = subprocess.run(
                ["whoami"], capture_output=True, text=True, check=True, timeout=5
            ).stdout.strip()
            accounts: list[str] = [account] if account else []
            # A local AI sandbox/service can run under a different account
            # from the interactive customer.  Keep the customer account from
            # the standard Windows environment when available, otherwise the
            # ACL hardening step can lock the person out of their own config.
            username = os.environ.get("USERNAME", "").strip()
            domain = os.environ.get("USERDOMAIN", "").strip()
            interactive = f"{domain}\\{username}" if domain and username else username
            if interactive and interactive.casefold() not in {item.casefold() for item in accounts}:
                accounts.append(interactive)
            grants = [f"{item}:F" for item in accounts if item]
            grants.append("SYSTEM:F")
            if grants:
                subprocess.run(
                    ["icacls", str(path), "/inheritance:r", "/grant:r", *grants],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=10,
                )
        except (OSError, subprocess.SubprocessError):
            return
        return
    try:
        path.chmod(0o600)
    except OSError:
        return


def _config_permission_status(path: Path) -> tuple[str, str]:
    """Best-effort check that a token file is not broadly readable."""

    try:
        if path.is_symlink():
            return "insecure", "token config is a symbolic link; use a regular user-owned file"
    except OSError:
        return "unknown", "token config path type could not be verified"

    if os.name != "nt":
        try:
            mode = stat.S_IMODE(path.stat().st_mode)
        except OSError:
            return "unknown", "token config permissions could not be read"
        if mode & 0o077:
            return "insecure", f"token config mode is {mode:04o}; restrict it to the owner (0600)"
        return "secure", "token config is owner-only"

    try:
        result = subprocess.run(
            ["icacls", str(path)], capture_output=True, text=True, check=False, timeout=10
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown", "icacls is unavailable"
    if result.returncode != 0:
        return "unknown", "icacls could not inspect the token config"

    # Avoid matching ``C:\Users`` in the path itself; inspect permission
    # entries for broad principals and inherited ACEs only.
    permission_lines = [line for line in result.stdout.splitlines() if ")" in line or ":" in line]
    broad = re.compile(r"(?i)(?:^|\\)(?:everyone|authenticated users|builtin\\users|users)\s*:")
    if any(broad.search(line) for line in permission_lines):
        return "insecure", "token config grants access to a broad Windows account group"
    if any("(I)" in line for line in permission_lines):
        return "insecure", "token config inherits permissions; rerun --init-config or restrict its ACL"
    return "secure", "token config ACL does not show broad or inherited access"
