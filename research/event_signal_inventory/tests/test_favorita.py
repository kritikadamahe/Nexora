"""Favorita loader on a tiny hand-made dataset (no download needed)."""
import numpy as np
import pandas as pd
import pytest

from esi.favorita import build_event_calendar, load_world, suspect_stockout, training_log_uplift


def _write_dataset(d):
    dates = pd.date_range("2016-12-20", "2016-12-31")
    pd.DataFrame({"store_nbr": [1, 2, 3], "city": ["Quito", "Quito", "Cuenca"],
                  "state": ["Pichincha", "Pichincha", "Azuay"]}).to_csv(d / "stores.csv", index=False)
    pd.DataFrame({"item_nbr": [10, 11, 12], "family": ["DAIRY", "PRODUCE", "CLEANING"],
                  "perishable": [1, 1, 0]}).to_csv(d / "items.csv", index=False)
    open_dates = [x for x in dates if x.day != 25]          # chain closed on Christmas
    pd.DataFrame([(x.date(), s, 100 * s) for x in open_dates for s in (1, 2, 3)],
                 columns=["date", "store_nbr", "transactions"]).to_csv(d / "transactions.csv", index=False)
    rows = []
    for x in open_dates:
        for s in (1, 2, 3):
            rows.append((x.date(), s, 10, 5.4))
            if x.day != 22:
                rows.append((x.date(), s, 11, -1.0 if x.day == 21 else 3.0))
            rows.append((x.date(), s, 12, 50.0))
    pd.DataFrame(rows, columns=["date", "store_nbr", "item_nbr", "unit_sales"]).assign(
        id=range(len(rows)), onpromotion=False).to_csv(d / "train.csv", index=False)
    pd.DataFrame([
        ("2016-12-24", "Additional", "National", "Ecuador", "Navidad-1", False),
        ("2016-12-26", "Holiday", "National", "Ecuador", "Primer dia", True),      # moved away
        ("2016-12-27", "Transfer", "National", "Ecuador", "Traslado Primer dia", False),
        ("2016-12-28", "Event", "National", "Ecuador", "Terremoto Manabi+5", False),
        ("2016-12-29", "Event", "National", "Ecuador", "Black Friday", False),
        ("2016-12-30", "Holiday", "Local", "Quito", "Fundacion de Quito", False),
        ("2016-12-31", "Holiday", "Local", "Cuenca", "Fundacion de Cuenca", False),
        ("2016-12-23", "Work Day", "National", "Ecuador", "Recupero", False),
    ], columns=["date", "type", "locale", "locale_name", "description", "transferred"]
    ).to_csv(d / "holidays_events.csv", index=False)


@pytest.fixture
def dcfg(tmp_path):
    _write_dataset(tmp_path)
    return {"source": "favorita", "data_dir": str(tmp_path), "city": "Quito",
            "start": "2016-12-20", "end": "2016-12-31", "n_stores": 2, "n_items": 2,
            "min_open_share": 0.9, "min_selling_share": 0.8, "exclude_events": ["Terremoto"]}


def test_panel_shape_selection_and_cleaning(dcfg):
    world, p = load_world(dcfg, train_end=5, verbose=False)
    assert world.demand.shape == (4, 11)                     # 2 Quito stores x 2 perishables, 25 Dec dropped
    assert set(p["series"][:, 0]) == {1, 2} and set(p["series"][:, 1]) == {10, 11}
    assert np.datetime64("2016-12-25") not in p["dates"]
    item10 = world.demand[p["series"][:, 1] == 10]
    assert (item10 == 5).all()                               # 5.4 rounded
    item11 = world.demand[p["series"][:, 1] == 11]
    day = {str(x): i for i, x in enumerate(p["dates"])}
    assert (item11[:, day["2016-12-21"]] == 0).all()         # return (negative) clipped to 0
    assert (item11[:, day["2016-12-22"]] == 0).all()         # missing row filled with 0


def test_event_calendar_rules(dcfg):
    world, p = load_world(dcfg, train_end=5, verbose=False)
    et = {str(x): int(k) for x, k in zip(p["dates"], world.event_type)}
    assert et["2016-12-24"] == 1                             # national additional
    assert et["2016-12-26"] == 0                             # transferred away
    assert et["2016-12-27"] == 1                             # observed on transfer day
    assert et["2016-12-28"] == 0                             # excluded earthquake
    assert et["2016-12-29"] == 2                             # national commercial event
    assert et["2016-12-30"] == 3                             # local holiday in Quito
    assert et["2016-12-31"] == 0                             # other city's holiday
    assert et["2016-12-23"] == 0                             # work day is not an event
    for s, dur, k in world.events:                           # occurrences match the daily array
        assert (world.event_type[s:s + dur] == k).all()


def test_overlap_takes_lowest_type():
    dates = pd.date_range("2017-01-01", "2017-01-03")
    h = pd.DataFrame([("2017-01-02", "Event", "National", "Ecuador", "x", False),
                      ("2017-01-02", "Holiday", "National", "Ecuador", "y", False)],
                     columns=["date", "type", "locale", "locale_name", "description", "transferred"])
    et, events = build_event_calendar(h, dates, "Quito", "Pichincha", [])
    assert et.tolist() == [0, 1, 0] and events == [(1, 1, 1)]


def test_uplift_uses_training_days_only():
    demand = np.array([[10, 10, 30, 10, 999]])
    et = np.array([0, 0, 1, 0, 1])
    up = training_log_uplift(demand, et, train_end=4)
    assert up[0, 1] == pytest.approx(np.log1p(30) - np.log1p(10))


def test_suspect_stockout():
    d = np.array([[10] * 30 + [0, 10]])
    s = suspect_stockout(d, flag_mean=5.0)
    assert s[0, 30] and s.sum() == 1
