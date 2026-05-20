from __future__ import annotations

from pydantic import BaseModel, Field


class FuturesSpotItem(BaseModel):
    """A single futures contract real-time quote."""

    symbol: str
    exchange: str | None = None
    name: str | None = None
    price: float | None = None                     # 最新价
    settlement: float | None = None                  # 结算价
    prev_settlement: float | None = None             # 前结算价
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None                      # 成交量
    position: float | None = None                     # 持仓量
    change_percent: float | None = None               # 涨跌幅%
    trade_date: str | None = None
    tick_time: str | None = None


class FuturesHistItem(BaseModel):
    """A single futures daily bar."""

    date: str
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None
    position: float | None = None                     # 持仓量
    settle: float | None = None                        # 结算价


class OptionContractItem(BaseModel):
    """A single option contract from SSE/SZSE."""

    code: str                                          # 合约编码
    contract_code: str | None = None                  # 合约交易代码
    name: str | None = None                           # 合约简称
    underlying: str | None = None                     # 标的
    option_type: str | None = None                    # 认购/认沽
    strike: float | None = None                       # 行权价
    unit: int | None = None                           # 合约单位
    expire_date: str | None = None                    # 到期日
    exchange: str | None = None                       # SSE/SZSE
    # SZSE-only fields
    upper_limit: float | None = None                  # 涨停价格
    lower_limit: float | None = None                  # 跌停价格
    prev_settle: float | None = None                  # 前结算价
    total_position: float | None = None               # 合约总持仓


class QVIXItem(BaseModel):
    """A data point in the QVIX implied volatility index."""

    date: str
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None


class DerivativesDataResult(BaseModel):
    """Full result for derivatives_data tool."""

    futures_spot: list[FuturesSpotItem] = Field(default_factory=list)
    futures_spot_count: int = 0
    futures_hist: list[FuturesHistItem] = Field(default_factory=list)
    futures_hist_count: int = 0
    option_list: list[OptionContractItem] = Field(default_factory=list)
    option_list_count: int = 0
    qvix: list[QVIXItem] = Field(default_factory=list)
    qvix_count: int = 0
    summary: str = ""
    source: str = "akshare"
