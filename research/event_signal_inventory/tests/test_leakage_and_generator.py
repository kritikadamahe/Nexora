import json, os
import numpy as np
from esi.forecasting import build_X, targets, MIN_HISTORY
from esi.generator import generate_world
from esi.experiment import make_origins

CFG = json.load(open(os.path.join(os.path.dirname(__file__), "..", "configs", "smoke.json")))


def test_features_do_not_use_current_or_future_demand():
    w = generate_world(CFG["world"], 0)
    origins = np.arange(60, 120)
    X1, s1 = build_X(w.demand, origins, 2, None, 3)
    for t in origins[::10]:
        D2 = w.demand.copy()
        D2[:, t:] = 10_000                               # corrupt day t and everything after
        Xa, sa = build_X(w.demand, [t], 2, None, 3)
        Xb, sb = build_X(D2, [t], 2, None, 3)
        np.testing.assert_array_equal(Xa, Xb)
        np.testing.assert_array_equal(sa, sb)


def test_event_features_ignore_not_yet_announced_signals():
    w = generate_world(CFG["world"], 0)
    ann = [(30, 100, 2, 1)]
    future = ann + [(81, 81, 3, 2), (200, 82, 2, 3)]      # announced after origin 80
    Xa, _ = build_X(w.demand, [80], 2, ann, 3)
    Xb, _ = build_X(w.demand, [80], 2, future, 3)
    np.testing.assert_array_equal(Xa, Xb)


def test_targets_are_window_sums():
    w = generate_world(CFG["world"], 0)
    y = targets(w.demand, [50, 51], 2)
    assert y[0] == w.demand[0, 50:53].sum() and y[2] == w.demand[1, 50:53].sum()


def test_split_origins_do_not_overlap_or_leak():
    T, tr, va, L = 730, 420, 560, 2
    o_tr, o_va, o_te = make_origins(T, tr, va, L)
    assert o_tr.min() >= MIN_HISTORY
    assert o_tr.max() + L < tr                            # training targets inside train period
    assert o_va.min() == tr and o_va.max() < va and o_te.min() == va and o_te.max() + L < T


def test_generator_reproducible_and_events_raise_demand():
    a, b, c = (generate_world(CFG["world"], s) for s in (7, 7, 8))
    np.testing.assert_array_equal(a.demand, b.demand)
    assert a.events == b.events and not np.array_equal(a.demand, c.demand)
    big = generate_world({**CFG["world"], "n_sku": 50, "n_days": 2000}, 1)
    resp = (big.uplift[:, 1:] > 0.3).all(axis=1)
    ev = big.event_type > 0
    assert big.demand[resp][:, ev].mean() > 1.3 * big.demand[resp][:, ~ev].mean()
