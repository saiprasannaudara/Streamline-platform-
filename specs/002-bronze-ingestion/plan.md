# Implementation Plan: Bronze Ingestion (Databricks Lakehouse)

**Branch**: `[002-bronze-ingestion]` | **Date**: 2026-05-07 | **Spec**: `specs/002-bronze-ingestion/spec.md`
**Input**: Feature specification from `specs/002-bronze-ingestion/spec.md`

## Summary

Implement Databricks ingestion jobs to load synthetic landing datasets into Bronze Delta tables with ingestion metadata and idempotent reruns per `dt`.

## Technical Context

**Language/Version**: Databricks Python (PySpark), Spark SQL  
**Primary Dependencies**: Spark runtime, Delta Lake  
**Storage**: ADLS Gen2 (preferred) or DBFS for dev  
**Orchestration**: Databricks Workflows  
**Testing**: manual smoke checks (table exists, counts stable on rerun); automated tests deferred to later feature  
**Target Platform**: Azure Databricks  
**Project Type**: data pipelines/jobs

## Constitution Check

*GATE: Must pass before implementation.*

- Spec-first delivery: **PASS**
- Production-minded: **PASS** (idempotency + metadata required)
- No proprietary data: **PASS**

## Design Decisions

- **Table naming**: `brz_retail_orders`, `brz_retail_order_lines`, `brz_retail_inventory_snapshot`, `brz_retail_fulfilment_events`
- **Metadata fields**:
  - `dt` (string `YYYY-MM-DD`)
  - `load_id` (string; unique per run)
  - `ingestion_ts` (timestamp)
  - `source_path` (string)
- **Idempotency**:
  - Overwrite-by-partition pattern for Bronze: write to Delta partitioned by `dt` and `overwrite` the target partition on rerun.
  - Requires: stable `dt` in source path and enforced partition column.

## Project Structure

### Documentation (this feature)

```text
specs/002-bronze-ingestion/
├── plan.md
└── spec.md
```

### Source Code (repository root)

```text
pipelines/
└── bronze/
    ├── bronze_ingest_orders.py
    ├── bronze_ingest_inventory.py
    ├── bronze_ingest_fulfilment.py
    └── bronze_common.py
```

**Structure Decision**: Keep Databricks job code as `.py` files (easy to review in git) runnable as Databricks tasks.

## Run Parameters (Databricks Workflow)

- `dt`: date partition to ingest (e.g. `2026-01-01`)
- `landing_base_path`: base path for landing datasets (e.g. `dbfs:/FileStore/landing` or `abfss://.../landing`)
- `bronze_base_path`: base path for bronze delta tables (e.g. `dbfs:/FileStore/bronze` or `abfss://.../bronze`)

## Open Items (resolved during implementation)

- Decide whether to ingest JSONL using `spark.read.json` (multiline off) and whether to enforce schemas per dataset in Bronze.
- Define behavior for missing datasets for a given `dt` (fail fast vs partial success).

