from openclaw_stock_mcp.server.transport import TransportApp


def test_sector_lookup_missing_sector_type_returns_json_safe_invalid_argument_envelope():
    app = TransportApp()
    result = app.call_tool("sector_lookup", {"mode": "children", "sector_name": "银行", "limit": 20})

    assert result["success"] is False
    assert result["error"]["error_code"] == "INVALID_ARGUMENT"
    assert "details" in result["error"]
    assert isinstance(result["error"]["details"], list)
    assert result["error"]["details"][0]["type"] == "value_error"

    payload = app.to_stdio_payload("sector_lookup", {"mode": "children", "sector_name": "银行", "limit": 20})
    assert '"error_code": "INVALID_ARGUMENT"' in payload
    assert 'sector_type is required when mode=members/children' in payload
