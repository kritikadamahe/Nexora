
import pytest

from app.modules.m7_xai.shap_explainer import SHAPExplainer


@pytest.fixture
def explainer():
    return SHAPExplainer.__new__(SHAPExplainer)


def test_fallback_returns_top_three_features(explainer):
    result = explainer._fallback_importance({
        "expiry_risk_score": 0.8,
        "sales_velocity_ratio": 0.2,
        "stock_to_sales_ratio": 1.0,
        "return_rate_30d": 0.1,
    })

    assert len(result) == 3
    assert [item["feature"] for item in result] == [
        "expiry_risk_score",
        "stock_to_sales_ratio",
        "sales_velocity_ratio",
    ]


def test_fallback_returns_empty_for_non_dictionary(explainer):
    assert explainer._fallback_importance(None) == []
    assert explainer._fallback_importance([]) == []
    assert explainer._fallback_importance("invalid") == []


@pytest.mark.parametrize("invalid_value", [
    "invalid",
    None,
    float("nan"),
    float("inf"),
    float("-inf"),
])
def test_fallback_handles_invalid_numeric_values(explainer, invalid_value):
    result = explainer._fallback_importance({
        "expiry_risk_score": invalid_value,
        "sales_velocity_ratio": invalid_value,
        "stock_to_sales_ratio": invalid_value,
        "return_rate_30d": invalid_value,
    })

    assert result == []


def test_fallback_respects_feature_thresholds(explainer):
    result = explainer._fallback_importance({
        "expiry_risk_score": 0.0,
        "sales_velocity_ratio": 0.8,
        "stock_to_sales_ratio": 2.0,
        "return_rate_30d": 0.05,
    })

    assert result == []


def test_fallback_uses_defaults_for_missing_features(explainer):
    result = explainer._fallback_importance({})

    assert result == []
