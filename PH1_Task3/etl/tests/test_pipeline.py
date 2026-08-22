"""
Unit tests for the extract and transform stages.

These deliberately avoid touching the database (load.py / SQLAlchemy),
so they run in any environment with just pandas + pytest installed —
useful for fast CI checks before running the full pipeline against a
real database.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import pytest

from config import PRODUCT_CATALOG_CSV, INVENTORY_FEED_JSON, IMAGE_MANIFEST_CSV, VALID_STATUSES
from extract import extract_products, extract_inventory, extract_images
from transform import transform_products, transform_inventory, transform_images, _parse_price


# ---------- extract ----------

def test_extract_products_returns_rows():
    df = extract_products(PRODUCT_CATALOG_CSV)
    assert len(df) > 0
    assert "sku" in df.columns


def test_extract_inventory_returns_rows():
    df = extract_inventory(INVENTORY_FEED_JSON)
    assert len(df) > 0
    assert "stock_qty" in df.columns


def test_extract_images_returns_rows():
    df = extract_images(IMAGE_MANIFEST_CSV)
    assert len(df) > 0
    assert "image_url" in df.columns


# ---------- transform: products ----------

@pytest.fixture
def clean_products():
    raw = extract_products(PRODUCT_CATALOG_CSV)
    df, report = transform_products(raw)
    return df, report


def test_price_parsing_handles_currency_symbols():
    assert _parse_price("$64.50") == 64.50
    assert _parse_price("89.99") == 89.99
    assert _parse_price("") is None
    assert _parse_price(None) is None


def test_transform_products_drops_duplicate_skus(clean_products):
    df, report = clean_products
    assert df["sku"].duplicated().sum() == 0
    assert report["dropped_duplicate_sku"] >= 1


def test_transform_products_drops_missing_title(clean_products):
    df, _ = clean_products
    assert not (df["title"].str.strip() == "").any()


def test_transform_products_drops_negative_or_missing_price(clean_products):
    df, report = clean_products
    assert (df["price"] >= 0).all()
    assert df["price"].isna().sum() == 0
    assert report["dropped_invalid_price"] >= 1


def test_transform_products_coerces_invalid_status(clean_products):
    df, _ = clean_products
    assert df["status"].isin(VALID_STATUSES).all()


def test_transform_products_all_have_product_id(clean_products):
    df, _ = clean_products
    assert df["product_id"].notna().all()
    assert (df["product_id"].astype(str).str.strip() != "").all()


# ---------- transform: inventory ----------

def test_transform_inventory_clips_negative_stock(clean_products):
    products_df, _ = clean_products
    valid_skus = set(products_df["sku"])
    raw_inv = extract_inventory(INVENTORY_FEED_JSON)
    df, report = transform_inventory(raw_inv, valid_skus)
    assert (df["stock_qty"] >= 0).all()
    assert report["clipped_negative_stock"] >= 1


def test_transform_inventory_drops_orphan_skus(clean_products):
    products_df, _ = clean_products
    valid_skus = set(products_df["sku"])
    raw_inv = extract_inventory(INVENTORY_FEED_JSON)
    df, report = transform_inventory(raw_inv, valid_skus)
    assert df["sku"].isin(valid_skus).all()
    assert report["dropped_orphan_sku"] >= 1


# ---------- transform: images ----------

def test_transform_images_drops_missing_url(clean_products):
    products_df, _ = clean_products
    valid_skus = set(products_df["sku"])
    raw_img = extract_images(IMAGE_MANIFEST_CSV)
    df, report = transform_images(raw_img, valid_skus)
    assert (df["image_url"].str.strip() != "").all()
    assert report["dropped_missing_url"] >= 1


def test_transform_images_drops_orphan_skus(clean_products):
    products_df, _ = clean_products
    valid_skus = set(products_df["sku"])
    raw_img = extract_images(IMAGE_MANIFEST_CSV)
    df, report = transform_images(raw_img, valid_skus)
    assert df["sku"].isin(valid_skus).all()
    assert report["dropped_orphan_sku"] >= 1


def test_transform_images_exactly_one_primary_per_sku(clean_products):
    products_df, _ = clean_products
    valid_skus = set(products_df["sku"])
    raw_img = extract_images(IMAGE_MANIFEST_CSV)
    df, report = transform_images(raw_img, valid_skus)
    primary_counts = df[df["is_primary"]].groupby("sku").size()
    assert (primary_counts <= 1).all()
    assert report["demoted_duplicate_primary"] >= 1
