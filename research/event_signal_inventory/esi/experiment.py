"""Run the event-signal-quality experiment.

Usage (from research/event_signal_inventory):
    python -m esi.experiment --config configs/small.json --out results/small
"""
import argparse
import json
import os
import platform
import subprocess
import time

import numpy as np
import pandas as pd
import sklearn

from .forecasting import MIN_HISTORY, QuantileForecaster, build_X, targets
from .generator import generate_world
from .inventory import simulate
from .signals import clean_calendar, generate_signals

ARMS = {"A_blind": "event-blind",
        "B_clean_trained": "trained on true calendar, served imperfect signal",
        "C_asavailable_trained": "trained and served with the same signal process"}


def make_origins(T, train_end, val_end, L):
    """Forecast origins per split. Training targets (days t..t+L) end before train_end,
    so no validation/test demand enters model fitting."""
    return (np.arange(MIN_HISTORY, train_end - L), np.arange(train_end, val_end),
            np.arange(val_end, T - L))


def pinball(y, qhat, tau):
    diff = y - qhat
    return np.mean(np.maximum(tau * diff, (tau - 1) * diff))


def event_window_mask(events, start, end, L, shelf_life):
    m = np.zeros(end - start, dtype=bool)
    for (s, d, _) in events:
        lo, hi = max(start, s - L), min(end, s + d + shelf_life)
        if lo < hi:
            m[lo - start:hi - start] = True
    return m


def simulate_segment(demand, preds, tau, median_q, start, end, L, shelf_life, costs, origins):
    """Simulate all SKUs over days start..end-1 using forecasts made at those origins."""
    n_or = len(origins)
    assert origins[0] == start and len(origins) == end - start
    out = []
    for i in range(demand.shape[0]):
        sl = slice(i * n_or, (i + 1) * n_or)
        hist = demand[i, start - MIN_HISTORY:start]
        init = int(round(hist.mean() * L))                   # uses only pre-segment history
        out.append(simulate(demand[i, start:end], preds[tau][sl], preds[median_q][sl],
                            L, shelf_life, costs, init_stock=init))
    return out


def summarize(recs, warmup, ev_mask):
    keys = ["cost", "hold_cost", "short_cost", "waste_cost", "lost", "waste", "sales", "received"]
    per_sku = []
    for r in recs:
        row = {k: r[k][warmup:].sum() for k in keys}
        row["demand"] = row["sales"] + row["lost"]
        row["cost_event_window"] = r["cost"][warmup:][ev_mask[warmup:]].sum()
        row["cost_other_days"] = r["cost"][warmup:][~ev_mask[warmup:]].sum()
        per_sku.append(row)
    return pd.DataFrame(per_sku)


def run(cfg, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    L, m, K = cfg["lead_time"], cfg["shelf_life"], cfg["world"]["n_event_types"]
    T, tr_end, va_end = cfg["world"]["n_days"], cfg["split"]["train_end"], cfg["split"]["val_end"]
    tr_or, va_or, te_or = make_origins(T, tr_end, va_end, L)
    taus, med = cfg["quantile_grid"], 0.5
    assert med in taus
    rows, sku_rows, sig_rows = [], [], []
    t0 = time.time()

    for seed in cfg["seeds"]:
        world = generate_world(cfg["world"], seed)
        D = world.demand
        clean = clean_calendar(world.events, cfg["clean_lead_days"])
        y_tr, y_va, y_te = (targets(D, o, L) for o in (tr_or, va_or, te_or))

        def fit(ann_train):
            X, s = build_X(D, tr_or, L, ann_train, K)
            return QuantileForecaster(taus, cfg["model_params"], seed).fit(X, y_tr, s)

        def predict(model, ann_serve, origins):
            X, s = build_X(D, origins, L, ann_serve, K)
            return model.predict(X, s)

        model_A, model_B = fit(None), fit(clean)
        for ci, (cname, scfg) in enumerate(cfg["conditions"].items()):
            ann = generate_signals(world.events, T, K, cfg["world"]["event_type_log_uplift"],
                                   scfg, seed=seed * 1000 + ci + 1)
            n_true_te = sum(1 for (s, d, k) in world.events if va_end <= s < T)
            n_ann_te = sum(1 for a in ann if va_end <= a[1] < T)
            sig_rows.append({"seed": seed, "condition": cname, "true_events_test": n_true_te,
                             "announcements_test": n_ann_te})
            arm_models = {"A_blind": (model_A, None),
                          "B_clean_trained": (model_B, ann),
                          "C_asavailable_trained": (fit(ann), ann)}
            ev_mask = event_window_mask(world.events, va_end, T - L, L, m)
            for arm, (model, serve) in arm_models.items():
                p_va, p_te = predict(model, serve, va_or), predict(model, serve, te_or)
                # tune tau on VALIDATION ONLY
                val_cost = {}
                for tau in taus:
                    recs = simulate_segment(D, p_va, tau, med, tr_end, va_end, L, m, cfg["costs"], va_or)
                    val_cost[tau] = sum(r["cost"][cfg["warmup_days"]:].sum() for r in recs)
                tau_star = min(val_cost, key=val_cost.get)
                recs = simulate_segment(D, p_te, tau_star, med, va_end, T - L, L, m, cfg["costs"], te_or)
                df = summarize(recs, cfg["warmup_days"], ev_mask)
                df["sku"], df["seed"], df["condition"], df["arm"] = range(len(df)), seed, cname, arm
                sku_rows.append(df)
                tot = df.sum(numeric_only=True)
                rows.append({
                    "seed": seed, "condition": cname, "arm": arm, "tau_selected": tau_star,
                    "val_cost": val_cost[tau_star], "total_cost": tot["cost"],
                    "holding_cost": tot["hold_cost"], "shortage_cost": tot["short_cost"],
                    "waste_cost": tot["waste_cost"], "lost_units": tot["lost"],
                    "waste_units": tot["waste"], "fill_rate": tot["sales"] / tot["demand"],
                    "waste_rate": tot["waste"] / max(tot["received"], 1),
                    "cost_event_window": tot["cost_event_window"],
                    "cost_other_days": tot["cost_other_days"],
                    "wape_median": np.abs(p_te[med] - y_te).sum() / y_te.sum(),
                    "pinball_tau_norm": pinball(y_te, p_te[tau_star], tau_star) / y_te.mean(),
                })
        print(f"seed {seed} done ({time.time() - t0:.0f}s)", flush=True)

    by_seed = pd.DataFrame(rows)
    sku = pd.concat(sku_rows, ignore_index=True)
    signals = pd.DataFrame(sig_rows)
    summary = (by_seed.drop(columns="seed").groupby(["condition", "arm"])
               .agg(["mean", "std"]).round(4))
    paired = paired_differences(sku, cfg["bootstrap_reps"], cfg["bootstrap_seed"])

    by_seed.to_csv(f"{out_dir}/metrics_by_seed.csv", index=False)
    sku.to_csv(f"{out_dir}/metrics_by_sku.csv", index=False)
    signals.to_csv(f"{out_dir}/signal_counts.csv", index=False)
    summary.to_csv(f"{out_dir}/metrics_summary.csv")
    paired.to_csv(f"{out_dir}/paired_differences.csv", index=False)
    with open(f"{out_dir}/config.json", "w") as f:
        json.dump(cfg, f, indent=2)
    with open(f"{out_dir}/environment.json", "w") as f:
        json.dump(environment(), f, indent=2)
    md = results_markdown(by_seed, paired, signals, cfg, time.time() - t0)
    with open(f"{out_dir}/results.md", "w") as f:
        f.write(md)
    print(md)
    return by_seed, paired


def paired_differences(sku, reps, seed):
    """Relative test-cost difference between arms, paired by (seed, sku).
    95% CI from a bootstrap that resamples (seed, sku) units."""
    rng = np.random.default_rng(seed)
    out = []
    piv = sku.pivot_table(index=["condition", "seed", "sku"], columns="arm", values="cost")
    for cond, g in piv.groupby(level="condition"):
        for a, b in [("C_asavailable_trained", "B_clean_trained"),
                     ("C_asavailable_trained", "A_blind"), ("B_clean_trained", "A_blind")]:
            x, y = g[a].values, g[b].values
            rel = (x.sum() - y.sum()) / y.sum()
            idx = rng.integers(0, len(x), size=(reps, len(x)))
            boots = (x[idx].sum(1) - y[idx].sum(1)) / y[idx].sum(1)
            out.append({"condition": cond, "comparison": f"{a} vs {b}",
                        "rel_cost_diff": rel, "ci95_low": np.percentile(boots, 2.5),
                        "ci95_high": np.percentile(boots, 97.5),
                        "units_where_first_cheaper": float(np.mean(x < y)), "n_units": len(x)})
    return pd.DataFrame(out)


def environment():
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip() != ""
    except Exception:
        commit, dirty = None, None
    return {"python": platform.python_version(), "numpy": np.__version__,
            "pandas": pd.__version__, "sklearn": sklearn.__version__,
            "git_commit": commit, "git_worktree_dirty": dirty,
            "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def results_markdown(by_seed, paired, signals, cfg, elapsed):
    g = by_seed.groupby(["condition", "arm"])
    cols = ["total_cost", "shortage_cost", "waste_cost", "holding_cost", "lost_units",
            "waste_units", "fill_rate", "wape_median", "pinball_tau_norm", "tau_selected"]
    lines = [f"Seeds: {cfg['seeds']} | SKUs: {cfg['world']['n_sku']} | test days: "
             f"{cfg['world']['n_days'] - cfg['lead_time'] - cfg['split']['val_end']} "
             f"(first {cfg['warmup_days']} excluded) | runtime {elapsed:.0f}s", "",
             "Test-period metrics, mean ± sd across seeds (cost summed over SKUs):", "",
             "| condition | arm | " + " | ".join(cols) + " |",
             "|" + "---|" * (len(cols) + 2)]
    for (c, a), d in g:
        cells = []
        for col in cols:
            mu, sd = d[col].mean(), d[col].std()
            fmt = "{:.3f}" if col in ("fill_rate", "wape_median", "pinball_tau_norm", "tau_selected") else "{:.0f}"
            cells.append((fmt + " ± " + fmt).format(mu, sd))
        lines.append(f"| {c} | {a} | " + " | ".join(cells) + " |")
    lines += ["", "Paired relative test-cost difference (negative = first arm cheaper), "
              "bootstrap 95% CI over (seed, SKU) units:", "",
              "| condition | comparison | rel. cost diff | 95% CI | share of units first cheaper |",
              "|---|---|---|---|---|"]
    for _, r in paired.iterrows():
        lines.append(f"| {r.condition} | {r.comparison} | {r.rel_cost_diff:+.3%} | "
                     f"[{r.ci95_low:+.3%}, {r.ci95_high:+.3%}] | {r.units_where_first_cheaper:.2f} |")
    piv = by_seed.pivot_table(index=["condition", "seed"], columns="arm", values="total_cost")
    lines += ["", "Per-seed relative test cost (cluster-level check; each seed is one independent world):", "",
              "| condition | seed | C vs B | C vs A |", "|---|---|---|---|"]
    for (c, sd), r in piv.iterrows():
        lines.append(f"| {c} | {sd} | {r.C_asavailable_trained / r.B_clean_trained - 1:+.1%} | "
                     f"{r.C_asavailable_trained / r.A_blind - 1:+.1%} |")
    s = signals.groupby("condition")[["true_events_test", "announcements_test"]].mean()
    lines += ["", "Mean event counts in the test period (announcements include spurious ones):", ""]
    lines += [f"- {c}: true events {r.true_events_test:.1f}, announcements {r.announcements_test:.1f}"
              for c, r in s.iterrows()]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/small.json")
    ap.add_argument("--out", default="results/small")
    args = ap.parse_args()
    with open(args.config) as f:
        cfg = json.load(f)
    run(cfg, args.out)


if __name__ == "__main__":
    main()
