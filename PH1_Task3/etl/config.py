"""
Configuration for the VisualSeek ingestion pipeline.

Reads a database URL from the DATABASE_URL environment variable, per the
project's tech stack (PostgreSQL via SQLAlchemy). Falls back to a local
SQLite file for local development/testing so the pipeline can be run
without a live Postgres instance.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

PRODUCT_CATALOG_CSV = RAW_DATA_DIR / "product_catalog_export.csv"
INVENTORY_FEED_JSON = RAW_DATA_DIR / "inventory_feed.json"
IMAGE_MANIFEST_CSV = RAW_DATA_DIR / "image_manifest.csv"

# Target database. In production this points at PostgreSQL, e.g.:
#   postgresql+psycopg2://user:password@host:5432/visualseek
# For local dev/testing it defaults to a SQLite file so the pipeline
# runs with zero external setup.
DATABASE_URL = os.environ.get(
    "DATABASE_URL", f"sqlite:///{BASE_DIR / 'visualseek_dev.db'}"
)

VALID_STATUSES = {"active", "discontinued", "out_of_stock"}

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "pipeline.log"
