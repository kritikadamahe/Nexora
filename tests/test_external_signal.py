"""
Regression tests for the external-signal override.

nexora-v0 computed sentiment/urgency and then overwrote them with
NEUTRAL / 0.25 for every product. These tests pin both sides of that change:
  * the old behaviour still exists, but only as the explicit `legacy_neutral` mode;
  * in every other mode the computed signal now reaches the caller.
"""
import pytest

from conftest import StubProvider, POSITIVE_MENTIONS, NEGATIVE_MENTIONS
from external_signal_service import main as sig
from external_signal_service.providers.synthetic_provider import SyntheticProvider
from external_signal_service.schemas import ExternalSignals


def _signals(avg, volume=100, conf=1.0):
    return ExternalSignals(average_sentiment=avg, positive_ratio=0, negative_ratio=0,
                           mention_volume=volume, unique_threads=1,
                           trend_velocity="stable", confidence_score=conf)


# --- the regression itself -------------------------------------------------

def test_legacy_neutral_mode_reproduces_v0_exactly():
    # Even with overwhelmingly positive mentions available, v0 answered NEUTRAL/0.25.
    out = sig.reddit_trend("Milk", 30, None,
                           provider=StubProvider(POSITIVE_MENTIONS()), mode="legacy_neutral")
    assert out["news_sentiment"] == "NEUTRAL"
    assert out["urgency_score"] == 0.25
    assert out["mode"] == "legacy_neutral"


def test_override_removed_positive_signal_reaches_caller():
    out = sig.reddit_trend("Milk", 30, None,
                           provider=StubProvider(POSITIVE_MENTIONS()), mode="synthetic")
    assert out["news_sentiment"] == "POSITIVE"
    assert out["urgency_score"] > 0.6            # v0 would have said 0.25
    assert out["external_signals"]["average_sentiment"] > 0.5


def test_override_removed_negative_signal_reaches_caller():
    out = sig.reddit_trend("Milk", 30, None,
                           provider=StubProvider(NEGATIVE_MENTIONS()), mode="synthetic")
    assert out["news_sentiment"] == "NEGATIVE"
    assert out["urgency_score"] > 0.6


def test_no_mentions_means_zero_urgency_not_the_v0_constant():
    out = sig.reddit_trend("Milk", 30, None, provider=StubProvider([]), mode="synthetic")
    assert out["news_sentiment"] == "NEUTRAL"
    assert out["urgency_score"] == 0.0


def test_positional_call_signature_used_by_decision_engine_still_works(legacy_mode):
    # engine.py calls reddit_trend(product_name, 30, None)
    out = sig.reddit_trend("Milk", 30, None)
    assert set(out) >= {"product_name", "time_window_days", "external_signals",
                        "urgency_score", "news_sentiment"}


# --- pure formula (unchanged from v0, Build Plan 3.12) -----------------------

@pytest.mark.parametrize("avg,label", [(0.06, "POSITIVE"), (0.05, "NEUTRAL"),
                                       (0.0, "NEUTRAL"), (-0.05, "NEUTRAL"),
                                       (-0.06, "NEGATIVE")])
def test_sentiment_thresholds(avg, label):
    assert sig.urgency_and_sentiment(_signals(avg))["news_sentiment"] == label


def test_urgency_formula_and_clipping():
    # |0.8| * min(5/10,1) * 0.5 = 0.2
    assert sig.urgency_and_sentiment(_signals(0.8, volume=5, conf=0.5))["urgency_score"] == pytest.approx(0.2)
    # saturates at 1.0 and never exceeds it
    assert sig.urgency_and_sentiment(_signals(1.0, volume=500, conf=1.0))["urgency_score"] == 1.0


# --- mode selection -----------------------------------------------------------

def test_default_mode_is_synthetic(monkeypatch):
    monkeypatch.delenv("NEXORA_EXTERNAL_SIGNAL_MODE", raising=False)
    assert sig.get_signal_mode() == "synthetic"


def test_invalid_mode_is_rejected(monkeypatch):
    monkeypatch.setenv("NEXORA_EXTERNAL_SIGNAL_MODE", "banana")
    with pytest.raises(ValueError):
        sig.get_signal_mode()


def test_failures_are_raised_not_silently_neutral():
    class Boom:
        def fetch_mentions(self, *a):
            raise RuntimeError("network down")
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        sig.reddit_trend("Milk", 30, None, provider=Boom(), mode="synthetic")


# --- reproducibility of the synthetic provider ---------------------------------

def _strip_time(mentions):
    return [{k: v for k, v in m.items() if k != "created_utc"} for m in mentions]


def test_synthetic_provider_same_seed_same_mentions():
    a = SyntheticProvider(seed=7).fetch_mentions("Milk", 30, None)
    b = SyntheticProvider(seed=7).fetch_mentions("Milk", 30, None)
    assert _strip_time(a) == _strip_time(b)


def test_synthetic_provider_different_seed_or_product_differs():
    base = _strip_time(SyntheticProvider(seed=7).fetch_mentions("Milk", 30, None))
    assert base != _strip_time(SyntheticProvider(seed=8).fetch_mentions("Milk", 30, None))
    assert base != _strip_time(SyntheticProvider(seed=7).fetch_mentions("Bread", 30, None))


def test_end_to_end_synthetic_signal_is_deterministic(monkeypatch):
    monkeypatch.setenv("NEXORA_EXTERNAL_SIGNAL_MODE", "synthetic")
    monkeypatch.setenv("NEXORA_SEED", "123")
    a = sig.reddit_trend("Milk", 30, None)
    b = sig.reddit_trend("Milk", 30, None)
    assert (a["urgency_score"], a["news_sentiment"]) == (b["urgency_score"], b["news_sentiment"])
