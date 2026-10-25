"""Invariants added during the validation pass."""
import json, os
import numpy as np
import pandas as pd
import pytest

import esi.experiment as ex
from esi.clustered_ci import analyse, clustered_comparison, signflip_p
from esi.forecasting import base_features
from esi.generator import generate_world
from esi.inventory import simulate
from esi.signals import generate_signals

HERE = os.path.dirname(os.path.abspath(__file__))
SMOKE = json.load(open(os.path.join(HERE, "..", "configs", "smoke.json")))
COSTS = {"holding": 0.05, "shortage": 1.0, "waste": 0.6}


def test_long_lead_time_rejected_to_prevent_seasonal_naive_leak():
    d = np.ones((1, 100))
    base_features(d, [50], 6)                                # L+1 = 7: window ends at t-1
    with pytest.raises(ValueError):
        base_features(d, [50], 7)                            # would include day t


def test_orders_do_not_depend_on_same_day_or_future_demand():
    rng = np.random.default_rng(1)
    T, L, m = 80, 2, 4
    d = rng.poisson(8, T)
    S = rng.uniform(10, 40, T); M = S * 0.7
    base = simulate(d, S, M, L, m, COSTS, init_stock=10)
    for k in (10, 40, 70):
        d2 = d.copy(); d2[k:] = rng.poisson(30, T - k)
        alt = simulate(d2, S, M, L, m, COSTS, init_stock=10)
        np.testing.assert_array_equal(base["order"][:k + 1], alt["order"][:k + 1])


def test_signal_error_rates_match_configuration():
    events = [(s, 2, 1 + s % 3) for s in range(20, 200_000, 20)]
    base = {"p_miss": 0.3, "p_late": 0.3, "late_lead": 0, "lead_days": 14,
            "spurious_rate": 0.0, "p_misleading": 0.5}
    ann = generate_signals(events, 200_000, 3, [0.4, 0.8, 1.2], base, seed=5)
    assert abs(1 - len(ann) / len(events) - 0.3) < 0.01                # misses
    assert all(a[1] - a[0] in (0, 14) for a in ann)
    assert abs(np.mean([a[1] - a[0] == 0 for a in ann]) - 0.3) < 0.01  # late = on start day
    spur = generate_signals([], 200_000, 3, [0.4, 0.8, 1.2],
                            {**base, "spurious_rate": 0.04}, seed=6)
    assert abs(len(spur) / 200_000 - 0.04) < 0.003                     # false alarms per day
    assert all(a[1] - a[0] == 14 for a in spur)                         # announced on time
    top = np.mean([a[3] == 3 for a in spur])
    assert abs(top - (0.5 + 0.5 / 3)) < 0.02                           # misleading labels


def test_arms_share_world_costs_periods_and_clean_b_equals_c(tmp_path):
    by_seed, _ = ex.run(SMOKE, str(tmp_path))
    sku = pd.read_csv(tmp_path / "metrics_by_sku.csv")
    # every arm/condition evaluated on the same SKUs and the same test demand
    dem = sku.groupby(["condition", "arm"]).demand.sum()
    assert dem.nunique() == 1
    clean = by_seed[by_seed.condition == "clean"].set_index("arm")
    for col in ["total_cost", "tau_selected", "waste_units", "lost_units"]:
        assert clean.loc["B_clean_trained", col] == clean.loc["C_asavailable_trained", col]
    a = by_seed[by_seed.arm == "A_blind"]
    assert a.total_cost.nunique() == 1                                 # A ignores signals


def test_signflip_and_identical_arms():
    assert signflip_p([-1, -2, -3, -4, -5]) == pytest.approx(2 / 32)
    assert signflip_p([1, -1, 1, -1]) == 1.0
    x = np.arange(1, 21, dtype=float); seeds = np.repeat([0, 1, 2, 3], 5)
    r = clustered_comparison(x, x.copy(), seeds, 200, np.random.default_rng(0))
    for k in ["rel_cost_diff", "iid_low", "iid_high", "cluster_low", "cluster_high",
              "twostage_low", "twostage_high"]:
        assert r[k] == 0


def test_cluster_interval_wider_when_seeds_disagree():
    rng = np.random.default_rng(0)
    seeds = np.repeat(np.arange(5), 40)
    y = rng.uniform(90, 110, 200)
    effect = np.repeat([-0.3, -0.2, 0.0, 0.1, 0.25], 40)               # strong seed-level effect
    x = y * (1 + effect + rng.normal(0, 0.01, 200))
    r = clustered_comparison(x, y, seeds, 2000, np.random.default_rng(1))
    assert (r["twostage_high"] - r["twostage_low"]) > 3 * (r["iid_high"] - r["iid_low"])


def test_analyse_runs_on_saved_results_format():
    sku = pd.DataFrame({"condition": "c", "seed": np.repeat([0, 1], 6),
                        "sku": np.tile(np.arange(2), 6),
                        "arm": np.tile(np.repeat(["A_blind", "B_clean_trained", "C_asavailable_trained"], 2), 2),
                        "cost": np.arange(12, dtype=float) + 10})
    df = analyse(sku, reps=50)
    assert len(df) == 3 and set(df.n_seeds) == {2}
