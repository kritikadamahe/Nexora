"""Tests for the shared replenishment calculation and its two callers
(nightly plan and live forward logistics)."""
import asyncio
import math

import numpy as np
import pandas as pd
import pytest

from inventory_painpoints_service.app.inventory_policy.replenishment import (
    BASIS_FIXED, BASIS_SPREAD, PolicyParams, compute_replenishment, order_up_to,
    plan_replenishment, resolve_lead_time)

ORIGINAL_PLAN_COLUMNS = [
    "product_id", "store_id", "action", "order_quantity", "current_stock", "forecast_7d",
    "forecast_7d_p90", "daily_demand_forecast", "days_of_cover", "lead_time_days",
    "safety_stock", "order_up_to_level", "policy_reorder_point", "reorder_level",
    "below_static_reorder_level", "stockout_before_arrival", "days_to_expiry",
    "expiry_at_risk_units", "order_capped_by_shelf_life"]


def calc(**kw):
    base = dict(forecast_7d=70.0, forecast_7d_p90=84.0, current_stock=10, lead_time_days=3,
                review_period_days=7, forecast_method="gbm")
    base.update(kw)
    return compute_replenishment(**base)


# ── trained forecast with a genuine spread ─────────────────────────────────

def test_trained_forecast_uses_quantile_spread():
    r = calc()
    ref = order_up_to(70, 84, 3, 7)
    assert r["safety_stock_basis"] == BASIS_SPREAD and r["uncertainty_available"] is True
    assert r["safety_stock"] == pytest.approx(ref["safety_stock"])
    assert r["order_up_to_level"] == pytest.approx(ref["order_up_to"])
    assert r["order_quantity"] == math.ceil(ref["order_up_to"] - 10)
    assert r["expected_demand_protection_period"] == pytest.approx(100)
    assert r["protection_period_days"] == 10 and r["forecast_horizon_days"] == 7
    assert r["action"] == "ORDER_URGENT"        # 3 days x 10/day = 30 > 10 on hand


# ── heuristic fallback: no pretending to have uncertainty ──────────────────

def test_heuristic_fallback_uses_documented_fixed_multiplier():
    r = calc(forecast_method="heuristic_fallback", forecast_7d_p90=70.0)
    assert r["safety_stock_basis"] == BASIS_FIXED and r["uncertainty_available"] is False
    assert r["safety_stock"] == pytest.approx(30.0)          # (1.3 - 1) x 100
    assert r["order_up_to_level"] == pytest.approx(130.0)
    assert r["order_quantity"] == 120
    assert any("not a probabilistic estimate" in a for a in r["assumptions"])
    assert any("heuristic_fallback" in w for w in r["input_warnings"])


def test_fallback_method_ignores_a_p90_that_it_cannot_vouch_for():
    r = calc(forecast_method="heuristic_fallback", forecast_7d_p90=500.0)
    assert r["uncertainty_available"] is False and r["safety_stock"] == pytest.approx(30.0)


def test_multiplier_is_configurable():
    r = calc(forecast_method="heuristic_fallback", forecast_7d_p90=70.0,
             params=PolicyParams(fallback_cover_multiplier=1.0))
    assert r["safety_stock"] == 0 and r["order_quantity"] == 90


@pytest.mark.parametrize("p90", [None, float("nan"), 50.0])    # missing, NaN, below P50
def test_trained_method_without_valid_p90_falls_back_with_warning(p90):
    r = calc(forecast_7d_p90=p90)
    assert r["uncertainty_available"] is False and r["safety_stock_basis"] == BASIS_FIXED
    assert r["input_warnings"]


def test_unknown_method_trusts_a_positive_spread_only_with_a_warning():
    with_spread = calc(forecast_method=None)
    assert with_spread["uncertainty_available"] is True
    assert any("forecast_method not provided" in w for w in with_spread["input_warnings"])
    no_spread = calc(forecast_method=None, forecast_7d_p90=70.0)
    assert no_spread["uncertainty_available"] is False


# ── quantities and actions ─────────────────────────────────────────────────

def test_zero_unit_recommendation_is_not_an_order():
    r = calc(current_stock=500, forecast_7d=70, forecast_7d_p90=84)
    assert r["order_quantity"] == 0 and r["action"] in ("HOLD", "OVERSTOCK_REVIEW")
    assert r["restock_recommended"] is False
    hold = calc(current_stock=130)
    assert hold["action"] == "HOLD" and hold["order_quantity"] == 0


def test_positive_order_and_urgency_split():
    plain = calc(current_stock=60)
    assert plain["action"] == "ORDER" and plain["order_quantity"] > 0
    assert plain["stockout_before_arrival"] is False
    assert calc(current_stock=10)["action"] == "ORDER_URGENT"


def test_shelf_life_caps_the_order_and_never_goes_negative():
    r = calc(current_stock=0, shelf_life_days=2)
    assert r["order_quantity"] == 20 and r["order_capped_by_shelf_life"] is True
    assert calc(current_stock=0, shelf_life_days=None)["order_capped_by_shelf_life"] is False
    ignored = calc(current_stock=0, shelf_life_days=-5)
    assert ignored["order_quantity"] > 20 and any("shelf_life" in w for w in ignored["input_warnings"])


def test_zero_forecast_means_no_order():
    r = calc(forecast_7d=0.0, forecast_7d_p90=0.0, current_stock=5)
    assert r["order_quantity"] == 0 and np.isfinite(r["days_of_cover"])


def test_expiry_risk_and_overstock_block_orders_with_expiry_first():
    expiry = calc(current_stock=100, days_to_expiry=4)         # 10/day: 60 units cannot sell
    assert expiry["action"] == "EXPIRY_RISK" and expiry["expiry_at_risk_units"] == 60
    assert expiry["order_quantity"] == 0
    both = calc(current_stock=2000, days_to_expiry=4)           # also hugely overstocked
    assert both["action"] == "EXPIRY_RISK"                       # expiry takes precedence
    over = calc(current_stock=2000)
    assert over["action"] == "OVERSTOCK_REVIEW" and over["order_quantity"] == 0
    assert calc(current_stock=50, days_to_expiry=0)["action"] == "EXPIRY_RISK"   # expires today
    assert calc(current_stock=50, days_to_expiry=9999)["action"] != "EXPIRY_RISK"


def test_outstanding_orders_are_reported_unavailable_not_zero():
    r = calc()
    assert r["outstanding_orders_available"] is False and r["outstanding_orders_units"] is None
    assert r["inventory_position"] == r["current_stock"]
    assert any("outstanding purchase orders" in a for a in r["assumptions"])


# ── lead time ──────────────────────────────────────────────────────────────

def test_lead_time_precedence_product_then_category_then_default():
    p = PolicyParams(lead_time_days=3, lead_time_by_category={"A": 5}, lead_time_by_product={1: 9})
    assert resolve_lead_time(1, "A", p) == (9.0, "product_override")
    assert resolve_lead_time(2, "A", p) == (5.0, "category_override")
    assert resolve_lead_time(3, "B", p) == (3.0, "default_assumption")
    assert resolve_lead_time(3, None, p) == (3.0, "default_assumption")


def test_default_lead_time_is_flagged_as_a_placeholder():
    r = calc(lead_time_source="default_assumption")
    assert any("placeholder" in a for a in r["assumptions"])
    assert not any("placeholder" in a for a in calc(lead_time_source="product_override")["assumptions"])


def test_plan_applies_lead_time_overrides():
    analysis = pd.DataFrame({
        "product_id": [1, 2, 3], "store_id": 1, "current_stock": 0, "reorder_level": 5,
        "days_to_expiry": 9999, "forecast_7d": 70.0, "forecast_7d_p90": 84.0,
        "forecast_method": "gbm"})
    prods = pd.DataFrame({"product_id": [1, 2, 3], "category": ["A", "A", "B"],
                          "shelf_life_days": np.nan})
    p = PolicyParams(lead_time_by_category={"A": 5}, lead_time_by_product={1: 9})
    plan = plan_replenishment(analysis, prods, p).set_index("product_id")
    assert list(plan["lead_time_days"]) == [9.0, 5.0, 3.0]
    assert list(plan["lead_time_source"]) == ["product_override", "category_override",
                                              "default_assumption"]
    assert plan["order_quantity"].is_monotonic_decreasing


# ── invalid inputs ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("kw", [
    dict(forecast_7d=float("nan")), dict(forecast_7d=-1.0), dict(forecast_7d=float("inf")),
    dict(forecast_7d=None), dict(current_stock=-3), dict(current_stock=float("nan")),
    dict(current_stock=None), dict(lead_time_days=-1), dict(lead_time_days=float("nan")),
    dict(review_period_days=0), dict(review_period_days=float("nan"))])
def test_invalid_inputs_never_produce_an_order(kw):
    r = calc(**kw)
    assert r["action"] == "INSUFFICIENT_DATA" and r["order_quantity"] == 0
    assert r["restock_recommended"] is False and r["input_warnings"]


def test_plan_marks_invalid_rows_instead_of_crashing_or_ordering():
    analysis = pd.DataFrame({
        "product_id": [1, 2], "store_id": 1, "current_stock": [10, 10], "reorder_level": 5,
        "days_to_expiry": 9999, "forecast_7d": [70.0, float("nan")],
        "forecast_7d_p90": [84.0, 84.0], "forecast_method": "gbm"})
    prods = pd.DataFrame({"product_id": [1, 2], "category": "A", "shelf_life_days": np.nan})
    plan = plan_replenishment(analysis, prods).set_index("product_id")
    assert plan.loc[2, "action"] == "INSUFFICIENT_DATA" and plan.loc[2, "order_quantity"] == 0
    assert plan.loc[1, "order_quantity"] > 0


# ── plan structure stays compatible ────────────────────────────────────────

def test_plan_keeps_original_columns_first_and_adds_explanation_columns():
    analysis = pd.DataFrame({
        "product_id": [1], "store_id": 1, "current_stock": 10, "reorder_level": 5,
        "days_to_expiry": 9999, "forecast_7d": 70.0, "forecast_7d_p90": 84.0})
    prods = pd.DataFrame({"product_id": [1], "category": "A", "shelf_life_days": np.nan})
    plan = plan_replenishment(analysis, prods)
    assert list(plan.columns[:len(ORIGINAL_PLAN_COLUMNS)]) == ORIGINAL_PLAN_COLUMNS
    for c in ["forecast_method", "uncertainty_available", "safety_stock_basis",
              "protection_period_days", "lead_time_source", "input_warnings"]:
        assert c in plan.columns
    assert plan.loc[0, "forecast_method"] == "unspecified"      # old CSVs: stated, not guessed
    with pytest.raises(ValueError, match="forecast_7d"):
        plan_replenishment(analysis.drop(columns=["forecast_7d"]), prods)


# ── nightly plan and live forward logistics agree ──────────────────────────

def _signal(row, **kw):
    from app.decision_engine.unified_signal import build_unified_signal
    full = {"composite_risk_score": 0.2, "pain_points_triggered": "[]",
            "sales_velocity_ratio": 1.0, "return_rate_30d": 0.0, "reorder_level": 5,
            "tft_forecast_7d": row["forecast_7d"]}
    full.update(row)
    return build_unified_signal(full, **kw)


SCENARIOS = [
    dict(current_stock=10, forecast_method="gbm", forecast_7d_p90=84.0, shelf=None, dte=9999),
    dict(current_stock=60, forecast_method="gbm", forecast_7d_p90=84.0, shelf=None, dte=9999),
    dict(current_stock=10, forecast_method="heuristic_fallback", forecast_7d_p90=70.0, shelf=None, dte=9999),
    dict(current_stock=0, forecast_method="gbm", forecast_7d_p90=84.0, shelf=2.0, dte=9999),
    dict(current_stock=300, forecast_method="gbm", forecast_7d_p90=84.0, shelf=None, dte=9999),
    dict(current_stock=100, forecast_method="gbm", forecast_7d_p90=84.0, shelf=None, dte=4),
    dict(current_stock=130, forecast_method="gbm", forecast_7d_p90=84.0, shelf=None, dte=9999),
]


@pytest.mark.parametrize("sc", SCENARIOS)
def test_nightly_plan_and_live_forward_logistics_agree(sc):
    from app.modules.logistics.forward_logistics import compute_forward_logistics
    params = PolicyParams(lead_time_by_category={"A": 4})
    row = dict(product_id=1, store_id=1, current_stock=sc["current_stock"], forecast_7d=70.0,
               forecast_7d_p90=sc["forecast_7d_p90"], forecast_method=sc["forecast_method"],
               days_to_expiry=sc["dte"])
    analysis = pd.DataFrame([{**row, "reorder_level": 5}])
    shelf = np.nan if sc["shelf"] is None else sc["shelf"]
    prods = pd.DataFrame({"product_id": [1], "category": ["A"], "shelf_life_days": [shelf]})
    plan = plan_replenishment(analysis, prods, params).iloc[0]

    info = {"cost_price": 1.0, "base_selling_price": 2.0, "category": "A",
            "shelf_life_days": sc["shelf"]}
    live = compute_forward_logistics(_signal(row), info, params)
    rep = live["replenishment"]
    assert live["restock_quantity"] == plan["order_quantity"]
    assert rep["action"] == plan["action"]
    assert rep["order_up_to_level"] == pytest.approx(plan["order_up_to_level"])
    assert rep["safety_stock"] == pytest.approx(plan["safety_stock"])
    assert rep["lead_time_days"] == plan["lead_time_days"] == 4.0
    assert rep["uncertainty_available"] == plan["uncertainty_available"]
    assert live["action"] == ("RESTOCK" if plan["action"] in ("ORDER", "ORDER_URGENT") else "NO_RESTOCK")


# ── live forward logistics output ──────────────────────────────────────────

def test_forward_logistics_keeps_existing_keys_and_exposes_the_calculation():
    from app.modules.logistics.forward_logistics import compute_forward_logistics
    row = dict(product_id=1, store_id=1, current_stock=10, forecast_7d=70.0,
               forecast_7d_p90=84.0, forecast_method="gbm", days_to_expiry=9999)
    out = compute_forward_logistics(_signal(row), {"cost_price": 1.0, "base_selling_price": 2.0})
    for key in ["action", "direction", "restock_quantity", "restock_method", "order_up_to_level",
                "safety_stock", "demand_forecast_7d", "current_stock", "reorder_level",
                "trigger_reason", "recommended_value", "projected_impact"]:
        assert key in out
    assert out["restock_method"] == "order_up_to_p90" and out["action"] == "RESTOCK"
    rep = out["replenishment"]
    for key in ["forecast_method", "uncertainty_available", "lead_time_days", "lead_time_source",
                "review_period_days", "protection_period_days", "current_stock",
                "inventory_position", "outstanding_orders_available", "assumptions"]:
        assert key in rep
    assert rep["lead_time_source"] == "default_assumption"


def test_forward_logistics_zero_quantity_is_not_a_restock():
    from app.modules.logistics.forward_logistics import compute_forward_logistics
    row = dict(product_id=1, store_id=1, current_stock=130, forecast_7d=70.0,
               forecast_7d_p90=84.0, forecast_method="gbm", days_to_expiry=9999)
    out = compute_forward_logistics(_signal(row), {"cost_price": 1.0, "base_selling_price": 2.0})
    assert out["restock_quantity"] == 0 and out["action"] == "NO_RESTOCK"
    assert out["projected_impact"]["units_to_restock"] == 0
    assert any("no order recommended" in t for t in out["trigger_reason"])


def test_forward_logistics_fallback_is_labelled_not_p90():
    from app.modules.logistics.forward_logistics import compute_forward_logistics
    row = dict(product_id=1, store_id=1, current_stock=10, forecast_7d=70.0,
               forecast_7d_p90=70.0, forecast_method="heuristic_fallback", days_to_expiry=9999)
    out = compute_forward_logistics(_signal(row), {"cost_price": 1.0, "base_selling_price": 2.0})
    assert out["restock_method"] == "order_up_to_fixed_multiplier"
    assert out["replenishment"]["uncertainty_available"] is False


def test_forward_logistics_with_invalid_forecast_does_not_order():
    from app.modules.logistics.forward_logistics import compute_forward_logistics
    from app.decision_engine.unified_signal import UnifiedSignal
    sig = UnifiedSignal(product_id=1, store_id=1, composite_risk_score=0.1, pain_points=["LOW_STOCK"],
                        sales_velocity=1.0, days_to_expiry=9999, return_rate_30d=0.0,
                        current_stock=5, reorder_level=5, tft_forecast_7d=float("nan"))
    out = compute_forward_logistics(sig, {"cost_price": 1.0, "base_selling_price": 2.0})
    assert out["action"] == "NO_RESTOCK" and out["restock_quantity"] == 0
    assert out["restock_method"] == "insufficient_data"


def test_logistics_module_resolves_category_lead_time_from_products_csv(tmp_path):
    from app.modules.logistics.logistics import LogisticsModule
    csv = tmp_path / "products.csv"
    pd.DataFrame({"id": [1], "name": ["Milk"], "category": ["Dairy"], "cost_price": [1.0],
                  "base_selling_price": [2.0], "shelf_life_days": [7]}).to_csv(csv, index=False)
    module = LogisticsModule(str(csv), PolicyParams(lead_time_by_category={"Dairy": 2}))
    row = dict(product_id=1, store_id=1, current_stock=0, forecast_7d=70.0,
               forecast_7d_p90=84.0, forecast_method="gbm", days_to_expiry=9999)
    out = asyncio.run(module.run(_signal(row), needs_reverse=False))
    assert out["replenishment"]["lead_time_days"] == 2.0
    assert out["replenishment"]["lead_time_source"] == "category_override"
    assert out["replenishment"]["shelf_life_days"] == 7.0


# ── UnifiedSignal pass-through ─────────────────────────────────────────────

def test_signal_carries_forecast_method_and_preserves_expiry_today():
    from app.decision_engine.unified_signal import build_unified_signal
    base = {"product_id": 1, "store_id": 1, "tft_forecast_7d": 10.0, "forecast_7d_p90": 12.0}
    s = build_unified_signal({**base, "forecast_method": "gbm", "days_to_expiry": 0})
    assert s.forecast_method == "gbm" and s.days_to_expiry == 0       # 0 is not "no expiry"
    nan_method = build_unified_signal({**base, "forecast_method": float("nan"),
                                       "days_to_expiry": float("nan")})
    assert nan_method.forecast_method is None and nan_method.days_to_expiry == 9999
    assert build_unified_signal({**base, "days_to_expiry": -3}).days_to_expiry == -3
    missing = build_unified_signal({"product_id": 1, "store_id": 1, "rolling_sales_7d": 9.0})
    assert missing.forecast_method == "rolling_sales_fallback" and missing.tft_forecast_7d == 9.0
