# Data Dictionary — Visual Product Search Data Model

Every table in [`erd.md`](erd.md), with each attribute's type, key role, and purpose. Types are written as PostgreSQL types (the target database per the tech stack).

---

## BRAND

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| brand_id | uuid | PK | No | Unique identifier for the brand |
| name | varchar(120) | | No | Display name shown on product pages and used as a search filter |

---

## CATEGORY

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| category_id | uuid | PK | No | Unique identifier for the category |
| name | varchar(120) | | No | Display name (e.g., "Women's Sneakers") |
| parent_category_id | uuid | FK → CATEGORY.category_id | Yes | Self-referencing link that builds the category hierarchy (root categories have NULL here) |

---

## PRODUCT

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| product_id | uuid | PK | No | Unique identifier for the product |
| sku | varchar(64) | Unique | No | Business-facing stock keeping unit code |
| title | varchar(255) | | No | Product name shown in search results and used for text search fallback |
| description | text | | Yes | Full product description; source text for any NLP-based re-ranking |
| brand_id | uuid | FK → BRAND.brand_id | Yes | Links product to its brand |
| category_id | uuid | FK → CATEGORY.category_id | No | Links product to its leaf category; used to constrain/boost visual search results within a category |
| base_price | decimal(10,2) | | No | List price before variant-level overrides |
| status | varchar(20) | | No | Lifecycle state (active, discontinued, out_of_stock) — filters what's eligible to appear in search results |
| created_at | timestamp | | No | When the product was first listed; used for "new arrivals" and cold-start detection |
| updated_at | timestamp | | No | Last catalog update; drives incremental ETL loads |

---

## PRODUCT_VARIANT

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| variant_id | uuid | PK | No | Unique identifier for a specific color/size combination |
| product_id | uuid | FK → PRODUCT.product_id | No | Parent product |
| color | varchar(50) | | Yes | Variant attribute; also usable as a visual-search filter/facet |
| size | varchar(20) | | Yes | Variant attribute |
| price_override | decimal(10,2) | | Yes | Overrides base_price for this specific variant, if set |
| variant_sku | varchar(64) | Unique | No | Variant-level SKU, distinct from the parent product SKU |

**Why variants exist as their own table:** color and size directly change what a product photo looks like, so visual search needs to match against the correct variant's images — not just the parent product.

---

## PRODUCT_IMAGE

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| image_id | uuid | PK | No | Unique identifier for the image |
| variant_id | uuid | FK → PRODUCT_VARIANT.variant_id | No | Which variant this image depicts |
| image_url | varchar(500) | | No | CDN path to the image file |
| image_type | varchar(20) | | No | `catalog`, `marketing`, or `lifestyle` — lets the pipeline exclude staged marketing photos from model training (per Marketing stakeholder feedback, Task 1) |
| width | int | | Yes | Pixel width, used for pre-resize/normalization before inference |
| height | int | | Yes | Pixel height |
| is_primary | boolean | | No | Marks the default image shown in search results/listings |
| uploaded_at | timestamp | | No | When the image was added |

---

## IMAGE_EMBEDDING

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| embedding_id | uuid | PK | No | Unique identifier for the embedding record |
| image_id | uuid | FK → PRODUCT_IMAGE.image_id | No | Which image this embedding was generated from |
| embedding_vector | vector(512) | | No | The actual feature vector output by the TensorFlow model (pgvector type); this is what visual similarity search matches against |
| model_version | varchar(30) | | No | Which model produced this embedding — critical for re-indexing when the model is retrained, since old and new embeddings aren't comparable |
| created_at | timestamp | | No | When the embedding was generated |

**This is the table that makes "visual" search possible.** Everything else in the schema supports catalog and business logic; this table is the actual input to the nearest-neighbor lookup that finds visually similar products.

---

## USER

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| user_id | uuid | PK | No | Unique identifier for the user |
| email | varchar(255) | Unique | No | Login/contact identifier |
| created_at | timestamp | | No | Account creation date; used for cohort analysis and new-user cold-start handling |

*(Additional profile/preference fields intentionally omitted here — see Task 1 report, Section 2, "User Profiles & Preferences" source; that's a separate service and out of scope for the visual-search-specific model.)*

---

## USER_INTERACTION

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| interaction_id | uuid | PK | No | Unique identifier for the event |
| user_id | uuid | FK → USER.user_id | No | Who performed the action |
| product_id | uuid | FK → PRODUCT.product_id | No | Which product was acted on |
| interaction_type | varchar(30) | | No | `view`, `click`, `add_to_cart`, `wishlist`, etc. — the label used to train ranking/relevance models |
| source | varchar(20) | | No | `text_search` or `visual_search` — critical for measuring whether visual search actually improves engagement vs. traditional search (ties directly to the $2.5M business problem) |
| occurred_at | timestamp | | No | Event timestamp; streamed from Kafka |

---

## SEARCH_QUERY

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| query_id | uuid | PK | No | Unique identifier for the search event |
| user_id | uuid | FK → USER.user_id | Yes | Who searched (nullable to support anonymous/guest search) |
| query_type | varchar(10) | | No | `text` or `image` — distinguishes traditional from visual search |
| query_text | varchar(500) | | Yes | Raw text query, if query_type = text |
| query_image_id | uuid | FK → PRODUCT_IMAGE.image_id or external upload ref | Yes | The uploaded/reference image, if query_type = image |
| results_count | int | | No | How many results were returned — used to detect zero-result queries, a key visual-search quality signal |
| clicked_product_id | uuid | FK → PRODUCT.product_id | Yes | First product clicked from these results, if any — used to measure search relevance |
| timestamp | timestamp | | No | When the query was submitted |

---

## REVIEW

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| review_id | uuid | PK | No | Unique identifier for the review |
| product_id | uuid | FK → PRODUCT.product_id | No | Product being reviewed |
| user_id | uuid | FK → USER.user_id | No | Author of the review |
| rating | int | | No | 1–5 star rating |
| review_text | text | | Yes | Free-text review content |
| created_at | timestamp | | No | When the review was posted |

---

## REVIEW_IMAGE

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| review_image_id | uuid | PK | No | Unique identifier for the image |
| review_id | uuid | FK → REVIEW.review_id | No | Parent review |
| image_url | varchar(500) | | No | CDN path to the user-uploaded image |

**Why this matters for visual search:** review images are real-world, user-taken photos — visually very different from staged catalog photography. They're a valuable secondary training signal for making the visual search model robust to photos users actually upload (per Marketing's feedback in Task 1: don't overfit purely to staged imagery).

---

## ORDER_

*(Named `ORDER_` to avoid clashing with the SQL reserved word `ORDER`.)*

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| order_id | uuid | PK | No | Unique identifier for the order |
| user_id | uuid | FK → USER.user_id | No | Who placed the order |
| order_date | timestamp | | No | When the order was placed |
| total_amount | decimal(10,2) | | No | Total order value — used to tie visual search sessions back to actual revenue |
| status | varchar(20) | | No | Order lifecycle state (placed, shipped, returned, refunded) |

---

## ORDER_ITEM

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| order_item_id | uuid | PK | No | Unique identifier for the line item |
| order_id | uuid | FK → ORDER_.order_id | No | Parent order |
| variant_id | uuid | FK → PRODUCT_VARIANT.variant_id | No | Which specific variant was purchased |
| quantity | int | | No | Units purchased |
| unit_price | decimal(10,2) | | No | Price at time of purchase (kept separate from current price for historical accuracy) |

---

## WAREHOUSE

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| warehouse_id | uuid | PK | No | Unique identifier for the fulfillment center |
| name | varchar(120) | | No | Display name |
| location | varchar(255) | | No | Physical location, used for "in stock near me" logic |

---

## INVENTORY

| Attribute | Type | Key | Nullable | Purpose |
|---|---|---|---|---|
| inventory_id | uuid | PK | No | Unique identifier for the stock record |
| variant_id | uuid | FK → PRODUCT_VARIANT.variant_id | No | Which variant this stock count applies to |
| warehouse_id | uuid | FK → WAREHOUSE.warehouse_id | No | Which warehouse holds this stock |
| stock_qty | int | | No | Current available quantity — used to filter/de-rank out-of-stock items in visual search results |
| updated_at | timestamp | | No | Last sync time from the ERP/WMS system |

---

## Notes on completeness

This dictionary intentionally covers only the entities needed to **serve visual product search end to end**: catalog structure (Brand/Category/Product/Variant), the imagery + AI layer (Image/Embedding), behavioral signal (Interaction/SearchQuery), trust signal (Review/ReviewImage), and the commercial layer that justifies the feature (Order/OrderItem/Inventory/Warehouse). Broader account/identity data (addresses, payment methods, notification preferences) lives in other services per the Task 1 inventory and is out of scope here to keep the model focused on what visual search actually needs.
