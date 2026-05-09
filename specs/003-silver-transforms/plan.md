# Implementation Plan: Silver Transforms (Conformed Delta Tables)

**Branch**: `[003-silver-transforms]` | **Date**: 2026-05-08 | **Spec**: `specs/003-silver-transforms/spec.md`
**Input**: Feature specification from `specs/003-silver-transforms/spec.md`

## Summary

Create Silver Delta tables from Bronze with standardized types, minimal conforming rules, and idempotent partition overwrite per `dt`.

## Technical Context

**Language/Version**: Databricks Python (PySpark), Spark SQL  
**Storage**: Unity Catalog volume `/Volumes/retail_lakehouse/silver/tables`  
**Orchestration**: Notebook/Job execution (serverless compute ok)  
**Testing**: manual validations (counts, type checks, orphan checks)

## Constitution Check

- Spec-first delivery: **PASS**
- Production-minded: **PASS** (idempotent, clear contracts)
- No proprietary data: **PASS**

## Design Decisions

- **Read source**: UC tables under `retail_lakehouse.bronze.*` (preferred) with fallback to Delta paths if needed.
- **Write strategy**: Delta, partition by `dt`, overwrite partition on rerun using `replaceWhere`.
- **Orphan policy**: filter order_lines to orders present for the same `dt`.
- **Deduping**:
  - Orders: keep latest by `ingestion_ts` for `(dt, order_id)`
  - Fulfilment: keep latest by `ingestion_ts` for `(dt, order_id)`

## Project Structure

```text
specs/003-silver-transforms/
├── spec.md
├── plan.md
└── tasks.md

pipelines/silver/
├── __init__.py
├── silver_common.py
├── silver_transform_orders.py
├── silver_transform_inventory.py
├── silver_transform_fulfillment.py   # canonical (US spelling)
└── silver_transform_fulfilment.py    # shim → re-exports fulfillment
```

## Run Parameters

- `dt`: partition date, e.g. `2026-01-01`
- `silver_base_path`: `/Volumes/retail_lakehouse/silver/tables`

## One-time UC setup (manual)

```sql
CREATE SCHEMA IF NOT EXISTS retail_lakehouse.silver;
-- In Catalog UI: create Volume 'tables' in schema retail_lakehouse.silver
```

