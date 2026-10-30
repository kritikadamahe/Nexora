# app/modules/m5_logistics/forward_logistics.py
#
# Section 3.21 — Forward Logistics
#
# Triggered (by the routing rules, not here) when e.g. LOW_STOCK is flagged or news is
# positive with accelerating sales.
#
# The restock quantity comes from the SAME calculation as the nightly replenishment plan
# (inventory_policy.replenishment.compute_replenishment): forecast, lead time, review period,
# on-hand stock and shelf life. See that module for the policy and its assumptions.
#
# Output:
#   restock_quantity, restock_method, the full calculation inputs/assumptions
#   ("replenishment"), projected revenue/cost/margin of the order.

from app.decision_engine.unified_signal import UnifiedSignal
from inventory_painpoints_service.app.inventory_policy.replenishment import (
    BASIS_SPREAD,
    PolicyParams,
    compute_replenishment,
    resolve_lead_time,
)


def compute_forward_logistics(
    signal: UnifiedSignal,
    product_info: dict,
    params: PolicyParams = None,
) -> dict:
    """
    Computes restock recommendation for a product.

    product_info dict needs:
        cost_price, base_selling_price, name
    and optionally: category, shelf_life_days, lead_time_days (supplier lead time, if known)

    Returns recommendation dict with:
        action          : "RESTOCK" (order recommended) or "NO_RESTOCK" (no order; see
                          replenishment["action"] for why: HOLD, EXPIRY_RISK,
                          OVERSTOCK_REVIEW, INSUFFICIENT_DATA)
        restock_quantity: units to order (0 when action is NO_RESTOCK)
        replenishment   : every input, intermediate value and assumption behind the number
        trigger_reason  : why forward logistics fired
        projected_impact: expected revenue
    """
    params = params or PolicyParams()

    if "lead_time_days" in product_info and product_info["lead_time_days"] is not None:
        lead, source = product_info["lead_time_days"], "product_info"
    else:
        lead, source = resolve_lead_time(signal.product_id, product_info.get("category"), params)

    rep = compute_replenishment(
        forecast_7d=signal.tft_forecast_7d,
        forecast_7d_p90=signal.forecast_7d_p90,
        current_stock=signal.current_stock,
        lead_time_days=lead,
        review_period_days=params.review_period_days,
        forecast_method=signal.forecast_method,
        shelf_life_days=product_info.get("shelf_life_days"),
        days_to_expiry=signal.days_to_expiry,
        lead_time_source=source,
        params=params,
    )
    restock_quantity = rep["order_quantity"]
    method = ("order_up_to_p90" if rep["safety_stock_basis"] == BASIS_SPREAD
              else "order_up_to_fixed_multiplier")
    if rep["action"] == "INSUFFICIENT_DATA":
        method = "insufficient_data"

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
    if rep["stockout_before_arrival"]:
        reasons.append("forecast demand during the lead time exceeds current stock")
    if not rep["restock_recommended"]:
        reasons.append(f"no order recommended by the replenishment policy ({rep['action']})")

    # ── Projected impact ──────────────────────────────────────────────────────
    base_price = product_info.get("base_selling_price", 0)
    cost_price = product_info.get("cost_price", 0)

    projected_revenue    = round(restock_quantity * base_price, 2)
    projected_cost       = round(restock_quantity * cost_price, 2)
    projected_margin     = round(projected_revenue - projected_cost, 2)

    def r1(x):
        return None if x is None else round(x, 1)

    return {
        "action":            "RESTOCK" if rep["restock_recommended"] else "NO_RESTOCK",
        "direction":         "FORWARD",
        "restock_quantity":  restock_quantity,
        "restock_method":    method,
        "order_up_to_level": r1(rep["order_up_to_level"]),
        "safety_stock":      r1(rep["safety_stock"]),
        "demand_forecast_7d":round(signal.tft_forecast_7d or 0.0, 2),
        "current_stock":     signal.current_stock,
        "reorder_level":     signal.reorder_level,
        "trigger_reason":    reasons,
        "replenishment":     rep,
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
