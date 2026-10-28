"""Forecast-driven replenishment recommendations.

Periodic-review order-up-to policy driven by the trained 7-day forecast:

    P  = lead_time + review_period                    protection period (days)
    mu = forecast_7d / 7 * P                          expected demand over P
    ss = max(0, p90 - p50) * sqrt(P / 7)              safety stock from the forecast spread
    S  = mu + ss                                      order-up-to level
    order = max(0, S - inventory_position), capped at what can sell within shelf life

ASSUMPTIONS (not present in the data; override via PolicyParams, nothing is invented silently)
  * lead_time_days: NOT in the dataset. Default 3 days, a placeholder. Supply real
    supplier lead times via `lead_time_by_category` or `lead_time_by_product`.
  * review_period_days = 7: replenishment is reviewed weekly, matching the forecast horizon.
  * Inventory position = on-hand stock. There is no on-order / in-transit data, so open
    purchase orders are assumed to be zero. This over-orders if POs are already open.
  * Uncertainty of demand over P scales with sqrt(P/7) (independent days). The P90-P50 gap
    comes from the forecast model's own quantile estimates (calibrated on backtest).
  * No MOQ / pack size / budget / storage-capacity constraints (not in the data).
  * Remaining stock is treated as one batch with the recorded expiry date. A new order is
    assumed to arrive with a full shelf life (shelf_life_days from products.csv).
"""
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from inventory_painpoints_service.app.core.config import OVERSTOCK_RATIO

NO_EXPIRY = 9999


@dataclass
class PolicyParams:
    lead_time_days: float = 3.0
    review_period_days: float = 7.0
    lead_time_by_category: dict = field(default_factory=dict)
    lead_time_by_product: dict = field(default_factory=dict)
    overstock_cover_days: float = OVERSTOCK_RATIO * 7     # same threshold as the pain-point config
    expiry_risk_min_fraction: float = 0.2                 # ignore trivial leftovers


def order_up_to(f50: float, f90: float, lead: float, review: float) -> dict:
    """Core arithmetic, shared by the plan, the simulation and the logistics module."""
    p = lead + review
    mu = f50 / 7.0 * p
    ss = max(0.0, f90 - f50) * np.sqrt(p / 7.0)
    return {"protection_days": p, "expected_demand_p": mu, "safety_stock": ss, "order_up_to": mu + ss}


def plan_replenishment(analysis_df: pd.DataFrame, products_df: pd.DataFrame,
                       params: Optional[PolicyParams] = None) -> pd.DataFrame:
    """analysis_df: product_analysis (needs forecast_7d, forecast_7d_p90, current_stock,
    days_to_expiry, reorder_level). products_df: needs product_id, category, shelf_life_days."""
    params = params or PolicyParams()
    need = {"forecast_7d", "forecast_7d_p90", "current_stock", "days_to_expiry"}
    missing = need - set(analysis_df.columns)
    if missing:
        raise ValueError(f"analysis table lacks columns: {sorted(missing)}")

    df = analysis_df[["product_id", "store_id", "current_stock", "reorder_level",
                      "days_to_expiry", "forecast_7d", "forecast_7d_p90"]].copy()
    prod = products_df[["product_id", "category", "shelf_life_days"]]
    df = df.merge(prod, on="product_id", how="left")

    def lead_for(r):
        if r["product_id"] in params.lead_time_by_product:
            return params.lead_time_by_product[r["product_id"]]
        return params.lead_time_by_category.get(r["category"], params.lead_time_days)
    df["lead_time_days"] = df.apply(lead_for, axis=1).astype(float)

    f50 = df["forecast_7d"].to_numpy(float)
    f90 = np.maximum(df["forecast_7d_p90"].to_numpy(float), f50)
    lead = df["lead_time_days"].to_numpy(float)
    P = lead + params.review_period_days
    daily = f50 / 7.0
    stock = df["current_stock"].to_numpy(float)

    mu = daily * P
    ss = (f90 - f50) * np.sqrt(P / 7.0)
    S = mu + ss
    df["daily_demand_forecast"] = daily
    df["days_of_cover"] = np.where(daily > 0, stock / np.where(daily > 0, daily, 1), NO_EXPIRY)
    df["safety_stock"] = ss
    df["order_up_to_level"] = S
    df["policy_reorder_point"] = daily * lead + (f90 - f50) * np.sqrt(lead / 7.0)

    # units that can be sold within the shelf life of a freshly delivered batch
    shelf = df["shelf_life_days"].to_numpy(float)
    cap = np.where(np.isnan(shelf), np.inf, daily * shelf)
    raw = np.maximum(0.0, S - stock)
    df["order_quantity"] = np.ceil(np.minimum(raw, cap) - 1e-9).astype(int)
    df["order_capped_by_shelf_life"] = raw > cap + 1e-9

    # expiry risk on the units already in stock
    dte = df["days_to_expiry"].to_numpy(float)
    finite = dte < NO_EXPIRY
    sellable = daily * np.maximum(dte, 0)
    at_risk = np.where(finite, np.maximum(0.0, stock - sellable), 0.0)
    df["expiry_at_risk_units"] = np.ceil(at_risk - 1e-9).astype(int)
    frac = np.where(stock > 0, at_risk / np.where(stock > 0, stock, 1), 0.0)

    stockout_before_arrival = (daily * lead) > stock
    expiry_flag = finite & (at_risk >= 1) & (frac >= params.expiry_risk_min_fraction)
    overstock = (df["days_of_cover"].to_numpy() > params.overstock_cover_days) & (stock > 0)

    action = np.full(len(df), "HOLD", dtype=object)
    action[df["order_quantity"].to_numpy() > 0] = "ORDER"
    action[(stockout_before_arrival) & (df["order_quantity"].to_numpy() > 0)] = "ORDER_URGENT"
    action[overstock] = "OVERSTOCK_REVIEW"
    action[expiry_flag] = "EXPIRY_RISK"
    df["action"] = action
    # do not order against stock that is already expected to expire unsold
    df.loc[df["action"].isin(["EXPIRY_RISK", "OVERSTOCK_REVIEW"]), "order_quantity"] = 0
    df["below_static_reorder_level"] = df["current_stock"] <= df["reorder_level"]
    df["stockout_before_arrival"] = stockout_before_arrival
    return df[["product_id", "store_id", "action", "order_quantity", "current_stock",
               "forecast_7d", "forecast_7d_p90", "daily_demand_forecast", "days_of_cover",
               "lead_time_days", "safety_stock", "order_up_to_level", "policy_reorder_point",
               "reorder_level", "below_static_reorder_level", "stockout_before_arrival",
               "days_to_expiry", "expiry_at_risk_units", "order_capped_by_shelf_life"]]
