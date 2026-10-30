"""Forecast-driven replenishment: one shared calculation for the nightly plan and live decisions.

Periodic-review order-up-to policy driven by the 7-day demand forecast:

    P  = lead_time + review_period                    protection period (days)
    mu = forecast_7d / 7 * P                          expected demand over P
    S  = mu + safety stock                            order-up-to level
    order = max(0, S - inventory_position), capped at what can sell within shelf life

Safety stock depends on what the forecast can honestly support:

  * forecast_quantile_spread  -- the forecast is from the trained model AND a valid P90 >= P50
        is available:  ss = (p90 - p50) * sqrt(P / 7).
  * fixed_multiplier_no_uncertainty -- anything else (heuristic fallback, missing or
        inconsistent P90, unknown method without a spread):  ss = (m - 1) * mu with
        m = PolicyParams.fallback_cover_multiplier (default 1.3, the build-plan restock
        factor). This is a fixed rule of thumb, NOT a probabilistic estimate, and results
        say so (`uncertainty_available=False`).

ASSUMPTIONS (not present in the data; override via PolicyParams, nothing is invented silently)
  * lead_time_days: NOT in the dataset. Default 3 days, a placeholder. Supply real
    supplier lead times via `lead_time_by_product` / `lead_time_by_category`
    (product overrides category overrides default).
  * review_period_days = 7: replenishment is reviewed weekly, matching the forecast horizon.
  * Inventory position = on-hand stock. There is no on-order / in-transit data, so open
    purchase orders are assumed to be zero. This over-orders if POs are already open.
  * Uncertainty of demand over P scales with sqrt(P/7) (independent days).
  * No MOQ / pack size / budget / storage-capacity constraints (not in the data).
  * Remaining stock is treated as one batch with the recorded expiry date. A new order is
    assumed to arrive with a full shelf life (shelf_life_days from products.csv).

Invalid inputs (missing, non-finite or negative stock/forecast/lead time, review period <= 0)
produce action INSUFFICIENT_DATA with order_quantity 0 and the reason in `input_warnings`;
they never produce an order.
"""
import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from inventory_painpoints_service.app.core.config import OVERSTOCK_RATIO

NO_EXPIRY = 9999
HORIZON_DAYS = 7
TRAINED_METHODS = frozenset({"gbm"})        # methods that provide a genuine P50/P90 spread

BASIS_SPREAD = "forecast_quantile_spread"
BASIS_FIXED = "fixed_multiplier_no_uncertainty"

ORDER_ACTIONS = ("ORDER", "ORDER_URGENT")


@dataclass
class PolicyParams:
    lead_time_days: float = 3.0
    review_period_days: float = 7.0
    lead_time_by_category: dict = field(default_factory=dict)
    lead_time_by_product: dict = field(default_factory=dict)
    overstock_cover_days: float = OVERSTOCK_RATIO * 7     # same threshold as the pain-point config
    expiry_risk_min_fraction: float = 0.2                 # ignore trivial leftovers
    fallback_cover_multiplier: float = 1.3                # used only without genuine uncertainty


def order_up_to(f50: float, f90: float, lead: float, review: float) -> dict:
    """Quantile-spread arithmetic, used by the simulation (which always has a spread)."""
    p = lead + review
    mu = f50 / 7.0 * p
    ss = max(0.0, f90 - f50) * np.sqrt(p / 7.0)
    return {"protection_days": p, "expected_demand_p": mu, "safety_stock": ss, "order_up_to": mu + ss}


def resolve_lead_time(product_id, category, params: Optional[PolicyParams] = None):
    """Returns (lead_time_days, source). Product override > category override > default."""
    params = params or PolicyParams()
    if product_id in params.lead_time_by_product:
        return float(params.lead_time_by_product[product_id]), "product_override"
    if category is not None and category in params.lead_time_by_category:
        return float(params.lead_time_by_category[category]), "category_override"
    return float(params.lead_time_days), "default_assumption"


def _num(x) -> Optional[float]:
    """float(x) if x is a finite number, else None."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _clean_method(m) -> Optional[str]:
    if m is None or (isinstance(m, float) and m != m):
        return None
    m = str(m).strip()
    return m or None


def compute_replenishment(
    *,
    forecast_7d,
    forecast_7d_p90,
    current_stock,
    lead_time_days,
    review_period_days: float = 7.0,
    forecast_method: Optional[str] = None,
    shelf_life_days=None,
    days_to_expiry=None,
    lead_time_source: str = "caller_supplied",
    params: Optional[PolicyParams] = None,
) -> dict:
    """The single replenishment calculation (used by plan_replenishment and forward logistics)."""
    params = params or PolicyParams()
    warnings = []
    method = _clean_method(forecast_method)

    f50, stock = _num(forecast_7d), _num(current_stock)
    lead, review = _num(lead_time_days), _num(review_period_days)
    problems = []
    if f50 is None or f50 < 0:
        problems.append("forecast_7d missing, non-finite or negative")
    if stock is None or stock < 0:
        problems.append("current_stock missing, non-finite or negative")
    if lead is None or lead < 0:
        problems.append("lead_time_days missing, non-finite or negative")
    if review is None or review <= 0:
        problems.append("review_period_days missing, non-finite or not positive")
    if problems:
        return _insufficient(forecast_7d, forecast_7d_p90, current_stock, lead_time_days,
                             review_period_days, method, lead_time_source, problems)

    # ── uncertainty: only claim a spread the inputs genuinely support ─────────
    f90 = _num(forecast_7d_p90)
    spread_ok = False
    if f90 is None:
        warnings.append("no valid P90 forecast: fixed-multiplier safety stock used")
    elif f90 < f50:
        warnings.append("P90 < P50 is inconsistent: spread ignored, fixed-multiplier safety stock used")
    elif method is None:
        if f90 > f50:
            spread_ok = True
            warnings.append("forecast_method not provided: P90-P50 spread taken at face value")
        else:
            warnings.append("forecast_method not provided and P90 == P50: no spread, "
                            "fixed-multiplier safety stock used")
    elif method in TRAINED_METHODS:
        spread_ok = True
    else:
        warnings.append(f"forecast_method '{method}' provides no uncertainty estimate: "
                        "fixed-multiplier safety stock used")

    P = lead + review
    daily = f50 / 7.0
    mu = daily * P
    if spread_ok:
        ss = (f90 - f50) * math.sqrt(P / 7.0)
        rop_ss = (f90 - f50) * math.sqrt(lead / 7.0)
        basis = BASIS_SPREAD
    else:
        ss = (params.fallback_cover_multiplier - 1.0) * mu
        rop_ss = (params.fallback_cover_multiplier - 1.0) * daily * lead
        basis = BASIS_FIXED
    S = mu + ss

    # ── shelf-life cap on the new order ───────────────────────────────────────
    shelf = _num(shelf_life_days)
    if shelf is not None and shelf <= 0:
        warnings.append("shelf_life_days <= 0 ignored")
        shelf = None
    raw = max(0.0, S - stock)
    cap = daily * shelf if shelf is not None else math.inf
    qty = int(math.ceil(min(raw, cap) - 1e-9))
    qty = max(qty, 0)
    capped = bool(raw > cap + 1e-9)

    # ── expiry risk on stock already held ─────────────────────────────────────
    dte = _num(days_to_expiry)
    finite_expiry = dte is not None and dte < NO_EXPIRY
    at_risk = 0.0
    if finite_expiry:
        at_risk = max(0.0, stock - daily * max(dte, 0.0))
    frac = at_risk / stock if stock > 0 else 0.0
    expiry_flag = finite_expiry and at_risk >= 1 and frac >= params.expiry_risk_min_fraction

    cover = stock / daily if daily > 0 else float(NO_EXPIRY)
    overstock = cover > params.overstock_cover_days and stock > 0
    stockout_before_arrival = daily * lead > stock

    if expiry_flag:
        action, qty = "EXPIRY_RISK", 0
    elif overstock:
        action, qty = "OVERSTOCK_REVIEW", 0
    elif qty > 0 and stockout_before_arrival:
        action = "ORDER_URGENT"
    elif qty > 0:
        action = "ORDER"
    else:
        action = "HOLD"

    assumptions = [
        f"lead_time_days={lead:g} ({lead_time_source})"
        + ("; placeholder, not supplier data" if lead_time_source == "default_assumption" else ""),
        f"review_period_days={review:g}",
        "inventory position = on-hand stock; outstanding purchase orders / in-transit stock "
        "are not available and assumed zero",
        "no MOQ, pack-size, budget or capacity constraints",
        ("safety stock from the trained model's P90-P50 spread, scaled by sqrt(protection/7)"
         if spread_ok else
         f"safety stock = ({params.fallback_cover_multiplier:g} - 1) x expected demand: a fixed "
         "multiplier, not a probabilistic estimate"),
    ]
    if shelf is not None:
        assumptions.append("a newly delivered batch is assumed to have its full shelf life")

    return {
        "action": action,
        "restock_recommended": action in ORDER_ACTIONS,
        "order_quantity": qty,
        "order_capped_by_shelf_life": capped,
        "shelf_life_days": shelf,
        "forecast_horizon_days": HORIZON_DAYS,
        "forecast_method": method,
        "forecast_7d": f50,
        "forecast_7d_p90": f90,
        "uncertainty_available": spread_ok,
        "safety_stock_basis": basis,
        "daily_demand_forecast": daily,
        "lead_time_days": lead,
        "lead_time_source": lead_time_source,
        "review_period_days": review,
        "protection_period_days": P,
        "expected_demand_protection_period": mu,
        "safety_stock": ss,
        "order_up_to_level": S,
        "policy_reorder_point": daily * lead + rop_ss,
        "current_stock": stock,
        "inventory_position": stock,
        "outstanding_orders_available": False,
        "outstanding_orders_units": None,
        "days_of_cover": cover,
        "stockout_before_arrival": bool(stockout_before_arrival),
        "days_to_expiry": dte if dte is not None else None,
        "expiry_at_risk_units": int(math.ceil(at_risk - 1e-9)) if finite_expiry else 0,
        "input_warnings": warnings,
        "assumptions": assumptions,
    }


def _insufficient(f50, f90, stock, lead, review, method, lead_source, problems) -> dict:
    return {
        "action": "INSUFFICIENT_DATA", "restock_recommended": False, "order_quantity": 0,
        "order_capped_by_shelf_life": False, "shelf_life_days": None,
        "forecast_horizon_days": HORIZON_DAYS, "forecast_method": method,
        "forecast_7d": _num(f50), "forecast_7d_p90": _num(f90),
        "uncertainty_available": False, "safety_stock_basis": None,
        "daily_demand_forecast": None, "lead_time_days": _num(lead),
        "lead_time_source": lead_source, "review_period_days": _num(review),
        "protection_period_days": None, "expected_demand_protection_period": None,
        "safety_stock": None, "order_up_to_level": None, "policy_reorder_point": None,
        "current_stock": _num(stock), "inventory_position": _num(stock),
        "outstanding_orders_available": False, "outstanding_orders_units": None,
        "days_of_cover": None, "stockout_before_arrival": False, "days_to_expiry": None,
        "expiry_at_risk_units": 0, "input_warnings": list(problems),
        "assumptions": ["no recommendation: required inputs are invalid or missing"],
    }


def plan_replenishment(analysis_df: pd.DataFrame, products_df: pd.DataFrame,
                       params: Optional[PolicyParams] = None) -> pd.DataFrame:
    """Nightly plan: applies `compute_replenishment` to every row.

    analysis_df: product_analysis (needs forecast_7d, forecast_7d_p90, current_stock,
    days_to_expiry, reorder_level; forecast_method is used when present).
    products_df: needs product_id, category, shelf_life_days."""
    params = params or PolicyParams()
    need = {"forecast_7d", "forecast_7d_p90", "current_stock", "days_to_expiry"}
    missing = need - set(analysis_df.columns)
    if missing:
        raise ValueError(f"analysis table lacks columns: {sorted(missing)}")

    cols = ["product_id", "store_id", "current_stock", "reorder_level",
            "days_to_expiry", "forecast_7d", "forecast_7d_p90"]
    if "forecast_method" in analysis_df.columns:
        cols.append("forecast_method")
    df = analysis_df[cols].copy()
    if "forecast_method" not in df.columns:
        df["forecast_method"] = None
    df = df.merge(products_df[["product_id", "category", "shelf_life_days"]],
                  on="product_id", how="left")

    rows = []
    for r in df.itertuples(index=False):
        lead, source = resolve_lead_time(r.product_id, r.category, params)
        res = compute_replenishment(
            forecast_7d=r.forecast_7d, forecast_7d_p90=r.forecast_7d_p90,
            current_stock=r.current_stock, lead_time_days=lead,
            review_period_days=params.review_period_days, forecast_method=r.forecast_method,
            shelf_life_days=r.shelf_life_days, days_to_expiry=r.days_to_expiry,
            lead_time_source=source, params=params)
        rows.append({
            "product_id": r.product_id, "store_id": r.store_id,
            "action": res["action"], "order_quantity": res["order_quantity"],
            "current_stock": r.current_stock,
            "forecast_7d": r.forecast_7d, "forecast_7d_p90": r.forecast_7d_p90,
            "daily_demand_forecast": res["daily_demand_forecast"],
            "days_of_cover": res["days_of_cover"],
            "lead_time_days": res["lead_time_days"], "safety_stock": res["safety_stock"],
            "order_up_to_level": res["order_up_to_level"],
            "policy_reorder_point": res["policy_reorder_point"],
            "reorder_level": r.reorder_level,
            "below_static_reorder_level": bool(r.current_stock <= r.reorder_level),
            "stockout_before_arrival": res["stockout_before_arrival"],
            "days_to_expiry": r.days_to_expiry,
            "expiry_at_risk_units": res["expiry_at_risk_units"],
            "order_capped_by_shelf_life": res["order_capped_by_shelf_life"],
            # additive columns: what the number rests on
            "forecast_method": res["forecast_method"] or "unspecified",
            "uncertainty_available": res["uncertainty_available"],
            "safety_stock_basis": res["safety_stock_basis"] or "none",
            "review_period_days": res["review_period_days"],
            "protection_period_days": res["protection_period_days"],
            "expected_demand_protection_period": res["expected_demand_protection_period"],
            "lead_time_source": res["lead_time_source"],
            "input_warnings": "; ".join(res["input_warnings"]) or "none",
        })
    return pd.DataFrame(rows)
