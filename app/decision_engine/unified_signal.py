# app/decision_engine/unified_signal.py
#
# Section 3.5.4 — The Unified Signal Record
#
# One UnifiedSignal per (product_id, store_id) pair.
# Created by merging M2/M4 outputs (product_analysis.csv)
# with M3 news signals (Reddit module — stubbed for now).
#
# This is an in-memory dataclass — not saved to DB directly.
# The Decision Engine processes it and writes recommendations to DB.

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UnifiedSignal:

    # ── Identity ──────────────────────────────────────────────────────────────
    product_id:             int
    store_id:               int

    # ── From M2 (product_analysis.csv) ───────────────────────────────────────
    composite_risk_score:   float          # 0..1 — overall inventory risk
    pain_points:            List[str]      # ["NEAR_EXPIRY", "LOW_STOCK"]
    sales_velocity:         float          # sales_velocity_ratio
    days_to_expiry:         int            # 9999 for non-perishables
    return_rate_30d:        float          # return rate last 30 days
    current_stock:          int
    reorder_level:          int
    tft_forecast_7d:        float          # trained 7-day forecast (legacy column name; not a TFT)

    # ── From M3 (Reddit module — stubbed as 0.0/NEUTRAL for now) ─────────────
    urgency_score:          float = 0.0   # 0..1 — external news urgency
    news_sentiment:         str   = "NEUTRAL"  # POSITIVE/NEGATIVE/NEUTRAL

    # ── Computed by Decision Engine (Section 3.5.5) ───────────────────────────
    action_priority_score:  float = 0.0   # filled by priority_score.py

    # ── Routing flags (Section 3.5.6) ─────────────────────────────────────────
    procurement_flag:       bool  = False  # True = product not in DB, found in news

    # ── From the trained demand model (None when unavailable, e.g. old CSVs) ─────────────
    forecast_7d_p90:        Optional[float] = None   # upper (P90) 7-day demand forecast
    forecast_method:        Optional[str]   = None   # "gbm", "heuristic_fallback", ... (None = unknown)

    # ── Set by the Decision Engine before routing (shared replenishment calculation) ────
    replenishment_action:   Optional[str]   = None   # ORDER_URGENT / ORDER / HOLD / ... (None = not assessed)


def build_unified_signal(row: dict, urgency_score: float = 0.0,
                         news_sentiment: str = "NEUTRAL") -> UnifiedSignal:
    """
    Builds a UnifiedSignal from a product_analysis row (dict).
    urgency_score and news_sentiment come from M3 (stubbed for now).
    """
    import json

    # Parse pain_points from JSON string
    raw_pp = row.get("pain_points_triggered", "[]")
    if isinstance(raw_pp, str):
        pain_points = json.loads(raw_pp)
    else:
        pain_points = raw_pp or []

    # tft_forecast_7d is the legacy column name for the 7-day forecast (trained model, or the
    # heuristic fallback written by the pipeline). If it is missing (very old CSVs) fall back
    # to rolling_sales_7d and say so in forecast_method.
    method = row.get("forecast_method")
    method = None if method is None or method != method else str(method)
    tft_forecast = row.get("tft_forecast_7d")
    if tft_forecast is None or (isinstance(tft_forecast, float) and tft_forecast != tft_forecast):
        tft_forecast = row.get("rolling_sales_7d", 0.0) or 0.0
        method = "rolling_sales_fallback"

    p90 = row.get("forecast_7d_p90")
    p90 = None if p90 is None or p90 != p90 else float(p90)

    return UnifiedSignal(
        product_id            = int(row["product_id"]),
        store_id              = int(row["store_id"]),
        composite_risk_score  = float(row.get("composite_risk_score") or 0.0),
        pain_points           = pain_points,
        sales_velocity        = float(row.get("sales_velocity_ratio") or 0.0),
        days_to_expiry        = _days_to_expiry(row.get("days_to_expiry")),
        return_rate_30d       = float(row.get("return_rate_30d") or 0.0),
        current_stock         = int(row.get("current_stock") or 0),
        reorder_level         = int(row.get("reorder_level") or 0),
        tft_forecast_7d       = float(tft_forecast),
        urgency_score         = urgency_score,
        news_sentiment        = news_sentiment,
        forecast_7d_p90       = p90,
        forecast_method       = method,
    )


def _days_to_expiry(value) -> int:
    """9999 = no expiry. Unlike `value or 9999`, a genuine 0 (expires today) is preserved."""
    if value is None or value != value:
        return 9999
    return int(value)
