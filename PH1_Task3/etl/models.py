"""
SQLAlchemy ORM models for the ingestion pipeline's target tables.

This is a deliberately narrow slice of the full data model in
docs/task2/erd.md — just the tables this pipeline actually populates
(Product, Inventory, ProductImage) — since Task 3 is scoped to initial
data loading, not the full schema.
"""

from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String, primary_key=True)
    sku = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    category = Column(String, nullable=True, index=True)
    price = Column(Float, nullable=False)
    status = Column(String, nullable=False)

    inventory = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (UniqueConstraint("sku", "warehouse", name="uq_inventory_sku_warehouse"),)

    inventory_id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String, ForeignKey("products.sku"), nullable=False, index=True)
    warehouse = Column(String, nullable=False)
    stock_qty = Column(Integer, nullable=False, default=0)
    updated_at = Column(String, nullable=True)  # stored as ISO string for simplicity in this task

    product = relationship("Product", back_populates="inventory")


class ProductImage(Base):
    __tablename__ = "product_images"

    image_id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String, ForeignKey("products.sku"), nullable=False, index=True)
    image_url = Column(String, nullable=False)
    image_type = Column(String, nullable=True)
    is_primary = Column(Boolean, default=False)

    product = relationship("Product", back_populates="images")
