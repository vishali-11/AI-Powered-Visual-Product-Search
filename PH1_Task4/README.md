# AI-Powered Visual Product Search — QCraque Data Engineer Track

This repository contains all Milestone 1 task submissions for the AI-Powered Visual Product Search project (VisualSeek Inc.), completed as part of the QCraque Data Engineer program.

## Tasks

| Task | Description | Folder | Key files |
|---|---|---|---|
| Task 1 | Analyze Data Sources | [`PH1_Task1/visualseek-data-foundation`](PH1_Task1/visualseek-data-foundation) | `docs/data_sources_inventory_report.md`, `docs/incidents/` |
| Task 2 | Design Data Model | [`PH1_Task2`](PH1_Task2) | `diagram/visual-product-search-erd.md`, `docs/data_dictionary.md`, `docs/modeling_rationale.md` |
| Task 3 | Build Ingestion Pipeline | [`PH1_Task3`](PH1_Task3) | `etl/pipeline.py`, `docs/ingestion_pipeline.md`, `docs/testing_report.md` |
| Task 4 | Data Validation Checks | [`PH1_Task4`](PH1_Task4) | `validate.py`, `docs/validation_logic.md`, `reports/validation_report.md` |

## Project Context

VisualSeek Inc. is losing an estimated $2.5M in potential sales because traditional keyword search can't capture what users are looking for visually. This project builds the data foundation — data sources, data model, ETL pipeline, and data quality validation — for an AI-powered visual product search feature.

## How to run each task

Each task folder has its own README with setup and run instructions. In general:
```bash
cd PH1_TaskN
pip install -r requirements.txt   # where applicable
python <entry_script>.py
```
See the individual task README for specifics.