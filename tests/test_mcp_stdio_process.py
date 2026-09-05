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
            cwd=root,
            env={
                "PYTHONPATH": str(root / "src"),
                "CN_STOCK_MCP_CONFIG": str(tmp_path / "missing-config.json"),
            },
        )
    )

    assert result["invalid_call_error"] == "INVALID_ARGUMENT"
