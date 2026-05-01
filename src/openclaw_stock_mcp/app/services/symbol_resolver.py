from __future__ import annotations

from openclaw_stock_mcp.app.models.instrument import Instrument
from openclaw_stock_mcp.app.services.normalizer import Normalizer


class SymbolResolver:
    def __init__(self) -> None:
        self.normalizer = Normalizer()

    def resolve(self, raw: str, sec_type: str | None = None) -> Instrument:
        symbol = self.normalizer.normalize_symbol(raw)
        inferred_sec_type = sec_type or self._infer_sec_type(symbol)
        board = self.normalizer.detect_board(symbol, inferred_sec_type)
        exchange = symbol.split(".", 1)[1] if "." in symbol else None
        return Instrument(
            symbol=symbol,
            name=None,
            market="CN",
            exchange=exchange,  # type: ignore[arg-type]
            board=board,
            sec_type=inferred_sec_type,  # type: ignore[arg-type]
            raw_symbol=raw,
            source="resolver",
        )

    def _infer_sec_type(self, symbol: str) -> str:
        if symbol.endswith(".BK") or symbol.endswith(".BKZS"):
            return "sector"

        code = symbol.split(".", 1)[0]
        exchange = symbol.split(".", 1)[1] if "." in symbol else ""

        known_index_symbols = {
            "000001.SH",
            "399001.SZ",
            "399006.SZ",
            "899050.BJ",
        }
        if symbol in known_index_symbols:
            return "index"

        if exchange in {"SH", "SZ"} and code.startswith(("15", "16", "50", "51", "56", "58")):
            return "fund"

        return "stock"
