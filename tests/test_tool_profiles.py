from cn_stock_mcp.app.services.tool_profiles import RETAIL_V1_PREVIEW, select_tool_names
from cn_stock_mcp.server.mcp_server import create_server


def test_retail_preview_is_bounded_and_contains_high_level_tools():
    assert len(RETAIL_V1_PREVIEW) == 10
    assert {"stock_search", "market_brief", "stock_snapshot", "stock_quote"} <= RETAIL_V1_PREVIEW


def test_full_profile_preserves_all_names():
    names = {"stock_quote", "stock_history", "provider_health"}
    assert select_tool_names(names, "full") == names


def test_unknown_profile_fails_open_to_full_for_backward_compatibility():
    names = {"stock_quote", "provider_health"}
    assert select_tool_names(names, "future_profile") == names


def test_server_applies_profile_from_user_config(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"tool_profile":"retail_v1_preview"}', encoding="utf-8")
    monkeypatch.setenv("CN_STOCK_MCP_CONFIG", str(config_path))

    server = create_server()

    assert set(server.tools) == RETAIL_V1_PREVIEW
    assert server.version == __import__("cn_stock_mcp").__version__
