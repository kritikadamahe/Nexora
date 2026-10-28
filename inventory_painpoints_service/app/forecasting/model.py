"""Gradient-boosted 7-day demand model (point + P90) trained across all products.

One global model is fitted for all (product, store) series. Because unit scales span
three orders of magnitude, the target is the *ratio* to the trailing-28-day level
(`base = 7 * max(m28, 0.1)`) and training rows are weighted by `base`, so the loss is
the usual absolute error in units. `early_stopping` is disabled: sklearn's default would
split validation rows at random from the training set (not chronologically).
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from .features import feature_columns


@dataclass
class ModelConfig:
    use_festival: bool = True
    use_category: bool = True
    max_iter: int = 300
    learning_rate: float = 0.05
    max_leaf_nodes: int = 15
    min_samples_leaf: int = 100
    upper_quantile: float = 0.9
    random_state: int = 0
    columns: list = field(default_factory=list)

    def __post_init__(self):
        if not self.columns:
            self.columns = feature_columns(self.use_festival, self.use_category)


class DemandForecaster:
    """fit() on rows with a known target; predict() returns p50 and p90 7-day demand."""

    def __init__(self, config: ModelConfig | None = None):
        self.config = config or ModelConfig()
        self.point_model = None
        self.upper_model = None

    def _make(self, **loss_kw):
        c = self.config
        return HistGradientBoostingRegressor(
            max_iter=c.max_iter, learning_rate=c.learning_rate,
            max_leaf_nodes=c.max_leaf_nodes, min_samples_leaf=c.min_samples_leaf,
            categorical_features=[col == "category_code" for col in c.columns],
            early_stopping=False, random_state=c.random_state, **loss_kw)

    def fit(self, train: pd.DataFrame) -> "DemandForecaster":
        train = train[train["y_h"].notna()]
        if len(train) == 0:
            raise ValueError("no training rows with an observed target")
        X = train[self.config.columns]
        ratio = train["y_h"] / train["base"]
        w = train["base"]
        self.point_model = self._make(loss="absolute_error").fit(X, ratio, sample_weight=w)
        self.upper_model = self._make(
            loss="quantile", quantile=self.config.upper_quantile).fit(X, ratio, sample_weight=w)
        return self

    def predict(self, feats: pd.DataFrame) -> pd.DataFrame:
        X = feats[self.config.columns]
        p50 = np.clip(self.point_model.predict(X), 0, None) * feats["base"].to_numpy()
        p90 = np.clip(self.upper_model.predict(X), 0, None) * feats["base"].to_numpy()
        p90 = np.maximum(p90, p50)          # enforce quantile ordering
        return pd.DataFrame({"forecast_7d": p50, "forecast_7d_p90": p90}, index=feats.index)
