"""Clearance projections must respect the product's remaining shelf life."""
import pytest

from app.decision_engine.unified_signal import UnifiedSignal
from app.modules.clearance import project_clearance
from app.modules.logistics.reverse_logistics import _compute_projected_impact
from app.modules.m7_xai.llm_narrator import _template_rationale


def _signal(stock, days_to_expiry, forecast_7d=8.58):
    return UnifiedSignal(
        product_id=93, store_id=1, composite_risk_score=0.48,
        pain_points=["NEAR_EXPIRY"], sales_velocity=1.0,
        days_to_expiry=days_to_expiry, return_rate_30d=0.0,
        current_stock=stock, reorder_level=5, tft_forecast_7d=forecast_7d,
    )


def test_item_expiring_tomorrow_cannot_recover_full_stock_value():
    # Regression: 7 units, 1 day left, ~1.5 units/day -> only 1 unit can sell.
    out = project_clearance(current_stock=7, new_daily_sales=1.52,
                            days_to_expiry=1, unit_price=199.5)
    assert out["units_sold_before_expiry"] == 1
    assert out["units_unsold_at_expiry"] == 6
    assert out["clears_before_expiry"] is False
    assert out["projected_revenue"] == pytest.approx(199.5)
    assert out["days_to_clear"] > 1  # raw clear time is still reported


def test_stock_that_clears_in_time_keeps_full_revenue():
    out = project_clearance(current_stock=6, new_daily_sales=2.0,
                            days_to_expiry=10, unit_price=50.0)
    assert out["units_sold_before_expiry"] == 6
    assert out["units_unsold_at_expiry"] == 0
    assert out["clears_before_expiry"] is True
    assert out["projected_revenue"] == pytest.approx(300.0)


def test_non_perishable_has_no_expiry_cap():
    out = project_clearance(current_stock=40, new_daily_sales=0.5,
                            days_to_expiry=9999, unit_price=10.0)
    assert out["units_unsold_at_expiry"] == 0
    assert out["projected_revenue"] == pytest.approx(400.0)


def test_expired_or_zero_demand_recovers_nothing():
    expired = project_clearance(5, 2.0, 0, 10.0)
    assert expired["projected_revenue"] == 0.0 and expired["units_unsold_at_expiry"] == 5
    no_demand = project_clearance(5, 0.0, 5, 10.0)
    assert no_demand["days_to_clear"] == 999 and no_demand["projected_revenue"] == 0.0


def test_projection_never_sells_more_than_stock():
    out = project_clearance(3, 100.0, 30, 10.0)
    assert out["units_sold_before_expiry"] == 3
    assert out["projected_revenue"] == pytest.approx(30.0)


def test_markdown_projection_is_expiry_aware():
    sig = _signal(stock=7, days_to_expiry=1)
    rec = {"suggested_price": 199.5}
    out = _compute_projected_impact("MARKDOWN", sig, cost_price=150.0,
                                    base_price=285.0, recommended_value=rec)
    assert out["clears_before_expiry"] is False
    assert out["units_unsold_at_expiry"] > 0
    assert out["projected_revenue"] < 7 * 199.5       # no longer the full-stock figure
    assert out["revenue_recovery"] == out["projected_revenue"]


def test_narrator_fallback_is_well_formed_and_flags_unsold_units():
    prompt = ("Action: MARKDOWN. Expected revenue recovery: Rs199. "
              "Units unsold at expiry: 6. Days to clear: 5.")
    text = _template_rationale(prompt)
    assert text.startswith("Recommended to MARKDOWN — ")
    assert "5. days" not in text
    assert "before expiry" in text and "about 5 days" not in text
    assert "6 unit(s)" in text


def test_narrator_fallback_without_unsold_units_has_no_warning():
    text = _template_rationale("Action: MARKDOWN. Expected revenue recovery: Rs500. "
                               "Units unsold at expiry: 0. Days to clear: 3.")
    assert "unsold" not in text and "about 3 days" in text


def test_combo_projection_is_expiry_aware():
    from app.modules.combo.combo import ComboModule
    module = ComboModule.__new__(ComboModule)          # no data load needed
    out = module._compute_projected_impact(
        _signal(stock=7, days_to_expiry=1),
        {"base_selling_price": 285.0},
        {"discount_pct": 25, "confidence_level": "LOW"},
    )
    assert out["clears_before_expiry"] is False
    assert out["projected_revenue"] < 7 * out["combo_price"]
    assert out["units_sold_before_expiry"] + out["units_unsold_at_expiry"] == 7
