# app/modules/m5_logistics/forward_logistics.py
#
# Section 3.21 — Forward Logistics
#
# Triggered when:
#   urgency_score > 0.6 AND sentiment == POSITIVE AND
#   (LOW_STOCK in pain_points OR sales_velocity_ratio > 1.2)
#
# Also fires on:
#   SEASONAL_MISMATCH with incoming demand spike
#
# Output:
#   restock_quantity, projected_revenue_recovery

import math

from app.decision_engine.unified_signal import UnifiedSignal
from inventory_painpoints_service.app.inventory_policy.replenishment import (
    PolicyParams, order_up_to,
)

# Restock safety factor — build plan default 1.3
RESTOCK_SAFETY_FACTOR = 1.3


def compute_forward_logistics(
    signal: UnifiedSignal,
    product_info: dict,
) -> dict:
    """
    Computes restock recommendation for a product.

    product_info dict needs:
        cost_price, base_selling_price, name

    Returns recommendation dict with:
        action          : "RESTOCK"
        restock_quantity: units to order
        trigger_reason  : why forward logistics fired
        projected_impact: expected revenue
    """

    # ── Restock quantity formula (Section 3.21) ───────────────────────────────
    # restock_quantity = demand_forecast_7d * safety_factor - current_stock
    # If tft_forecast_7d is null → use rolling_sales_7d as fallback

    demand_7d = signal.tft_forecast_7d or 0.0
    if signal.forecast_7d_p90 is not None:
        # Forecast-driven order-up-to policy (see inventory_policy/replenishment.py for the
        # assumptions: placeholder lead time, no open purchase orders, no MOQ).
        params = PolicyParams()
        lead = product_info.get("lead_time_days", params.lead_time_days)
        pol = order_up_to(demand_7d, max(signal.forecast_7d_p90, demand_7d),
                          lead, params.review_period_days)
        raw = max(0.0, pol["order_up_to"] - signal.current_stock)
        shelf = product_info.get("shelf_life_days")
        if shelf:   # cannot usefully order more than can sell within shelf life
            raw = min(raw, demand_7d / 7.0 * shelf)
        restock_quantity = int(math.ceil(raw - 1e-9))
        method = "order_up_to_p90"
    else:
        restock_quantity = max(0, round(
            (demand_7d * RESTOCK_SAFETY_FACTOR) - signal.current_stock
        ))
        method = "legacy_safety_factor"
        pol = None

    # ── Trigger reason ────────────────────────────────────────────────────────
    reasons = []
    if "LOW_STOCK" in signal.pain_points:
        reasons.append("LOW_STOCK pain point detected")
    if signal.sales_velocity > 1.2:
        reasons.append(f"sales_velocity_ratio={signal.sales_velocity:.2f} > 1.2 (accelerating)")
    if signal.urgency_score > 0.6 and signal.news_sentiment == "POSITIVE":
        reasons.append(f"positive news urgency={signal.urgency_score:.2f}")
    if "SEASONAL_MISMATCH" in signal.pain_points:
        reasons.append("seasonal demand spike incoming")

    # ── Projected impact ──────────────────────────────────────────────────────
    base_price = product_info.get("base_selling_price", 0)
    cost_price = product_info.get("cost_price", 0)

    projected_revenue    = round(restock_quantity * base_price, 2)
    projected_cost       = round(restock_quantity * cost_price, 2)
    projected_margin     = round(projected_revenue - projected_cost, 2)

    return {
        "action":            "RESTOCK",
        "direction":         "FORWARD",
        "restock_quantity":  restock_quantity,
        "restock_method":    method,
        "order_up_to_level": round(pol["order_up_to"], 1) if pol else None,
        "safety_stock":      round(pol["safety_stock"], 1) if pol else None,
        "demand_forecast_7d":round(demand_7d, 2),
        "current_stock":     signal.current_stock,
        "reorder_level":     signal.reorder_level,
        "trigger_reason":    reasons,
        "recommended_value": {
            "quantity":          restock_quantity,
            "supplier":          "nearest_supplier",   # M8 dashboard fills this
        },
        "projected_impact": {
            "projected_revenue": projected_revenue,
            "projected_cost":    projected_cost,
            "projected_margin":  projected_margin,
            "units_to_restock":  restock_quantity,
        },
    }
