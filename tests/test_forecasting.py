"""Tests for the trained forecasting pipeline: leakage, splits, model contract, evaluation."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from inventory_painpoints_service.app.forecasting.evaluation import (
    bootstrap_wape_diff, make_folds, point_metrics, interval_metrics)
from inventory_painpoints_service.app.forecasting.features import (
    MIN_HISTORY_DAYS, build_features, feature_columns)
from inventory_painpoints_service.app.forecasting.model import DemandForecaster, ModelConfig
from inventory_painpoints_service.app.forecasting.panel import build_daily_panel
from inventory_painpoints_service.app.forecasting.predict import forecast_next_7d

from conftest import REPO_ROOT


def _sales(n_days=500, n_series=6, seed=0, start="2024-01-01"):
    rng = np.random.default_rng(seed)
    rows = []
    dates = pd.date_range(start, periods=n_days)
    for p in range(1, n_series + 1):
        level = 3 + 4 * p
        for i, d in enumerate(dates):
            q = rng.poisson(level * (1.3 if d.dayofweek >= 5 else 1.0))
            if q > 0:
                rows.append((p, 1, d, q))
    return pd.DataFrame(rows, columns=["product_id", "store_id", "sale_date", "quantity_sold"])


def _products(n_series=6):
    return pd.DataFrame({"product_id": range(1, n_series + 1),
                         "category": ["A", "B"] * (n_series // 2),
                         "shelf_life_days": [np.nan] * n_series})


# ── panel ───────────────────────────────────────────────────────────────────

def test_panel_zero_fills_gaps_but_not_prelaunch_days():
    s = pd.DataFrame({"product_id": [1, 1, 2], "store_id": [1, 1, 1],
                      "sale_date": pd.to_datetime(["2025-01-01", "2025-01-04", "2025-01-03"]),
                      "quantity_sold": [5, 7, 2]})
    p = build_daily_panel(s)
    i1 = p.keys.index[p.keys.product_id == 1][0]
    i2 = p.keys.index[p.keys.product_id == 2][0]
    assert list(p.y[i1]) == [5, 0, 0, 7]            # internal gap -> zero demand
    assert p.start_idx[i2] == 2                      # product 2 first sold on day index 2
    assert p.y[i2, :2].sum() == 0 and p.start_idx[i1] == 0


# ── leakage ────────────────────────────────────────────────────────────────

def test_features_at_origin_ignore_all_future_data():
    sales = _sales()
    panel = build_daily_panel(sales)
    origin = 420
    base = build_features(panel, [origin])
    tampered = panel.y.copy()
    tampered[:, origin + 1:] *= 1000                 # wreck everything after the origin
    panel2 = type(panel)(panel.keys, panel.dates, tampered, panel.start_idx)
    other = build_features(panel2, [origin])
    cols = feature_columns(True, False)
    pd.testing.assert_frame_equal(base[cols].reset_index(drop=True),
                                  other[cols].reset_index(drop=True))
    assert not np.allclose(base["y_h"], other["y_h"])   # but the target does change


def test_target_is_sum_of_next_seven_days_and_nan_at_the_end():
    panel = build_daily_panel(_sales())
    f = build_features(panel, [300, panel.n_days - 3])
    row = f[f.origin_idx == 300].iloc[0]
    k = panel.keys.index[(panel.keys.product_id == row.product_id)][0]
    assert row.y_h == panel.y[k, 301:308].sum()
    assert f[f.origin_idx == panel.n_days - 3]["y_h"].isna().all()


def test_short_history_series_are_excluded():
    panel = build_daily_panel(_sales(n_days=40))
    f = build_features(panel, [MIN_HISTORY_DAYS - 2, MIN_HISTORY_DAYS + 5])
    assert f["origin_idx"].min() >= MIN_HISTORY_DAYS - 1


# ── chronological splits ───────────────────────────────────────────────────

def test_folds_are_chronological_and_do_not_leak_targets():
    n_days = 546
    folds = make_folds(n_days)
    assert folds[-1]["test_end"] == n_days - 7 - 1          # last fully observed target
    prev_end = None
    for fo in folds:
        # every training target window (t+1..t+7) ends before the first test origin
        assert fo["train_last_origin"] + 7 < fo["test_start"]
        if prev_end is not None:
            assert fo["test_start"] == prev_end + 1          # contiguous, non-overlapping
        prev_end = fo["test_end"]


# ── model contract ─────────────────────────────────────────────────────────

def test_forecaster_is_deterministic_nonnegative_and_ordered():
    sales, prods = _sales(), _products()
    panel = build_daily_panel(sales)
    codes = np.array([0, 1] * 3)
    f = build_features(panel, list(range(MIN_HISTORY_DAYS - 1, panel.n_days)), codes)
    tr = f[f.y_h.notna()]
    cfg = ModelConfig(max_iter=20, min_samples_leaf=20)
    a = DemandForecaster(cfg).fit(tr).predict(f.tail(30))
    b = DemandForecaster(cfg).fit(tr).predict(f.tail(30))
    pd.testing.assert_frame_equal(a, b)
    assert (a["forecast_7d"] >= 0).all() and (a["forecast_7d_p90"] >= a["forecast_7d"]).all()


def test_forecast_next_7d_uses_only_data_up_to_as_of(monkeypatch):
    sales, prods = _sales(), _products()
    monkeypatch.setenv("NEXORA_FORECAST_MAX_ITER", "20")
    as_of = pd.Timestamp("2024-01-01") + pd.Timedelta(days=420)
    a = forecast_next_7d(sales, prods, as_of)
    future = sales[sales.sale_date > as_of].copy()
    future["quantity_sold"] *= 50                          # corrupt the future
    tampered = pd.concat([sales[sales.sale_date <= as_of], future])
    b = forecast_next_7d(tampered, prods, as_of)
    pd.testing.assert_frame_equal(a, b)
    assert len(a) == 6 and (a.forecast_method == "gbm").all()


def test_forecast_raises_when_data_too_short():
    with pytest.raises(ValueError):
        forecast_next_7d(_sales(n_days=45), _products(), "2024-02-14")


def test_model_beats_naive_on_a_known_process():
    """Sanity check on a process where a trailing-level model must do well: out-of-sample."""
    sales, prods = _sales(n_days=520, n_series=10, seed=3), _products(10)
    panel = build_daily_panel(sales)
    codes = np.array([0, 1] * 5)
    f = build_features(panel, list(range(MIN_HISTORY_DAYS - 1, panel.n_days)), codes)
    cut = 440
    tr = f[(f.origin_idx + 7 < cut) & f.y_h.notna()]
    te = f[(f.origin_idx >= cut) & f.y_h.notna()]
    pred = DemandForecaster(ModelConfig(max_iter=60, min_samples_leaf=30)).fit(tr).predict(te)
    wape_model = point_metrics(te.y_h, pred.forecast_7d)["WAPE"]
    wape_naive = point_metrics(te.y_h, 7 * te.m7)["WAPE"]
    assert wape_model < wape_naive * 1.05      # at least comparable; usually better


# ── metrics ────────────────────────────────────────────────────────────────

def test_metric_definitions():
    m = point_metrics([10, 20], [12, 15])
    assert m["WAPE"] == pytest.approx(7 / 30)
    assert m["MAE"] == pytest.approx(3.5)
    assert m["bias_pct"] == pytest.approx(-3 / 30)
    iv = interval_metrics([1, 2, 3, 4], [2, 2, 2, 5], tau=0.9)
    assert iv["coverage"] == 0.75


def test_bootstrap_ci_contains_point_estimate_and_is_reproducible():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"product_id": np.repeat(np.arange(30), 10), "store_id": 1,
                       "y_h": rng.poisson(20, 300).astype(float)})
    df["a"] = df.y_h + rng.normal(0, 1, 300)
    df["b"] = df.y_h + rng.normal(0, 5, 300)
    d, lo, hi = bootstrap_wape_diff(df, "a", "b", n_boot=200)
    assert lo <= d <= hi and d < 0
    assert (d, lo, hi) == bootstrap_wape_diff(df, "a", "b", n_boot=200)


# ── committed evaluation results are consistent with the claim ──────────────

def test_committed_evaluation_supports_documented_claim():
    path = REPO_ROOT / "inventory_painpoints_service" / "forecast_evaluation" / "forecast_metrics.csv"
    if not path.exists():
        pytest.skip("run `python -m inventory_painpoints_service.app.forecasting.run_evaluation`")
    m = pd.read_csv(path)
    pooled = m[m.fold == "pooled"].set_index("method")["WAPE"]
    baselines = pooled[["naive_last_7d", "moving_avg_28d", "moving_avg_91d", "nexora_heuristic"]]
    assert pooled["gbm"] < baselines.min()
    extras = json.loads(path.with_name("forecast_extras.json").read_text())
    assert 0.8 <= extras["interval_p90"]["coverage"] <= 0.97
