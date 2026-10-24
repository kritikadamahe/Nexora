import numpy as np
from esi.signals import (clean_calendar, generate_signals, visible_window_features,
                         window_feature_table)

SCFG = {"p_miss": 0.0, "p_late": 0.0, "late_lead": 0, "lead_days": 5,
        "spurious_rate": 0.0, "p_misleading": 0.0}


def test_announcement_visible_only_from_announce_day():
    ann = [(10, 14, 2, 1)]                  # announced day 10, event days 14-15, type 1
    f = lambda t: window_feature_table(ann, [t], 4, 2)[0]
    assert f(9)[0] == 0                      # day 9: not yet announced
    assert f(10)[0] == 1                     # window 10..14 covers day 14
    assert f(12)[0] == 2                     # window 12..16 covers 14, 15


def test_late_signal_arrives_on_event_start():
    events = [(50, 2, 1)]
    ann = generate_signals(events, 100, 2, [0.5, 1.0], {**SCFG, "p_late": 1.0, "late_lead": 0}, 0)
    assert ann == [(50, 50, 2, 1)]
    assert window_feature_table(ann, [49], 2, 2)[0].sum() == 0
    assert window_feature_table(ann, [50], 2, 2)[0][0] == 2


def test_clean_calendar_and_misses():
    events = [(20, 1, 1), (40, 3, 2)]
    assert clean_calendar(events, 14) == [(6, 20, 1, 1), (26, 40, 3, 2)]
    assert generate_signals(events, 60, 2, [0.5, 1.0], {**SCFG, "p_miss": 1.0}, 0) == []
    no_err = generate_signals(events, 60, 2, [0.5, 1.0], SCFG, 0)
    assert no_err == clean_calendar(events, 5)


def test_misleading_spurious_use_top_type():
    ann = generate_signals([], 1000, 3, [0.2, 1.5, 0.4],
                           {**SCFG, "spurious_rate": 0.05, "p_misleading": 1.0}, 1)
    assert len(ann) > 0 and all(a[3] == 2 for a in ann)


def test_vectorised_matches_reference():
    rng = np.random.default_rng(3)
    ann = [(int(rng.integers(0, 90)), int(rng.integers(0, 100)), int(rng.integers(1, 4)),
            int(rng.integers(1, 4))) for _ in range(30)]
    for t in range(0, 100, 7):
        np.testing.assert_array_equal(window_feature_table(ann, [t], 2, 3)[0],
                                      visible_window_features(ann, t, range(t, t + 3), 3))
