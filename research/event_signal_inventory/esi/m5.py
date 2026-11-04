"""Real-data world built from the Walmart M5 dataset (Kaggle "m5-forecasting-accuracy").

Produces the same `World` the synthetic generator returns, so `esi.experiment` can run the
arms on real sales with strong, scheduled events. Data must be downloaded separately into
`data_dir` (calendar.csv, sales_train_evaluation.csv); it is never committed.

Selection (all choices are config fields):
  stores : every store in `state` (Wisconsin: WI_1, WI_2, WI_3).
  items  : items of category `category` that sold on at least `min_selling_share` of the
           window's days in every selected store, ranked by total units; the top `n_items`
           are kept. A series is one (store, item) pair.
  days   : every date in [start, end] except dates on which no selected series recorded any
           sale (Walmart stores close on 25 December).

M5 items are not labelled perishable. The same shelf life is imposed on them as on the
Favorita perishables, so M5 is a test of how event strength moves cost, not of a specific
product's spoilage.

Event types (one per day; when several apply, the lower type number wins):
  1 SNAP day            : snap_<state> == 1 (scheduled benefit days, published in advance)
  2 national/religious  : event_type_1 or event_type_2 in {National, Religious}
  3 cultural/sporting   : event_type_1 or event_type_2 in {Cultural, Sporting}
Consecutive days with the same type form one event occurrence.
"""
import hashlib
import json
import os

import numpy as np
import pandas as pd

from .favorita import suspect_stockout, training_log_uplift
from .generator import World

N_EVENT_TYPES = 3
TYPE_NAMES = ["SNAP day", "national/religious event", "cultural/sporting event"]


def _cache_path(dcfg):
    keys = ["state", "category", "start", "end", "n_items", "min_selling_share"]
    h = hashlib.sha1(json.dumps({k: dcfg.get(k) for k in keys}, sort_keys=True).encode())
    return os.path.join(dcfg["data_dir"], f"m5_panel_{h.hexdigest()[:10]}.npz")


def build_event_calendar(cal, state):
    """Daily event type (0 = none) aligned to the rows of `cal`, plus the occurrences
    (start_index, duration, type)."""
    named = cal[["event_type_1", "event_type_2"]]
    major = named.isin(["National", "Religious"]).any(axis=1).values
    minor = named.isin(["Cultural", "Sporting"]).any(axis=1).values
    snap = cal[f"snap_{state}"].values == 1
    event_type = np.select([snap, major, minor], [1, 2, 3], default=0)
    events, t = [], 0
    while t < len(event_type):
        k = event_type[t]
        if k == 0:
            t += 1
            continue
        s = t
        while t < len(event_type) and event_type[t] == k:
            t += 1
        events.append((s, t - s, int(k)))
    return event_type, events


def build_panel(dcfg, verbose=True):
    d = dcfg["data_dir"]
    cal = pd.read_csv(os.path.join(d, "calendar.csv"), parse_dates=["date"])
    cal = cal[(cal.date >= dcfg["start"]) & (cal.date <= dcfg["end"])]
    sales = pd.read_csv(os.path.join(d, "sales_train_evaluation.csv"))
    sales = sales[(sales.state_id == dcfg["state"]) & (sales.cat_id == dcfg["category"])]
    cal = cal[cal.d.isin(sales.columns)]
    if verbose:
        print(f"[m5] {len(sales)} {dcfg['category']} series in {dcfg['state']}, "
              f"{len(cal)} days {cal.date.min().date()} .. {cal.date.max().date()}", flush=True)
    store_ids = sorted(sales.store_id.unique())
    X = sales.set_index(["store_id", "item_id"])[cal.d.tolist()]

    share = (X > 0).mean(axis=1).unstack("store_id").reindex(columns=store_ids)
    dense = share.index[(share >= dcfg["min_selling_share"]).all(axis=1)]
    units = X[X.index.get_level_values("item_id").isin(dense)].groupby(level="item_id").sum().sum(axis=1)
    if len(units) < dcfg["n_items"]:
        raise ValueError(f"only {len(units)} items meet the density rule, need {dcfg['n_items']}")
    item_ids = sorted(units.sort_values(ascending=False).index[:dcfg["n_items"]].tolist())

    X = X.reindex(pd.MultiIndex.from_product([store_ids, item_ids], names=["store_id", "item_id"]))
    open_day = X.values.sum(axis=0) > 0                      # drop chain-wide closed days
    demand = X.values[:, open_day].astype(int)
    cal = cal[open_day]
    event_type, events = build_event_calendar(cal, dcfg["state"])
    series = np.array([f"{s}|{i}" for s, i in X.index], dtype="U")
    path = _cache_path(dcfg)
    np.savez_compressed(path, demand=demand, series=series,
                        dates=cal.date.values.astype("datetime64[D]"), event_type=event_type,
                        events=np.array(events, dtype=int).reshape(-1, 3))
    if verbose:
        print(f"[m5] panel {demand.shape} cached to {path}", flush=True)
    return path


def load_panel(dcfg, verbose=True):
    path = _cache_path(dcfg)
    if not os.path.exists(path):
        build_panel(dcfg, verbose)
    z = np.load(path, allow_pickle=False)
    return {k: z[k] for k in z.files}


def load_world(dcfg, train_end, verbose=True):
    p = load_panel(dcfg, verbose)
    demand, event_type = p["demand"], p["event_type"]
    events = [tuple(int(x) for x in e) for e in p["events"]]
    return World(demand=demand, event_type=event_type, events=events,
                 uplift=training_log_uplift(demand, event_type, train_end),
                 base=demand[:, :train_end].mean(axis=1)), p


def series_table(p):
    store, item = zip(*(s.split("|") for s in p["series"]))
    return pd.DataFrame({"sku": range(len(store)), "store": store, "item": item,
                         "dept": [i.rsplit("_", 1)[0] for i in item]})


def describe(dcfg, train_end, val_end):
    """Plain summary of the panel for the run log and the paper's data section."""
    world, p = load_world(dcfg, train_end, verbose=False)
    D, T = world.demand, world.demand.shape[1]
    sus = suspect_stockout(D, dcfg.get("stockout_flag_mean", 5.0))
    st = series_table(p)
    up = world.uplift[:, 1:]
    lines = [f"M5 panel: {D.shape[0]} series ({st.store.nunique()} stores x {st.item.nunique()} "
             f"{dcfg['category']} items), {T} days {str(p['dates'][0])} .. {str(p['dates'][-1])}",
             f"split: train < day {train_end}, validation < day {val_end}, test {T - val_end} days",
             f"mean daily units per series: {D.mean():.1f} (median series {np.median(D.mean(1)):.1f})",
             f"zero-sale days: {np.mean(D == 0):.1%}; suspected stockout days: {sus.mean():.1%}",
             "departments: " + ", ".join(f"{k} {v}" for k, v in st.dept.value_counts().sort_index().items())]
    for k, name in enumerate(TYPE_NAMES, start=1):
        occ = [e for e in world.events if e[2] == k]
        n_test = sum(1 for e in occ if e[0] >= val_end)
        lines.append(f"type {k} {name}: {len(occ)} occurrences ({n_test} in test), "
                     f"{int((world.event_type == k).sum())} days; training log-uplift "
                     f"mean {up[:, k - 1].mean():+.3f}, sd {up[:, k - 1].std():+.3f}")
    return "\n".join(lines)
