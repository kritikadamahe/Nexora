"""
External signal service.

Turns social-media mentions about a product into the two numbers the Decision
Engine consumes: ``urgency_score`` (0..1) and ``news_sentiment``
(POSITIVE / NEGATIVE / NEUTRAL).

History
-------
In nexora-v0 the computed values were unconditionally overwritten with
``NEUTRAL`` / ``0.25`` just before returning, so no external signal ever
reached the Decision Engine. That overwrite has been removed. The old
behaviour is still available, but only as an explicit, named mode
(``legacy_neutral``) so baselines can reproduce v0 on purpose.

Signal source is chosen with the NEXORA_EXTERNAL_SIGNAL_MODE environment
variable (see .env.example):

    synthetic       seeded placeholder generator (default, deterministic)
    reddit          live Reddit through PRAW (needs credentials)
    legacy_neutral  v0 behaviour: always NEUTRAL, urgency 0.25
"""
import logging
import os
from typing import Optional, List

import numpy as np
from fastapi import HTTPException

from external_signal_service.sentiment import SentimentEngine
from external_signal_service.aggregator import SignalAggregator
from external_signal_service.schemas import ExternalSignals
from external_signal_service.providers.synthetic_provider import SyntheticProvider

logging.basicConfig(level=logging.INFO)

MODE_SYNTHETIC = "synthetic"
MODE_REDDIT = "reddit"
MODE_LEGACY_NEUTRAL = "legacy_neutral"
VALID_MODES = (MODE_SYNTHETIC, MODE_REDDIT, MODE_LEGACY_NEUTRAL)
DEFAULT_MODE = MODE_SYNTHETIC

# The exact constants nexora-v0 returned for every product.
LEGACY_NEUTRAL_URGENCY = 0.25
LEGACY_NEUTRAL_SENTIMENT = "NEUTRAL"

# Sentiment cut-offs and urgency formula are unchanged from v0
# (Build Plan Section 3.12): urgency = |sentiment| x mention weight x confidence.
SENTIMENT_THRESHOLD = 0.05
MENTION_WEIGHT_SATURATION = 10

sentiment_engine = SentimentEngine()


def get_signal_mode() -> str:
    mode = os.getenv("NEXORA_EXTERNAL_SIGNAL_MODE", DEFAULT_MODE).strip().lower()
    if mode not in VALID_MODES:
        raise ValueError(
            f"NEXORA_EXTERNAL_SIGNAL_MODE={mode!r} is invalid; choose one of {VALID_MODES}"
        )
    return mode


def get_base_seed() -> int:
    return int(os.getenv("NEXORA_SEED", "42"))


def build_provider(mode: str):
    """Creates the mention provider for a mode. Reddit is imported lazily so
    that praw / credentials are only required when that mode is selected."""
    if mode == MODE_SYNTHETIC:
        return SyntheticProvider(seed=get_base_seed())
    if mode == MODE_REDDIT:
        from external_signal_service.providers.reddit_provider import RedditProvider
        return RedditProvider()
    raise ValueError(f"No provider for mode {mode!r}")


def urgency_and_sentiment(signals: ExternalSignals) -> dict:
    """Pure function: aggregated signals -> {urgency_score, news_sentiment}."""
    mention_weight = min(signals.mention_volume / MENTION_WEIGHT_SATURATION, 1.0)
    urgency_score = abs(signals.average_sentiment) * mention_weight * signals.confidence_score
    urgency_score = float(np.clip(urgency_score, 0.0, 1.0))

    if signals.average_sentiment > SENTIMENT_THRESHOLD:
        news_sentiment = "POSITIVE"
    elif signals.average_sentiment < -SENTIMENT_THRESHOLD:
        news_sentiment = "NEGATIVE"
    else:
        news_sentiment = "NEUTRAL"

    return {"urgency_score": urgency_score, "news_sentiment": news_sentiment}


def _neutral_signals() -> ExternalSignals:
    return ExternalSignals(
        average_sentiment=0.0, positive_ratio=0.0, negative_ratio=0.0,
        mention_volume=0, unique_threads=0, trend_velocity="stable",
        confidence_score=0.0,
    )


def reddit_trend(
    product_name: str,
    days_window: int = 30,
    subreddits: Optional[List[str]] = None,
    provider=None,
    mode: Optional[str] = None,
):
    """
    Returns {product_name, time_window_days, external_signals, urgency_score,
    news_sentiment, mode}.

    The name and the first three positional arguments are unchanged so the
    Decision Engine call ``reddit_trend(product_name, 30, None)`` still works.
    ``provider`` / ``mode`` are optional overrides, mainly for tests.

    Errors are raised, not swallowed: silently falling back to NEUTRAL would
    make a failed signal look like "no news" and contaminate experiments.
    """
    try:
        mode = mode or get_signal_mode()

        if mode == MODE_LEGACY_NEUTRAL:
            return {
                "product_name": product_name,
                "time_window_days": days_window,
                "external_signals": _neutral_signals().model_dump(),
                "urgency_score": LEGACY_NEUTRAL_URGENCY,
                "news_sentiment": LEGACY_NEUTRAL_SENTIMENT,
                "mode": mode,
            }

        provider = provider or build_provider(mode)

        mentions = provider.fetch_mentions(product_name, days_window, subreddits)

        all_texts = []
        for m in mentions:
            all_texts.append(m["title"])
            all_texts.append(m["body"])
            all_texts.extend(m["comments"])

        sentiment_scores = sentiment_engine.analyze_texts(all_texts)

        signals = SignalAggregator.compute_signals(
            product_name=product_name,
            days_window=days_window,
            mentions=mentions,
            sentiment_scores=sentiment_scores,
        )

        derived = urgency_and_sentiment(signals)

        return {
            "product_name": product_name,
            "time_window_days": days_window,
            "external_signals": signals.model_dump(),
            "urgency_score": derived["urgency_score"],
            "news_sentiment": derived["news_sentiment"],
            "mode": mode,
        }

    except Exception as e:
        logging.exception("Trend analysis failed")
        raise HTTPException(status_code=500, detail=str(e))
