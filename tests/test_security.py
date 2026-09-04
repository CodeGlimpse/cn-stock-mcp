from cn_stock_mcp.infra.security import redact_sensitive_text, redact_sensitive_value


def test_redact_sensitive_text_removes_query_and_assignment_values():
    value = "https://api.example.test?q=1&token=TOKEN_A api_key=KEY_A"

    result = redact_sensitive_text(value, secrets=["TOKEN_A"])

    assert "TOKEN_A" not in result
    assert "KEY_A" not in result
    assert "token=<redacted>" in result


def test_redact_sensitive_text_does_not_change_normal_diagnostics():
    assert redact_sensitive_text("bars=2") == "bars=2"


def test_redact_sensitive_text_handles_json_keys_bearer_and_access_token():
    value = '{"access_token":"ACCESS", "authorization":"Bearer SECRET", "ok": "x"}'

    result = redact_sensitive_text(value)

    assert "ACCESS" not in result
    assert "Bearer SECRET" not in result
    assert '"ok": "x"' in result


def test_redact_sensitive_value_does_not_echo_nested_secret_fields():
    result = redact_sensitive_value(
        {"zhitu_token": "TOKEN", "nested": {"api_key": "KEY", "count": 1}}
    )

    assert result["zhitu_token"] != "TOKEN"
    assert result["nested"]["api_key"] == "<redacted>"
    assert result["nested"]["count"] == 1
