"""Tests for the forecast-driven replenishment policy and its simulation."""
import math

import numpy as np
import pandas as pd
import pytest

from inventory_painpoints_service.app.inventory_policy.replenishment import (
    PolicyParams, order_up_to, plan_replenishment)
from inventory_painpoints_service.app.inventory_policy.simulation import simulate


def _analysis(**kw):
    base = dict(product_id=1, store_id=1, current_stock=10, reorder_level=5, days_to_expiry=9999,
                forecast_7d=70.0, forecast_7d_p90=84.0)
    base.update(kw)
    return pd.DataFrame([base])


def _products(shelf=np.nan, category="A", pid=1):
    return pd.DataFrame({"product_id": [pid], "category": [category], "shelf_life_days": [shelf]})


def test_order_up_to_arithmetic():
    r = order_up_to(70, 84, lead=3, review=7)       # P=10 -> mu=100, ss=14*sqrt(10/7)
    assert r["expected_demand_p"] == pytest.approx(100)
    assert r["safety_stock"] == pytest.approx(14 * math.sqrt(10 / 7))
    assert r["order_up_to"] == pytest.approx(100 + 14 * math.sqrt(10 / 7))


def test_p90_below_p50_never_gives_negative_safety_stock():
    assert order_up_to(70, 50, 3, 7)["safety_stock"] == 0


def test_urgent_order_when_stock_cannot_cover_lead_time():
    plan = plan_replenishment(_analysis(current_stock=10), _products())   # 10/day, L=3 -> need 30
    row = plan.iloc[0]
    assert row.action == "ORDER_URGENT" and row.stockout_before_arrival
    assert row.order_quantity == math.ceil(order_up_to(70, 84, 3, 7)["order_up_to"] - 10)


def test_plain_order_vs_hold():
    needs = plan_replenishment(_analysis(current_stock=60), _products()).iloc[0]
    assert needs.action == "ORDER" and not needs.stockout_before_arrival
    enough = plan_replenishment(_analysis(current_stock=130), _products()).iloc[0]
    assert enough.action == "HOLD" and enough.order_quantity == 0


def test_overstock_blocks_ordering():
    row = plan_replenishment(_analysis(current_stock=10 * 100), _products()).iloc[0]
    assert row.action == "OVERSTOCK_REVIEW" and row.order_quantity == 0


def test_expiry_risk_flags_stock_that_cannot_sell_before_expiry_and_blocks_order():
    # sells 10/day, 100 units, expires in 4 days -> 60 units at risk
    row = plan_replenishment(_analysis(current_stock=100, days_to_expiry=4), _products()).iloc[0]
    assert row.action == "EXPIRY_RISK"
    assert row.expiry_at_risk_units == 60 and row.order_quantity == 0


def test_already_expired_stock_is_fully_at_risk():
    row = plan_replenishment(_analysis(current_stock=50, days_to_expiry=-2), _products()).iloc[0]
    assert row.action == "EXPIRY_RISK" and row.expiry_at_risk_units == 50


def test_order_is_capped_by_shelf_life():
    # short-life item (2 days): at most 10/day * 2 = 20 units can sell in a batch's life
    row = plan_replenishment(_analysis(current_stock=0), _products(shelf=2)).iloc[0]
    assert row.order_quantity == 20 and row.order_capped_by_shelf_life


def test_zero_forecast_means_no_order_and_finite_cover():
    row = plan_replenishment(_analysis(forecast_7d=0.0, forecast_7d_p90=0.0, current_stock=5),
                             _products()).iloc[0]
    assert row.order_quantity == 0 and np.isfinite(row.days_of_cover)


def test_lead_time_override_changes_quantity():
    a = plan_replenishment(_analysis(current_stock=0), _products()).iloc[0].order_quantity
    b = plan_replenishment(_analysis(current_stock=0), _products(),
                           PolicyParams(lead_time_by_category={"A": 10})).iloc[0].order_quantity
    assert b > a


def test_missing_forecast_columns_is_a_clear_error():
    with pytest.raises(ValueError, match="forecast_7d"):
        plan_replenishment(_analysis().drop(columns=["forecast_7d"]), _products())


# ── forward logistics now uses the policy ──────────────────────────────────

def _signal(**kw):
    from app.decision_engine.unified_signal import UnifiedSignal
    base = dict(product_id=1, store_id=1, composite_risk_score=0.2, pain_points=["LOW_STOCK"],
                sales_velocity=1.0, days_to_expiry=9999, return_rate_30d=0.0, current_stock=10,
                reorder_level=5, tft_forecast_7d=70.0)
    base.update(kw)
    return UnifiedSignal(**base)


def test_forward_logistics_uses_order_up_to_when_p90_available():
    from app.modules.logistics.forward_logistics import compute_forward_logistics
    info = {"cost_price": 1.0, "base_selling_price": 2.0, "shelf_life_days": None}
    with_p90 = compute_forward_logistics(_signal(forecast_7d_p90=84.0), info)
    assert with_p90["restock_method"] == "order_up_to_p90"
    assert with_p90["restock_quantity"] == math.ceil(order_up_to(70, 84, 3, 7)["order_up_to"] - 10)
    legacy = compute_forward_logistics(_signal(), info)
    assert legacy["restock_method"] == "legacy_safety_factor"
    assert legacy["restock_quantity"] == round(70 * 1.3 - 10)


# ── simulation ─────────────────────────────────────────────────────────────

def test_simulation_with_perfect_forecast_reaches_full_fill_rate():
    T, lead = 80, 3
    y = np.full((1, T), 10.0)
    origins = list(range(30, 67, 7))
    rows = [dict(origin_idx=o, product_id=1, store_id=1, gbm=70.0, gbm_p90=70.0,
                 nexora_heuristic=70.0) for o in range(30, 70)]
    sim = simulate(y, pd.DataFrame(rows), {(1, 1): 0}, origins, 69, np.array([1.0]), lead_time=lead)
    r = sim.set_index("policy")
    assert r.loc["nexora_gbm", "fill_rate"] == pytest.approx(1.0)
    assert r.loc["nexora_gbm", "fill_rate"] >= r.loc["legacy_rule", "fill_rate"]
