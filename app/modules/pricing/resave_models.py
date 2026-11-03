# app/modules/pricing/resave_models.py
#
# Re-saves the pickled pricing models under the CURRENT library versions
# (use the pinned environment from requirements-lock.txt) without retraining.
#
# Why: the committed .pkl files were written by older scikit-learn / XGBoost
# releases, so loading them in the pinned environment raises
# InconsistentVersionWarning / "older version of XGBoost" warnings. This script
# loads each bundle, checks that predictions survive the round trip unchanged,
# records the library versions in the bundle, and writes it back.
#
# Run from the project root:
#     python -m app.modules.pricing.resave_models
#
# To retrain from data instead, use train_xgboost_pricing.py.

import os
import warnings

import joblib
import numpy as np
import sklearn
import xgboost

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_FILES = ["predictify_xgb_model.pkl", "legacy_xgb_model.pkl"]


def _probe_matrix(feature_cols, n=500, seed=0):
    """Deterministic non-negative probe inputs, one column per model feature."""
    rng = np.random.default_rng(seed)
    return rng.uniform(0.0, 100.0, size=(n, len(feature_cols)))


def resave(path: str) -> dict:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")          # old-version warnings expected here
        bundle = joblib.load(path)

    cols = bundle["feature_cols"]
    probe = _probe_matrix(cols)
    before = np.asarray(bundle["model"].predict(probe))

    bundle["library_versions"] = {
        "xgboost": xgboost.__version__,
        "scikit-learn": sklearn.__version__,
    }
    joblib.dump(bundle, path)

    with warnings.catch_warnings():
        warnings.simplefilter("error")           # a clean reload must raise no warnings
        reloaded = joblib.load(path)
    after = np.asarray(reloaded["model"].predict(probe))

    if not np.array_equal(before, after):
        raise RuntimeError(f"{os.path.basename(path)}: predictions changed after re-save")
    return {"file": os.path.basename(path), "probe_rows": len(probe),
            "max_abs_diff": float(np.max(np.abs(before - after))),
            "versions": bundle["library_versions"]}


def main():
    for name in MODEL_FILES:
        print(resave(os.path.join(MODEL_DIR, name)))


if __name__ == "__main__":
    main()
