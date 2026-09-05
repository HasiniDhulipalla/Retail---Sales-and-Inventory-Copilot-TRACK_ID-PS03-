from datetime import date, timedelta
import random
from decimal import Decimal
from sqlalchemy.orm import Session
from .models import Store, Product, Sale, Inventory

random.seed(42)

def seed_demo_data(session: Session) -> None:
    stores = [Store(store_name="Central Market", city="Hyderabad", region="South"), Store(store_name="Lake View", city="Vijayawada", region="South"), Store(store_name="Metro Point", city="Pune", region="West")]
    session.add_all(stores)
    session.flush()
    categories = [("Beverages", ["Coca Cola", "Fresh Sip", "Sunrise"]), ("Snacks", ["Crunchy", "Daily Bite", "Tasty"]), ("Dairy", ["Milky Way", "Farm Fresh"]), ("Household", ["CleanCo", "HomeCare"]), ("Personal Care", ["PureLife", "Glow"])]
    products = []
    for i in range(50):
        category, brands = categories[i % len(categories)]
        name = ["500ml", "1L", "Pack of 6", "Family Pack", "200g"][i % 5]
        price = Decimal(str(round(25 + (i * 7.35) % 240, 2)))
        products.append(Product(product_name=f"{brands[i % len(brands)]} {name}", category=category, brand=brands[i % len(brands)], unit_price=price, reorder_level=10 + i % 12, target_stock=35 + i % 35, supplier=f"Supplier {i % 6 + 1}", lead_time_days=2 + i % 6))
    session.add_all(products)
    session.flush()
    start = date.today() - timedelta(days=89)
    sales, inventory = [], []
    stock = {(s.store_id, p.product_id): 45 + (p.product_id * 3 + s.store_id * 7) % 80 for s in stores for p in products}
    for day_index in range(90):
        current = start + timedelta(days=day_index)
        for store in stores:
            for product in products:
                base = 2 + (product.product_id % 7)
                if product.product_id == 1: base = 9
                if product.product_id == 2: base = 1
                if product.product_id == 3: base = 0
                if product.product_id == 4 and day_index >= 72: base += 8
                if product.product_id == 5 and day_index >= 60: base = max(0, base - 2)
                store_factor = [1.35, 0.9, 1.1][store.store_id - 1]
                qty = max(0, int(round(base * store_factor + random.choice([-1, 0, 0, 1]))))
                if product.product_id == 3: qty = 0
                opening = stock[(store.store_id, product.product_id)]
                received = 0
                if opening < product.reorder_level and product.product_id not in (1, 2):
                    received = product.target_stock
                closing = max(0, opening + received - qty)
                stock[(store.store_id, product.product_id)] = closing
                sales.append(Sale(date=current, store_id=store.store_id, product_id=product.product_id, quantity_sold=qty, unit_price=product.unit_price, total_amount=product.unit_price * qty))
                inventory.append(Inventory(date=current, store_id=store.store_id, product_id=product.product_id, opening_stock=opening, received_stock=received, quantity_sold=qty, closing_stock=closing))
    session.add_all(sales + inventory)
    session.commit()
