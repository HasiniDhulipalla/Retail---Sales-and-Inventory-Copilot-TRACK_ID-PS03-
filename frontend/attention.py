from backend.calculations import stockout

def attention_items(session, store_id=None):
    return stockout(session, store_id)
