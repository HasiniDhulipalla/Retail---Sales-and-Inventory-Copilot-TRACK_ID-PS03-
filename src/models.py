from datetime import date
from decimal import Decimal
from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Store(Base):
    __tablename__ = "stores"
    store_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_name: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    region: Mapped[str] = mapped_column(String(80), nullable=False)

class Product(Base):
    __tablename__ = "products"
    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_name: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    brand: Mapped[str] = mapped_column(String(80), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reorder_level: Mapped[int] = mapped_column(Integer, nullable=False)
    target_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    supplier: Mapped[str] = mapped_column(String(120), nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)

class Sale(Base):
    __tablename__ = "sales"
    sale_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.store_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    quantity_sold: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

class Inventory(Base):
    __tablename__ = "inventory"
    inventory_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.store_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    opening_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    received_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_sold: Mapped[int] = mapped_column(Integer, nullable=False)
    closing_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint("date", "store_id", "product_id"),)
