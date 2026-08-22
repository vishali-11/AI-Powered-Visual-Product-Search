# Modeling Rationale — Normalized vs. Dimensional

## The decision

This data model uses a **normalized (3NF) relational design as the system of record**, with a **denormalized, search-optimized read layer** built on top of it for the actual visual search queries. It is not a pure dimensional (star schema) model, and it is not a pure normalized model either — the two query patterns in this system genuinely need different structures, and picking only one would under-serve half the workload.

## Why not pure normalized

A fully normalized schema (which is what [`erd.md`](erd.md) and [`data_dictionary.md`](data_dictionary.md) describe) is excellent for:
- Data integrity — a product's brand or category only exists in one place, so updates never go stale in two spots.
- Write efficiency — catalog updates, inventory syncs, and order placement are all frequent, small writes. Normalization keeps those cheap and safe.
- Avoiding redundancy — with ~2.1M SKUs and 40+ attributes each (Task 1 inventory), duplicating attribute data across rows would bloat storage fast.

But a visual search query at read time needs to go from "user uploads a photo" → embedding → nearest-neighbor match → **a fully assembled product card** (title, price, brand name, category name, primary image, stock status) in well under a second. Fetching that from a normalized schema means joining across `PRODUCT`, `PRODUCT_VARIANT`, `BRAND`, `CATEGORY`, `PRODUCT_IMAGE`, and `INVENTORY` for every single result in a ranked list — for a search feature, that join cost repeated at high query volume is the wrong tradeoff.

## Why not pure dimensional

A pure star schema (one flat `fact_product_search` table with all attributes pre-joined and duplicated) would make reads fast, but:
- It's a poor fit for the write side of this system. Inventory changes every 15–30 minutes, prices change, new SKUs land ~15K/month (Task 1 inventory) — a flat denormalized table means every one of those updates has to find and rewrite potentially many duplicated rows instead of one row in one table.
- It doesn't map cleanly onto the AI/embedding workload. `IMAGE_EMBEDDING` is a genuinely different kind of data (high-dimensional vectors) that doesn't belong flattened into a wide fact table alongside transactional fields.
- Referential integrity gets harder to enforce — nothing stops a flattened table from drifting out of sync with the actual catalog.

## The hybrid approach used here

| Layer | Structure | Purpose |
|---|---|---|
| System of record | Normalized (3NF) — this ERD | Catalog management, inventory sync, order processing, review moderation. Optimized for correctness and low-redundancy writes. |
| Search-serving layer | Denormalized "product search document" (materialized view or Elasticsearch/vector-DB index, built by ETL from the normalized tables) | Fast reads for the actual visual search API — one document per variant, pre-joined with brand, category, primary image, embedding reference, and current stock status. |

This mirrors a standard pattern: **normalize where data is written, denormalize where data is read at scale** — and use the ETL pipeline (Airflow, per the tech stack) as the bridge that keeps the search layer in sync with the source of truth on a defined refresh cadence.

## How query patterns drove this choice

The task brief explicitly asks to choose based on "expected query patterns" — here's the breakdown that drove the decision:

- **High-frequency, low-latency reads** (visual search lookups, browsing) → favors denormalization.
- **Frequent, small, must-be-correct writes** (inventory sync every 15–30 min, order placement, catalog edits) → favors normalization.
- **Vector similarity search** (embedding nearest-neighbor) → needs its own indexed structure regardless of schema philosophy — this is handled by pgvector (or a dedicated vector index) on `IMAGE_EMBEDDING`, separate from the OLTP/OLAP question entirely.
- **Analytics/reporting** (e.g., "did visual search reduce abandonment") → a starker dimensional model would help here too, but that's a Milestone 3-level concern (a proper analytics warehouse), not the operational schema this task is scoped to.

Because both a write-heavy operational workload and a read-heavy search workload exist in the same system, neither pure approach is "appropriate" on its own — the justification for the hybrid is that it matches structure to actual access pattern instead of forcing one structure to serve two very different jobs.

## What would change the answer

If this were a pure analytics/reporting project (e.g., a BI dashboard team measuring search performance trends over time, with no real-time query requirement), a dimensional star schema alone would be the right call — fact table of search events, dimensions for product/user/time. That's not this task: the deliverable here is the operational model that *serves* visual search, which is why normalized-core-plus-denormalized-read-layer is the better fit.