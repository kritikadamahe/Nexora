"""Daily single-SKU perishable inventory simulator and the shared replenishment policy.

Day-t sequence (start of day -> end of day):
  1. Receive the order placed on day t-L; it enters with `shelf_life` sellable days.
  2. Place order q_t (arrives at the start of day t+L).
  3. Serve demand FIFO (oldest stock first); unmet demand is lost (no backorders).
  4. Units on their last sellable day that remain unsold expire (waste).
  5. Remaining stock ages by one day.
  6. Holding cost is charged on end-of-day on-hand stock.

stock[a] = units with a+1 sellable days left (a = 0 is the oldest).
A unit received on day t can be sold on days t .. t+shelf_life-1.
"""
import numpy as np


def projected_expiry(stock, pipeline, daily_demand, shelf_life, horizon):
    """FIFO projection of units that would expire within `horizon` days if daily demand
    equals `daily_demand`. `pipeline[j]` arrives at the start of projected day j+1."""
    s = np.array(stock, dtype=float)
    expired = 0.0
    for j in range(horizon):
        if 1 <= j <= len(pipeline):
            s[shelf_life - 1] += pipeline[j - 1]
        need = daily_demand
        for a in range(shelf_life):
            take = min(s[a], need)
            s[a] -= take
            need -= take
            if need <= 0:
                break
        expired += s[0]
        s[:-1] = s[1:]
        s[-1] = 0.0
    return expired


def order_quantity(order_up_to, median_window, stock, pipeline, shelf_life, L):
    """Shared policy: outdating-corrected order-up-to.
    q = max(0, S - (inventory position - projected expiry over the protection window)).
    A heuristic in the spirit of Broekmeulen & van Donselaar (2009); not claimed optimal."""
    ip = float(np.sum(stock) + np.sum(pipeline))
    exp_hat = projected_expiry(stock, pipeline, median_window / (L + 1), shelf_life, L + 1)
    return max(0, int(round(order_up_to - (ip - exp_hat))))


def simulate(demand, order_up_to, median_window, L, shelf_life, costs, init_stock=0):
    """Simulate one SKU. `order_up_to[t]` and `median_window[t]` are forecasts made at
    origin t (start of day t) for cumulative demand over days t..t+L.
    Returns per-day arrays. Orders arriving after the horizon are never received."""
    T = len(demand)
    stock = np.zeros(shelf_life)
    stock[shelf_life - 1] = init_stock
    arrivals = np.zeros(T + L + 1)
    rec = {k: np.zeros(T) for k in
           ["received", "order", "sales", "lost", "waste", "end_stock", "cost", "hold_cost",
            "short_cost", "waste_cost"]}
    for t in range(T):
        rec["received"][t] = arrivals[t]
        stock[shelf_life - 1] += arrivals[t]
        pipeline = arrivals[t + 1:t + L]                     # orders arriving t+1..t+L-1
        q = order_quantity(order_up_to[t], median_window[t], stock, pipeline, shelf_life, L)
        arrivals[t + L] += q
        rec["order"][t] = q
        need = demand[t]
        for a in range(shelf_life):                          # FIFO
            take = min(stock[a], need)
            stock[a] -= take
            need -= take
        rec["sales"][t] = demand[t] - need
        rec["lost"][t] = need
        rec["waste"][t] = stock[0]
        stock[:-1] = stock[1:].copy()
        stock[-1] = 0.0
        rec["end_stock"][t] = stock.sum()
        rec["hold_cost"][t] = costs["holding"] * rec["end_stock"][t]
        rec["short_cost"][t] = costs["shortage"] * rec["lost"][t]
        rec["waste_cost"][t] = costs["waste"] * rec["waste"][t]
        rec["cost"][t] = rec["hold_cost"][t] + rec["short_cost"][t] + rec["waste_cost"][t]
    rec["init_stock"] = init_stock
    return rec
