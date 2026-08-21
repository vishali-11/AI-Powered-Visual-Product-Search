# VisualSeek — Data Foundation for AI-Powered Visual Product Search

**Project Milestone 1 — Data Engineer Track (E-commerce & Retail Domain)**

This repo contains my work for Task 1 of Milestone 1: **Analyze Data Sources** for VisualSeek Inc.'s AI-powered visual product search system.

## Business Problem

Traditional keyword search fails to capture ~$2.5M in potential sales because users struggle to find products visually. This project's goal is to design the data foundation — data model, ETL pipelines, and data quality standards — for a visual search system inspired by Pinterest's visual discovery engine.

## Task 1: Analyze Data Sources

Before any pipeline or model can be built, this task inventories every data source relevant to visual product search: what exists, in what format, at what volume, and what additional data stakeholders flagged as useful.

📄 Full report: [`docs/data_sources_inventory_report.md`](docs/data_sources_inventory_report.md)

### Deliverables in this repo

| Deliverable | Location |
|---|---|
| Data sources inventory report | `docs/data_sources_inventory_report.md` |
| Data source format & volume documentation | Tables in the same report |
| Stakeholder feedback summary | Section 5 of the same report |
| Reliability incident log | Section 7 of the same report, full postmortems in `docs/incidents/` |

## Repo Structure

```
visualseek-data-foundation/
├── README.md                              ← you are here
├── docs/
│   ├── data_sources_inventory_report.md   ← main deliverable for Task 1
│   └── incidents/                          ← reliability postmortems (Section 7 of the report)
│       ├── README.md
│       ├── 01_redis_cache_crash.md
│       ├── 02_tensorflow_inference_latency.md
│       ├── 03_kafka_consumer_lag.md
│       └── 04_s3_regional_outage.md
└── data_samples/
    └── README.md                           ← notes on sample/reference datasets used
```

## Company Context (for graders)

VisualSeek Inc. is the simulated organization used for this course project: $120M revenue, 3M users, 60-person engineering team, e-commerce/retail domain. Volume figures in the report are realistic estimates derived from this profile using standard industry ratios, since no live backend is available — this is flagged explicitly in the report.

## Next Milestones

- Data modeling (schema design for product catalog, image manifest, user interaction tables)
- ETL pipeline design (Airflow DAGs, incremental loading)
- Data quality standards (Great Expectations suites)
