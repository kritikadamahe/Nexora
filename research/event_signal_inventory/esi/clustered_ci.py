"""Seed-clustered uncertainty for paired arm comparisons.

SKUs simulated with the same seed share one demand world, one event calendar and one
signal realisation, so their cost differences are correlated. The original bootstrap in
experiment.paired_differences resamples (seed, SKU) units independently and therefore
ignores this dependence. This script re-analyses an existing results directory
(metrics_by_sku.csv) without rerunning the experiment and reports:

  iid_*        : original unit-level bootstrap (for reference)
  cluster_*    : bootstrap resampling whole seeds
  twostage_*   : seeds resampled, then SKUs resampled within each drawn seed
  seed_t_*     : t-interval of the per-seed relative differences (df = n_seeds - 1)
  signflip_p   : exact two-sided sign-flip test on the per-seed relative differences

Usage:
    python -m esi.clustered_ci --results results/small --out results/validation_clustered_ci/small
"""
import argparse
import itertools
import os

import numpy as np
import pandas as pd
from scipy import stats

COMPARISONS = [("C_asavailable_trained", "B_clean_trained"),
               ("C_asavailable_trained", "A_blind"), ("B_clean_trained", "A_blind")]


def _ratio(x, y):
    return (x.sum() - y.sum()) / y.sum()


def signflip_p(d):
    """Exact two-sided sign-flip p-value for mean(d) = 0 (all 2^n sign patterns)."""
    d = np.asarray(d, dtype=float)
    obs = abs(d.mean())
    flips = np.array(list(itertools.product([1, -1], repeat=len(d))))
    return float(np.mean(np.abs((flips * d).mean(axis=1)) >= obs - 1e-12))


def clustered_comparison(x, y, seeds, reps, rng):
    """x, y: per-(seed, SKU) costs for two arms; seeds: seed label per row."""
    useeds = np.unique(seeds)
    groups = [np.where(seeds == s)[0] for s in useeds]
    point = _ratio(x, y)
    # iid unit bootstrap (original method)
    idx = rng.integers(0, len(x), size=(reps, len(x)))
    iid = (x[idx].sum(1) - y[idx].sum(1)) / y[idx].sum(1)
    # cluster bootstrap over seeds
    xs = np.array([x[g].sum() for g in groups]); ys = np.array([y[g].sum() for g in groups])
    cidx = rng.integers(0, len(useeds), size=(reps, len(useeds)))
    clus = (xs[cidx].sum(1) - ys[cidx].sum(1)) / ys[cidx].sum(1)
    # two-stage: seeds, then SKUs within each drawn seed
    two = np.empty(reps)
    for r in range(reps):
        sx = sy = 0.0
        for c in cidx[r]:
            g = groups[c]
            j = g[rng.integers(0, len(g), size=len(g))]
            sx += x[j].sum(); sy += y[j].sum()
        two[r] = (sx - sy) / sy
    # per-seed relative differences
    per_seed = xs / ys - 1
    n = len(per_seed)
    se = per_seed.std(ddof=1) / np.sqrt(n) if n > 1 else np.nan
    tq = stats.t.ppf(0.975, n - 1) if n > 1 else np.nan
    pct = lambda a: (np.percentile(a, 2.5), np.percentile(a, 97.5))
    return {
        "rel_cost_diff": point,
        "iid_low": pct(iid)[0], "iid_high": pct(iid)[1],
        "cluster_low": pct(clus)[0], "cluster_high": pct(clus)[1],
        "twostage_low": pct(two)[0], "twostage_high": pct(two)[1],
        "seed_mean": per_seed.mean(), "seed_t_low": per_seed.mean() - tq * se,
        "seed_t_high": per_seed.mean() + tq * se,
        "seeds_first_cheaper": int((per_seed < 0).sum()), "n_seeds": n,
        "signflip_p": signflip_p(per_seed), "min_possible_signflip_p": 2 / 2 ** n,
    }


def analyse(sku, reps=2000, seed=12345):
    rng = np.random.default_rng(seed)
    piv = sku.pivot_table(index=["condition", "seed", "sku"], columns="arm", values="cost")
    rows = []
    for cond, g in piv.groupby(level="condition", sort=False):
        seeds = g.index.get_level_values("seed").values
        for a, b in COMPARISONS:
            r = clustered_comparison(g[a].values, g[b].values, seeds, reps, rng)
            rows.append({"condition": cond, "comparison": f"{a} vs {b}", **r})
    return pd.DataFrame(rows)


def to_markdown(df, src):
    L = [f"# Seed-clustered intervals for `{src}`", "",
         "Relative total-cost difference (negative = first arm cheaper). 95% intervals.", "",
         "| condition | comparison | estimate | iid bootstrap (original) | seed-cluster bootstrap | "
         "two-stage bootstrap | per-seed t-interval | seeds first cheaper | sign-flip p |",
         "|---|---|---|---|---|---|---|---|---|"]
    f = lambda lo, hi: f"[{lo:+.1%}, {hi:+.1%}]"
    for _, r in df.iterrows():
        L.append(f"| {r.condition} | {r.comparison} | {r.rel_cost_diff:+.1%} | {f(r.iid_low, r.iid_high)} | "
                 f"{f(r.cluster_low, r.cluster_high)} | {f(r.twostage_low, r.twostage_high)} | "
                 f"{f(r.seed_t_low, r.seed_t_high)} | {r.seeds_first_cheaper}/{r.n_seeds} | {r.signflip_p:.3f} |")
    n = int(df.n_seeds.iloc[0])
    L += ["", f"With {n} seeds the smallest attainable two-sided sign-flip p-value is "
          f"{2 / 2 ** n:.4f}. A seed-cluster bootstrap with only {n} clusters also tends to "
          "understate uncertainty, so the per-seed t-interval is the more conservative summary."]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=12345)
    a = ap.parse_args()
    if os.path.abspath(a.out) == os.path.abspath(a.results):
        raise SystemExit("refusing to write into the source results directory")
    sku = pd.read_csv(os.path.join(a.results, "metrics_by_sku.csv"), float_precision="round_trip")
    df = analyse(sku, a.reps, a.seed)
    os.makedirs(a.out, exist_ok=True)
    df.to_csv(os.path.join(a.out, "clustered_ci.csv"), index=False)
    md = to_markdown(df, a.results)
    open(os.path.join(a.out, "clustered_ci.md"), "w").write(md)
    print(md)


if __name__ == "__main__":
    main()
