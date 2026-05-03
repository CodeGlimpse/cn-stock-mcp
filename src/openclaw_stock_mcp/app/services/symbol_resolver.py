from __future__ import annotations

from openclaw_stock_mcp.app.models.instrument import Instrument
from openclaw_stock_mcp.app.services.normalizer import Normalizer


class SymbolResolver:
    def __init__(self) -> None:
        self.normalizer = Normalizer()

    def infer_sec_type(self, raw: str) -> str:
        symbol = self.normalizer.normalize_symbol(raw)
        return self._infer_sec_type(symbol)

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
        if symbol.endswith(".BK") or symbol.endswith(".BKZS") or symbol.startswith("PRIMARY:"):
            return "sector"

        code = symbol.split(".", 1)[0]
        exchange = symbol.split(".", 1)[1] if "." in symbol else ""

        if self._looks_like_index_symbol(code, exchange):
            return "index"

        if self._looks_like_fund_symbol(code, exchange):
            return "fund"

        return "stock"

    def _looks_like_index_symbol(self, code: str, exchange: str) -> bool:
        if exchange == "SH" and code.startswith("000"):
            return True
        if exchange == "SZ" and code.startswith("399"):
            return True
        if exchange == "BJ" and code.startswith("899"):
            return True
        return False

    def _looks_like_fund_symbol(self, code: str, exchange: str) -> bool:
        if exchange == "SH" and code.startswith(("50", "51", "56", "58")):
            return True
        if exchange == "SZ" and code.startswith(("15", "16")):
            return True
        return False
