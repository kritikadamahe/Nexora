"""Back-simulation of replenishment policies on held-out history.

Compares, over the same out-of-sample weeks and the same starting stock:
  * nexora_gbm        order-up-to driven by the trained forecast (P50 + sqrt-scaled P90 spread)
  * textbook_ma28     order-up-to with 28-day mean demand + z * (91-day daily std) * sqrt(P)
  * legacy_rule       the original forward-logistics rule: max(0, heuristic_7d * 1.3 - stock)

Assumptions: weekly review, deterministic lead time, orders placed at end of the review day
arrive L days later, unmet demand is lost (not backordered), no MOQ/capacity, sales = demand
(historical stock-outs are unobserved), initial stock = 2 weeks of the trailing 28-day mean.
"""
import numpy as np
import pandas as pd

from .replenishment import order_up_to

Z90 = 1.2816


def simulate(y: np.ndarray, preds: pd.DataFrame, series_pos: dict, review_origins: list,
             end_idx: int, cost: np.ndarray, lead_time: int = 3, review: int = 7) -> pd.DataFrame:
    """y: (S, T) daily demand. preds: rows for (series, origin) with gbm, gbm_p90,
    nexora_heuristic, m28. series_pos maps (product_id, store_id) -> row in y."""
    S = y.shape[0]
    first = review_origins[0]
    p = lead_time + review
    lookup = preds.set_index(["origin_idx", "product_id", "store_id"])
    results = {}
    for policy in ("nexora_gbm", "textbook_ma28", "legacy_rule"):
        on_hand = np.maximum(0.0, 14 * y[:, first - 27: first + 1].mean(axis=1))
        pipeline = []                        # (arrival_idx, qty array)
        demand_tot = sold_tot = 0.0
        stock_units = stock_value = 0.0
        days = 0
        stockout_series_days = 0
        for d in range(first + 1, end_idx + 1):
            # review at end of day d-1 (origin) — decide order, arrives start of day d+lead-1+1
            o = d - 1
            if o in review_origins:
                q = np.zeros(S)
                position = on_hand + sum(a for _, a in pipeline) if pipeline else on_hand.copy()
                rows = lookup.loc[o]
                f50 = np.zeros(S); f90 = np.zeros(S); heur = np.zeros(S)
                idx = np.array([series_pos[(a, b)] for a, b in rows.index])
                f50[idx] = rows["gbm"].to_numpy(); f90[idx] = rows["gbm_p90"].to_numpy()
                heur[idx] = rows["nexora_heuristic"].to_numpy()
                if policy == "nexora_gbm":
                    lvl = np.array([order_up_to(a, b, lead_time, review)["order_up_to"]
                                    for a, b in zip(f50, f90)])
                    q = np.maximum(0.0, lvl - position)
                elif policy == "textbook_ma28":
                    mean28 = y[:, max(o - 27, 0): o + 1].mean(axis=1)
                    sd91 = y[:, max(o - 90, 0): o + 1].std(axis=1)
                    lvl = mean28 * p + Z90 * sd91 * np.sqrt(p)
                    q = np.maximum(0.0, lvl - position)
                else:
                    q = np.maximum(0.0, heur * 1.3 - on_hand)
                q = np.ceil(q - 1e-9)
                if q.sum() > 0:
                    pipeline.append((o + 1 + lead_time, q))
            arrivals = [a for t, a in pipeline if t == d]
            if arrivals:
                on_hand = on_hand + sum(arrivals)
            pipeline = [(t, a) for t, a in pipeline if t > d]
            dem = y[:, d]
            sold = np.minimum(on_hand, dem)
            on_hand = on_hand - sold
            demand_tot += dem.sum(); sold_tot += sold.sum()
            stock_units += on_hand.sum(); stock_value += (on_hand * cost).sum()
            stockout_series_days += int(((dem > 0) & (sold < dem)).sum())
            days += 1
        results[policy] = {
            "policy": policy,
            "fill_rate": sold_tot / demand_tot,
            "avg_on_hand_units": stock_units / days,
            "avg_on_hand_value_at_cost": stock_value / days,
            "stockout_series_days": stockout_series_days,
        }
    return pd.DataFrame(results.values())
