"""Leakage-safe features and quantile forecasts of cumulative demand over days t..t+L.

Features at origin t use only demand on days < t and event announcements with
announce_day <= t. The target is sum(demand[t : t+L+1]) and is never used as a feature.
Everything is scaled by the SKU's trailing 28-day mean so one pooled model serves all SKUs.
"""
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor

from .signals import window_feature_table

MIN_HISTORY = 28


def base_features(demand, origins, L):
    """Return (X_base, scale) for every (sku, origin). Rows are ordered sku-major."""
    if L + 1 > 7:
        # the seasonal-naive window d[t-7 : t-7+L+1] would include day t or later
        raise ValueError(f"lead time L={L} too long for the 7-day seasonal-naive feature (needs L <= 6)")
    n, _ = demand.shape
    rows, scales = [], []
    for i in range(n):
        d = demand[i]
        for t in origins:
            assert t >= MIN_HISTORY, "origin needs 28 days of history"
            past = d[t - MIN_HISTORY:t]                     # strictly before t
            scale = past.mean() + 1.0
            last7 = d[t - 7:t].mean()
            # seasonal-naive window: same weekdays in each of the last 4 weeks
            sn = np.mean([d[t - 7 * w:t - 7 * w + L + 1].sum() for w in range(1, 5)])
            rows.append([i, t % 7, last7 / scale, past.mean() / scale, sn / scale,
                         past.std() / scale])
            scales.append(scale)
    return np.array(rows, dtype=float), np.array(scales)


def event_features(announcements, origins, L, n_types, n_sku):
    ev = window_feature_table(announcements, origins, L, n_types)
    return np.tile(ev, (n_sku, 1))                           # sku-major, same calendar for all


def targets(demand, origins, L):
    return np.concatenate([[demand[i, t:t + L + 1].sum() for t in origins]
                           for i in range(demand.shape[0])]).astype(float)


def build_X(demand, origins, L, announcements, n_types):
    Xb, scale = base_features(demand, origins, L)
    if announcements is None:                                # event-blind arm
        return Xb, scale
    Xe = event_features(announcements, origins, L, n_types, demand.shape[0])
    return np.hstack([Xb, Xe]), scale


class QuantileForecaster:
    """One gradient-boosted quantile model per quantile level (sklearn, no LightGBM)."""

    def __init__(self, quantiles, params, seed):
        self.quantiles = list(quantiles)
        self.params = params
        self.seed = seed
        self.models = {}

    def fit(self, X, y, scale):
        yn = y / scale
        for q in self.quantiles:
            m = HistGradientBoostingRegressor(loss="quantile", quantile=q, random_state=self.seed,
                                              categorical_features=[0], **self.params)
            self.models[q] = m.fit(X, yn)
        return self

    def predict(self, X, scale):
        return {q: np.maximum(0.0, m.predict(X)) * scale for q, m in self.models.items()}
