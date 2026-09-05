from datetime import date, timedelta
from decimal import Decimal
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Store, Product, Sale, Inventory

TODAY = date.today()
def frame(session: Session, model) -> pd.DataFrame:
    rows = session.execute(select(model)).scalars().all()
    return pd.DataFrame([{c.name: getattr(row, c.name) for c in model.__table__.columns} for row in rows])

def snapshot(session: Session):
    inv = frame(session, Inventory); products = frame(session, Product); stores = frame(session, Store); sales = frame(session, Sale)
    if inv.empty: return inv, products, stores, sales
    latest = inv[inv.date == inv.date.max()].copy()
    latest = latest.merge(products, on="product_id").merge(stores, on="store_id")
    return latest, products, stores, sales

def dashboard(session: Session, store_id=None):
    latest, products, stores, sales = snapshot(session)
    if store_id: sales = sales[sales.store_id == store_id]; latest = latest[latest.store_id == store_id]
    month_start = TODAY.replace(day=1); today_sales = sales[sales.date == TODAY]; month_sales = sales[sales.date >= month_start]
    low = latest[latest.closing_stock <= latest.reorder_level]
    return {"today_sales": float(today_sales.total_amount.sum()), "monthly_sales": float(month_sales.total_amount.sum()), "units_sold": int(month_sales.quantity_sold.sum()), "current_inventory": int(latest.closing_stock.sum()), "low_stock": int(len(low)), "predicted_stockouts": int(len(stockout(session, store_id))), "overstocked": int(len(overstock(session, store_id))), "non_moving": int(len(non_moving(session, store_id)))}

def stockout(session: Session, store_id=None):
    latest, products, _, sales = snapshot(session)
    if store_id: latest=latest[latest.store_id == store_id]; sales=sales[sales.store_id == store_id]
    since = TODAY - timedelta(days=29); recent=sales[sales.date >= since].groupby("product_id").quantity_sold.sum().rename("sold").reset_index()
    days = max(1, (TODAY - since).days + 1); out=latest.merge(recent, on="product_id", how="left").fillna({"sold":0}); out["ads"] = out.sold / days; out["doi"] = out.apply(lambda r: r.closing_stock / r.ads if r.ads > 0 else None, axis=1); out["status"] = out.apply(lambda r: "CRITICAL" if r.ads > 0 and r.doi <= r.lead_time_days else ("WARNING" if r.ads > 0 and r.doi <= r.lead_time_days + 3 else "HEALTHY"), axis=1); return out[out.status != "HEALTHY"].sort_values(["status", "doi"], ascending=[True, True])

def overstock(session: Session, store_id=None):
    latest, _, _, sales = snapshot(session)
    if store_id: latest=latest[latest.store_id == store_id]; sales=sales[sales.store_id == store_id]
    since=TODAY-timedelta(days=29); ads=sales[sales.date >= since].groupby("product_id").quantity_sold.sum().rename("sold").reset_index(); out=latest.merge(ads,on="product_id",how="left").fillna({"sold":0}); out["ads"]=out.sold/30; out["doi"]=out.apply(lambda r:r.closing_stock/r.ads if r.ads else None,axis=1); out["excess_units"]=(out.closing_stock-out.target_stock).clip(lower=0); out["excess_capital"]=out.excess_units*out.unit_price; return out[(out.closing_stock>out.target_stock)|((out.doi.notna())&(out.doi>45))].sort_values("excess_capital",ascending=False)

def non_moving(session: Session, store_id=None):
    latest, _, _, sales = snapshot(session); since=TODAY-timedelta(days=29)
    if store_id: latest=latest[latest.store_id==store_id]; sales=sales[sales.store_id==store_id]
    sold=set(sales[sales.date>=since].loc[sales[sales.date>=since].quantity_sold>0,"product_id"]); out=latest[~latest.product_id.isin(sold)].copy(); last=sales[sales.quantity_sold>0].groupby("product_id").date.max().rename("last_sale"); return out.merge(last,on="product_id",how="left")

def product_performance(session: Session, product_id: int):
    _, products, _, sales = snapshot(session); product=products[products.product_id==product_id]
    if product.empty: return None
    row=product.iloc[0]; current=sales[(sales.product_id==product_id)&(sales.date>=TODAY-timedelta(days=29))]; return {"product": row.to_dict(), "units_30d": int(current.quantity_sold.sum()), "revenue_30d": float(current.total_amount.sum()), "daily": current.groupby("date").quantity_sold.sum().reset_index().to_dict("records")}
