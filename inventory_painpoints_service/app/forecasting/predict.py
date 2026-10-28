"""Fit on all data observed so far and forecast the next 7 days (used by the nightly pipeline)."""
import os

import numpy as np
import pandas as pd

from .features import MIN_HISTORY_DAYS, build_features
from .model import DemandForecaster, ModelConfig
from .panel import build_daily_panel

HORIZON = 7
MIN_TRAIN_ROWS = 2000     # below this a global model is not credible -> caller falls back


def default_config() -> ModelConfig:
    """ModelConfig honouring NEXORA_FORECAST_MAX_ITER (used to keep the test-suite fast)."""
    cfg = ModelConfig()
    override = os.getenv("NEXORA_FORECAST_MAX_ITER")
    if override:
        cfg.max_iter = int(override)
    return cfg


def forecast_next_7d(sales_df: pd.DataFrame, products_df: pd.DataFrame, as_of,
                     config: ModelConfig | None = None) -> pd.DataFrame:
    """Trains on origins whose 7-day target is fully observed by `as_of` and predicts days
    as_of+1..as_of+7. Returns product_id, store_id, forecast_7d, forecast_7d_p90,
    forecast_method. Series with < 28 days of history are omitted (caller falls back).
    Raises ValueError if there is too little data to train a model.
    """
    from .evaluation import category_codes_for
    as_of = pd.Timestamp(as_of)
    panel = build_daily_panel(sales_df, end_date=as_of)
    codes = category_codes_for(panel, products_df)
    last = panel.n_days - 1
    feats = build_features(panel, list(range(MIN_HISTORY_DAYS - 1, panel.n_days)), codes)
    train = feats[feats["y_h"].notna()]
    if len(train) < MIN_TRAIN_ROWS:
        raise ValueError(f"only {len(train)} training rows; need >= {MIN_TRAIN_ROWS}")
    now = feats[feats["origin_idx"] == last].copy()
    if now.empty:
        raise ValueError("no series with enough history at the forecast origin")
    model = DemandForecaster(config or default_config()).fit(train)
    pred = model.predict(now)
    out = now[["product_id", "store_id"]].reset_index(drop=True)
    out["forecast_7d"] = pred["forecast_7d"].to_numpy()
    out["forecast_7d_p90"] = pred["forecast_7d_p90"].to_numpy()
    out["forecast_method"] = "gbm"
    out.attrs["train_rows"] = int(len(train))
    return out
