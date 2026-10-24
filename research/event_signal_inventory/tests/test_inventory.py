import numpy as np
from esi.inventory import simulate, projected_expiry, order_quantity

COSTS = {"holding": 0.1, "shortage": 1.0, "waste": 0.5}


def _forced(T, schedule):
    """order_up_to array that orders exactly `schedule[t]` on day t when IP is known."""
    S = np.zeros(T)
    for t, v in schedule.items():
        S[t] = v
    return S


def test_inventory_balance_random():
    rng = np.random.default_rng(0)
    T, L, m = 120, 2, 4
    d = rng.poisson(10, T)
    S = rng.uniform(0, 60, T)
    r = simulate(d, S, S * 0.6, L, m, COSTS, init_stock=15)
    # every unit that entered is sold, wasted, or still on hand
    assert r["init_stock"] + r["received"].sum() == r["sales"].sum() + r["waste"].sum() + r["end_stock"][-1]
    assert np.all(r["sales"] + r["lost"] == d)
    assert np.all(r["sales"] >= 0) and np.all(r["lost"] >= 0) and np.all(r["waste"] >= 0)
    np.testing.assert_allclose(r["cost"], r["hold_cost"] + r["short_cost"] + r["waste_cost"])


def test_lead_time_arrival_day():
    T, L, m = 10, 3, 5
    d = np.zeros(T, dtype=int)
    r = simulate(d, _forced(T, {0: 7}), np.zeros(T), L, m, COSTS)
    assert r["order"][0] == 7
    assert r["received"][L] == 7 and r["received"].sum() == 7


def test_expiry_after_exact_shelf_life():
    T, L, m = 12, 1, 3
    d = np.zeros(T, dtype=int)
    r = simulate(d, _forced(T, {0: 5}), np.zeros(T), L, m, COSTS)
    # arrives day 1, sellable days 1..3, expires at end of day 3
    assert r["waste"][3] == 5 and r["waste"].sum() == 5
    assert r["end_stock"][2] == 5 and r["end_stock"][3] == 0


def test_fifo_sells_oldest_first():
    T, L, m = 10, 1, 3
    d = np.zeros(T, dtype=int); d[2] = 5
    # day0 order 5 (arrives day1); day1 order up to 10 -> 5 more (arrives day2)
    r = simulate(d, _forced(T, {0: 5, 1: 10}), np.zeros(T), L, m, COSTS)
    assert r["received"][1] == 5 and r["received"][2] == 5
    # FIFO: day-2 demand consumes batch 1, so batch 2 (sellable 2..4) expires end of day 4
    assert r["waste"][3] == 0 and r["waste"][4] == 5
    # under LIFO batch 1 would have expired on day 3 instead


def test_lost_sales_when_out_of_stock():
    T = 5
    d = np.array([3, 4, 0, 2, 1])
    r = simulate(d, np.zeros(T), np.zeros(T), 1, 3, COSTS)
    assert np.all(r["lost"] == d) and r["short_cost"].sum() == d.sum() * COSTS["shortage"]


def test_projected_expiry_and_policy():
    stock = np.array([4.0, 0.0, 0.0])          # 4 units on their last day
    assert projected_expiry(stock, [], 1.0, 3, 2) == 3.0   # sell 1, 3 expire tonight
    # order covers the units projected to expire
    q = order_quantity(10, 2.0, stock, [], 3, 1)
    assert q == round(10 - (4 - 3))
