from datetime import date, timedelta
import pandas as pd
from .calculations import snapshot, TODAY

def forecast(session, product_id=None, store_id=None, horizon=7):
    _, _, _, sales = snapshot(session)
    if product_id is not None: sales = sales[sales.product_id == product_id]
    if store_id is not None: sales = sales[sales.store_id == store_id]
    recent = sales[sales.date >= TODAY - timedelta(days=29)]
    grouped = recent.groupby("date").quantity_sold.sum()
    average = float(grouped.mean()) if not grouped.empty else 0.0
    rows = []
    for offset in range(1, horizon + 1):
        rows.append({"date": (TODAY + timedelta(days=offset)).isoformat(), "expected_demand": round(average, 2), "method": "30-day moving average"})
    return rows
