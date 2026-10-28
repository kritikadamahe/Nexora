# app/services/nightly_pipeline.py
#
# Main entry point for the nightly batch job (runs via cron at 2am).
# Wires together all layers: load → clean → features → detect → save.
#
# Output: product_analysis.csv (now) → PostgreSQL product_analysis table (later)
# One row per product per nightly run.
#
# To swap CSV → PostgreSQL: replace _save_to_csv() with _save_to_db()
# Everything else stays the same.
#
# Build Plan Section 2 — Build Order:
#   This service is the M2 + M4 combined nightly pipeline.
#   M3 (news urgency_score) is added later as a separate pipeline
#   that runs alongside this and feeds the Decision Engine together.

import os
import json
import pandas as pd
from datetime import datetime

from inventory_painpoints_service.app.data.loaders.products_loader  import load_products
from inventory_painpoints_service.app.data.loaders.stores_loader    import load_stores
from inventory_painpoints_service.app.data.loaders.sales_loader     import load_sales
from inventory_painpoints_service.app.data.loaders.inventory_loader import load_inventory
from inventory_painpoints_service.app.data.loaders.returns_loader   import load_returns

from inventory_painpoints_service.app.data.cleaners.clean_products  import clean_products
from inventory_painpoints_service.app.data.cleaners.clean_stores    import clean_stores
from inventory_painpoints_service.app.data.cleaners.clean_sales     import clean_sales
from inventory_painpoints_service.app.data.cleaners.clean_inventory import clean_inventory
from inventory_painpoints_service.app.data.cleaners.clean_returns   import clean_returns

from inventory_painpoints_service.app.features.sales_features      import compute_sales_features
from inventory_painpoints_service.app.features.expiry_features     import compute_expiry_features
from inventory_painpoints_service.app.features.return_features     import compute_return_features
from inventory_painpoints_service.app.features.inventory_features  import compute_inventory_features
from inventory_painpoints_service.app.features.feature_assembler   import assemble_features

from inventory_painpoints_service.app.detectors.detector_runner    import run_all_detectors
from inventory_painpoints_service.app.core.config                  import DATA_END_DATE
from inventory_painpoints_service.app.forecasting.predict          import forecast_next_7d
from inventory_painpoints_service.app.inventory_policy.replenishment import plan_replenishment


# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

DATA_DIR   = "data_samples"           # folder with input CSVs
OUTPUT_DIR = "pipeline_output"        # folder for output CSV


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def run_nightly_pipeline(
    data_dir:   str = DATA_DIR,
    output_dir: str = OUTPUT_DIR,
) -> pd.DataFrame:
    """
    Runs the full nightly pipeline.
    Returns the final product_analysis DataFrame.
    """

    start = datetime.now()
    print(f"\n{'='*60}")
    print(f"  Predictify AI — Nightly Pipeline")
    print(f"  Started : {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # ── STEP 1: LOAD ─────────────────────────────────────────────────────────
    print("[ 1 / 4 ]  Loading data...")

    products  = load_products (os.path.join(data_dir, "products.csv"))
    stores    = load_stores   (os.path.join(data_dir, "stores.csv"))
    sales     = load_sales    (os.path.join(data_dir, "sales.csv"))
    inventory = load_inventory(os.path.join(data_dir, "inventory.csv"))
    returns   = load_returns  (os.path.join(data_dir, "returns.csv"))

    print(f"  products={len(products)}  stores={len(stores)}  "
          f"sales={len(sales):,}  inventory={len(inventory)}  returns={len(returns):,}")

    # ── STEP 2: CLEAN ────────────────────────────────────────────────────────
    print("\n[ 2 / 4 ]  Cleaning data...")

    products  = clean_products(products)
    stores    = clean_stores(stores)
    sales     = clean_sales(sales, products, stores)
    inventory = clean_inventory(inventory, products, stores)
    returns   = clean_returns(returns, products, stores)

    print(f"  After cleaning — products={len(products)}  sales={len(sales):,}  "
          f"inventory={len(inventory)}  returns={len(returns):,}")

    # ── STEP 3: FEATURES (M2) ────────────────────────────────────────────────
    print("\n[ 3 / 4 ]  Computing features (M2)...")

    sales_feat  = compute_sales_features(sales)
    expiry_feat = compute_expiry_features(inventory, products)
    return_feat = compute_return_features(returns, sales, products)
    inv_feat    = compute_inventory_features(inventory, sales_feat)
    forecast    = _run_forecast(sales, products)
    features    = assemble_features(inv_feat, return_feat, expiry_feat, forecast)

    print(f"  Feature matrix: {len(features)} rows × {len(features.columns)} columns")

    # ── STEP 4: DETECT PAIN POINTS (M4) ─────────────────────────────────────
    print("\n[ 4 / 4 ]  Detecting pain points (M4)...")

    result = run_all_detectors(features)

    # Summary
    result["_pp_list"] = result["pain_points_triggered"].apply(json.loads)
    flagged   = (result["_pp_list"].apply(len) > 0).sum()
    high_risk = (result["composite_risk_score"] > 0.5).sum()

    from collections import Counter
    all_pp = [pp for pps in result["_pp_list"] for pp in pps]
    pp_counts = Counter(all_pp)

    print(f"  Products evaluated : {len(result)}")
    print(f"  Products flagged   : {flagged}")
    print(f"  High risk (>0.5)   : {high_risk}")
    print(f"  Pain point breakdown:")
    for pp, count in sorted(pp_counts.items(), key=lambda x: -x[1]):
        print(f"    {pp:<25} {count}")

    result = result.drop(columns=["_pp_list"])

    # ── REPLENISHMENT PLAN (forecast + stock + product data) ────────────────
    plan = plan_replenishment(result, products)
    print("\n  Replenishment actions: " + ", ".join(
        f"{k}={v}" for k, v in plan["action"].value_counts().items()))

    # ── SAVE ─────────────────────────────────────────────────────────────────
    _save_to_csv(result, output_dir)
    plan.to_csv(os.path.join(output_dir, "replenishment_plan.csv"), index=False)

    elapsed = (datetime.now() - start).total_seconds()
    print(f"\n{'='*60}")
    print(f"  Pipeline complete in {elapsed:.1f}s")
    print(f"{'='*60}\n")

    return result


def _run_forecast(sales: pd.DataFrame, products: pd.DataFrame):
    """Trains the demand model on history up to DATA_END_DATE and forecasts the next 7 days.
    Returns None (-> heuristic fallback in assemble_features) if training is not possible."""
    try:
        fc = forecast_next_7d(sales, products, DATA_END_DATE)
        print(f"  Demand model trained on {fc.attrs.get('train_rows', '?'):,} rows; "
              f"forecast for {len(fc)} series")
        return fc
    except ValueError as exc:
        print(f"  [warning] trained forecast unavailable ({exc}); using heuristic fallback")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# SAVE — CSV now, swap to DB later
# ─────────────────────────────────────────────────────────────────────────────

def _save_to_csv(result: pd.DataFrame, output_dir: str) -> None:
    """
    Saves product_analysis DataFrame to CSV.
    Later: replace this function body with PostgreSQL INSERT.
    
    PostgreSQL swap (when ready):
        from app.db.session import get_db_session
        from app.db.models import ProductAnalysis
        session = get_db_session()
        session.bulk_insert_mappings(ProductAnalysis, result.to_dict("records"))
        session.commit()
    """
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "product_analysis.csv")
    result.to_csv(path, index=False)
    print(f"\n  Saved → {path}  ({len(result)} rows)")


