"""Train/serve error-rate mismatch for noise-injected training (arm D), synthetic worlds only.

Arm D trains on the true calendar corrupted with simulated signal errors at an ASSUMED rate
p1, and is then served real-time signals whose errors occur at the TRUE rate p2. This sweep
crosses p1 x p2 for one error parameter (by default the false-alarm rate `spurious_rate`)
at several event strengths, and asks how wrong the assumed rate can be before D loses its
advantage over clean-calendar training (B) and over ignoring events (A).

Per seed and strength: A and B are fitted once; C is fitted once per served rate (trained on
that signal process, so it is the "correct rate, real archive" reference); D is fitted once
per assumed rate. Every model is served the same signal realisation for a given p2, so all
comparisons within a p2 column are paired. Tau is tuned on validation cost only, exactly as
in `esi.experiment`.

Usage (from research/event_signal_inventory):
    python -m esi.mismatch --config configs/mismatch_false_alarm.json --out results/mismatch_false_alarm
"""
import argparse
import copy
import json
import os
import time

import numpy as np
import pandas as pd

from .clustered_ci import signflip_p
from .experiment import D_SEED_OFFSET, environment, evaluate_arm, make_origins
from .forecasting import QuantileForecaster, build_X, targets
from .generator import generate_world
from .sensitivity import SWEEPABLE
from .signals import clean_calendar, generate_signals


def strength_config(base_cfg, strength, seeds):
    if "data" in base_cfg:
        raise ValueError("the mismatch sweep needs a synthetic base config (event strength is a world setting)")
    cfg = copy.deepcopy(base_cfg)
    cfg["seeds"] = seeds
    cfg["world"]["event_type_log_uplift"] = [strength * u for u in base_cfg["world"]["event_type_log_uplift"]]
    return cfg


def run_strength(cfg, base_signal, param, train_values, serve_values, strength):
    L, K = cfg["lead_time"], cfg["world"]["n_event_types"]
    T, tr_end, va_end = cfg["world"]["n_days"], cfg["split"]["train_end"], cfg["split"]["val_end"]
    tr_or, _, _ = make_origins(T, tr_end, va_end, L)
    uplift = cfg["world"]["event_type_log_uplift"]

    def signal_cfg(v):
        c = copy.deepcopy(base_signal)
        c[param] = float(v)
        return c

    rows, t0 = [], time.time()
    for seed in cfg["seeds"]:
        world = generate_world(cfg["world"], seed)
        D = world.demand
        y_tr = targets(D, tr_or, L)

        def fit(ann_train):
            X, s = build_X(D, tr_or, L, ann_train, K)
            return QuantileForecaster(cfg["quantile_grid"], cfg["model_params"], seed).fit(X, y_tr, s)

        model_A, model_B = fit(None), fit(clean_calendar(world.events, cfg["clean_lead_days"]))
        model_D = {v1: fit(generate_signals(world.events, T, K, uplift, signal_cfg(v1),
                                            seed=seed * 1000 + i + 1 + D_SEED_OFFSET))
                   for i, v1 in enumerate(train_values)}
        for j, v2 in enumerate(serve_values):
            served = generate_signals(world.events, T, K, uplift, signal_cfg(v2), seed=seed * 1000 + j + 1)
            arms = [("A_blind", None, model_A, None), ("B_clean_trained", None, model_B, served),
                    ("C_asavailable_trained", v2, fit(served), served)]
            arms += [("D_noise_injected", v1, m, served) for v1, m in model_D.items()]
            for arm, assumed, model, serve in arms:
                r, _ = evaluate_arm(cfg, D, world.events, model, serve)
                rows.append({"strength": strength, "seed": seed, "served": v2, "arm": arm,
                             "assumed": assumed, "total_cost": r["total_cost"],
                             "tau_selected": r["tau_selected"]})
        print(f"strength {strength:g} seed {seed} done ({time.time() - t0:.0f}s)", flush=True)
    return pd.DataFrame(rows)


def summarize(by_seed):
    """Per (strength, served, assumed): per-seed relative cost of D against A, B and C."""
    out = []
    for (s, v2), g in by_seed.groupby(["strength", "served"], sort=False):
        ref = {a: g[g.arm == a].set_index("seed").total_cost for a in
               ("A_blind", "B_clean_trained", "C_asavailable_trained")}
        cands = [("C_asavailable_trained", v2, ref["C_asavailable_trained"])]
        cands += [("D_noise_injected", v1, d.set_index("seed").total_cost)
                  for v1, d in g[g.arm == "D_noise_injected"].groupby("assumed", sort=False)]
        for arm, v1, cost in cands:
            for vs, base in (("A_blind", ref["A_blind"]), ("B_clean_trained", ref["B_clean_trained"]),
                             ("C_asavailable_trained", ref["C_asavailable_trained"])):
                if arm == vs:
                    continue
                d = (cost / base.reindex(cost.index) - 1).values
                out.append({"strength": s, "served": v2, "arm": arm, "assumed": v1, "vs": vs,
                            "mean_rel_diff": d.mean(), "seeds_first_cheaper": int((d < 0).sum()),
                            "n_seeds": len(d), "signflip_p": signflip_p(d) if np.any(d != 0) else 1.0})
    return pd.DataFrame(out)


def mismatch_markdown(summary, spec, elapsed):
    p = spec["parameter"]
    L = [f"# Train/serve mismatch in {p} (arm D)", "",
         f"Base config `{spec['base_config']}`, base condition `{spec['base_condition']}`, "
         f"seeds {spec['seeds']}. Runtime {elapsed:.0f}s.", "",
         f"Rows: {p} ASSUMED when injecting noise into D's training calendar. Columns: TRUE {p} of the "
         "served signals. Cells: mean per-seed relative test-cost difference (negative = D cheaper), then "
         "seeds where D was cheaper and the exact sign-flip p (not multiplicity-corrected). The C row is "
         "the as-available reference (trained on the true process).", ""]
    for s, gs in summary.groupby("strength", sort=False):
        serves = list(dict.fromkeys(gs.served))
        for vs in ("A_blind", "B_clean_trained", "C_asavailable_trained"):
            sub = gs[gs.vs == vs]
            L += [f"## strength {s:g}: vs {vs}", "",
                  f"| assumed \\ true {p} | " + " | ".join(f"{v:g}" for v in serves) + " |",
                  "|---|" + "---|" * len(serves)]
            if vs != "C_asavailable_trained":
                c = sub[sub.arm == "C_asavailable_trained"].set_index("served")
                L.append("| C (as-available) | " + " | ".join(
                    f"{c.loc[v, 'mean_rel_diff']:+.1%}" for v in serves) + " |")
            d = sub[sub.arm == "D_noise_injected"]
            for v1, g in d.groupby("assumed", sort=False):
                g = g.set_index("served")
                L.append(f"| D, assumed {v1:g} | " + " | ".join(
                    f"{g.loc[v, 'mean_rel_diff']:+.1%} ({g.loc[v, 'seeds_first_cheaper']}/{g.loc[v, 'n_seeds']}, "
                    f"p={g.loc[v, 'signflip_p']:.3f})" for v in serves) + " |")
            L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    spec = json.load(open(args.config))
    if spec["parameter"] not in SWEEPABLE:
        raise ValueError(f"parameter must be one of {sorted(SWEEPABLE)}, got {spec['parameter']!r}")
    base_cfg = json.load(open(spec["base_config"]))
    base_signal = base_cfg["conditions"][spec["base_condition"]]
    os.makedirs(args.out, exist_ok=True)
    json.dump(spec, open(f"{args.out}/mismatch_spec.json", "w"), indent=2)
    t0, parts = time.time(), []
    for s in spec["strengths"]:
        cfg = strength_config(base_cfg, s, spec["seeds"])
        parts.append(run_strength(cfg, base_signal, spec["parameter"], spec["train_values"],
                                  spec["serve_values"], s))
    by_seed = pd.concat(parts, ignore_index=True)
    by_seed.to_csv(f"{args.out}/metrics_by_seed.csv", index=False)
    summary = summarize(by_seed)
    summary.to_csv(f"{args.out}/mismatch_summary.csv", index=False)
    json.dump(environment(), open(f"{args.out}/environment.json", "w"), indent=2)
    md = mismatch_markdown(summary, spec, time.time() - t0)
    open(f"{args.out}/mismatch_results.md", "w").write(md)
    print(md)


if __name__ == "__main__":
    main()
