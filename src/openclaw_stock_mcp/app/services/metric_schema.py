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

SENTIMENT_SCORE_MIN = -5.0
SENTIMENT_SCORE_MAX = 5.0
SENTIMENT_SCORE_NEUTRAL = 0.0
SENTIMENT_NORMALIZED_MIN = 0.0
SENTIMENT_NORMALIZED_MAX = 100.0
SENTIMENT_NORMALIZED_NEUTRAL = 50.0
SENTIMENT_SCORE_SCHEMA_NAME = "sentiment_temperature_v1"

SENTIMENT_SCORE_SCHEMA = {
    "schema": SENTIMENT_SCORE_SCHEMA_NAME,
    "score": {
        "min": SENTIMENT_SCORE_MIN,
        "max": SENTIMENT_SCORE_MAX,
        "neutral": SENTIMENT_SCORE_NEUTRAL,
        "higher_is_stronger": True,
        "unit": "heuristic_point",
    },
    "normalized_score": {
        "min": SENTIMENT_NORMALIZED_MIN,
        "max": SENTIMENT_NORMALIZED_MAX,
        "neutral": SENTIMENT_NORMALIZED_NEUTRAL,
        "higher_is_stronger": True,
        "unit": "percent",
    },
    "label_thresholds": {
        "hot": "score >= 3.0",
        "warm": "1.5 <= score < 3.0",
        "neutral": "-1.0 < score < 1.5",
        "cool": "-2.5 < score <= -1.0",
        "cold": "score <= -2.5",
    },
}

REVIEW_ENVELOPE_SCHEMA = {
    "schema": "review_envelope_v1",
    "top_level_fields": [
        "subject_type",
        "subject_name",
        "mode",
        "trade_date",
        "requested_trade_date",
        "start_date",
        "end_date",
        "member_count",
        "reviewed_count",
        "breadth",
        "stats",
        "sentiment",
        "benchmark_summary",
        "continuity",
        "rotation",
        "structure",
        "leaders",
        "laggards",
        "rankings",
        "buckets",
        "items",
        "summary",
        "partial_failure",
        "errors",
        "meta",
    ],
    "item_fields": [
        "symbol",
        "name",
        "mode",
        "trade_date",
        "start_date",
        "end_date",
        "close",
        "relative_strength",
        "return",
        "max_drawdown",
        "volume_ratio",
        "tags",
        "benchmark",
        "stats",
        "summary",
        "source",
    ],
    "not_applicable_policy": "When a field does not apply to a subject type, return null, empty list, or applicable=false instead of omitting the key.",
}


def clamp_sentiment_score(score: float) -> float:
    value = float(score)
    if value < SENTIMENT_SCORE_MIN:
        return SENTIMENT_SCORE_MIN
    if value > SENTIMENT_SCORE_MAX:
        return SENTIMENT_SCORE_MAX
    return value



def sentiment_label(score: float) -> tuple[str, str]:
    if score >= 3.0:
        return "hot", "偏热"
    if score >= 1.5:
        return "warm", "偏强"
    if score > -1.0:
        return "neutral", "中性"
    if score > -2.5:
        return "cool", "偏弱"
    return "cold", "偏冷"



def normalize_sentiment_score(score: float) -> float:
    clamped = clamp_sentiment_score(score)
    return ((clamped - SENTIMENT_SCORE_MIN) / (SENTIMENT_SCORE_MAX - SENTIMENT_SCORE_MIN)) * 100.0



def build_sentiment_payload(score: float) -> dict:
    canonical_score = round(clamp_sentiment_score(score), 2)
    label, label_zh = sentiment_label(canonical_score)
    return {
        "score": canonical_score,
        "normalized_score": round(normalize_sentiment_score(canonical_score), 2),
        "label": label,
        "label_zh": label_zh,
        "score_semantics": SENTIMENT_SCORE_SCHEMA_NAME,
    }
