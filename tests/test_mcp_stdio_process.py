from __future__ import annotations

import sys
from functools import partial
from pathlib import Path

import anyio

from scripts.verify_mcp_stdio import verify_stdio


def test_real_stdio_subprocess_initializes_lists_and_returns_error(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    result = anyio.run(
        partial(
            verify_stdio,
            command=sys.executable,
            args=["-m", "cn_stock_mcp.main", "--stdio"],
            expected_tools=53,
            expected_version=__import__("cn_stock_mcp").__version__,
            cwd=tmp_path,
            env={
                "PYTHONPATH": str(root / "src"),
                "CN_STOCK_MCP_CONFIG": str(tmp_path / "missing-config.json"),
            },
        )
    )

    assert result["invalid_call_error"] == "INVALID_ARGUMENT"


def test_real_stdio_success_preserves_data_and_metadata(tmp_path: Path):
    """Exercise the real registry, serialization and stdio with fixture data."""
    root = Path(__file__).resolve().parents[1]
    fixture = tmp_path / "fixture_server.py"
    fixture.write_text(
        "import anyio\n"
        "from cn_stock_mcp import __version__\n"
        "from cn_stock_mcp.server import stdio_server\n"
        "from cn_stock_mcp.server.mcp_server import MCPServerStub, MCPTool\n"
        "from cn_stock_mcp.server.schemas import StockQuoteRequest\n"
        "registry = MCPServerStub(name='cn-stock-mcp', version=__version__)\n"
        "def quote(request):\n"
        "    return {'items': [{'symbol': request.symbols[0], 'price': 10.5, 'source': 'akshare', 'date': '2026-09-04'}], 'errors': [], 'partial_failure': False}\n"
        "registry.register_tool(MCPTool(name='stock_quote', description='Offline fixture quote', input_model=StockQuoteRequest, handler=quote))\n"
        "stdio_server.create_server = lambda: registry\n"
        "anyio.run(stdio_server.run_stdio_server, stdio_server.build_fastmcp_server())\n",
        encoding="utf-8",
    )
    result = anyio.run(partial(
        verify_stdio, command=sys.executable, args=[str(fixture)],
        expected_tools=1, expected_version=__import__("cn_stock_mcp").__version__,
        cwd=tmp_path,
        env={"PYTHONPATH": str(root / "src"), "CN_STOCK_MCP_CONFIG": str(tmp_path / "missing.json")},
        success_call=("stock_quote", {"symbols": ["000001.SZ"]}),
    ))
    assert result["successful_call"] == "stock_quote"
