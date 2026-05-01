from pydantic import BaseModel, Field


class OrderBookLevel(BaseModel):
    price: float | None = None
    volume: float | None = None


class OrderBook(BaseModel):
    symbol: str
    timestamp: str | None = None
    bids: list[OrderBookLevel] = Field(default_factory=list)
    asks: list[OrderBookLevel] = Field(default_factory=list)
    source: str
