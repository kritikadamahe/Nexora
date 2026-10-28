"""
Trained demand forecasting for Nexora.

Modules
-------
panel       dense daily demand matrix per (product, store)
features    leakage-safe "as of origin t" features + 7-day-ahead targets
baselines   naive / moving-average / the original Nexora heuristic, all as-of t
model       gradient-boosted point (P50-style) and P90 models, fit/predict
evaluation  chronological splits, rolling-origin backtest, metrics, report

Forecast target: total units demanded over the 7 days after the origin date
(days t+1 .. t+7), for each (product_id, store_id).
"""
HORIZON_DAYS = 7
