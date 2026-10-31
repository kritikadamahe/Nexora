"""Split each arm's cost difference against A into event-window days and other days.

Re-analyses an existing results directory (metrics_by_sku.csv) without rerunning the
experiment. Event windows are the days experiment.event_window_mask marks: L days before
each true event through shelf_life days after it. Costs are summed over SKUs and seeds.

Usage:
    python -m esi.event_windows --results results/favorita_v2
"""
import argparse

import pandas as pd

COLS = ["cost", "cost_event_window", "cost_other_days"]


def event_window_split(sku):
    g = sku.groupby(["condition", "arm"])[COLS].sum()
    rows = []
    for (cond, arm), r in g.iterrows():
        a = g.loc[(cond, "A_blind")]
        rows.append({"condition": cond, "arm": arm,
                     "event_window_share_of_cost": r["cost_event_window"] / r["cost"],
                     **{f"{c}_vs_A": r[c] / a[c] - 1 for c in COLS}})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--out", help="output CSV (default: <results>/event_window_split.csv)")
    a = ap.parse_args()
    df = event_window_split(pd.read_csv(f"{a.results}/metrics_by_sku.csv"))
    out = a.out or f"{a.results}/event_window_split.csv"
    df.to_csv(out, index=False)
    print(df.to_string(index=False, float_format=lambda x: f"{x:+.4%}"))
    print(f"\nwritten to {out}")


if __name__ == "__main__":
    main()
