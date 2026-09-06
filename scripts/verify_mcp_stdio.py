from __future__ import annotations

import argparse
import json
import os
from functools import partial
from pathlib import Path
from typing import Any

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _server_environment(extra: dict[str, str] | None = None) -> dict[str, str]:
    allowed = (
        "CN_STOCK_MCP_CONFIG",
        "PYTHONPATH",
        "PYTHONUTF8",
        "PYTHONIOENCODING",
    )
    env = {name: os.environ[name] for name in allowed if os.environ.get(name)}
    env.update(extra or {})
    return env


async def verify_stdio(
    *,
    command: str,
    args: list[str],
    expected_tools: int,
    expected_version: str,
    cwd: str | Path | None = None,
    env: dict[str, str] | None = None,
    success_call: tuple[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Launch a real MCP subprocess and verify handshake/list/call."""

    params = StdioServerParameters(
        command=command,
        args=args,
        cwd=str(cwd) if cwd is not None else None,
        env=_server_environment(env),
        encoding="utf-8",
    )
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()
            invalid = await session.call_tool("stock_quote", {"symbols": []})
            successful = await session.call_tool(*success_call) if success_call else None

    server_version = initialized.server_info.version
    if server_version != expected_version:
        raise AssertionError(f"server version {server_version!r} != {expected_version!r}")
    if len(tools.tools) != expected_tools:
        raise AssertionError(f"tool count {len(tools.tools)} != {expected_tools}")
    if not invalid.is_error:
        raise AssertionError("invalid tools/call did not return an MCP error result")
    text = "\n".join(getattr(item, "text", "") for item in invalid.content)
    if "INVALID_ARGUMENT" not in text:
        raise AssertionError("invalid tools/call did not preserve INVALID_ARGUMENT")

    if successful is not None:
        if successful.is_error:
            raise AssertionError("valid tools/call returned an MCP error")
        structured = successful.structured_content
        content = json.loads("\n".join(getattr(item, "text", "") for item in successful.content))
        if not isinstance(structured, dict) or structured.get("success") is not True or structured != content:
            raise AssertionError("valid tools/call text and structured envelopes differ")
        meta = structured.get("meta", {})
        if not structured.get("data") or not all(key in meta for key in ("freshness", "data_quality", "disclaimer")):
            raise AssertionError("valid tools/call omitted data or required metadata")

    return {
        "server": initialized.server_info.name,
        "version": server_version,
        "protocol_version": initialized.protocol_version,
        "tool_count": len(tools.tools),
        "invalid_call_error": "INVALID_ARGUMENT",
        "successful_call": success_call[0] if successful is not None else None,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Verify a real cn-stock-mcp stdio subprocess")
    parser.add_argument("--command", required=True)
    parser.add_argument("--expected-tools", type=int, required=True)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--cwd")
    parser.add_argument("--server-arg", action="append", dest="server_args")
    ns = parser.parse_args(argv)
    result = anyio.run(
        partial(
            verify_stdio,
            command=ns.command,
            args=ns.server_args or ["--stdio"],
            expected_tools=ns.expected_tools,
            expected_version=ns.expected_version,
            cwd=ns.cwd,
        )
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
