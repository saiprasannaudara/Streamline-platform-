---

description: "Tasks for Bronze ingestion feature"
---

# Tasks: Bronze Ingestion (Databricks Lakehouse)

**Input**: `specs/002-bronze-ingestion/spec.md`, `specs/002-bronze-ingestion/plan.md`

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 Create `pipelines/bronze/` folder structure
- [ ] T002 Implement shared helpers in `pipelines/bronze/bronze_common.py` (params, metadata, write mode)

## Phase 2: User Story 1 - Ingest landing data into Bronze Delta tables (P1)

**Independent Test**: run for one `dt`, validate counts and rerun idempotency

- [ ] T010 Implement orders ingestion in `pipelines/bronze/bronze_ingest_orders.py` (orders + order_lines)
- [ ] T011 Implement inventory ingestion in `pipelines/bronze/bronze_ingest_inventory.py`
- [ ] T012 Implement fulfilment ingestion in `pipelines/bronze/bronze_ingest_fulfilment.py`
- [ ] T013 Add ingestion metadata columns consistently across all Bronze tables
- [ ] T014 Implement partition overwrite by `dt` to guarantee idempotency

## Phase 3: User Story 2 - Support schema evolution safely (P2)

**Independent Test**: add a nullable column to a landing file and rerun ingestion

- [ ] T020 Decide schema drift policy for Bronze (permit additive columns vs quarantine)
- [ ] T021 Implement chosen policy consistently (documented in code + docs)

## Phase 4: Workflow wiring (Polish)

- [ ] T030 Create a Databricks Workflow outline (tasks + parameters) documented in `docs/` (implementation may be manual in UI initially)

