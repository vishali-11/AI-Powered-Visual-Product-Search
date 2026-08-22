"""
Runs the full extract -> transform -> load pipeline end to end and prints
a summary report. This is the entry point referenced in the deliverables
doc and is what a scheduler (Airflow, or cron for a simpler setup) would
invoke on a schedule to keep the target database in sync with source
systems.

Usage:
    python pipeline.py
"""

import logging
import time

from config import LOG_FILE
from extract import extract_all
from transform import transform_products, transform_inventory, transform_images
from load import load_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger("pipeline")


def run():
    start = time.time()
    logger.info("=== Ingestion pipeline run started ===")

    raw = extract_all()

    products_df, products_report = transform_products(raw["products"])
    valid_skus = set(products_df["sku"])

    inventory_df, inventory_report = transform_inventory(raw["inventory"], valid_skus)
    images_df, images_report = transform_images(raw["images"], valid_skus)

    load_counts = load_all(products_df, inventory_df, images_df)

    elapsed = time.time() - start

    summary = {
        "elapsed_seconds": round(elapsed, 3),
        "products": products_report,
        "inventory": inventory_report,
        "images": images_report,
        "loaded_row_counts": load_counts,
    }

    logger.info("=== Ingestion pipeline run complete in %.3fs ===", elapsed)
    for section, data in summary.items():
        logger.info("%s: %s", section, data)

    return summary


if __name__ == "__main__":
    run()
