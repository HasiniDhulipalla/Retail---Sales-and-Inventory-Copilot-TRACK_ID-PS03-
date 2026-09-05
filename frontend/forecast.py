from backend.forecasting import forecast

def forecast_items(session, product_id=None, store_id=None):
    return forecast(session, product_id, store_id)
