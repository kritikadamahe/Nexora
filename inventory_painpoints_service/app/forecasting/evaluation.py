"""Chronological backtest: trained model vs. baselines.

Protocol
--------
* Data are split strictly by time. For a block of test origins starting at day `te0`,
  the model is trained only on origins `t` whose target window is completely observed
  *before* `te0` (t + horizon < te0). Features of a test origin use data <= that origin.
* Rolling-origin: three consecutive 4-week test blocks (expanding training window,
  retrained for every block). The last 12 weeks of data are therefore all out-of-sample.
* Hyper-parameters are fixed in `ModelConfig` and were chosen on a validation window that
  ends before the first test block (see README); they are not tuned on test data.
* Metrics are computed on units of demand over the next 7 days per (product, store).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .baselines import nexora_heuristic, simple_baselines
from .features import MIN_HISTORY_DAYS, build_features
from .model import DemandForecaster, ModelConfig
from .panel import DemandPanel, build_daily_panel

HORIZON = 7
TEST_DAYS = 84
BLOCK_DAYS = 28


# ───────────────────────────── metrics ──────────────────────────────────────

def point_metrics(y, f) -> dict:
    y, f = np.asarray(y, float), np.asarray(f, float)
    err = f - y
    return {
        "n": int(len(y)),
        "WAPE": float(np.abs(err).sum() / y.sum()),
        "MAE": float(np.abs(err).mean()),
        "RMSE": float(np.sqrt((err ** 2).mean())),
        "bias_pct": float(err.sum() / y.sum()),      # >0 over-forecast, <0 under-forecast
    }


def interval_metrics(y, q, tau=0.9) -> dict:
    y, q = np.asarray(y, float), np.asarray(q, float)
    d = y - q
    pinball = np.maximum(tau * d, (tau - 1) * d)
    return {"coverage": float((y <= q).mean()), "target_coverage": tau,
            "pinball_loss": float(pinball.mean())}


def _series_wape_median(df, col) -> float:
    g = df.assign(_e=(df[col] - df["y_h"]).abs()).groupby(["product_id", "store_id"])
    s = g["_e"].sum() / g["y_h"].sum().replace(0, np.nan)
    return float(s.median())


def bootstrap_wape_diff(df, col_a, col_b, n_boot=1000, seed=0):
    """CI of WAPE(a) - WAPE(b), resampling whole products (clusters) with replacement."""
    rng = np.random.default_rng(seed)
    g = df.groupby(["product_id", "store_id"])
    ea = g.apply(lambda d: (d[col_a] - d["y_h"]).abs().sum(), include_groups=False).to_numpy()
    eb = g.apply(lambda d: (d[col_b] - d["y_h"]).abs().sum(), include_groups=False).to_numpy()
    ys = g["y_h"].sum().to_numpy()
    n = len(ys)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        diffs[i] = (ea[idx].sum() - eb[idx].sum()) / ys[idx].sum()
    point = (ea.sum() - eb.sum()) / ys.sum()
    return float(point), float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))


# ───────────────────────────── splitting ────────────────────────────────────

def make_folds(n_days: int, test_days: int = TEST_DAYS, block: int = BLOCK_DAYS,
               horizon: int = HORIZON) -> list:
    """List of dicts with train_last_origin and test origin range (day indices)."""
    first = n_days - test_days
    last_origin = n_days - horizon - 1       # last origin whose target is fully observed
    folds = []
    start = first
    while start <= last_origin:
        end = min(start + block - 1, last_origin)
        folds.append({"test_start": start, "test_end": end,
                      "train_last_origin": start - horizon - 1})
        start += block
    return folds


# ───────────────────────────── backtest ─────────────────────────────────────

def category_codes_for(panel: DemandPanel, products_df: pd.DataFrame) -> np.ndarray:
    cat = products_df.set_index("product_id")["category"].astype("category").cat.codes
    return panel.keys["product_id"].map(cat).fillna(-1).astype(int).to_numpy()


def run_backtest(sales_df: pd.DataFrame, products_df: pd.DataFrame,
                 config: ModelConfig | None = None, include_heuristic: bool = True):
    """Returns (predictions_df, metrics_df, extras). predictions_df has one row per test origin/series."""
    panel = build_daily_panel(sales_df)
    codes = category_codes_for(panel, products_df)
    cfg = config or ModelConfig()
    feats = build_features(panel, list(range(MIN_HISTORY_DAYS - 1, panel.n_days)), codes,
                           use_festival=True)
    folds = make_folds(panel.n_days)

    # model variants: full, and the same model without the festival calendar (ablation)
    nofest_cfg = ModelConfig(use_festival=False, use_category=cfg.use_category,
                             max_iter=cfg.max_iter, learning_rate=cfg.learning_rate,
                             max_leaf_nodes=cfg.max_leaf_nodes,
                             min_samples_leaf=cfg.min_samples_leaf,
                             random_state=cfg.random_state)
    parts = []
    for k, fo in enumerate(folds, start=1):
        train = feats[(feats["origin_idx"] <= fo["train_last_origin"]) & feats["y_h"].notna()]
        test = feats[(feats["origin_idx"] >= fo["test_start"]) &
                     (feats["origin_idx"] <= fo["test_end"]) & feats["y_h"].notna()].copy()
        # explicit leakage guard: every training target window ends before the test block
        assert train["origin_idx"].max() + HORIZON < fo["test_start"]
        pred = DemandForecaster(cfg).fit(train).predict(test)
        test["gbm"] = pred["forecast_7d"].to_numpy()
        test["gbm_p90"] = pred["forecast_7d_p90"].to_numpy()
        test["gbm_no_calendar"] = DemandForecaster(nofest_cfg).fit(train).predict(test)[
            "forecast_7d"].to_numpy()
        for name, v in simple_baselines(test).items():
            test[name] = v
        if include_heuristic:
            test["nexora_heuristic"] = nexora_heuristic(sales_df, test)
        test["fold"] = k
        parts.append(test)
    preds = pd.concat(parts, ignore_index=True)

    methods = ["naive_last_7d", "moving_avg_28d", "moving_avg_91d"]
    if include_heuristic:
        methods.append("nexora_heuristic")
    methods += ["gbm_no_calendar", "gbm"]
    rows = []
    for fold_label, sub in [("pooled", preds)] + [(f"fold{k}", preds[preds["fold"] == k])
                                                  for k in sorted(preds["fold"].unique())]:
        for m in methods:
            rows.append({"fold": fold_label, "method": m, **point_metrics(sub["y_h"], sub[m]),
                         "median_series_WAPE": _series_wape_median(sub, m)})
    metrics = pd.DataFrame(rows)

    extras = {"folds": folds,
              "interval_p90": interval_metrics(preds["y_h"], preds["gbm_p90"]),
              "n_series": int(panel.n_series),
              "panel_dates": [str(panel.dates[0].date()), str(panel.dates[-1].date())]}
    # volume tiers by trailing level at the origin
    tiers = pd.qcut(preds["m28"].rank(method="first"), 3, labels=["low", "mid", "high"])
    extras["wape_by_volume_tier"] = {
        t: {m: point_metrics(preds.loc[tiers == t, "y_h"], preds.loc[tiers == t, m])["WAPE"]
            for m in methods} for t in ["low", "mid", "high"]}
    best_base = min([m for m in methods if m not in ("gbm", "gbm_no_calendar")],
                    key=lambda m: metrics[(metrics.fold == "pooled") & (metrics.method == m)]["WAPE"].iloc[0])
    extras["best_baseline"] = best_base
    extras["paired_bootstrap_WAPE_diff"] = {}
    for other in [best_base] + (["nexora_heuristic"] if include_heuristic and best_base != "nexora_heuristic" else []):
        d, lo, hi = bootstrap_wape_diff(preds, "gbm", other)
        extras["paired_bootstrap_WAPE_diff"][f"gbm_minus_{other}"] = {"diff": d, "ci95": [lo, hi]}
    return preds, metrics, extras


def write_report(metrics: pd.DataFrame, extras: dict, out_dir) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(out / "forecast_metrics.csv", index=False)
    (out / "forecast_extras.json").write_text(json.dumps(extras, indent=2, default=str))
