from pathlib import Path

from cn_stock_mcp.infra.config import Settings
from cn_stock_mcp.infra.config import initialize_user_config
from cn_stock_mcp import __version__


def test_resolve_zhitu_tokens_reads_default_first_and_keeps_others(tmp_path: Path):
    config_path = tmp_path / "zhitu_tokens.json"
    config_path.write_text(
        '\n'.join([
            '# comment line',
            '{',
            '  "default": "secondary",',
            '  "tokens": {',
            '    "primary": "TOKEN_A",',
            '    "secondary": "TOKEN_B"',
            '  }',
            '}',
        ]),
        encoding='utf-8',
    )

    settings = Settings(zhitu_token_config_path=str(config_path), zhitu_token="")

    assert settings.resolve_zhitu_tokens() == ["TOKEN_B", "TOKEN_A"]
    assert settings.resolve_zhitu_token() == "TOKEN_B"


def test_token_config_status_reports_invalid_json_without_exposing_content(tmp_path: Path):
    config_path = tmp_path / "zhitu_tokens.json"
    config_path.write_text('{"tokens":', encoding="utf-8")

    settings = Settings(zhitu_token_config_path=str(config_path), zhitu_token="")
    status = settings.zhitu_token_config_status()

    assert status["status"] == "invalid"
    assert "line" in status["message"]
    assert "tokens" not in status["message"]
    assert settings.resolve_zhitu_tokens() == []


def test_token_config_status_reports_invalid_shape(tmp_path: Path):
    config_path = tmp_path / "zhitu_tokens.json"
    config_path.write_text('{"tokens": []}', encoding="utf-8")

    settings = Settings(zhitu_token_config_path=str(config_path), zhitu_token="")

    assert settings.zhitu_token_config_status()["status"] == "invalid_shape"


def test_nested_user_config_reads_token_and_tool_profile(tmp_path: Path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        '{"tool_profile":"retail_v1_preview","zhitu":{"token":"TOKEN_NESTED"}}',
        encoding="utf-8",
    )

    settings = Settings(zhitu_token_config_path=str(config_path), zhitu_token="")

    assert settings.resolve_zhitu_tokens() == ["TOKEN_NESTED"]
    assert settings.resolve_tool_profile() == "retail_v1_preview"


def test_initialize_user_config_is_idempotent_and_contains_no_token(tmp_path: Path):
    config_path = tmp_path / "config.json"

    first_path, first_created = initialize_user_config(str(config_path))
    second_path, second_created = initialize_user_config(str(config_path))

    assert first_path == second_path == config_path
    assert first_created is True
    assert second_created is False
    assert '"primary": ""' in config_path.read_text(encoding="utf-8")


def test_package_version_cannot_be_overridden_by_environment(monkeypatch):
    monkeypatch.setenv("MCP_SERVER_VERSION", "9.9.9")

    assert Settings().mcp_server_version == __version__


def test_file_token_takes_precedence_over_legacy_environment_value(tmp_path: Path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"zhitu":{"token":"FILE_TOKEN"}}', encoding="utf-8")

    settings = Settings(zhitu_token_config_path=str(config_path), zhitu_token="ENV_TOKEN")

    assert settings.resolve_zhitu_token() == "FILE_TOKEN"


def test_posix_permission_check_flags_group_readable_token_file(tmp_path: Path, monkeypatch):
    from cn_stock_mcp.infra import config as config_module

    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    path.chmod(0o644)
    monkeypatch.setattr(config_module.os, "name", "posix")

    status, _message = config_module._config_permission_status(path)

    assert status == "insecure"


def test_windows_acl_hardening_keeps_interactive_user_access(tmp_path: Path, monkeypatch):
    from types import SimpleNamespace
    from cn_stock_mcp.infra import config as config_module

    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")
    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(stdout="DESKTOP\\Sandbox\n")

    monkeypatch.setattr(config_module.os, "name", "nt")
    monkeypatch.setenv("USERDOMAIN", "DESKTOP")
    monkeypatch.setenv("USERNAME", "Customer")
    monkeypatch.setattr(config_module.subprocess, "run", fake_run)

    config_module._harden_config_permissions(path)

    assert len(calls) == 2
    acl_args = calls[1]
    assert "DESKTOP\\Customer:F" in acl_args
    assert "SYSTEM:F" in acl_args


def test_non_string_token_values_are_ignored(tmp_path: Path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"zhitu":{"tokens":{"bad":{"value":1},"ok":"TOKEN"}}}', encoding="utf-8")

    settings = Settings(zhitu_token_config_path=str(config_path))

    assert settings.resolve_zhitu_tokens() == ["TOKEN"]


def test_invalid_config_fails_closed_to_retail_profile(tmp_path: Path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"tool_profile":', encoding="utf-8")

    settings = Settings(zhitu_token_config_path=str(config_path), tool_profile="full")

    assert settings.resolve_tool_profile() == "retail_v1_preview"


def test_token_source_status_reports_environment_conflict_without_values(tmp_path: Path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"zhitu":{"token":"FILE_TOKEN"}}', encoding="utf-8")

    settings = Settings(zhitu_token_config_path=str(config_path), zhitu_token="ENV_TOKEN")
    status = settings.zhitu_token_source_status()

    assert status["source"] == "config_file"
    assert status["file_token_count"] == 1
    assert status["environment_token_present"] is True
    assert status["environment_conflict"] is True
    assert "TOKEN" not in str(status)
