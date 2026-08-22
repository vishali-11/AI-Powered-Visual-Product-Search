# Data Validation Report

Generated: 2026-08-22T15:19:01+00:00
Source file: `data\raw\product_catalog_export.csv`

## Summary

- Total rows checked: **11**
- Total violations found: **13**
- Rows with at least one violation: **6**
- Fully clean rows: **5** (45%)

## Violations by check type

| Check | Violations |
|---|---|
| Null / blank value in a critical column | 3 |
| Duplicate SKU | 1 |
| Data type violation | 3 |
| Range violation (e.g. price <= 0) | 1 |
| Unknown category (not in lookup table) | 2 |
| Unknown brand (not in lookup table) | 3 |

## Full violation detail

| Row | SKU | Check | Column | Value | Issue |
|---|---|---|---|---|---|
| 1 | SKU-1002 | Data type violation | price | `$64.50` | price is formatted as currency text (e.g. '$64.50') rather than a plain numeric type |
| 3 | SKU-1004 | Unknown brand (not in lookup table) | brand | `Zenith` | 'Zenith' not found in the valid brand lookup table |
| 3 | SKU-1004 | Unknown category (not in lookup table) | category | `fitness` | 'fitness' not found in the valid category lookup table |
| 3 | SKU-1004 | Null / blank value in a critical column | price | `` | 'price' is null or blank |
| 5 | SKU-1002 | Data type violation | price | `$64.50` | price is formatted as currency text (e.g. '$64.50') rather than a plain numeric type |
| 5 | SKU-1002 | Duplicate SKU | sku | `SKU-1002` | duplicate SKU — already seen in an earlier row |
| 6 | SKU-1006 | Unknown brand (not in lookup table) | brand | `HomeCraft` | 'HomeCraft' not found in the valid brand lookup table |
| 6 | SKU-1006 | Unknown category (not in lookup table) | category | `home` | 'home' not found in the valid category lookup table |
| 6 | SKU-1006 | Data type violation | status | `unknown_status` | status 'unknown_status' is not one of the valid values: ['active', 'discontinued', 'out_of_stock'] |
| 6 | SKU-1006 | Null / blank value in a critical column | price | `` | 'price' is null or blank |
| 8 | SKU-1008 | Unknown brand (not in lookup table) | brand | `HydroLife` | 'HydroLife' not found in the valid brand lookup table |
| 8 | SKU-1008 | Null / blank value in a critical column | title | `` | 'title' is null or blank |
| 10 | SKU-1010 | Range violation (e.g. price <= 0) | price | `-19.99` | price must be greater than 0 (parsed value: -19.99) |
