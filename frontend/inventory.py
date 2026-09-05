from backend.calculations import stockout, overstock, non_moving

def inventory_views(session, store_id=None):
    return stockout(session, store_id), overstock(session, store_id), non_moving(session, store_id)
