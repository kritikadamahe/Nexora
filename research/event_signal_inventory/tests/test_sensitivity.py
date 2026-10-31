import copy, json, os
import numpy as np
import pandas as pd
import pytest

import esi.experiment as ex
from esi.sensitivity import build_sensitivity_config, compare_with_baseline, condition_name

HERE = os.path.dirname(os.path.abspath(__file__))
SMOKE = json.load(open(os.path.join(HERE, "..", "configs", "smoke.json")))
SWEEP = {"base_config": "configs/smoke.json", "base_condition": "clean",
         "parameter": "spurious_rate", "values": [0.0, 0.2]}


def test_sweep_config_changes_only_the_swept_parameter():
    base = copy.deepcopy(SMOKE)
    cfg = build_sensitivity_config(base, SWEEP)
    assert base == SMOKE                                     # base config not mutated
    assert list(cfg["conditions"]) == ["spurious_rate=0", "spurious_rate=0.2"]
    for v in SWEEP["values"]:
        c = cfg["conditions"][condition_name("spurious_rate", v)]
        expected = {**SMOKE["conditions"]["clean"], "spurious_rate": v}
        assert c == expected
    for k in SMOKE:
        if k not in ("conditions", "description"):
            assert cfg[k] == SMOKE[k]


@pytest.mark.parametrize("bad", [
    {"parameter": "lead_time"}, {"base_condition": "nope"}, {"values": []},
    {"values": [0.1, 0.1]}, {"values": [-0.1]}, {"parameter": "p_miss", "values": [1.5]}])
def test_invalid_sweep_specs_rejected(bad):
    with pytest.raises(ValueError):
        build_sensitivity_config(SMOKE, {**SWEEP, **bad})


def test_reproducible_and_zero_rate_equals_clean(tmp_path):
    cfg = build_sensitivity_config(SMOKE, SWEEP)
    a, _ = ex.run(cfg, str(tmp_path / "a"))
    b, _ = ex.run(cfg, str(tmp_path / "b"))
    pd.testing.assert_frame_equal(a, b)                      # same seeds -> identical results
    ex.run(SMOKE, str(tmp_path / "base"))
    _, same = compare_with_baseline(a, "spurious_rate=0", str(tmp_path / "base" / "metrics_by_seed.csv"),
                                    "clean", SMOKE["seeds"])
    assert same
    _, same_hi = compare_with_baseline(a, "spurious_rate=0.2", str(tmp_path / "base" / "metrics_by_seed.csv"),
                                       "clean", SMOKE["seeds"])
    assert not same_hi                                       # the check can detect differences


def test_model_selection_does_not_see_test_period(tmp_path, monkeypatch):
    cfg = build_sensitivity_config(SMOKE, SWEEP)
    clean_run, _ = ex.run(cfg, str(tmp_path / "orig"))
    real = ex.generate_world

    def corrupted(wcfg, seed):
        w = real(wcfg, seed)
        w.demand[:, cfg["split"]["val_end"]:] *= 7           # change only test-period demand
        return w

    monkeypatch.setattr(ex, "generate_world", corrupted)
    corrupt_run, _ = ex.run(cfg, str(tmp_path / "corrupt"))
    for col in ["tau_selected", "val_cost"]:
        np.testing.assert_array_equal(clean_run[col].values, corrupt_run[col].values)
    assert not np.array_equal(clean_run["total_cost"].values, corrupt_run["total_cost"].values)


def test_grid_configs_scale_strength_and_keep_base_unchanged():
    import copy
    from esi.grid import build_grid_configs, summarize_grid
    base = json.load(open(os.path.join(os.path.dirname(__file__), "..", "configs", "smoke.json")))
    before = copy.deepcopy(base)
    spec = {"parameter": "spurious_rate", "values": [0.0, 0.1], "strengths": [0.5, 1.0],
            "base_condition": list(base["conditions"])[0], "seeds": [0]}
    cfgs = build_grid_configs(base, spec)
    assert base == before
    up = base["world"]["event_type_log_uplift"]
    assert cfgs[0.5]["world"]["event_type_log_uplift"] == [0.5 * u for u in up]
    assert list(cfgs[1.0]["conditions"]) == ["spurious_rate=0", "spurious_rate=0.1"]
    with pytest.raises(ValueError):
        build_grid_configs({**base, "data": {"source": "favorita"}}, spec)
    rows = [{"strength": 1.0, "condition": "c", "seed": s, "arm": a, "total_cost": v}
            for s in (0, 1) for a, v in [("A_blind", 100.0), ("B_clean_trained", 110.0),
                                          ("C_asavailable_trained", 90.0)]]
    summ = summarize_grid(pd.DataFrame(rows)).set_index("comparison")
    assert summ.loc["C_asavailable_trained vs A_blind", "mean_rel_diff"] == pytest.approx(-0.1)
    assert summ.loc["B_clean_trained vs A_blind", "seeds_first_cheaper"] == 0
