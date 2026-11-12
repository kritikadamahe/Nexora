
"""Validate pricing model artifacts in their compatible environment."""

import os
import warnings

import joblib
import pytest
import sklearn
import xgboost

from app.modules.pricing.resave_models import MODEL_DIR, MODEL_FILES


# Versions recorded when the pricing models were saved.
SAVED_VERSIONS = {
    "xgboost": "3.4.1",
    "scikit-learn": "1.9.1",
}


def require_compatible_environment():
    """Skip artifact loading when installed versions do not match."""

    installed_versions = {
        "xgboost": xgboost.__version__,
        "scikit-learn": sklearn.__version__,
    }

    if installed_versions != SAVED_VERSIONS:
        pytest.skip(
            "Pricing model compatibility requires "
            f"{SAVED_VERSIONS}; installed versions are "
            f"{installed_versions}."
        )


@pytest.mark.parametrize("name", MODEL_FILES)
def test_pricing_model_loads_without_version_warnings(name):
    require_compatible_environment()

    model_path = os.path.join(MODEL_DIR, name)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        bundle = joblib.load(model_path)

    assert {"model", "metrics", "feature_cols"} <= set(bundle)


@pytest.mark.parametrize("name", MODEL_FILES)
def test_pricing_model_records_the_versions_it_was_saved_with(name):
    require_compatible_environment()

    model_path = os.path.join(MODEL_DIR, name)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        bundle = joblib.load(model_path)

    assert bundle["library_versions"] == SAVED_VERSIONS
