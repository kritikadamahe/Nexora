"""Tests for the Decision Engine: scoring, routing, conflicts, end-to-end, outputs."""
import asyncio
import json

import pandas as pd
import pytest

from conftest import PRODUCTS_CSV, StubProvider, POSITIVE_MENTIONS, run_quiet
from app.decision_engine.unified_signal import UnifiedSignal, build_unified_signal
from app.decision_engine.priority_score import compute_action_priority_score
from app.decision_engine.routing_rules import determine_action_types
from app.decision_engine.conflict_resolver import resolve_conflicts

RESPONSE_KEYS = {
    "product_id", "product_name", "store_id", "run_at", "elapsed_ms",
    "composite_risk_score", "action_priority_score", "pain_points", "urgency_score",
    "news_sentiment", "days_to_expiry", "current_stock", "sales_velocity_ratio",
    "return_rate_30d", "skipped", "action_types", "conflicts_resolved",
    "conflict_log", "recommendations",
}
RECOMMENDATION_COLUMNS = [
    "product_id", "store_id", "product_name", "created_at", "action_type", "module",
    "action_priority_score", "pain_points_triggered", "recommended_value", "reason_json",
    "rationale", "projected_impact", "acted_on", "outcome_json",
]


def make_signal(**kw):
    base = dict(product_id=1, store_id=1, composite_risk_score=0.0, pain_points=[],
                sales_velocity=1.0, days_to_expiry=9999, return_rate_30d=0.0,
                current_stock=100, reorder_level=20, tft_forecast_7d=70.0,
                urgency_score=0.0, news_sentiment="NEUTRAL")
    base.update(kw)
    return UnifiedSignal(**base)


# --- priority score (Build Plan 3.5.5) -----------------------------------------

def test_priority_score_formula():
    s = make_signal(composite_risk_score=0.5, urgency_score=0.4,
                    days_to_expiry=10, return_rate_30d=0.1)
    # expiry_urgency = 1 - 10/100 = 0.9
    expected = 0.35 * 0.5 + 0.30 * 0.4 + 0.20 * 0.9 + 0.15 * 0.1
    assert compute_action_priority_score(s, shelf_life_days=100) == pytest.approx(expected)


def test_priority_score_non_perishable_has_no_expiry_term():
    s = make_signal(composite_risk_score=1.0, urgency_score=1.0, return_rate_30d=1.0)
    assert compute_action_priority_score(s, shelf_life_days=9999) == pytest.approx(0.35 + 0.30 + 0.15)


def test_priority_score_is_clamped():
    s = make_signal(composite_risk_score=5, urgency_score=5, return_rate_30d=5, days_to_expiry=0)
    assert compute_action_priority_score(s, shelf_life_days=10) == 1.0


# --- routing rules (Build Plan 3.5.6) ------------------------------------------

@pytest.mark.parametrize("kwargs,expected", [
    (dict(urgency_score=0.1), []),                                             # rule 9: skip
    (dict(urgency_score=0.4), ["MONITOR"]),                                    # rule 8
    (dict(pain_points=["NEAR_EXPIRY"]), ["LOGISTICS", "COMBO"]),               # rule 4
    (dict(pain_points=["LOW_STOCK"], urgency_score=0.1), ["LOGISTICS"]),       # rule 5
    (dict(pain_points=["STAGNANT"], urgency_score=0.1), ["COMBO", "PRICING"]), # rule 6
    (dict(urgency_score=0.8, news_sentiment="POSITIVE", sales_velocity=1.2),
     ["LOGISTICS", "PRICING"]),                                                # rule 2
    (dict(urgency_score=0.8, news_sentiment="NEGATIVE"), ["LOGISTICS", "PRICING"]),  # rule 3
])
def test_routing_rules(kwargs, expected):
    assert determine_action_types(make_signal(**kwargs)) == expected


def test_procurement_flag_short_circuits():
    s = make_signal(pain_points=["NEAR_EXPIRY"], procurement_flag=True)
    assert determine_action_types(s) == ["ACQUIRE"]


# --- conflict resolver ------------------------------------------------------------

def test_conflict_resolver_returns_expected_shape():
    s = make_signal(pain_points=["NEAR_EXPIRY", "LOW_STOCK"])
    out = resolve_conflicts(s, ["LOGISTICS", "COMBO"])
    assert {"action_types", "conflicts_resolved", "conflict_log", "needs_reverse"} <= set(out)
    assert out["needs_reverse"] is True        # reverse wins over forward
    assert out["conflicts_resolved"] >= 1


def test_build_unified_signal_parses_json_pain_points_and_forecast_fallback():
    row = {"product_id": 3, "store_id": 1, "pain_points_triggered": '["LOW_STOCK"]',
           "tft_forecast_7d": float("nan"), "rolling_sales_7d": 12.0}
    s = build_unified_signal(row)
    assert s.pain_points == ["LOW_STOCK"]
    assert s.tft_forecast_7d == 12.0           # falls back to rolling_sales_7d


# --- end-to-end engine, legacy (v0) signal mode ---------------------------------------

def _run(engine, pid):
    return run_quiet(lambda: asyncio.run(engine.run_for_product(pid)))


def test_engine_response_schema(engine, legacy_mode):
    r = _run(engine, 106)
    assert RESPONSE_KEYS <= set(r)


@pytest.mark.parametrize("pid,pains,actions,prio", [
    (106, ["LOW_STOCK"], ["LOGISTICS"], 0.3776),               # values from the v0 run
    (93, ["NEAR_EXPIRY"], ["LOGISTICS", "COMBO"], 0.4437),
])
def test_engine_golden_decisions_match_v0(engine, legacy_mode, pid, pains, actions, prio):
    r = _run(engine, pid)
    assert r["pain_points"] == pains
    assert r["action_types"] == actions
    assert r["urgency_score"] == 0.25 and r["news_sentiment"] == "NEUTRAL"
    assert r["action_priority_score"] == pytest.approx(prio, abs=1e-3)


def test_engine_skips_product_with_no_pain_points(engine, legacy_mode):
    r = _run(engine, 1)
    assert r["skipped"] is True and r["action_types"] == []


def test_engine_unknown_product_returns_error_dict(engine, legacy_mode):
    assert "error" in _run(engine, 999999)


def test_engine_writes_recommendations_with_expected_schema(engine, legacy_mode):
    from pathlib import Path
    _run(engine, 93)
    csv =Path(engine.product_analysis_path).parent / "recommendations.csv"
    df = pd.read_csv(csv)
    assert list(df.columns) == RECOMMENDATION_COLUMNS
    assert (df["acted_on"] == False).all()                       # feedback loop not built yet
    assert {"LOGISTICS", "COMBO"} <= set(df["action_type"])
    json.loads(df.iloc[-1]["reason_json"])                       # reason_json is valid JSON


# --- the override fix, seen through the engine -----------------------------------------

def test_engine_now_receives_external_signal(engine, monkeypatch):
    """With the v0 override gone, a strong positive signal changes urgency and priority."""
    from external_signal_service import main as sig
    monkeypatch.setenv("NEXORA_EXTERNAL_SIGNAL_MODE", "synthetic")
    monkeypatch.setattr(sig, "build_provider", lambda mode: StubProvider(POSITIVE_MENTIONS()))
    r = _run(engine, 106)
    assert r["news_sentiment"] == "POSITIVE"
    assert r["urgency_score"] > 0.6
    assert r["action_priority_score"] > 0.3776 + 0.1        # > v0's 0.3776 (0.30 weight on urgency)


# --- pricing module sanity (bounds only; v0 model quality is a known research gap) ------

@pytest.mark.parametrize("urgency,path", [(0.0, "XGBOOST"), (0.8, "LLM")])
def test_pricing_respects_hard_price_bounds(engine, urgency, path):
    p = pd.read_csv(PRODUCTS_CSV).iloc[0]
    s = make_signal(product_id=int(p["id"]), pain_points=["STAGNANT"], sales_velocity=0.5,
                    urgency_score=urgency, news_sentiment="NEGATIVE")
    res = run_quiet(lambda: asyncio.run(engine.m6_pricing.run(s)))
    assert res["path"] == path
    lo, hi = p["cost_price"] * 1.02, p["base_selling_price"] * 1.5
    assert lo - 0.01 <= res["recommended_price"] <= hi + 0.01
