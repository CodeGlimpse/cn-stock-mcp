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
