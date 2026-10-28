"""Leakage-safe features for 7-day-ahead demand.

Every feature for origin day t is computed from y[..t] only (data observed by the end of
day t) plus *calendar* information about days t+1..t+7 (weekday/holiday dates are known in
advance). The target for origin t is sum(y[t+1..t+7]); it is never used to build features.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from .panel import DemandPanel

HORIZON = 7
MIN_HISTORY_DAYS = 28            # origins with less observed history are not used
CAL_PATH = Path(__file__).with_name("festival_calendar.csv")

BASE_FEATURES = [
    "m1", "m3", "m7", "m14", "m28", "m56", "m91",
    "r7_28", "r28_91", "zero_frac_28", "cv_28", "max_ratio_28",
    "days_since_sale", "hist_days", "log_level",
    "ly_fwd", "ly_ratio",
]
# Day-of-year sin/cos were tried and removed: with < 2 years of history they let the model
# memorise one calendar year (validation WAPE got worse in the ablation, see README).
FESTIVAL_FEATURES = ["fest_days_fwd", "fest_days_back"]
CATEGORY_FEATURE = ["category_code"]


def festival_day_flags(dates: pd.DatetimeIndex, calendar_path=CAL_PATH) -> np.ndarray:
    """1.0 on days that fall inside a listed festival window (dates known in advance)."""
    cal = pd.read_csv(calendar_path, parse_dates=["date"])
    flag = pd.Series(0.0, index=dates)
    for _, r in cal.iterrows():
        rng = pd.date_range(r["date"], periods=int(r["duration_days"]), freq="D")
        flag.loc[flag.index.intersection(rng)] = 1.0
    return flag.to_numpy()


def build_features(
    panel: DemandPanel,
    origins: list,
    category_codes: np.ndarray | None = None,
    use_festival: bool = True,
    horizon: int = HORIZON,
) -> pd.DataFrame:
    """One row per (series, origin). `origins` are day *indices* into panel.dates.

    The target column `y_h` is NaN when the full horizon is not observed.
    """
    y, S, T = panel.y, panel.n_series, panel.n_days
    # cumulative sums with a leading zero column: C[:, k] = sum(y[:, :k])
    C = np.concatenate([np.zeros((S, 1)), np.cumsum(y, axis=1)], axis=1)
    rows = []
    sidx = np.arange(S)
    for t in origins:
        n_obs = t - panel.start_idx + 1                      # observed days up to and incl. t
        ok = n_obs >= MIN_HISTORY_DAYS
        if not ok.any():
            continue

        def mean_w(w):
            lo = np.maximum(t + 1 - w, panel.start_idx)       # first usable day
            cnt = np.maximum(t + 1 - lo, 1)
            return (C[sidx, t + 1] - C[sidx, lo]) / cnt

        m = {w: mean_w(w) for w in (1, 3, 7, 14, 28, 56, 91)}
        w28 = y[:, max(t - 27, 0): t + 1]
        mean28 = np.maximum(m[28], 1e-9)
        zero_frac = (w28 == 0).mean(axis=1)
        cv = w28.std(axis=1) / mean28
        max_ratio = w28.max(axis=1) / mean28
        # days since last sale (cap 60)
        recent = y[:, max(t - 59, 0): t + 1][:, ::-1] > 0
        dsl = np.where(recent.any(axis=1), recent.argmax(axis=1), 60).astype(float)

        # same forward window one year earlier (needs history of 364+ days)
        lyt = t - 364
        if lyt - 27 >= 0:
            ly_fwd = (C[sidx, lyt + horizon + 1] - C[sidx, lyt + 1]) / horizon
            ly_trail = (C[sidx, lyt + 1] - C[sidx, lyt - 27]) / 28.0
            ly_ratio = ly_fwd / np.maximum(ly_trail, 1e-9)
            valid = (lyt - 27 >= panel.start_idx)
            ly_fwd = np.where(valid, ly_fwd, np.nan)
            ly_ratio = np.where(valid & (ly_trail > 0), ly_ratio, np.nan)
        else:
            ly_fwd = np.full(S, np.nan)
            ly_ratio = np.full(S, np.nan)

        feat = {
            "product_id": panel.keys["product_id"].to_numpy(),
            "store_id": panel.keys["store_id"].to_numpy(),
            "origin_idx": np.full(S, t),
            "origin_date": np.full(S, panel.dates[0] + pd.Timedelta(days=t)),
            "m1": m[1], "m3": m[3], "m7": m[7], "m14": m[14], "m28": m[28],
            "m56": m[56], "m91": m[91],
            "r7_28": m[7] / mean28,
            "r28_91": m[28] / np.maximum(m[91], 1e-9),
            "zero_frac_28": zero_frac, "cv_28": cv, "max_ratio_28": max_ratio,
            "days_since_sale": dsl, "hist_days": n_obs.astype(float),
            "log_level": np.log1p(m[28]),
            "ly_fwd": ly_fwd, "ly_ratio": ly_ratio,
        }
        if use_festival:
            # calendar for days t+1..t+h may extend past the panel (dates are known in advance)
            feat["fest_days_fwd"] = np.full(S, _fest_sum(panel, t + 1, t + horizon))
            feat["fest_days_back"] = np.full(S, _fest_sum(panel, t - 6, t))
        if category_codes is not None:
            feat["category_code"] = category_codes
        # target (never a feature)
        if t + horizon < T:
            feat["y_h"] = C[sidx, t + 1 + horizon] - C[sidx, t + 1]
        else:
            feat["y_h"] = np.full(S, np.nan)
        df = pd.DataFrame(feat)[ok]
        rows.append(df)
    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True)
    out["base"] = np.maximum(out["m28"], 0.1) * horizon
    return out


_FEST_CACHE: dict = {}


def _fest_sum(panel: DemandPanel, i0: int, i1: int) -> float:
    """Festival days among day indices i0..i1 (indices may extend past the panel)."""
    key = (panel.dates[0], panel.dates[-1])
    if key not in _FEST_CACHE:
        ext = pd.date_range(panel.dates[0] - pd.Timedelta(days=400),
                            panel.dates[-1] + pd.Timedelta(days=30), freq="D")
        _FEST_CACHE[key] = (ext, festival_day_flags(ext))
    ext, flags = _FEST_CACHE[key]
    d0 = panel.dates[0] + pd.Timedelta(days=i0)
    d1 = panel.dates[0] + pd.Timedelta(days=i1)
    mask = (ext >= d0) & (ext <= d1)
    return float(flags[mask].sum())


def feature_columns(use_festival: bool = True, use_category: bool = True) -> list:
    cols = list(BASE_FEATURES)
    if use_festival:
        cols += FESTIVAL_FEATURES
    if use_category:
        cols += CATEGORY_FEATURE
    return cols
