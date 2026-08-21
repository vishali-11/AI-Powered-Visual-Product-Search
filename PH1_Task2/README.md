# VisualSeek — Visual Product Search Data Model

## Task 2 — Design Data Model

This repository contains my submission for **Task 2: Design Data Model** for an AI-powered visual product search system in the e-commerce and retail domain.

## Objective

The objective of this task is to design a data model that captures the attributes and relationships required to support visual product search.

The model supports:

- Product catalog information
- Product categories and brands
- Product variants such as color and size
- Product images
- Image embeddings for visual similarity search
- User search behavior
- User interactions
- Reviews and review images
- Orders and purchased products
- Inventory and warehouse information

## Modeling Approach

The system uses a **normalized relational model as the system of record**, following a 3NF-oriented structure.

A separate **denormalized search-serving layer** can be built on top of the normalized model to support low-latency visual search queries.

This hybrid approach was selected because the system has two different workloads:

- Frequent and accurate catalog, inventory, and transaction updates
- High-frequency, low-latency visual search queries

Normalization reduces data redundancy and improves data integrity, while the search-serving layer can optimize read performance.

## ERD

The Entity-Relationship Diagram shows the relationships between the product catalog, visual-search components, user behavior, and transactional data.

**ERD:** [View ERD](diagrams/visual-product-search-erd.md)

A PDF version is also available:

**[View ERD PDF](diagrams/visual-product-search-erd.pdf)**

## Data Dictionary

The data dictionary documents each entity and attribute, including:

- Data type
- Primary and foreign keys
- Nullability
- Purpose of each attribute

**[View Data Dictionary](docs/data-dictionary.md)**

## Modeling Rationale

The modeling rationale explains why a normalized model was selected as the system of record and why a denormalized search-serving layer is appropriate for high-speed visual search queries.

**[View Modeling Rationale](docs/modeling_rationale.md)**

## Key Visual Search Components

### Product Images

Product images are associated with specific product variants so that visual search can distinguish between different colors and sizes.

### Image Embeddings

Image embeddings store vector representations generated from product images. These vectors can be used for nearest-neighbor similarity searches.

### Search Queries

Search queries capture whether a user performed a text or image-based search and provide information useful for evaluating search quality.

### User Interactions

Interactions such as views, clicks, wishlist actions, and add-to-cart events provide behavioral signals that can later support ranking and recommendation models.

### Inventory

Inventory information allows search results to consider product availability and warehouse stock.

## Repository Structure

```text
visual-product-search-data-model/
│
├── README.md
│
├── diagrams/
│   ├── visual-product-search-erd.md
│   └── visual-product-search-erd.pdf
│
├── docs/
│   ├── data-dictionary.md
│   ├── data-dictionary.pdf
│   └── modeling_rationale.md
│
└── sql/