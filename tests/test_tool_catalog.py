from cn_stock_mcp.app.services.tool_catalog import build_tool_catalog
from cn_stock_mcp.server.mcp_server import create_server


def test_every_generated_minimal_example_validates_against_its_schema():
    server = create_server(profile_override="full")

    for entry in build_tool_catalog(server):
        model = server.tools[entry["name"]].input_model
        model(**entry["minimal_example"])
