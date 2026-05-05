from __future__ import annotations

REVIEW_METRIC_SCHEMA = {
    "return_pct": "percentage return over configured window, computed as (last_close-base_price)/base_price*100",
    "max_drawdown_pct": "max peak-to-trough drawdown percentage within window",
    "relative_strength_pct": "instrument return_pct minus benchmark return_pct over same window",
    "volatility_pct": "population stddev of daily return percentages within window",
    "volume_ratio": "latest volume / average volume of previous lookback bars",
}

REVIEW_WINDOWS = {
    "trade_date": {
        "primary_return_window": "20d",
        "max_drawdown_window": "20d",
        "volatility_window": "20d",
        "relative_strength_window": "20d_vs_benchmark",
    },
    "range_review": {
        "primary_return_window": "effective_range",
        "max_drawdown_window": "effective_range",
        "volatility_window": "effective_range",
        "relative_strength_window": "effective_range_vs_benchmark",
    },
}
