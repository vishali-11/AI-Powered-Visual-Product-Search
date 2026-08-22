"""
Load stage of the ingestion pipeline.

Loads cleaned DataFrames (from transform.py) into the target database
using SQLAlchemy, per the project's tech stack. Uses a truncate-and-reload
strategy per table within a single transaction: simple and correct for an
initial bulk load, with each table's write wrapped so a failure rolls back
cleanly rather than leaving the target half-updated.

Points DATABASE_URL (config.py) at PostgreSQL in production; defaults to
a local SQLite file so the pipeline can be run and tested without a live
Postgres instance.
"""

import logging

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL
from models import Base, Product, Inventory, ProductImage

logger = logging.getLogger(__name__)


def get_engine(database_url: str = DATABASE_URL):
    return create_engine(database_url, future=True)


def init_db(engine):
    """Create all tables if they don't already exist."""
    Base.metadata.create_all(engine)
    logger.info("Ensured target schema exists")


def load_products(session, df: pd.DataFrame) -> int:
    session.query(Product).delete()
    records = [
        Product(
            product_id=row.product_id,
            sku=row.sku,
            title=row.title,
            description=None if pd.isna(row.description) else row.description,
            brand=row.brand,
            category=row.category,
            price=float(row.price),
            status=row.status,
        )
        for row in df.itertuples(index=False)
    ]
    session.bulk_save_objects(records)
    logger.info("Loaded %d product rows", len(records))
    return len(records)


def load_inventory(session, df: pd.DataFrame) -> int:
    session.query(Inventory).delete()
    records = [
        Inventory(
            sku=row.sku,
            warehouse=row.warehouse,
            stock_qty=int(row.stock_qty),
            updated_at=row.updated_at,
        )
        for row in df.itertuples(index=False)
    ]
    session.bulk_save_objects(records)
    logger.info("Loaded %d inventory rows", len(records))
    return len(records)


def load_images(session, df: pd.DataFrame) -> int:
    session.query(ProductImage).delete()
    records = [
        ProductImage(
            sku=row.sku,
            image_url=row.image_url,
            image_type=row.image_type,
            is_primary=bool(row.is_primary),
        )
        for row in df.itertuples(index=False)
    ]
    session.bulk_save_objects(records)
    logger.info("Loaded %d image rows", len(records))
    return len(records)


def load_all(products_df, inventory_df, images_df, database_url: str = DATABASE_URL) -> dict:
    """
    Load all three cleaned DataFrames into the target database inside a
    single transaction. Products are loaded first so that inventory/image
    foreign keys resolve correctly; if any step fails, the whole load is
    rolled back rather than partially applied.
    """
    engine = get_engine(database_url)
    init_db(engine)
    Session = sessionmaker(bind=engine, future=True)
    session = Session()

    counts = {}
    try:
        counts["products"] = load_products(session, products_df)
        counts["inventory"] = load_inventory(session, inventory_df)
        counts["images"] = load_images(session, images_df)
        session.commit()
        logger.info("Load committed successfully: %s", counts)
    except Exception:
        session.rollback()
        logger.exception("Load failed, transaction rolled back")
        raise
    finally:
        session.close()

    return counts
