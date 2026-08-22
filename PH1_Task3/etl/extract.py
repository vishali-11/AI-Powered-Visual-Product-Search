"""
Extract stage of the ingestion pipeline.

Pulls raw data from the three source formats identified in the Task 1
data sources inventory: a CSV catalog export, a JSON inventory feed, and
a CSV image manifest. Each function returns a raw pandas DataFrame with
no cleaning applied — validation and transformation happen in transform.py,
kept separate so each stage is independently testable.
"""

import json
import logging

import pandas as pd

from config import PRODUCT_CATALOG_CSV, INVENTORY_FEED_JSON, IMAGE_MANIFEST_CSV

logger = logging.getLogger(__name__)


def extract_products(path=PRODUCT_CATALOG_CSV) -> pd.DataFrame:
    """Extract raw product catalog rows from a CSV export."""
    logger.info("Extracting product catalog from %s", path)
    df = pd.read_csv(path, dtype=str)  # read as string; type-casting happens in transform
    logger.info("Extracted %d raw product rows", len(df))
    return df


def extract_inventory(path=INVENTORY_FEED_JSON) -> pd.DataFrame:
    """Extract raw inventory records from a JSON feed."""
    logger.info("Extracting inventory feed from %s", path)
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)
    df = pd.DataFrame(records)
    logger.info("Extracted %d raw inventory rows", len(df))
    return df


def extract_images(path=IMAGE_MANIFEST_CSV) -> pd.DataFrame:
    """Extract raw image manifest rows from a CSV export."""
    logger.info("Extracting image manifest from %s", path)
    df = pd.read_csv(path, dtype=str)
    logger.info("Extracted %d raw image rows", len(df))
    return df


def extract_all() -> dict:
    """Run all three extractions and return them keyed by source name."""
    return {
        "products": extract_products(),
        "inventory": extract_inventory(),
        "images": extract_images(),
    }
