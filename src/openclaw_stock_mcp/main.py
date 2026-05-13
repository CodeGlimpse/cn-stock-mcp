from __future__ import annotations

import argparse
import json

from openclaw_stock_mcp.infra.config import get_settings
from openclaw_stock_mcp.infra.logging import setup_logging
from openclaw_stock_mcp.server.transport import TransportApp


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)

    parser = argparse.ArgumentParser(description="openclaw-stock-mcp")
    parser.add_argument("--list-tools", action="store_true", help="List registered tools")
    parser.add_argument("--tool", type=str, help="Tool name to invoke")
    parser.add_argument("--payload", type=str, help="Inline JSON payload for tool invocation")
    parser.add_argument("--stdio", action="store_true", help="Run MCP stdio transport")
    args = parser.parse_args()

    app = TransportApp()

    if args.stdio:
        app.run_stdio()
        return

    if args.list_tools:
        print(json.dumps(app.list_tools(), ensure_ascii=False, indent=2))
        return

    if args.tool:
        payload = json.loads(args.payload or "{}")
        app.run_stdio_once(args.tool, payload)
        return

    print("openclaw-stock-mcp ready")


if __name__ == "__main__":
    main()
