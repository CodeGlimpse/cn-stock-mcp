from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DailyDetailItem(BaseModel):
    """A single stock's dragon-tiger board entry for a trade date."""

    symbol: str
    name: str
    trade_date: str | None = None
    close: float | None = None
    change_percent: float | None = None
    net_buy_amount: float | None = None       # 龙虎榜净买额（元）
    buy_amount: float | None = None            # 龙虎榜买入额（元）
    sell_amount: float | None = None           # 龙虎榜卖出额（元）
    turnover_amount: float | None = None       # 龙虎榜成交额（元）
    market_total_amount: float | None = None   # 市场总成交额（元）
    net_buy_ratio: float | None = None         # 净买额占总成交比%
    turnover_ratio: float | None = None        # 成交额占总成交比%
    turnover_rate: float | None = None         # 换手率%
    float_market_cap: float | None = None      # 流通市值（元）
    reason: str | None = None                  # 上榜原因
    interpretation: str | None = None           # 解读（如"主力做T，成功率47%"）
    after_1d: float | None = None              # 上榜后1日涨跌%
    after_2d: float | None = None
    after_5d: float | None = None
    after_10d: float | None = None


class InstitutionItem(BaseModel):
    """Institution buy/sell statistics for a stock on the board."""

    symbol: str
    name: str
    close: float | None = None
    change_percent: float | None = None
    buy_inst_count: int | None = None          # 买方机构数
    sell_inst_count: int | None = None          # 卖方机构数
    inst_buy_total: float | None = None         # 机构买入总额（元）
    inst_sell_total: float | None = None        # 机构卖出总额（元）
    inst_net_buy: float | None = None           # 机构买入净额（元）
    market_total_amount: float | None = None
    inst_net_buy_ratio: float | None = None     # 机构净买额占总成交比%
    turnover_rate: float | None = None
    float_market_cap: float | None = None
    reason: str | None = None
    trade_date: str | None = None


class ActiveBrokerItem(BaseModel):
    """Active broker / trading desk on the board."""

    broker_name: str
    broker_code: str | None = None
    trade_date: str | None = None
    buy_count: int | None = None                # 买入个股数
    sell_count: int | None = None               # 卖出个股数
    buy_amount: float | None = None             # 买入总金额（元）
    sell_amount: float | None = None            # 卖出总金额（元）
    net_amount: float | None = None             # 总买卖净额（元）
    buy_stocks: str | None = None               # 买入股票列表（空格分隔）


class BrokerRankItem(BaseModel):
    """Broker success-rate ranking (after-listing performance)."""

    broker_name: str
    after_1d_count: int | None = None
    after_1d_avg_change: float | None = None
    after_1d_up_prob: float | None = None
    after_2d_count: int | None = None
    after_2d_avg_change: float | None = None
    after_2d_up_prob: float | None = None
    after_5d_count: int | None = None
    after_5d_avg_change: float | None = None
    after_5d_up_prob: float | None = None
    after_10d_count: int | None = None
    after_10d_avg_change: float | None = None
    after_10d_up_prob: float | None = None


class StockStatItem(BaseModel):
    """Stock's historical board statistics over a period."""

    symbol: str
    name: str
    last_listed_date: str | None = None
    close: float | None = None
    change_percent: float | None = None
    listed_count: int | None = None             # 上榜次数
    board_turnover: float | None = None         # 龙虎榜成交金额
    net_buy_amount: float | None = None         # 龙虎榜净买额
    after_1d_avg: float | None = None           # 上榜后1日平均涨跌%
    after_2d_avg: float | None = None
    after_5d_avg: float | None = None
    after_10d_avg: float | None = None


class DragonTigerResult(BaseModel):
    """Full result for dragon_tiger tool."""

    daily_detail: list[DailyDetailItem] = Field(default_factory=list)
    daily_detail_count: int = 0
    institution: list[InstitutionItem] = Field(default_factory=list)
    institution_count: int = 0
    active_broker: list[ActiveBrokerItem] = Field(default_factory=list)
    active_broker_count: int = 0
    broker_rank: list[BrokerRankItem] = Field(default_factory=list)
    broker_rank_count: int = 0
    stock_stat: list[StockStatItem] = Field(default_factory=list)
    stock_stat_count: int = 0
    summary: str = ""
    source: str = "akshare"
