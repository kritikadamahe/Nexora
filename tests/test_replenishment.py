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


# ── simulation: timing, inventory position, metrics, evaluation window ─────

def _one_series_inputs(T, first, f50=1000.0, f90=1000.0):
    """Demand 1/day up to `first` (initial stock = 14 units), then 10/day."""
    y = np.full((1, T), 10.0)
    y[:, : first + 1] = 1.0
    rows = [dict(origin_idx=o, product_id=1, store_id=1, gbm=f50, gbm_p90=f90,
                 nexora_heuristic=f50) for o in range(first, T)]
    return y, pd.DataFrame(rows)


def _gbm(sim):
    return sim.set_index("policy").loc["nexora_gbm"]


@pytest.mark.parametrize("lead, stockout_days", [(1, 0), (3, 2), (5, 4)])
def test_order_arrives_lead_time_days_after_review(lead, stockout_days):
    """Review at end of day 30; initial stock 14. Day 31 sells 10, day 32 has 4 left.
    The order is available from day 31 + lead: days 32..30+lead are short iff lead > 1."""
    first, T = 30, 50
    y, preds = _one_series_inputs(T, first)
    sim = simulate(y, preds, {(1, 1): 0}, [first], first + 8, np.array([2.0]), lead_time=lead)
    assert _gbm(sim).stockout_series_days == stockout_days


def test_metrics_match_hand_calculation():
    first, lead = 30, 3
    y, preds = _one_series_inputs(50, first)
    r = _gbm(simulate(y, preds, {(1, 1): 0}, [first], first + 8, np.array([2.0]), lead_time=lead))
    # order = ceil(1000 * 10/7 - 14) = 1415 arrives day 34. Demand 10 on days 31..38 = 80.
    # sold: 10, 4, 0, 10 x5 -> 64 of 80. End-of-day stock: 4,0,0,1405,1395,1385,1375,1365.
    assert r.fill_rate == pytest.approx(64 / 80)
    assert r.stockout_series_days == 2
    assert r.avg_on_hand_units == pytest.approx(6929 / 8)
    assert r.avg_on_hand_value_at_cost == pytest.approx(2 * 6929 / 8)


def _reference_order_up_to(y, f7, lead, review, reviews, end, p_days):
    """Independent single-series reference with an explicit inventory position."""
    first = reviews[0]
    on_hand = max(0.0, 14 * y[first - 27: first + 1].mean())
    orders = []                                   # [arrival_day, qty]
    sold_tot = dem_tot = stock_sum = 0.0
    for day in range(first + 1, end + 1):
        if day - 1 in reviews:
            position = on_hand + sum(q for a, q in orders if a >= day)   # outstanding orders
            qty = max(0.0, f7 * p_days / 7 - position)
            qty = float(np.ceil(qty - 1e-9))
            if qty > 0:
                orders.append([day + lead, qty])
        on_hand += sum(q for a, q in orders if a == day)
        sold = min(on_hand, y[day]); on_hand -= sold
        sold_tot += sold; dem_tot += y[day]; stock_sum += on_hand
    return sold_tot / dem_tot, stock_sum / (end - first)


@pytest.mark.parametrize("lead", [3, 10])     # 10 > review: orders are still in transit at review 2
def test_inventory_position_includes_outstanding_orders(lead):
    first, review, T = 30, 7, 80
    y = np.full((1, T), 10.0)
    rows = [dict(origin_idx=o, product_id=1, store_id=1, gbm=70.0, gbm_p90=70.0,
                 nexora_heuristic=70.0) for o in range(first, T)]
    reviews = [first, first + 7, first + 14]
    end = 55
    got = _gbm(simulate(y, pd.DataFrame(rows), {(1, 1): 0}, reviews, end, np.array([1.0]),
                        lead_time=lead, review=review))
    fill, avg = _reference_order_up_to(y[0], 70.0, lead, review, reviews,
                                       min(end, reviews[-1] + review + lead), lead + review)
    assert got.fill_rate == pytest.approx(fill)
    assert got.avg_on_hand_units == pytest.approx(avg)


def test_scoring_stops_where_the_last_review_stops_mattering():
    """Days beyond last_review + review + lead depend on an unsimulated review; they must not
    be scored, so extending end_idx cannot change any metric."""
    first, T = 30, 80
    y = np.full((1, T), 10.0)
    rows = [dict(origin_idx=o, product_id=1, store_id=1, gbm=70.0, gbm_p90=70.0,
                 nexora_heuristic=70.0) for o in range(first, T)]
    reviews = [first, first + 7]
    a = simulate(y, pd.DataFrame(rows), {(1, 1): 0}, reviews, first + 17, np.array([1.0]))
    b = simulate(y, pd.DataFrame(rows), {(1, 1): 0}, reviews, T - 1, np.array([1.0]))
    pd.testing.assert_frame_equal(a, b)


def test_all_policies_share_start_stock_and_window():
    """With no review before the end of the window no policy can order, so every policy must
    report identical metrics: same starting stock, same days, same demand."""
    first, T = 30, 60
    y, preds = _one_series_inputs(T, first)
    sim = simulate(y, preds, {(1, 1): 0}, [first], first + 1, np.array([1.0]), lead_time=3)
    # window is 1 day (31); the order cannot arrive within it for any policy
    assert sim["fill_rate"].nunique() == 1 and sim["avg_on_hand_units"].nunique() == 1
    assert sim["avg_on_hand_units"].iloc[0] == pytest.approx(4.0)


def test_missing_forecast_rows_raise_instead_of_silently_zeroing_a_series():
    y = np.full((2, 60), 5.0)
    rows = [dict(origin_idx=30, product_id=1, store_id=1, gbm=35.0, gbm_p90=40.0,
                 nexora_heuristic=35.0)]                    # series 2 has no forecast
    with pytest.raises(ValueError, match="every policy needs a forecast"):
        simulate(y, pd.DataFrame(rows), {(1, 1): 0, (2, 1): 1}, [30], 45, np.ones(2))


def test_scoring_end_helper_matches_simulate_window():
    from inventory_painpoints_service.app.inventory_policy.simulation import scoring_end
    assert scoring_end([30, 37], 79) == 37 + 7 + 3
    assert scoring_end([30, 37], 40) == 40          # never extends past the data
    assert scoring_end([37, 30], 79, lead_time=5) == 37 + 7 + 5   # order-insensitive
