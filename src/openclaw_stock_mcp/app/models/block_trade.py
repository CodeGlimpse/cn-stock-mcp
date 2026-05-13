from __future__ import annotations

from pydantic import BaseModel


class BlockTradeDailyItem(BaseModel):
    """单笔大宗交易明细"""
    trade_date: str
    symbol: str
    name: str
    price: float | None
    volume: float | None
    turnover: float | None
    buyer_broker: str | None
    seller_broker: str | None
    source: str = "akshare"


class BlockTradeDailyStatItem(BaseModel):
    """每日个股大宗交易汇总"""
    trade_date: str
    symbol: str
    name: str
    change_percent: float | None
    close_price: float | None
    trade_price: float | None
    discount_rate: float | None
    trade_count: int | None
    total_volume: float | None
    total_turnover: float | None
    turnover_to_float_cap: float | None
    source: str = "akshare"


class BlockTradeIndustryItem(BaseModel):
    """行业大宗交易汇总"""
    industry: str
    listed_count: int | None
    trade_count: int | None
    total_turnover: float | None
    avg_discount_rate: float | None
    premium_count: int | None
    discount_count: int | None
    premium_turnover: float | None
    discount_turnover: float | None
    source: str = "akshare"


class BlockTradeBrokerRankItem(BaseModel):
    """营业部大宗交易排行"""
    broker_name: str
    buy_count_1d: int | None
    avg_return_1d: float | None
    win_rate_1d: float | None
    buy_count_5d: int | None
    avg_return_5d: float | None
    win_rate_5d: float | None
    buy_count_10d: int | None
    avg_return_10d: float | None
    win_rate_10d: float | None
    buy_count_20d: int | None
    avg_return_20d: float | None
    win_rate_20d: float | None
    source: str = "akshare"


class BlockTradeActiveStockItem(BaseModel):
    """活跃大宗交易个股"""
    symbol: str
    name: str
    latest_price: float | None
    change_percent: float | None
    last_listed_date: str | None
    total_listed_count: int | None
    premium_listed_count: int | None
    discount_listed_count: int | None
    total_turnover: float | None
    avg_discount_rate: float | None
    turnover_to_float_cap: float | None
    avg_return_1d: float | None
    avg_return_5d: float | None
    avg_return_10d: float | None
    avg_return_20d: float | None
    source: str = "akshare"


class BlockTradeResult(BaseModel):
    daily_detail: list[BlockTradeDailyItem] = []
    daily_detail_count: int = 0
    daily_stat: list[BlockTradeDailyStatItem] = []
    daily_stat_count: int = 0
    industry_stat: list[BlockTradeIndustryItem] = []
    industry_stat_count: int = 0
    broker_rank: list[BlockTradeBrokerRankItem] = []
    broker_rank_count: int = 0
    active_stock: list[BlockTradeActiveStockItem] = []
    active_stock_count: int = 0
    summary: str = ""
