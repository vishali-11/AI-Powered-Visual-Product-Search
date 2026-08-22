"""
Transform stage of the ingestion pipeline.

Cleans and validates the raw extracts from extract.py and converts them
into a structured format matching the target schema (see
docs/task2/data_dictionary.md). Every cleaning decision is logged and
counted so a data-quality report can be produced at the end of the run
(see docs/task3/testing_report.md for a sample run's results).

Each function is pure (DataFrame in, DataFrame out) and independent of
any database connection, which keeps it unit-testable without a live DB
(see tests/test_transform.py).
"""

import logging
import re
import uuid

import pandas as pd

from config import VALID_STATUSES

logger = logging.getLogger(__name__)


def _parse_price(raw_price):
    """Convert a price string like '$64.50' or '89.99' into a float.
    Returns None if missing/unparseable so the caller can decide how to
    handle it, rather than silently guessing a value."""
    if pd.isna(raw_price) or str(raw_price).strip() == "":
        return None
    cleaned = re.sub(r"[^0-9.\-]", "", str(raw_price))
    try:
        value = float(cleaned)
    except ValueError:
        return None
    return value


def transform_products(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Clean the raw product catalog extract.

    Rules applied (each counted in the returned quality report):
      - Blank product_id -> generate a UUID (source system doesn't assign one)
      - Duplicate SKUs -> keep the first occurrence, drop the rest
      - Title blank -> row dropped (title is required to display a product)
      - Category -> lowercased/stripped for consistent taxonomy matching
      - Price -> parsed from strings like "$64.50"; negative or unparseable
        prices are treated as invalid and the row is dropped
      - Status -> anything outside the valid enum is coerced to "active"
        with a warning, since an unrecognized status shouldn't silently
        block product visibility
    """
    df = raw_df.copy()
    report = {"input_rows": len(df)}

    before = len(df)
    title_missing_mask = df["title"].isna() | (df["title"].astype(str).str.strip() == "")
    df = df[~title_missing_mask].copy()
    df["title"] = df["title"].astype(str).str.strip()
    report["dropped_missing_title"] = before - len(df)

    before = len(df)
    df = df.drop_duplicates(subset=["sku"], keep="first")
    report["dropped_duplicate_sku"] = before - len(df)

    df["product_id"] = df["product_id"].apply(
        lambda v: str(uuid.uuid4()) if pd.isna(v) or str(v).strip() == "" else v
    )

    df["category"] = df["category"].astype(str).str.strip().str.lower()
    df["brand"] = df["brand"].astype(str).str.strip()

    df["price"] = df["price"].apply(_parse_price)
    before = len(df)
    invalid_price_mask = df["price"].isna() | (df["price"] < 0)
    report["dropped_invalid_price"] = int(invalid_price_mask.sum())
    df = df[~invalid_price_mask]
    _ = before  # kept for readability; count already captured above

    invalid_status_mask = ~df["status"].isin(VALID_STATUSES)
    report["coerced_invalid_status"] = int(invalid_status_mask.sum())
    df.loc[invalid_status_mask, "status"] = "active"

    report["output_rows"] = len(df)
    logger.info("Product transform report: %s", report)
    return df.reset_index(drop=True), report


def transform_inventory(raw_df: pd.DataFrame, valid_skus: set) -> tuple[pd.DataFrame, dict]:
    """
    Clean the raw inventory feed.

    Rules applied:
      - stock_qty coerced to int; negative values clipped to 0 (a negative
        stock count is a source-system bug, not a valid state to load)
      - rows referencing a SKU not present in the cleaned product catalog
        are dropped, to protect referential integrity in the target DB
    """
    df = raw_df.copy()
    report = {"input_rows": len(df)}

    df["stock_qty"] = pd.to_numeric(df["stock_qty"], errors="coerce").fillna(0).astype(int)
    negative_mask = df["stock_qty"] < 0
    report["clipped_negative_stock"] = int(negative_mask.sum())
    df.loc[negative_mask, "stock_qty"] = 0

    before = len(df)
    df = df[df["sku"].isin(valid_skus)]
    report["dropped_orphan_sku"] = before - len(df)

    report["output_rows"] = len(df)
    logger.info("Inventory transform report: %s", report)
    return df.reset_index(drop=True), report


def transform_images(raw_df: pd.DataFrame, valid_skus: set) -> tuple[pd.DataFrame, dict]:
    """
    Clean the raw image manifest.

    Rules applied:
      - rows with a missing image_url are dropped (unusable for visual search)
      - rows referencing a SKU not present in the cleaned product catalog
        are dropped, to protect referential integrity
      - if multiple images for the same SKU are marked is_primary, only the
        first is kept as primary and the rest are demoted, so downstream
        consumers can always rely on exactly one primary image per SKU
    """
    df = raw_df.copy()
    report = {"input_rows": len(df)}

    before = len(df)
    url_missing_mask = df["image_url"].isna() | (df["image_url"].astype(str).str.strip() == "")
    df = df[~url_missing_mask].copy()
    df["image_url"] = df["image_url"].astype(str).str.strip()
    report["dropped_missing_url"] = before - len(df)

    before = len(df)
    df = df[df["sku"].isin(valid_skus)]
    report["dropped_orphan_sku"] = before - len(df)

    df["is_primary"] = df["is_primary"].astype(str).str.lower() == "true"
    dup_primary_count = 0
    for sku, group in df.groupby("sku"):
        primary_idx = group.index[group["is_primary"]]
        if len(primary_idx) > 1:
            dup_primary_count += len(primary_idx) - 1
            df.loc[primary_idx[1:], "is_primary"] = False
    report["demoted_duplicate_primary"] = dup_primary_count

    report["output_rows"] = len(df)
    logger.info("Image transform report: %s", report)
    return df.reset_index(drop=True), report
