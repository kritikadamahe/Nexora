# app/modules/clearance.py
#
# Shared clearance-projection logic for the markdown (reverse logistics) and
# bundle (combo) modules.
#
# Why this exists: both modules used to assume that ALL current stock sells at
# the discounted price, and computed days_to_clear without comparing it to the
# product's remaining shelf life. A product expiring tomorrow could therefore be
# reported as "clears in 5 days, recovering revenue on every unit".
#
# Here the units that can realistically be sold are capped by the days left
# before expiry, and anything beyond that is reported as unsold at expiry.

import math

NON_PERISHABLE_DAYS = 9999   # sentinel used across the app for non-perishables


def project_clearance(current_stock: float, new_daily_sales: float,
                      days_to_expiry: int, unit_price: float) -> dict:
    """
    Returns the expiry-aware clearance projection.

    days_to_clear            raw days needed to sell all stock at the new rate
                             (999 if the new rate is zero)
    units_sold_before_expiry units that can sell before expiry (whole units,
                             rounded down so the projection stays conservative)
    units_unsold_at_expiry   stock still on hand when the product expires
    clears_before_expiry     True only if every unit is expected to sell
    projected_revenue        revenue from units_sold_before_expiry only
    """
    stock = max(float(current_stock), 0.0)
    rate = max(float(new_daily_sales), 0.0)

    days_to_clear = round(stock / rate) if rate > 0 else 999

    if days_to_expiry >= NON_PERISHABLE_DAYS:
        sellable = stock                      # no expiry constraint
    else:
        sellable = min(stock, rate * max(days_to_expiry, 0))

    units_sold = int(math.floor(sellable + 1e-9))
    units_sold = min(units_sold, int(stock))
    units_unsold = int(stock) - units_sold

    return {
        "days_to_clear":            days_to_clear,
        "units_sold_before_expiry": units_sold,
        "units_unsold_at_expiry":   units_unsold,
        "clears_before_expiry":     units_unsold == 0,
        "projected_revenue":        round(units_sold * unit_price, 2),
    }
