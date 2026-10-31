"""Stage 2: explanations, decision-API fields and forecast-aware routing."""
import asyncio
import json

import numpy as np
import pandas as pd
import pytest

from conftest import PRODUCTS_CSV, run_quiet
from app.decision_engine.routing_rules import determine_action_types
from app.decision_engine.unified_signal import UnifiedSignal
from app.modules.m7_xai.reason_builder import build_evidence, build_reasoning
from inventory_painpoints_service.app.inventory_policy.replenishment import (
    PolicyParams, compute_replenishment, explain_replenishment, plan_replenishment)


def rep(**kw):
    base = dict(forecast_7d=70.0, forecast_7d_p90=84.0, current_stock=10, lead_time_days=3,
                review_period_days=7, forecast_method="gbm", lead_time_source="default_assumption")
    base.update(kw)
    return compute_replenishment(**base)


def signal(**kw):
    base = dict(product_id=1, store_id=1, composite_risk_score=0.1, pain_points=[],
                sales_velocity=1.0, days_to_expiry=9999, return_rate_30d=0.0, current_stock=100,
                reorder_level=5, tft_forecast_7d=70.0, urgency_score=0.25, news_sentiment="NEUTRAL")
    base.update(kw)
    return UnifiedSignal(**base)


# ── explain_replenishment ──────────────────────────────────────────────────

def test_explanation_for_an_order_states_the_real_numbers_and_assumptions():
    r = rep()
    text = explain_replenishment(r)
    assert f"{r['order_quantity']} units" in text and "Recommended restock" in text
    assert "70 units over the next 7 days" in text and "trained demand model" in text
    assert "3-day lead time" in text and "placeholder assumption" in text
    assert "outstanding orders" in text and "assumed to be zero" in text
    assert f"order-up-to level {r['order_up_to_level']:.0f}" in text
    assert "P90" in text and "stock-out is expected" in text       # urgent: stock < lead demand


def test_explanation_does_not_call_a_fallback_probabilistic():
    text = explain_replenishment(rep(forecast_method="heuristic_fallback", forecast_7d_p90=70.0))
    assert "P90" not in text
    assert "fixed 30% of expected demand" in text and "not a probabilistic estimate" in text
    assert "heuristic fallback (not a trained forecast)" in text


def test_explanation_for_no_restock_cases_says_why():
    assert "already meets the order-up-to level" in explain_replenishment(rep(current_stock=130))
    assert "expire" in explain_replenishment(rep(current_stock=100, days_to_expiry=4))
    assert "overstock threshold" in explain_replenishment(rep(current_stock=2000))
    bad = explain_replenishment(rep(forecast_7d=float("nan")))
    assert "could not run" in bad and "forecast_7d" in bad
    capped = explain_replenishment(rep(current_stock=0, shelf_life_days=2))
    assert "capped" in capped and "2-day shelf life" in capped
    assert "placeholder" not in explain_replenishment(rep(lead_time_source="product_override"))


# ── reason_builder ─────────────────────────────────────────────────────────

def _forward_result(**kw):
    r = rep(**kw)
    return {"direction": "FORWARD", "action": "RESTOCK" if r["restock_recommended"] else "NO_RESTOCK",
            "restock_quantity": r["order_quantity"], "demand_forecast_7d": 70.0,
            "trigger_reason": ["LOW_STOCK pain point detected"], "replenishment": r}


def test_reasoning_reports_no_restock_instead_of_a_hard_coded_restock():
    out = build_reasoning("LOGISTICS", _forward_result(current_stock=130), signal())
    assert out["action_chosen"] == "NO_RESTOCK" and out["restock_quantity"] == 0
    assert out["replenishment_action"] == "HOLD"
    yes = build_reasoning("LOGISTICS", _forward_result(), signal())
    assert yes["action_chosen"] == "RESTOCK" and yes["restock_quantity"] > 0


def test_reasoning_exposes_calculation_assumptions_and_explanation():
    out = build_reasoning("LOGISTICS", _forward_result(), signal())
    calc = out["calculation"]
    for k in ["forecast_method", "uncertainty_available", "lead_time_days", "lead_time_source",
              "review_period_days", "protection_period_days", "order_up_to_level",
              "inventory_position", "outstanding_orders_available"]:
        assert k in calc
    assert calc["outstanding_orders_available"] is False
    assert any("outstanding purchase orders" in a for a in out["assumptions"])
    assert out["explanation"] == explain_replenishment(_forward_result()["replenishment"])
    json.dumps(out)                                              # must be JSON-serialisable


def test_reasoning_keeps_old_shape_for_results_without_a_calculation():
    old = {"direction": "FORWARD", "restock_quantity": 40, "demand_forecast_7d": 70.0,
           "trigger_reason": []}
    out = build_reasoning("LOGISTICS", old, signal())
    assert out == {"action_chosen": "RESTOCK", "restock_quantity": 40, "demand_forecast_7d": 70.0,
                   "trigger_reasons": []}


def test_evidence_adds_forecast_fields_without_removing_any():
    ev = build_evidence(signal(forecast_method="gbm", forecast_7d_p90=84.0), [])
    for k in ["current_stock", "reorder_level", "days_to_expiry", "sales_velocity_ratio",
              "return_rate_30d", "urgency_score", "news_sentiment", "tft_forecast_7d",
              "top_shap_features"]:
        assert k in ev
    assert ev["forecast_method"] == "gbm" and ev["forecast_7d_p90"] == 84.0
    assert build_evidence(signal(), [])["forecast_7d_p90"] is None


def test_xai_rationale_for_restock_comes_from_the_calculation_not_the_llm(tmp_path, monkeypatch):
    from app.modules.m7_xai import xai as xai_mod
    monkeypatch.setattr(xai_mod, "generate_rationale",
                        lambda **kw: pytest.fail("LLM must not describe a restock calculation"))
    layer = xai_mod.XAILayer(output_path=str(tmp_path / "recs.csv"))
    rec = {"module": "M5_LOGISTICS", **_forward_result(current_stock=130)}
    out = run_quiet(layer.explain_and_save, signal(), [rec], "Test")
    assert out[0]["rationale"] == explain_replenishment(rec["replenishment"])
    assert "No restock" in out[0]["rationale"]
    saved = json.loads(out[0]["reason_json"])
    assert saved["reasoning"]["action_chosen"] == "NO_RESTOCK"


# ── routing ────────────────────────────────────────────────────────────────

def test_forecast_stockout_risk_routes_to_logistics_without_low_stock_flag():
    assert determine_action_types(signal(replenishment_action="ORDER_URGENT")) == ["LOGISTICS"]


@pytest.mark.parametrize("action", [None, "ORDER", "HOLD", "EXPIRY_RISK", "OVERSTOCK_REVIEW",
                                    "INSUFFICIENT_DATA"])
def test_only_order_urgent_adds_a_forecast_route(action):
    assert determine_action_types(signal(replenishment_action=action)) == []


def test_forecast_route_does_not_duplicate_or_override_existing_rules():
    both = determine_action_types(signal(pain_points=["LOW_STOCK"], replenishment_action="ORDER_URGENT"))
    assert both == ["LOGISTICS"]
    expiry = determine_action_types(signal(pain_points=["NEAR_EXPIRY"], replenishment_action="ORDER_URGENT"))
    assert expiry == ["LOGISTICS", "COMBO"]
    assert determine_action_types(signal(procurement_flag=True, replenishment_action="ORDER_URGENT")) == ["ACQUIRE"]


# ── engine end to end ──────────────────────────────────────────────────────

def _run(engine, pid):
    return run_quiet(lambda: asyncio.run(engine.run_for_product(pid)))


def test_engine_response_adds_forecast_block_and_keeps_existing_fields(engine, legacy_mode):
    r = _run(engine, 106)
    for k in ["product_id", "product_name", "store_id", "run_at", "elapsed_ms",
              "composite_risk_score", "action_priority_score", "pain_points", "urgency_score",
              "news_sentiment", "days_to_expiry", "current_stock", "sales_velocity_ratio",
              "return_rate_30d", "skipped", "action_types", "conflicts_resolved",
              "conflict_log", "recommendations"]:
        assert k in r
    assert set(r["forecast"]) == {"horizon_days", "forecast_7d", "forecast_7d_p90", "method",
                                  "uncertainty_available"}
    assert r["forecast"]["method"] == "gbm" and r["forecast"]["uncertainty_available"] is True
    assert r["forecast"]["forecast_7d_p90"] >= r["forecast"]["forecast_7d"]
    assert r["replenishment_action"] in {"ORDER", "ORDER_URGENT", "HOLD", "EXPIRY_RISK",
                                         "OVERSTOCK_REVIEW", "INSUFFICIENT_DATA"}
    json.dumps(r)
    rec = next(x for x in r["recommendations"] if x.get("direction") == "FORWARD")
    assert rec["xai"]["summary"] == explain_replenishment(rec["replenishment"])
    assert rec["xai"]["confidence_basis"] == "news_urgency"


def test_skipped_products_still_report_their_forecast(engine, legacy_mode):
    r = _run(engine, 1)
    assert r["skipped"] is True and r["forecast"]["method"] == "gbm"


def test_live_decision_and_nightly_plan_agree_on_the_quantity(engine, legacy_mode, analysis_df):
    products = pd.read_csv(PRODUCTS_CSV).rename(columns={"id": "product_id"})
    plan = plan_replenishment(analysis_df, products).set_index("product_id")
    checked = 0
    for pid in analysis_df.loc[analysis_df["pain_points_triggered"].str.contains("LOW_STOCK"),
                               "product_id"].head(4):
        r = _run(engine, int(pid))
        fwd = [x for x in r["recommendations"] if x.get("direction") == "FORWARD"]
        if fwd:
            assert fwd[0]["restock_quantity"] == plan.loc[pid, "order_quantity"]
            checked += 1
    assert checked >= 1


def test_forecast_stockout_reaches_the_engine_when_lead_time_is_longer(engine, legacy_mode, analysis_df):
    """With a 14-day lead time the plan flags products that are not LOW_STOCK. Live decisions
    must no longer skip them, and must agree with the plan."""
    products = pd.read_csv(PRODUCTS_CSV).rename(columns={"id": "product_id"})
    long_lead = PolicyParams(lead_time_days=14)
    plan = plan_replenishment(analysis_df, products, long_lead).set_index("product_id")
    clean = analysis_df.set_index("product_id")["pain_points_triggered"] == "[]"
    candidates = plan[(plan["action"] == "ORDER_URGENT") & clean.reindex(plan.index)].index
    assert len(candidates) > 0
    pid = int(candidates[0])
    assert _run(engine, pid)["skipped"] is True                    # default 3-day lead: not at risk
    old = engine.m5.policy_params
    engine.m5.policy_params = long_lead
    try:
        r = _run(engine, pid)
    finally:
        engine.m5.policy_params = old
    assert r["skipped"] is False and r["action_types"] == ["LOGISTICS"]
    assert r["replenishment_action"] == "ORDER_URGENT"
    fwd = r["recommendations"][0]
    assert fwd["action"] == "RESTOCK" and fwd["restock_quantity"] == plan.loc[pid, "order_quantity"]
    assert fwd["replenishment"]["lead_time_days"] == 14.0


def test_unhandled_action_type_no_longer_crashes_the_engine(engine, legacy_mode, monkeypatch):
    import app.decision_engine.engine as eng
    monkeypatch.setattr(eng, "determine_action_types", lambda s: ["ACQUIRE"])
    r = _run(engine, 106)
    assert r["recommendations"] == [] and "error" not in r
