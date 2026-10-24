"""Synthetic daily retail demand with heterogeneous calendar-event effects.

Demand D[i, t] ~ NegativeBinomial(mean = mu[i, t], dispersion = cfg.nb_dispersion), with
    mu[i, t] = base[i] * weekday[i, t % 7] * trend[i, t] * event_mult[i, t]
event_mult[i, t] = exp(uplift[i, k]) if an event of type k is active on day t, else 1.

All randomness comes from one numpy Generator seeded by `seed`.
"""
from dataclasses import dataclass
import numpy as np


@dataclass
class World:
    demand: np.ndarray          # (n_sku, T) int, true (uncensored) demand
    event_type: np.ndarray      # (T,) int, 0 = no event, k = 1..K active event type
    events: list                # list of (start_day, duration, type) true event occurrences
    uplift: np.ndarray          # (n_sku, K+1) log-uplift; column 0 is 0
    base: np.ndarray            # (n_sku,) base daily mean


def generate_world(cfg: dict, seed: int) -> World:
    rng = np.random.default_rng(seed)
    n, T, K = cfg["n_sku"], cfg["n_days"], cfg["n_event_types"]

    base = np.exp(rng.normal(np.log(cfg["base_mean"]), cfg["base_log_sd"], size=n))
    weekday = np.exp(rng.normal(0.0, cfg["weekday_log_sd"], size=(n, 7)))
    weekday /= weekday.mean(axis=1, keepdims=True)
    slope = rng.normal(0.0, cfg["trend_sd"], size=n)  # relative change over the horizon
    trend = 1.0 + slope[:, None] * (np.arange(T)[None, :] / T)
    trend = np.clip(trend, 0.3, None)

    # Event-type mean log-uplifts (heterogeneous across types) and SKU-level deviations.
    type_mu = np.array(cfg["event_type_log_uplift"], dtype=float)
    assert len(type_mu) == K
    uplift = np.zeros((n, K + 1))
    uplift[:, 1:] = type_mu[None, :] + rng.normal(0.0, cfg["event_sku_log_sd"], size=(n, K))
    # A fraction of SKUs does not respond to events at all.
    nonresp = rng.random(n) < cfg["frac_sku_unresponsive"]
    uplift[nonresp, 1:] = 0.0

    # Non-overlapping event occurrences.
    event_type = np.zeros(T, dtype=int)
    events = []
    t = int(rng.integers(5, 15))
    while t < T:
        dur = int(rng.integers(cfg["event_min_days"], cfg["event_max_days"] + 1))
        k = int(rng.integers(1, K + 1))
        end = min(T, t + dur)
        event_type[t:end] = k
        events.append((t, end - t, k))
        t = end + int(rng.integers(cfg["event_gap_min"], cfg["event_gap_max"] + 1))

    mult = np.exp(uplift[:, event_type])                      # (n, T)
    mu = base[:, None] * weekday[:, np.arange(T) % 7] * trend * mult
    r = cfg["nb_dispersion"]
    demand = rng.negative_binomial(r, r / (r + mu)).astype(int)
    return World(demand=demand, event_type=event_type, events=events, uplift=uplift, base=base)
