"""Pickled pricing models must load cleanly in the pinned environment."""
import os
import warnings

import joblib
import pytest
import sklearn
import xgboost

from app.modules.pricing.resave_models import MODEL_DIR, MODEL_FILES


@pytest.mark.parametrize("name", MODEL_FILES)
def test_pricing_model_loads_without_version_warnings(name):
    with warnings.catch_warnings():
        warnings.simplefilter("error")      # any version warning fails the test
        bundle = joblib.load(os.path.join(MODEL_DIR, name))
    assert {"model", "metrics", "feature_cols"} <= set(bundle)


@pytest.mark.parametrize("name", MODEL_FILES)
def test_pricing_model_records_the_versions_it_was_saved_with(name):
    bundle = joblib.load(os.path.join(MODEL_DIR, name))
    assert bundle["library_versions"] == {
        "xgboost": xgboost.__version__,
        "scikit-learn": sklearn.__version__,
    }
