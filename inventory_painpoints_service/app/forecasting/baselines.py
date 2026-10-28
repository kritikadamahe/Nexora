"""Baseline 7-day demand forecasts, all computed as-of the origin date.

Every baseline only sees data up to and including the origin day.
"""
import numpy as np
import pandas as pd

from inventory_painpoints_service.app.features.sales_features import compute_sales_features

HORIZON = 7


def simple_baselines(feats: pd.DataFrame, horizon: int = HORIZON) -> dict:
    """Baselines derived from the already leakage-safe trailing means in `feats`."""
    return {
        "naive_last_7d": feats["m7"].to_numpy() * horizon,      # repeat last week
        "moving_avg_28d": feats["m28"].to_numpy() * horizon,
        "moving_avg_91d": feats["m91"].to_numpy() * horizon,
    }


def nexora_heuristic(sales_df: pd.DataFrame, feats: pd.DataFrame) -> np.ndarray:
    """The original Nexora forecast (avg_daily_sales x 7 x seasonality_index), as-of each origin.

    Calls the project's own `compute_sales_features` on sales truncated at the origin date.
    Series with no sales in the last 30 days get 0, exactly as the original code does.
    """
    sales = sales_df.copy()
    sales["sale_date"] = pd.to_datetime(sales["sale_date"])
    out = np.full(len(feats), np.nan)
    for origin, idx in feats.groupby("origin_date").indices.items():
        origin = pd.Timestamp(origin)
        sf = compute_sales_features(sales[sales["sale_date"] <= origin], as_of=origin)
        sf["h"] = sf["avg_daily_sales"] * HORIZON * sf["seasonality_index"]
        sub = feats.iloc[idx][["product_id", "store_id"]].merge(
            sf[["product_id", "store_id", "h"]], on=["product_id", "store_id"], how="left")
        out[idx] = sub["h"].fillna(0.0).to_numpy()
    return out

