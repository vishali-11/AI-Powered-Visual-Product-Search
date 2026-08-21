# Entity-Relationship Diagram — Visual Product Search Data Model

This diagram renders natively on GitHub (mermaid.js). It covers every entity needed to support visual product search: product catalog, imagery + embeddings, user behavior, and transactions.

```mermaid
erDiagram
  BRAND ||--o{ PRODUCT : makes
  CATEGORY ||--o{ PRODUCT : classifies
  CATEGORY ||--o{ CATEGORY : "has subcategory"
  PRODUCT ||--o{ PRODUCT_VARIANT : has
  PRODUCT_VARIANT ||--o{ PRODUCT_IMAGE : has
  PRODUCT_IMAGE ||--o| IMAGE_EMBEDDING : generates
  PRODUCT_VARIANT ||--o{ INVENTORY : stocked_as
  WAREHOUSE ||--o{ INVENTORY : holds
  USER ||--o{ USER_INTERACTION : performs
  USER ||--o{ SEARCH_QUERY : submits
  USER ||--o{ REVIEW : writes
  USER ||--o{ ORDER_ : places
  PRODUCT ||--o{ USER_INTERACTION : target_of
  PRODUCT ||--o{ REVIEW : receives
  PRODUCT_VARIANT ||--o{ ORDER_ITEM : ordered_as
  ORDER_ ||--o{ ORDER_ITEM : contains
  REVIEW ||--o{ REVIEW_IMAGE : includes

  PRODUCT {
    uuid product_id PK
    string sku
    string title
    string description
    uuid brand_id FK
    uuid category_id FK
    decimal base_price
    string status
  }
  PRODUCT_VARIANT {
    uuid variant_id PK
    uuid product_id FK
    string color
    string size
    decimal price_override
  }
  PRODUCT_IMAGE {
    uuid image_id PK
    uuid variant_id FK
    string image_url
    string image_type
    boolean is_primary
  }
  IMAGE_EMBEDDING {
    uuid embedding_id PK
    uuid image_id FK
    vector embedding_vector
    string model_version
  }
  CATEGORY {
    uuid category_id PK
    string name
    uuid parent_category_id FK
  }
  BRAND {
    uuid brand_id PK
    string name
  }
  USER {
    uuid user_id PK
    string email
    timestamp created_at
  }
  USER_INTERACTION {
    uuid interaction_id PK
    uuid user_id FK
    uuid product_id FK
    string interaction_type
    string source
    timestamp occurred_at
  }
  SEARCH_QUERY {
    uuid query_id PK
    uuid user_id FK
    string query_type
    uuid query_image_id FK
    int results_count
  }
  REVIEW {
    uuid review_id PK
    uuid product_id FK
    uuid user_id FK
    int rating
    string review_text
  }
  REVIEW_IMAGE {
    uuid review_image_id PK
    uuid review_id FK
    string image_url
  }
  ORDER_ {
    uuid order_id PK
    uuid user_id FK
    timestamp order_date
    decimal total_amount
  }
  ORDER_ITEM {
    uuid order_item_id PK
    uuid order_id FK
    uuid variant_id FK
    int quantity
    decimal unit_price
  }
  WAREHOUSE {
    uuid warehouse_id PK
    string name
    string location
  }
  INVENTORY {
    uuid inventory_id PK
    uuid variant_id FK
    uuid warehouse_id FK
    int stock_qty
  }
```

## How to read this

- **Catalog spine:** `BRAND` and `CATEGORY` classify `PRODUCT`; each `PRODUCT` has one or more `PRODUCT_VARIANT` (color/size combinations), and each variant has its own images and stock.
- **Visual search core:** `PRODUCT_IMAGE` → `IMAGE_EMBEDDING` is the pair that actually powers visual search — every catalog image gets a vector embedding used for similarity lookup. `SEARCH_QUERY` can itself reference an uploaded image (`query_image_id`), which is embedded the same way and compared against `IMAGE_EMBEDDING`.
- **Behavioral loop:** `USER_INTERACTION` and `SEARCH_QUERY` capture what users do and search for; `REVIEW` (with its own `REVIEW_IMAGE`s) is a second, real-world source of product imagery distinct from staged catalog photos.
- **Transactional spine:** `ORDER_` → `ORDER_ITEM` → `PRODUCT_VARIANT` ties visual search usage back to actual revenue, and `INVENTORY` (per variant, per `WAREHOUSE`) supports "in stock near me" filtering on search results.

See [`data_dictionary.md`](data_dictionary.md) for every field's type and purpose, and [`modeling_rationale.md`](modeling_rationale.md) for why this is structured as normalized core + a denormalized search layer rather than one or the other.
