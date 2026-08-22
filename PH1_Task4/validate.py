"""
validate.py — Data validation checks for the VisualSeek product catalog.

Implements the four validation categories the task calls for:
  1. Null checks on critical columns
  2. Data type checks (price must be a valid number, etc.)
  3. Range checks on numerical fields (price > 0)
  4. Referential integrity checks (category/brand must exist in lookup tables)

Usage:
    python validate.py

Loads data/raw/product_catalog_export.csv and the lookup tables in
data/lookup/, runs every check, prints a summary to the console, and
writes a full violation-level report to reports/validation_report.md.

Design notes / assumptions are documented in docs/validation_logic.md —
read that alongside this file, since several checks encode a judgment
call (e.g., what counts as a "critical" column) that isn't obvious from
the code alone.
"""

import re
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAW_CSV = BASE_DIR / "data" / "raw" / "product_catalog_export.csv"
VALID_CATEGORIES_CSV = BASE_DIR / "data" / "lookup" / "valid_categories.csv"
VALID_BRANDS_CSV = BASE_DIR / "data" / "lookup" / "valid_brands.csv"
REPORT_PATH = BASE_DIR / "reports" / "validation_report.md"

CRITICAL_COLUMNS = ["sku", "title", "category", "brand", "price"]
VALID_STATUSES = {"active", "discontinued", "out_of_stock"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_data(path: Path) -> pd.DataFrame:
    """Load the raw catalog as strings — no implicit type coercion, so the
    type-checking step below is checking the real, as-received data."""
    return pd.read_csv(path, dtype=str)


def load_lookup(path: Path, column: str) -> set:
    df = pd.read_csv(path, dtype=str)
    return set(df[column].str.strip())


def try_parse_price(raw_price):
    """Attempt to interpret a price value as a number, allowing common
    currency formatting (e.g. "$64.50") since that's expected from a raw
    source export. Returns (parsed_value_or_None, was_directly_numeric)."""
    if pd.isna(raw_price) or str(raw_price).strip() == "":
        return None, False
    raw = str(raw_price).strip()
    directly_numeric = bool(re.fullmatch(r"-?\d+(\.\d+)?", raw))
    cleaned = re.sub(r"[^0-9.\-]", "", raw)
    try:
        return float(cleaned), directly_numeric
    except ValueError:
        return None, False


# ---------------------------------------------------------------------------
# Validation checks — each returns a list of violation dicts
# ---------------------------------------------------------------------------

def check_nulls(df: pd.DataFrame, columns: list) -> list:
    """Flag any row where a critical column is null or blank."""
    violations = []
    for col in columns:
        missing_mask = df[col].isna() | (df[col].astype(str).str.strip() == "")
        for idx in df[missing_mask].index:
            violations.append({
                "check": "null_check",
                "row": idx,
                "sku": df.at[idx, "sku"] if pd.notna(df.at[idx, "sku"]) else "(missing sku)",
                "column": col,
                "value": None,
                "issue": f"'{col}' is null or blank",
            })
    return violations


def check_duplicate_sku(df: pd.DataFrame) -> list:
    """Flag rows sharing a SKU with an earlier row (SKU should be unique)."""
    violations = []
    dup_mask = df.duplicated(subset=["sku"], keep="first")
    for idx in df[dup_mask].index:
        violations.append({
            "check": "duplicate_sku",
            "row": idx,
            "sku": df.at[idx, "sku"],
            "column": "sku",
            "value": df.at[idx, "sku"],
            "issue": "duplicate SKU — already seen in an earlier row",
        })
    return violations


def check_price_type_and_range(df: pd.DataFrame) -> list:
    """
    Two related checks on `price`, kept separate in the report even though
    they're computed together:
      - type: does the raw value parse to a number at all (allowing
        currency formatting), or is it garbage?
      - range: for values that DO parse, is the number > 0?
    A price of "abc" fails the type check. A price of "-19.99" passes the
    type check but fails the range check. Both are reported distinctly so
    it's clear which problem needs fixing.
    """
    violations = []
    for idx, raw in df["price"].items():
        parsed, directly_numeric = try_parse_price(raw)
        sku = df.at[idx, "sku"]

        if pd.isna(raw) or str(raw).strip() == "":
            continue  # already caught by check_nulls; avoid double-reporting

        if parsed is None:
            violations.append({
                "check": "data_type",
                "row": idx,
                "sku": sku,
                "column": "price",
                "value": raw,
                "issue": "price is not a valid number",
            })
            continue

        if not directly_numeric:
            violations.append({
                "check": "data_type",
                "row": idx,
                "sku": sku,
                "column": "price",
                "value": raw,
                "issue": "price is formatted as currency text (e.g. '$64.50') rather than a plain numeric type",
            })

        if parsed <= 0:
            violations.append({
                "check": "range_check",
                "row": idx,
                "sku": sku,
                "column": "price",
                "value": raw,
                "issue": f"price must be greater than 0 (parsed value: {parsed})",
            })

    return violations


def check_status_enum(df: pd.DataFrame) -> list:
    """Flag rows where `status` isn't one of the known valid values."""
    violations = []
    for idx, raw in df["status"].items():
        if pd.isna(raw) or str(raw).strip() == "":
            continue  # covered by null check if status were critical; not critical here
        if raw not in VALID_STATUSES:
            violations.append({
                "check": "data_type",
                "row": idx,
                "sku": df.at[idx, "sku"],
                "column": "status",
                "value": raw,
                "issue": f"status '{raw}' is not one of the valid values: {sorted(VALID_STATUSES)}",
            })
    return violations


def check_referential_integrity(df: pd.DataFrame, column: str, valid_values: set, check_name: str) -> list:
    """Flag rows whose `column` value isn't present in the corresponding
    lookup table (case-insensitive, since source systems are inconsistent
    about casing — see docs/validation_logic.md)."""
    violations = []
    valid_lower = {v.lower() for v in valid_values}
    for idx, raw in df[column].items():
        if pd.isna(raw) or str(raw).strip() == "":
            continue  # covered by null check
        if raw.strip().lower() not in valid_lower:
            violations.append({
                "check": check_name,
                "row": idx,
                "sku": df.at[idx, "sku"],
                "column": column,
                "value": raw,
                "issue": f"'{raw}' not found in the valid {column} lookup table",
            })
    return violations


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_report(df: pd.DataFrame, all_violations: list) -> str:
    total_rows = len(df)
    total_violations = len(all_violations)
    affected_rows = len({v["row"] for v in all_violations})
    clean_rows = total_rows - affected_rows

    by_check = {}
    for v in all_violations:
        by_check.setdefault(v["check"], []).append(v)

    check_labels = {
        "null_check": "Null / blank value in a critical column",
        "duplicate_sku": "Duplicate SKU",
        "data_type": "Data type violation",
        "range_check": "Range violation (e.g. price <= 0)",
        "category_referential_integrity": "Unknown category (not in lookup table)",
        "brand_referential_integrity": "Unknown brand (not in lookup table)",
    }

    lines = []
    lines.append("# Data Validation Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    lines.append(f"Source file: `{RAW_CSV.relative_to(BASE_DIR)}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total rows checked: **{total_rows}**")
    lines.append(f"- Total violations found: **{total_violations}**")
    lines.append(f"- Rows with at least one violation: **{affected_rows}**")
    lines.append(f"- Fully clean rows: **{clean_rows}** ({clean_rows/total_rows:.0%})")
    lines.append("")
    lines.append("## Violations by check type")
    lines.append("")
    lines.append("| Check | Violations |")
    lines.append("|---|---|")
    for check_key, label in check_labels.items():
        count = len(by_check.get(check_key, []))
        lines.append(f"| {label} | {count} |")
    lines.append("")
    lines.append("## Full violation detail")
    lines.append("")
    lines.append("| Row | SKU | Check | Column | Value | Issue |")
    lines.append("|---|---|---|---|---|---|")
    for v in sorted(all_violations, key=lambda x: (x["row"], x["check"])):
        value_display = "" if v["value"] is None else str(v["value"])
        lines.append(
            f"| {v['row']} | {v['sku']} | {check_labels.get(v['check'], v['check'])} | "
            f"{v['column']} | `{value_display}` | {v['issue']} |"
        )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_validation():
    df = load_data(RAW_CSV)
    valid_categories = load_lookup(VALID_CATEGORIES_CSV, "category")
    valid_brands = load_lookup(VALID_BRANDS_CSV, "brand")

    all_violations = []
    all_violations += check_nulls(df, CRITICAL_COLUMNS)
    all_violations += check_duplicate_sku(df)
    all_violations += check_price_type_and_range(df)
    all_violations += check_status_enum(df)
    all_violations += check_referential_integrity(
        df, "category", valid_categories, "category_referential_integrity"
    )
    all_violations += check_referential_integrity(
        df, "brand", valid_brands, "brand_referential_integrity"
    )

    report_md = build_report(df, all_violations)
    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text(report_md, encoding="utf-8")

    # Console summary
    total_rows = len(df)
    affected_rows = len({v["row"] for v in all_violations})
    print(f"Checked {total_rows} rows, found {len(all_violations)} violations across {affected_rows} rows.")
    print(f"Full report written to {REPORT_PATH.relative_to(BASE_DIR)}")

    return all_violations


if __name__ == "__main__":
    run_validation()
