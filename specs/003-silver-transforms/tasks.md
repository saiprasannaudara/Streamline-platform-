---

description: "Tasks for Silver transforms feature"
---

# Tasks: Silver Transforms (Conformed Delta Tables)

**Input**: `specs/003-silver-transforms/spec.md`, `specs/003-silver-transforms/plan.md`

## Phase 1: Setup

- [ ] T001 Create `pipelines/silver/` folder and package markers
- [ ] T002 Implement shared utilities in `pipelines/silver/silver_common.py` (paths, overwrite strategy, source table names)

## Phase 2: User Story 1 - Produce typed, conformed Silver tables (P1)

- [ ] T010 Implement orders + order_lines transforms in `pipelines/silver/silver_transform_orders.py`
- [ ] T011 Implement inventory snapshot transform in `pipelines/silver/silver_transform_inventory.py`
- [ ] T012 Implement fulfilment events transform in `pipelines/silver/silver_transform_fulfilment.py`
- [ ] T013 Ensure all outputs are idempotent per `dt` via `replaceWhere`

## Phase 3: User Story 2 - Enforce basic referential sanity (P2)

- [ ] T020 Filter orphan order_lines (no matching order_id for the day)
- [ ] T021 Add simple validation queries (documented) to prove orphan count is 0

## Phase 4: Catalog registration (Polish)

- [ ] T030 Provide SQL `CREATE TABLE ... LOCATION ...` statements for Silver tables

