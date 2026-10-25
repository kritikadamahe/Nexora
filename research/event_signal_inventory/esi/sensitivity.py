"""One-factor sensitivity analysis on top of the existing experiment runner.

The sweep varies a single signal-error parameter, starting from one base condition of the
base config. Everything else (world, splits, arms, policy, costs, seeds, tau grid) is taken
unchanged from the base config, and the existing `experiment.run` does all modelling,
validation-only tuning and test evaluation.

Usage (from research/event_signal_inventory):
    python -m esi.sensitivity --config configs/sensitivity_false_alarm.json \
        --out results/sensitivity_false_alarm
"""
import argparse
import copy
import json
import os
import time

import numpy as np
import pandas as pd

from .experiment import run

SWEEPABLE = {"p_miss", "p_late", "spurious_rate", "p_misleading"}
COMPARE_COLS = ["tau_selected", "val_cost", "total_cost", "holding_cost", "shortage_cost",
                "waste_cost", "lost_units", "waste_units", "fill_rate", "waste_rate",
                "wape_median", "pinball_tau_norm"]


def condition_name(param, value):
    return f"{param}={value:g}"


def build_sensitivity_config(base_cfg, sweep):
    """Return a full experiment config whose `conditions` are the sweep points.
    The base config is deep-copied and never modified."""
    param, values, base_cond = sweep["parameter"], sweep["values"], sweep["base_condition"]
    if param not in SWEEPABLE:
        raise ValueError(f"parameter must be one of {sorted(SWEEPABLE)}, got {param!r}")
    if base_cond not in base_cfg["conditions"]:
        raise ValueError(f"base_condition {base_cond!r} not in base config conditions")
    if len(values) == 0 or len(set(values)) != len(values):
        raise ValueError("values must be a non-empty list without duplicates")
    for v in values:
        if v < 0 or (param != "spurious_rate" and v > 1):
            raise ValueError(f"invalid value {v} for {param}")
    cfg = copy.deepcopy(base_cfg)
    base_signal = cfg["conditions"][base_cond]
    cfg["conditions"] = {}
    for v in values:
        c = copy.deepcopy(base_signal)
        c[param] = float(v)
        cfg["conditions"][condition_name(param, v)] = c
    cfg["description"] = (f"Sensitivity of {param} over {values}, all other signal parameters "
                          f"from base condition {base_cond!r}; other settings from base config.")
    return cfg


def per_seed_table(by_seed):
    piv = by_seed.pivot_table(index=["condition", "seed"], columns="arm", values="total_cost")
    out = pd.DataFrame({
        "cost_A": piv["A_blind"], "cost_B": piv["B_clean_trained"],
        "cost_C": piv["C_asavailable_trained"],
        "C_vs_A": piv["C_asavailable_trained"] / piv["A_blind"] - 1,
        "C_vs_B": piv["C_asavailable_trained"] / piv["B_clean_trained"] - 1,
    }).reset_index()
    return out


def compare_with_baseline(by_seed, cond_name, baseline_csv, baseline_cond, seeds):
    """Compare one sweep condition with a condition of a previous run, seed by seed and arm
    by arm. Returns (DataFrame of max absolute differences, all_identical flag)."""
    base = pd.read_csv(baseline_csv, float_precision="round_trip")  # exact float round-trip
    base = base[(base.condition == baseline_cond) & (base.seed.isin(seeds))]
    new = by_seed[by_seed.condition == cond_name]
    m = new.merge(base, on=["seed", "arm"], suffixes=("_new", "_base"))
    if len(m) != len(new) or len(m) == 0:
        raise ValueError("baseline does not contain the same seeds and arms")
    rows = []
    for col in COMPARE_COLS:
        diff = np.abs(m[f"{col}_new"].astype(float) - m[f"{col}_base"].astype(float)).max()
        rows.append({"metric": col, "max_abs_diff": diff})
    df = pd.DataFrame(rows)
    return df, bool((df.max_abs_diff == 0).all())


def sensitivity_markdown(by_seed, paired, per_seed, check, cfg_sens, sweep, elapsed):
    order = [condition_name(sweep["parameter"], v) for v in sweep["values"]]
    cols = ["total_cost", "holding_cost", "shortage_cost", "waste_cost", "lost_units",
            "waste_units", "fill_rate"]
    L = [f"# Sensitivity: `{sweep['parameter']}` ∈ {sweep['values']}", "",
         f"Base condition: `{sweep['base_condition']}` of `{sweep['base_config']}`. Seeds: "
         f"{cfg_sens['seeds']} (same as baseline; no additional seeds). Runtime {elapsed:.0f}s.", "",
         "## Test-period metrics (mean ± sd across seeds; summed over SKUs)", "",
         "| condition | arm | " + " | ".join(cols) + " |", "|" + "---|" * (len(cols) + 2)]
    for c in order:
        for a in ["A_blind", "B_clean_trained", "C_asavailable_trained"]:
            d = by_seed[(by_seed.condition == c) & (by_seed.arm == a)]
            cells = [(("{:.3f} ± {:.3f}" if col == "fill_rate" else "{:.0f} ± {:.0f}")
                      .format(d[col].mean(), d[col].std())) for col in cols]
            L.append(f"| {c} | {a} | " + " | ".join(cells) + " |")
    L += ["", "## Paired relative total-cost differences (negative = C cheaper)", "",
          "95% bootstrap CI over (seed, SKU) units; seed count = seeds where C is cheaper.", "",
          "| condition | C vs A | 95% CI | seeds C<A | C vs B | 95% CI | seeds C<B |",
          "|---|---|---|---|---|---|---|"]
    for c in order:
        pa = paired[(paired.condition == c) & (paired.comparison == "C_asavailable_trained vs A_blind")].iloc[0]
        pb = paired[(paired.condition == c) & (paired.comparison == "C_asavailable_trained vs B_clean_trained")].iloc[0]
        ps = per_seed[per_seed.condition == c]
        n = len(ps)
        L.append(f"| {c} | {pa.rel_cost_diff:+.1%} | [{pa.ci95_low:+.1%}, {pa.ci95_high:+.1%}] | "
                 f"{(ps.C_vs_A < 0).sum()}/{n} | {pb.rel_cost_diff:+.1%} | "
                 f"[{pb.ci95_low:+.1%}, {pb.ci95_high:+.1%}] | {(ps.C_vs_B < 0).sum()}/{n} |")
    L += ["", "## Per-seed relative total cost", "",
          "| condition | seed | cost A | cost B | cost C | C vs A | C vs B |", "|---|---|---|---|---|---|---|"]
    for c in order:
        for _, r in per_seed[per_seed.condition == c].iterrows():
            L.append(f"| {c} | {r.seed} | {r.cost_A:.0f} | {r.cost_B:.0f} | {r.cost_C:.0f} | "
                     f"{r.C_vs_A:+.1%} | {r.C_vs_B:+.1%} |")
    if check is not None:
        df, same = check
        L += ["", f"## Baseline cross-check: `{sweep['baseline_check']['condition']}` vs "
              f"`{sweep['baseline_check']['baseline_condition']}` in "
              f"`{sweep['baseline_check']['baseline_metrics']}`", "",
              f"All compared metrics identical for every seed and arm: **{same}**", "",
              "| metric | max abs difference |", "|---|---|"]
        L += [f"| {r.metric} | {r.max_abs_diff:.6g} |" for _, r in df.iterrows()]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/sensitivity_false_alarm.json")
    ap.add_argument("--out", default="results/sensitivity_false_alarm")
    args = ap.parse_args()
    with open(args.config) as f:
        sweep = json.load(f)
    with open(sweep["base_config"]) as f:
        base_cfg = json.load(f)
    cfg = build_sensitivity_config(base_cfg, sweep)
    os.makedirs(args.out, exist_ok=True)
    with open(f"{args.out}/sensitivity_spec.json", "w") as f:
        json.dump(sweep, f, indent=2)
    t0 = time.time()
    by_seed, paired = run(cfg, args.out)                     # writes config.json etc.
    elapsed = time.time() - t0
    per_seed = per_seed_table(by_seed)
    per_seed.to_csv(f"{args.out}/per_seed_relative_cost.csv", index=False)
    check = None
    bc = sweep.get("baseline_check")
    if bc:
        check = compare_with_baseline(by_seed, bc["condition"], bc["baseline_metrics"],
                                      bc["baseline_condition"], cfg["seeds"])
        check[0].to_csv(f"{args.out}/baseline_check.csv", index=False)
    md = sensitivity_markdown(by_seed, paired, per_seed, check, cfg, sweep, elapsed)
    with open(f"{args.out}/sensitivity_results.md", "w") as f:
        f.write(md)
    print(md)


if __name__ == "__main__":
    main()
