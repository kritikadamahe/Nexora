"""Dense daily demand panel.

Assumption (documented, not verifiable from the data): sales.csv only contains days on
which at least one unit was sold (quantity_sold >= 1 everywhere), so a missing day for a
product that is already on sale is treated as zero demand. Days before a product's first
recorded sale are NOT zero-filled (the product may not have been listed yet); they are
marked as "not observed" and excluded from history length.

Also note: sales are an observed proxy for demand. There is no historical stock-level
data, so demand on days the item was out of stock is censored and cannot be recovered.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class DemandPanel:
    keys: pd.DataFrame          # product_id, store_id (row order of `y`)
    dates: pd.DatetimeIndex     # column order of `y`
    y: np.ndarray               # (n_series, n_days) units sold, 0 where no sale
    start_idx: np.ndarray       # first observed day index per series

    @property
    def n_series(self) -> int:
        return self.y.shape[0]

    @property
    def n_days(self) -> int:
        return self.y.shape[1]


def build_daily_panel(sales_df: pd.DataFrame, end_date=None) -> DemandPanel:
    """sales_df: cleaned sales with product_id, store_id, sale_date, quantity_sold."""
    if sales_df.empty:
        raise ValueError("cannot build a demand panel from an empty sales table")

    df = sales_df[["product_id", "store_id", "sale_date", "quantity_sold"]].copy()
    df["sale_date"] = pd.to_datetime(df["sale_date"]).dt.normalize()
    if end_date is not None:
        df = df[df["sale_date"] <= pd.Timestamp(end_date)]
    daily = (
        df.groupby(["product_id", "store_id", "sale_date"], as_index=False)["quantity_sold"].sum()
    )

    first = daily.groupby(["product_id", "store_id"])["sale_date"].min()
    keys = first.reset_index()[["product_id", "store_id"]]
    last_day = pd.Timestamp(end_date) if end_date is not None else daily["sale_date"].max()
    dates = pd.date_range(daily["sale_date"].min(), last_day, freq="D")

    series_index = pd.MultiIndex.from_frame(keys)
    pos = series_index.get_indexer(pd.MultiIndex.from_frame(daily[["product_id", "store_id"]]))
    col = (daily["sale_date"] - dates[0]).dt.days.to_numpy()
    y = np.zeros((len(keys), len(dates)), dtype=np.float64)
    y[pos, col] = daily["quantity_sold"].to_numpy(dtype=np.float64)
    start_idx = ((first.to_numpy() - np.datetime64(dates[0])) / np.timedelta64(1, "D")).astype(int)
    return DemandPanel(keys=keys.reset_index(drop=True), dates=dates, y=y, start_idx=start_idx)
