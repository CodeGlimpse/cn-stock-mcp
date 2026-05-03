from pathlib import Path

from openclaw_stock_mcp.infra.config import Settings


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
