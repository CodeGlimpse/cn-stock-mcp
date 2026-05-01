from __future__ import annotations

from openclaw_stock_mcp.infra.time_utils import detect_board, normalize_symbol


class Normalizer:
    def normalize_symbol(self, raw: str, exchange: str | None = None) -> str:
        return normalize_symbol(raw, exchange)

    def detect_board(self, symbol: str, sec_type: str) -> str | None:
        return detect_board(symbol, sec_type)
