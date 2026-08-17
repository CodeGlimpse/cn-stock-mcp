from cn_stock_mcp.infra.security import redact_sensitive_text


def test_redact_sensitive_text_removes_query_and_assignment_values():
    value = "https://api.example.test?q=1&token=TOKEN_A api_key=KEY_A"

    result = redact_sensitive_text(value, secrets=["TOKEN_A"])

    assert "TOKEN_A" not in result
    assert "KEY_A" not in result
    assert "token=<redacted>" in result


def test_redact_sensitive_text_does_not_change_normal_diagnostics():
    assert redact_sensitive_text("bars=2") == "bars=2"
