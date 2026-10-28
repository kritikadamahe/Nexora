# app/features/feature_assembler.py
#
# Assembles all feature DataFrames into the final product_analysis table.
# One row per (product_id, store_id) per nightly run.
#
# Output columns match the product_analysis table schema exactly —
# this is what gets saved to CSV (now) and PostgreSQL (later),
# and what the Decision Engine reads at runtime.

import numpy as np
import pandas as pd
from inventory_painpoints_service.app.core.config import DATA_END_DATE


def assemble_features(
    inventory_features_df: pd.DataFrame,
    return_features_df: pd.DataFrame,
    expiry_features_df: pd.DataFrame,
    forecast_df: pd.DataFrame = None,
) -> pd.DataFrame:
    """
    Merges all feature DataFrames into the product_analysis table structure.

    inventory_features_df contains:
        product_id, store_id, current_stock, reorder_level,
        rolling_sales_7d, rolling_sales_30d, avg_daily_sales,
        sales_velocity_ratio, seasonality_index,
        days_of_stock, stock_to_sales_ratio

    return_features_df contains:
        product_id, store_id, return_rate_30d, category_avg_return_rate

    expiry_features_df contains:
        product_id, store_id, days_to_expiry, expiry_risk_score

    forecast_df (optional) contains the trained 7-day demand forecast:
        product_id, store_id, forecast_7d, forecast_7d_p90, forecast_method
    When it is missing, or a series is absent from it, the original heuristic
    (avg_daily_sales * 7 * seasonality_index) is used and forecast_method is
    "heuristic_fallback".
    """

    if inventory_features_df.empty:
        return pd.DataFrame()

    df = inventory_features_df.copy()

    # Merge return features
    if not return_features_df.empty:
        df = df.merge(return_features_df, on=["product_id", "store_id"], how="left")
    else:
        df["return_rate_30d"]          = 0.0
        df["category_avg_return_rate"] = 0.0

    # Merge expiry features
    if not expiry_features_df.empty:
        df = df.merge(expiry_features_df, on=["product_id", "store_id"], how="left")
    else:
        df["days_to_expiry"]    = 9999
        df["expiry_risk_score"] = 0.0

    # Fill nulls
    df["return_rate_30d"]          = df["return_rate_30d"].fillna(0.0)
    df["category_avg_return_rate"] = df["category_avg_return_rate"].fillna(0.0)
    df["days_to_expiry"]           = df["days_to_expiry"].fillna(9999)
    df["expiry_risk_score"]        = df["expiry_risk_score"].fillna(0.0)

    # Add run_date
    df["run_date"] = DATA_END_DATE

    # M4 placeholders — filled by detector layer after this function returns
    df["pain_points_triggered"] = None
    df["composite_risk_score"]  = None
    
    # 7-day demand forecast.
    # Heuristic = avg_daily_sales * 7 * seasonality_index (the original proxy). It is only a
    # fallback now; the trained model's output (forecast_df) is used whenever available.
    if forecast_df is not None and not forecast_df.empty:
        cols = ["product_id", "store_id", "forecast_7d", "forecast_7d_p90", "forecast_method"]
        df = df.merge(forecast_df[cols], on=["product_id", "store_id"], how="left")
    else:
        df["forecast_7d"] = np.nan
        df["forecast_7d_p90"] = np.nan
        df["forecast_method"] = None
    heuristic = df["avg_daily_sales"] * 7 * df["seasonality_index"]
    missing = df["forecast_7d"].isna()
    df.loc[missing, "forecast_7d"] = heuristic[missing]
    df.loc[missing, "forecast_7d_p90"] = heuristic[missing]   # no spread information -> no safety stock
    df.loc[missing, "forecast_method"] = "heuristic_fallback"
    # Legacy column name kept because downstream modules read it. Despite the name it is NOT a
    # Temporal Fusion Transformer; it equals forecast_7d (trained model, or heuristic fallback).
    df["tft_forecast_7d"] = df["forecast_7d"]

    # Drop internal columns not needed downstream
    cols_to_drop = ["inventory_id", "expiry_date", "last_restocked_at"]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

    # Final column order matching product_analysis table schema
    final_cols = [
        "product_id", "store_id", "run_date",
        "rolling_sales_7d", "rolling_sales_30d", "sales_velocity_ratio",
        "avg_daily_sales", "seasonality_index",
        "current_stock", "reorder_level", "days_of_stock", "stock_to_sales_ratio",
        "days_to_expiry", "expiry_risk_score",
        "return_rate_30d", "category_avg_return_rate",
        "pain_points_triggered", "composite_risk_score", "tft_forecast_7d",
        "forecast_7d", "forecast_7d_p90", "forecast_method",
    ]
    final_cols = [c for c in final_cols if c in df.columns]

    return df[final_cols].reset_index(drop=True)
