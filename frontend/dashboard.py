from backend.calculations import dashboard

def get_dashboard(session, store_id=None):
    return dashboard(session, store_id)
