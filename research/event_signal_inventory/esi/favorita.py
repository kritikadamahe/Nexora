"""Real-data world built from the Kaggle Favorita grocery dataset.

Produces the same `World` the synthetic generator returns, so `esi.experiment` can run the
three arms on real perishable sales. Data must be downloaded separately (Kaggle competition
"favorita-grocery-sales-forecasting") into `data_dir`; it is never committed.

Selection (all choices are config fields):
  stores : the `n_stores` stores in `city` with the most transactions over the window that
           were open on at least `min_open_share` of its days.
  items  : perishable items (items.csv perishable == 1) that sold on at least
           `min_selling_share` of open days in every selected store, ranked by total units;
           the top `n_items` are kept. A series is one (store, item) pair.
  days   : every date in [start, end] except dates on which no selected store recorded any
           sale (Favorita stores close on 25 December).

Demand is recorded sales: negative unit_sales (returns) are set to 0 and weighed items are
rounded to whole units. Recorded sales are censored by stockouts; `suspect_stockout` flags a
zero-sale day whose trailing 28-day mean is at least `stockout_flag_mean` (a Poisson zero
would then have probability below exp(-mean)).

Event types (one per day; when several apply, the lower type number wins):
  1 national holiday   : locale National, type in {Holiday, Transfer, Additional, Bridge}
  2 national event     : locale National, type Event (Black Friday, Mother's Day, ...)
  3 local holiday      : locale Regional/Local matching the city or its state, any holiday type
Rows with transferred == True are skipped (the holiday was observed on its Transfer day
instead), "Work Day" rows are not events, and descriptions matching `exclude_events` are
dropped (default: the April 2016 earthquake, which could not have been announced).
Consecutive days with the same type form one event occurrence.
"""
import hashlib
import json
import os

import numpy as np
import pandas as pd

from .generator import World

N_EVENT_TYPES = 3
HOLIDAY_TYPES = {"Holiday", "Transfer", "Additional", "Bridge"}


def _cache_path(dcfg):
    keys = ["city", "start", "end", "n_stores", "n_items", "min_open_share",
            "min_selling_share", "exclude_events"]
    h = hashlib.sha1(json.dumps({k: dcfg.get(k) for k in keys}, sort_keys=True).encode())
    return os.path.join(dcfg["data_dir"], f"panel_{h.hexdigest()[:10]}.npz")


def select_stores(data_dir, city, start, end, n_stores, min_open_share):
    stores = pd.read_csv(os.path.join(data_dir, "stores.csv"))
    tx = pd.read_csv(os.path.join(data_dir, "transactions.csv"), parse_dates=["date"])
    tx = tx[(tx.date >= start) & (tx.date <= end)]
    n_days = (pd.Timestamp(end) - pd.Timestamp(start)).days + 1
    agg = tx.groupby("store_nbr").agg(total=("transactions", "sum"), days=("date", "nunique"))
    cand = stores[stores.city == city].store_nbr
    agg = agg[agg.index.isin(cand) & (agg.days >= min_open_share * n_days)]
    if len(agg) < n_stores:
        raise ValueError(f"only {len(agg)} eligible stores in {city}, need {n_stores}")
    return sorted(agg.sort_values("total", ascending=False).index[:n_stores].tolist())


def read_sales(data_dir, store_ids, item_ids, start, end, chunksize=5_000_000):
    """One pass over train.csv keeping only the selected stores, items and dates."""
    keep = []
    stores, items = set(store_ids), set(item_ids)
    cols = ["date", "store_nbr", "item_nbr", "unit_sales"]
    for ch in pd.read_csv(os.path.join(data_dir, "train.csv"), usecols=cols, chunksize=chunksize,
                          dtype={"store_nbr": "int16", "item_nbr": "int32", "unit_sales": "float32"}):
        ch = ch[(ch.date >= start) & (ch.date <= end)]
        ch = ch[ch.store_nbr.isin(stores) & ch.item_nbr.isin(items)]
        if len(ch):
            keep.append(ch)
    sales = pd.concat(keep, ignore_index=True) if keep else pd.DataFrame(columns=cols)
    sales["date"] = pd.to_datetime(sales["date"])
    return sales


def select_items(sales, store_ids, open_days, n_items, min_selling_share):
    """Items selling on >= min_selling_share of each store's open days, top n_items by units."""
    days_sold = sales[sales.unit_sales > 0].groupby(["item_nbr", "store_nbr"]).date.nunique()
    share = days_sold.unstack("store_nbr").reindex(columns=store_ids).fillna(0)
    share = share / pd.Series(open_days).reindex(store_ids).values
    dense = share.index[(share >= min_selling_share).all(axis=1)]
    units = sales[sales.item_nbr.isin(dense)].groupby("item_nbr").unit_sales.sum()
    if len(units) < n_items:
        raise ValueError(f"only {len(units)} items meet the density rule, need {n_items}")
    return sorted(units.sort_values(ascending=False).index[:n_items].tolist())


def build_event_calendar(holidays, dates, city, state, exclude_events):
    """Daily event type (0 = none) aligned to `dates`, plus the list of occurrences
    (start_index, duration, type)."""
    h = holidays.copy()
    h["date"] = pd.to_datetime(h["date"])
    h = h[~h.transferred.astype(bool) & (h.type != "Work Day")]
    for pat in exclude_events:
        h = h[~h.description.str.contains(pat, case=False, regex=False)]
    nat = h.locale == "National"
    loc = h.locale_name.isin([city, state]) & h.locale.isin(["Local", "Regional"])
    typed = pd.concat([h[nat & h.type.isin(HOLIDAY_TYPES)].assign(k=1),
                       h[nat & (h.type == "Event")].assign(k=2),
                       h[loc].assign(k=3)])
    by_day = typed.groupby("date").k.min()
    event_type = by_day.reindex(dates).fillna(0).astype(int).values
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


def training_log_uplift(demand, event_type, train_end):
    """Mean log ratio of event-day to non-event-day demand per type, per series, estimated on
    days before `train_end` only. Column 0 is 0; types without training days get 0."""
    d = np.log1p(demand[:, :train_end].astype(float))
    et = event_type[:train_end]
    base = d[:, et == 0].mean(axis=1)
    up = np.zeros((demand.shape[0], N_EVENT_TYPES + 1))
    for k in range(1, N_EVENT_TYPES + 1):
        if (et == k).any():
            up[:, k] = d[:, et == k].mean(axis=1) - base
    return up


def build_panel(dcfg, verbose=True):
    d = dcfg["data_dir"]
    start, end = dcfg["start"], dcfg["end"]
    store_ids = select_stores(d, dcfg["city"], start, end, dcfg["n_stores"], dcfg["min_open_share"])
    items = pd.read_csv(os.path.join(d, "items.csv"))
    perishable = items.loc[items.perishable == 1, "item_nbr"].tolist()
    if verbose:
        print(f"[favorita] stores {store_ids}; scanning train.csv for {len(perishable)} perishable items ...",
              flush=True)
    sales = read_sales(d, store_ids, perishable, start, end)
    open_days = sales.groupby("store_nbr").date.nunique().to_dict()
    item_ids = select_items(sales, store_ids, open_days, dcfg["n_items"], dcfg["min_selling_share"])

    dates = pd.date_range(start, end, freq="D")
    dates = dates[dates.isin(sales.date.unique())]          # drop chain-wide closed days
    sales = sales[sales.item_nbr.isin(item_ids)]
    sales = sales.assign(unit_sales=sales.unit_sales.clip(lower=0))
    grid = (sales.groupby(["store_nbr", "item_nbr", "date"]).unit_sales.sum()
            .unstack("date").reindex(columns=dates)
            .reindex(pd.MultiIndex.from_product([store_ids, item_ids], names=["store_nbr", "item_nbr"]))
            .fillna(0.0))
    demand = np.rint(grid.values).astype(int)
    series = np.array(grid.index.tolist(), dtype=int)
    stores = pd.read_csv(os.path.join(d, "stores.csv"))
    state = stores.loc[stores.city == dcfg["city"], "state"].iloc[0]
    holidays = pd.read_csv(os.path.join(d, "holidays_events.csv"))
    event_type, events = build_event_calendar(holidays, dates, dcfg["city"], state,
                                              dcfg.get("exclude_events", ["Terremoto"]))
    item_family = np.array(items.set_index("item_nbr").family.reindex(series[:, 1]).tolist(), dtype="U")
    path = _cache_path(dcfg)
    np.savez_compressed(path, demand=demand, series=series, dates=dates.values.astype("datetime64[D]"),
                        event_type=event_type, events=np.array(events, dtype=int).reshape(-1, 3),
                        item_family=item_family)
    if verbose:
        print(f"[favorita] panel {demand.shape} cached to {path}", flush=True)
    return path


def load_panel(dcfg, verbose=True):
    path = _cache_path(dcfg)
    if not os.path.exists(path):
        build_panel(dcfg, verbose)
    z = np.load(path, allow_pickle=False)
    return {k: z[k] for k in z.files}


def suspect_stockout(demand, flag_mean, window=28):
    """True where sales are 0 although the trailing `window`-day mean is >= flag_mean."""
    out = np.zeros(demand.shape, dtype=bool)
    c = np.cumsum(np.pad(demand, ((0, 0), (1, 0))), axis=1)
    for t in range(window, demand.shape[1]):
        trail = (c[:, t] - c[:, t - window]) / window
        out[:, t] = (demand[:, t] == 0) & (trail >= flag_mean)
    return out


def load_world(dcfg, train_end, verbose=True):
    p = load_panel(dcfg, verbose)
    demand, event_type = p["demand"], p["event_type"]
    events = [tuple(int(x) for x in e) for e in p["events"]]
    return World(demand=demand, event_type=event_type, events=events,
                 uplift=training_log_uplift(demand, event_type, train_end),
                 base=demand[:, :train_end].mean(axis=1)), p


def describe(dcfg, train_end, val_end):
    """Plain summary of the panel for the run log and the paper's data section."""
    world, p = load_world(dcfg, train_end, verbose=False)
    D, T = world.demand, world.demand.shape[1]
    sus = suspect_stockout(D, dcfg.get("stockout_flag_mean", 5.0))
    up = world.uplift[:, 1:]
    lines = [f"Favorita panel: {D.shape[0]} series ({len(np.unique(p['series'][:, 0]))} stores x "
             f"{len(np.unique(p['series'][:, 1]))} perishable items), {T} days "
             f"{str(p['dates'][0])} .. {str(p['dates'][-1])}",
             f"split: train < day {train_end}, validation < day {val_end}, test {T - val_end} days",
             f"mean daily units per series: {D.mean():.1f} (median series {np.median(D.mean(1)):.1f})",
             f"zero-sale days: {np.mean(D == 0):.1%}; suspected stockout days: {sus.mean():.1%}",
             "families: " + ", ".join(f"{f} {n}" for f, n in
                                      zip(*np.unique(p['item_family'], return_counts=True)))]
    for k, name in enumerate(["national holiday", "national event", "local holiday"], start=1):
        occ = [e for e in world.events if e[2] == k]
        n_test = sum(1 for e in occ if e[0] >= val_end)
        lines.append(f"type {k} {name}: {len(occ)} occurrences ({n_test} in test), "
                     f"{int((world.event_type == k).sum())} days; training log-uplift "
                     f"mean {up[:, k - 1].mean():+.3f}, sd {up[:, k - 1].std():+.3f}")
    return "\n".join(lines)
