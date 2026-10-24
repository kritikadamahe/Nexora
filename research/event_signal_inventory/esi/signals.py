"""Event signals as they become available over time.

A signal is an announcement (announce_day, start_day, duration, event_type). At decision
origin t an announcement is visible only if announce_day <= t. This is the single rule
that prevents future-information leakage from the signal channel.

Error process (configurable):
  p_miss        : a true event is never announced
  p_late        : a true event is announced only `late_lead` days before its start
  lead_days     : announcement lead for on-time true events
  spurious_rate : expected spurious (false) announcements started per day
  p_misleading  : a spurious announcement is labelled as the highest-uplift event type
"""
import numpy as np


def clean_calendar(events, lead_days: int):
    """Perfect information: every true event announced `lead_days` before it starts."""
    return [(s - lead_days, s, d, k) for (s, d, k) in events]


def generate_signals(events, n_days, n_types, type_log_uplift, scfg: dict, seed: int):
    rng = np.random.default_rng(seed)
    ann = []
    for (s, d, k) in events:
        if rng.random() < scfg["p_miss"]:
            continue
        lead = scfg["late_lead"] if rng.random() < scfg["p_late"] else scfg["lead_days"]
        ann.append((s - lead, s, d, k))
    n_spur = rng.poisson(scfg["spurious_rate"] * n_days)
    top_type = int(np.argmax(type_log_uplift)) + 1
    for _ in range(n_spur):
        s = int(rng.integers(0, n_days))
        d = int(rng.integers(1, 3))
        k = top_type if rng.random() < scfg["p_misleading"] else int(rng.integers(1, n_types + 1))
        ann.append((s - scfg["lead_days"], s, d, k))
    return ann


def visible_window_features(announcements, origin: int, days, n_types: int) -> np.ndarray:
    """Count of days in `days` covered by each event type, using only announcements
    with announce_day <= origin. Returns vector of length n_types."""
    feats = np.zeros(n_types)
    for k in range(1, n_types + 1):
        covered = set()
        for (a, s, d, kk) in announcements:
            if kk != k or a > origin:
                continue
            for day in days:
                if s <= day < s + d:
                    covered.add(day)
        feats[k - 1] = len(covered)
    return feats


def window_feature_table(announcements, origins, L: int, n_types: int) -> np.ndarray:
    """Vectorised over origins: rows = origins, cols = event types; window = origin..origin+L."""
    ann = np.array(announcements, dtype=int).reshape(-1, 4)
    out = np.zeros((len(origins), n_types))
    for j, t in enumerate(origins):
        vis = ann[ann[:, 0] <= t]
        if len(vis) == 0:
            continue
        for k in range(1, n_types + 1):
            vk = vis[vis[:, 3] == k]
            if len(vk) == 0:
                continue
            days = np.arange(t, t + L + 1)
            cov = ((days[:, None] >= vk[None, :, 1]) & (days[:, None] < vk[None, :, 1] + vk[None, :, 2])).any(axis=1)
            out[j, k - 1] = cov.sum()
    return out
