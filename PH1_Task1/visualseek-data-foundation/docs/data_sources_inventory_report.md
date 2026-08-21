# Data Sources Inventory Report
### AI-Powered Visual Product Search — Project Milestone 1
**VisualSeek Inc.** | Role: Data Engineer — E-commerce & Retail Domain | Task: Analyze Data Sources

---

## 1. Executive Summary

VisualSeek Inc. is losing an estimated $2.5M in potential sales because traditional keyword search cannot capture what users are looking for visually. This report inventories every data source needed to build the data foundation for an AI-powered visual product search system: product catalog data, imagery, user behavior signals, transactional history, and relevant external datasets. It documents format, estimated volume, and update frequency for each source, and summarizes feedback gathered from key stakeholders (Product, Marketing, Data Science, Customer Support, and Engineering) so that Milestone 2 (data modeling and ETL pipeline design) can proceed on a validated foundation.

> **Note on figures:** VisualSeek Inc. is a simulated organization for this project. Volume estimates below are derived from the stated company profile ($120M revenue, 3M users, 60-person engineering team) using standard e-commerce industry ratios, and are flagged as assumptions throughout. Replace with actuals if a real backend/sandbox is available.

---

## 2. Data Source Inventory — Internal Sources

| Data Source | Owner / System | Format | Est. Current Volume | Growth / Frequency |
|---|---|---|---|---|
| Product Catalog | Product/Catalog DB (PostgreSQL) | Relational / JSON attributes | ~2.1M active SKUs, 40+ attributes each | Real-time writes; ~15K new SKUs/month |
| Product Images | Media/CDN Store (S3-compatible) | JPEG / PNG / WebP | ~12M images (avg. 5-6 per SKU); ~4.8 TB | Grows with catalog; batch + on-demand upload |
| User Interaction / Clickstream | Event bus (Kafka topics: view, click, add_to_cart, dwell) | JSON (event-based) | ~45-60M events/day across 3M MAU | Streaming, continuous; retained 90 days hot / archived to cold storage |
| Search Query Logs | Search service logs | JSON / semi-structured text | ~6-8M queries/month; ~35% zero-result or abandoned | Streaming; daily batch aggregation |
| Transaction / Order History | Orders DB (PostgreSQL) + Data Warehouse | Relational | ~9-10M orders/year (derived from $120M revenue, ~AOV $60-70) | Real-time transactional; nightly ETL to warehouse |
| User Profiles & Preferences | Identity/Account service (PostgreSQL) | Relational + JSON preferences | 3M registered users | Updated on profile edit / login events |
| Wishlists & Saved Items | Account service | Relational | ~1.2M active wishlists | Real-time on user action |
| Reviews & Ratings | Reviews service (PostgreSQL / document store) | JSON (text, star rating, user-uploaded images) | ~800K reviews; ~180K with embedded images | Async writes; moderation batch job daily |
| Inventory & Warehouse Stock | ERP / WMS system | CSV export + relational | 2.1M SKUs across ~6 fulfillment centers | Syncs every 15-30 min |
| Category Taxonomy & Metadata | Catalog service (reference tables) | JSON / relational hierarchy | ~1,800 leaf categories, 6-level hierarchy | Low-frequency; quarterly curation updates |
| Product Return / Refund Records | Orders DB | Relational | ~4-6% of orders (~450K-600K/year) | Nightly ETL |

---

## 3. Data Source Inventory — External / Third-Party Sources

| Data Source | Owner / System | Format | Est. Current Volume | Growth / Frequency |
|---|---|---|---|---|
| Instacart Market Basket Dataset (Kaggle) | Public dataset | CSV | ~3M grocery orders, 200K users | Static — one-time reference for basket/behavior modeling |
| Amazon Berkeley Objects (ABO) / DeepFashion | Public research dataset | Images + JSON metadata | ABO: ~398K listings, 8M images; DeepFashion: ~800K images | Static — pretraining / benchmarking visual similarity models |
| Vision Labeling APIs (Google Vision, AWS Rekognition) | Third-party API | JSON (labels, tags, embeddings) | Usage-based, pay-per-call | On-demand — baseline auto-tagging for cold-start products |
| Social/Visual Trend Signals (e.g., Pinterest Trends) | Third-party API (where licensing permits) | JSON | Sampled trend data, not full firehose | Weekly/monthly trend refresh |
| Competitor Catalog Snapshots | Internal market-intel team | CSV / scraped JSON | Spot-check samples ~10-20K listings | Periodic (monthly) competitive benchmarking |

---

## 4. Data Categorization Summary

- **Product Data:** Catalog, taxonomy, inventory, image assets — the backbone for the visual embedding index and product metadata store.
- **Behavioral / Interaction Data:** Clickstream, search logs, wishlists — used to train ranking/relevance and evaluate whether visual search reduces abandonment.
- **Transactional Data:** Orders, returns, refunds — ties visual search usage back to the $2.5M revenue opportunity and measures ROI.
- **User-Generated Content:** Reviews, ratings, review images — a secondary, real-world image source distinct from staged catalog photography.
- **External Reference Data:** Public datasets and vision APIs — used for pretraining/benchmarking, not as a source of truth for production data.

---

## 5. Stakeholder Consultation Summary

| Stakeholder | Data Needs Raised | Key Feedback | Action Taken / Planned |
|---|---|---|---|
| Product Management | Category structure priorities, which product lines drive the most search abandonment, definition of "visually similar" from a merchandising standpoint | Flagged that category taxonomy is inconsistently applied for ~8% of SKUs (legacy migration) and should be cleaned before use as a training label | Provide a taxonomy-cleanliness data quality check in Milestone 1 deliverables |
| Marketing | Campaign and seasonal trend data, which product images are used in promotions, brand style guides for image quality | Requested that promotional/banner images be excluded from the training set to avoid bias toward staged marketing photography vs. actual catalog photos | Add a source-tag field to distinguish catalog vs. marketing imagery |
| Data Science / ML Team | Label quality for reviews and image tags, need for a held-out validation set, embedding storage requirements | Confirmed TensorFlow pipeline will need images pre-resized/normalized; asked for a manifest file mapping image → SKU → attributes | Design ETL to output a structured image-manifest table as part of the pipeline |
| Customer Support / CX | Common complaint themes tied to search ("couldn't find what I saw on Instagram"), return reasons linked to product mismatch | Noted returns tagged "not as pictured" are a proxy signal for visual-search quality and should be tracked over time | Include return-reason codes in the transactional data model |
| Engineering / Platform Team | Kafka topic ownership, current retention policies, PostgreSQL schema constraints, rate limits on internal APIs | Clickstream retention is only 90 days hot storage; older data lives in cold archive with slower access — affects incremental load design | Plan Airflow DAGs around the 90-day hot-storage window and schedule archive backfills separately |

---

## 6. Gaps and Risks Identified

- **Taxonomy inconsistency:** ~8% of SKUs carry legacy category labels that don't map cleanly to the current 6-level taxonomy — needs a data quality rule before use as a training label (see Great Expectations checks planned for Milestone 1 data quality standards).
- **Clickstream retention window:** only 90 days of hot Kafka data is available before archival, constraining the lookback window for any incremental training pipeline — needs to be reflected in Airflow DAG design.
- **Marketing vs. catalog imagery bias:** promotional/banner images are visually distinct from real catalog photos and must be tagged and filtered separately, or the visual model will overfit to staged photography.
- **Cold-start products:** newly listed SKUs (~15K/month) have no interaction history and limited imagery, so external pretraining datasets (ABO, DeepFashion) and vision-labeling APIs are needed to bootstrap them.
- **No existing image-to-SKU manifest:** the ML team's requested manifest table (image path → SKU → attributes → source tag) doesn't exist yet and is a required ETL output, not just a raw source.

---

## 7. Known Reliability Issues & Incident Log

The data sources identified in Sections 2–3 don't just need to be *inventoried* — they need to be *available* for the visual search system to work. This section documents reliability incidents observed across the underlying infrastructure that these sources depend on (caching, event streaming, model serving, object storage), why they matter for data engineering, and how they were mitigated. Full postmortems for each are in [`incidents/`](incidents/).

| # | Incident | Source Affected | Impact | Detection | Mitigation |
|---|---|---|---|---|---|
| 1 | Redis cache crash under traffic spike | User Interaction / Clickstream (cache layer) | ~10,000 users hit higher search latency; 15% sales drop over 3 hours | Datadog alerts on cache latency/error rates | Scaled Redis instance; moved to a Redis Cluster for load distribution |
| 2 | TensorFlow model inference slowdown at peak | Product Images → visual search inference pipeline | Search response times rose sharply; 10% increase in abandonment during peak hours | User reports + performance monitoring | Applied quantization; redeployed via TensorFlow Serving |
| 3 | Kafka consumer lag delaying product indexing | Product Catalog sync / clickstream event bus | Search index stale for 2 hours, affecting ~20% of queries | Monitoring dashboards showing rising message lag | Fixed consumer group misconfiguration; added topic replicas |
| 4 | AWS S3 regional outage blocking image retrieval | Product Images (S3-compatible media store) | ~5,000 users couldn't view product images; 25% engagement drop over 1 hour | AWS status notifications + user feedback | Adopted a multi-region S3 strategy for redundancy |

**Why this belongs in the data sources report, not just an ops log:** each incident maps directly to a source documented in Sections 2–3 (Redis caches interaction data, Kafka feeds catalog/index updates, S3 hosts product images, TensorFlow consumes those images for inference). A data source inventory that only covers volume and format — and not the failure modes of the systems serving that data — understates the operational risk data engineering has to design around. These incidents are folded into the risk list in Section 6 conceptually, and inform Milestone 1's data quality and pipeline orchestration work (retry logic, replica counts, multi-region storage, model-serving optimization).

### Incident detail

#### 1. Redis cache went down during a traffic spike
- **Root cause:** An unexpected traffic increase exceeded the Redis instance's capacity, causing a crash.
- **Impact:** ~10,000 users experienced increased search latency, contributing to a 15% drop in sales over a 3-hour window.
- **Detection:** Datadog alerts flagged high latency and error rates on cache lookups.
- **Mitigation:** Scaled the Redis instance and moved to a Redis Cluster setup to distribute load.

#### 2. TensorFlow model inference was slow during peak hours
- **Root cause:** The deployed model wasn't optimized for real-time inference, so latency rose sharply under heavy load.
- **Impact:** Search response times increased significantly; user abandonment rose 10% during peak hours.
- **Detection:** User reports combined with performance monitoring tools surfaced the latency pattern.
- **Mitigation:** Applied model optimization techniques (quantization) and deployed via TensorFlow Serving for faster inference.

#### 3. Kafka message lag delayed product indexing
- **Root cause:** A misconfiguration in Kafka consumer group settings caused processing delays.
- **Impact:** Search results were outdated for 2 hours, affecting ~20% of search queries and likely reducing conversions.
- **Detection:** Monitoring dashboards showed rising message lag on the relevant Kafka topic.
- **Mitigation:** Corrected the consumer group settings and increased topic replicas to handle load.

#### 4. AWS S3 experienced temporary access issues affecting image retrieval
- **Root cause:** A regional AWS outage affected accessibility of the S3 bucket storing product images.
- **Impact:** ~5,000 users were unable to view product images, contributing to a 25% engagement drop over 1 hour.
- **Detection:** AWS status notifications plus user feedback flagged the issue.
- **Mitigation:** Implemented a multi-region S3 strategy for redundancy and to reduce future disruption risk.

---

## 8. Next Steps (Feeds Into Milestone 1 Data Modeling)

- Design a normalized product/image schema in PostgreSQL, including the image manifest table requested by Data Science.
- Define Great Expectations suites for catalog completeness, taxonomy validity, and image-SKU referential integrity.
- Draft initial Airflow DAGs for: (a) nightly catalog + inventory sync, (b) streaming clickstream ingestion via Kafka, (c) image ingestion/normalization for TensorFlow input.
- Confirm data governance rules for user-generated content (review images) given privacy and moderation requirements.
