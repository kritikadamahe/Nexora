"""Tests for the nightly pipeline (M2 features + M4 pain-point detection)."""
import json

import pandas as pd
import pytest

from conftest import DATA_DIR, run_quiet

EXPECTED_COLUMNS = [
    "product_id", "store_id", "run_date", "rolling_sales_7d", "rolling_sales_30d",
    "sales_velocity_ratio", "avg_daily_sales", "seasonality_index", "current_stock",
    "reorder_level", "days_of_stock", "stock_to_sales_ratio", "days_to_expiry",
    "expiry_risk_score", "return_rate_30d", "category_avg_return_rate",
    "pain_points_triggered", "composite_risk_score", "tft_forecast_7d",
    "forecast_7d", "forecast_7d_p90", "forecast_method",
]
VALID_PAIN_POINTS = {"NEAR_EXPIRY", "HIGH_RETURN", "STAGNANT", "LOW_STOCK", "SEASONAL_MISMATCH"}


def test_output_schema_columns(analysis_df):
    assert list(analysis_df.columns) == EXPECTED_COLUMNS


def test_one_row_per_product_store_and_no_missing_values(analysis_df):
    assert len(analysis_df) == 200                      # inventory.csv has 200 rows
    assert not analysis_df.duplicated(["product_id", "store_id"]).any()
    assert not analysis_df.isna().any().any()


def test_composite_risk_is_a_probability_like_score(analysis_df):
    assert analysis_df["composite_risk_score"].between(0.0, 1.0).all()


def test_pain_points_are_valid_json_labels(analysis_df):
    for raw in analysis_df["pain_points_triggered"]:
        labels = json.loads(raw)
        assert isinstance(labels, list)
        assert set(labels) <= VALID_PAIN_POINTS


def test_pipeline_is_deterministic(pipeline_dir, tmp_path):
    from inventory_painpoints_service.app.services.nightly_pipeline import run_nightly_pipeline
    again = run_quiet(run_nightly_pipeline, str(DATA_DIR), str(tmp_path))
    pd.testing.assert_frame_equal(pipeline_dir[1].reset_index(drop=True),
                                  again.reset_index(drop=True))


def test_pipeline_writes_csv_that_round_trips(pipeline_dir):
    out_dir, df = pipeline_dir
    on_disk = pd.read_csv(out_dir / "product_analysis.csv")
    assert list(on_disk.columns) == EXPECTED_COLUMNS
    assert len(on_disk) == len(df)


def test_golden_pain_point_counts_match_v0_run(analysis_df):
    """Counts observed when the untouched nexora-v0 code was run on the same data."""
    from collections import Counter
    counts = Counter(p for raw in analysis_df["pain_points_triggered"] for p in json.loads(raw))
    assert counts == {"LOW_STOCK": 15, "NEAR_EXPIRY": 8, "SEASONAL_MISMATCH": 1}
    assert int((analysis_df["pain_points_triggered"] != "[]").sum()) == 24
    assert int((analysis_df["composite_risk_score"] > 0.5).sum()) == 3


def test_forecast_columns_come_from_trained_model(analysis_df):
    """tft_forecast_7d is a legacy column name: it now equals the trained forecast_7d."""
    pd.testing.assert_series_equal(analysis_df["tft_forecast_7d"], analysis_df["forecast_7d"],
                                   check_names=False)
    assert (analysis_df["forecast_method"] == "gbm").all()
    assert (analysis_df["forecast_7d"] >= 0).all()
    assert (analysis_df["forecast_7d_p90"] >= analysis_df["forecast_7d"]).all()


def test_heuristic_fallback_when_forecast_missing():
    """Without a trained forecast the original heuristic is used and labelled as a fallback."""
    from inventory_painpoints_service.app.features.feature_assembler import assemble_features
    inv = pd.DataFrame({"product_id": [1], "store_id": [1], "current_stock": [10],
                        "reorder_level": [5], "rolling_sales_7d": [7.0], "rolling_sales_30d": [30.0],
                        "avg_daily_sales": [1.0], "sales_velocity_ratio": [1.0],
                        "seasonality_index": [1.5], "days_of_stock": [10.0],
                        "stock_to_sales_ratio": [1.4]})
    out = assemble_features(inv, pd.DataFrame(), pd.DataFrame(), forecast_df=None)
    assert out.loc[0, "forecast_method"] == "heuristic_fallback"
    assert out.loc[0, "forecast_7d"] == pytest.approx(1.0 * 7 * 1.5)
    assert out.loc[0, "tft_forecast_7d"] == out.loc[0, "forecast_7d"]


def test_replenishment_plan_is_written_and_consistent(pipeline_dir):
    out_dir, df = pipeline_dir
    plan = pd.read_csv(out_dir / "replenishment_plan.csv")
    assert len(plan) == len(df)
    assert set(plan["action"]) <= {"ORDER", "ORDER_URGENT", "HOLD", "OVERSTOCK_REVIEW", "EXPIRY_RISK"}
    assert (plan["order_quantity"] >= 0).all()
    assert not plan.isna().any().any()
