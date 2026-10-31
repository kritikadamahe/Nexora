"""Two-factor sweep: event strength x one signal-error parameter (synthetic worlds only).

Event strength scales the base config's `event_type_log_uplift` (1.0 = unchanged; the
Favorita panel's training-period log-uplifts are roughly 0.1 of the synthetic defaults).
For each strength the existing `experiment.run` is called once with one condition per
error value, so modelling, validation-only tuning and test evaluation are unchanged.
The summary reports per-seed relative cost differences (each seed is an independent world).

Usage (from research/event_signal_inventory):
    python -m esi.grid --config configs/grid_strength_false_alarm.json --out results/grid_strength_false_alarm
"""
import argparse
import copy
import json
import os
import time

import numpy as np
import pandas as pd

from .clustered_ci import COMPARISONS, signflip_p
from .experiment import run
from .sensitivity import SWEEPABLE, condition_name


def build_grid_configs(base_cfg, spec):
    """Return {strength: experiment config}. The base config is never modified."""
    param, values = spec["parameter"], spec["values"]
    if param not in SWEEPABLE:
        raise ValueError(f"parameter must be one of {sorted(SWEEPABLE)}, got {param!r}")
    if "data" in base_cfg:
        raise ValueError("the grid sweep needs a synthetic base config (event strength is a world setting)")
    base_signal = base_cfg["conditions"][spec["base_condition"]]
    out = {}
    for s in spec["strengths"]:
        if s < 0:
            raise ValueError(f"invalid strength {s}")
        cfg = copy.deepcopy(base_cfg)
        cfg["seeds"] = spec.get("seeds", cfg["seeds"])
        cfg["world"]["event_type_log_uplift"] = [s * u for u in base_cfg["world"]["event_type_log_uplift"]]
        cfg["conditions"] = {}
        for v in values:
            c = copy.deepcopy(base_signal)
            c[param] = float(v)
            cfg["conditions"][condition_name(param, v)] = c
        cfg["description"] = f"Grid cell set: event strength {s:g}, {param} over {values}."
        out[s] = cfg
    return out


def summarize_grid(by_seed_all):
    """Per (strength, condition, comparison): mean and range of per-seed relative cost
    differences, seeds where the first arm is cheaper, and the exact sign-flip p."""
    rows = []
    for (s, cond), g in by_seed_all.groupby(["strength", "condition"], sort=False):
        piv = g.pivot_table(index="seed", columns="arm", values="total_cost")
        for a, b in COMPARISONS:
            d = (piv[a] / piv[b] - 1).values
            rows.append({"strength": s, "condition": cond, "comparison": f"{a} vs {b}",
                         "mean_rel_diff": d.mean(), "min": d.min(), "max": d.max(),
                         "seeds_first_cheaper": int((d < 0).sum()), "n_seeds": len(d),
                         "signflip_p": signflip_p(d) if np.any(d != 0) else 1.0})
    return pd.DataFrame(rows)


def grid_markdown(summary, spec, elapsed):
    L = [f"# Event strength x {spec['parameter']}", "",
         f"Base config `{spec['base_config']}`, base condition `{spec['base_condition']}`, "
         f"seeds {spec.get('seeds')}. Runtime {elapsed:.0f}s.", "",
         "Cells: mean per-seed relative test-cost difference (negative = first arm cheaper), "
         "then seeds where the first arm was cheaper and the exact sign-flip p (not multiplicity-corrected).", ""]
    for comp in summary.comparison.unique():
        sub = summary[summary.comparison == comp]
        conds = list(dict.fromkeys(sub.condition))
        L += [f"## {comp}", "", "| strength | " + " | ".join(conds) + " |", "|---|" + "---|" * len(conds)]
        for s, g in sub.groupby("strength", sort=False):
            g = g.set_index("condition")
            L.append(f"| {s:g} | " + " | ".join(
                f"{g.loc[c, 'mean_rel_diff']:+.1%} ({g.loc[c, 'seeds_first_cheaper']}/{g.loc[c, 'n_seeds']}, "
                f"p={g.loc[c, 'signflip_p']:.3f})" for c in conds) + " |")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    spec = json.load(open(args.config))
    base_cfg = json.load(open(spec["base_config"]))
    cfgs = build_grid_configs(base_cfg, spec)
    os.makedirs(args.out, exist_ok=True)
    json.dump(spec, open(f"{args.out}/grid_spec.json", "w"), indent=2)
    t0, parts = time.time(), []
    for s, cfg in cfgs.items():
        by_seed, _ = run(cfg, os.path.join(args.out, f"strength={s:g}"))
        parts.append(by_seed.assign(strength=s))
    by_seed_all = pd.concat(parts, ignore_index=True)
    by_seed_all.to_csv(f"{args.out}/metrics_by_seed_all.csv", index=False)
    summary = summarize_grid(by_seed_all)
    summary.to_csv(f"{args.out}/grid_summary.csv", index=False)
    md = grid_markdown(summary, spec, time.time() - t0)
    open(f"{args.out}/grid_results.md", "w").write(md)
    print(md)


if __name__ == "__main__":
    main()
