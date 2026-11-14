
import pytest

from app.modules.m7_xai import llm_narrator


def test_build_prompt_includes_shap_values():
    prompt = llm_narrator._build_prompt(
        "LOGISTICS",
        {"pain_points": ["NEAR_EXPIRY"], "composite_risk_score": 0.8},
        {"urgency_score": 0.7, "days_to_expiry": 5},
        {"action_chosen": "MARKDOWN"},
        {"revenue_recovery": 500, "days_to_clear": 3},
        [{
            "feature": "expiry_risk_score",
            "direction": "+",
            "shap_value": 0.35,
            "raw_value": 0.8,
        }],
    )

    assert "expiry_risk_score" in prompt
    assert "0.350" in prompt
    assert "MARKDOWN" in prompt


def test_build_prompt_uses_pain_points_without_shap():
    prompt = llm_narrator._build_prompt(
        "LOGISTICS",
        {"pain_points": ["LOW_STOCK"], "composite_risk_score": 0.6},
        {},
        {},
        {},
        [],
    )

    assert "LOW_STOCK" in prompt
    assert "Key signals" in prompt


def test_template_rationale_with_revenue_and_clearance():
    prompt = (
        "Action: MARKDOWN. "
        "Expected revenue recovery: Rs500. "
        "Units unsold at expiry: 0. "
        "Days to clear: 3."
    )

    result = llm_narrator._template_rationale(prompt)

    assert "MARKDOWN" in result
    assert "Rs500" in result
    assert "3 days" in result


def test_template_rationale_with_unsold_units():
    prompt = (
        "Action: MARKDOWN. "
        "Expected revenue recovery: Rs500. "
        "Units unsold at expiry: 4."
    )

    result = llm_narrator._template_rationale(prompt)

    assert "Rs500" in result
    assert "4 unit(s)" in result


def test_template_rationale_handles_missing_context():
    result = llm_narrator._template_rationale(
        "No action details available."
    )

    assert result == "Action recommended based on inventory risk analysis."


def test_call_llm_uses_fallback_without_api_key(monkeypatch):
    monkeypatch.setattr(llm_narrator, "GROQ_API_KEY", None)
    monkeypatch.setattr(
        llm_narrator,
        "_template_rationale",
        lambda prompt: "Fallback explanation",
    )

    result = llm_narrator._call_llm("Test prompt")

    assert result == "Fallback explanation"

from types import SimpleNamespace
from unittest.mock import Mock


def test_call_llm_uses_fallback_for_empty_response(monkeypatch):
    monkeypatch.setattr(llm_narrator, "GROQ_API_KEY", "test-key")

    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="   ")
            )
        ]
    )

    groq_mock = Mock(return_value=client)
    monkeypatch.setattr(llm_narrator, "Groq", groq_mock)

    monkeypatch.setattr(
        llm_narrator,
        "_template_rationale",
        lambda prompt: "Empty response fallback",
    )

    result = llm_narrator._call_llm("Test prompt")

    assert result == "Empty response fallback"
    groq_mock.assert_called_once_with(
        api_key="test-key",
        timeout=llm_narrator.LLM_TIMEOUT,
    )


def test_call_llm_uses_fallback_when_api_fails(monkeypatch):
    monkeypatch.setattr(llm_narrator, "GROQ_API_KEY", "test-key")

    client = Mock()
    client.chat.completions.create.side_effect = RuntimeError(
        "API unavailable"
    )

    monkeypatch.setattr(
        llm_narrator,
        "Groq",
        Mock(return_value=client),
    )

    monkeypatch.setattr(
        llm_narrator,
        "_template_rationale",
        lambda prompt: "API error fallback",
    )

    result = llm_narrator._call_llm("Test prompt")

    assert result == "API error fallback"
