import hashlib
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .base_provider import BaseSocialProvider


def derive_seed(base_seed: int, *parts) -> int:
    """
    Stable 32-bit seed derived from a base seed and arbitrary labels.

    Python's built-in hash() is randomised per process, so it must not be used
    for reproducibility. SHA-256 of the labels is identical on every machine.
    """
    key = "|".join([str(base_seed), *[str(p) for p in parts]])
    return int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:8], 16)


class SyntheticProvider(BaseSocialProvider):
    """
    Placeholder social-media generator (NOT a model of real consumer behaviour).

    Its templates are generic gadget-style sentences and the generated volume /
    sentiment are independent of any sales data. It exists only so the pipeline
    can run without Reddit credentials. Experiments that need news with a known
    causal effect on demand use the Phase-1 simulator instead.

    seed=None  -> fresh, non-reproducible randomness (original v0 behaviour).
    seed=<int> -> mentions are a deterministic function of
                  (seed, product_name, days_window).
    """

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self.positive_templates = [
            "{product} battery life is insane",
            "Loving the new {product}",
            "{product} exceeded my expectations",
            "Best purchase ever: {product}",
        ]

        self.negative_templates = [
            "{product} is overpriced",
            "Very disappointed with {product}",
            "{product} heating issues are real",
            "Worst upgrade ever: {product}",
        ]

        self.neutral_templates = [
            "Thinking of buying {product}",
            "Is {product} worth it?",
            "{product} vs competitors?",
            "Anyone using {product}?",
        ]

    def _make_rngs(self, product_name: str, days_window: int):
        if self.seed is None:
            return random.Random(), np.random.default_rng()
        s = derive_seed(self.seed, product_name, days_window)
        return random.Random(s), np.random.default_rng(s)

    def _generate_text(self, product: str, sentiment: str, rng: random.Random):

        if sentiment == "positive":
            template = rng.choice(self.positive_templates)
        elif sentiment == "negative":
            template = rng.choice(self.negative_templates)
        else:
            template = rng.choice(self.neutral_templates)

        return template.format(product=product)

    def fetch_mentions(
        self,
        product_name: str,
        days_window: int,
        subreddits: List[str]
    ) -> List[Dict]:

        rng, np_rng = self._make_rngs(product_name, days_window)

        now = datetime.utcnow()

        # Simulate trend velocity behavior
        trend_type = rng.choice(["increasing", "decreasing", "stable"])

        base_volume = rng.randint(80, 200)

        mentions = []

        for i in range(base_volume):

            if trend_type == "increasing":
                day_offset = int(np_rng.exponential(scale=days_window / 4))
            elif trend_type == "decreasing":
                day_offset = days_window - int(np_rng.exponential(scale=days_window / 4))
            else:
                day_offset = rng.randint(0, days_window)

            day_offset = max(0, min(days_window - 1, day_offset))

            created_time = now - timedelta(days=day_offset)

            sentiment_distribution = np_rng.choice(
                ["positive", "negative", "neutral"],
                p=[0.4, 0.35, 0.25]
            )

            title = self._generate_text(product_name, sentiment_distribution, rng)
            body = self._generate_text(product_name, sentiment_distribution, rng)

            comments = [
                self._generate_text(product_name, np_rng.choice(
                    ["positive", "negative", "neutral"],
                    p=[0.4, 0.35, 0.25]
                ), rng)
                for _ in range(rng.randint(2, 8))
            ]

            # Realistic upvote distribution (power law)
            upvotes = int(np_rng.pareto(a=2) * 50)

            mentions.append({
                "thread_id": f"synthetic_{i}",
                "title": title,
                "body": body,
                "comments": comments,
                "upvotes": upvotes,
                "created_utc": created_time.timestamp()
            })

        return mentions
