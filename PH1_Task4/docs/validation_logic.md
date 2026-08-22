# Validation Logic & Assumptions

This document explains what `validate.py` checks, why each rule was implemented the way it was, and the assumptions behind judgment calls that aren't obvious from the code alone.

## What's checked

| Category | Column(s) | Rule |
|---|---|---|
| Null check | `sku`, `title`, `category`, `brand`, `price` | Flagged if null or blank after stripping whitespace |
| Duplicate check | `sku` | Flagged if a SKU appears more than once (first occurrence is treated as valid, later ones as duplicates) |
| Data type check | `price` | Flagged if the raw value can't be interpreted as a number at all, or if it parses only after stripping currency formatting (e.g. `"$64.50"`) |
| Data type check | `status` | Flagged if the value isn't one of `active`, `discontinued`, `out_of_stock` |
| Range check | `price` | Flagged if the parsed value is ≤ 0 |
| Referential integrity | `category` | Flagged if the value (case-insensitive) doesn't exist in `data/lookup/valid_categories.csv` |
| Referential integrity | `brand` | Flagged if the value (case-insensitive) doesn't exist in `data/lookup/valid_brands.csv` |

## Why these columns are "critical"

The task brief calls out product name, category, and price explicitly. I extended that list to include `sku` (nothing downstream works without a stable identifier) and `brand` (used as a search facet and for referential integrity, per the Task 2 data model). Other columns — `description`, `status`, `product_id` — are validated but not treated as blocking-critical, because:
- `description` can legitimately be blank for a newly listed product without breaking search or checkout.
- `status` has its own enum check, which is a stronger validation than a plain null check anyway.
- `product_id` isn't present in this raw source at all — see below.

## Assumption: `product_id` is out of scope here

The raw catalog export has an empty `product_id` column for every row. In the Task 3 ETL pipeline, this is expected and handled by generating a UUID during transform — the source system doesn't assign one. Since this task's raw data intentionally mirrors that same source file, `product_id` is **not** included in the null check here; flagging every single row for the same non-issue would just add noise without surfacing a real problem. If this validation script were pointed at data *after* the Task 3 transform step (where `product_id` should always be populated), `product_id` should be added to `CRITICAL_COLUMNS`.

## Assumption: currency-formatted prices are a type violation, not just noise

A value like `"$64.50"` will successfully parse to `64.50` if you strip the currency symbol — so it's tempting to treat it as "fine." I chose to flag it anyway, distinctly from unparseable garbage, because:
- The task explicitly asks to verify "correct data types for each attribute (e.g., price should be a float)" — a string like `"$64.50"` is not a float, even if it's recoverable.
- Silently accepting inconsistent formatting hides a real upstream problem (the source system isn't emitting clean numeric data), which is exactly the kind of thing a validation report should surface so someone can go fix the export, not just work around it downstream.

This is why the report distinguishes **"price is not a valid number"** (genuinely broken — can't be recovered) from **"price is formatted as currency text"** (recoverable, but still a type violation worth flagging).

## Assumption: referential integrity is case-insensitive

The sample data has `category` values like `ELECTRONICS` (uppercase) alongside `electronics` (lowercase) elsewhere. Treating these as different values would produce a flood of false-positive violations for what's clearly the same category with inconsistent casing — a data entry/formatting issue, not a genuine "this category doesn't exist" issue. The lookup match is therefore case-insensitive. If your organization's actual taxonomy is case-sensitive by design (unlikely, but possible), this should be changed to a strict match.

## Assumption: nulls aren't double-counted across checks

If `price` is blank, that's a null-check violation — I chose *not* to also run it through the type/range checks, since "missing" and "wrong type" are different problems and reporting both would overstate the number of distinct issues on that row. Similarly, blank `category`/`brand` values are caught by the null check, not the referential integrity check. Each row can still have multiple *different* violations (e.g., a row can have both an unknown brand and an unknown category) — the checks that are skipped when null are specifically the checks that duplicate the null check's finding.

## Why lookup tables instead of hardcoded valid values

`data/lookup/valid_categories.csv` and `data/lookup/valid_brands.csv` are separate files rather than lists embedded in `validate.py`, matching how this would actually work in production — these should be the same reference/dimension tables the Task 2 data model already defines (`CATEGORY`, `BRAND`), not something re-typed into validation code. In this task's sample setup, both lookup tables are intentionally **incomplete** relative to the sample catalog (missing `fitness`, `home`, and three brands), specifically so the referential integrity checks have real violations to catch rather than trivially passing.

## What this script does *not* check

- **Cross-field consistency** (e.g., "shoes shouldn't have a `size` field formatted like a clothing size") — out of scope for this task's four required check categories.
- **Image/embedding validity** — covered conceptually in the Task 1 reliability incident log and the Task 2 data model, not here.
- **Business-rule validation** (e.g., "discontinued products shouldn't have positive stock") — this task is scoped to the catalog file alone, not a cross-table join against inventory.
