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
